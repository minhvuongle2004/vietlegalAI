import sys
from pathlib import Path
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
from backend.app.services.rag.embeddings import get_embedding_service
from backend.app.services.rag.vector_store import QdrantVectorStore
from backend.app.services.rag.retriever import HybridRetriever

CLOUD_URL = "https://69f07c1e-2e88-452f-aded-6dd577ddbd9b.us-west-2-0.aws.cloud.qdrant.io"
CLOUD_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIiwic3ViamVjdCI6ImFwaS1rZXk6OTAxNjk0MzUtYjMwMS00YjAzLWFmMGYtYmYyZjc0MWE4MjYxIn0.bJ2YtMtnmDJXN4k3FKdduN_TsLARSOAvGjBRKW3p028"

store = QdrantVectorStore(collection_name="vietlegal_articles_staging", url=CLOUD_URL, api_key=CLOUD_API_KEY)
embedder = get_embedding_service()
retriever = HybridRetriever(vector_store=store, embedding_service=embedder)

contrast_query = "Thí sinh thi sát hạch lái xe ô tô vào ngày 30/06/2026 có phải thực hiện bài thi mô phỏng tình huống giao thông không?"
res_b = retriever.retrieve(query=contrast_query, as_of_date="2026-07-01", top_k=5)

print("=== RETRIEVAL RESULTS FOR TC-DOM-CONTRAST-01B (as_of_date=2026-07-01) ===")
for i, r in enumerate(res_b, 1):
    doc_id = r.get("doc_id")
    off_num = r.get("official_number")
    art = r.get("article_number")
    title = r.get("article_title")
    clause = r.get("clause_number")
    score = r.get("score")
    text = r.get("text", "")
    print(f"\nRank {i}: score={score}")
    print(f"  Doc: {off_num} ({doc_id})")
    print(f"  Article: {art} - {title}")
    print(f"  Clause: {clause}")
    print(f"  Text: {text[:300]}...")
