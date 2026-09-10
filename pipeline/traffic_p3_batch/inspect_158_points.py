import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
import os
from pathlib import Path
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
load_dotenv(PROJECT_ROOT / ".env")

from qdrant_client import QdrantClient

client = QdrantClient(url=os.getenv("QDRANT_URL"), api_key=os.getenv("QDRANT_API_KEY"))

# Find points where official_number or doc_id matches 158
points_158 = []
offset = None
scanned = 0

while scanned < 7800:
    res, offset = client.scroll(
        collection_name="vietlegal_articles",
        limit=250,
        offset=offset,
        with_payload=True
    )
    for p in res:
        scanned += 1
        d = p.payload.get("official_number") or p.payload.get("document_id") or p.payload.get("doc_id") or ""
        if "158/2024" in str(d) or "158" in str(d):
            points_158.append(p)
    if offset is None:
        break

print(f"Found {len(points_158)} points for NĐ 158 in production:")
for p in points_158:
    print(f"  ID: {p.id} | article: {p.payload.get('article_number')} | doc_id: {p.payload.get('doc_id')} | title: {p.payload.get('doc_title')}")
