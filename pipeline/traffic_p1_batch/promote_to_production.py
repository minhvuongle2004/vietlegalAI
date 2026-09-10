import sys
import os
import json
import time
from pathlib import Path
from typing import List, Dict, Any

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels
from backend.app.services.rag.embeddings import get_embedding_service

CLOUD_URL = "https://69f07c1e-2e88-452f-aded-6dd577ddbd9b.us-west-2-0.aws.cloud.qdrant.io"
CLOUD_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIiwic3ViamVjdCI6ImFwaS1rZXk6OTAxNjk0MzUtYjMwMS00YjAzLWFmMGYtYmYyZjc0MWE4MjYxIn0.bJ2YtMtnmDJXN4k3FKdduN_TsLARSOAvGjBRKW3p028"

STAGING_COLLECTION = "vietlegal_articles_staging"
PROD_COLLECTION = "vietlegal_articles"

BENCHMARK_25_FILE = PROJECT_ROOT / "data" / "03_parsed" / "traffic_p0_5_batch" / "benchmark_25_cases.json"
RESULTS_DIR = PROJECT_ROOT / "data" / "03_parsed" / "traffic_p1_batch"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

def main():
    print("=" * 80)
    print("   VIETLEGAL AI: STEP 4 - CONTROLLED PRODUCTION PROMOTION")
    print("=" * 80)

    client = QdrantClient(url=CLOUD_URL, api_key=CLOUD_API_KEY, timeout=30.0)

    # 1. Pre-promotion Verification
    print("\n--- GIAI ĐOẠN 1: PRE-PROMOTION VERIFICATION ---")
    prod_info_before = client.get_collection(PROD_COLLECTION)
    before_count = prod_info_before.points_count
    print(f"[*] Production Collection ('{PROD_COLLECTION}') before promotion: {before_count} points")
    if before_count != 7170:
        raise ValueError(f"CRITICAL: Baseline mismatch! Expected 7170, found {before_count}")

    staging_info = client.get_collection(STAGING_COLLECTION)
    staging_count = staging_info.points_count
    print(f"[*] Staging Collection ('{STAGING_COLLECTION}'): {staging_count} points")
    if staging_count != 325:
        raise ValueError(f"CRITICAL: Staging count mismatch! Expected 325, found {staging_count}")

    # Scroll all points from Staging (including vectors and payloads)
    print("[*] Retrieving all 325 points from Staging collection...")
    staging_points, _ = client.scroll(
        collection_name=STAGING_COLLECTION,
        limit=500,
        with_payload=True,
        with_vectors=True
    )
    print(f"[+] Retrieved {len(staging_points)} points from Staging.")

    # Collision Check
    staging_ids = [p.id for p in staging_points]
    print(f"[*] Checking for ID collisions in production collection...")
    existing_in_prod = client.retrieve(
        collection_name=PROD_COLLECTION,
        ids=staging_ids
    )
    collision_count = len(existing_in_prod)
    print(f"[+] ID Collision Check: {collision_count} collisions detected (Expected: 0)")
    if collision_count > 0:
        raise ValueError(f"CRITICAL: {collision_count} ID collisions detected between staging and production!")

    # 2. Execute Promotion (Upsert in Batches)
    print("\n--- GIAI ĐOẠN 2: EXECUTING PRODUCTION PROMOTION ---")
    batch_size = 50
    promoted_count = 0
    failed_count = 0
    skipped_count = 0

    points_to_upsert = [
        qmodels.PointStruct(
            id=p.id,
            vector=p.vector,
            payload=p.payload
        )
        for p in staging_points
    ]

    t0 = time.time()
    for i in range(0, len(points_to_upsert), batch_size):
        batch = points_to_upsert[i : i + batch_size]
        try:
            client.upsert(
                collection_name=PROD_COLLECTION,
                points=batch
            )
            promoted_count += len(batch)
            print(f" [+] Promoted {promoted_count}/{len(points_to_upsert)} points to production...")
        except Exception as e:
            print(f" [!] Error upserting batch {i}: {e}")
            failed_count += len(batch)

    t1 = time.time()
    print(f"[+] Promotion upsert finished in {t1 - t0:.2f}s! Promoted: {promoted_count}, Failed: {failed_count}, Skipped: {skipped_count}")

    # 3. Post-promotion Verification
    print("\n--- GIAI ĐOẠN 3: POST-PROMOTION INTEGRITY VERIFICATION ---")
    prod_info_after = client.get_collection(PROD_COLLECTION)
    final_production_count = prod_info_after.points_count
    expected_final_count = before_count + promoted_count

    print(f"[*] Production Count Before: {before_count}")
    print(f"[*] Promoted Count:          {promoted_count}")
    print(f"[*] Production Count After:  {final_production_count} (Expected: {expected_final_count})")

    if final_production_count != expected_final_count:
        raise ValueError(f"Count mismatch! Expected {expected_final_count}, got {final_production_count}")
    print("🟢 EXACT POINT COUNT MATCHES PERFECTLY: 7,170 + 325 = 7,495 POINTS!")

    # Verify retrievability of newly promoted points from Production
    print("\n[*] Verifying retrievability of promoted points from Production...")
    sample_ids = staging_ids[:10]
    retrieved_sample = client.retrieve(
        collection_name=PROD_COLLECTION,
        ids=sample_ids,
        with_payload=True
    )
    print(f"[+] Retrievability check: Successfully retrieved {len(retrieved_sample)}/{len(sample_ids)} sample points directly from Production.")
    sample_pld = retrieved_sample[0].payload
    print(f"    Sample Point: {sample_pld.get('official_number')} {sample_pld.get('article_number')} ({sample_pld.get('clause_number')})")
    print(f"    Provenance fields check: doc_id={bool(sample_pld.get('doc_id'))}, effective_date={sample_pld.get('effective_date')}, relations={bool(sample_pld.get('relations') is not None)}")

    # 4. Re-run 25 Baseline Regression Cases on Production (Post-Promotion)
    print("\n--- GIAI ĐOẠN 4: 25-CASE BASELINE REGRESSION TEST ON PRODUCTION (7,495 POINTS) ---")
    embedder = get_embedding_service()

    with open(BENCHMARK_25_FILE, "r", encoding="utf-8") as f:
        cases_25 = json.load(f)["cases"]

    reg_results = []
    reg_hit1 = 0
    reg_hit2 = 0
    reg_hit3 = 0

    for tc in cases_25:
        cid = tc["test_case_id"]
        q = tc["query"]
        expected_docs = tc["expected_documents"]
        primary_evi = tc.get("expected_primary_evidence", "")

        q_vec = embedder.embed_query(q)
        hits = client.query_points(
            collection_name=PROD_COLLECTION,
            query=q_vec,
            limit=5,
            with_payload=True
        ).points

        hit_rank = None
        matched_doc = None
        for r, pt in enumerate(hits, 1):
            pld = pt.payload
            doc_id = str(pld.get("doc_id", "") or "")
            off_num = str(pld.get("official_number", "") or "")
            title = str(pld.get("doc_title", "") or "")
            art = str(pld.get("article_number", "") or pld.get("article", "") or "")
            cl = str(pld.get("clause_number", "") or pld.get("clause", "") or "")

            is_match = any(exp in doc_id or exp in off_num or exp in title for exp in expected_docs)
            if is_match and hit_rank is None:
                hit_rank = r
                matched_doc = f"{off_num or title[:20]} {art} {cl}".strip()

        if hit_rank == 1:
            reg_hit1 += 1
            reg_hit2 += 1
            reg_hit3 += 1
            status_str = "🟢 HIT@1"
        elif hit_rank == 2:
            reg_hit2 += 1
            reg_hit3 += 1
            status_str = "🟡 HIT@2"
        elif hit_rank == 3:
            reg_hit3 += 1
            status_str = "🟡 HIT@3"
        else:
            status_str = f"🔴 MISS (Rank {hit_rank})"

        reg_results.append({
            "test_case_id": cid,
            "dimension": tc["dimension"],
            "query": q,
            "expected_documents": expected_docs,
            "primary_evidence": primary_evi,
            "hit_rank": hit_rank,
            "status": status_str,
            "matched_doc": matched_doc,
            "top1_found": f"{hits[0].payload.get('official_number')} {hits[0].payload.get('article_number')}" if hits else None
        })

    total_25 = len(cases_25)
    print("\n--- 25-CASE POST-PROMOTION REGRESSION SUMMARY ---")
    print(f"Primary Hit@1: {reg_hit1}/{total_25} ({reg_hit1/total_25*100:.1f}%) | Baseline: 92.0%")
    print(f"Hit@2:         {reg_hit2}/{total_25} ({reg_hit2/total_25*100:.1f}%) | Baseline: 100.0%")
    print(f"Hit@3:         {reg_hit3}/{total_25} ({reg_hit3/total_25*100:.1f}%) | Baseline: 100.0%")

    regression_passed = (reg_hit1 >= 23) and (reg_hit2 == 25)
    print("\n" + "=" * 80)
    if regression_passed:
        print("🟢 ZERO REGRESSION POST-PROMOTION: 100% BASELINE FIDELITY PRESERVED ON PRODUCTION!")
    else:
        print("🔴 REGRESSION DETECTED POST-PROMOTION! REQUIRES INVESTIGATION.")
    print("=" * 80)

    # 5. Save Full Promotion Audit Report JSON
    promotion_report = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "production_collection": PROD_COLLECTION,
        "metrics": {
            "before_count": before_count,
            "promoted_count": promoted_count,
            "skipped_duplicate_count": skipped_count,
            "failed_count": failed_count,
            "final_production_count": final_production_count,
            "expected_final_count": expected_final_count
        },
        "regression_results": {
            "total_cases": total_25,
            "hit1": reg_hit1,
            "hit2": reg_hit2,
            "hit3": reg_hit3,
            "hit1_rate": reg_hit1 / total_25,
            "hit2_rate": reg_hit2 / total_25,
            "regression_passed": regression_passed,
            "cases": reg_results
        },
        "verdict": "PASS" if regression_passed and failed_count == 0 else "NEEDS FIX"
    }

    report_path = RESULTS_DIR / "production_promotion_report.json"
    report_path.write_text(json.dumps(promotion_report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[+] Saved promotion audit report to {report_path.name}")

if __name__ == "__main__":
    main()
