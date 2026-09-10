import os
import sys
import requests
from dotenv import load_dotenv

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

load_dotenv()
supabase_url = os.getenv("SUPABASE_URL", "").rstrip("/")
supabase_key = os.getenv("SUPABASE_KEY", "")

headers = {
    "apikey": supabase_key,
    "Authorization": f"Bearer {supabase_key}",
    "Prefer": "count=exact"
}

print("=" * 80)
print("SUPABASE & VECTOR STORE AUDIT")
print("=" * 80)

# 1. legal_documents count & list
r_docs = requests.get(f"{supabase_url}/rest/v1/legal_documents?select=id,official_number,short_title,title", headers=headers)
doc_count_header = r_docs.headers.get("Content-Range", "Unknown")
docs = r_docs.json() if r_docs.status_code == 200 else []
print(f"\n[1] Bảng legal_documents: {len(docs)} văn bản (Content-Range: {doc_count_header})")
for idx, d in enumerate(docs, 1):
    doc_id = d.get("id")
    off_num = d.get("official_number") or ""
    title = d.get("short_title") or d.get("title") or ""
    print(f"  {idx:2d}. {doc_id:<42} | {off_num:<20} | {title}")

# 2. legal_articles count
r_arts = requests.get(f"{supabase_url}/rest/v1/legal_articles?select=count", headers=headers)
art_count_header = r_arts.headers.get("Content-Range", "Unknown")
total_articles = 0
if "/" in art_count_header:
    total_articles = int(art_count_header.split("/")[-1])
print(f"\n[2] Bảng legal_articles: {total_articles} điều luật (Content-Range: {art_count_header})")

from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# 3. Check unique documents in legal_articles
all_doc_ids = set()
offset = 0
limit = 1000
fetch_headers = {
    "apikey": supabase_key,
    "Authorization": f"Bearer {supabase_key}"
}
while True:
    r = requests.get(f"{supabase_url}/rest/v1/legal_articles?select=document_id&offset={offset}&limit={limit}", headers=fetch_headers)
    if r.status_code != 200:
        break
    data = r.json()
    if not data:
        break
    for item in data:
        if item.get("document_id"):
            all_doc_ids.add(item["document_id"])
    offset += limit
    if len(data) < limit:
        break
print(f"    Số document_id độc nhất xuất hiện trong legal_articles: {len(all_doc_ids)}")

# 4. Check Qdrant points (Chunks)
from backend.app.services.rag.vector_store import QdrantVectorStore
vs = QdrantVectorStore()
info = vs.client.get_collection(vs.collection_name)
total_chunks = info.points_count
print(f"\n[3] Qdrant Collection '{vs.collection_name}': {total_chunks} vectors/chunks")

print("\n" + "=" * 80)
print(f"TỔNG KẾT THỰC TẾ:")
print(f"- Số văn bản (legal_documents): {len(docs)} văn bản trong legal_documents ({len(all_doc_ids)} văn bản có điều luật)")
print(f"- Số điều luật (legal_articles): {total_articles} điều luật")
print(f"- Số vector chunks (Qdrant): {total_chunks} chunks")
print("=" * 80)
