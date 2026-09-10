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

def check():
    client = QdrantClient(url=os.getenv("QDRANT_URL"), api_key=os.getenv("QDRANT_API_KEY"))
    embedder = get_embedding_service()

    with open(PROJECT_ROOT / "data" / "03_parsed" / "traffic_p0_5_batch" / "benchmark_25_cases.json", encoding="utf-8") as f:
        cases = json.load(f)["cases"]

    print("Checking all 25 cases for ND 158 points in Top 10...")
    nd158_hits = []
    for idx, tc in enumerate(cases, 1):
        q = tc["query"]
        qv = embedder.embed_query(q)
        res = client.query_points(collection_name="vietlegal_articles", query=qv, limit=10, with_payload=True)
        for r, pt in enumerate(res.points, 1):
            pld = pt.payload
            off = str(pld.get("official_number", ""))
            doc_id = str(pld.get("doc_id", ""))
            batch = str(pld.get("batch", ""))
            if "158" in off or "158" in doc_id:
                nd158_hits.append((idx, tc["test_case_id"], r, pt.score, off, pld.get("article_number"), batch, pt.id))

    if not nd158_hits:
        print(">> No ND 158 points found in Top 10 for ANY of the 25 cases!")
    else:
        print(f">> Found {len(nd158_hits)} ND 158 occurrences in Top 10:")
        for h in nd158_hits:
            print(f"   Case [{h[0]:02d}] {h[1]} | Rank {h[2]} | Score: {h[3]:.4f} | {h[4]} Điều {h[5]} | Batch: {h[6]} | ID: {h[7]}")

if __name__ == "__main__":
    check()
