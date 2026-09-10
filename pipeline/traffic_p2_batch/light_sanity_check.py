import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
import os
import json
import requests
from pathlib import Path
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
load_dotenv(PROJECT_ROOT / ".env")

from qdrant_client import QdrantClient

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_KEY = os.getenv("QDRANT_API_KEY")

client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_KEY)
sb_h = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}

targets = [
    ("traffic_road_law_detail_165_2024_nd_cp:article_21", "v2_nd241", 21),
    ("traffic_road_law_detail_165_2024_nd_cp:article_52a", "v2_nd241", 52),
    ("traffic_road_law_detail_165_2024_nd_cp:article_17:clause_1:point_d", "v1_original", 17)
]

CHUNKS_FILE = PROJECT_ROOT / "data" / "03_parsed" / "traffic_p2_batch" / "traffic_p2_chunks.json"
with open(CHUNKS_FILE, "r", encoding="utf-8") as f:
    chunks = json.load(f)

chunk_map = {(c["canonical_provision_id"], c["version_id"]): c for c in chunks}

print("=" * 80)
print("   POST-P2 LIGHT SANITY CHECK (3 TARGET HYDRATIONS)")
print("=" * 80)

for canon, ver, sb_art_num in targets:
    c = chunk_map.get((canon, ver))
    assert c, f"Missing chunk for {canon} {ver}"
    pt_id = c["chunk_id"]

    # 1. Fetch Qdrant point from Production collection
    pts = client.retrieve(collection_name="vietlegal_articles", ids=[pt_id], with_payload=True)
    assert len(pts) == 1, f"Point {pt_id} not found in production"
    p = pts[0]
    payload = p.payload

    # 2. Fetch Supabase article record
    r = requests.get(
        f"{SUPABASE_URL}/rest/v1/legal_articles?document_id=eq.traffic_road_law_detail_165_2024_nd_cp&article_number=eq.{sb_art_num}",
        headers=sb_h
    )
    sb_records = r.json()
    assert len(sb_records) == 1, f"Supabase article {sb_art_num} not found"
    sb_art = sb_records[0]

    u_type = payload.get("unit_type")
    l_status = payload.get("legal_status")
    v_int = payload.get("valid_interval")
    ctx = payload.get("context_header")
    cnt = payload.get("content", "").replace("\n", " ")[:110]

    print(f"\n[*] Target: {canon} [{ver}]")
    print(f"    - Qdrant Point ID:   {p.id}")
    print(f"    - Unit Type:         {u_type}")
    print(f"    - Legal Status:      {l_status}")
    print(f"    - Valid Interval:    {v_int}")
    print(f"    - Citation Header:   {ctx}")
    print(f"    - Supabase Record:   ID {sb_art['id']} | Điều {sb_art['article_number']}: {sb_art['article_title'][:40]}...")
    print(f"    - Text Snippet:      {cnt}...")
    print("    -> HYDRATION STATUS:  PASS")

print("\n" + "=" * 80)
print("   ALL 3 HYDRATION CHECKS = PASS (STOP AUDIT CONFIRMED)")
print("=" * 80)
