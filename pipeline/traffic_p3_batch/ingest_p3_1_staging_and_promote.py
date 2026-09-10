import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
import os
import json
import time
import requests
from pathlib import Path
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
load_dotenv(PROJECT_ROOT / ".env")

from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels
from backend.app.services.rag.embeddings import get_embedding_service

CHUNKS_FILE = PROJECT_ROOT / "data" / "03_parsed" / "traffic_p3_batch" / "p3_1_chunks.json"
CLOUD_URL = os.getenv("QDRANT_URL")
CLOUD_API_KEY = os.getenv("QDRANT_API_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

def is_active(payload, as_of_date):
    vf = payload.get("valid_from")
    vt = payload.get("valid_to")
    if not vf or vf > as_of_date:
        return False
    if vt and as_of_date >= vt:
        return False
    return True

def process_p3_1():
    print("=" * 80)
    print("   P3.1 INGESTION & PROMOTION: NĐ 168/2024 + NĐ 238/2026")
    print("=" * 80)

    client = QdrantClient(url=CLOUD_URL, api_key=CLOUD_API_KEY, timeout=30.0)

    with open(CHUNKS_FILE, "r", encoding="utf-8") as f:
        chunks = json.load(f)

    # 1. Compute Embeddings
    print(f"[*] Embedding {len(chunks)} chunks with BAAI/bge-m3...")
    embedder = get_embedding_service()
    texts = [c["full_search_text"] for c in chunks]
    vectors = embedder.embed_texts(texts)

    points = []
    for c, vec in zip(chunks, vectors):
        points.append(qmodels.PointStruct(
            id=c["chunk_id"],
            vector=vec,
            payload=c
        ))

    # 2. Ingest to Staging
    print(f"[*] Upserting {len(points)} points into 'vietlegal_articles_staging'...")
    client.upsert(collection_name="vietlegal_articles_staging", points=points)

    # 3. Temporal Tests
    print("\n--- P3.1 TEMPORAL TESTS ---")
    date_before = "2026-08-14"
    date_after = "2026-08-15"

    d5_v1 = next(p for p in points if p.payload["canonical_provision_id"] == "traffic_penalty_168_2024_nd_cp:article_5" and p.payload["version_id"] == "v1_original")
    d5_v2 = next(p for p in points if p.payload["canonical_provision_id"] == "traffic_penalty_168_2024_nd_cp:article_5" and p.payload["version_id"] == "v2_nd238")

    assert is_active(d5_v1.payload, date_before) is True
    assert is_active(d5_v1.payload, date_after) is False
    assert is_active(d5_v2.payload, date_before) is False
    assert is_active(d5_v2.payload, date_after) is True
    print(f"[+] Temporal Test Điều 5 (before {date_before} vs from {date_after}): PASS")

    d13_v1 = next(p for p in points if p.payload["canonical_provision_id"] == "traffic_penalty_168_2024_nd_cp:article_13" and p.payload["version_id"] == "v1_original")
    d13_v2 = next(p for p in points if p.payload["canonical_provision_id"] == "traffic_penalty_168_2024_nd_cp:article_13" and p.payload["version_id"] == "v2_nd238")
    assert is_active(d13_v1.payload, date_before) is True
    assert is_active(d13_v1.payload, date_after) is False
    assert is_active(d13_v2.payload, date_after) is True
    print(f"[+] Temporal Test Điều 13: PASS")

    # 4. Cross-database Parity Check
    print("\n--- P3.1 CROSS-DATABASE PARITY ---")
    sb_h = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}
    
    # Check document in Supabase
    r_doc168 = requests.get(f"{SUPABASE_URL}/rest/v1/legal_documents?id=eq.traffic_penalty_168_2024_nd_cp", headers=sb_h).json()
    r_doc238 = requests.get(f"{SUPABASE_URL}/rest/v1/legal_documents?id=eq.traffic_penalty_amendment_238_2026_nd_cp", headers=sb_h).json()
    assert len(r_doc168) == 1, "Doc 168 missing in Supabase"
    assert len(r_doc238) == 1, "Doc 238 missing in Supabase"
    print("[+] Supabase documents resolved: NĐ 168 & NĐ 238")

    # Check articles in Supabase
    r_arts = requests.get(f"{SUPABASE_URL}/rest/v1/legal_articles?document_id=eq.traffic_penalty_amendment_238_2026_nd_cp", headers=sb_h).json()
    assert len(r_arts) == 2, "Doc 238 articles missing in Supabase"
    print("[+] Supabase articles resolved: 2 articles for NĐ 238")

    # 5. Production Promotion
    print("\n--- P3.1 PRODUCTION PROMOTION ---")
    prod_before = client.get_collection("vietlegal_articles").points_count
    print(f"[*] Production points BEFORE promotion: {prod_before} (Expected: 7800)")
    assert prod_before == 7800, f"Expected 7800 in production, found {prod_before}"

    # Upsert points to production
    client.upsert(collection_name="vietlegal_articles", points=points)
    time.sleep(2)
    prod_after = client.get_collection("vietlegal_articles").points_count
    print(f"[*] Production points AFTER promotion:  {prod_after} (+{prod_after - prod_before})")
    assert prod_after == 7808, f"Expected 7808 in production, found {prod_after}"
    print("[+] P3.1 COMPLETED AND PROMOTED SUCCESSFULLY!")

if __name__ == "__main__":
    process_p3_1()
