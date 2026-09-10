import os
import sys
import json
import time
from pathlib import Path
from qdrant_client import QdrantClient

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.services.rag.embeddings import get_embedding_service

CLOUD_URL = "https://69f07c1e-2e88-452f-aded-6dd577ddbd9b.us-west-2-0.aws.cloud.qdrant.io"
CLOUD_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIiwic3ViamVjdCI6ImFwaS1rZXk6OTAxNjk0MzUtYjMwMS00YjAzLWFmMGYtYmYyZjc0MWE4MjYxIn0.bJ2YtMtnmDJXN4k3FKdduN_TsLARSOAvGjBRKW3p028"
COLLECTION_NAME = "vietlegal_articles"

PARSED_DIR = PROJECT_ROOT / "data" / "03_parsed" / "traffic_p0_batch"
SUMMARY_FILE = PARSED_DIR / "traffic_p0_batch_summary.json"

def main():
    print("=" * 80)
    print(" KIỂM THỬ THỰC TẾ: BENCHMARK RETRIEVAL TRÊN QDRANT CLOUD")
    print("=" * 80)

    with open(SUMMARY_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
        test_cases = data["benchmark_ground_truth"]

    from backend.app.services.rag.vector_store import QdrantVectorStore
    store = QdrantVectorStore(url=CLOUD_URL, api_key=CLOUD_API_KEY)
    embedding_service = get_embedding_service()

    results = []
    for tc in test_cases:
        query = tc["query"]
        expected_docs = tc["expected_documents"]
        tc_id = tc["test_case_id"]

        print(f"\n[*] Đang kiểm thử {tc_id} ({tc['category']}):")
        print(f"    Query: \"{query}\"")
        print(f"    Mốc áp dụng: {tc['as_of_date']}")

        query_vector = embedding_service.embed_texts([query])[0]
        search_results = store.search_similar(
            query_vector=query_vector,
            limit=5
        )

        hit = False
        top_match = None
        for rank, res in enumerate(search_results, 1):
            doc_id = str(res.get("doc_id", "") or "")
            off_num = str(res.get("official_number", "") or "")
            art = str(res.get("article_number", "") or res.get("article", "") or "")
            cl = str(res.get("clause_number", "") or res.get("clause", "") or "")
            title = str(res.get("doc_title", "") or "")
            score = round(res.get("score", 0.0), 4)

            # Check if expected doc is in top results
            match_found = any(exp in doc_id or exp in off_num or exp in title for exp in expected_docs)
            if match_found:
                hit = True
                if top_match is None:
                    top_match = (rank, off_num or title[:20], art, cl, score)

        if hit:
            print(f"    -> [HIT] Rank #{top_match[0]}: {top_match[1]} {top_match[2]} {top_match[3]} (Score: {top_match[4]})")
            results.append({"id": tc_id, "status": "HIT", "rank": top_match[0], "doc": top_match[1]})
        else:
            top_first = search_results[0] if search_results else {}
            first_doc = top_first.get("official_number") or top_first.get("doc_title", "Unknown")[:25]
            print(f"    -> [MISS] Top 1 trả về: {first_doc} {top_first.get('article_number')}")
            results.append({"id": tc_id, "status": "MISS", "rank": None, "doc": None})

    print("\n" + "=" * 80)
    print(" KẾT QUẢ ĐO LƯỜNG RETRIEVAL BENCHMARK")
    print("=" * 80)
    hits = sum(1 for r in results if r["status"] == "HIT")
    print(f" Tỷ lệ HIT RATE: {hits}/{len(results)} ({round(hits/len(results)*100, 1)}%)")
    for r in results:
        print(f" - {r['id']}: {r['status']} (Rank: {r['rank']} | Doc: {r['doc']})")
    print("=" * 80)

if __name__ == "__main__":
    main()
