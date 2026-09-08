import sys
sys.path.insert(0, ".")
from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels

client = QdrantClient(path="data/03_vectordb/qdrant")
points, _ = client.scroll(
    collection_name="vietlegal_articles",
    scroll_filter=qmodels.Filter(
        must=[
            qmodels.FieldCondition(key="doc_id", match=qmodels.MatchValue(value="tncn_109_2025_qh15"))
        ]
    ),
    limit=50,
    with_payload=True,
    with_vectors=False
)

print(f"Total points found for tncn_109: {len(points)}")
for p in points:
    pay = p.payload
    if pay.get("article_number") in [7, 8, 9, 10]:
        print(f"ID: {p.id} | Điều {pay.get('article_number')}: {pay.get('article_title')} | chunk_id: {pay.get('chunk_id')} | header: {pay.get('context_header')}")
