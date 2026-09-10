import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
import os
import json
import time
from pathlib import Path
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
load_dotenv(PROJECT_ROOT / ".env")

from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels

CLOUD_URL = os.getenv("QDRANT_URL")
CLOUD_API_KEY = os.getenv("QDRANT_API_KEY")

STAGING_COLLECTION = "vietlegal_articles_staging"
PROD_COLLECTION = "vietlegal_articles"
CHUNKS_FILE = PROJECT_ROOT / "data" / "03_parsed" / "traffic_p2_batch" / "traffic_p2_chunks.json"

def promote_to_production():
    print("=" * 80)
    print("   PROMOTING TRAFFIC P2 VECTORS TO PRODUCTION (vietlegal_articles)")
    print("=" * 80)

    client = QdrantClient(url=CLOUD_URL, api_key=CLOUD_API_KEY, timeout=30.0)

    # 1. Verify before counts
    prod_before = client.get_collection(PROD_COLLECTION).points_count
    staging_count = client.get_collection(STAGING_COLLECTION).points_count
    print(f"[*] Production points BEFORE promotion: {prod_before} (Expected: 7658)")
    print(f"[*] Staging points count:               {staging_count} (Expected: 7800)")

    assert prod_before == 7658, f"CRITICAL: Production count mismatch! Expected 7658, found {prod_before}"
    assert staging_count == 7800, f"CRITICAL: Staging count mismatch! Expected 7800, found {staging_count}"

    # 2. Retrieve the 142 P2 points from Staging with vectors and payloads
    with open(CHUNKS_FILE, "r", encoding="utf-8") as f:
        chunks = json.load(f)
    p2_ids = [c["chunk_id"] for c in chunks]
    print(f"[*] Retrieving {len(p2_ids)} P2 points with vectors from staging...")

    p2_points = []
    for i in range(0, len(p2_ids), 100):
        batch_ids = p2_ids[i:i+100]
        pts = client.retrieve(
            collection_name=STAGING_COLLECTION,
            ids=batch_ids,
            with_payload=True,
            with_vectors=True
        )
        p2_points.extend(pts)

    print(f"[+] Retrieved {len(p2_points)} points to promote.")
    assert len(p2_points) == 142, f"Expected 142 points, got {len(p2_points)}"

    # 3. Collision check in Production
    existing_in_prod = client.retrieve(
        collection_name=PROD_COLLECTION,
        ids=p2_ids
    )
    print(f"[*] ID collision check in production: {len(existing_in_prod)} collisions (Expected: 0)")
    assert len(existing_in_prod) == 0, f"Collision detected: {len(existing_in_prod)} points already exist in production!"

    # 4. Upsert into production in batches of 50
    points_to_upsert = [
        qmodels.PointStruct(
            id=p.id,
            vector=p.vector,
            payload=p.payload
        )
        for p in p2_points
    ]

    print(f"[*] Promoting {len(points_to_upsert)} points to production '{PROD_COLLECTION}'...")
    batch_size = 50
    for i in range(0, len(points_to_upsert), batch_size):
        batch = points_to_upsert[i : i + batch_size]
        client.upsert(
            collection_name=PROD_COLLECTION,
            points=batch
        )
        print(f"    [+] Upserted batch {i//batch_size + 1} ({len(batch)} points)")

    time.sleep(2)
    prod_after = client.get_collection(PROD_COLLECTION).points_count
    print("\n" + "=" * 80)
    print(f"[*] Production points AFTER promotion: {prod_after} (+{prod_after - prod_before})")
    print(f"[*] Expected points: 7800 | Actual: {prod_after}")
    print("=" * 80)

    assert prod_after == 7800, f"CRITICAL: Final production points count mismatch! Expected 7800, got {prod_after}"

    report = {
        "production_collection": PROD_COLLECTION,
        "production_before": prod_before,
        "production_after": prod_after,
        "promoted_points": len(points_to_upsert),
        "status": "PASS"
    }

    report_path = PROJECT_ROOT / "data" / "03_parsed" / "traffic_p2_batch" / "production_promotion_report.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(f"[+] Saved promotion report to {report_path}")
    return report

if __name__ == "__main__":
    promote_to_production()
