import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
import os
import json
from pathlib import Path
from dotenv import load_dotenv
import requests

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
load_dotenv(PROJECT_ROOT / ".env")

supabase_url = os.getenv("SUPABASE_URL", "").rstrip("/")
supabase_key = os.getenv("SUPABASE_KEY", "")

headers = {
    "apikey": supabase_key,
    "Authorization": f"Bearer {supabase_key}"
}

print("=== 1. CHECK SUPABASE TABLES & COLUMNS ===")
# Check legal_articles schema/columns
r = requests.get(f"{supabase_url}/rest/v1/?apikey={supabase_key}")
print("API Spec status:", r.status_code)

# Check 5 rows of legal_documents
r_docs = requests.get(f"{supabase_url}/rest/v1/legal_documents?select=*&limit=5", headers=headers)
print("Docs status:", r_docs.status_code)
if r_docs.status_code == 200:
    docs = r_docs.json()
    if docs:
        print("Sample doc keys:", list(docs[0].keys()))
        for d in docs:
            print("Doc ID:", d.get("id"), "| Official number:", d.get("official_number"), "| Title:", d.get("title", "")[:40])

# Check 5 rows of legal_articles
r_arts = requests.get(f"{supabase_url}/rest/v1/legal_articles?select=*&limit=5", headers=headers)
print("Articles status:", r_arts.status_code)
if r_arts.status_code == 200:
    arts = r_arts.json()
    if arts:
        print("Sample article keys:", list(arts[0].keys()))
        for a in arts:
            print("Article ID:", a.get("id"), "| Document ID:", a.get("document_id"), "| Article #:", a.get("article_number"), "| Title:", a.get("article_title", "")[:40])

# Check total traffic documents in Supabase
r_traffic_docs = requests.get(f"{supabase_url}/rest/v1/legal_documents?select=id,official_number,title", headers=headers)
if r_traffic_docs.status_code == 200:
    all_docs = r_traffic_docs.json()
    print(f"\nTotal documents in Supabase legal_documents: {len(all_docs)}")
    traffic_docs = [d for d in all_docs if any(k in str(d).lower() for k in ["giao thông", "đường bộ", "36/2024", "168/2024", "38/2024", "73/2024", "79/2024", "traffic"])]
    print(f"Traffic documents found in Supabase: {len(traffic_docs)}")
    for td in traffic_docs[:15]:
        print("  -", td.get("id"), "-->", td.get("official_number"), "-->", td.get("title", "")[:50])
