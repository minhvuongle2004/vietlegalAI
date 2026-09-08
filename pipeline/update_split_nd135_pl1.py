import os
import sys
import uuid
import time
from pathlib import Path
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")
sys.path.insert(0, str(PROJECT_ROOT))

from bs4 import BeautifulSoup
import requests
from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels

from pipeline.reingest_nd135_tables import (
    html_table_to_matrix,
    format_subtable_markdown,
)
from pipeline.models import LegalChunkPayload, DocumentStatus
from backend.app.services.rag.embeddings import get_embedding_service
from backend.app.services.rag.vector_store import QdrantVectorStore

def run_update():
    print("=" * 80)
    print("  TÁCH PHỤ LỤC I NĐ 135 THÀNH 2 EVIDENCE UNITS: BẢNG NAM VÀ BẢNG NỮ")
    print("=" * 80)

    # 1. Trích xuất bảng Markdown chuẩn từ HTML gốc
    html_path = PROJECT_ROOT / "data" / "01_raw" / "html" / "135_2020_ND_CP.html"
    with open(html_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f.read(), "html.parser")

    tables = soup.find_all("table")
    grid_t5 = html_table_to_matrix(tables[4])

    note_nam_pl1 = (
        "> **QUY TẮC PHÁP LÝ BẮT BUỘC ĐỐI VỚI LAO ĐỘNG NAM (ĐIỀU KIỆN LAO ĐỘNG BÌNH THƯỜNG)**:\n"
        "> 1. Theo Điều 4 và Phụ lục I Nghị định 135/2020/NĐ-CP, lộ trình tăng tuổi nghỉ hưu của nam kết thúc vào năm 2028 ở mốc đủ 62 tuổi.\n"
        "> 2. **Tất cả lao động nam sinh từ tháng 04/1966 trở đi (bao gồm các năm 1967, 1968, 1969, 1970, 1971, 1972... trở về sau) đều nghỉ hưu khi ĐỦ 62 TUỔI**.\n"
        "> 3. **Thời điểm nghỉ hưu**: Kết thúc ngày cuối cùng của tháng người lao động đủ 62 tuổi.\n"
        "> 4. **Thời điểm hưởng lương hưu**: Bắt đầu ngày đầu tiên của tháng liền kề sau thời điểm nghỉ hưu (Năm hưởng lương hưu = Năm sinh + 62)."
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
        "> 2. Kể từ tháng 01/1975 trở đi, lao động nữ nghỉ hưu khi đủ 60 tuổi."
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

    # 2. Cập nhật Supabase
    print("\n[1/3] Cập nhật bảng legal_articles trên Supabase...")
    url = os.getenv("SUPABASE_URL", "").rstrip("/")
    key = os.getenv("SUPABASE_KEY", "")
    headers = {
        "apikey": key,
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "Prefer": "resolution=merge-duplicates",
    }

    # Article 10: Phụ lục I - Nam
    payload_art10 = {
        "document_id": "nd_135_2020_nd_cp",
        "article_number": 10,
        "article_title": "Phụ lục I: Lộ trình tuổi nghỉ hưu điều kiện bình thường (LAO ĐỘNG NAM)",
        "full_text": f"Phụ lục I: Lộ trình tuổi nghỉ hưu đối với Lao động Nam trong điều kiện bình thường\n\n{md_pl1_nam}",
        "chapter_info": "Chương I: QUY ĐỊNH VỀ TUỔI NGHỈ HƯU",
        "status": "CON_HIEU_LUC",
    }
    r10 = requests.post(f"{url}/rest/v1/legal_articles", json=payload_art10, headers=headers)
    print(f"  [+] Upsert Điều 10 (Nam) Supabase: {r10.status_code}")

    # Article 13: Phụ lục I - Nữ
    payload_art13 = {
        "document_id": "nd_135_2020_nd_cp",
        "article_number": 13,
        "article_title": "Phụ lục I: Lộ trình tuổi nghỉ hưu điều kiện bình thường (LAO ĐỘNG NỮ)",
        "full_text": f"Phụ lục I: Lộ trình tuổi nghỉ hưu đối với Lao động Nữ trong điều kiện bình thường\n\n{md_pl1_nu}",
        "chapter_info": "Chương I: QUY ĐỊNH VỀ TUỔI NGHỈ HƯU",
        "status": "CON_HIEU_LUC",
    }
    r13 = requests.post(f"{url}/rest/v1/legal_articles", json=payload_art13, headers=headers)
    print(f"  [+] Upsert Điều 13 (Nữ) Supabase: {r13.status_code}")

    # 3. Tạo 2 LegalChunkPayload
    print("\n[2/3] Tính toán Vector Embeddings cho 2 chunks mới...")
    from datetime import date
    eff_date = date(2021, 1, 1)

    chunk_nam = LegalChunkPayload(
        chunk_id="nd_135_2020_nd_cp_pl1_nam",
        doc_id="nd_135_2020_nd_cp",
        doc_title="Nghị định 135/2020/NĐ-CP",
        official_number="135/2020/NĐ-CP",
        chapter="Chương I: QUY ĐỊNH VỀ TUỔI NGHỈ HƯU",
        article_number=10,
        article_title="Phụ lục I: Lộ trình tuổi nghỉ hưu điều kiện bình thường (LAO ĐỘNG NAM)",
        clause_number=1,
        status=DocumentStatus.CON_HIEU_LUC,
        effective_date=eff_date,
        expiry_date=None,
        context_header="Văn bản: Nghị định 135/2020/NĐ-CP. Chương I. Phụ lục I: BẢNG TRA CỨU TUỔI NGHỈ HƯU ĐỐI VỚI LAO ĐỘNG NAM THEO THÁNG NĂM SINH. ĐỐI TƯỢNG: LAO ĐỘNG NAM ĐIỀU KIỆN BÌNH THƯỜNG.",
        content=md_pl1_nam,
        full_search_text=f"Văn bản: Nghị định 135/2020/NĐ-CP. Chương I. Phụ lục I: BẢNG TRA CỨU TUỔI NGHỈ HƯU ĐỐI VỚI LAO ĐỘNG NAM THEO THÁNG NĂM SINH. ĐỐI TƯỢNG: LAO ĐỘNG NAM ĐIỀU KIỆN BÌNH THƯỜNG.\n{md_pl1_nam}",
        scope_tags=["nghi_dinh", "lao_dong", "nam", "huu_tri", "phu_luc"],
    )

    chunk_nu = LegalChunkPayload(
        chunk_id="nd_135_2020_nd_cp_pl1_nu",
        doc_id="nd_135_2020_nd_cp",
        doc_title="Nghị định 135/2020/NĐ-CP",
        official_number="135/2020/NĐ-CP",
        chapter="Chương I: QUY ĐỊNH VỀ TUỔI NGHỈ HƯU",
        article_number=13,
        article_title="Phụ lục I: Lộ trình tuổi nghỉ hưu điều kiện bình thường (LAO ĐỘNG NỮ)",
        clause_number=2,
        status=DocumentStatus.CON_HIEU_LUC,
        effective_date=eff_date,
        expiry_date=None,
        context_header="Văn bản: Nghị định 135/2020/NĐ-CP. Chương I. Phụ lục I: BẢNG TRA CỨU TUỔI NGHỈ HƯU ĐỐI VỚI LAO ĐỘNG NỮ THEO THÁNG NĂM SINH. ĐỐI TƯỢNG: LAO ĐỘNG NỮ ĐIỀU KIỆN BÌNH THƯỜNG.",
        content=md_pl1_nu,
        full_search_text=f"Văn bản: Nghị định 135/2020/NĐ-CP. Chương I. Phụ lục I: BẢNG TRA CỨU TUỔI NGHỈ HƯU ĐỐI VỚI LAO ĐỘNG NỮ THEO THÁNG NĂM SINH. ĐỐI TƯỢNG: LAO ĐỘNG NỮ ĐIỀU KIỆN BÌNH THƯỜNG.\n{md_pl1_nu}",
        scope_tags=["nghi_dinh", "lao_dong", "nu", "huu_tri", "phu_luc"],
    )

    chunks = [chunk_nam, chunk_nu]
    embed_service = get_embedding_service()
    embed_service.model.max_seq_length = 2048
    raw_vecs = embed_service.model.encode(
        [c.full_search_text for c in chunks],
        normalize_embeddings=True,
    )
    vectors = raw_vecs.tolist()
    print(f"  [+] Đã tạo {len(vectors)} vectors thành công.")

    # 4. Cập nhật Qdrant
    print("\n[3/3] Nạp vào Qdrant Vector Store...")
    vector_store = QdrantVectorStore(collection_name="vietlegal_articles")
    
    # Xóa các chunk cũ có thể bị trùng của pl1
    old_ids = [
        str(uuid.uuid5(uuid.NAMESPACE_DNS, "nd_135_2020_nd_cp_pl1_nam")),
        str(uuid.uuid5(uuid.NAMESPACE_DNS, "nd_135_2020_nd_cp_pl1_nu")),
        str(uuid.uuid5(uuid.NAMESPACE_DNS, "nd_135_2020_nd_cp_pl1_nu_p1")),
        str(uuid.uuid5(uuid.NAMESPACE_DNS, "nd_135_2020_nd_cp_pl1_nu_p2")),
    ]
    try:
        vector_store.client.delete(
            collection_name=vector_store.collection_name,
            points_selector=qmodels.PointIdsList(points=old_ids),
        )
        print("  [+] Đã dọn dẹp các point ID cũ của Phụ lục I.")
    except Exception as e:
        print(f"  [!] Lưu ý dọn dẹp: {e}")

    uploaded = vector_store.insert_chunks(chunks=chunks, embeddings=vectors)
    print(f"  [+] Đã nạp thành công {uploaded} chunks mới vào Qdrant!")

    print("\n" + "=" * 80)
    print("  [HOÀN TẤT] Đã tách Phụ lục I thành 2 chunks Nam (Đ10) và Nữ (Đ13)!")
    print("=" * 80)

if __name__ == "__main__":
    run_update()
