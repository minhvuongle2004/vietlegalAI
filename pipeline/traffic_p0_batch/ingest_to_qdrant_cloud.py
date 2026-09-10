import os
import sys
import json
import time
import uuid
from pathlib import Path
from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.services.rag.embeddings import get_embedding_service

CLOUD_URL = "https://69f07c1e-2e88-452f-aded-6dd577ddbd9b.us-west-2-0.aws.cloud.qdrant.io"
CLOUD_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIiwic3ViamVjdCI6ImFwaS1rZXk6OTAxNjk0MzUtYjMwMS00YjAzLWFmMGYtYmYyZjc0MWE4MjYxIn0.bJ2YtMtnmDJXN4k3FKdduN_TsLARSOAvGjBRKW3p028"
COLLECTION_NAME = "vietlegal_articles"

PARSED_DIR = PROJECT_ROOT / "data" / "03_parsed" / "traffic_p0_batch"
SUMMARY_FILE = PARSED_DIR / "traffic_p0_batch_summary.json"

def main():
    print("=" * 80)
    print(" BẮT ĐẦU INGESTION: TRAFFIC P0 VERSION-AWARE BATCH VÀO QDRANT CLOUD")
    print("=" * 80)

    if not SUMMARY_FILE.exists():
        print(f"[!] Lỗi: Không tìm thấy file {SUMMARY_FILE}")
        return

    # 1. Đọc danh sách chunks đã bóc tách
    print("[1/4] Đang nạp danh sách 42 chunks từ các file parsed JSON...")
    all_chunks = []
    for parsed_file in PARSED_DIR.glob("*.json"):
        if parsed_file.name == "traffic_p0_batch_summary.json":
            continue
        with open(parsed_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            meta = data["metadata"]
            hierarchy = data["hierarchy"]
            
            for art in hierarchy["articles"]:
                art_num = art["article_number"]
                art_title = art["article_title"]
                ch_title = art["chapter"]
                
                if art["clauses"]:
                    for cl in art["clauses"]:
                        cl_num = cl["clause_number"]
                        cl_body = cl["clause_text"]
                        pts = "\n".join([f"  - {p['point_identifier']}) {p['point_text']}" for p in cl["points"]])
                        full_content = f"{cl_body}\n{pts}".strip()
                        search_text = f"[{meta['official_number']} - {meta['title']}]\n{ch_title} > {art_num}: {art_title} > {cl_num}\n{full_content}"
                        
                        all_chunks.append({
                            "chunk_id": f"{meta['doc_id']}_{art_num}_{cl_num}".replace(" ", "_").lower(),
                            "document_id": meta["doc_id"],
                            "official_number": meta["official_number"],
                            "title": meta["title"],
                            "doc_type": meta["doc_type"],
                            "article": art_num,
                            "clause": cl_num,
                            "article_title": art_title,
                            "chapter": ch_title,
                            "content": full_content,
                            "full_search_text": search_text,
                            "effective_from": meta["effective_date"],
                            "effective_to": None,
                            "status": meta["status"],
                            "version_chain": meta.get("version_chain", []),
                            "relations": meta.get("relations", {}),
                            "scope_tags": meta.get("scope_tags", [])
                        })
                else:
                    search_text = f"[{meta['official_number']} - {meta['title']}]\n{ch_title} > {art_num}: {art_title}\n{art['raw_text']}"
                    all_chunks.append({
                        "chunk_id": f"{meta['doc_id']}_{art_num}".replace(" ", "_").lower(),
                        "document_id": meta["doc_id"],
                        "official_number": meta["official_number"],
                        "title": meta["title"],
                        "doc_type": meta["doc_type"],
                        "article": art_num,
                        "clause": None,
                        "article_title": art_title,
                        "chapter": ch_title,
                        "content": art["raw_text"],
                        "full_search_text": search_text,
                        "effective_from": meta["effective_date"],
                        "effective_to": None,
                        "status": meta["status"],
                        "version_chain": meta.get("version_chain", []),
                        "relations": meta.get("relations", {}),
                        "scope_tags": meta.get("scope_tags", [])
                    })

    print(f"      -> Đã chuẩn bị sẵn sàng {len(all_chunks)} chunks.")

    # 2. Tạo Embeddings với BGE-M3
    print(f"\n[2/4] Khởi tạo BGE-M3 Embedding Service & vector hóa {len(all_chunks)} chunks...")
    embedding_service = get_embedding_service()
    texts = [c["full_search_text"] for c in all_chunks]
    t0 = time.time()
    embeddings = embedding_service.embed_texts(texts, batch_size=8)
    dur = round(time.time() - t0, 2)
    print(f"      -> Hoàn tất vector hóa {len(embeddings)} vectors trong {dur}s (1024 dims)!")

    # 3. Kết nối Qdrant Cloud
    print(f"\n[3/4] Kết nối tới Qdrant Cloud ({CLOUD_URL[:45]}...)...")
    client = QdrantClient(url=CLOUD_URL, api_key=CLOUD_API_KEY, check_compatibility=False)
    before_info = client.get_collection(COLLECTION_NAME)
    before_count = before_info.points_count
    print(f"      -> Số lượng points hiện có trên Cloud: {before_count} points.")

    # 4. Upsert vào Qdrant Cloud
    print(f"\n[4/4] Nạp {len(all_chunks)} vector points vào collection '{COLLECTION_NAME}'...")
    points = []
    for i, (chunk, emb) in enumerate(zip(all_chunks, embeddings)):
        point_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, chunk["chunk_id"]))
        payload = {
            "chunk_id": chunk["chunk_id"],
            "doc_id": chunk["document_id"],
            "document_id": chunk["document_id"],
            "official_number": chunk["official_number"],
            "doc_title": chunk["title"],
            "title": chunk["title"],
            "doc_type": chunk["doc_type"],
            "article": chunk["article"],
            "article_number": chunk["article"],
            "clause": chunk["clause"],
            "clause_number": chunk["clause"],
            "article_title": chunk["article_title"],
            "chapter": chunk["chapter"],
            "context_header": f"{chunk['chapter']} > {chunk['article']}: {chunk['article_title']}",
            "content": chunk["content"],
            "full_search_text": chunk["full_search_text"],
            "effective_date": chunk["effective_from"],
            "effective_from": chunk["effective_from"],
            "effective_to": chunk["effective_to"],
            "status": chunk["status"],
            "scope_tags": chunk["scope_tags"],
            "version_chain": chunk["version_chain"],
            "relations": chunk["relations"]
        }
        points.append(qmodels.PointStruct(id=point_id, vector=emb, payload=payload))

    client.upsert(
        collection_name=COLLECTION_NAME,
        points=points,
        wait=True
    )

    after_info = client.get_collection(COLLECTION_NAME)
    after_count = after_info.points_count
    print(f"      -> Đã nạp thành công! Points trước: {before_count} | Points sau: {after_count} (+{after_count - before_count})")

    # Kiểm tra thử cả Local Qdrant nếu local đang chạy
    try:
        local_client = QdrantClient(url="http://localhost:6333", check_compatibility=False)
        local_info = local_client.get_collection(COLLECTION_NAME)
        local_before = local_info.points_count
        local_client.upsert(collection_name=COLLECTION_NAME, points=points, wait=True)
        local_after = local_client.get_collection(COLLECTION_NAME).points_count
        print(f"      -> Đồng bộ thêm Local Qdrant: {local_before} -> {local_after} points.")
    except Exception as e:
        print(f"      -> (Local Qdrant offline hoặc bỏ qua: {e})")

    print("\n" + "=" * 80)
    print(" INGESTION HOÀN TẤT THÀNH CÔNG RỰC RỠ!")
    print(f" Bộ luật Giao thông hiện đại (Traffic P0 Version-Aware) đã có mặt trên Qdrant Cloud!")
    print("=" * 80)

if __name__ == "__main__":
    main()
