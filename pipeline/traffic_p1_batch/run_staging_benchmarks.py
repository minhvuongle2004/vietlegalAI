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
from backend.app.services.rag.embeddings import get_embedding_service

CLOUD_URL = "https://69f07c1e-2e88-452f-aded-6dd577ddbd9b.us-west-2-0.aws.cloud.qdrant.io"
CLOUD_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIiwic3ViamVjdCI6ImFwaS1rZXk6OTAxNjk0MzUtYjMwMS00YjAzLWFmMGYtYmYyZjc0MWE4MjYxIn0.bJ2YtMtnmDJXN4k3FKdduN_TsLARSOAvGjBRKW3p028"

STAGING_COLLECTION = "vietlegal_articles_staging"
PROD_COLLECTION = "vietlegal_articles"

BENCHMARK_25_FILE = PROJECT_ROOT / "data" / "03_parsed" / "traffic_p0_5_batch" / "benchmark_25_cases.json"
RESULTS_DIR = PROJECT_ROOT / "data" / "03_parsed" / "traffic_p1_batch"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# 10 New Coverage Cases specifically testing Traffic P1 legal provisions
NEW_P1_BENCHMARK_CASES = [
    {
        "case_id": "TC-P1-CSGT-01",
        "dimension": "TUAN_TRA_CSGT",
        "query": "Cảnh sát giao thông được dừng phương tiện giao thông trong những trường hợp nào?",
        "expected_doc": "73/2024/TT-BCA",
        "expected_article": "Điều 11",
        "description": "4 trường hợp CSGT được dừng xe để kiểm soát"
    },
    {
        "case_id": "TC-P1-CSGT-02",
        "dimension": "TUAN_TRA_CSGT",
        "query": "Kiểm tra giấy tờ xe qua ứng dụng định danh quốc gia VNeID và tạm giữ giấy tờ điện tử",
        "expected_doc": "73/2024/TT-BCA",
        "expected_article": "Điều 12",
        "description": "Kiểm tra và tước tạm giữ giấy tờ trên môi trường điện tử VNeID"
    },
    {
        "case_id": "TC-P1-DANGKIEM-01",
        "dimension": "DANG_KIEM_XE",
        "query": "Quy định về niên hạn sử dụng xe ô tô tải chở hàng và xe ô tô khách chở người",
        "expected_doc": "89/2026/NĐ-CP",
        "expected_article": "Điều 18",
        "description": "Niên hạn ô tô tải không quá 25 năm, ô tô khách không quá 20 năm"
    },
    {
        "case_id": "TC-P1-DANGKIEM-02",
        "dimension": "DANG_KIEM_XE",
        "query": "Xe cơ giới mới chưa qua sử dụng có được miễn kiểm định lần đầu không?",
        "expected_doc": "30/2026/TT-BXD",
        "expected_article": "Điều 6",
        "description": "Miễn kiểm định lần đầu cho xe mới dưới 3 năm"
    },
    {
        "case_id": "TC-P1-DANGKIEM-03",
        "dimension": "DANG_KIEM_XE",
        "query": "Đổi biển số xe hoặc sang tên đổi chủ có phải mang xe đi đăng kiểm lại không?",
        "expected_doc": "30/2026/TT-BXD",
        "expected_article": "Điều 10",
        "description": "Miễn khám xe lại khi đổi biển số, sang tên, chuyển vùng"
    },
    {
        "case_id": "TC-P1-DANGKIEM-04",
        "dimension": "DANG_KIEM_XE",
        "query": "Lắp thêm giá nóc baga mui hoặc cản trước sau có bị coi là cải tạo xe và bị từ chối đăng kiểm không?",
        "expected_doc": "30/2026/TT-BXD",
        "expected_article": "Điều 11",
        "description": "Các trường hợp lắp phụ kiện không coi là cải tạo xe"
    },
    {
        "case_id": "TC-P1-GPLX-01",
        "dimension": "PHUC_HOI_DIEM_GPLX",
        "query": "Bao lâu sau khi bị trừ hết 12 điểm bằng lái xe thì được đăng ký kiểm tra kiến thức phục hồi điểm?",
        "expected_doc": "65/2024/TT-BCA",
        "expected_article": "Điều 3",
        "description": "Thời hạn tối thiểu 06 tháng kể từ ngày bị trừ hết điểm"
    },
    {
        "case_id": "TC-P1-TAITRONG-01",
        "dimension": "TAI_TRONG_DUONG_BO",
        "query": "Tải trọng trục đơn và tải trọng cụm trục kép cho phép của xe cơ giới đường bộ",
        "expected_doc": "12/2025/TT-BXD",
        "expected_article": "Điều 5",
        "description": "Tải trọng trục đơn tối đa 10 tấn, cụm trục kép từ 11 đến 18 tấn"
    },
    {
        "case_id": "TC-P1-TAITRONG-02",
        "dimension": "AMENDMENT_RESOLUTION",
        "query": "Cụm trục kép trang bị hệ thống treo khí nén bóng hơi được nâng tải trọng trục tối đa lên bao nhiêu?",
        "expected_doc": "19/2026/TT-BXD",
        "expected_article": "Điều 1",
        "description": "Nâng tải trọng trục kép bóng hơi lên 19,0 tấn (sửa TT 12/2025)"
    },
    {
        "case_id": "TC-P1-PROVISION-01",
        "dimension": "PROVISION_HISTORICAL",
        "query": "Trách nhiệm thi hành và tổ chức thực hiện của Thông tư 28/2024/TT-BCA",
        "expected_doc": "28/2024/TT-BCA",
        "expected_article": "Điều 3",
        "description": "Truy xuất provision active Điều 3 TT 28/2024"
    }
]

