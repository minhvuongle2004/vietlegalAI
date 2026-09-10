import sys
from pathlib import Path
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.services.rag.embeddings import get_embedding_service
from backend.app.services.rag.vector_store import QdrantVectorStore
from backend.app.services.rag.retriever import HybridRetriever

CLOUD_URL = "https://69f07c1e-2e88-452f-aded-6dd577ddbd9b.us-west-2-0.aws.cloud.qdrant.io"
CLOUD_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIiwic3ViamVjdCI6ImFwaS1rZXk6OTAxNjk0MzUtYjMwMS00YjAzLWFmMGYtYmYyZjc0MWE4MjYxIn0.bJ2YtMtnmDJXN4k3FKdduN_TsLARSOAvGjBRKW3p028"
PROD_COLLECTION = "vietlegal_articles"

def run_smoke_tests():
    print("=" * 100)
    print(f" STEP 3: POST-PROMOTION SMOKE TESTS DIRECTLY ON PRODUCTION ('{PROD_COLLECTION}' - 7,658 POINTS)")
    print("=" * 100)

    store = QdrantVectorStore(collection_name=PROD_COLLECTION, url=CLOUD_URL, api_key=CLOUD_API_KEY)
    embedder = get_embedding_service()
    retriever = HybridRetriever(vector_store=store, embedding_service=embedder)

    total_points = store.client.get_collection(PROD_COLLECTION).points_count
    print(f"[+] Confirmed Production Points: {total_points}")

    # --------------------------------------------------------------------------
    # 1. Representative P1.2 Queries
    # --------------------------------------------------------------------------
    smoke_queries = [
        {
            "name": "1. NĐ 94/2026 Đào tạo & Sát hạch lái xe",
            "query": "Thẩm quyền cấp, cấp lại và thu hồi giấy phép sát hạch lái xe thuộc cơ quan nào theo Nghị định 94/2026/NĐ-CP?",
            "expected_doc": "94_2026",
            "expected_art": "26",
            "check_top": 1
        },
        {
            "name": "2. NĐ 241/2026 Kết cấu hạ tầng đường bộ & ITS",
            "query": "Quy định về chia sẻ dữ liệu giám sát giao thông trực tuyến thời gian thực từ hệ thống ITS đường cao tốc cho CSGT theo Nghị định 241/2026/NĐ-CP?",
            "expected_doc": "241_2026",
            "expected_art": "1",
            "check_top": 1
        },
        {
            "name": "3. TT 45/2026 Đăng kiểm phương tiện",
            "query": "Kiểm chuẩn thiết bị đo lực phanh con lăn và phân tích khí thải tự động theo Thông tư 45/2026/TT-BXD?",
            "expected_doc": "45_2026",
            "expected_art": "1",
            "check_top": 1
        },
        {
            "name": "4. QCVN 41:2024 / TT 51/2024 Báo hiệu đường bộ",
            "query": "Quy chuẩn kỹ thuật quốc gia QCVN 41:2024/BGTVT về báo hiệu đường bộ",
            "expected_doc": "qcvn41",
            "expected_art": "1",
            "check_top": 3
        }
    ]

    print("\n[*] --- PART 1: REPRESENTATIVE P1.2 QUERIES SMOKE CHECK ---")
    smoke_results = []
    for sq in smoke_queries:
        print(f"\nQuery: {sq['name']}")
        print(f"  Text: {sq['query']}")
        res = retriever.retrieve(query=sq["query"], top_k=3)
        check_k = sq.get("check_top", 1)
        matched = False
        top_match_info = None

        for rank, hit in enumerate(res[:check_k], start=1):
            doc = hit.get("doc_id", "")
            title = hit.get("doc_title", "")
            art = str(hit.get("article_number", ""))
            header = str(hit.get("context_header", ""))
            score = hit.get("score", 0.0)

            pass_doc = sq["expected_doc"].lower() in doc.lower() or sq["expected_doc"].lower() in title.lower()
            pass_art = sq["expected_art"].lower() in art.lower() or sq["expected_art"].lower() in header.lower()

            if pass_doc and pass_art:
                matched = True
                top_match_info = f"Rank #{rank}: {doc} | {art} (Score: {score:.4f})"
                break

        top1 = res[0] if res else {}
        print(f"  Top 1: {top1.get('doc_id')} | {top1.get('article_number')} (Score: {top1.get('score', 0.0):.4f})")
        if matched:
            print(f"  P1.2 Match: {top_match_info}")
            print(f"  Status: PASS 🟢")
        else:
            print(f"  Status: FAIL 🔴")

        smoke_results.append({
            "name": sq["name"],
            "pass": matched,
            "match_info": top_match_info
        })

    # --------------------------------------------------------------------------
    # 2. Temporal Contrast Verification
    # --------------------------------------------------------------------------
    print("\n[*] --- PART 2: TEMPORAL CONTRAST ON PRODUCTION ---")
    contrast_query = "Thí sinh thi sát hạch lái xe ô tô vào ngày 30/06/2026 có phải thực hiện bài thi mô phỏng tình huống giao thông không?"

    # A. 2026-06-30
    print("\n[A] as_of_date = 2026-06-30:")
    print("    Expected: TT 12/2025 Điều 14 (NĐ 94/2026 & TT 108/2026 excluded)")
    res_a = retriever.retrieve(query=contrast_query, as_of_date="2026-06-30", top_k=3)
    top1_a = res_a[0] if res_a else {}
    doc_a = str(top1_a.get("doc_id", "") or top1_a.get("official_number", ""))
    art_a = str(top1_a.get("article_number", ""))
    title_a = str(top1_a.get("article_title", ""))

    pass_a = ("12_2025" in doc_a or "12/2025" in doc_a) and "108_2026" not in doc_a and "94_2026" not in doc_a
    print(f"    Found Top 1: {doc_a} | {art_a} ({title_a})")
    print(f"    NĐ 94 and TT 108 excluded: {'94_2026' not in doc_a and '108_2026' not in doc_a}")
    print(f"    Status: {'PASS 🟢' if pass_a else 'FAIL 🔴'}")

    # B. 2026-07-01
    print("\n[B] as_of_date = 2026-07-01:")
    print("    Expected: TT 108/2026 Điều 15 (Correct provision/citation, not Điều 35)")
    res_b = retriever.retrieve(query=contrast_query, as_of_date="2026-07-01", top_k=3)
    top1_b = res_b[0] if res_b else {}
    doc_b = str(top1_b.get("doc_id", "") or top1_b.get("official_number", ""))
    art_b = str(top1_b.get("article_number", ""))
    clause_b = str(top1_b.get("clause_number", ""))
    title_b = str(top1_b.get("article_title", ""))

    pass_b_doc = "108_2026" in doc_b or "108/2026" in doc_b
    pass_b_art = "15" in art_b and "35" not in art_b
    pass_b = pass_b_doc and pass_b_art

    print(f"    Found Top 1: {doc_b} | {art_b} ({clause_b}) - {title_b}")
    print(f"    Provision is Điều 15 (not Điều 35): {pass_b_art}")
    print(f"    Status: {'PASS 🟢' if pass_b else 'FAIL 🔴'}")

    # Summary
    all_smoke_pass = all(r["pass"] for r in smoke_results) and pass_a and pass_b
    print("\n" + "=" * 100)
    print(f" POST-PROMOTION PRODUCTION SMOKE TESTS VERDICT: {'PASS 🟢' if all_smoke_pass else 'FAIL 🔴'}")
    print("=" * 100)

if __name__ == "__main__":
    run_smoke_tests()
