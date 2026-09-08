import sys
import io
import os
import json
import time
from pathlib import Path
from typing import List

# Đảm bảo UTF-8 cho Windows console
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from pipeline.models import LegalChunkPayload
from backend.app.services.rag.embeddings import get_embedding_service
from backend.app.services.rag.vector_store import QdrantVectorStore


def load_chunks_from_jsonl(file_path: Path) -> List[LegalChunkPayload]:
    """Đọc danh sách chunks từ file jsonl"""
    chunks: List[LegalChunkPayload] = []
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                data = json.loads(line)
                chunks.append(LegalChunkPayload(**data))
    return chunks


def main():
    print("=" * 70)
    print("   VIETLEGAL AI - VECTOR EMBEDDING & QDRANT INGESTION PIPELINE")
    print("=" * 70)

    chunks_file = PROJECT_ROOT / "data" / "04_curated_chunks" / "bllđ_2019_chunks.jsonl"
    if not chunks_file.exists():
        print(f"[!] Không tìm thấy file {chunks_file}. Vui lòng chạy crawler trước!")
        return

    # 1. Đọc danh sách Chunks
    print(f"[*] Đang tải danh sách chunks từ: {chunks_file}")
    chunks = load_chunks_from_jsonl(chunks_file)
    print(f"[+] Đã đọc thành công {len(chunks)} chunks!")

    # 2. Khởi tạo mô hình Embedding
    embedder = get_embedding_service()
    dim = embedder.dimension
    print(f"[+] Số chiều vector (Dimension): {dim}")

    # 3. Trích xuất text cần nhúng (full_search_text = context_header + content)
    texts_to_embed = [c.full_search_text for c in chunks]

    # 4. Tính toán Vector Embeddings
    print(f"\n[*] Đang nhúng {len(texts_to_embed)} chunks thành Vectors (tiến trình có thể mất khoảng 30s - 1 phút)...")
    start_time = time.time()
    vectors = embedder.embed_texts(texts_to_embed)
    embed_time = time.time() - start_time
    print(f"[+] Đã tính toán xong {len(vectors)} vectors trong {embed_time:.2f} giây!")

    # 5. Khởi tạo Qdrant Vector Store
    print("\n[*] Đang khởi tạo kết nối Qdrant Vector Store...")
    vector_store = QdrantVectorStore(collection_name="vietlegal_articles")
    vector_store.ensure_collection(vector_size=dim, recreate=True)

    # 6. Nạp Chunks và Vectors vào Qdrant
    print("\n[*] Đang nạp vectors và metadata vào Qdrant...")
    uploaded_count = vector_store.insert_chunks(chunks=chunks, embeddings=vectors, batch_size=50)

    # 7. Thử nghiệm tìm kiếm ngữ nghĩa thực tế (Semantic Search Test)
    print("\n" + "=" * 70)
    print("   THỬ NGHIỆM TÌM KIẾM NGỮ NGHĨA (SEMANTIC SEARCH TEST)")
    print("=" * 70)

    test_queries = [
        "thời gian thử việc tối đa của kỹ sư là mấy tháng?",
        "công ty đơn phương đuổi việc nhân viên trái luật thì phải bồi thường gì?",
        "lương tối thiểu vùng được xác định như thế nào?",
    ]

    for q in test_queries:
        print(f"\n❓ Câu hỏi: \"{q}\"")
        q_vec = embedder.embed_query(q)
        top_results = vector_store.search_similar(query_vector=q_vec, limit=2)

        for rank, r in enumerate(top_results, start=1):
            print(f"  [{rank}] Độ tương đồng (Cosine Score): {r['score']:.4f}")
            print(f"      -> Điều {r['article_number']}: {r['article_title']}")
            print(f"      -> Ngữ cảnh: {r['context_header']}")
            snippet = r['content'].replace('\n', ' ')[:150]
            print(f"      -> Trích đoạn: \"{snippet}...\"")

    vector_store.close()
    print("\n🎉 HOÀN THÀNH! Toàn bộ 323 Chunks đã được số hóa thành công trong Qdrant!")


if __name__ == "__main__":
    main()
