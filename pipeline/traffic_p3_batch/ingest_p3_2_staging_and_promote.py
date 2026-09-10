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

CHUNKS_FILE = PROJECT_ROOT / "data" / "03_parsed" / "traffic_p3_batch" / "p3_2_chunks.json"
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

def process_p3_2():
    print("=" * 80)
    print("   P3.2 INGESTION & PROMOTION: NĐ 158/2024 + NĐ 218/2026")
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
    print("\n--- P3.2 TEMPORAL TESTS ---")
    date_before = "2026-08-09"
    date_after = "2026-08-10"

    d7_v1 = next(p for p in points if p.payload["canonical_provision_id"] == "traffic_transport_158_2024_nd_cp:article_7" and p.payload["version_id"] == "v1_original")
    d7_v2 = next(p for p in points if p.payload["canonical_provision_id"] == "traffic_transport_158_2024_nd_cp:article_7" and p.payload["version_id"] == "v2_amended")

    assert is_active(d7_v1.payload, date_before) is True, "Điều 7 v1 should be active before 2026-08-10"
    assert is_active(d7_v1.payload, date_after) is False, "Điều 7 v1 should be inactive from 2026-08-10"
    assert is_active(d7_v2.payload, date_before) is False, "Điều 7 v2 should be inactive before 2026-08-10"
    assert is_active(d7_v2.payload, date_after) is True, "Điều 7 v2 should be active from 2026-08-10"
    print(f"[+] Temporal Test Điều 7 (before {date_before} vs from {date_after}): PASS")

    d19_v1 = next(p for p in points if p.payload["canonical_provision_id"] == "traffic_transport_158_2024_nd_cp:article_19" and p.payload["version_id"] == "v1_original")
    d19_v2 = next(p for p in points if p.payload["canonical_provision_id"] == "traffic_transport_158_2024_nd_cp:article_19" and p.payload["version_id"] == "v2_amended")

    assert is_active(d19_v1.payload, date_before) is True, "Điều 19 v1 should be active before 2026-08-10"
    assert is_active(d19_v1.payload, date_after) is False, "Điều 19 v1 should be inactive from 2026-08-10"
    assert is_active(d19_v2.payload, date_before) is False, "Điều 19 v2 should be inactive before 2026-08-10"
    assert is_active(d19_v2.payload, date_after) is True, "Điều 19 v2 should be active from 2026-08-10"
    print(f"[+] Temporal Test Điều 19 (before {date_before} vs from {date_after}): PASS")

    c218_1 = next(p for p in points if p.payload["canonical_provision_id"] == "traffic_amendment_218_2026_nd_cp:article_1")
    assert is_active(c218_1.payload, date_before) is False, "NĐ 218 Điều 1 should be inactive before 2026-08-10"
    assert is_active(c218_1.payload, date_after) is True, "NĐ 218 Điều 1 should be active from 2026-08-10"
    print(f"[+] Temporal Test NĐ 218 Điều 1: PASS")

    # 4. Cross-database Parity Check
    print("\n--- P3.2 CROSS-DATABASE PARITY ---")
    sb_h = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}
    
    # Check documents in Supabase
    r_doc158 = requests.get(f"{SUPABASE_URL}/rest/v1/legal_documents?id=eq.traffic_transport_158_2024_nd_cp", headers=sb_h).json()
    r_doc218 = requests.get(f"{SUPABASE_URL}/rest/v1/legal_documents?id=eq.traffic_amendment_218_2026_nd_cp", headers=sb_h).json()
    assert len(r_doc158) == 1, "Doc 158 missing in Supabase"
    assert len(r_doc218) == 1, "Doc 218 missing in Supabase"
    print("[+] Supabase documents resolved: NĐ 158 & NĐ 218")

    # Check articles in Supabase
    r_arts158 = requests.get(f"{SUPABASE_URL}/rest/v1/legal_articles?document_id=eq.traffic_transport_158_2024_nd_cp", headers=sb_h).json()
    r_arts218 = requests.get(f"{SUPABASE_URL}/rest/v1/legal_articles?document_id=eq.traffic_amendment_218_2026_nd_cp", headers=sb_h).json()
    assert len(r_arts158) == 8, f"Expected 8 articles for NĐ 158, found {len(r_arts158)}"
    assert len(r_arts218) == 2, f"Expected 2 articles for NĐ 218, found {len(r_arts218)}"
    print(f"[+] Supabase articles resolved: {len(r_arts158)} for NĐ 158, {len(r_arts218)} for NĐ 218")

    # 5. Production Promotion
    print("\n--- P3.2 PRODUCTION PROMOTION ---")
    prod_before = client.get_collection("vietlegal_articles").points_count
    print(f"[*] Production points BEFORE promotion: {prod_before} (Expected: 7808)")
    assert prod_before == 7808, f"Expected 7808 in production, found {prod_before}"

    # Upsert points to production
    client.upsert(collection_name="vietlegal_articles", points=points)
    time.sleep(2)
    prod_after = client.get_collection("vietlegal_articles").points_count
    print(f"[*] Production points AFTER promotion:  {prod_after} (+{prod_after - prod_before})")
    assert prod_after == 7820, f"Expected 7820 in production, found {prod_after}"
    print("[+] P3.2 COMPLETED AND PROMOTED SUCCESSFULLY!")

if __name__ == "__main__":
    process_p3_2()
