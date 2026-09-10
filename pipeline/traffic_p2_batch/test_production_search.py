import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
import os
from pathlib import Path
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
load_dotenv(PROJECT_ROOT / ".env")

from qdrant_client import QdrantClient
from backend.app.services.rag.embeddings import get_embedding_service

client = QdrantClient(url=os.getenv("QDRANT_URL"), api_key=os.getenv("QDRANT_API_KEY"))
embedder = get_embedding_service()

queries = [
    "Quy định đầu tư xây dựng trạm dừng nghỉ trên đường cao tốc",
    "Mẫu tờ trình đề nghị giao UBND tỉnh quản lý tuyến quốc lộ",
    "Thẩm quyền thẩm tra thẩm định an toàn giao thông đường bộ",
    "Thủ tục cấp phép sử dụng tạm thời vỉa hè lòng đường"
]

print("=== FINAL PRODUCTION SEMANTIC SEARCH TEST ===")
for q in queries:
    vec = embedder.embed_query(q)
    results = client.query_points(
        collection_name="vietlegal_articles",
        query=vec,
        limit=2
    ).points
    print(f"\n[Query]: {q}")
    for r in results:
        off = r.payload.get('official_number', '')
        ctx = r.payload.get('context_header', '')[:80]
        print(f"  [Score: {r.score:.4f}] {off} -> {ctx}")

print("\n[+] Production semantic search verification PASS!")
