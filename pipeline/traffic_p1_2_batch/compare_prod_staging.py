import json
import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

with open("data/03_parsed/traffic_p1_2_batch/production_reference_results.json", "r", encoding="utf-8") as f:
    prod_results = json.load(f)

with open("data/03_parsed/traffic_p1_2_batch/staging_frozen_baseline_protocol_results.json", "r", encoding="utf-8") as f:
    stag_results = json.load(f)

prod_cases = {c["test_case_id"]: c for c in prod_results.get("detailed_results", [])}
stag_cases = {c["test_case_id"]: c for c in stag_results.get("detailed_results", [])}

print(f"Prod count: {len(prod_cases)}, Staging count: {len(stag_cases)}")

diffs = []
for cid, sc in stag_cases.items():
    pc = prod_cases.get(cid, {})
    p_rank = pc.get("rank")
    s_rank = sc.get("rank")
    if p_rank != s_rank or s_rank is None or s_rank > 3:
        diffs.append((cid, p_rank, s_rank, sc, pc))

print(f"Total diff cases: {len(diffs)}")
for cid, p_rank, s_rank, sc, pc in diffs:
    print("=" * 80)
    print(f"Case: {cid}")
    print(f"Prod Rank: {p_rank}  -->  Staging Rank: {s_rank}")
    print(f"Query: {sc.get('query')}")
    print(f"As of date: {sc.get('as_of_date')}")
    print(f"Expected Docs: {sc.get('expected_documents')}")
    print(f"Expected Evidence: {sc.get('expected_primary_evidence')}")
    print("\n--- Production Candidates ---")
    for i, c in enumerate(pc.get("top5_candidates", []), 1):
        print(f"  P{i}: score={c.get('score', 0):.4f} | doc_id={c.get('doc_id')} | official_num={c.get('official_number')} | art={c.get('article_number') or c.get('article_id')} | title={c.get('article_title')}")
        print(f"       keys: {list(c.keys())}")
        print(f"       text snippet: {repr(c.get('text', '')[:120])}")
    print("\n--- Staging Candidates ---")
    for i, c in enumerate(sc.get("top5_candidates", []), 1):
        print(f"  S{i}: score={c.get('score', 0):.4f} | doc_id={c.get('doc_id')} | official_num={c.get('official_number')} | art={c.get('article_number') or c.get('article_id')} | title={c.get('article_title')}")
        print(f"       keys: {list(c.keys())}")
        print(f"       text snippet: {repr(c.get('text', '')[:120])}")
