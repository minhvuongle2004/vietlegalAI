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

print("=== INSPECTING ALL DOCS IN QDRANT PRODUCTION COLLECTION ===")

# Scroll through collection to sample doc_ids
doc_ids = {}
offset = None
scanned = 0
while scanned < 7800:
    res, offset = client.scroll(
        collection_name="vietlegal_articles",
        limit=200,
        offset=offset,
        with_payload=["doc_id", "document_id", "official_number"]
    )
    for p in res:
        d = p.payload.get("official_number") or p.payload.get("document_id") or p.payload.get("doc_id")
        doc_ids[d] = doc_ids.get(d, 0) + 1
        scanned += 1
    if offset is None:
        break

print(f"Total points scanned: {scanned}")
print(f"Total unique documents in Qdrant production: {len(doc_ids)}")
for d, cnt in sorted(doc_ids.items(), key=lambda x: x[1], reverse=True):
    print(f"  - {str(d):30}: {cnt:4} points")
