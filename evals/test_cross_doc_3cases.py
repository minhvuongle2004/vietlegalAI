"""
TC-17 Pipeline Debug: Tìm Điều 47 BLLĐ ở từng stage.
Gọi /api/v1/legal/debug-retrieve để xem dense/sparse results riêng biệt.
"""
import requests
import json
import sys

BASE = "http://127.0.0.1:8000/api/v1/legal/debug-retrieve"

query = "Doanh nghiệp sáp nhập dẫn đến dôi dư lao động và phải cho 10 người thôi việc. Theo BLLĐ 2019 và Nghị định 145/2020/NĐ-CP, doanh nghiệp phải xây dựng phương án sử dụng lao động ra sao và chi trả trợ cấp mất việc làm với mức tối thiểu là bao nhiêu?"

print("=" * 85)
print("  TC-17 PIPELINE DEBUG: Tìm Điều 47 BLLĐ ở từng stage")
print("=" * 85)

resp = requests.get(BASE, params={"q": query}, timeout=60)
data = resp.json()

def print_stage(name, hits):
    print(f"\n  --- {name} ({len(hits)} results) ---")
    d47_rank = None
    for h in hits:
        marker = ""
        if h["article_number"] == 47 and "bll" in h["doc_id"].lower():
            marker = " ◄◄◄ Đ47 BLLĐ"
            d47_rank = h["rank"]
        elif h["article_number"] == 44 and "bll" in h["doc_id"].lower():
            marker = " ◄ Đ44"
        elif h["article_number"] == 46 and "bll" in h["doc_id"].lower():
            marker = " ◄ Đ46"
        elif h["article_number"] == 43 and "bll" in h["doc_id"].lower():
            marker = " ◄ Đ43"
        elif h["article_number"] == 8 and "145" in h["doc_id"]:
            marker = " ◄ Đ8 NĐ145"
        
        score = h.get("score", 0)
        score_str = f"{score:.6f}" if isinstance(score, float) else str(score)
        title = h.get("title", "?")[:55]
        print(f"    [{h['rank']:>2}] {h['doc_id']:<25} Đ{str(h['article_number']):<5} {score_str:<12} {title}{marker}")
    
    if d47_rank:
        print(f"  ✅ Điều 47 FOUND at rank #{d47_rank}")
    else:
        print(f"  ❌ Điều 47 NOT FOUND in this stage")
    return d47_rank

# Decomposition
print(f"\n  Decomposition:")
for d in data["decomposition"]:
    print(f"    → {d['category']} → doc_keyword={d['doc_keyword']}")

# Stage 1: Dense - Original Query
d47_dense_orig = print_stage("Dense Search: Query Gốc", data["dense_original_query"])

# Stage 2: Dense - Sub-queries
for cat, hits in data["dense_sub_queries"].items():
    d47_sub = print_stage(f"Dense Search: Sub-query '{cat}'", hits)

# Stage 3: Sparse - Original Query
d47_sparse = print_stage("Sparse Search: Query Gốc", data["sparse_original_query"])

# Summary
print(f"\n{'='*85}")
print(f"  SUMMARY: Điều 47 BLLĐ xuất hiện ở đâu?")
print(f"{'='*85}")
print(f"  Dense query gốc         → {'Rank #' + str(d47_dense_orig) if d47_dense_orig else '❌ ABSENT'}")
for cat, hits in data["dense_sub_queries"].items():
    d47_r = None
    for h in hits:
        if h["article_number"] == 47 and "bll" in h["doc_id"].lower():
            d47_r = h["rank"]
    print(f"  Dense sub '{cat}' → {'Rank #' + str(d47_r) if d47_r else '❌ ABSENT'}")
print(f"  Sparse query gốc        → {'Rank #' + str(d47_sparse) if d47_sparse else '❌ ABSENT'}")

# Final Top-5 after Full Pipeline (Balanced Allocation + Reranker)
final_top5 = data.get("final_top5", [])
print(f"\n{'='*85}")
print("  TOP-5 CUỐI CÙNG (Sau RRF + Reranker + Balanced Allocation):")
print(f"{'='*85}")
print(f"  {'rank':<5} | {'doc_id':<22} | {'article_number':<14} | {'reranker_score':<15} | {'title'}")
print(f"  {'-'*5}-|-{'-'*22}-|-{'-'*14}-|-{'-'*15}-|-{'-'*25}")

found_d47_final = False
for h in final_top5:
    rank = h["rank"]
    doc_id = h["doc_id"]
    art = h["article_number"]
    r_score = h["reranker_score"]
    title = h["title"][:50]
    marker = ""
    if art == 47 and "bll" in doc_id.lower():
        marker = " ◄◄◄ Đ47 BLLĐ"
        found_d47_final = True
    elif art == 44 and "bll" in doc_id.lower():
        marker = " ◄ Đ44 BLLĐ"
    elif art == 8 and "145" in doc_id.lower():
        marker = " ◄ Đ8 NĐ145"
    print(f"  {rank:<5} | {doc_id:<22} | {art:<14} | {r_score:<15.6f} | {title}{marker}")

print(f"{'='*85}")
if found_d47_final:
    print("  ✅ KẾT QUẢ: Điều 47 BLLĐ ĐÃ lọt vào Top-5 cuối cùng!")
else:
    print("  ❌ KẾT QUẢ: Điều 47 BLLĐ CHƯA lọt vào Top-5 cuối cùng!")
print(f"{'='*85}")
