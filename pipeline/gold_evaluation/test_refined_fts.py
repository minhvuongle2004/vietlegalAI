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

# Meta-words indicating document names or legal structural references,
# NOT the substantive topic being queried
DOC_META_WORDS = {
    "luật", "nghị", "định", "thông", "tư", "điều", "khoản", "điểm", "chương", "mục",
    "quy", "định", "pháp", "luật", "văn", "bản", "số", "năm",
    "2024", "2025", "2026", "qh14", "qh15", "bca", "bgtvt", "bxd", "cp",
    "trật", "tự", "toàn", "giao", "thông", "đường", "bộ"
}

QUESTION_FILLERS = {
    "là", "gì", "bao", "nhiêu", "nào", "mấy", "ở", "đâu", "khi",
    "có", "được", "không", "thế", "như", "theo", "của",
    "trong", "vào", "ngày", "tại", "cho", "về", "thì", "phải", "những",
    "hỏi", "biết", "cho", "em", "mình", "ai", "trước", "tiên"
}

ALL_STOPWORDS = DOC_META_WORDS | QUESTION_FILLERS

def extract_substantive_topic(query: str):
    q_clean = re.sub(r"[^\w\s]", " ", query.lower())
    tokens = q_clean.split()
    
    # Substantive topic: without meta words and fillers
    topic_tokens = [t for t in tokens if t not in ALL_STOPWORDS and len(t) > 1]
    
    # Also keep general legal keywords (with some meta words if query is very short)
    general_tokens = [t for t in tokens if t not in QUESTION_FILLERS and len(t) > 1]
    
    return " ".join(topic_tokens), " ".join(general_tokens)

# Traffic docs mapping (strictly exclude BHYT)
r_docs = requests.get(f"{url}/rest/v1/legal_documents?select=id,official_number,title,effective_date,expiry_date", headers=headers)
traffic_docs = {}
for d in r_docs.json():
    did = d["id"]
    if did == "bhyt_51_2024_qh15":
        continue
    if "traffic" in did or "road" in did:
        traffic_docs[did] = d

traffic_ids_list = list(traffic_docs.keys())
print(f"Verified Pure Traffic Documents in Supabase: {len(traffic_ids_list)}")

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

print("\n=== RUNNING REFINED POSTGRESQL FTS ON SAMPLE CASES ===")
for cid, q, expected in test_cases:
    topic_query, gen_query = extract_substantive_topic(q)
    
    # We query Supabase with substantive topic first, fallback to gen_query
    q_search = topic_query if len(topic_query.split()) >= 2 else gen_query
    # Take first 4 tokens to avoid over-constraining tsquery
    tokens = q_search.split()[:4]
    search_phrase = " ".join(tokens)
    
    params = {
        "document_id": f"in.({','.join(traffic_ids_list)})",
        "full_text": f"wfts.{search_phrase}",
        "select": "document_id,article_number,article_title",
        "limit": "5"
    }
    r = requests.get(f"{url}/rest/v1/legal_articles", headers=headers, params=params, timeout=5)
    hits = r.json() if r.status_code == 200 else []
    
    # If no hits, fallback to top 2 tokens
    if not hits and len(tokens) > 2:
        search_phrase_fallback = " ".join(tokens[:2])
        params["full_text"] = f"wfts.{search_phrase_fallback}"
        r = requests.get(f"{url}/rest/v1/legal_articles", headers=headers, params=params, timeout=5)
        hits = r.json() if r.status_code == 200 else []
        
    print(f"\n[{cid}] Expected: {expected}")
    print(f"  Topic Search: '{search_phrase}' -> Returned: {len(hits)}")
    for r_idx, h in enumerate(hits[:3], 1):
        doc_off = traffic_docs.get(h["document_id"], {}).get("official_number", h["document_id"])
        print(f"    Rank {r_idx}: {doc_off} Điều {h.get('article_number')}: {h.get('article_title')[:35]}")
