import os
import sys
import json
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.services.rag.retriever import HybridRetriever
from backend.app.services.rag.reranker import get_reranker_service

QUERY = (
    "Tôi nghỉ việc sau 6 năm làm việc, trong đó có đóng BHXH và bảo hiểm thất nghiệp đầy đủ. "
    "Khi nghỉ việc, tôi có thể được hưởng những chế độ nào? "
    "Hãy phân biệt điều kiện hưởng BHXH một lần và trợ cấp thất nghiệp, đồng thời chỉ rõ căn cứ pháp lý của từng chế độ."
)

def debug_pipeline():
    print("=" * 80)
    print("   DEEP TRACE: CROSS-DOCUMENT RETRIEVAL PIPELINE")
    print(f"QUERY: {QUERY}")
    print("=" * 80)

    retriever = HybridRetriever()

    # 1. Tầng 1: Dense Retrieval (Qdrant)
    print("\n" + "-" * 80)
    print("1. TẦNG DENSE RETRIEVAL (Vector Qdrant - Top 20)")
    print("-" * 80)
    dense_hits = retriever._dense_search(QUERY, limit=20)
    found_d60_dense = False
    for rank, hit in enumerate(dense_hits, start=1):
        doc = hit.get("doc_id")
        art = hit.get("article_number")
        cl = hit.get("clause_number")
        title = hit.get("article_title")
        score = hit.get("score")
        is_d60 = (art == 60 and "bhxh" in doc)
        marker = " <=== [ĐIỀU 60 TẠI ĐÂY!]" if is_d60 else ""
        if is_d60:
            found_d60_dense = True
        print(f"  #{rank:02d} [Score: {score:.4f}] [{doc}] Điều {art} (Khoản {cl}): {title}{marker}")
    if not found_d60_dense:
        print("  ❌ KHÔNG TÌM THẤY Điều 60 trong Top 20 Dense!")

    # 2. Tầng 2: Sparse Retrieval (Supabase BM25)
    print("\n" + "-" * 80)
    print("2. TẦNG SPARSE RETRIEVAL (Supabase BM25 - Top 20)")
    print("-" * 80)
    sparse_hits = retriever._sparse_search_bm25(QUERY, limit=20)
    found_d60_sparse = False
    for rank, hit in enumerate(sparse_hits, start=1):
        doc = hit.get("doc_id")
        art = hit.get("article_number")
        title = hit.get("article_title")
        is_d60 = (art == 60 and "bhxh" in str(doc))
        marker = " <=== [ĐIỀU 60 TẠI ĐÂY!]" if is_d60 else ""
        if is_d60:
            found_d60_sparse = True
        print(f"  #{rank:02d} [{doc}] Điều {art}: {title}{marker}")
    if not found_d60_sparse:
        print("  ❌ KHÔNG TÌM THẤY Điều 60 trong Top 20 Sparse!")

    # 3. Tầng 3: RRF Fusion
    print("\n" + "-" * 80)
    print("3. TẦNG RRF FUSION (Hợp nhất Dense + Sparse)")
    print("-" * 80)
    candidate_limit = 20
    rrf_scores = {}
    doc_store = {}

    for rank, hit in enumerate(dense_hits, start=1):
        art_num = hit.get("article_number")
        if not art_num:
            continue
        doc_id = hit.get("doc_id", "bllđ_45_2019_qh14")
        key = f"{doc_id}_{art_num}"
        rrf_scores[key] = rrf_scores.get(key, 0.0) + (1.0 / (retriever.rrf_k + rank))
        if key not in doc_store:
            doc_store[key] = hit

    for rank, hit in enumerate(sparse_hits, start=1):
        art_num = hit.get("article_number")
        if not art_num:
            continue
        doc_id = hit.get("doc_id", "bllđ_45_2019_qh14")
        key = f"{doc_id}_{art_num}"
        rrf_scores[key] = rrf_scores.get(key, 0.0) + (1.0 / (retriever.rrf_k + rank))
        if key not in doc_store:
            doc_store[key] = hit

    sorted_articles = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)
    found_d60_rrf = False
    candidates_for_rerank = []
    for rank, (key, score) in enumerate(sorted_articles[:20], start=1):
        item = doc_store[key].copy()
        item["rrf_score"] = score
        candidates_for_rerank.append(item)
        is_d60 = ("bhxh" in key and "_60" in key)
        marker = " <=== [ĐIỀU 60 TẠI ĐÂY!]" if is_d60 else ""
        if is_d60:
            found_d60_rrf = True
        print(f"  #{rank:02d} [RRF Score: {score:.5f}] Key: {key} ({item.get('article_title')}){marker}")
    if not found_d60_rrf:
        print("  ❌ KHÔNG TÌM THẤY Điều 60 trong Top 20 RRF!")

    # 5. Tầng 5: End-to-End retrieve() với Balanced Representation
    print("\n" + "=" * 80)
    print("5. KẾT QUẢ END-TO-END: retriever.retrieve(QUERY, top_k=5, use_reranker=True)")
    print("=" * 80)
    final_hits = retriever.retrieve(QUERY, top_k=5, use_reranker=True)
    for rank, hit in enumerate(final_hits, start=1):
        doc = hit.get("doc_id")
        art = hit.get("article_number")
        title = hit.get("article_title")
        score = hit.get("rerank_score", hit.get("rrf_score"))
        is_d60 = (art == 60 and "bhxh" in doc)
        marker = " <=== [ĐIỀU 60 TẠI ĐÂY!]" if is_d60 else ""
        print(f"  #{rank:02d} [{doc}] Điều {art}: {title} (Score: {score}){marker}")

    retriever.close()

if __name__ == "__main__":
    debug_pipeline()

