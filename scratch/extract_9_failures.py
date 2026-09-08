import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open("evals/benchmark_report.json", "r", encoding="utf-8") as f:
    report = json.load(f)

with open("evals/vietlegal_benchmark.json", "r", encoding="utf-8") as f:
    benchmarks = {b["id"]: b for b in json.load(f)}

details = report.get("details", [])
non_passed = [c for c in details if not c.get("passed", False)]

print(f"Tổng số case không PASS: {len(non_passed)}/30\n")

for idx, c in enumerate(non_passed, 1):
    tc_id = c.get("id")
    bm = benchmarks.get(tc_id, {})
    cat = c.get("category")
    title = c.get("title")
    query = c.get("query")
    retrieval_ok = c.get("retrieval_ok")
    matched_articles = c.get("matched_articles")
    missing_articles = c.get("missing_articles")
    kw_ratio = c.get("kw_ratio")
    hit_forbidden = c.get("hit_forbidden")
    status = c.get("status")
    answer = c.get("full_answer")
    ground_truth = bm.get("ground_truth")
    expected_kw = bm.get("expected_keywords")
    forbidden_kw = bm.get("forbidden_keywords")

    print("=" * 100)
    print(f"Case {idx}: [{tc_id}] {title}")
    print(f"Category: {cat}")
    print(f"Query: {query}")
    print(f"Ground Truth: {ground_truth}")
    print(f"Expected Keywords: {expected_kw}")
    print(f"Forbidden Keywords: {forbidden_kw}")
    print(f"Retrieval: {'OK' if retrieval_ok else 'FAILED'} | Matched: {matched_articles} | Missing: {missing_articles}")
    print(f"KW Ratio: {kw_ratio} | Hit Forbidden: {hit_forbidden}")
    print(f"Status: {status}")
    print(f"\n--- MODEL ANSWER ---:\n{answer}\n")
