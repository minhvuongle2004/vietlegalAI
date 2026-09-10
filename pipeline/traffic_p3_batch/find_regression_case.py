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

CLOUD_URL = os.getenv("QDRANT_URL")
CLOUD_API_KEY = os.getenv("QDRANT_API_KEY")
PROD_COLLECTION = "vietlegal_articles"
BENCHMARK_FILE = PROJECT_ROOT / "data" / "03_parsed" / "traffic_p0_5_batch" / "benchmark_25_cases.json"

def analyze():
    client = QdrantClient(url=CLOUD_URL, api_key=CLOUD_API_KEY, timeout=30.0)
    embedder = get_embedding_service()

    with open(BENCHMARK_FILE, "r", encoding="utf-8") as f:
        cases = json.load(f)["cases"]

    # Also load P0.5 baseline results
    with open(PROJECT_ROOT / "data" / "03_parsed" / "traffic_p0_5_batch" / "benchmark_25_cases_results.json", "r", encoding="utf-8") as f:
        p0_5_data = json.load(f)
    p0_5_map = {c["test_case_id"]: c for c in p0_5_data["detailed_results"]}

    print("=" * 100)
    print("   EXACT RANK MOVEMENT COMPARISON: BASELINE vs CURRENT PRODUCTION")
    print("=" * 100)

    for idx, tc in enumerate(cases, 1):
        cid = tc["test_case_id"]
        q = tc["query"]
        expected_docs = [d.lower() for d in tc["expected_documents"]]

        # 1. P0.5 baseline rank
        b_case = p0_5_map.get(cid, {})
        b_rank = b_case.get("rank")
        b_top1 = b_case.get("top1_doc", "")

        # 2. Current production rank
        q_vec = embedder.embed_query(q)
        res = client.query_points(collection_name=PROD_COLLECTION, query=q_vec, limit=5, with_payload=True)
        hits = res.points

        cur_rank = None
        matched_chunk = None
        for r, pt in enumerate(hits, 1):
            pld = pt.payload
            doc_id = str(pld.get("doc_id", "") or "").lower()
            off_num = str(pld.get("official_number", "") or "").lower()
            title = str(pld.get("doc_title", "") or "").lower()
            if any(exp in doc_id or exp in off_num or exp in title for exp in expected_docs):
                if cur_rank is None:
                    cur_rank = r
                    matched_chunk = pld

        top1 = hits[0].payload if hits else {}
        top1_str = f"{top1.get('official_number')} {top1.get('article_number')}"
        
        # Check if rank changed or worsened
        status = "SAME"
        if b_rank != cur_rank:
            status = f"CHANGED ({b_rank} -> {cur_rank})"

        print(f"[{idx:02d}/25] {cid:22} | Baseline Rank: {str(b_rank):4} | Current Rank: {str(cur_rank):4} | {status}")
        if cur_rank != b_rank or cur_rank > 2:
            print(f"       Query: {q}")
            print(f"       Expected: {expected_docs}")
            print(f"       Current Top 1: {top1_str} (score={hits[0].score:.4f}, doc_id={top1.get('doc_id')})")
            if len(hits) > 1:
                t2 = hits[1].payload
                print(f"       Current Top 2: {t2.get('official_number')} {t2.get('article_number')} (score={hits[1].score:.4f}, doc_id={t2.get('doc_id')})")
            if len(hits) > 2:
                t3 = hits[2].payload
                print(f"       Current Top 3: {t3.get('official_number')} {t3.get('article_number')} (score={hits[2].score:.4f}, doc_id={t3.get('doc_id')})")
            if len(hits) > 3:
                t4 = hits[3].payload
                print(f"       Current Top 4: {t4.get('official_number')} {t4.get('article_number')} (score={hits[3].score:.4f}, doc_id={t4.get('doc_id')})")

if __name__ == "__main__":
    analyze()
