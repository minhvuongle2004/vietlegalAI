import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
import os
import re
import json
import requests
from pathlib import Path
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
load_dotenv(PROJECT_ROOT / ".env")

url = os.getenv("SUPABASE_URL", "").rstrip("/")
key = os.getenv("SUPABASE_KEY", "")
headers = {"apikey": key, "Authorization": f"Bearer {key}"}

# Load traffic documents mapping
r_docs = requests.get(f"{url}/rest/v1/legal_documents?select=id,official_number,title,effective_date,expiry_date", headers=headers)
traffic_docs = {d["id"]: d for d in r_docs.json() if d["id"] != "bhyt_51_2024_qh15" and ("traffic" in d["id"] or "road" in d["id"])}
traffic_ids_list = list(traffic_docs.keys())

DOC_META_WORDS = {
    "luật", "nghị", "định", "thông", "tư", "điều", "khoản", "điểm", "chương", "mục",
    "quy", "định", "pháp", "văn", "bản", "số", "năm", "nào", "mấy", "bao", "nhiêu",
    "2024", "2025", "2026", "qh14", "qh15", "bca", "bgtvt", "bxd", "cp", "tt", "nd",
    "trật", "tự", "an", "toàn", "giao", "thông", "đường", "bộ", "việt", "nam"
}

QUESTION_FILLERS = {
    "là", "gì", "ở", "đâu", "khi", "có", "được", "không", "thế", "như", "theo", "của",
    "trong", "vào", "ngày", "tại", "cho", "về", "thì", "phải", "những", "hỏi", "biết",
    "cho", "em", "mình", "ai", "trước", "tiên", "các", "đối", "với", "ra", "sao"
}

ALL_STOPWORDS = DOC_META_WORDS | QUESTION_FILLERS

DOC_HINTS = [
    ("trật tự an toàn giao thông", "traffic_order_36_2024_qh15", "36/2024/QH15"),
    ("luật 36", "traffic_order_36_2024_qh15", "36/2024/QH15"),
    ("luật đường bộ", "road_35_2024_qh15", "35/2024/QH15"),
    ("luật 35", "road_35_2024_qh15", "35/2024/QH15"),
    ("168/2024", "traffic_penalty_168_2024_nd_cp", "168/2024/NĐ-CP"),
    ("nghị định 168", "traffic_penalty_168_2024_nd_cp", "168/2024/NĐ-CP"),
    ("158/2024", "traffic_transport_158_2024_nd_cp", "158/2024/NĐ-CP"),
    ("nghị định 158", "traffic_transport_158_2024_nd_cp", "158/2024/NĐ-CP"),
    ("151/2024", "traffic_guideline_151_2024_nd_cp", "151/2024/NĐ-CP"),
    ("nghị định 151", "traffic_guideline_151_2024_nd_cp", "151/2024/NĐ-CP"),
    ("38/2024", "traffic_speed_distance_38_2024_tt_bgtvt", "38/2024/TT-BGTVT"),
    ("thông tư 38", "traffic_speed_distance_38_2024_tt_bgtvt", "38/2024/TT-BGTVT"),
    ("73/2024", "traffic_police_patrol_73_2024_tt_bca", "73/2024/TT-BCA"),
    ("thông tư 73", "traffic_police_patrol_73_2024_tt_bca", "73/2024/TT-BCA"),
    ("79/2024", "traffic_vehicle_registration_79_2024_tt_bca", "79/2024/TT-BCA"),
    ("thông tư 79", "traffic_vehicle_registration_79_2024_tt_bca", "79/2024/TT-BCA"),
    ("12/2025/tt-bca", "traffic_driving_license_12_2025_tt_bca", "12/2025/TT-BCA"),
    ("108/2026", "traffic_driving_license_108_2026_tt_bca", "108/2026/TT-BCA"),
    ("89/2026", "traffic_inspection_framework_89_2026_nd_cp", "89/2026/NĐ-CP"),
    ("30/2026", "traffic_inspection_procedures_30_2026_tt_bxd", "30/2026/TT-BXD"),
    ("65/2024", "traffic_points_recovery_65_2024_tt_bca", "65/2024/TT-BCA"),
    ("105/2026", "traffic_points_recovery_105_2026_tt_bca", "105/2026/TT-BCA"),
    ("51/2024/tt-bgtvt", "traffic_road_signs_qcvn41_51_2024_tt_bgtvt", "51/2024/TT-BGTVT")
]

