import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
import os
import re
import requests
from dotenv import load_dotenv

load_dotenv()
url = os.getenv("SUPABASE_URL", "").rstrip("/")
key = os.getenv("SUPABASE_KEY", "")
headers = {"apikey": key, "Authorization": f"Bearer {key}"}

# Document hint mapping
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
    ("51/2024", "traffic_road_signs_qcvn41_51_2024_tt_bgtvt", "51/2024/TT-BGTVT")
]

# Get traffic documents
r_docs = requests.get(f"{url}/rest/v1/legal_documents?select=id,official_number,title,effective_date,expiry_date", headers=headers)
traffic_docs = {d["id"]: d for d in r_docs.json() if d["id"] != "bhyt_51_2024_qh15" and ("traffic" in d["id"] or "road" in d["id"])}
traffic_ids_list = list(traffic_docs.keys())

def score_candidate(query_lower: str, tokens: list, cand: dict, target_doc_id: str = None) -> float:
    score = 0.0
    doc_id = cand.get("document_id", "")
    title_lower = (cand.get("article_title") or "").lower()
    text_lower = (cand.get("full_text") or "").lower()
    art_num = str(cand.get("article_number") or "")
    
    # 1. Document match bonus
    if target_doc_id and target_doc_id == doc_id:
        score += 5.0
        
    # 2. Exact phrase in title bonus
    for i in range(len(tokens) - 1):
        bigram = f"{tokens[i]} {tokens[i+1]}"
        if bigram in title_lower:
            score += 3.0
            
    # 3. Individual token match in title
    for t in tokens:
        if t in title_lower:
            score += 1.5
            
    # 4. Token match in full text
    for t in tokens:
        if t in text_lower:
            # Term count in text
            count = text_lower.count(t)
            score += min(count * 0.2, 2.0)
            
    # 5. Question asks specifically about an article number (e.g. "Điều 15")
    q_art_match = re.search(r"điều\s*(\d+)", query_lower)
    if q_art_match and q_art_match.group(1) == art_num:
        score += 10.0
        
    return score

print("=== SCORING CANDIDATES WITH DOCUMENT AWARENESS & LEXICAL OVERLAP ===")

test_cases = [
    ("GOLD-DIR-01", "Người tham gia giao thông đường bộ phải đi bên nào theo quy định của Luật Trật tự an toàn giao thông đường bộ?", "36/2024/QH15 Điều 10"),
    ("GOLD-DIR-02", "Khi có người điều khiển giao thông thì người tham gia giao thông phải chấp hành hiệu lệnh của ai trước tiên?", "36/2024/QH15 Điều 11"),
    ("GOLD-DIR-03", "Người lái xe ô tô có được sử dụng điện thoại bằng tay khi xe đang chạy trên đường không?", "36/2024/QH15 Điều 10"),
    ("GOLD-ART-01", "Điều nào trong Luật Trật tự, an toàn giao thông đường bộ 2024 quy định về việc chuyển hướng xe?", "36/2024/QH15 Điều 15"),
    ("GOLD-ART-02", "Quy định về việc vượt xe và nhường đường cho xe xin vượt nằm ở Điều mấy của Luật 36/2024/QH15?", "36/2024/QH15 Điều 14"),
    ("GOLD-ART-03", "Điều bao nhiêu của Luật Trật tự, an toàn giao thông đường bộ quy định về dừng xe, đỗ xe trên đường?", "36/2024/QH15 Điều 18"),
    ("GOLD-ART-04", "Điều nào của Luật 36/2024/QH15 quy định quy tắc giao thông đối với xe ưu tiên?", "36/2024/QH15 Điều 27"),
    ("GOLD-ART-05", "Quy định về phân hạng giấy phép lái xe A1, A, B, C1, C, D nằm ở Điều nào trong Luật TTATGTĐB 2024?", "36/2024/QH15 Điều 58"),
    ("GOLD-DIR-08", "Độ tuổi tối thiểu để được cấp Giấy phép lái xe hạng A1 theo Luật 36/2024/QH15 là bao nhiêu?", "36/2024/QH15 Điều 59"),
    ("GOLD-DIR-09", "Thời hạn của Giấy phép lái xe ô tô hạng B theo Luật Trật tự, an toàn giao thông đường bộ là bao nhiêu năm?", "36/2024/QH15 Điều 60"),
    ("GOLD-DIR-10", "Mỗi giấy phép lái xe có tổng cộng bao nhiêu điểm trừ trong một năm theo Luật TTATGTĐB?", "36/2024/QH15 Điều 62")
]

for cid, q, expected in test_cases:
    q_lower = q.lower()
    
    # 1. Detect target document if user query explicitly refers to it
    target_doc_id = None
    target_doc_off = None
    for pattern, did, off in DOC_HINTS:
        if pattern in q_lower:
            target_doc_id = did
            target_doc_off = off
            break
            
    # 2. Extract substantive query tokens
    q_clean = re.sub(r"[^\w\s]", " ", q_lower)
    raw_tokens = q_clean.split()
    tokens = [t for t in raw_tokens if t not in ["là", "gì", "bao", "nhiêu", "nào", "mấy", "ở", "đâu", "khi", "có", "được", "không", "thế", "như", "theo", "của", "trong", "vào", "ngày", "tại", "cho", "về", "thì", "phải", "những"] and len(t) > 1]
    
    # Query Supabase: if target doc is explicitly specified, filter to it; else filter to all traffic docs
    doc_filter = f"eq.{target_doc_id}" if target_doc_id and target_doc_id in traffic_docs else f"in.({','.join(traffic_ids_list)})"
    
    search_phrase = " ".join(tokens[:4]) if tokens else "giao thông"
    params = {
        "document_id": doc_filter,
        "full_text": f"wfts.{search_phrase}",
        "select": "document_id,article_number,article_title,full_text",
        "limit": "20"
    }
    r = requests.get(f"{url}/rest/v1/legal_articles", headers=headers, params=params, timeout=5)
    hits = r.json() if r.status_code == 200 else []
    
    # Fallback to fewer tokens if empty
    if not hits and len(tokens) > 2:
        params["full_text"] = f"wfts.{' '.join(tokens[:2])}"
        r = requests.get(f"{url}/rest/v1/legal_articles", headers=headers, params=params, timeout=5)
        hits = r.json() if r.status_code == 200 else []
        
    # Re-rank hits using score_candidate
    scored_hits = []
    for h in hits:
        sc = score_candidate(q_lower, tokens, h, target_doc_id)
        scored_hits.append((sc, h))
    scored_hits.sort(key=lambda x: x[0], reverse=True)
    
    print(f"\n[{cid}] Expected: {expected}")
    print(f"  Doc hint: {target_doc_off or 'None'} | Terms: '{search_phrase}' | Candidates: {len(hits)}")
    for r_idx, (sc, h) in enumerate(scored_hits[:3], 1):
        doc_off = traffic_docs.get(h["document_id"], {}).get("official_number", h["document_id"])
        print(f"    Rank {r_idx} (Score {sc:.1f}): {doc_off} Điều {h.get('article_number')}: {h.get('article_title')[:35]}")
