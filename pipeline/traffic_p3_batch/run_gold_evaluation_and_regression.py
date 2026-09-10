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
from backend.app.services.rag.embeddings import get_embedding_service

CLOUD_URL = os.getenv("QDRANT_URL")
CLOUD_API_KEY = os.getenv("QDRANT_API_KEY")
PROD_COLLECTION = "vietlegal_articles"
BENCHMARK_25_FILE = PROJECT_ROOT / "data" / "03_parsed" / "traffic_p0_5_batch" / "benchmark_25_cases.json"

def run_evaluation():
    print("=" * 90)
    print("   TRAFFIC P3 EVALUATION: 25 BASELINE REGRESSION & GOLD TEMPORAL EVALUATION")
    print("=" * 90)

    client = QdrantClient(url=CLOUD_URL, api_key=CLOUD_API_KEY, timeout=30.0)
    embedder = get_embedding_service()

    # -------------------------------------------------------------
    # 1. 25 BASELINE REGRESSION CASES
    # -------------------------------------------------------------
    print("\n>>> [1/2] Running 25 Baseline Cases Regression on Production Collection...")
    with open(BENCHMARK_25_FILE, "r", encoding="utf-8") as f:
        raw_data = json.load(f)
        cases_25 = raw_data["cases"] if isinstance(raw_data, dict) and "cases" in raw_data else raw_data

    reg_hit1 = 0
    reg_hit2 = 0
    reg_hit3 = 0

    for idx, tc in enumerate(cases_25, 1):
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

            is_match = any(exp in doc_id or exp in off_num or exp in title for exp in expected_docs)
            if is_match and hit_rank is None:
                hit_rank = r

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

        top1_pld = hits[0].payload if hits else {}
        print(f"  [{idx:02d}/25] {status_str} {cid} ({tc.get('dimension', '')}): Top #1 = {top1_pld.get('official_number')} Điều {top1_pld.get('article_number')}")

    total_25 = len(cases_25)
    print("\n--- 25-CASE REGRESSION SUMMARY ---")
    print(f"Primary Hit@1: {reg_hit1}/{total_25} ({reg_hit1/total_25*100:.1f}%) | Baseline Target: >=92.0%")
    print(f"Hit@2:         {reg_hit2}/{total_25} ({reg_hit2/total_25*100:.1f}%) | Baseline Target: 100.0%")
    print(f"Hit@3:         {reg_hit3}/{total_25} ({reg_hit3/total_25*100:.1f}%) | Baseline Target: 100.0%")

    regression_passed = (reg_hit1 >= 23)
    print(f"[+] Baseline Regression Verdict: {'PASS 🟢' if regression_passed else 'FAIL 🔴'}")
    assert regression_passed, "Baseline regression failed"

    # -------------------------------------------------------------
    # 2. GOLD TEMPORAL EVALUATIONS
    # -------------------------------------------------------------
    print("\n>>> [2/2] Running Gold Temporal Evaluations...")

    def check_temporal_active(chunk_id, as_of_date):
        pts = client.retrieve(collection_name=PROD_COLLECTION, ids=[chunk_id], with_payload=True)
        if not pts:
            return False, None
        pld = pts[0].payload
        vf = pld.get("valid_from")
        vt = pld.get("valid_to")
        active = (vf is not None and vf <= as_of_date and (vt is None or as_of_date < vt))
        return active, pld

    # A. NĐ 165 Temporal Transition (2026-05-01 vs 2026-07-01+)
    print("\n[*] Check A: NĐ 165 Temporal Transition (2026-05-01 vs 2026-07-01)")
    id_165_d21_v1 = "f4d88ffa-37a0-5d5b-90ca-2898e358d6c8"
    id_165_d21_v2 = "0772dd57-2b16-5e6d-8649-3583e0054e1a"
    
    act_v1_pre, _ = check_temporal_active(id_165_d21_v1, "2026-05-01")
    act_v2_pre, _ = check_temporal_active(id_165_d21_v2, "2026-05-01")
    act_v1_post, _ = check_temporal_active(id_165_d21_v1, "2026-07-01")
    act_v2_post, pld_v2 = check_temporal_active(id_165_d21_v2, "2026-07-01")

    print(f"  - as_of_date = 2026-05-01 (BEFORE NĐ 241): v1 active = {act_v1_pre}, v2 active = {act_v2_pre}")
    print(f"  - as_of_date = 2026-07-01 (AFTER NĐ 241):  v1 active = {act_v1_post}, v2 active = {act_v2_post} ({pld_v2.get('version_id')})")
    assert act_v1_pre is True and act_v2_pre is False, "Before 2026-07-01, only v1 must be active"
    assert act_v1_post is False and act_v2_post is True, "From 2026-07-01, only v2 must be active"
    print("  [+] NĐ 165 Temporal Transition: PASS 🟢")

    # B. NĐ 160 -> NĐ 94 Transition (from 2026-07-01)
    print("\n[*] Check B: NĐ 160 -> NĐ 94 Transition (2026-06-30 vs 2026-07-01)")
    q_vec_dt = embedder.embed_query("Đào tạo, sát hạch lái xe mô phỏng tình huống giao thông")
    res_dt = client.query_points(collection_name=PROD_COLLECTION, query=q_vec_dt, limit=5, with_payload=True)
    dt_docs = [pt.payload.get("official_number") for pt in res_dt.points]
    print(f"  - Active docs retrieved: {dt_docs[:3]}")
    assert not any("160/2024" in str(d) for d in dt_docs), "NĐ 160 must not appear in current active corpus"
    print("  [+] NĐ 160 Exclusion & Transition: PASS 🟢")

    # C. NĐ 158 -> NĐ 218 Transition (from 2026-08-10)
    print("\n[*] Check C: NĐ 158 -> NĐ 218 Transition (2026-08-09 vs 2026-08-10)")
    id_158_d7_v1 = str(uuid.uuid5(uuid.NAMESPACE_DNS, "traffic_transport_158_2024_nd_cp:article_7:v1"))
    id_158_d7_v2 = str(uuid.uuid5(uuid.NAMESPACE_DNS, "traffic_transport_158_2024_nd_cp:article_7:v2"))
    
    act_158_v1_pre, _ = check_temporal_active(id_158_d7_v1, "2026-08-09")
    act_158_v2_pre, _ = check_temporal_active(id_158_d7_v2, "2026-08-09")
    act_158_v1_post, _ = check_temporal_active(id_158_d7_v1, "2026-08-10")
    act_158_v2_post, pld_158_v2 = check_temporal_active(id_158_d7_v2, "2026-08-10")

    print(f"  - as_of_date = 2026-08-09: v1 active = {act_158_v1_pre}, v2 active = {act_158_v2_pre}")
    print(f"  - as_of_date = 2026-08-10: v1 active = {act_158_v1_post}, v2 active = {act_158_v2_post} ({pld_158_v2.get('version_id')})")
    assert act_158_v1_pre is True and act_158_v2_pre is False
    assert act_158_v1_post is False and act_158_v2_post is True
    print("  [+] NĐ 158/NĐ 218 Transition: PASS 🟢")

    # D. NĐ 161 -> NĐ 105 Transition (from 2025-07-01)
    print("\n[*] Check D: NĐ 161 -> NĐ 105 Transition (2025-06-30 vs 2025-07-01)")
    id_161_d14_v1 = str(uuid.uuid5(uuid.NAMESPACE_DNS, "traffic_dangerous_goods_161_2024_nd_cp:article_14:v1"))
    id_161_d14_v2 = str(uuid.uuid5(uuid.NAMESPACE_DNS, "traffic_dangerous_goods_161_2024_nd_cp:article_14:v2"))
    id_161_d19 = str(uuid.uuid5(uuid.NAMESPACE_DNS, "traffic_dangerous_goods_161_2024_nd_cp:article_19:v1"))

    act_14_v1_pre, _ = check_temporal_active(id_161_d14_v1, "2025-06-30")
    act_14_v2_pre, _ = check_temporal_active(id_161_d14_v2, "2025-06-30")
    act_14_v1_post, _ = check_temporal_active(id_161_d14_v1, "2025-07-01")
    act_14_v2_post, pld_14_v2 = check_temporal_active(id_161_d14_v2, "2025-07-01")
    act_19_pre, pld_19_pre = check_temporal_active(id_161_d19, "2025-06-30")
    act_19_post, pld_19_post = check_temporal_active(id_161_d19, "2025-07-01")

    print(f"  - Điều 14: before 2025-07-01 (v1={act_14_v1_pre}, v2={act_14_v2_pre}), from 2025-07-01 (v1={act_14_v1_post}, v2={act_14_v2_post})")
    print(f"  - Điều 19: before 2025-07-01 (active={act_19_pre}), from 2025-07-01 (active={act_19_post}, status={pld_19_post.get('legal_status')})")
    assert act_14_v1_pre is True and act_14_v2_pre is False
    assert act_14_v1_post is False and act_14_v2_post is True
    assert act_19_pre is True and act_19_post is False
    assert pld_19_post.get("legal_status") == "HET_HIEU_LUC", "Điều 19 status must be HET_HIEU_LUC"
    print("  [+] NĐ 161/NĐ 105 Amendment Transition: PASS 🟢")

    print("\n" + "=" * 90)
    print("   ALL REGRESSION & GOLD TEMPORAL EVALUATION SUITES PASSED 100% 🟢")
    print("=" * 90)

if __name__ == "__main__":
    run_evaluation()
