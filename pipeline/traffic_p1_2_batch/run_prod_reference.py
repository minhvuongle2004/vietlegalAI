import os
import sys
import json
import time
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.services.rag.embeddings import get_embedding_service
from backend.app.services.rag.vector_store import QdrantVectorStore

CLOUD_URL = "https://69f07c1e-2e88-452f-aded-6dd577ddbd9b.us-west-2-0.aws.cloud.qdrant.io"
CLOUD_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIiwic3ViamVjdCI6ImFwaS1rZXk6OTAxNjk0MzUtYjMwMS00YjAzLWFmMGYtYmYyZjc0MWE4MjYxIn0.bJ2YtMtnmDJXN4k3FKdduN_TsLARSOAvGjBRKW3p028"

BENCHMARK_FILE = PROJECT_ROOT / "data" / "03_parsed" / "traffic_p0_5_batch" / "benchmark_25_cases.json"
RESULTS_FILE = PROJECT_ROOT / "data" / "03_parsed" / "traffic_p1_2_batch" / "production_reference_results.json"
PROD_COLLECTION = "vietlegal_articles"

def run_prod_reference():
    print("=" * 100)
    print(" RUNNING FROZEN PRODUCTION REFERENCE (vietlegal_articles - 7,495 points)")
    print("=" * 100)

    with open(BENCHMARK_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
        test_cases = data["cases"]

    store = QdrantVectorStore(collection_name=PROD_COLLECTION, url=CLOUD_URL, api_key=CLOUD_API_KEY)
    embedder = get_embedding_service()

    detailed_results = []
    dim_stats = {
        "GPLX": {"total": 0, "hit1": 0, "hit2": 0, "hit3": 0},
        "DANG_KY_XE": {"total": 0, "hit1": 0, "hit2": 0, "hit3": 0},
        "TOC_DO_KHOANG_CACH": {"total": 0, "hit1": 0, "hit2": 0, "hit3": 0},
        "CONTRASTIVE_PAIRS": {"total": 0, "hit1": 0, "hit2": 0, "hit3": 0}
    }

    t0 = time.time()

    for idx, tc in enumerate(test_cases, 1):
        cid = tc["test_case_id"]
        dim = tc["dimension"]
        cat = tc["category"]
        query = tc["query"]
        expected = tc["expected_documents"]
        as_of = tc["as_of_date"]

        dim_stats[dim]["total"] += 1

        vec = embedder.embed_texts([query])[0]
        hits = store.search_similar(query_vector=vec, limit=5)

        rank_hit = None
        matched_doc = None
        top1_doc = hits[0].get("official_number") or hits[0].get("doc_title", "Unknown")[:25] if hits else "None"
        top1_score = round(hits[0].get("score", 0.0), 4) if hits else 0.0

        for r, h in enumerate(hits, 1):
            doc_id = str(h.get("doc_id", "") or "")
            off_num = str(h.get("official_number", "") or "")
            title = str(h.get("doc_title", "") or "")
            art = str(h.get("article_number", "") or h.get("article", "") or "")
            cl = str(h.get("clause_number", "") or h.get("clause", "") or "")

            is_match = any(exp in doc_id or exp in off_num or exp in title for exp in expected)
            if is_match and rank_hit is None:
                rank_hit = r
                matched_doc = f"{off_num or title[:20]} {art} {cl}".strip()

        if rank_hit == 1:
            dim_stats[dim]["hit1"] += 1
            dim_stats[dim]["hit2"] += 1
            dim_stats[dim]["hit3"] += 1
        elif rank_hit == 2:
            dim_stats[dim]["hit2"] += 1
            dim_stats[dim]["hit3"] += 1
        elif rank_hit == 3:
            dim_stats[dim]["hit3"] += 1

        res_entry = {
            "test_case_id": cid,
            "dimension": dim,
            "category": cat,
            "query": query,
            "as_of_date": as_of,
            "rank": rank_hit,
            "matched_doc": matched_doc,
            "top1_doc": top1_doc,
            "top1_score": top1_score,
            "expected_documents": expected,
            "expected_primary_evidence": tc.get("expected_primary_evidence", ""),
            "top5_candidates": [
                {
                    "rank": r,
                    "score": round(h.get("score", 0.0), 4),
                    "official_number": h.get("official_number"),
                    "article": h.get("article_number") or h.get("article"),
                    "clause": h.get("clause_number") or h.get("clause"),
                    "text_preview": (h.get("content") or h.get("full_search_text") or "")[:100]
                }
                for r, h in enumerate(hits, 1)
            ]
        }
        detailed_results.append(res_entry)

    elapsed = round(time.time() - t0, 2)
    total_cases = len(test_cases)
    total_hit1 = sum(d["hit1"] for d in dim_stats.values())
    total_hit2 = sum(d["hit2"] for d in dim_stats.values())
    total_hit3 = sum(d["hit3"] for d in dim_stats.values())

    print("\n" + "=" * 100)
    print(f" TỔNG KẾT METRIC PRODUCTION REFERENCE (vietlegal_articles, {elapsed}s):")
    print("=" * 100)
    print(f"-> Primary Hit@1 = {total_hit1}/{total_cases} ({total_hit1/total_cases*100:.1f}%)")
    print(f"-> Primary Hit@2 = {total_hit2}/{total_cases} ({total_hit2/total_cases*100:.1f}%)")
    print(f"-> Primary Hit@3 = {total_hit3}/{total_cases} ({total_hit3/total_cases*100:.1f}%)")
    print("-" * 100)

    output_data = {
        "benchmark_name": "Traffic Domain Expanded Benchmark (25 Cases) - Production Reference (vietlegal_articles)",
        "evaluated_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "qdrant_cloud_url": CLOUD_URL,
        "collection_name": PROD_COLLECTION,
        "points_count": store.client.get_collection(PROD_COLLECTION).points_count,
        "elapsed_seconds": elapsed,
        "overall_metrics": {
            "total_cases": total_cases,
            "primary_hit1": total_hit1,
            "primary_hit1_pct": round(total_hit1 / total_cases * 100, 1),
            "primary_hit2": total_hit2,
            "primary_hit2_pct": round(total_hit2 / total_cases * 100, 1),
            "primary_hit3": total_hit3,
            "primary_hit3_pct": round(total_hit3 / total_cases * 100, 1)
        },
        "dimension_breakdown": dim_stats,
        "detailed_results": detailed_results
    }

    with open(RESULTS_FILE, "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    print(f"\n[OK] Đã lưu kết quả Production Reference vào: {RESULTS_FILE}")

if __name__ == "__main__":
    run_prod_reference()
