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


CHAPTERS_METADATA = [
    ("Chương I", "NHỮNG QUY ĐỊNH CHUNG", 1, 16),
    ("Chương II", "THÀNH LẬP DOANH NGHIỆP", 17, 45),
    ("Chương III", "CÔNG TY TRÁCH NHIỆM HỮU HẠN", 46, 87),
    ("Chương IV", "DOANH NGHIỆP NHÀ NƯỚC", 88, 110),
    ("Chương V", "CÔNG TY CỔ PHẦN", 111, 176),
    ("Chương VI", "CÔNG TY HỢP DANH", 177, 187),
    ("Chương VII", "DOANH NGHIỆP TƯ NHÂN", 188, 193),
    ("Chương VIII", "NHÓM CÔNG TY", 194, 197),
    ("Chương IX", "TỔ CHỨC LẠI, GIẢI THỂ VÀ PHÁ SẢN DOANH NGHIỆP", 198, 214),
    ("Chương X", "ĐIỀU KHOẢN THI HÀNH", 215, 218),
]


def get_chapter_for_article(art_num: int) -> Tuple[str, str]:
    for chap_id, chap_title, start_art, end_art in CHAPTERS_METADATA:
        if start_art <= art_num <= end_art:
            return chap_id, chap_title
    return "Chương X", "ĐIỀU KHOẢN THI HÀNH"


def parse_ldn_2020(html_path: Path) -> LegalDocumentParsed:
    """Bóc tách toàn văn Luật Doanh nghiệp 2020 (59/2020/QH14) chuẩn phân cấp."""
    with open(html_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f.read(), "html.parser")

    # Loại bỏ bảng biểu chữ ký nơi nhận nếu có
    for t in soup.find_all("table"):
        t.decompose()

    # Chuẩn hóa khoảng trắng trong từng thẻ p
    p_tags = [" ".join(p.get_text().split()) for p in soup.find_all("p") if p.get_text().strip()]
    lines = []
    for l in p_tags:
        if not lines or l != lines[-1]:
            lines.append(l)

    metadata = LegalDocumentMetadata(
        doc_id="ldn_59_2020_qh14",
        official_number="59/2020/QH14",
        title="Luật Doanh nghiệp",
        short_title="Luật Doanh nghiệp 2020",
        doc_type=DocumentType.LUAT,
        issuer="Quốc hội",
        signer="Nguyễn Thị Kim Ngân",
        issue_date=date(2020, 6, 17),
        effective_date=date(2021, 1, 1),
        status=DocumentStatus.CON_HIEU_LUC,
        source_url="https://thuvienphapluat.vn/van-ban/Doanh-nghiep/Luat-Doanh-nghiep-so-59-2020-QH14-427301.aspx",
        replaces=["68/2014/QH13"],
    )

    # Tìm vị trí bắt đầu của từng Điều
    art_indices = []
    for i, l in enumerate(lines):
        m = re.match(r"^Điều\s+(\d+)[\.:\s]+(.*)", l)
        if m:
            art_num = int(m.group(1))
            raw_title = m.group(2).strip()
            art_indices.append((art_num, i, raw_title))

    articles: List[LegalArticle] = []
    for idx, (art_num, start_i, raw_title) in enumerate(art_indices):
        end_i = art_indices[idx + 1][1] if idx + 1 < len(art_indices) else len(lines)
        art_lines = lines[start_i:end_i]

        art_title = raw_title
        content_lines = art_lines[1:]
        if not art_title and content_lines:
            art_title = content_lines[0]
            content_lines = content_lines[1:]

        # Gom khối
        clean_blocks = []
        curr_block = []
        for l in content_lines:
            if re.match(r"^(\d+\.|\bKhoản\s+\d+|[a-zđ]\))", l, re.IGNORECASE):
                if curr_block:
                    clean_blocks.append(" ".join(curr_block))
                    curr_block = []
            curr_block.append(l)
        if curr_block:
            clean_blocks.append(" ".join(curr_block))

        full_text = f"Điều {art_num}. {art_title}\n" + "\n".join(clean_blocks)

        # Tách Khoản & Điểm
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
            article_number=art_num,
            article_title=f"Điều {art_num}. {art_title}",
            full_text=full_text,
            clauses=clauses,
            status=DocumentStatus.CON_HIEU_LUC,
        )
        articles.append(art_obj)

    # Nhóm vào 10 Chương
    chapters: List[LegalChapter] = []
    for chap_id, chap_title, start_art, end_art in CHAPTERS_METADATA:
        chap_articles = [a for a in articles if start_art <= a.article_number <= end_art]
        chapters.append(
            LegalChapter(
                chapter_number=chap_id,
                chapter_title=chap_title,
                articles=chap_articles,
            )
        )

    parsed_doc = LegalDocumentParsed(
        metadata=metadata,
        chapters=chapters,
        raw_articles=articles,
    )
    return parsed_doc


