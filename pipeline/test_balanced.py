import os
import sys
import re
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

retriever = HybridRetriever()
print("1. Sub queries:")
sub_configs = retriever._decompose_query(QUERY)
for c in sub_configs:
    print("  -", c["category"], ":", c["sub_query"])

# Lấy sparse
sparse_hits = retriever._sparse_search_bm25(QUERY, limit=15)
print(f"\n2. Sparse hits ({len(sparse_hits)}):")
for h in sparse_hits:
    print(f"  [{h.get('doc_id')}] D{h.get('article_number')}: {h.get('article_title')} (len: {len(h.get('content',''))})")

# Lấy dense từ các sub-queries
dense_hits = []
for c in sub_configs:
    hits = retriever._dense_search(c["sub_query"], limit=10)
    for h in hits:
        dense_hits.append(h)

# Gộp doc_store: luôn ưu tiên chunk có nội dung dài hơn / đầy đủ hơn
doc_store = {}
for h in sparse_hits + dense_hits:
    doc_id = h.get("doc_id")
    art_num = h.get("article_number")
    if not art_num:
        continue
    key = f"{doc_id}_{art_num}"
    if key not in doc_store or len(h.get("content", "")) > len(doc_store[key].get("content", "")):
        doc_store[key] = h

print(f"\n3. Unique candidates in doc_store: {len(doc_store)}")
for k, v in doc_store.items():
    if "60" in k or "49" in k or "50" in k or "58" in k:
        print(f"  {k}: {v.get('article_title')} (len: {len(v.get('content',''))})")

# Rerank
reranker = get_reranker_service()
candidates = list(doc_store.values())
reranked = reranker.rerank(QUERY, candidates, top_k=len(candidates))

print("\n4. Top 10 sau Reranker:")
for r, it in enumerate(reranked[:10], 1):
    sc = it.get("rerank_score")
    doc = it.get("doc_id")
    art = it.get("article_number")
    title = it.get("article_title")
    print(f"  #{r:02d} [Score: {sc:.5f}] [{doc}] Điều {art}: {title}")

retriever.close()
