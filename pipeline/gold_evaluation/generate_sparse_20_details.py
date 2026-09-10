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

from backend.app.services.rag.retriever import HybridRetriever

retriever = HybridRetriever()

GOLD_DATASET_FILE = PROJECT_ROOT / "data" / "gold_evaluation" / "gold_retrieval_225_cases.json"
with open(GOLD_DATASET_FILE, "r", encoding="utf-8") as f:
    gold_data = json.load(f)
cases = gold_data["cases"]

# 20 representative cases:
# - 5 direct questions
# - 5 article retrieval
# - 5 temporal/amendment
# - 5 speed/lane/GPLX

direct_cases = [c for c in cases if c["category"] == "DIRECT_RULE"][:5]
article_cases = [c for c in cases if c["category"] == "ARTICLE_RETRIEVAL"][:5]
temporal_cases = [c for c in cases if c["category"] in ["TEMPORAL_QUERY", "AMENDMENT_LINEAGE"]][:5]
speed_lane_gplx_cases = [c for c in cases if any(k in c["query"].lower() for k in ["tốc độ", "làn", "gplx", "giấy phép lái xe"])][:5]

test_20 = direct_cases + article_cases + temporal_cases + speed_lane_gplx_cases

results_20 = []

for i, tc in enumerate(test_20, 1):
    q = tc["query"]
    cid = tc["test_case_id"]
    cat = tc["category"]
    exp = tc["expected_evidence"]
    as_of = tc.get("as_of_date")
    
    # Analyze searchable logic used by retriever
    # Check regex for Điều/Khoản
    import re
    art_nums = re.findall(r"(?:điều|khoản)\s*(\d+)", q.lower())
    triggers_matched = []
    q_l = q.lower()
    if "tốc độ" in q_l or "quá tốc độ" in q_l:
        triggers_matched.append("tốc độ -> Điều 6, 7, 17, 58")
    if any(t in q_l for t in ["hiệu lực", "áp dụng từ", "2025", "2026", "thay thế nghị định 100"]):
        triggers_matched.append("temporal trigger -> Điều 53, 54, 88")
    if "trừ điểm" in q_l or "phục hồi điểm" in q_l:
        triggers_matched.append("trừ điểm -> Điều 6, 7, 50, 51, 58")
    if "tước gplx" in q_l or "không có gplx" in q_l or "sai loại gplx" in q_l:
        triggers_matched.append("gplx -> Điều 6, 7, 18, 57")
        
    sparse_results = retriever._sparse_search_bm25(q, limit=5, as_of_date=as_of)
    
    # Check if expected evidence appeared
    exp_matched = False
    exp_rank = None
    top5_formatted = []
    for r_idx, res in enumerate(sparse_results[:5], 1):
        is_match = (
            (exp["document_id"].lower() in res.get("doc_id", "").lower() or res.get("doc_id", "").lower() in exp["document_id"].lower())
            and str(res.get("article_number")) == str(exp.get("article"))
        )
        if is_match and not exp_matched:
            exp_matched = True
            exp_rank = r_idx
        top5_formatted.append({
            "rank": r_idx,
            "doc_id": res.get("doc_id"),
            "official_number": res.get("official_number", "N/A"),
            "article_number": res.get("article_number"),
            "article_title": res.get("article_title"),
            "score": "N/A (unranked SQL fetch)"
        })
        
    results_20.append({
        "case_num": i,
        "test_case_id": cid,
        "category": cat,
        "query": q,
        "as_of_date": as_of,
        "searchable_index_used": "Supabase legal_articles (filter: article_number eq & title ilike; NO tsvector BM25)",
        "hardcoded_triggers": triggers_matched or ["No trigger matched -> Empty query unless regex matched"],
        "regex_extracted_articles": art_nums or "None",
        "returned_count": len(sparse_results),
        "expected_evidence": f"{exp['official_number']} ({exp['document_id']}) Điều {exp.get('article')}",
        "expected_appeared": exp_matched,
        "expected_rank": exp_rank,
        "top5_results": top5_formatted
    })

output_file = PROJECT_ROOT / "data" / "gold_evaluation" / "sparse_20_validation.json"
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(results_20, f, ensure_ascii=False, indent=2)

print(f"Generated sparse validation for 20 cases into {output_file}")
print("Expected evidence appeared count:", sum(1 for r in results_20 if r["expected_appeared"]), "/ 20")
