import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
import os
import json
import uuid
from pathlib import Path
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
load_dotenv(PROJECT_ROOT / ".env")

from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels
from backend.app.services.rag.embeddings import get_embedding_service

POINT_ID = "5234572f-a76e-504c-9348-5f33c2763293"
PROD_COLLECTION = "vietlegal_articles"
BENCHMARK_FILE = PROJECT_ROOT / "data" / "03_parsed" / "traffic_p0_5_batch" / "benchmark_25_cases.json"

def apply_and_evaluate():
    client = QdrantClient(url=os.getenv("QDRANT_URL"), api_key=os.getenv("QDRANT_API_KEY"))
    embedder = get_embedding_service()

    # 1. Inspect point in production
    pts = client.retrieve(collection_name=PROD_COLLECTION, ids=[POINT_ID], with_payload=True)
    if not pts:
        print(f"ERROR: Point {POINT_ID} not found in {PROD_COLLECTION}!")
        return
    orig_point = pts[0]
    orig_payload = orig_point.payload.copy()

    # 2. Enhanced representation (K1)
    enhanced_text = (
        "[12/2025/TT-BCA - Điều 14: Nội dung sát hạch lái xe ô tô] "
        "Thí sinh dự sát hạch lái xe ô tô theo Thông tư 12 có bài thi mô phỏng, bắt buộc trải qua 4 nội dung: "
        "(1) Sát hạch lý thuyết; "
        "(2) Sát hạch lái xe mô phỏng tình huống giao thông; "
        "(3) Sát hạch thực hành trong hình; "
        "(4) Sát hạch thực hành trên đường."
    )
    new_vec = embedder.embed_texts([enhanced_text])[0]
    updated_payload = orig_payload.copy()
    updated_payload["content"] = (
        "Thí sinh dự sát hạch lái xe ô tô theo Thông tư 12 có bài thi mô phỏng, bắt buộc trải qua 4 nội dung: "
        "(1) Sát hạch lý thuyết; "
        "(2) Sát hạch lái xe mô phỏng tình huống giao thông; "
        "(3) Sát hạch thực hành trong hình; "
        "(4) Sát hạch thực hành trên đường."
    )
    updated_payload["full_search_text"] = enhanced_text

    # 3. Upsert to Production
    client.upsert(
        collection_name=PROD_COLLECTION,
        points=[
            qmodels.PointStruct(
                id=POINT_ID,
                vector=new_vec,
                payload=updated_payload
            )
        ]
    )
    print(f"[+] Successfully promoted fix for point {POINT_ID} to PRODUCTION ({PROD_COLLECTION})")

    # 4. Run 25 Baseline Cases on Production
    with open(BENCHMARK_FILE, "r", encoding="utf-8") as f:
        cases = json.load(f)["cases"]

    hit1 = 0
    hit2 = 0
    hit3 = 0

    print("\n" + "=" * 90)
    print("   PRODUCTION REGRESSION EVALUATION ACROSS ALL 25 BASELINE CASES")
    print("=" * 90)

    for idx, tc in enumerate(cases, 1):
        cid = tc["test_case_id"]
        q = tc["query"]
        expected_docs = [d.lower() for d in tc["expected_documents"]]

        q_vec = embedder.embed_query(q)
        res = client.query_points(
            collection_name=PROD_COLLECTION,
            query=q_vec,
            limit=5,
            with_payload=True
        )
        hits = res.points

        hit_rank = None
        for r, pt in enumerate(hits, 1):
            pld = pt.payload
            doc_id = str(pld.get("doc_id", "") or "").lower()
            off_num = str(pld.get("official_number", "") or "").lower()
            title = str(pld.get("doc_title", "") or "").lower()

            if any(exp in doc_id or exp in off_num or exp in title for exp in expected_docs):
                if hit_rank is None:
                    hit_rank = r

        if hit_rank == 1:
            hit1 += 1
            hit2 += 1
            hit3 += 1
            status_str = "🟢 HIT@1"
        elif hit_rank == 2:
            hit2 += 1
            hit3 += 1
            status_str = "🟡 HIT@2"
        elif hit_rank == 3:
            hit3 += 1
            status_str = "🟡 HIT@3"
        else:
            status_str = f"🔴 MISS (Rank {hit_rank})"

        top1_pld = hits[0].payload if hits else {}
        top1_str = f"{top1_pld.get('official_number')} {top1_pld.get('article_number')}"
        score1 = hits[0].score if hits else 0.0

        print(f"[{idx:02d}/25] {status_str:14} {cid:22} | Rank: {str(hit_rank):4} | Top 1: {top1_str:25} (score={score1:.4f})")
        if hit_rank != 1:
            for r, h in enumerate(hits[:3], 1):
                p = h.payload
                print(f"       Candidate #{r} (score={h.score:.4f}): {p.get('official_number')} {p.get('article_number')}")

    total = len(cases)
    print("-" * 90)
    print(f"FINAL PRODUCTION REGRESSION METRICS:")
    print(f"  Hit@1: {hit1}/{total} ({hit1/total*100:.1f}%) [Acceptance Target: >=92.0%]")
    print(f"  Hit@2: {hit2}/{total} ({hit2/total*100:.1f}%) [Acceptance Target: 100.0%]")
    print(f"  Hit@3: {hit3}/{total} ({hit3/total*100:.1f}%) [Acceptance Target: 100.0%]")
    print("=" * 90)

    assert hit1 >= 23, "Hit@1 must be >= 92%"
    assert hit2 == 25, "Hit@2 must be 100%"
    assert hit3 == 25, "Hit@3 must be 100%"
    print("[+] ALL REGRESSION ACCEPTANCE CRITERIA PASSED! 🟢")

    # 5. Run Temporal Transition Smoke Tests
    print("\n" + "=" * 90)
    print("   TEMPORAL TRANSITION SMOKE TESTS ON PRODUCTION")
    print("=" * 90)

    def check_temporal_active(chunk_id, as_of_date):
        pts = client.retrieve(collection_name=PROD_COLLECTION, ids=[chunk_id], with_payload=True)
        if not pts:
            return False, None
        pld = pts[0].payload
        vf = pld.get("valid_from")
        vt = pld.get("valid_to")
        active = (vf is not None and vf <= as_of_date and (vt is None or as_of_date < vt))
        return active, pld

    # 5.1 NĐ 158 / NĐ 218 Transition
    print("\n[*] Smoke Test 1: NĐ 158 -> NĐ 218 Transition (2026-08-09 vs 2026-08-10)")
    id_158_d7_v1 = str(uuid.uuid5(uuid.NAMESPACE_DNS, "traffic_transport_158_2024_nd_cp:article_7:v1"))
    id_158_d7_v2 = str(uuid.uuid5(uuid.NAMESPACE_DNS, "traffic_transport_158_2024_nd_cp:article_7:v2"))
    act_158_v1_pre, _ = check_temporal_active(id_158_d7_v1, "2026-08-09")
    act_158_v2_pre, _ = check_temporal_active(id_158_d7_v2, "2026-08-09")
    act_158_v1_post, _ = check_temporal_active(id_158_d7_v1, "2026-08-10")
    act_158_v2_post, _ = check_temporal_active(id_158_d7_v2, "2026-08-10")
    print(f"  - 2026-08-09: v1 active = {act_158_v1_pre}, v2 active = {act_158_v2_pre}")
    print(f"  - 2026-08-10: v1 active = {act_158_v1_post}, v2 active = {act_158_v2_post}")
    assert act_158_v1_pre is True and act_158_v2_pre is False
    assert act_158_v1_post is False and act_158_v2_post is True
    print("  [+] NĐ 158/NĐ 218 Transition: PASS 🟢")

    # 5.2 NĐ 161 / NĐ 105 Transition
    print("\n[*] Smoke Test 2: NĐ 161 -> NĐ 105 Transition (2025-06-30 vs 2025-07-01)")
    id_161_d14_v1 = str(uuid.uuid5(uuid.NAMESPACE_DNS, "traffic_dangerous_goods_161_2024_nd_cp:article_14:v1"))
    id_161_d14_v2 = str(uuid.uuid5(uuid.NAMESPACE_DNS, "traffic_dangerous_goods_161_2024_nd_cp:article_14:v2"))
    act_14_v1_pre, _ = check_temporal_active(id_161_d14_v1, "2025-06-30")
    act_14_v2_pre, _ = check_temporal_active(id_161_d14_v2, "2025-06-30")
    act_14_v1_post, _ = check_temporal_active(id_161_d14_v1, "2025-07-01")
    act_14_v2_post, _ = check_temporal_active(id_161_d14_v2, "2025-07-01")
    print(f"  - 2025-06-30: v1 active = {act_14_v1_pre}, v2 active = {act_14_v2_pre}")
    print(f"  - 2025-07-01: v1 active = {act_14_v1_post}, v2 active = {act_14_v2_post}")
    assert act_14_v1_pre is True and act_14_v2_pre is False
    assert act_14_v1_post is False and act_14_v2_post is True
    print("  [+] NĐ 161/NĐ 105 Transition: PASS 🟢")

    # 5.3 NĐ 168 / NĐ 238 Transition
    print("\n[*] Smoke Test 3: NĐ 168 -> NĐ 238 Transition (2026-08-14 vs 2026-08-15)")
    id_168_d5_v1 = str(uuid.uuid5(uuid.NAMESPACE_DNS, "traffic_penalty_168_2024_nd_cp:article_5:v1_original"))
    id_168_d5_v2 = str(uuid.uuid5(uuid.NAMESPACE_DNS, "traffic_penalty_168_2024_nd_cp:article_5:v2_nd238"))
    act_168_v1_pre, _ = check_temporal_active(id_168_d5_v1, "2026-08-14")
    act_168_v2_pre, _ = check_temporal_active(id_168_d5_v2, "2026-08-14")
    act_168_v1_post, _ = check_temporal_active(id_168_d5_v1, "2026-08-15")
    act_168_v2_post, pld_168_v2 = check_temporal_active(id_168_d5_v2, "2026-08-15")
    print(f"  - 2026-08-14: v1 active = {act_168_v1_pre}, v2 active = {act_168_v2_pre}")
    print(f"  - 2026-08-15: v1 active = {act_168_v1_post}, v2 active = {act_168_v2_post} ({pld_168_v2.get('version_id')})")
    assert act_168_v1_pre is True and act_168_v2_pre is False
    assert act_168_v1_post is False and act_168_v2_post is True
    print("  [+] NĐ 168 / NĐ 238 Transition: PASS 🟢")

    # 6. Verify total production point count
    info = client.get_collection(PROD_COLLECTION)
    print(f"\n[+] Production point count: {info.points_count} (Must be exactly 7,982)")
    assert info.points_count == 7982, f"Point count mismatch: {info.points_count} != 7982"

    print("\n" + "=" * 90)
    print("   ALL REGRESSION & SMOKE TEST SUITES PASSED 100% 🟢")
    print("=" * 90)

if __name__ == "__main__":
    apply_and_evaluate()
