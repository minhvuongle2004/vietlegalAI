import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.services.rag.vector_store import QdrantVectorStore
from backend.app.services.rag.embeddings import get_embedding_service
from backend.app.services.rag.retriever import HybridRetriever

CLOUD_URL = "https://69f07c1e-2e88-452f-aded-6dd577ddbd9b.us-west-2-0.aws.cloud.qdrant.io"
CLOUD_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIiwic3ViamVjdCI6ImFwaS1rZXk6OTAxNjk0MzUtYjMwMS00YjAzLWFmMGYtYmYyZjc0MWE4MjYxIn0.bJ2YtMtnmDJXN4k3FKdduN_TsLARSOAvGjBRKW3p028"

embedder = get_embedding_service()
store = QdrantVectorStore(
    collection_name="vietlegal_articles_staging",
    url=CLOUD_URL,
    api_key=CLOUD_API_KEY
)
retriever = HybridRetriever(vector_store=store, embedding_service=embedder)

with open("data/03_parsed/traffic_p0_5_batch/benchmark_25_cases.json", "r", encoding="utf-8") as f:
    data = json.load(f)["cases"]

hit1 = 0
hit2 = 0
hit3 = 0

print("=" * 80)
print("   25 BASELINE CASES RETRIEVAL (TEMPORAL-AWARE HYBRID ON COMBINED STAGING)")
print("=" * 80)

for tc in data:
    cid = tc["test_case_id"]
    q = tc["query"]
    as_of = tc.get("as_of_date")
    exp = tc["expected_documents"]

    hits = retriever.retrieve(query=q, as_of_date=as_of, top_k=5)
    rank = None
    for r, h in enumerate(hits, 1):
        doc_id = str(h.get("doc_id", "") or "")
        off_num = str(h.get("official_number", "") or "")
        title = str(h.get("doc_title", "") or "")
        if any(e in doc_id or e in off_num or e in title for e in exp):
            rank = r
            break

    if rank == 1:
        hit1 += 1
        hit2 += 1
        hit3 += 1
        status = "PASS (Hit@1)"
    elif rank == 2:
        hit2 += 1
        hit3 += 1
        status = "PASS (Hit@2)"
    elif rank == 3:
        hit3 += 1
        status = "PASS (Hit@3)"
    else:
        status = f"MISS (Rank: {rank})"

    top1 = hits[0] if hits else {}
    print(f"[{status:14}] {cid:15} | as_of={as_of} | Top 1: {top1.get('official_number')} {top1.get('article_number')}")

print("-" * 80)
print(f"Total: 25 | Hit@1: {hit1}/25 ({hit1/25*100:.1f}%) | Hit@2: {hit2}/25 ({hit2/25*100:.1f}%) | Hit@3: {hit3}/25 ({hit3/25*100:.1f}%)")
print("=" * 80)
