import os
import requests
from typing import Dict, Any
from fastapi import APIRouter
import torch

from backend.app.core.config import settings

router = APIRouter()


@router.get("/health", response_model=Dict[str, Any])
async def health_check() -> Dict[str, Any]:
    """
    Kiểm tra trạng thái sẵn sàng (Liveness & Readiness Probe) của toàn bộ hệ thống:
    - Trạng thái kết nối Database Supabase (PostgreSQL BM25)
    - Trạng thái kết nối Vector Store (Qdrant)
    - Thiết bị suy luận Reranker (CUDA FP16 / CPU / Remote GPU)
    - Nhà cung cấp LLM
    """
    components = {}
    is_healthy = True

    # 1. Kiểm tra Database Supabase
    try:
        supabase_url = os.getenv("SUPABASE_URL", "").rstrip("/")
        supabase_key = os.getenv("SUPABASE_KEY", "")
        if supabase_url and supabase_key:
            res = requests.get(
                f"{supabase_url}/rest/v1/legal_documents?select=id&limit=1",
                headers={"apikey": supabase_key, "Authorization": f"Bearer {supabase_key}"},
                timeout=2.0,
            )
            components["supabase"] = "connected" if res.status_code == 200 else f"degraded (HTTP {res.status_code})"
        else:
            components["supabase"] = "not_configured"
    except Exception as e:
        components["supabase"] = f"unreachable ({str(e)[:50]})"
        is_healthy = False

    # 2. Kiểm tra Qdrant Vector Store (tái sử dụng client sẵn có, tránh lock thư mục)
    try:
        from backend.app.api.v1.endpoints.chat import retriever
        cols = retriever.vector_store.client.get_collections().collections
        col_names = [c.name for c in cols]
        has_collection = retriever.vector_store.collection_name in col_names
        components["qdrant"] = f"connected (collection: {has_collection})"
    except Exception as e:
        components["qdrant"] = f"unreachable ({str(e)[:50]})"
        is_healthy = False

    # 3. Trạng thái Reranker & Phần cứng
    remote_reranker = os.getenv("RERANKER_SERVICE_URL")
    cuda_available = torch.cuda.is_available()
    gpu_name = torch.cuda.get_device_name(0) if cuda_available else None

    reranker_info = {
        "remote_gpu_url": remote_reranker if remote_reranker else "none (in-process fallback)",
        "cuda_available": cuda_available,
        "device": gpu_name if cuda_available else "CPU",
        "precision": "FP16" if cuda_available else "FP32",
    }
    components["reranker"] = reranker_info

    # 4. LLM Provider
    openai_key = os.getenv("OPENAI_API_KEY")
    gemini_key = os.getenv("GEMINI_API_KEY")
    if openai_key and len(openai_key) > 20:
        llm_provider = f"OpenAI ({settings.OPENAI_MODEL})"
    elif gemini_key and len(gemini_key) > 15:
        llm_provider = f"Google Gemini ({os.getenv('GEMINI_MODEL', 'gemini-3.5-flash-lite')})"
    else:
        llm_provider = "mock (demo mode)"
    components["llm_provider"] = llm_provider

    return {
        "status": "healthy" if is_healthy else "degraded",
        "service": settings.PROJECT_NAME,
        "environment": settings.ENVIRONMENT,
        "version": "1.0.0",
        "components": components,
    }
