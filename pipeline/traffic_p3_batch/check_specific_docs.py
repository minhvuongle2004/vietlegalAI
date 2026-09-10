import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
import os
import requests
from pathlib import Path
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
load_dotenv(PROJECT_ROOT / ".env")

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
h = {"apikey": key, "Authorization": f"Bearer {key}", "Prefer": "count=exact"}

docs_to_check = [
    "35/2024/QH15",
    "36/2024/QH15",
    "168/2024/NĐ-CP",
    "158/2024/NĐ-CP",
    "79/2024/TT-BCA",
    "12/2025/TT-BCA",
    "105/2026/TT-BCA",
    "108/2026/TT-BCA",
    "38/2024/TT-BGTVT",
    "118/2025/QH15",
    "140/2025/NĐ-CP",
    "144/2025/NĐ-CP"
]

print("=== CHECKING KEY TRAFFIC DOCUMENTS IN SUPABASE ===")
for doc_num in docs_to_check:
    r_doc = requests.get(f"{url}/rest/v1/legal_documents?official_number=eq.{doc_num}", headers=h).json()
    if r_doc:
        d = r_doc[0]
        doc_id = d["id"]
        doc_title = d.get("title") or "N/A"
        r_art = requests.get(f"{url}/rest/v1/legal_articles?document_id=eq.{doc_id}&select=id", headers=h, params={"limit": 1})
        cnt_str = r_art.headers.get("Content-Range", "0/0")
        cnt_art = cnt_str.split("/")[-1] if "/" in cnt_str else len(r_art.json())
        print(f"  [FOUND] {doc_num:18} | ID: {doc_id:32} | Articles: {cnt_art:4} | Title: {doc_title[:50]}")
    else:
        print(f"  [MISSING IN SUPABASE] {doc_num:18}")
