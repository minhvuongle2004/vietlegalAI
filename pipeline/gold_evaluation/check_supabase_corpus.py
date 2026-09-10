import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
import os
import requests
from dotenv import load_dotenv

load_dotenv()
url = os.getenv("SUPABASE_URL", "").rstrip("/")
key = os.getenv("SUPABASE_KEY", "")
headers = {"apikey": key, "Authorization": f"Bearer {key}"}

r = requests.get(f"{url}/rest/v1/legal_documents?select=id,official_number,title,effective_date,expiry_date", headers=headers)
docs = r.json()
print(f"Total documents in Supabase: {len(docs)}\n")
for d in sorted(docs, key=lambda x: x["id"]):
    print(f"{d['id']:45s} | {str(d.get('official_number')):18s} | eff: {str(d.get('effective_date'))} | exp: {str(d.get('expiry_date'))}")
