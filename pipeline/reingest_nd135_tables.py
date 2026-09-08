import sys
import os
import re
import json
import time
from pathlib import Path
from datetime import date
from typing import List, Dict, Any, Tuple
import numpy as np

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from bs4 import BeautifulSoup
from qdrant_client.http import models as qmodels

from pipeline.models import (
    LegalArticle,
    LegalClause,
    LegalPoint,
    LegalChapter,
    LegalDocumentMetadata,
    LegalDocumentParsed,
    LegalChunkPayload,
    DocumentType,
    DocumentStatus,
)
from pipeline.loaders.supabase_loader import SupabaseLegalLoader
from backend.app.services.rag.embeddings import get_embedding_service
from backend.app.services.rag.vector_store import QdrantVectorStore


def html_table_to_matrix(table_tag) -> List[List[str]]:
    """Chuyển đổi thẻ table HTML có rowspan và colspan thành ma trận 2D chuẩn."""
    rows = table_tag.find_all("tr")
    matrix = {}
    max_r = len(rows)
    max_c = 0
    for r_idx, row in enumerate(rows):
        c_idx = 0
        for cell in row.find_all(["td", "th"]):
            while (r_idx, c_idx) in matrix:
                c_idx += 1
            rowspan = int(cell.get("rowspan", 1))
            colspan = int(cell.get("colspan", 1))
            text = " ".join(cell.get_text().split())
            for dr in range(rowspan):
                for dc in range(colspan):
                    matrix[(r_idx + dr, c_idx + dc)] = text
            c_idx += colspan
            if c_idx > max_c:
                max_c = c_idx

    table_grid = []
    for r in range(max_r):
        row_cells = [matrix.get((r, c), "") for c in range(max_c)]
        table_grid.append(row_cells)
    return table_grid