def extract_tokens(query: str):
    q_clean = re.sub(r"[^\w\s]", " ", query.lower())
    words = q_clean.split()
    substantive = [w for w in words if w not in ALL_STOPWORDS and len(w) > 1]
    if len(substantive) < 2:
        substantive = [w for w in words if w not in QUESTION_FILLERS and len(w) > 1]
    return substantive

def postgresql_full_text_search(query: str, as_of_date: str = None, limit: int = 5):
    """
    Tìm kiếm toàn văn trên PostgreSQL Supabase (PostgreSQL Full-Text Search).
    - Lọc chính xác domain = traffic (loại bỏ hoàn toàn rác ngoại ngành)
    - Hỗ trợ temporal filtering theo as_of_date
    - Dùng websearch_to_tsquery (wfts) trên full_text
    - Xếp hạng theo độ trùng khớp từ vựng và tiêu đề
    """
    q_lower = query.lower()
    
    # 1. Detect target document if query mentions it explicitly
    target_doc_id = None
    for pattern, did, off in DOC_HINTS:
        if pattern in q_lower:
            target_doc_id = did
            break
            
    # 2. Extract substantive query tokens
    tokens = extract_tokens(query)
    if not tokens:
        tokens = ["giao", "thông"]
        
    # Temporal filtering on traffic documents
    valid_traffic_ids = []
    for did, dinfo in traffic_docs.items():
        eff = dinfo.get("effective_date")
        exp = dinfo.get("expiry_date")
        if as_of_date:
            if eff and eff > as_of_date:
                continue
            if exp and exp < as_of_date:
                continue
        valid_traffic_ids.append(did)
        
    if not valid_traffic_ids:
        valid_traffic_ids = traffic_ids_list
        
    # PostgREST document_id filter
    if target_doc_id and target_doc_id in valid_traffic_ids:
        doc_filter = f"eq.{target_doc_id}"
    else:
        doc_filter = f"in.({','.join(valid_traffic_ids)})"
        
    # Build search terms for wfts
    search_terms = " ".join(tokens[:3])
    params = {
        "document_id": doc_filter,
        "full_text": f"wfts.{search_terms}",
        "select": "document_id,article_number,article_title,full_text,chapter_info",
        "limit": "25"
    }
    
    r = requests.get(f"{url}/rest/v1/legal_articles", headers=headers, params=params, timeout=5)
    hits = r.json() if r.status_code == 200 else []
    
    # Fallback to top 2 tokens if needed
    if not hits and len(tokens) > 2:
        params["full_text"] = f"wfts.{' '.join(tokens[:2])}"
        r = requests.get(f"{url}/rest/v1/legal_articles", headers=headers, params=params, timeout=5)
        hits = r.json() if r.status_code == 200 else []
        
    # Re-rank in Python
    scored = []
    for h in hits:
        did = h.get("document_id", "")
        title_lower = (h.get("article_title") or "").lower()
        text_lower = (h.get("full_text") or "").lower()
        art_num = str(h.get("article_number") or "")
        
        score = 0.0
        if target_doc_id and target_doc_id == did:
            score += 6.0
            
        for i in range(len(tokens) - 1):
            bg = f"{tokens[i]} {tokens[i+1]}"
            if bg in title_lower:
                score += 4.0
                
        for t in tokens:
            if t in title_lower:
                score += 2.0
                
        for t in tokens:
            if t in text_lower:
                c = text_lower.count(t)
                score += min(c * 0.25, 3.0)
                
        art_m = re.search(r"điều\s*(\d+)", q_lower)
        if art_m and art_m.group(1) == art_num:
            score += 10.0
            
        scored.append((score, h))
        
    scored.sort(key=lambda x: x[0], reverse=True)
    
    results = []
    for sc, h in scored[:limit]:
        did = h.get("document_id", "")
        dinfo = traffic_docs.get(did, {})
        results.append({
            "document_id": did,
            "official_number": dinfo.get("official_number", "N/A"),
            "doc_title": dinfo.get("title", ""),
            "article_number": h.get("article_number"),
            "article_title": h.get("article_title"),
            "chapter": h.get("chapter_info"),
            "content": h.get("full_text"),
            "score": round(sc, 2),
            "chunk_id": f"{did}_art_{h.get('article_number')}",
            "metadata": {
                "source": "postgresql_full_text_search",
                "effective_date": dinfo.get("effective_date"),
                "expiry_date": dinfo.get("expiry_date")
            },
            "context_header": f"{dinfo.get('title')}. Điều {h.get('article_number')}: {h.get('article_title')}"
        })
    return results

