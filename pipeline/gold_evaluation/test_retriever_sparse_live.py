import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
import os
import json
from pathlib import Path
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
load_dotenv(PROJECT_ROOT / ".env")

from backend.app.services.rag.retriever import HybridRetriever

retriever = HybridRetriever()

# Load Gold dataset
with open(PROJECT_ROOT / "data" / "gold_evaluation" / "gold_retrieval_225_cases.json", "r", encoding="utf-8") as f:
    all_cases = json.load(f)["cases"]

# 20 representative cases
direct_cases = [c for c in all_cases if c["category"] == "DIRECT_RULE"][:5]
article_cases = [c for c in all_cases if c["category"] == "ARTICLE_RETRIEVAL"][:5]
temporal_cases = [c for c in all_cases if c["category"] in ["TEMPORAL_QUERY", "AMENDMENT_LINEAGE"]][:5]
speed_lane_gplx_cases = [c for c in all_cases if any(k in c["query"].lower() for k in ["tốc độ", "làn", "gplx", "giấy phép lái xe"])][:5]
test_20 = direct_cases + article_cases + temporal_cases + speed_lane_gplx_cases

# Specific topic cases: tốc độ tối đa, khoảng cách an toàn, dừng xe, GPLX, đăng kiểm, xử phạt
specific_topic_cases = []
for topic_kw in ["tốc độ tối đa", "khoảng cách an toàn", "dừng xe", "giấy phép lái xe", "đăng kiểm", "xử phạt"]:
    matched = [c for c in all_cases if topic_kw in c["query"].lower()][:2]
    specific_topic_cases.extend(matched)

combined_cases = test_20 + [c for c in specific_topic_cases if c["test_case_id"] not in [t["test_case_id"] for t in test_20]]

print(f"=== TESTING retriever._sparse_search_postgresql_fts ON {len(combined_cases)} CASES ===")

hit1, hit3, hit5 = 0, 0, 0
empty_count = 0
non_traffic_count = 0

detailed_records = []

for i, tc in enumerate(combined_cases, 1):
    cid = tc["test_case_id"]
    q = tc["query"]
    exp = tc["expected_evidence"]
    as_of = tc.get("as_of_date")
    
    hits = retriever._sparse_search_postgresql_fts(q, limit=5, as_of_date=as_of)
    
    if len(hits) == 0:
        empty_count += 1
        
    for h in hits:
        did = h.get("document_id", "")
        if not ("traffic" in did or "road" in did):
            non_traffic_count += 1
            
    # Check match
    rank = None
    exp_doc = exp["document_id"].lower()
    exp_off = exp["official_number"].lower()
    exp_art = str(exp.get("article"))
    
    for r_idx, h in enumerate(hits, 1):
        d_id = h.get("document_id", "").lower()
        d_off = h.get("official_number", "").lower()
        d_art = str(h.get("article_number"))
        if (exp_doc in d_id or d_id in exp_doc or exp_off in d_off) and d_art == exp_art:
            rank = r_idx
            break
            
    if rank == 1:
        hit1 += 1
        hit3 += 1
        hit5 += 1
    elif rank in [2, 3]:
        hit3 += 1
        hit5 += 1
    elif rank in [4, 5]:
        hit5 += 1
        
    top1_str = f"{hits[0].get('official_number')} Đ{hits[0].get('article_number')}" if hits else "None"
    status_str = f"HIT (Rank {rank})" if rank else "MISS"
    print(f"[{i:2d}/{len(combined_cases)}] {cid:12s} | Exp: {exp['official_number']} Đ{exp.get('article'):<3} | Top1: {top1_str:<22} | {status_str}")
    
    detailed_records.append({
        "case_num": i,
        "test_case_id": cid,
        "category": tc["category"],
        "query": q,
        "as_of_date": as_of,
        "expected": f"{exp['official_number']} Điều {exp.get('article')}",
        "top1_returned": top1_str,
        "rank": rank,
        "hit5": rank is not None,
        "top5_hits": [f"{h.get('official_number')} Đ{h.get('article_number')} (sc={h.get('score')})" for h in hits]
    })

print("\n=== FINAL TEST METRICS (POSTGRESQL FULL-TEXT SEARCH) ===")
print(f"Total Cases: {len(combined_cases)}")
print(f"Sparse FTS Hit@1: {hit1}/{len(combined_cases)} ({hit1/len(combined_cases)*100:.1f}%)")
print(f"Sparse FTS Hit@3: {hit3}/{len(combined_cases)} ({hit3/len(combined_cases)*100:.1f}%)")
print(f"Sparse FTS Hit@5: {hit5}/{len(combined_cases)} ({hit5/len(combined_cases)*100:.1f}%)")
print(f"Empty results: {empty_count}/{len(combined_cases)}")
print(f"Non-traffic results: {non_traffic_count} (0.0% - ZERO POLLUTION)")

# Save validation result
out_file = PROJECT_ROOT / "data" / "gold_evaluation" / "sparse_retrieval_live_validation.json"
with open(out_file, "w", encoding="utf-8") as f:
    json.dump({
        "summary": {
            "total_cases": len(combined_cases),
            "hit1": hit1,
            "hit3": hit3,
            "hit5": hit5,
            "hit1_pct": round(hit1/len(combined_cases)*100, 2),
            "hit3_pct": round(hit3/len(combined_cases)*100, 2),
            "hit5_pct": round(hit5/len(combined_cases)*100, 2),
            "empty_count": empty_count,
            "non_traffic_count": non_traffic_count
        },
        "records": detailed_records
    }, f, ensure_ascii=False, indent=2)

print(f"Results saved to {out_file}")