def format_subtable_markdown(
    grid: List[List[str]],
    col_start: int,
    col_end: int,
    title: str,
    note_suffix: str = "",
    min_row: int = 3,
    max_row: int = None,
) -> str:
    """Tạo bảng Markdown chuẩn 5 cột cho từng đối tượng (Nam hoặc Nữ)."""
    headers = ["Tháng sinh", "Năm sinh", "Tuổi nghỉ hưu", "Tháng hưởng lương hưu", "Năm hưởng lương hưu"]
    lines = [f"### {title}\n", "| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    
    end_r = len(grid) if max_row is None else min(len(grid), max_row)
    for r in range(min_row, end_r):
        row = grid[r][col_start:col_end]
        if not any(row) or all(x == "" for x in row):
            continue
        if row[0] == row[1] and "Từ tháng" in row[0]:
            thang_sinh = row[0]
            nam_sinh = ""
            tuoi = row[2] if len(row) > 2 else ""
            thang_huong = row[3] if len(row) > 3 else ""
            nam_huong = row[4] if len(row) > 4 else ""
            line = f"| {thang_sinh} | {nam_sinh} | {tuoi} | {thang_huong} | {nam_huong} |"
            lines.append(line)
        else:
            line = "| " + " | ".join(row) + " |"
            lines.append(line)

    if note_suffix:
        lines.append("\n" + note_suffix)
    return "\n".join(lines)


def format_table2_dieu4_markdown(grid: List[List[str]]) -> str:
    """Định dạng Table 2 tại Điều 4 thành 2 bảng lộ trình riêng cho Nam và Nữ."""
    nam_lines = [
        "#### BẢNG 1: LỘ TRÌNH ĐIỀU CHỈNH TUỔI NGHỈ HƯU ĐỐI VỚI LAO ĐỘNG NAM (ĐIỀU 4 KHOẢN 2)",
        "| Năm nghỉ hưu | Tuổi nghỉ hưu |",
        "| --- | --- |",
    ]
    for r in range(2, 10):
        if r < len(grid):
            nam_lines.append(f"| {grid[r][0]} | {grid[r][1]} |")
    nam_lines.append(
        "\n> **Ghi chú đối với Lao động Nam**: Lộ trình tăng tuổi nghỉ hưu của nam kết thúc vào năm 2028 khi đạt đủ 62 tuổi. Kể từ năm 2028 trở đi, mọi lao động nam đều nghỉ hưu khi đủ 62 tuổi (áp dụng cho mọi nam giới sinh từ tháng 04/1966 trở đi, bao gồm sinh năm 1970, 1975, 1980...)."
    )

    nu_lines = [
        "#### BẢNG 2: LỘ TRÌNH ĐIỀU CHỈNH TUỔI NGHỈ HƯU ĐỐI VỚI LAO ĐỘNG NỮ (ĐIỀU 4 KHOẢN 2)",
        "| Năm nghỉ hưu | Tuổi nghỉ hưu |",
        "| --- | --- |",
    ]
    for r in range(2, 17):
        if r < len(grid):
            nu_lines.append(f"| {grid[r][2]} | {grid[r][3]} |")
    nu_lines.append(
        "\n> **Ghi chú đối với Lao động Nữ**: Lộ trình tăng tuổi nghỉ hưu của nữ mỗi năm tăng 4 tháng cho đến khi đủ 60 tuổi vào năm 2035."
    )

    return "\n\n" + "\n".join(nam_lines) + "\n\n" + "\n".join(nu_lines) + "\n\n"


def format_table3_dieu5_markdown(grid: List[List[str]]) -> str:
    """Định dạng Table 3 tại Điều 5 thành 2 bảng tuổi nghỉ hưu thấp nhất riêng cho Nam và Nữ."""
    nam_lines = [
        "#### BẢNG 1: LỘ TRÌNH TUỔI NGHỈ HƯU THẤP NHẤT ĐỐI VỚI LAO ĐỘNG NAM (ĐIỀU 5 KHOẢN 2)",
        "| Năm nghỉ hưu | Tuổi nghỉ hưu thấp nhất |",
        "| --- | --- |",
    ]
    for r in range(2, 10):
        if r < len(grid):
            nam_lines.append(f"| {grid[r][0]} | {grid[r][1]} |")
    nam_lines.append(
        "\n> **Ghi chú đối với Lao động Nam**: Tuổi nghỉ hưu thấp nhất (diện nghề nặng nhọc, độc hại, suy giảm KNLĐ) của nam từ năm 2028 trở đi là đủ 57 tuổi."
    )

    nu_lines = [
        "#### BẢNG 2: LỘ TRÌNH TUỔI NGHỈ HƯU THẤP NHẤT ĐỐI VỚI LAO ĐỘNG NỮ (ĐIỀU 5 KHOẢN 2)",
        "| Năm nghỉ hưu | Tuổi nghỉ hưu thấp nhất |",
        "| --- | --- |",
    ]
    for r in range(2, 17):
        if r < len(grid):
            nu_lines.append(f"| {grid[r][2]} | {grid[r][3]} |")
    nu_lines.append(
        "\n> **Ghi chú đối với Lao động Nữ**: Tuổi nghỉ hưu thấp nhất của nữ từ năm 2035 trở đi là đủ 55 tuổi."
    )

    return "\n\n" + "\n".join(nam_lines) + "\n\n" + "\n".join(nu_lines) + "\n\n"


def build_curated_nd135() -> Tuple[LegalDocumentParsed, List[LegalChunkPayload]]:
    html_path = PROJECT_ROOT / "data" / "01_raw" / "html" / "135_2020_ND_CP.html"
    with open(html_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f.read(), "html.parser")

    tables = soup.find_all("table")
    grid_t2 = html_table_to_matrix(tables[1])
    grid_t3 = html_table_to_matrix(tables[2])
    grid_t5 = html_table_to_matrix(tables[4])
    grid_t6 = html_table_to_matrix(tables[5])

    md_dieu4_tables = format_table2_dieu4_markdown(grid_t2)
    md_dieu5_tables = format_table3_dieu5_markdown(grid_t3)

    note_nam_pl1 = (
        "> **QUY TẮC PHÁP LÝ BẮT BUỘC ĐỐI VỚI LAO ĐỘNG NAM (ĐIỀU KIỆN LAO ĐỘNG BÌNH THƯỜNG)**:\n"
        "> 1. Theo Điều 4 và Phụ lục I Nghị định 135/2020/NĐ-CP, lộ trình tăng tuổi nghỉ hưu của nam kết thúc vào năm 2028 ở mốc đủ 62 tuổi.\n"
        "> 2. **Tất cả lao động nam sinh từ tháng 04/1966 trở đi (bao gồm các năm 1967, 1968, 1969, 1970, 1971, 1972... trở về sau) đều nghỉ hưu khi ĐỦ 62 TUỔI**.\n"
        "> 3. **Thời điểm nghỉ hưu**: Kết thúc ngày cuối cùng của tháng người lao động đủ 62 tuổi.\n"
        "> 4. **Thời điểm hưởng lương hưu**: Bắt đầu ngày đầu tiên của tháng liền kề sau thời điểm nghỉ hưu (Năm hưởng lương hưu = Năm sinh + 62).\n"
        "> *Ví dụ*: Lao động nam sinh tháng 01/1970 sẽ nghỉ hưu hết ngày 31/01/2032 và hưởng lương hưu từ ngày 01/02/2032 (năm 2032 khi đủ 62 tuổi). Tuyệt đối không áp dụng mức 57 tuổi của nữ cho nam."
    )
    md_pl1_nam = format_subtable_markdown(
        grid_t5,
        col_start=0,
        col_end=5,
        title="BẢNG TRA CỨU LỘ TRÌNH TUỔI NGHỈ HƯU ĐỐI VỚI LAO ĐỘNG NAM (PHỤ LỤC I - NGHỊ ĐỊNH 135/2020/NĐ-CP)",
        note_suffix=note_nam_pl1,
        min_row=3,
        max_row=67,
    )

    note_nu_pl1 = (
        "> **QUY TẮC ĐỐI VỚI LAO ĐỘNG NỮ (ĐIỀU KIỆN LAO ĐỘNG BÌNH THƯỜNG)**:\n"
        "> 1. Kể từ năm 2021, tuổi nghỉ hưu của nữ tăng mỗi năm 4 tháng cho đến khi đủ 60 tuổi vào năm 2035.\n"
        "> 2. **Đối với lao động nữ sinh năm 1970**:\n"
        ">    - Nữ sinh từ tháng 01/1970 đến tháng 08/1970: Tuổi nghỉ hưu là **57 tuổi 4 tháng**; thời điểm hưởng lương hưu từ tháng 06/2027 đến tháng 01/2028.\n"
        ">    - Nữ sinh từ tháng 09/1970 đến tháng 12/1970: Tuổi nghỉ hưu là **57 tuổi 8 tháng**; thời điểm hưởng lương hưu từ tháng 06/2028 đến tháng 09/2028.\n"
        "> 3. Kể từ tháng 01/1975 trở đi, lao động nữ nghỉ hưu khi đủ 60 tuổi."
    )
    md_pl1_nu = format_subtable_markdown(
        grid_t5,
        col_start=5,
        col_end=10,
        title="BẢNG TRA CỨU LỘ TRÌNH TUỔI NGHỈ HƯU ĐỐI VỚI LAO ĐỘNG NỮ (PHỤ LỤC I - NGHỊ ĐỊNH 135/2020/NĐ-CP)",
        note_suffix=note_nu_pl1,
        min_row=3,
        max_row=None,
    )

    note_nam_pl2 = (
        "> **QUY TẮC ĐỐI VỚI LAO ĐỘNG NAM NGHỈ HƯU THẤP NHẤT (ĐIỀU 5 & PHỤ LỤC II)**:\n"
        "> Áp dụng cho người lao động có từ đủ 15 năm làm nghề nặng nhọc, độc hại hoặc suy giảm KNLĐ từ 61% trở lên. Nam sinh từ tháng 04/1971 trở đi thì tuổi nghỉ hưu thấp nhất là 57 tuổi."
    )
    md_pl2_nam = format_subtable_markdown(
        grid_t6,
        col_start=0,
        col_end=5,
        title="BẢNG TRA CỨU TUỔI NGHỈ HƯU THẤP NHẤT ĐỐI VỚI LAO ĐỘNG NAM (PHỤ LỤC II - NGHỊ ĐỊNH 135/2020/NĐ-CP)",
        note_suffix=note_nam_pl2,
        min_row=3,
        max_row=67,
    )

    note_nu_pl2 = (
        "> **QUY TẮC ĐỐI VỚI LAO ĐỘNG NỮ NGHỈ HƯU THẤP NHẤT (ĐIỀU 5 & PHỤ LỤC II)**:\n"
        "> Nữ sinh từ tháng 01/1980 trở đi thì tuổi nghỉ hưu thấp nhất là 55 tuổi."
    )
    md_pl2_nu = format_subtable_markdown(
        grid_t6,
        col_start=5,
        col_end=10,
        title="BẢNG TRA CỨU TUỔI NGHỈ HƯU THẤP NHẤT ĐỐI VỚI LAO ĐỘNG NỮ (PHỤ LỤC II - NGHỊ ĐỊNH 135/2020/NĐ-CP)",
        note_suffix=note_nu_pl2,
        min_row=3,
        max_row=None,
    )

    tables[1].replace_with(soup.new_string(md_dieu4_tables))
    tables[2].replace_with(soup.new_string(md_dieu5_tables))
    tables[4].replace_with(soup.new_string(f"\n\n{md_pl1_nam}\n\n{md_pl1_nu}\n\n"))
    tables[5].replace_with(soup.new_string(f"\n\n{md_pl2_nam}\n\n{md_pl2_nu}\n\n"))

    raw_lines = [l.strip() for l in soup.get_text().split("\n") if l.strip()]
    lines = []
    for l in raw_lines:
        if not lines or l != lines[-1]:
            lines.append(l)

    metadata = LegalDocumentMetadata(
        doc_id="nd_135_2020_nd_cp",
        official_number="135/2020/NĐ-CP",
        title="Nghị định quy định về tuổi nghỉ hưu",
        short_title="Nghị định 135/2020/NĐ-CP",
        doc_type=DocumentType.NGHI_DINH,
        issuer="Chính phủ",
        signer="Nguyễn Xuân Phúc",
        issue_date=date(2020, 11, 18),
        effective_date=date(2021, 1, 1),
        status=DocumentStatus.CON_HIEU_LUC,
        source_url="https://thuvienphapluat.vn/van-ban/Lao-dong-Tien-luong/Nghi-dinh-135-2020-ND-CP-tuoi-nghi-huu-445512.aspx",
        guides=["bllđ_45_2019_qh14"],
    )

    articles_data = []
    curr_art = None
    for l in lines:
        m = re.match(r"^(Điều\s+\d+)[\.:\s]*(.*)", l)
        m_pl = re.match(r"^(PHỤ\s+LỤC\s+[IVX]+)[\.:\s]*(.*)", l, re.IGNORECASE)

        if m:
            if curr_art:
                articles_data.append(curr_art)
            curr_art = {"num_str": m.group(1), "title": m.group(2).strip(), "lines": []}
        elif m_pl:
            if curr_art:
                articles_data.append(curr_art)
            pl_num = m_pl.group(1).upper()
            title_desc = "Bảng tra cứu lộ trình tuổi nghỉ hưu"
            if "I" in pl_num and "II" not in pl_num and "III" not in pl_num:
                title_desc = "Phụ lục I: Lộ trình tuổi nghỉ hưu trong điều kiện lao động bình thường gắn với tháng năm sinh"
            elif "II" in pl_num and "III" not in pl_num:
                title_desc = "Phụ lục II: Lộ trình tuổi nghỉ hưu thấp nhất gắn với tháng năm sinh"
            elif "III" in pl_num:
                title_desc = "Phụ lục III: Danh mục nghề nghiệp nặng nhọc độc hại, hầm lò, vùng ĐBKK"
            curr_art = {"num_str": pl_num, "title": title_desc, "lines": [l]}
        elif curr_art:
            curr_art["lines"].append(l)

    if curr_art:
        articles_data.append(curr_art)

    articles: List[LegalArticle] = []
    for idx, item in enumerate(articles_data, start=1):
        num_str = item["num_str"]
        art_title = item["title"]
        content_lines = item["lines"]
        if not art_title and content_lines:
            art_title = content_lines[0]
            content_lines = content_lines[1:]

        full_text = f"Điều {idx}. {art_title}\n" + "\n".join(content_lines)
        art_obj = LegalArticle(
            article_number=idx,
            article_title=f"{num_str}: {art_title}",
            full_text=full_text,
            clauses=[],
            status=DocumentStatus.CON_HIEU_LUC,
        )
        articles.append(art_obj)

    parsed_doc = LegalDocumentParsed(
        metadata=metadata,
        chapters=[
            LegalChapter(
                chapter_number="Chương I",
                chapter_title="QUY ĐỊNH VỀ TUỔI NGHỈ HƯU",
                articles=articles,
            )
        ],
        raw_articles=articles,
    )

    chunks: List[LegalChunkPayload] = []

    # Chunk Điều 1, 2, 3
    for art in articles[:3]:
        chunks.append(
            LegalChunkPayload(
                chunk_id=f"nd_135_2020_nd_cp_d{art.article_number}",
                doc_id=metadata.doc_id,
                doc_title=metadata.short_title,
                official_number=metadata.official_number,
                chapter="Chương I: QUY ĐỊNH VỀ TUỔI NGHỈ HƯU",
                article_number=art.article_number,
                article_title=art.article_title,
                clause_number=None,
                status=DocumentStatus.CON_HIEU_LUC,
                effective_date=metadata.effective_date,
                expiry_date=None,
                context_header=f"Văn bản: {metadata.title} (Số hiệu: {metadata.official_number}). Chương I. {art.article_title}.",
                content=art.full_text,
                full_search_text=f"Văn bản: {metadata.title} (Số hiệu: {metadata.official_number}). Chương I. {art.article_title}.\n{art.full_text}",
                scope_tags=["nghi_dinh", "lao_dong", "huu_tri"],
            )
        )

    # Chunk Điều 4: Phân tách rõ Nam và Nữ
    dieu4_text_nam = (
        "Điều 4. Tuổi nghỉ hưu trong điều kiện lao động bình thường — LAO ĐỘNG NAM\n"
        "1. Kể từ ngày 01 tháng 01 năm 2021, tuổi nghỉ hưu của người lao động trong điều kiện lao động bình thường là đủ 60 tuổi 03 tháng đối với lao động nam; sau đó, cứ mỗi năm tăng thêm 03 tháng đối với lao động nam cho đến khi đủ 62 tuổi vào năm 2028.\n"
        "2. Bảng lộ trình điều chỉnh tuổi nghỉ hưu đối với LAO ĐỘNG NAM:\n"
        "| Năm nghỉ hưu | Tuổi nghỉ hưu của Lao động nam |\n"
        "| :--- | :--- |\n"
        "| 2021 | 60 tuổi 3 tháng |\n"
        "| 2022 | 60 tuổi 6 tháng |\n"
        "| 2023 | 60 tuổi 9 tháng |\n"
        "| 2024 | 61 tuổi |\n"
        "| 2025 | 61 tuổi 3 tháng |\n"
        "| 2026 | 61 tuổi 6 tháng |\n"
        "| 2027 | 61 tuổi 9 tháng |\n"
        "| Từ năm 2028 trở đi | 62 tuổi |\n\n"
        "LƯU Ý ĐẶC BIỆT ĐỐI VỚI LAO ĐỘNG NAM: Kể từ năm 2028 trở đi, tuổi nghỉ hưu của nam đạt mốc tối đa là ĐỦ 62 TUỔI. Do đó, tất cả lao động nam sinh từ tháng 04/1966 trở đi (bao gồm người sinh năm 1967, 1968, 1969, 1970, 1971...) đều nghỉ hưu khi ĐỦ 62 TUỔI. Người nam sinh năm 1970 sẽ nghỉ hưu vào năm 2032 (1970 + 62 = 2032)!"
    )
    chunks.append(
        LegalChunkPayload(
            chunk_id="nd_135_2020_nd_cp_d4_nam",
            doc_id=metadata.doc_id,
            doc_title=metadata.short_title,
            official_number=metadata.official_number,
            chapter="Chương I: QUY ĐỊNH VỀ TUỔI NGHỈ HƯU",
            article_number=4,
            article_title="Điều 4: Tuổi nghỉ hưu trong điều kiện bình thường (Lao động Nam)",
            clause_number=1,
            status=DocumentStatus.CON_HIEU_LUC,
            effective_date=metadata.effective_date,
            expiry_date=None,
            context_header=f"Văn bản: {metadata.title} (Số hiệu: {metadata.official_number}). Điều 4: Tuổi nghỉ hưu trong điều kiện bình thường. ĐỐI TƯỢNG: LAO ĐỘNG NAM.",
            content=dieu4_text_nam,
            full_search_text=f"Văn bản: {metadata.title} (Số hiệu: {metadata.official_number}). Điều 4: Tuổi nghỉ hưu trong điều kiện bình thường. ĐỐI TƯỢNG: LAO ĐỘNG NAM.\n{dieu4_text_nam}",
            scope_tags=["nghi_dinh", "lao_dong", "nam", "huu_tri"],
        )
    )

    dieu4_text_nu = (
        "Điều 4. Tuổi nghỉ hưu trong điều kiện lao động bình thường — LAO ĐỘNG NỮ\n"
        "1. Kể từ ngày 01 tháng 01 năm 2021, tuổi nghỉ hưu của người lao động trong điều kiện lao động bình thường là đủ 55 tuổi 04 tháng đối với lao động nữ; sau đó, cứ mỗi năm tăng thêm 04 tháng đối với lao động nữ cho đến khi đủ 60 tuổi vào năm 2035.\n"
        "2. Bảng lộ trình điều chỉnh tuổi nghỉ hưu đối với LAO ĐỘNG NỮ:\n"
        "| Năm nghỉ hưu | Tuổi nghỉ hưu của Lao động nữ |\n"
        "| :--- | :--- |\n"
        "| 2021 | 55 tuổi 4 tháng |\n"
        "| 2022 | 55 tuổi 8 tháng |\n"
        "| 2023 | 56 tuổi |\n"
        "| 2024 | 56 tuổi 4 tháng |\n"
        "| 2025 | 56 tuổi 8 tháng |\n"
        "| 2026 | 57 tuổi |\n"
        "| 2027 | 57 tuổi 4 tháng |\n"
        "| 2028 | 57 tuổi 8 tháng |\n"
        "| 2029 | 58 tuổi |\n"
        "| 2030 | 58 tuổi 4 tháng |\n"
        "| 2031 | 58 tuổi 8 tháng |\n"
        "| 2032 | 59 tuổi |\n"
        "| 2033 | 59 tuổi 4 tháng |\n"
        "| 2034 | 59 tuổi 8 tháng |\n"
        "| Từ năm 2035 trở đi | 60 tuổi |\n\n"
        "LƯU Ý ĐỐI VỚI LAO ĐỘNG NỮ SINH NĂM 1970: Năm 2027 nữ đủ 57 tuổi. Nữ sinh từ tháng 1 đến tháng 8/1970 nghỉ hưu ở tuổi 57 tuổi 4 tháng (hưởng hưu từ tháng 6/2027 đến 1/2028). Nữ sinh từ tháng 9 đến tháng 12/1970 nghỉ hưu ở tuổi 57 tuổi 8 tháng (hưởng hưu từ tháng 6/2028 đến 9/2028)."
    )
    chunks.append(
        LegalChunkPayload(
            chunk_id="nd_135_2020_nd_cp_d4_nu",
            doc_id=metadata.doc_id,
            doc_title=metadata.short_title,
            official_number=metadata.official_number,
            chapter="Chương I: QUY ĐỊNH VỀ TUỔI NGHỈ HƯU",
            article_number=4,
            article_title="Điều 4: Tuổi nghỉ hưu trong điều kiện bình thường (Lao động Nữ)",
            clause_number=2,
            status=DocumentStatus.CON_HIEU_LUC,
            effective_date=metadata.effective_date,
            expiry_date=None,
            context_header=f"Văn bản: {metadata.title} (Số hiệu: {metadata.official_number}). Điều 4: Tuổi nghỉ hưu trong điều kiện bình thường. ĐỐI TƯỢNG: LAO ĐỘNG NỮ.",
            content=dieu4_text_nu,
            full_search_text=f"Văn bản: {metadata.title} (Số hiệu: {metadata.official_number}). Điều 4: Tuổi nghỉ hưu trong điều kiện bình thường. ĐỐI TƯỢNG: LAO ĐỘNG NỮ.\n{dieu4_text_nu}",
            scope_tags=["nghi_dinh", "lao_dong", "nu", "huu_tri"],
        )
    )

    # Chunk Điều 5 đến 9
    for art in articles[4:9]:
        chunks.append(
            LegalChunkPayload(
                chunk_id=f"nd_135_2020_nd_cp_d{art.article_number}",
                doc_id=metadata.doc_id,
                doc_title=metadata.short_title,
                official_number=metadata.official_number,
                chapter="Chương I: QUY ĐỊNH VỀ TUỔI NGHỈ HƯU",
                article_number=art.article_number,
                article_title=art.article_title,
                clause_number=None,
                status=DocumentStatus.CON_HIEU_LUC,
                effective_date=metadata.effective_date,
                expiry_date=None,
                context_header=f"Văn bản: {metadata.title} (Số hiệu: {metadata.official_number}). {art.article_title}.",
                content=art.full_text[:3500],
                full_search_text=f"Văn bản: {metadata.title} (Số hiệu: {metadata.official_number}). {art.article_title}.\n{art.full_text[:3500]}",
                scope_tags=["nghi_dinh", "lao_dong", "huu_tri"],
            )
        )

    # Phụ lục I - Lao động Nam
    chunks.append(
        LegalChunkPayload(
            chunk_id="nd_135_2020_nd_cp_pl1_nam",
            doc_id=metadata.doc_id,
            doc_title=metadata.short_title,
            official_number=metadata.official_number,
            chapter="Chương I: QUY ĐỊNH VỀ TUỔI NGHỈ HƯU",
            article_number=10,
            article_title="Phụ lục I: Lộ trình tuổi nghỉ hưu điều kiện bình thường (LAO ĐỘNG NAM)",
            clause_number=1,
            status=DocumentStatus.CON_HIEU_LUC,
            effective_date=metadata.effective_date,
            expiry_date=None,
            context_header=(
                f"Văn bản: {metadata.title} (Số hiệu: {metadata.official_number}). "
                "Phụ lục I: BẢNG TRA CỨU TUỔI NGHỈ HƯU ĐỐI VỚI LAO ĐỘNG NAM THEO THÁNG NĂM SINH. "
                "ĐỐI TƯỢNG: LAO ĐỘNG NAM ĐIỀU KIỆN BÌNH THƯỜNG."
            ),
            content=md_pl1_nam,
            full_search_text=(
                f"Văn bản: {metadata.title} (Số hiệu: {metadata.official_number}). "
                "Phụ lục I: BẢNG TRA CỨU TUỔI NGHỈ HƯU ĐỐI VỚI LAO ĐỘNG NAM THEO THÁNG NĂM SINH. "
                f"ĐỐI TƯỢNG: LAO ĐỘNG NAM ĐIỀU KIỆN BÌNH THƯỜNG.\n{md_pl1_nam}"
            ),
            scope_tags=["nghi_dinh", "lao_dong", "nam", "huu_tri", "phu_luc"],
        )
    )

    # Phụ lục I - Lao động Nữ
    nu_lines_all = md_pl1_nu.split("\n")
    nu_header = nu_lines_all[:3]
    nu_rows_p1 = [l for l in nu_lines_all[3:] if any(y in l for y in ["1966", "1967", "1968", "1969", "1970"])]
    nu_md_p1 = "\n".join(nu_header + nu_rows_p1) + "\n\n" + note_nu_pl1

    nu_rows_p2 = [l for l in nu_lines_all[3:] if any(y in l for y in ["1971", "1972", "1973", "1974", "1975"])]
    nu_md_p2 = "\n".join(nu_header + nu_rows_p2) + "\n\n" + note_nu_pl1

    chunks.append(
        LegalChunkPayload(
            chunk_id="nd_135_2020_nd_cp_pl1_nu_p1",
            doc_id=metadata.doc_id,
            doc_title=metadata.short_title,
            official_number=metadata.official_number,
            chapter="Chương I: QUY ĐỊNH VỀ TUỔI NGHỈ HƯU",
            article_number=10,
            article_title="Phụ lục I: Lộ trình tuổi nghỉ hưu điều kiện bình thường (LAO ĐỘNG NỮ sinh 1966 - 1970)",
            clause_number=2,
            status=DocumentStatus.CON_HIEU_LUC,
            effective_date=metadata.effective_date,
            expiry_date=None,
            context_header=(
                f"Văn bản: {metadata.title} (Số hiệu: {metadata.official_number}). "
                "Phụ lục I: BẢNG TRA CỨU TUỔI NGHỈ HƯU ĐỐI VỚI LAO ĐỘNG NỮ SINH NĂM 1966 ĐẾN 1970. "
                "ĐỐI TƯỢNG: LAO ĐỘNG NỮ ĐIỀU KIỆN BÌNH THƯỜNG."
            ),
            content=nu_md_p1,
            full_search_text=(
                f"Văn bản: {metadata.title} (Số hiệu: {metadata.official_number}). "
                "Phụ lục I: BẢNG TRA CỨU TUỔI NGHỈ HƯU ĐỐI VỚI LAO ĐỘNG NỮ SINH NĂM 1966 ĐẾN 1970. "
                f"ĐỐI TƯỢNG: LAO ĐỘNG NỮ ĐIỀU KIỆN BÌNH THƯỜNG.\n{nu_md_p1}"
            ),
            scope_tags=["nghi_dinh", "lao_dong", "nu", "huu_tri", "phu_luc"],
        )
    )

    chunks.append(
        LegalChunkPayload(
            chunk_id="nd_135_2020_nd_cp_pl1_nu_p2",
            doc_id=metadata.doc_id,
            doc_title=metadata.short_title,
            official_number=metadata.official_number,
            chapter="Chương I: QUY ĐỊNH VỀ TUỔI NGHỈ HƯU",
            article_number=10,
            article_title="Phụ lục I: Lộ trình tuổi nghỉ hưu điều kiện bình thường (LAO ĐỘNG NỮ sinh 1971 - 1975)",
            clause_number=3,
            status=DocumentStatus.CON_HIEU_LUC,
            effective_date=metadata.effective_date,
            expiry_date=None,
            context_header=(
                f"Văn bản: {metadata.title} (Số hiệu: {metadata.official_number}). "
                "Phụ lục I: BẢNG TRA CỨU TUỔI NGHỈ HƯU ĐỐI VỚI LAO ĐỘNG NỮ SINH NĂM 1971 ĐẾN 1975. "
                "ĐỐI TƯỢNG: LAO ĐỘNG NỮ ĐIỀU KIỆN BÌNH THƯỜNG."
            ),
            content=nu_md_p2,
            full_search_text=(
                f"Văn bản: {metadata.title} (Số hiệu: {metadata.official_number}). "
                "Phụ lục I: BẢNG TRA CỨU TUỔI NGHỈ HƯU ĐỐI VỚI LAO ĐỘNG NỮ SINH NĂM 1971 ĐẾN 1975. "
                f"ĐỐI TƯỢNG: LAO ĐỘNG NỮ ĐIỀU KIỆN BÌNH THƯỜNG.\n{nu_md_p2}"
            ),
            scope_tags=["nghi_dinh", "lao_dong", "nu", "huu_tri", "phu_luc"],
        )
    )

    # Phụ lục II - Nam & Nữ
    chunks.append(
        LegalChunkPayload(
            chunk_id="nd_135_2020_nd_cp_pl2_nam",
            doc_id=metadata.doc_id,
            doc_title=metadata.short_title,
            official_number=metadata.official_number,
            chapter="Chương I: QUY ĐỊNH VỀ TUỔI NGHỈ HƯU",
            article_number=11,
            article_title="Phụ lục II: Lộ trình tuổi nghỉ hưu thấp nhất (LAO ĐỘNG NAM)",
            clause_number=1,
            status=DocumentStatus.CON_HIEU_LUC,
            effective_date=metadata.effective_date,
            expiry_date=None,
            context_header=f"Văn bản: {metadata.title} (Số hiệu: {metadata.official_number}). Phụ lục II: TUỔI NGHỈ HƯU THẤP NHẤT LAO ĐỘNG NAM (nặng nhọc độc hại).",
            content=md_pl2_nam,
            full_search_text=f"Văn bản: {metadata.title} (Số hiệu: {metadata.official_number}). Phụ lục II: TUỔI NGHỈ HƯU THẤP NHẤT LAO ĐỘNG NAM (nặng nhọc độc hại).\n{md_pl2_nam}",
            scope_tags=["nghi_dinh", "lao_dong", "nam", "huu_tri", "nang_nhoc"],
        )
    )

    chunks.append(
        LegalChunkPayload(
            chunk_id="nd_135_2020_nd_cp_pl2_nu",
            doc_id=metadata.doc_id,
            doc_title=metadata.short_title,
            official_number=metadata.official_number,
            chapter="Chương I: QUY ĐỊNH VỀ TUỔI NGHỈ HƯU",
            article_number=11,
            article_title="Phụ lục II: Lộ trình tuổi nghỉ hưu thấp nhất (LAO ĐỘNG NỮ)",
            clause_number=2,
            status=DocumentStatus.CON_HIEU_LUC,
            effective_date=metadata.effective_date,
            expiry_date=None,
            context_header=f"Văn bản: {metadata.title} (Số hiệu: {metadata.official_number}). Phụ lục II: TUỔI NGHỈ HƯU THẤP NHẤT LAO ĐỘNG NỮ (nặng nhọc độc hại).",
            content=md_pl2_nu,
            full_search_text=f"Văn bản: {metadata.title} (Số hiệu: {metadata.official_number}). Phụ lục II: TUỔI NGHỈ HƯU THẤP NHẤT LAO ĐỘNG NỮ (nặng nhọc độc hại).\n{md_pl2_nu}",
            scope_tags=["nghi_dinh", "lao_dong", "nu", "huu_tri", "nang_nhoc"],
        )
    )

    # Phụ lục III
    if len(articles) > 11:
        art_pl3 = articles[11]
        chunks.append(
            LegalChunkPayload(
                chunk_id="nd_135_2020_nd_cp_pl3",
                doc_id=metadata.doc_id,
                doc_title=metadata.short_title,
                official_number=metadata.official_number,
                chapter="Chương I: QUY ĐỊNH VỀ TUỔI NGHỈ HƯU",
                article_number=12,
                article_title="Phụ lục III: Danh mục nghề nghiệp nặng nhọc độc hại",
                clause_number=None,
                status=DocumentStatus.CON_HIEU_LUC,
                effective_date=metadata.effective_date,
                expiry_date=None,
                context_header=f"Văn bản: {metadata.title} (Số hiệu: {metadata.official_number}). Phụ lục III: Nghề nặng nhọc độc hại.",
                content=art_pl3.full_text[:3500],
                full_search_text=f"Văn bản: {metadata.title} (Số hiệu: {metadata.official_number}). Phụ lục III: Nghề nặng nhọc độc hại.\n{art_pl3.full_text[:3500]}",
                scope_tags=["nghi_dinh", "lao_dong", "nang_nhoc"],
            )
        )

    return parsed_doc, chunks


def run_reingest():
    print("=" * 70)
    print("   VIETLEGAL AI - TÁI BÓC TÁCH & NẠP LẠI NGHỊ ĐỊNH 135/2020/NĐ-CP")
    print("   Khắc phục triệt để lỗi bảng biểu, rowspan và phân định Nam/Nữ")
    print("=" * 70)

    parsed_doc, chunks = build_curated_nd135()
    print(f"\n[1/4] Đã chuẩn hóa toàn văn NĐ 135 thành {len(parsed_doc.raw_articles)} Điều/Phụ lục.")
    print(f" [+] Đã sinh thành công {len(chunks)} chunks phân tách Nam/Nữ chuyên biệt.")

    curated_dir = PROJECT_ROOT / "data" / "04_curated_chunks"
    curated_dir.mkdir(parents=True, exist_ok=True)
    jsonl_path = curated_dir / "nd_135_2020_nd_cp_chunks.jsonl"
    with open(jsonl_path, "w", encoding="utf-8") as f:
        for c in chunks:
            f.write(c.model_dump_json() + "\n")
    print(f" [+] Đã ghi lại file chunks: {jsonl_path.name}")

    print("\n[2/4] Đồng bộ Điều/Phụ lục chuẩn hóa lên Supabase PostgreSQL...")
    supabase_loader = SupabaseLegalLoader()
    res = supabase_loader.sync_parsed_document(parsed_doc)
    print(f" [+] Supabase sync result: doc_synced={res['document_synced']}, articles_count={res['articles_count']}")

    print("\n[3/4] Tính toán Vector Embeddings với BAAI/bge-m3 (CUDA GPU FP16)...")
    embed_service = get_embedding_service()
    texts_to_embed = [c.full_search_text for c in chunks]
    t0 = time.time()
    embed_service.model.max_seq_length = 2048
    raw_vecs = embed_service.model.encode(
        texts_to_embed,
        batch_size=4,
        normalize_embeddings=True,
        show_progress_bar=True,
    )
    vectors = raw_vecs.tolist()
    elapsed = time.time() - t0
    print(f" [+] Đã tạo thành công {len(vectors)} vectors (dim={len(vectors[0])}) trong {elapsed:.2f}s!")

    print("\n[4/4] Cập nhật Vector Store Qdrant...")
    vector_store = QdrantVectorStore(collection_name="vietlegal_articles")
    vector_store.ensure_collection(vector_size=1024, recreate=False)

    try:
        vector_store.client.delete(
            collection_name=vector_store.collection_name,
            points_selector=qmodels.FilterSelector(
                filter=qmodels.Filter(
                    must=[
                        qmodels.FieldCondition(
                            key="doc_id",
                            match=qmodels.MatchValue(value="nd_135_2020_nd_cp"),
                        )
                    ]
                )
            ),
        )
        print(" [+] Đã xóa các vector cũ của Nghị định 135 trong Qdrant.")
    except Exception as e:
        print(f" [!] Ghi chú xóa cũ: {e}")

    uploaded = vector_store.insert_chunks(chunks=chunks, embeddings=vectors, batch_size=50)
    print(f" [+] Đã nạp thành công {uploaded} vectors mới của NĐ 135 vào Qdrant!")

    total_vectors = vector_store.client.count(collection_name=vector_store.collection_name).count
    print(f" [+] Tổng số vector hiện có trong Qdrant 'vietlegal_articles': {total_vectors} vectors!")

    print("\n" + "=" * 70)
    print("[SUCCESS] HOÀN TẤT TÁI CẤU TRÚC VÀ NẠP LẠI NGHỊ ĐỊNH 135/2020/NĐ-CP!")
    print("=" * 70)


if __name__ == "__main__":
    run_reingest()
