import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
import os
import json
from pathlib import Path
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
load_dotenv(PROJECT_ROOT / ".env")

from qdrant_client import QdrantClient
from backend.app.services.rag.embeddings import get_embedding_service

def diagnose():
    client = QdrantClient(url=os.getenv("QDRANT_URL"), api_key=os.getenv("QDRANT_API_KEY"))
    embedder = get_embedding_service()
    q = "Thí sinh thi sát hạch lái xe ô tô vào ngày 30/06/2026 có phải thực hiện bài thi mô phỏng tình huống giao thông không?"
    qv = embedder.embed_query(q)
    res = client.query_points(collection_name="vietlegal_articles", query=qv, limit=10, with_payload=True)

    print("=" * 80)
    print("   DIAGNOSIS FOR TC-DOM-CONTRAST-01A")
    print(f"   Query: {q}")
    print("=" * 80)
    for idx, pt in enumerate(res.points, 1):
        pld = pt.payload
        doc_id = pld.get("doc_id") or pld.get("document_id")
        off_num = pld.get("official_number")
        art = pld.get("article_number") or pld.get("article")
        batch = pld.get("batch")
        valid_from = pld.get("valid_from")
        valid_to = pld.get("valid_to")
        print(f"\n[Rank {idx}] Score: {pt.score:.4f} | ID: {pt.id}")
        print(f"  Doc ID: {doc_id} | Official Number: {off_num}")
        print(f"  Article: {art} | Batch: {batch}")
        print(f"  Valid: [{valid_from}, {valid_to})")
        print(f"  Content Snippet: {pld.get('content', '')[:120]}...")

if __name__ == "__main__":
    diagnose()