def main():
    print("=" * 70)
    print("   VIETLEGAL AI - INGESTION LUẬT DOANH NGHIỆP 2020 (59/2020/QH14)")
    print("=" * 70)

    html_path = PROJECT_ROOT / "data" / "01_raw" / "html" / "59_2020_QH14.html"
    if not html_path.exists():
        print(f"[!] Không tìm thấy file {html_path}")
        return

    # 1. Bóc tách toàn văn phân cấp
    print(f"\n[1/5] Bóc tách văn bản Luật Doanh nghiệp 2020...")
    parsed_doc = parse_ldn_2020(html_path)
    total_arts = len(parsed_doc.raw_articles)
    print(f" [+] Số chương bóc tách: {len(parsed_doc.chapters)} Chương.")
    print(f" [+] Số điều luật bóc tách: {total_arts}/218 Điều.")
    assert total_arts == 218, f"Lỗi: Số điều luật ({total_arts}) không đúng 218 Điều!"

    # Lưu bản parsed JSON
    parsed_out = PROJECT_ROOT / "data" / "03_parsed" / "ldn_2020.json"
    parsed_out.parent.mkdir(parents=True, exist_ok=True)
    with open(parsed_out, "w", encoding="utf-8") as f:
        f.write(parsed_doc.model_dump_json(indent=2))
    print(f" [+] Đã lưu file cấu trúc parsed: {parsed_out.name}")

    # 2. Sinh Legal Context Chunks
    print(f"\n[2/5] Tạo các Legal Context Chunks phân cấp...")
    parser = LegalHierarchicalParser()
    chunks = parser.create_chunks(parsed_doc)
    print(f" [+] Đã sinh thành công: {len(chunks)} chunks phân cấp.")

    curated_dir = PROJECT_ROOT / "data" / "04_curated_chunks"
    curated_dir.mkdir(parents=True, exist_ok=True)
    chunks_out = curated_dir / "ldn_2020_chunks.jsonl"
    with open(chunks_out, "w", encoding="utf-8") as f:
        for c in chunks:
            f.write(c.model_dump_json() + "\n")
    print(f" [+] Đã lưu file chunks: {chunks_out.name}")

    # 3. Đồng bộ lên Supabase Cloud Database (legal_documents & legal_articles)
    print(f"\n[3/5] Đồng bộ dữ liệu lên Supabase Cloud Database...")
    supabase_loader = SupabaseLegalLoader()
    res = supabase_loader.sync_parsed_document(parsed_doc)
    print(f" [+] Document synced: {res['document_synced']}")
    print(f" [+] Articles synced: {res['articles_count']}/218 Điều")

    # 4. Tính toán Vector Embeddings (BAAI/bge-m3 trên CUDA GPU FP16)
    print(f"\n[4/5] Tính toán Vector Embeddings cho {len(chunks)} Chunks bằng BAAI/bge-m3...")
    vec_path = curated_dir / "ldn_2020_vectors.npy"
    if vec_path.exists():
        print(f" [+] Tải {len(chunks)} vectors từ bộ nhớ đệm: {vec_path.name}")
        vectors = np.load(vec_path).tolist()
    else:
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
        np.save(vec_path, np.array(vectors, dtype=np.float32))
        print(f" [+] Đã lưu cache vectors vào: {vec_path.name}")

    # 5. Nạp vào Qdrant Vector Store (Bảo toàn 100% dữ liệu cũ: recreate=False)
    print(f"\n[5/5] Nạp Vector Chunks vào Qdrant Vector Store (recreate=False)...")
    vector_store = QdrantVectorStore(collection_name="vietlegal_articles")
    vector_store.ensure_collection(vector_size=1024, recreate=False)
    uploaded = vector_store.insert_chunks(chunks=chunks, embeddings=vectors, batch_size=50)
    print(f" [+] Đã nạp thành công {uploaded} chunks vào Qdrant!")

    total_vectors = vector_store.client.count(collection_name=vector_store.collection_name).count
    print(f" [+] Qdrant collection 'vietlegal_articles' hiện có tổng cộng: {total_vectors} vectors!")

    print("\n" + "=" * 70)
    print(f"[SUCCESS] ĐÃ HOÀN TẤT NẠP TOÀN VĂN LUẬT DOANH NGHIỆP 2020 VÀO HỆ THỐNG!")
    print(f"          - 218 Điều luật đã nạp vào Supabase legal_articles.")
    print(f"          - {len(chunks)} Vector Chunks đã nạp vào Qdrant (Tổng vector: {total_vectors}).")
    print("=" * 70)


if __name__ == "__main__":
    main()