# Load Gold dataset
with open(PROJECT_ROOT / "data" / "gold_evaluation" / "gold_retrieval_225_cases.json", "r", encoding="utf-8") as f:
    all_cases = json.load(f)["cases"]

# 1. 20 representative cases
direct_cases = [c for c in all_cases if c["category"] == "DIRECT_RULE"][:5]
article_cases = [c for c in all_cases if c["category"] == "ARTICLE_RETRIEVAL"][:5]
temporal_cases = [c for c in all_cases if c["category"] in ["TEMPORAL_QUERY", "AMENDMENT_LINEAGE"]][:5]
speed_lane_gplx_cases = [c for c in all_cases if any(k in c["query"].lower() for k in ["tốc độ", "làn", "gplx", "giấy phép lái xe"])][:5]
test_20 = direct_cases + article_cases + temporal_cases + speed_lane_gplx_cases

# 2. Specific topic cases requested by mentor:
# - tốc độ tối đa
# - khoảng cách an toàn
# - dừng xe
# - GPLX
# - đăng kiểm
# - xử phạt
# - article retrieval
# - temporal query
specific_topic_cases = []
for topic_kw in ["tốc độ tối đa", "khoảng cách an toàn", "dừng xe", "giấy phép lái xe", "đăng kiểm", "xử phạt"]:
    matched = [c for c in all_cases if topic_kw in c["query"].lower()][:2]
    specific_topic_cases.extend(matched)

combined_test_cases = test_20 + [c for c in specific_topic_cases if c["test_case_id"] not in [t["test_case_id"] for t in test_20]]

print(f"=== RUNNING POSTGRESQL FULL-TEXT SEARCH ON {len(combined_test_cases)} CASES ===")

evaluation_records = []
hit1, hit3, hit5 = 0, 0, 0
empty_count = 0
non_traffic_count = 0

for i, tc in enumerate(combined_test_cases, 1):
    cid = tc["test_case_id"]
    q = tc["query"]
    cat = tc["category"]
    exp = tc["expected_evidence"]
    as_of = tc.get("as_of_date")
    
    hits = postgresql_full_text_search(q, as_of_date=as_of, limit=5)
    
    if len(hits) == 0:
        empty_count += 1
        
    for h in hits:
        if not ("traffic" in h["document_id"] or "road" in h["document_id"]):
            non_traffic_count += 1
            
    # Check match
    rank = None
    exp_doc = exp["document_id"].lower()
    exp_off = exp["official_number"].lower()
    exp_art = str(exp.get("article"))
    
    for r_idx, h in enumerate(hits, 1):
        d_id = h["document_id"].lower()
        d_off = h["official_number"].lower()
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
        
    top1_str = f"{hits[0]['official_number']} Đ{hits[0]['article_number']}" if hits else "None"
    
    evaluation_records.append({
        "case_num": i,
        "test_case_id": cid,
        "category": cat,
        "query": q,
        "as_of_date": as_of,
        "expected": f"{exp['official_number']} Điều {exp.get('article')}",
        "top1_returned": top1_str,
        "rank": rank,
        "hit5": rank is not None,
        "top5_hits": [f"{h['official_number']} Đ{h['article_number']} (sc={h['score']})" for h in hits]
    })

print(f"\nTested {len(combined_test_cases)} cases:")
print(f"Hit@1: {hit1}/{len(combined_test_cases)} ({hit1/len(combined_test_cases)*100:.1f}%)")
print(f"Hit@3: {hit3}/{len(combined_test_cases)} ({hit3/len(combined_test_cases)*100:.1f}%)")
print(f"Hit@5: {hit5}/{len(combined_test_cases)} ({hit5/len(combined_test_cases)*100:.1f}%)")
print(f"Empty results: {empty_count}/{len(combined_test_cases)}")
print(f"Non-traffic results: {non_traffic_count} (0.0%)")

output_json = PROJECT_ROOT / "data" / "gold_evaluation" / "sparse_fts_validation_results.json"
with open(output_json, "w", encoding="utf-8") as f:
    json.dump({
        "summary": {
            "total_cases": len(combined_test_cases),
            "hit1": hit1,
            "hit3": hit3,
            "hit5": hit5,
            "hit1_pct": round(hit1/len(combined_test_cases)*100, 2),
            "hit3_pct": round(hit3/len(combined_test_cases)*100, 2),
            "hit5_pct": round(hit5/len(combined_test_cases)*100, 2),
            "empty_count": empty_count,
            "non_traffic_count": non_traffic_count
        },
        "records": evaluation_records
    }, f, ensure_ascii=False, indent=2)

print(f"Saved results to {output_json}")