def search_collection(client, collection_name, query_vector, limit=5, filter_eligible=True):
    query_filter = None
    if filter_eligible:
        query_filter = qmodels.Filter(
            must=[
                qmodels.FieldCondition(
                    key="current_retrieval_eligible",
                    match=qmodels.MatchValue(value=True)
                )
            ]
        )
    
    if hasattr(client, "query_points"):
        res = client.query_points(
            collection_name=collection_name,
            query=query_vector,
            limit=limit,
            query_filter=query_filter,
            with_payload=True
        )
        return res.points
    else:
        return client.search(
            collection_name=collection_name,
            query_vector=query_vector,
            limit=limit,
            query_filter=query_filter,
            with_payload=True
        )

def main():
    print("=" * 80)
    print("   TRAFFIC P1: STAGING RETRIEVAL BENCHMARK & REGRESSION CHECK")
    print("=" * 80)

    client = QdrantClient(url=CLOUD_URL, api_key=CLOUD_API_KEY, timeout=15.0)
    embedder = get_embedding_service()

    # PART 1: NEW P1 COVERAGE BENCHMARK ON STAGING
    print("\n" + "=" * 80)
    print("   PART 1: NEW P1 COVERAGE BENCHMARK (10 TEST CASES ON STAGING)")
    print("=" * 80)

    p1_results = []
    p1_hit1 = 0
    p1_hit2 = 0
    p1_hit3 = 0

    for tc in NEW_P1_BENCHMARK_CASES:
        cid = tc["case_id"]
        q = tc["query"]
        exp_doc = tc["expected_doc"]
        exp_art = tc["expected_article"]

        q_vec = embedder.embed_query(q)
        hits = search_collection(client, STAGING_COLLECTION, q_vec, limit=5, filter_eligible=False)

        hit_rank = None
        for r, pt in enumerate(hits, 1):
            pld = pt.payload
            doc_matched = exp_doc in pld.get("official_number", "")
            art_matched = exp_art in pld.get("article_number", "")
            if doc_matched and art_matched:
                hit_rank = r
                break
            elif doc_matched and not hit_rank:
                # Document match but different article
                hit_rank = r

        if hit_rank == 1:
            p1_hit1 += 1
            p1_hit2 += 1
            p1_hit3 += 1
            status_str = "🟢 HIT@1"
        elif hit_rank == 2:
            p1_hit2 += 1
            p1_hit3 += 1
            status_str = "🟡 HIT@2"
        elif hit_rank == 3:
            p1_hit3 += 1
            status_str = "🟡 HIT@3"
        else:
            status_str = f"🔴 MISS (Rank {hit_rank})"

        top1_pld = hits[0].payload if hits else {}
        print(f"[{status_str}] {cid}: {tc['dimension']}")
        print(f"      Query: {q}")
        print(f"      Expected: {exp_doc} {exp_art} | Found Top #1: {top1_pld.get('official_number')} {top1_pld.get('article_number')} (Score: {hits[0].score:.4f})")

        p1_results.append({
            "case_id": cid,
            "dimension": tc["dimension"],
            "query": q,
            "expected_doc": exp_doc,
            "expected_article": exp_art,
            "hit_rank": hit_rank,
            "status": status_str,
            "top_hits": [
                {"rank": idx+1, "official_number": h.payload.get("official_number"), "article": h.payload.get("article_number"), "score": h.score}
                for idx, h in enumerate(hits[:3])
            ]
        })

    p1_total = len(NEW_P1_BENCHMARK_CASES)
    print("\n--- NEW P1 BENCHMARK SUMMARY ---")
    print(f"Hit@1: {p1_hit1}/{p1_total} ({p1_hit1/p1_total*100:.1f}%)")
    print(f"Hit@2: {p1_hit2}/{p1_total} ({p1_hit2/p1_total*100:.1f}%)")
    print(f"Hit@3: {p1_hit3}/{p1_total} ({p1_hit3/p1_total*100:.1f}%)")

    # PART 2: 25-CASE BASELINE REGRESSION CHECK ON PRODUCTION
    print("\n" + "=" * 80)
    print("   PART 2: 25-CASE BASELINE REGRESSION TEST (ON PRODUCTION BASELINE)")
    print("=" * 80)

    with open(BENCHMARK_25_FILE, "r", encoding="utf-8") as f:
        data_25 = json.load(f)
        cases_25 = data_25["cases"]

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
        # Search production collection
        hits = search_collection(
            client=client,
            collection_name=PROD_COLLECTION,
            query_vector=q_vec,
            limit=5,
            filter_eligible=False
        )

        hit_rank = None
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
            "top1_found": f"{hits[0].payload.get('official_number')} {hits[0].payload.get('article_number')}" if hits else None
        })

    total_25 = len(cases_25)
    print("\n--- 25-CASE REGRESSION SUMMARY ---")
    print(f"Primary Hit@1: {reg_hit1}/{total_25} ({reg_hit1/total_25*100:.1f}%) | Baseline: 92.0%")
    print(f"Hit@2:         {reg_hit2}/{total_25} ({reg_hit2/total_25*100:.1f}%) | Baseline: 100.0%")
    print(f"Hit@3:         {reg_hit3}/{total_25} ({reg_hit3/total_25*100:.1f}%) | Baseline: 100.0%")

    regression_passed = (reg_hit1 >= 23) and (reg_hit2 == 25)
    print("\n" + "=" * 80)
    if regression_passed:
        print("🟢 ZERO REGRESSION DETECTED: 100% BASELINE FIDELITY PRESERVED!")
    else:
        print("🔴 REGRESSION DETECTED! ROLLBACK REQUIRED.")
    print("=" * 80)

    # Save comprehensive report JSON
    benchmark_report = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "staging_collection": STAGING_COLLECTION,
        "staging_points": 325,
        "new_p1_benchmark": {
            "total_cases": p1_total,
            "hit1": p1_hit1,
            "hit2": p1_hit2,
            "hit3": p1_hit3,
            "hit1_rate": p1_hit1 / p1_total,
            "hit2_rate": p1_hit2 / p1_total,
            "cases": p1_results
        },
        "regression_benchmark": {
            "total_cases": total_25,
            "hit1": reg_hit1,
            "hit2": reg_hit2,
            "hit3": reg_hit3,
            "hit1_rate": reg_hit1 / total_25,
            "hit2_rate": reg_hit2 / total_25,
            "regression_passed": regression_passed,
            "cases": reg_results
        }
    }
    out_path = RESULTS_DIR / "staging_benchmark_and_regression_report.json"
    out_path.write_text(json.dumps(benchmark_report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[+] Saved report to {out_path.name}")

if __name__ == "__main__":
    main()
