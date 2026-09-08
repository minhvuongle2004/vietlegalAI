import json
import sys

with open("evals/benchmark_report.json", "r", encoding="utf-8") as f:
    report = json.load(f)

with open("evals/vietlegal_benchmark.json", "r", encoding="utf-8") as f:
    benchmarks = {b["id"]: b for b in json.load(f)}

details = report.get("details", [])
non_passed = [c for c in details if not c.get("passed", False)]

lines = []
lines.append(f"Tổng số case không PASS: {len(non_passed)}/30\n")

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

    lines.append("=" * 80)
    lines.append(f"Case {idx}: [{tc_id}] {title}")
    lines.append(f"Category: {cat}")
    lines.append(f"Query: {query}")
    lines.append(f"Ground Truth: {ground_truth}")
    lines.append(f"Expected Keywords: {expected_kw}")
    lines.append(f"Forbidden Keywords: {forbidden_kw}")
    lines.append(f"Retrieval: {'OK' if retrieval_ok else 'FAILED'} | Matched: {matched_articles} | Missing: {missing_articles}")
    lines.append(f"KW Ratio: {kw_ratio} | Hit Forbidden: {hit_forbidden}")
    lines.append(f"Status: {status}")
    lines.append(f"\n--- MODEL ANSWER ---:\n{answer}\n")

with open("scratch/failures_summary.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

print("Wrote failures_summary.txt in UTF-8")
