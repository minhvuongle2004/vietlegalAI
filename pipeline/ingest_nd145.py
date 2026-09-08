import sys
import io
import os
import json
import time
from pathlib import Path
from datetime import date
from typing import List

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import docx
from pipeline.models import (
    LegalDocumentMetadata,
    DocumentType,
    DocumentStatus,
    LegalChunkPayload,
)
from pipeline.parsers.legal_hierarchical_parser import LegalHierarchicalParser
from pipeline.loaders.supabase_loader import SupabaseLegalLoader
from backend.app.services.rag.embeddings import get_embedding_service
from backend.app.services.rag.vector_store import QdrantVectorStore


def main():
    print("=" * 70)
    print("   VIETLEGAL AI - INGESTION NGHỊ ĐỊNH 145/2020/NĐ-CP")
    print("=" * 70)

    docx_path = PROJECT_ROOT / "data" / "01_raw" / "docx" / "145_2020_ND_CP.docx"
    if not docx_path.exists():
        print(f"[!] Không tìm thấy file {docx_path}")
        return

    # 1. Đọc nội dung file docx
    print(f"\n[1/5] Đang đọc file văn bản gốc từ: {docx_path}")
    doc = docx.Document(docx_path)
    full_text = "\n".join([p.text.strip() for p in doc.paragraphs if p.text.strip()])
    print(f" [+] Tổng ký tự: {len(full_text):,} ký tự ({len(doc.paragraphs)} đoạn)")

    # 2. Bóc tách phân cấp & Cắt Chunks
    print("\n[2/5] Bóc tách phân cấp (Chương -> Điều -> Khoản) & sinh Legal Context Chunks...")
    metadata = LegalDocumentMetadata(
        doc_id="nd_145_2020_nd_cp",
        official_number="145/2020/NĐ-CP",
        title="Nghị định quy định chi tiết và hướng dẫn thi hành một số điều của Bộ luật Lao động về điều kiện lao động và quan hệ lao động",
        short_title="Nghị định 145/2020/NĐ-CP",
        doc_type=DocumentType.NGHI_DINH,
        issuer="Chính phủ",
        signer="Nguyễn Xuân Phúc",
        issue_date=date(2020, 12, 14),
        effective_date=date(2021, 2, 1),
        status=DocumentStatus.CON_HIEU_LUC,
        source_url="https://congbao.chinhphu.vn",
        guides=["bllđ_45_2019_qh14"],
    )

    parser = LegalHierarchicalParser()
    parsed_doc = parser.parse(full_text, metadata)
    chunks = parser.create_chunks(parsed_doc)

    print(f" [+] Số chương bóc tách: {len(parsed_doc.chapters)}")
    print(f" [+] Số điều luật bóc tách: {len(parsed_doc.raw_articles)}/115 Điều")
    print(f" [+] Số lượng Chunks sinh ra: {len(chunks)} Chunks")

    # Lưu file parsed JSON & curated chunks JSONL
    parsed_out = PROJECT_ROOT / "data" / "03_parsed" / "nd_145_2020.json"
    chunks_out = PROJECT_ROOT / "data" / "04_curated_chunks" / "nd_145_2020_chunks.jsonl"

    parsed_out.parent.mkdir(parents=True, exist_ok=True)
    chunks_out.parent.mkdir(parents=True, exist_ok=True)

    with open(chunks_out, "w", encoding="utf-8") as f:
        for c in chunks:
            f.write(c.model_dump_json() + "\n")
    print(f" [+] Đã lưu file Chunks vào: {chunks_out}")

    # 3. Đồng bộ lên Supabase Cloud Database (legal_documents & legal_articles)
    print("\n[3/5] Đồng bộ dữ liệu lên Supabase Cloud (PostgreSQL)...")
    supabase_loader = SupabaseLegalLoader()
    sync_res = supabase_loader.sync_parsed_document(parsed_doc)
    print(f" [+] Văn bản legal_documents: {'Thành công' if sync_res['document_synced'] else 'Thất bại'}")
    print(f" [+] Số điều luật nạp vào legal_articles: {sync_res['articles_count']} Điều")

    # 4. Tính toán Vector Embeddings với mô hình BGE-M3 (CUDA GPU FP16)
    print("\n[4/5] Tính toán Vector Embeddings (BAAI/bge-m3)...")
    import numpy as np
    import requests

    vec_file = PROJECT_ROOT / "data" / "04_curated_chunks" / "nd_145_vectors.npy"
    if vec_file.exists():
        print(f" [+] Tải {len(chunks)} vectors từ bộ nhớ đệm: {vec_file}")
        vectors = np.load(vec_file).tolist()
    else:
        embedder = get_embedding_service()
        dim = embedder.dimension
        texts_to_embed = [c.full_search_text for c in chunks]

        t0 = time.time()
        vectors = embedder.embed_texts(texts_to_embed)
        print(f" [+] Đã nhúng {len(vectors)} vectors (dim={dim}) trong {time.time() - t0:.2f}s!")
        np.save(vec_file, np.array(vectors))
        print(f" [+] Đã lưu cache vectors vào: {vec_file}")

    # 5. Nạp vào Qdrant Vector Store (Giữ nguyên dữ liệu cũ, KHÔNG xóa collection)
    print("\n[5/5] Nạp Vectors và Metadata vào Qdrant Vector Store...")
    vector_store = QdrantVectorStore(collection_name="vietlegal_articles")
    vector_store.ensure_collection(vector_size=1024, recreate=False)
    uploaded = vector_store.insert_chunks(chunks=chunks, embeddings=vectors, batch_size=50)
    print(f" [+] Đã nạp thành công {uploaded} chunks vào Qdrant!")

    # 6. Kiểm tra truy vấn thử nghiệm đa văn bản trực tiếp
    print("\n" + "=" * 70)
    print("   KIỂM THỬ TRUY VẤN ĐA VĂN BẢN (MULTI-DOCUMENT SEMANTIC SEARCH)")
    print("=" * 70)
    embedder = get_embedding_service()
    test_queries = [
        "Cách tính tiền lương làm thêm giờ ban đêm ngày lễ theo nghị định 145?",
        "Hồ sơ và thành phần cuộc họp xử lý kỷ luật lao động gồm những gì?",
    ]

    for q in test_queries:
        print(f"\n❓ Truy vấn: \"{q}\"")
        q_vec = embedder.embed_query(q)
        results = vector_store.search_similar(query_vector=q_vec, limit=2)
        for idx, r in enumerate(results, 1):
            doc_title = r.get("doc_title", "Văn bản luật")
            print(f"  [{idx}] Điểm Cosine: {r['score']:.4f} | {doc_title} • Điều {r['article_number']}: {r['article_title']}")
            print(f"      Ngữ cảnh: {r['context_header']}")

    vector_store.close()
    print("\n🎉 HOÀN TẤT NẠP NGHỊ ĐỊNH 145/2020/NĐ-CP VÀO HỆ THỐNG!")


if __name__ == "__main__":
    main()
