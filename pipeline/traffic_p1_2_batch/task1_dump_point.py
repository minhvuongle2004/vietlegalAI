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
        must=[
            models.FieldCondition(key='official_number', match=models.MatchValue(value='94/2026/NĐ-CP')),
            models.FieldCondition(key='article_number', match=models.MatchValue(value='Điều 26'))
        ]
    ),
    with_payload=True,
    limit=10
)

for p in res[0]:
    if p.payload.get('clause_number') == 'Khoản 1':
        print("="*60)
        print("TASK 1 — INSPECT ACTUAL RETRIEVED POINT:")
        print(f"point_id: {p.id}")
        print(f"document_id: {p.payload.get('doc_id')}")
        print(f"official_number: {p.payload.get('official_number')}")
        print(f"article_number: {p.payload.get('article_number')}")
        print(f"article_title: {p.payload.get('article_title')}")
        print(f"clause_number: {p.payload.get('clause_number')}")
        print(f"point_number: {p.payload.get('point_letter')}")
        print(f"source_hash: {p.payload.get('source_hash')}")
        print(f"provenance: {p.payload.get('source_url')}")
        print(f"source_url: {p.payload.get('source_url')}")
        print("ACTUAL TEXT:")
        print(p.payload.get('content'))
        print("="*60)
