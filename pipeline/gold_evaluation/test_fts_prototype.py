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

# Stopwords and question fillers in Vietnamese legal questions
STOPWORDS = {
    "là", "gì", "bao", "nhiêu", "nào", "mấy", "ở", "đâu", "khi", "nào",
    "có", "được", "không", "thế", "như", "theo", "quy", "định", "của",
    "trong", "vào", "ngày", "tại", "cho", "về", "thì", "phải", "những"
}

def extract_keywords(query: str):
    # Clean special characters
    q_clean = re.sub(r"[^\w\s]", " ", query.lower())
    tokens = q_clean.split()
    # Keep terms that are not common interrogative fillers
    meaningful = [t for t in tokens if t not in STOPWORDS and len(t) > 1]
    return meaningful

# Get all traffic document IDs from Supabase
r_docs = requests.get(f"{url}/rest/v1/legal_documents?select=id,official_number,title,effective_date,expiry_date", headers=headers)
docs = r_docs.json()
traffic_doc_map = {}
for d in docs:
    did = d["id"]
    off = d.get("official_number", "")
    title = d.get("title", "")
    if "traffic" in did or "road" in did or any(num in off for num in ["36/2024", "35/2024", "168/2024", "158/2024", "161/2024", "38/2024", "73/2024", "79/2024", "12/2025", "108/2026", "89/2026", "30/2026", "94/2026", "65/2024", "105/2026", "51/2024", "28/2024", "13/2025", "51/2025", "238/2026", "241/2026", "45/2026", "19/2026", "26/2026", "151/2024"]):
        traffic_doc_map[did] = {
            "id": did,
            "official_number": off,
            "title": title,
            "effective_date": d.get("effective_date"),
            "expiry_date": d.get("expiry_date")
        }

print(f"Total traffic documents mapped: {len(traffic_doc_map)}")

traffic_ids_filter = f"in.({','.join(traffic_doc_map.keys())})"

test_cases = [
    ("GOLD-DIR-01", "Người tham gia giao thông đường bộ phải đi bên nào theo quy định của Luật Trật tự an toàn giao thông đường bộ?"),
    ("GOLD-DIR-02", "Khi có người điều khiển giao thông thì người tham gia giao thông phải chấp hành hiệu lệnh của ai trước tiên?"),
    ("GOLD-DIR-03", "Người lái xe ô tô có được sử dụng điện thoại bằng tay khi xe đang chạy trên đường không?"),
    ("GOLD-DIR-04", "Tốc độ tối đa cho phép xe con chạy trong khu vực đông dân cư trên đường đôi là bao nhiêu km/h?"),
    ("GOLD-ART-01", "Điều nào trong Luật Trật tự, an toàn giao thông đường bộ 2024 quy định về việc chuyển hướng xe?"),
    ("GOLD-ART-02", "Quy định về việc vượt xe và nhường đường cho xe xin vượt nằm ở Điều mấy của Luật 36/2024/QH15?"),
    ("GOLD-ART-03", "Điều bao nhiêu của Luật Trật tự, an toàn giao thông đường bộ quy định về dừng xe, đỗ xe trên đường?"),
    ("GOLD-ART-04", "Điều nào của Luật 36/2024/QH15 quy định quy tắc giao thông đối với xe ưu tiên?"),
    ("GOLD-ART-05", "Quy định về phân hạng giấy phép lái xe A1, A, B, C1, C, D nằm ở Điều nào trong Luật TTATGTĐB 2024?"),
    ("GOLD-DIR-08", "Độ tuổi tối thiểu để được cấp Giấy phép lái xe hạng A1 theo Luật 36/2024/QH15 là bao nhiêu?"),
    ("GOLD-DIR-09", "Thời hạn của Giấy phép lái xe ô tô hạng B theo Luật Trật tự, an toàn giao thông đường bộ là bao nhiêu năm?"),
    ("GOLD-DIR-10", "Mỗi giấy phép lái xe có tổng cộng bao nhiêu điểm trừ trong một năm theo Luật TTATGTĐB?")
]

print("\n=== RUNNING TEST QUERIES WITH POSTGRESQL FTS ===")
for cid, q in test_cases:
    # 1. Try full phrase or key phrases
    # Extract core phrases
    keywords = extract_keywords(q)
    # If question mentions specific article or document
    art_nums = re.findall(r"(?:điều|khoản)\s*(\d+)", q.lower())
    
    # Try FTS query with key phrases
    search_terms = " ".join(keywords[:6])
    
    # Supabase PostgREST FTS query
    params = {
        "document_id": traffic_ids_filter,
        "full_text": f"wfts.{search_terms}",
        "select": "document_id,article_number,article_title",
        "limit": "3"
    }
    r = requests.get(f"{url}/rest/v1/legal_articles", headers=headers, params=params, timeout=5)
    hits = r.json() if r.status_code == 200 else []
    
    # If wfts with all 6 words is too restrictive, fallback to first 3-4 keywords
    if not hits and len(keywords) > 3:
        search_terms_fallback = " ".join(keywords[:3])
        params["full_text"] = f"wfts.{search_terms_fallback}"
        r = requests.get(f"{url}/rest/v1/legal_articles", headers=headers, params=params, timeout=5)
        hits = r.json() if r.status_code == 200 else []
        
    print(f"\n[{cid}] {q[:50]}...")
    print(f"  Terms: '{search_terms}' -> Hits: {len(hits)}")
    for h in hits:
        doc_off = traffic_doc_map.get(h["document_id"], {}).get("official_number", h["document_id"])
        print(f"    - {doc_off} Điều {h.get('article_number')}: {h.get('article_title')}")
