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
from backend.app.services.rag.retriever import HybridRetriever

CLOUD_URL = "https://69f07c1e-2e88-452f-aded-6dd577ddbd9b.us-west-2-0.aws.cloud.qdrant.io"
CLOUD_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIiwic3ViamVjdCI6ImFwaS1rZXk6OTAxNjk0MzUtYjMwMS00YjAzLWFmMGYtYmYyZjc0MWE4MjYxIn0.bJ2YtMtnmDJXN4k3FKdduN_TsLARSOAvGjBRKW3p028"

BENCHMARK_FILE = PROJECT_ROOT / "data" / "03_parsed" / "traffic_p0_5_batch" / "benchmark_25_cases.json"
REPORT_FILE = PROJECT_ROOT / "data" / "03_parsed" / "traffic_p1_2_batch" / "temporal_aware_benchmark_report.json"
STAGING_COLLECTION = "vietlegal_articles_staging"

def run_temporal_benchmark():
    print("=" * 100)
    print(" TASK 2: TEMPORAL-AWARE BENCHMARK ON COMBINED STAGING (7,658 POINTS)")
    print("=" * 100)

    store = QdrantVectorStore(collection_name=STAGING_COLLECTION, url=CLOUD_URL, api_key=CLOUD_API_KEY)
    embedder = get_embedding_service()
    retriever = HybridRetriever(vector_store=store, embedding_service=embedder)

    with open(BENCHMARK_FILE, "r", encoding="utf-8") as f:
        test_cases = json.load(f)["cases"]

    # 1. VERIFY CONTRASTIVE PAIR 01A & 01B SPECIFICALLY
    contrast_query = "Thí sinh thi sát hạch lái xe ô tô vào ngày 30/06/2026 có phải thực hiện bài thi mô phỏng tình huống giao thông không?"

    print("\n[*] PART A: SPECIFIC TEMPORAL PAIR 01A / 01B VERIFICATION")
    print("-" * 100)

    # 01A: 2026-06-30
    res_a = retriever.retrieve(query=contrast_query, as_of_date="2026-06-30", top_k=5)
    top1_a = res_a[0] if res_a else {}
    top1_a_doc = str(top1_a.get("doc_id", "") or top1_a.get("official_number", ""))
    top1_a_art = str(top1_a.get("article_number", ""))
    top1_a_title = str(top1_a.get("article_title", ""))

    pass_01a = ("12_2025" in top1_a_doc or "12/2025" in top1_a_doc) and "108_2026" not in top1_a_doc and "94_2026" not in top1_a_doc

    print(f"-> [TC-DOM-CONTRAST-01A] as_of_date = 2026-06-30:")
    print(f"   Expected: Thông tư 12/2025/TT-BCA Điều 14 (Có hiệu lực đến 30/06/2026)")
    print(f"   Found Top 1: {top1_a_doc} | {top1_a_art} ({top1_a_title})")
    print(f"   ND 94/2026 & TT 108/2026 correctly excluded: {'94_2026' not in top1_a_doc and '108_2026' not in top1_a_doc}")
    print(f"   Status: {'PASS 🟢' if pass_01a else 'FAIL 🔴'}")

    # 01B: 2026-07-01
    res_b = retriever.retrieve(query=contrast_query, as_of_date="2026-07-01", top_k=5)
    top1_b = res_b[0] if res_b else {}
    top1_b_doc = str(top1_b.get("doc_id", "") or top1_b.get("official_number", ""))
    top1_b_art = str(top1_b.get("article_number", ""))
    top1_b_title = str(top1_b.get("article_title", ""))

    pass_01b = "108_2026" in top1_b_doc or "108/2026" in top1_b_doc

    print(f"\n-> [TC-DOM-CONTRAST-01B] as_of_date = 2026-07-01:")
    print(f"   Expected: Thông tư 108/2026/TT-BCA Điều 15/Điều 35 (Có hiệu lực từ 01/07/2026)")
    print(f"   Found Top 1: {top1_b_doc} | {top1_b_art} ({top1_b_title})")
    print(f"   Status: {'PASS 🟢' if pass_01b else 'FAIL 🔴'}")

    # 2. RUN TEMPORAL FILTERING ON VECTOR RETRIEVAL FOR ALL 25 CASES
    # Using store.search_similar(as_of_date=tc['as_of_date']) to evaluate Temporal-Aware Vector Retrieval
    print("\n" + "=" * 100)
    print("[*] PART B: 25 BASELINE CASES EVALUATED WITH TEMPORAL-AWARE METADATA FILTERING")
    print("-" * 100)

    temporal_results = []
    t_hit1 = 0
    t_hit2 = 0
    t_hit3 = 0

    for idx, tc in enumerate(test_cases, 1):
        cid = tc["test_case_id"]
        dim = tc["dimension"]
        query = tc["query"]
        as_of = tc["as_of_date"]
        expected = tc["expected_documents"]

        vec = embedder.embed_texts([query])[0]
        # Temporal filtering by effective_date <= as_of_date
        hits = store.search_similar(query_vector=vec, limit=5, as_of_date=as_of)

        rank_hit = None
        matched_doc = None
        top1_doc = hits[0].get("official_number") or hits[0].get("doc_title", "Unknown")[:25] if hits else "None"
        top1_score = round(hits[0].get("score", 0.0), 4) if hits else 0.0

        for r, h in enumerate(hits, 1):
            doc_id = str(h.get("doc_id", "") or "")
            off_num = str(h.get("official_number", "") or "")
            title = str(h.get("doc_title", "") or "")
            art = str(h.get("article_number", "") or h.get("article", "") or "")

            is_match = any(exp in doc_id or exp in off_num or exp in title for exp in expected)
            if is_match and rank_hit is None:
                rank_hit = r
                matched_doc = f"{off_num or title[:20]} {art}".strip()

        if rank_hit == 1:
            t_hit1 += 1
            t_hit2 += 1
            t_hit3 += 1
        elif rank_hit == 2:
            t_hit2 += 1
            t_hit3 += 1
        elif rank_hit == 3:
            t_hit3 += 1

        status_str = f"Rank #{rank_hit}" if rank_hit else "MISS"
        print(f"[{idx:02d}/25] {cid:20} | as_of={as_of} | {status_str:8} | Top1: {top1_doc[:25]} ({top1_score})")

        temporal_results.append({
            "test_case_id": cid,
            "dimension": dim,
            "as_of_date": as_of,
            "expected_documents": expected,
            "rank": rank_hit,
            "top1_doc": top1_doc,
            "top1_score": top1_score
        })

    print("-" * 100)
    print(f"TEMPORAL-AWARE METRICS:")
    print(f"Hit@1: {t_hit1}/25 ({t_hit1/25*100:.1f}%)")
    print(f"Hit@2: {t_hit2}/25 ({t_hit2/25*100:.1f}%)")
    print(f"Hit@3: {t_hit3}/25 ({t_hit3/25*100:.1f}%)")
    print("=" * 100)

    report_data = {
        "benchmark_name": "Temporal-Aware Traffic Domain Benchmark Report",
        "evaluated_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "collection_name": STAGING_COLLECTION,
        "staging_points_count": store.client.get_collection(STAGING_COLLECTION).points_count,
        "contrastive_pair_01": {
            "case_01a": {
                "as_of_date": "2026-06-30",
                "expected": "12/2025/TT-BCA",
                "actual_top1": f"{top1_a_doc} {top1_a_art}",
                "status": "PASS" if pass_01a else "FAIL"
            },
            "case_01b": {
                "as_of_date": "2026-07-01",
                "expected": "108/2026/TT-BCA",
                "actual_top1": f"{top1_b_doc} {top1_b_art}",
                "status": "PASS" if pass_01b else "FAIL"
            },
            "overall_pair_status": "PASS" if (pass_01a and pass_01b) else "FAIL"
        },
        "temporal_vector_metrics": {
            "total_cases": 25,
            "hit1": t_hit1,
            "hit1_pct": round(t_hit1 / 25 * 100, 1),
            "hit2": t_hit2,
            "hit2_pct": round(t_hit2 / 25 * 100, 1),
            "hit3": t_hit3,
            "hit3_pct": round(t_hit3 / 25 * 100, 1)
        },
        "cases": temporal_results
    }

    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        json.dump(report_data, f, ensure_ascii=False, indent=2)

    print(f"\n[OK] Đã lưu báo cáo Temporal-Aware Benchmark vào: {REPORT_FILE}")

if __name__ == "__main__":
    run_temporal_benchmark()
