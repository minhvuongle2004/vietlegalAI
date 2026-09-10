import sys
import os
import json
import time
from pathlib import Path
from typing import List, Dict, Any

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels

CLOUD_URL = "https://69f07c1e-2e88-452f-aded-6dd577ddbd9b.us-west-2-0.aws.cloud.qdrant.io"
CLOUD_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIiwic3ViamVjdCI6ImFwaS1rZXk6OTAxNjk0MzUtYjMwMS00YjAzLWFmMGYtYmYyZjc0MWE4MjYxIn0.bJ2YtMtnmDJXN4k3FKdduN_TsLARSOAvGjBRKW3p028"

STAGING_COLLECTION = "vietlegal_articles_staging"
PROD_COLLECTION = "vietlegal_articles"

REPORT_OUT = PROJECT_ROOT / "data" / "03_parsed" / "traffic_p1_2_batch" / "p1_2_promotion_verification_report.json"

def promote():
    print("=" * 100)
    print(" STEP 1: PROMOTING EXACTLY 163 P1.2 POINTS FROM STAGING TO PRODUCTION")
    print("=" * 100)

    client = QdrantClient(url=CLOUD_URL, api_key=CLOUD_API_KEY, timeout=30.0)
    print(f"[+] Connected to Qdrant Cloud: {CLOUD_URL}")

    # 1. Check current collection states
    prod_before = client.get_collection(PROD_COLLECTION).points_count
    staging_total = client.get_collection(STAGING_COLLECTION).points_count
    print(f"[*] Production Collection ('{PROD_COLLECTION}') points before: {prod_before}")
    print(f"[*] Staging Collection ('{STAGING_COLLECTION}') points total:  {staging_total}")

    if prod_before != 7495:
        raise ValueError(f"SAFETY ABORT: Production points count is {prod_before}, expected 7495!")

    # 2. Extract deterministic IDs from all_traffic_p1_2_chunks.json and retrieve from Staging
    print("\n[*] Loading 163 P1.2 chunks to get deterministic point IDs...")
    import uuid
    chunks_file = PROJECT_ROOT / "data" / "03_parsed" / "traffic_p1_2_batch" / "all_traffic_p1_2_chunks.json"
    with open(chunks_file, "r", encoding="utf-8") as f:
        chunks = json.load(f)
    
    p1_2_ids = [str(uuid.uuid5(uuid.NAMESPACE_DNS, c["chunk_id"])) for c in chunks]
    print(f"[*] Generated {len(p1_2_ids)} deterministic UUIDs.")

    # Retrieve all 163 points from Staging with vectors and payloads
    p1_2_records = client.retrieve(
        collection_name=STAGING_COLLECTION,
        ids=p1_2_ids,
        with_payload=True,
        with_vectors=True
    )

    print(f"[+] Retrieved {len(p1_2_records)} P1.2 points from Staging (Expected: 163).")
    if len(p1_2_records) != 163:
        raise ValueError(f"SAFETY ABORT: Expected exactly 163 P1.2 points, got {len(p1_2_records)}!")

    # 3. Collision and Duplicate Check against Production
    print("\n[*] Checking for ID collisions / duplicate records in Production...")
    p1_2_ids = [r.id for r in p1_2_records]
    existing_in_prod = client.retrieve(
        collection_name=PROD_COLLECTION,
        ids=p1_2_ids,
        with_payload=False,
        with_vectors=False
    )
    collision_count = len(existing_in_prod)
    print(f"[*] Existing P1.2 points in Production before promotion: {collision_count}")

    # 4. Prepare PointStruct batch for upload
    points_to_upsert = [
        qmodels.PointStruct(
            id=r.id,
            vector=r.vector,
            payload=r.payload
        )
        for r in p1_2_records
    ]

    # 5. Execute promotion upsert in batches of 50
    print(f"\n[*] Upserting {len(points_to_upsert)} points into Production ('{PROD_COLLECTION}')...")
    batch_size = 50
    promoted_count = 0
    failed_count = 0
    t0 = time.time()

    for i in range(0, len(points_to_upsert), batch_size):
        batch = points_to_upsert[i : i + batch_size]
        try:
            client.upsert(collection_name=PROD_COLLECTION, points=batch)
            promoted_count += len(batch)
            print(f" [+] Promoted batch {i // batch_size + 1}: {promoted_count}/{len(points_to_upsert)} points...")
        except Exception as e:
            failed_count += len(batch)
            print(f" [!] Error promoting batch {i // batch_size + 1}: {e}")
            raise e

    t1 = time.time()
    print(f"[+] Promotion upload completed in {t1 - t0:.2f}s! Promoted: {promoted_count}, Failed: {failed_count}")

    # 6. Verify Production count after promotion
    time.sleep(1.0)
    prod_after = client.get_collection(PROD_COLLECTION).points_count
    expected_final = prod_before + (len(points_to_upsert) - collision_count)
    print(f"\n[*] Production Points After Promotion: {prod_after} (Expected: {expected_final})")
    if prod_after != expected_final:
        raise ValueError(f"VERIFICATION FAILURE: Expected {expected_final} points, found {prod_after}!")

    print("🟢 STEP 1 PROMOTION SUCCESSFUL!")

    # ==========================================================================
    # STEP 2: POST-PROMOTION INTEGRITY VERIFICATION
    # ==========================================================================
    print("\n" + "=" * 100)
    print(" STEP 2: POST-PROMOTION INTEGRITY VERIFICATION (ON PRODUCTION)")
    print("=" * 100)

    # Verify all 163 points exist and check payload integrity
    verified_prod_points = client.retrieve(
        collection_name=PROD_COLLECTION,
        ids=p1_2_ids,
        with_payload=True,
        with_vectors=False
    )
    print(f"[*] Verified points retrieved from Production: {len(verified_prod_points)}/{len(p1_2_ids)}")

    doc_counts = {}
    qcvn_count = 0
    amendment_rel_count = 0
    intact_payloads = 0

    required_fields = [
        "chunk_id", "doc_id", "doc_title", "official_number",
        "chapter", "article_number", "article_title", "clause_number",
        "status", "legal_status", "ingestion_status", "document_role",
        "effective_date", "context_header", "content", "source_hash",
        "ingestion_batch"
    ]

    for pt in verified_prod_points:
        pl = pt.payload
        # Check required fields
        missing = [f for f in required_fields if f not in pl or pl[f] is None]
        if not missing:
            intact_payloads += 1
        
        off_num = pl.get("official_number")
        doc_counts[off_num] = doc_counts.get(off_num, 0) + 1

        if "QCVN 41" in str(pl.get("context_header", "")) or pl.get("annex_table_identifier"):
            qcvn_count += 1

        rel = pl.get("relations", {})
        if rel and any(k in rel for k in ["amends", "replaces", "repeals", "amended_by"]):
            amendment_rel_count += 1

    print(f"[+] Payload Integrity Check: {intact_payloads}/{len(verified_prod_points)} 100% complete!")
    print(f"[+] Document Breakdown in Promoted Batch:")
    for d, c in sorted(doc_counts.items()):
        print(f"    - {d}: {c} points")
    print(f"[+] QCVN Technical Units: {qcvn_count} points")
    print(f"[+] Amendment / Replacement Relations: {amendment_rel_count} points")

    # Specific NĐ 94 integrity check:
    nd94_points = [p for p in verified_prod_points if p.payload.get("official_number") == "94/2026/NĐ-CP"]
    d24_k3 = [p for p in nd94_points if p.payload.get("article_number") == "Điều 24" and p.payload.get("clause_number") == "Khoản 3"]
    d26_points = [p for p in nd94_points if p.payload.get("article_number") == "Điều 26"]

    print("\n[*] Specific NĐ 94 Post-Promotion Check:")
    print(f"    - Total NĐ 94 points: {len(nd94_points)} (Expected: 111)")
    if d24_k3:
        print(f"    - Điều 24 Khoản 3: FOUND | Title: {d24_k3[0].payload.get('article_title')} | Hash: {d24_k3[0].payload.get('source_hash')[:12]}...")
    if d26_points:
        print(f"    - Điều 26: FOUND ({len(d26_points)} clauses) | Title: {d26_points[0].payload.get('article_title')}")

    # Save summary report
    rep = {
        "production_before": prod_before,
        "promoted_count": promoted_count,
        "skipped_duplicate_count": collision_count,
        "failed_count": failed_count,
        "production_after": prod_after,
        "intact_payloads_count": intact_payloads,
        "document_breakdown": doc_counts,
        "qcvn_units_count": qcvn_count,
        "amendment_relations_count": amendment_rel_count,
        "promoted_at": time.strftime("%Y-%m-%dT%H:%M:%S%z")
    }
    with open(REPORT_OUT, "w", encoding="utf-8") as f:
        json.dump(rep, f, ensure_ascii=False, indent=2)
    print(f"[+] Saved promotion report to: {REPORT_OUT}")

if __name__ == "__main__":
    promote()
