import json
import time
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from sse_starlette.sse import EventSourceResponse

from backend.app.services.rag.retriever import HybridRetriever
from backend.app.services.rag.generator import LegalAnswerGenerator

router = APIRouter()

# Khởi tạo singleton services
retriever = HybridRetriever()
generator = LegalAnswerGenerator()


class ChatMessageRequest(BaseModel):
    query: str = Field(..., description="Câu hỏi pháp lý của người dùng", min_length=2)
    conversation_id: Optional[str] = Field(None, description="ID phiên hội thoại nếu có")
    top_k: int = Field(3, description="Số lượng điều luật liên quan cần trích xuất")
    use_reranker: bool = Field(False, description="Kích hoạt mô hình BGE-Reranker trên GPU")
    as_of_date: Optional[str] = Field(None, description="Thời điểm áp dụng pháp luật (YYYY-MM-DD), mặc định auto-infer hoặc hiện tại")


class CitationItem(BaseModel):
    article_number: int
    article_title: str
    chapter: Optional[str] = None
    context_header: Optional[str] = None
    excerpt: str


import os
import requests
from backend.app.core.auth import AuthenticatedUser, get_current_user_optional
from fastapi import Depends

SUPABASE_URL = os.getenv("SUPABASE_URL", "").rstrip("/")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")


def _save_message_to_db(conversation_id: str, role: str, content: str, citations: Optional[List[Dict[str, Any]]] = None, latency_ms: int = 0):
    if not SUPABASE_URL or not SUPABASE_KEY or not conversation_id:
        return
    
    # Kiểm tra xem conversation_id có phải là UUID hợp lệ của Supabase không
    import uuid
    try:
        uuid.UUID(str(conversation_id))
    except (ValueError, AttributeError):
        return

    try:
        endpoint = f"{SUPABASE_URL}/rest/v1/messages"
        headers = {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "application/json",
        }
        data = {
            "conversation_id": conversation_id,
            "role": role,
            "content": content,
            "citations": citations or [],
            "latency_ms": latency_ms,
        }
        requests.post(endpoint, json=data, headers=headers, timeout=5.0)

        # Cập nhật updated_at của conversation
        requests.patch(
            f"{SUPABASE_URL}/rest/v1/conversations?id=eq.{conversation_id}",
            json={"updated_at": "now()"},
            headers=headers,
            timeout=5.0,
        )
    except Exception as e:
        print(f"[!] Lỗi khi lưu tin nhắn vào database: {e}")


@router.post("/chat/completions")
async def chat_completions(
    request: ChatMessageRequest,
    current_user: Optional[AuthenticatedUser] = Depends(get_current_user_optional),
):
    """
    Core RAG Endpoint: Nhận câu hỏi, tìm kiếm kết hợp Hybrid Search,
    và trả về luồng phản hồi thời gian thực qua Server-Sent Events (SSE).
    Đồng thời tự động đồng bộ tin nhắn vào Supabase nếu có conversation_id.
    """
    start_time = time.time()
    query = request.query.strip()

    if not query:
        raise HTTPException(status_code=400, detail="Câu hỏi không được để trống")

    # Lưu tin nhắn của user nếu có conversation_id
    if request.conversation_id:
        _save_message_to_db(
            conversation_id=request.conversation_id,
            role="user",
            content=query,
        )

    # 1. Truy xuất căn cứ pháp lý liên quan nhất bằng Hybrid Search (+ Reranker tùy chọn)
    retrieved_chunks = retriever.retrieve(
        query=query,
        top_k=request.top_k,
        use_reranker=request.use_reranker,
        as_of_date=request.as_of_date,
    )

    citations = []
    for c in retrieved_chunks:
        citations.append({
            "doc_id": c.get("doc_id", "bllđ_45_2019_qh14"),
            "doc_title": c.get("doc_title", "Bộ luật Lao động 2019"),
            "article_number": c.get("article_number"),
            "article_title": c.get("article_title"),
            "chapter": c.get("chapter"),
            "context_header": c.get("context_header"),
            "excerpt": c.get("content", "")[:250] + "...",
        })

    # 2. Generator tạo luồng SSE
    async def event_generator():
        # Gửi sự kiện mở đầu với danh sách trích dẫn (Citations)
        yield {
            "event": "citations",
            "data": json.dumps({"citations": citations}, ensure_ascii=False),
        }

        # Gửi luồng token từ LLM
        full_text = ""
        async for token in generator.generate_answer_stream(query=query, retrieved_chunks=retrieved_chunks):
            full_text += token
            yield {
                "event": "token",
                "data": json.dumps({"token": token}, ensure_ascii=False),
            }

        # Gửi sự kiện kết thúc kèm thông tin độ trễ
        latency_ms = int((time.time() - start_time) * 1000)

        # Lưu tin nhắn AI vào database sau khi stream xong
        if request.conversation_id:
            _save_message_to_db(
                conversation_id=request.conversation_id,
                role="assistant",
                content=full_text,
                citations=citations,
                latency_ms=latency_ms,
            )

        yield {
            "event": "done",
            "data": json.dumps({"status": "completed", "latency_ms": latency_ms}, ensure_ascii=False),
        }

    return EventSourceResponse(event_generator())
