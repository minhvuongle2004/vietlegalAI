import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
import json
from collections import defaultdict

with open("sparse_225_results.json", "r", encoding="utf-8") as f:
    data = json.load(f)

cases = data["cases"]

cats = defaultdict(lambda: {"total": 0, "h1": 0, "h3": 0, "h5": 0, "dense_h5": 0})
for c in cases:
    cat = c.get("category", "UNKNOWN")
    cats[cat]["total"] += 1
    sr = c.get("sparse_rank")
    dr = c.get("dense_rank")
    if sr == 1:
        cats[cat]["h1"] += 1
        cats[cat]["h3"] += 1
        cats[cat]["h5"] += 1
    elif sr in [2, 3]:
        cats[cat]["h3"] += 1
        cats[cat]["h5"] += 1
    elif sr in [4, 5]:
        cats[cat]["h5"] += 1
        
    if dr and dr <= 5:
        cats[cat]["dense_h5"] += 1

print("=== CATEGORY BREAKDOWN ===")
for cat, s in sorted(cats.items()):
    tot = s["total"]
    print(f"{cat:<25}: Tot={tot:2d} | Sp_H@1={s['h1']:2d} ({s['h1']/tot*100:4.1f}%) | Sp_H@3={s['h3']:2d} ({s['h3']/tot*100:4.1f}%) | Sp_H@5={s['h5']:2d} ({s['h5']/tot*100:4.1f}%) | Dense_H@5={s['dense_h5']:2d} ({s['dense_h5']/tot*100:4.1f}%)")

print("\n=== THE 14 BOTH CORRECT CASES ===")
for c in cases:
    dr = c.get("dense_rank")
    sr = c.get("sparse_rank")
    if dr and dr <= 5 and sr and sr <= 5:
        print(f"{c['case_id']}: {c['expected_evidence']['official_number']} Đ{c['expected_evidence']['article']} | Dense Rank {dr} | Sparse Rank {sr} | Q: {c['query'][:60]}...")

print("\n=== THE 3 DENSE FAIL / SPARSE PASS CASES ===")
for c in cases:
    dr = c.get("dense_rank")
    sr = c.get("sparse_rank")
    if (not dr or dr > 5) and (sr and sr <= 5):
        print(f"{c['case_id']}: {c['expected_evidence']['official_number']} Đ{c['expected_evidence']['article']} | Dense: {dr} | Sparse: {sr} | Q: {c['query']}")
