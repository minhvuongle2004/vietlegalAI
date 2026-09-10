import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.services.rag.embeddings import get_embedding_service
from backend.app.services.rag.vector_store import QdrantVectorStore
from backend.app.services.rag.retriever import HybridRetriever

store = QdrantVectorStore(collection_name="vietlegal_articles")
r = HybridRetriever(vector_store=store, embedding_service=get_embedding_service())

q1 = "Các trường hợp Cảnh sát giao thông được dừng phương tiện giao thông đường bộ để kiểm soát theo Thông tư 73/2024/TT-BCA?"
print(f"\n--- QUERY: {q1} ---")
res1 = r.retrieve(q1, top_k=5)
for i, x in enumerate(res1):
    print(f"#{i+1}: {x.get('doc_id')} | Điều {x.get('article_number')}: {x.get('article_title')} (score: {x.get('score', 0):.4f})")

q2 = "Nội dung và hình thức kiểm tra kiến thức pháp luật về trật tự an toàn giao thông đường bộ để phục hồi điểm giấy phép lái xe theo Thông tư 65/2024/TT-BCA?"
print(f"\n--- QUERY: {q2} ---")
res2 = r.retrieve(q2, top_k=5)
for i, x in enumerate(res2):
    print(f"#{i+1}: {x.get('doc_id')} | Điều {x.get('article_number')}: {x.get('article_title')} (score: {x.get('score', 0):.4f})")
