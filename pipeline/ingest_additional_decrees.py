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
from pipeline.parsers.legal_hierarchical_parser import LegalHierarchicalParser
from pipeline.loaders.supabase_loader import SupabaseLegalLoader
from backend.app.services.rag.embeddings import get_embedding_service
from backend.app.services.rag.vector_store import QdrantVectorStore


def table_to_markdown(table_tag) -> str:
    """Chuyển đổi thẻ HTML table thành bảng Markdown rõ ràng."""
    rows = table_tag.find_all("tr")
    md_lines = []
    for r_idx, row in enumerate(rows):
        cells = [c.get_text().strip().replace("\n", " ") for c in row.find_all(["td", "th"])]
        if not any(cells):
            continue
        line = "| " + " | ".join(cells) + " |"
        md_lines.append(line)
        if r_idx == 0:
            sep = "| " + " | ".join(["---"] * len(cells)) + " |"
            md_lines.append(sep)
    return "\n\n" + "\n".join(md_lines) + "\n\n"


def parse_nd74(html_path: Path) -> LegalDocumentParsed:
    """Bóc tách toàn văn Nghị định 74/2024/NĐ-CP (Lương tối thiểu vùng)."""
    with open(html_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f.read(), "html.parser")

    for t in soup.find_all("table"):
        md_table = table_to_markdown(t)
        t.replace_with(soup.new_string(md_table))

    raw_lines = [l.strip() for l in soup.get_text().split("\n") if l.strip()]
    lines = []
    for l in raw_lines:
        if not lines or l != lines[-1]:
            lines.append(l)

    metadata = LegalDocumentMetadata(
        doc_id="nd_74_2024_nd_cp",
        official_number="74/2024/NĐ-CP",
        title="Nghị định quy định mức lương tối thiểu đối với người lao động làm việc theo hợp đồng lao động",
        short_title="Nghị định 74/2024/NĐ-CP",
        doc_type=DocumentType.NGHI_DINH,
        issuer="Chính phủ",
        signer="Lê Minh Khái",
        issue_date=date(2024, 6, 30),
        effective_date=date(2024, 7, 1),
        status=DocumentStatus.CON_HIEU_LUC,
        source_url="https://thuvienphapluat.vn/van-ban/Lao-dong-Tien-luong/Nghi-dinh-74-2024-ND-CP-muc-luong-toi-thieu-lao-dong-lam-viec-theo-hop-dong-603278.aspx",
        guides=["bllđ_45_2019_qh14"],
        replaces=["38/2022/NĐ-CP"],
    )

    articles_data = []
    curr_art = None
    for l in lines:
        m = re.match(r"^(Điều\s+\d+)[\.:\s]*(.*)", l)
        m_pl = re.match(r"^(PHỤ\s+LỤC\b.*)", l, re.IGNORECASE) if not m else None

        if m:
            if curr_art:
                articles_data.append(curr_art)
            curr_art = {"num_str": m.group(1), "title": m.group(2).strip(), "lines": []}
        elif m_pl and not any(a["num_str"] == "Phụ lục" for a in articles_data):
            if curr_art:
                articles_data.append(curr_art)
            curr_art = {
                "num_str": "Phụ lục",
                "title": "Danh mục địa bàn áp dụng mức lương tối thiểu vùng I, II, III, IV từ 01/07/2024",
                "lines": [l],
            }
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

        clean_blocks = []
        curr_block = []
        for l in content_lines:
            if l.startswith("|") or re.match(r"^(\d+\.|\bKhoản\s+\d+|[a-zđ]\)|Vùng\s+[I|V|X]+:)", l, re.IGNORECASE):
                if curr_block:
                    clean_blocks.append(" ".join(curr_block))
                    curr_block = []
            if l.startswith("|"):
                clean_blocks.append(l)
            else:
                curr_block.append(l)
        if curr_block:
            clean_blocks.append(" ".join(curr_block))

        full_text = f"Điều {idx}. {art_title}\n" + "\n".join(clean_blocks)

        clauses: List[LegalClause] = []
        curr_cl: LegalClause = None
        for block in clean_blocks:
            cl_m = re.match(r"^(\d+)\.\s*(.*)", block)
            if cl_m:
                if curr_cl:
                    clauses.append(curr_cl)
                curr_cl = LegalClause(
                    clause_number=int(cl_m.group(1)),
                    text=cl_m.group(2).strip(),
                    points=[],
                )
            else:
                pt_m = re.match(r"^([a-zđ])\)\s*(.*)", block, re.IGNORECASE)
                if pt_m and curr_cl:
                    curr_cl.points.append(
                        LegalPoint(point_letter=pt_m.group(1).lower(), text=pt_m.group(2).strip())
                    )
                elif curr_cl:
                    curr_cl.text += f"\n{block}"
                else:
                    if not clauses:
                        curr_cl = LegalClause(clause_number=1, text=block, points=[])
                    else:
                        clauses[-1].text += f"\n{block}"
        if curr_cl:
            clauses.append(curr_cl)

        art_obj = LegalArticle(
            article_number=idx,
            article_title=f"{num_str}: {art_title}",
            full_text=full_text,
            clauses=clauses,
            status=DocumentStatus.CON_HIEU_LUC,
        )
        articles.append(art_obj)

    parsed_doc = LegalDocumentParsed(
        metadata=metadata,
        chapters=[
            LegalChapter(
                chapter_number="Chương I",
                chapter_title="QUY ĐỊNH CHUNG VỀ MỨC LƯƠNG TỐI THIỂU VÙNG",
                articles=articles,
            )
        ],
        raw_articles=articles,
    )
    return parsed_doc


