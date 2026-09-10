import sys
from pathlib import Path
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
PROJECT_ROOT = Path(".").resolve()
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
as_of_date = "2026-07-01"

sub_query_configs = retriever._decompose_query(contrast_query, as_of_date=as_of_date)
print(f"sub_query_configs count: {len(sub_query_configs)}")

for idx, sq in enumerate(sub_query_configs, 1):
    q_text = sq["sub_query"]
    print(f"\n--- Sub-query {idx} ({sq['category']}) ---")
    print(f"Text: {q_text}")
    print(f"Target article: {sq.get('target_article')}")
    vec = embedder.embed_texts([q_text])[0]
    hits = store.search_similar(query_vector=vec, limit=5, as_of_date=as_of_date)
    for h_idx, h in enumerate(hits, 1):
        doc = h.get("doc_id") or h.get("official_number")
        art = h.get("article_number") or h.get("article")
        score = h.get("score")
        print(f"  hit {h_idx}: score={score:.4f} | doc={doc} | art={art}")
