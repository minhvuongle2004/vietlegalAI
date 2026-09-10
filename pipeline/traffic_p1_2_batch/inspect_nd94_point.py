import os
import sys
import json
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.http import models

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

load_dotenv()

client = QdrantClient(url=os.getenv('QDRANT_URL'), api_key=os.getenv('QDRANT_API_KEY'), timeout=60)
res = client.scroll(
    collection_name='vietlegal_articles_staging',
    scroll_filter=models.Filter(
        must=[models.FieldCondition(key='official_number', match=models.MatchValue(value='94/2026/NĐ-CP'))]
    ),
    with_payload=True,
    limit=200
)
points = res[0]
print(f"Total points: {len(points)}")
extracted = []
for p in points:
    art = p.payload.get('article_number')
    title = p.payload.get('article_title', '')
    if str(art) == '26' or '26' in str(art) or 'Điều 26' in title:
        item = {
            "point_id": p.id,
            "document_id": p.payload.get("document_id"),
            "official_number": p.payload.get("official_number"),
            "article_number": p.payload.get("article_number"),
            "article_title": p.payload.get("article_title"),
            "clause_number": p.payload.get("clause_number"),
            "point_number": p.payload.get("point_number"),
            "source_hash": p.payload.get("source_hash"),
            "provenance": p.payload.get("provenance"),
            "source_url": p.payload.get("source_url"),
            "chunk_text": p.payload.get("chunk_text")
        }
        extracted.append(item)
        print("="*60)
        print(f"point_id: {p.id}")
        for k in ['document_id', 'official_number', 'article_number', 'article_title', 'clause_number', 'point_number', 'source_hash', 'provenance', 'source_url']:
            print(f"- {k}: {p.payload.get(k)}")
        print("ACTUAL CHUNK TEXT:")
        print(p.payload.get('chunk_text'))

with open("data/03_parsed/traffic_p1_2_batch/task1_inspect_nd94_dieu26.json", "w", encoding="utf-8") as f:
    json.dump(extracted, f, ensure_ascii=False, indent=2)
print(f"\nSaved {len(extracted)} points to task1_inspect_nd94_dieu26.json")