def parse_nd135(html_path: Path) -> LegalDocumentParsed:
    """Bóc tách toàn văn Nghị định 135/2020/NĐ-CP (Tuổi nghỉ hưu)."""
    with open(html_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f.read(), "html.parser")

    for t in soup.find_all("table"):
        md_table = table_to_markdown(t)
        t.replace_with(soup.new_string(md_table))

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

        clean_blocks = []
        curr_block = []
        for l in content_lines:
            if l.startswith("|") or re.match(r"^(\d+\.|\bKhoản\s+\d+|[a-zđ]\))", l, re.IGNORECASE):
                if curr_block:
                    clean_blocks.append(" ".join(curr_block))
                    curr_block = []
            if l.startswith("|"):
                clean_blocks.append(l)
            else:
                curr_block.append(l)
        if curr_block:
            clean_blocks.append(" ".join(curr_block))

        full_text = f"Điều {idx}. {art_title}\n" + "\n".join(clean_blocks)

        clauses: List[LegalClause] = []
        curr_cl: LegalClause = None
        for block in clean_blocks:
            cl_m = re.match(r"^(\d+)\.\s*(.*)", block)
            if cl_m:
                if curr_cl:
                    clauses.append(curr_cl)
                curr_cl = LegalClause(
                    clause_number=int(cl_m.group(1)),
                    text=cl_m.group(2).strip(),
                    points=[],
                )
            else:
                pt_m = re.match(r"^([a-zđ])\)\s*(.*)", block, re.IGNORECASE)
                if pt_m and curr_cl:
                    curr_cl.points.append(
                        LegalPoint(point_letter=pt_m.group(1).lower(), text=pt_m.group(2).strip())
                    )
                elif curr_cl:
                    curr_cl.text += f"\n{block}"
                else:
                    if not clauses:
                        curr_cl = LegalClause(clause_number=1, text=block, points=[])
                    else:
                        clauses[-1].text += f"\n{block}"
        if curr_cl:
            clauses.append(curr_cl)

        art_obj = LegalArticle(
            article_number=idx,
            article_title=f"{num_str}: {art_title}",
            full_text=full_text,
            clauses=clauses,
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
    return parsed_doc


def run_ingestion():
    print("=" * 70)
    print("   VIETLEGAL AI - INGESTION NGHỊ ĐỊNH 74/2024 & NGHỊ ĐỊNH 135/2020")
    print("=" * 70)

    nd74_html = PROJECT_ROOT / "data" / "01_raw" / "html" / "74_2024_ND_CP.html"
    nd135_html = PROJECT_ROOT / "data" / "01_raw" / "html" / "135_2020_ND_CP.html"

    docs_to_process = [
        ("Nghị định 74/2024/NĐ-CP (Lương tối thiểu vùng)", parse_nd74(nd74_html)),
        ("Nghị định 135/2020/NĐ-CP (Tuổi nghỉ hưu)", parse_nd135(nd135_html)),
    ]

    all_chunks: List[LegalChunkPayload] = []
    parser = LegalHierarchicalParser()
    curated_dir = PROJECT_ROOT / "data" / "04_curated_chunks"
    curated_dir.mkdir(parents=True, exist_ok=True)

    # 1. Bóc tách và tạo Chunks
    for doc_name, parsed_doc in docs_to_process:
        doc_meta = parsed_doc.metadata
        print(f"\n[1/4] Xử lý văn bản: {doc_name} ({len(parsed_doc.raw_articles)} Điều/Phụ lục)...")
        chunks = parser.create_chunks(parsed_doc)
        print(f" [+] Đã sinh: {len(chunks)} chunks phân cấp chuẩn.")
        all_chunks.extend(chunks)

        # Lưu chunks jsonl
        jsonl_path = curated_dir / f"{doc_meta.doc_id}_chunks.jsonl"
        with open(jsonl_path, "w", encoding="utf-8") as f:
            for c in chunks:
                f.write(c.model_dump_json() + "\n")
        print(f" [+] Ghi file chunks: {jsonl_path.name}")

    # 2. Đồng bộ lên Supabase Cloud Database (legal_documents & legal_articles)
    print("\n[2/4] Đồng bộ dữ liệu lên Supabase Cloud (PostgreSQL)...")
    supabase_loader = SupabaseLegalLoader()
    for doc_name, parsed_doc in docs_to_process:
        res = supabase_loader.sync_parsed_document(parsed_doc)
        print(f" [+] {parsed_doc.metadata.short_title}: doc_synced={res['document_synced']}, articles_count={res['articles_count']}")

    # 3. Tính toán Vector Embeddings với BAAI/bge-m3 (CUDA GPU FP16)
    vec_path = curated_dir / "additional_decrees_vectors.npy"
    if vec_path.exists():
        print(f" [+] Tải {len(all_chunks)} vectors từ bộ nhớ đệm: {vec_path.name}")
        vectors = np.load(vec_path).tolist()
    else:
        embed_service = get_embedding_service()
        texts_to_embed = [c.full_search_text for c in all_chunks]
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
        np.save(vec_path, np.array(vectors, dtype=np.float32))
        print(f" [+] Đã lưu vectors vào bộ nhớ đệm: {vec_path.name}")

    # 4. Nạp vào Qdrant Vector Store (Bảo toàn 100% dữ liệu cũ: recreate=False)
    print("\n[4/4] Nạp Vector Chunks vào Qdrant Vector Store (recreate=False)...")
    vector_store = QdrantVectorStore(collection_name="vietlegal_articles")
    vector_store.ensure_collection(vector_size=1024, recreate=False)
    uploaded = vector_store.insert_chunks(chunks=all_chunks, embeddings=vectors, batch_size=50)
    print(f" [+] Đã nạp thành công {uploaded} chunks vào Qdrant!")

    total_vectors = vector_store.client.count(collection_name=vector_store.collection_name).count
    print(f" [+] Qdrant collection 'vietlegal_articles' hiện có tổng cộng: {total_vectors} vectors!")

    print("\n" + "=" * 70)
    print("[SUCCESS] ĐÃ NẠP HOÀN TẤT NGHỊ ĐỊNH 74/2024 VÀ NGHỊ ĐỊNH 135/2020!")
    print("=" * 70)


if __name__ == "__main__":
    run_ingestion()
