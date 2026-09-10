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

# Let's inspect step-by-step inside retrieve
sub_query_configs = retriever._decompose_query(contrast_query, as_of_date=as_of_date)
print("Decomposed configs:")
for c in sub_query_configs:
    print(" ", c)

# Let's see what RRF scores are produced
rrf_scores = {}
doc_store = {}
for q_idx, cfg in enumerate(sub_query_configs, start=1):
    q_text = cfg["sub_query"]
    weight = cfg.get("weight", 1.0)
    vec = embedder.embed_texts([q_text])[0]
    hits = store.search_similar(query_vector=vec, limit=20, as_of_date=as_of_date)
    for rank, hit in enumerate(hits, start=1):
        art_num = hit.get("article_number") or hit.get("article")
        if not art_num:
            continue
        doc_id = hit.get("doc_id", "traffic_driving_license_108_2026_tt_bca")
        key = f"{doc_id}_{art_num}"
        score_val = (weight / (retriever.rrf_k + rank))
        rrf_scores[key] = rrf_scores.get(key, 0.0) + score_val
        if key not in doc_store:
            doc_store[key] = hit

sorted_articles = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)
print("\nSorted RRF articles:")
for k, sc in sorted_articles[:10]:
    print(f"  {k}: {sc:.6f}")
