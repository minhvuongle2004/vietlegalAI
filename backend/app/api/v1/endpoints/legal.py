import os
import requests
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

router = APIRouter()


@router.get("/legal/articles/{article_number}")
def get_article(article_number: int, doc_id: Optional[str] = Query(None, description="Mã định danh văn bản")):
    """Lấy chi tiết toàn văn một Điều luật để người dùng kiểm chứng chéo"""
    url = os.getenv("SUPABASE_URL", "").rstrip("/")
    key = os.getenv("SUPABASE_KEY", "")

    if not url or not key:
        raise HTTPException(status_code=500, detail="Chưa cấu hình Supabase")

    headers = {"apikey": key, "Authorization": f"Bearer {key}"}
    endpoint = f"{url}/rest/v1/legal_articles"
    params = {
        "article_number": f"eq.{article_number}",
        "select": "id,document_id,article_number,article_title,full_text,chapter_info,status",
        "limit": "1",
    }
    if doc_id:
        params["document_id"] = f"eq.{doc_id}"

    res = requests.get(endpoint, headers=headers, params=params, timeout=5)
    if res.status_code == 200 and res.json():
        return res.json()[0]

    raise HTTPException(status_code=404, detail=f"Không tìm thấy Điều {article_number}")


@router.get("/legal/search")
def search_articles(q: str = Query(..., min_length=2, description="Từ khóa tra cứu")):
    """Tìm kiếm nhanh Điều luật theo từ khóa qua Supabase Full-Text Search"""
    url = os.getenv("SUPABASE_URL", "").rstrip("/")
    key = os.getenv("SUPABASE_KEY", "")

    if not url or not key:
        raise HTTPException(status_code=500, detail="Chưa cấu hình Supabase")

    words = [w.strip() for w in q.split() if len(w.strip()) > 1]
    ts_query = " & ".join(words[:4])

    headers = {"apikey": key, "Authorization": f"Bearer {key}"}
    endpoint = f"{url}/rest/v1/legal_articles"
    params = {
        "search_vector": f"wfts.{ts_query}",
        "select": "article_number,article_title,chapter_info,full_text",
        "limit": "10",
    }

    res = requests.get(endpoint, headers=headers, params=params, timeout=5)
    if res.status_code == 200:
        return res.json()

    return []


@router.get("/legal/retrieve")
def retrieve_legal_chunks(
    q: str = Query(..., min_length=2, description="Câu hỏi pháp lý"),
    top_k: int = 5,
    use_reranker: bool = Query(False, description="Kích hoạt Cross-Encoder Reranker"),
):
    """Truy xuất trực tiếp các căn cứ pháp lý liên quan qua Hybrid Search (RRF) có hỗ trợ Reranker"""
    from backend.app.api.v1.endpoints.chat import retriever
    return retriever.retrieve(query=q, top_k=top_k, use_reranker=use_reranker)


@router.get("/legal/debug-retrieve")
def debug_retrieve_stages(
    q: str = Query(..., min_length=2, description="Câu hỏi pháp lý"),
):
    """[TEMPORARY DEBUG] Expose individual pipeline stages for TC-17 diagnosis."""
    from backend.app.api.v1.endpoints.chat import retriever

    # 1. Decomposition
    sub_configs = retriever._decompose_query(q)

    # 2. Dense search - original query
    dense_original = retriever._dense_search(q, limit=20)

    # 3. Dense search - each sub-query
    dense_sub = {}
    for cfg in sub_configs:
        cat = cfg["category"]
        dense_sub[cat] = retriever._dense_search(cfg["sub_query"], limit=20)

    # 4. Sparse search - original query
    sparse_original = retriever._sparse_search_bm25(q, limit=20)

    # 5. Full pipeline retrieve (RRF + Reranker + Balanced Allocation)
    final_top5 = retriever.retrieve(q, top_k=5, use_reranker=True)

    def _simplify(hits):
        return [
            {
                "rank": i + 1,
                "doc_id": h.get("doc_id", "?"),
                "article_number": h.get("article_number"),
                "score": round(h.get("score", h.get("rrf_score", 0)), 6) if isinstance(h.get("score", h.get("rrf_score", 0)), float) else 0,
                "title": (h.get("article_title") or h.get("context_header") or "?")[:70],
            }
            for i, h in enumerate(hits[:20])
        ]

    def _simplify_final(hits):
        return [
            {
                "rank": i + 1,
                "doc_id": h.get("doc_id", "?"),
                "article_number": h.get("article_number"),
                "reranker_score": round(float(h.get("rerank_score", 0)), 6) if h.get("rerank_score") is not None else 0,
                "title": (h.get("article_title") or h.get("context_header") or "?")[:70],
            }
            for i, h in enumerate(hits)
        ]

    return {
        "decomposition": [{"category": c["category"], "doc_keyword": c["doc_keyword"]} for c in sub_configs],
        "dense_original_query": _simplify(dense_original),
        "dense_sub_queries": {cat: _simplify(hits) for cat, hits in dense_sub.items()},
        "sparse_original_query": _simplify(sparse_original),
        "final_top5": _simplify_final(final_top5),
    }
