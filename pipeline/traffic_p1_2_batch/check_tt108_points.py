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

# Let's search specifically for Điều 15 of TT 108 in Qdrant
print("[*] Searching Qdrant staging for TT 108 Điều 15...")
hits = store.client.scroll(
    collection_name="vietlegal_articles_staging",
    scroll_filter=None,
    limit=100,
    with_payload=True
)[0]

found_108 = []
for h in hits:
    p = h.payload or {}
    doc = p.get("doc_id", "") or p.get("official_number", "")
    if "108" in str(doc):
        found_108.append(p)

print(f"Total TT 108 points in staging (first 100 sample): {len(found_108)}")

# Let's check scroll with filter for TT 108
from qdrant_client import models as qmodels
scroll_res = store.client.scroll(
    collection_name="vietlegal_articles_staging",
    scroll_filter=qmodels.Filter(
        must=[
            qmodels.FieldCondition(
                key="doc_id",
                match=qmodels.MatchValue(value="traffic_driving_license_108_2026_tt_bca")
            )
        ]
    ),
    limit=50,
    with_payload=True
)[0]

print(f"Total points matching doc_id=traffic_driving_license_108_2026_tt_bca: {len(scroll_res)}")
for pt in scroll_res:
    pl = pt.payload
    print(f"  Point ID: {pt.id} | Art: {pl.get('article_number') or pl.get('article')} | Clause: {pl.get('clause_number') or pl.get('clause')} | Title: {pl.get('article_title')}")
