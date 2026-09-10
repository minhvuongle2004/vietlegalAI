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

BENCHMARK_FILE = PROJECT_ROOT / "data" / "03_parsed" / "traffic_p0_5_batch" / "benchmark_15_cases.json"
RESULTS_FILE = PROJECT_ROOT / "data" / "03_parsed" / "traffic_p0_5_batch" / "benchmark_15_cases_results.json"

def main():
    print("=" * 100)
    print(" ĐÁNH GIÁ THỰC TẾ: DOMAIN EXPANDED BENCHMARK (15 TEST CASES ĐA CHIỀU & CONTRASTIVE)")
    print("=" * 100)

    if not BENCHMARK_FILE.exists():
        print(f"[!] Không tìm thấy file {BENCHMARK_FILE}")
        return

    with open(BENCHMARK_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
        test_cases = data["cases"]

    store = QdrantVectorStore(url=CLOUD_URL, api_key=CLOUD_API_KEY)
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
            sc = round(h.get("score", 0.0), 4)

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

        status_str = f"Rank #{rank_hit}" if rank_hit else "MISS"
        detailed_results.append({
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
            "all_top5_hits": [
                {
                    "rank": i + 1,
                    "doc": h.get("official_number") or h.get("doc_title", "")[:25],
                    "article": h.get("article_number"),
                    "clause": h.get("clause_number"),
                    "score": round(h.get("score", 0.0), 4)
                } for i, h in enumerate(hits)
            ]
        })

        print(f"[{idx:02d}/15] {cid:<22} | {dim:<18} | Status: {status_str:<9} | Top Match: {matched_doc or top1_doc} (Top1 Score: {top1_score})")

    dur = round(time.time() - t0, 2)
    total_cases = len(test_cases)
    hit1_total = sum(d["hit1"] for d in dim_stats.values())
    hit2_total = sum(d["hit2"] for d in dim_stats.values())
    hit3_total = sum(d["hit3"] for d in dim_stats.values())

    print("\n" + "=" * 100)
    print(f" TỔNG KẾT METRIC BENCHMARK 15 TEST CASES (Thời gian chạy: {dur}s):")
    print("=" * 100)
    print(f" -> Hit@1 = {hit1_total}/{total_cases} ({round(hit1_total / total_cases * 100, 1)}%)")
    print(f" -> Hit@2 = {hit2_total}/{total_cases} ({round(hit2_total / total_cases * 100, 1)}%)")
    print(f" -> Hit@3 = {hit3_total}/{total_cases} ({round(hit3_total / total_cases * 100, 1)}%)")
    print("-" * 100)
    print(f"{'Phân khúc (Dimension)':<25} | {'Tổng số case':<12} | {'Hit@1':<12} | {'Hit@2':<12} | {'Hit@3':<12}")
    print("-" * 100)
    for dim, s in dim_stats.items():
        h1_pct = round(s["hit1"] / s["total"] * 100, 1)
        h2_pct = round(s["hit2"] / s["total"] * 100, 1)
        h3_pct = round(s["hit3"] / s["total"] * 100, 1)
        print(f"{dim:<25} | {s['total']:<12} | {s['hit1']}/{s['total']} ({h1_pct}%) | {s['hit2']}/{s['total']} ({h2_pct}%) | {s['hit3']}/{s['total']} ({h3_pct}%)")
    print("=" * 100)

    # Lưu kết quả chi tiết
    with open(RESULTS_FILE, "w", encoding="utf-8") as f:
        json.dump({
            "evaluated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "total_cases": total_cases,
            "overall_metrics": {
                "hit1": hit1_total,
                "hit2": hit2_total,
                "hit3": hit3_total,
                "hit1_rate": round(hit1_total / total_cases * 100, 1),
                "hit2_rate": round(hit2_total / total_cases * 100, 1),
                "hit3_rate": round(hit3_total / total_cases * 100, 1)
            },
            "dimension_breakdown": dim_stats,
            "detailed_results": detailed_results
        }, f, ensure_ascii=False, indent=2)

    print(f"[+] Đã lưu file kết quả chi tiết tại: {RESULTS_FILE}")

if __name__ == "__main__":
    main()
