import os
import sys
import json
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.services.rag.embeddings import get_embedding_service
from backend.app.services.rag.vector_store import QdrantVectorStore
from backend.app.services.rag.retriever import HybridRetriever

PROD_COLLECTION = "vietlegal_articles"
CLOUD_URL = "https://69f07c1e-2e88-452f-aded-6dd577ddbd9b.us-west-2-0.aws.cloud.qdrant.io"
CLOUD_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIiwic3ViamVjdCI6ImFwaS1rZXk6OTAxNjk0MzUtYjMwMS00YjAzLWFmMGYtYmYyZjc0MWE4MjYxIn0.bJ2YtMtnmDJXN4k3FKdduN_TsLARSOAvGjBRKW3p028"

def run_regression_tests():
    print("=" * 100)
    print("   TASK 7: POST-PARITY REGRESSION & TEMPORAL BENCHMARK (PRODUCTION: 7,658 POINTS)")
    print("=" * 100)

    store = QdrantVectorStore(collection_name=PROD_COLLECTION, url=CLOUD_URL, api_key=CLOUD_API_KEY)
    embedder = get_embedding_service()
    retriever = HybridRetriever(vector_store=store, embedding_service=embedder)

    # 1. Temporal Contrast Tests (2026-06-30 vs 2026-07-01)
    print("\n[*] --- PART 1: TEMPORAL CONTRAST TESTS ---")
    contrast_q = "Thí sinh thi sát hạch lái xe ô tô có phải thực hiện bài thi mô phỏng tình huống giao thông không?"

    # Mốc A: 2026-06-30
    res_a = retriever.retrieve(query=contrast_q, as_of_date="2026-06-30", top_k=3)
    top1_a = res_a[0] if res_a else {}
    doc_a = str(top1_a.get("doc_id", "") or top1_a.get("official_number", ""))
    art_a = str(top1_a.get("article_number", ""))
    pass_a = ("12_2025" in doc_a or "12/2025" in doc_a) and "108_2026" not in doc_a and "94_2026" not in doc_a

    print(f"[A] as_of_date = 2026-06-30:")
    print(f"    Expected: TT 12/2025 Điều 14 (NĐ 94/2026 & TT 108/2026 excluded)")
    print(f"    Found Top 1: {doc_a} | {art_a}")
    print(f"    Status: {'PASS 🟢' if pass_a else 'FAIL 🔴'}")

    # Mốc B: 2026-07-01
    res_b = retriever.retrieve(query=contrast_q, as_of_date="2026-07-01", top_k=3)
    top1_b = res_b[0] if res_b else {}
    doc_b = str(top1_b.get("doc_id", "") or top1_b.get("official_number", ""))
    art_b = str(top1_b.get("article_number", ""))
    pass_b = ("108_2026" in doc_b or "108/2026" in doc_b) and "15" in art_b and "35" not in art_b

    print(f"\n[B] as_of_date = 2026-07-01:")
    print(f"    Expected: TT 108/2026 Điều 15 (Correct provision, not Điều 35)")
    print(f"    Found Top 1: {doc_b} | {art_b}")
    print(f"    Status: {'PASS 🟢' if pass_b else 'FAIL 🔴'}")

    # 2. Key Traffic P1 Retrieval & Citation Tests
    print("\n[*] --- PART 2: KEY TRAFFIC P1 RETRIEVAL & CITATION VERIFICATION ---")
    p1_test_queries = [
        {
            "name": "TT 73/2024: Các trường hợp CSGT được dừng phương tiện",
            "query": "Các trường hợp Cảnh sát giao thông được dừng phương tiện giao thông đường bộ để kiểm soát theo Thông tư 73/2024/TT-BCA?",
            "expected_doc": "73_2024",
            "expected_art": "11"
        },
        {
            "name": "NĐ 89/2026: Điều kiện cấp giấy chứng nhận đủ điều kiện hoạt động kiểm định",
            "query": "Điều kiện cơ sở vật chất, dây chuyền kiểm định để cấp giấy chứng nhận cơ sở đăng kiểm theo Nghị định 89/2026/NĐ-CP?",
            "expected_doc": "89_2026",
            "expected_art": "7"
        },
        {
            "name": "TT 30/2026: Miễn kiểm định lần đầu cho xe cơ giới chưa qua sử dụng",
            "query": "Thủ tục lập hồ sơ phương tiện và cấp giấy chứng nhận kiểm định miễn kiểm định lần đầu theo Thông tư 30/2026/TT-BXD?",
            "expected_doc": "30_2026",
            "expected_art": "10"
        },
        {
            "name": "TT 65/2024: Kiểm tra kiến thức pháp luật phục hồi điểm GPLX",
            "query": "Nội dung và hình thức kiểm tra kiến thức pháp luật về trật tự an toàn giao thông đường bộ để phục hồi điểm giấy phép lái xe theo Thông tư 65/2024/TT-BCA?",
            "expected_doc": "65_2024",
            "expected_art": "6"
        }
    ]

    p1_results = []
    for tq in p1_test_queries:
        res = retriever.retrieve(query=tq["query"], top_k=3)
        matched_rank = None
        matched_item = None
        for rank, item in enumerate(res, start=1):
            doc = item.get("doc_id", "")
            art = str(item.get("article_number", ""))
            header = str(item.get("context_header", ""))
            pass_doc = tq["expected_doc"] in doc
            pass_art = tq["expected_art"] in art or tq["expected_art"] in header
            if pass_doc and (pass_art or not tq.get("expected_art")):
                matched_rank = rank
                matched_item = item
                break

        top1 = res[0] if res else {}
        top1_doc = top1.get("doc_id", "")
        top1_art = str(top1.get("article_number", ""))

        print(f"\nQuery: {tq['name']}")
        print(f"  Top 1: {top1_doc} | {top1_art}")
        if matched_rank:
            print(f"  Matched P1 Doc: Rank #{matched_rank} -> {matched_item.get('doc_id')} | {matched_item.get('article_number')}")
            print(f"  Status: PASS 🟢")
            p1_results.append(True)
        else:
            print(f"  Status: FAIL 🔴")
            p1_results.append(False)

    # Summary
    all_reg_pass = pass_a and pass_b and all(p1_results)
    print("\n" + "=" * 100)
    print(f" TASK 7 REGRESSION TEST VERDICT: {'PASS 🟢' if all_reg_pass else 'FAIL 🔴'}")
    print("=" * 100)

if __name__ == "__main__":
    run_regression_tests()
