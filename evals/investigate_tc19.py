import os
import sys
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent.parent
# Look for workspace root: d:\Đi làm\VietLegal AI
workspace_root = Path("d:/Đi làm/VietLegal AI")
if str(workspace_root) not in sys.path:
    sys.path.insert(0, str(workspace_root))

from dotenv import load_dotenv
load_dotenv(workspace_root / ".env")

from backend.app.services.rag.retriever import HybridRetriever
from backend.app.services.rag.reranker import get_reranker_service

tc19_query = "Người lao động làm việc từ ngày 01/01/2018 đến 30/09/2023 thì chấm dứt HĐLĐ hợp pháp. Trong suốt thời gian này người lao động không thuộc diện tham gia BHTN. Hỏi thời gian tính trợ cấp thôi việc là bao nhiêu năm?"

print("="*80)
print(f"QUERY TC-19: {tc19_query}")
print("="*80)

retriever = HybridRetriever()

# Step 1: Query Decomposition check
sub_queries = retriever._decompose_query(tc19_query)
print("\n--- 1. DECOMPOSE QUERY ---")
print(json.dumps(sub_queries, ensure_ascii=False, indent=2))

# Step 2: Dense Search on original query and sub-queries
print("\n--- 2. DENSE SEARCH (Original Query, top 20) ---")
dense_hits = retriever._dense_search(tc19_query, limit=20)
for idx, hit in enumerate(dense_hits, 1):
    doc_id = hit.get("doc_id")
    art_num = hit.get("article_number")
    title = hit.get("article_title")
    score = hit.get("score")
    match_marker = " <=== [TARGET ĐIỀU 8 NĐ 145]" if ("145" in str(doc_id) and str(art_num) == "8") else (" <=== [ĐIỀU 46 BLLĐ]" if ("bll" in str(doc_id).lower() and str(art_num) == "46") else "")
    print(f"Rank {idx:2d} | Score: {score:.4f} | doc_id: {doc_id} | Điều {art_num}: {title}{match_marker}")

# Step 3: Sparse Search
print("\n--- 3. SPARSE SEARCH (BM25 / Supabase) ---")
sparse_hits = retriever._sparse_search_bm25(tc19_query, limit=20)
for idx, hit in enumerate(sparse_hits, 1):
    doc_id = hit.get("doc_id")
    art_num = hit.get("article_number")
    title = hit.get("article_title")
    match_marker = " <=== [TARGET ĐIỀU 8 NĐ 145]" if ("145" in str(doc_id) and str(art_num) == "8") else (" <=== [ĐIỀU 46 BLLĐ]" if ("bll" in str(doc_id).lower() and str(art_num) == "46") else "")
    print(f"Rank {idx:2d} | doc_id: {doc_id} | Điều {art_num}: {title}{match_marker}")

# Step 4: Full Retrieval Top 10 WITHOUT Reranker (RRF Pool)
print("\n--- 4. RETRIEVE TOP 10 (use_reranker=False, RRF only) ---")
rrf_results = retriever.retrieve(tc19_query, top_k=10, use_reranker=False)
for idx, hit in enumerate(rrf_results, 1):
    doc_id = hit.get("doc_id")
    art_num = hit.get("article_number")
    title = hit.get("article_title")
    score = hit.get("rrf_score", 0.0)
    match_marker = " <=== [TARGET ĐIỀU 8 NĐ 145]" if ("145" in str(doc_id) and str(art_num) == "8") else (" <=== [ĐIỀU 46 BLLĐ]" if ("bll" in str(doc_id).lower() and str(art_num) == "46") else "")
    print(f"Rank {idx:2d} | RRF Score: {score:.5f} | doc_id: {doc_id} | Điều {art_num}: {title}{match_marker}")

# Step 5: Full Retrieval Top 10 WITH Reranker
print("\n--- 5. RETRIEVE TOP 10 (use_reranker=True) ---")
rerank_results = retriever.retrieve(tc19_query, top_k=10, use_reranker=True)
for idx, hit in enumerate(rerank_results, 1):
    doc_id = hit.get("doc_id")
    art_num = hit.get("article_number")
    title = hit.get("article_title")
    score = hit.get("rerank_score", hit.get("rrf_score", 0.0))
    match_marker = " <=== [TARGET ĐIỀU 8 NĐ 145]" if ("145" in str(doc_id) and str(art_num) == "8") else (" <=== [ĐIỀU 46 BLLĐ]" if ("bll" in str(doc_id).lower() and str(art_num) == "46") else "")
    print(f"Rank {idx:2d} | Score: {score} | doc_id: {doc_id} | Điều {art_num}: {title}{match_marker}")

# Step 6: Check directly if Điều 8 NĐ 145 exists in Qdrant or Supabase
print("\n--- 6. DIRECT CHECK: Điều 8 NĐ 145 in Supabase / Qdrant ---")
import requests
headers = {"apikey": os.getenv("SUPABASE_KEY", ""), "Authorization": f"Bearer {os.getenv('SUPABASE_KEY', '')}"}
res = requests.get(f"{os.getenv('SUPABASE_URL')}/rest/v1/legal_articles?document_id=ilike.*145*&article_number=eq.8", headers=headers)
if res.status_code == 200:
    data = res.json()
    print(f"Supabase found {len(data)} records for Điều 8 NĐ 145:")
    for d in data:
        print(f"  - document_id: {d.get('document_id')}, Điều {d.get('article_number')}: {d.get('article_title')}")
        print(f"    Excerpt: {d.get('full_text', '')[:200]}...")
else:
    print(f"Supabase query failed: {res.status_code}")
