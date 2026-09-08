import os
import requests
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from backend.app.core.auth import AuthenticatedUser, get_current_user

router = APIRouter()

SUPABASE_URL = os.getenv("SUPABASE_URL", "").rstrip("/")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")


def _get_supabase_headers():
    return {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation",
    }


class ConversationCreate(BaseModel):
    title: Optional[str] = Field("Tư vấn pháp lý mới", description="Tiêu đề cuộc trò chuyện")


class ConversationUpdate(BaseModel):
    title: str = Field(..., min_length=1, description="Tiêu đề mới")


@router.get("/conversations", response_model=List[Dict[str, Any]])
async def list_conversations(
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """Lấy danh sách các cuộc hội thoại của người dùng hiện tại"""
    endpoint = f"{SUPABASE_URL}/rest/v1/conversations?user_id=eq.{current_user.id}&order=updated_at.desc"
    res = requests.get(endpoint, headers=_get_supabase_headers(), timeout=5.0)
    if res.status_code != 200:
        raise HTTPException(status_code=500, detail="Không thể tải danh sách hội thoại từ cơ sở dữ liệu")
    return res.json()


@router.post("/conversations", status_code=status.HTTP_201_CREATED)
async def create_conversation(
    payload: ConversationCreate,
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """Tạo mới một cuộc hội thoại liên kết với tài khoản người dùng"""
    endpoint = f"{SUPABASE_URL}/rest/v1/conversations"
    data = {
        "title": payload.title,
        "user_id": current_user.id,
    }
    res = requests.post(endpoint, json=data, headers=_get_supabase_headers(), timeout=5.0)
    if res.status_code not in (200, 201):
        raise HTTPException(status_code=500, detail="Lỗi khi tạo cuộc hội thoại mới")
    results = res.json()
    return results[0] if results else data


@router.get("/conversations/{conversation_id}")
async def get_conversation_details(
    conversation_id: str,
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """Lấy chi tiết một cuộc hội thoại kèm toàn bộ lịch sử tin nhắn"""
    # 1. Kiểm tra quyền sở hữu
    conv_endpoint = f"{SUPABASE_URL}/rest/v1/conversations?id=eq.{conversation_id}&user_id=eq.{current_user.id}"
    conv_res = requests.get(conv_endpoint, headers=_get_supabase_headers(), timeout=5.0)
    if conv_res.status_code != 200 or not conv_res.json():
        raise HTTPException(status_code=404, detail="Không tìm thấy cuộc hội thoại hoặc bạn không có quyền truy cập")

    conversation = conv_res.json()[0]

    # 2. Lấy danh sách tin nhắn
    msg_endpoint = f"{SUPABASE_URL}/rest/v1/messages?conversation_id=eq.{conversation_id}&order=created_at.asc"
    msg_res = requests.get(msg_endpoint, headers=_get_supabase_headers(), timeout=5.0)
    messages = msg_res.json() if msg_res.status_code == 200 else []

    conversation["messages"] = messages
    return conversation


@router.patch("/conversations/{conversation_id}")
async def rename_conversation(
    conversation_id: str,
    payload: ConversationUpdate,
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """Đổi tên tiêu đề của cuộc hội thoại"""
    endpoint = f"{SUPABASE_URL}/rest/v1/conversations?id=eq.{conversation_id}&user_id=eq.{current_user.id}"
    res = requests.patch(
        endpoint,
        json={"title": payload.title, "updated_at": "now()"},
        headers=_get_supabase_headers(),
        timeout=5.0,
    )
    if res.status_code != 200 or not res.json():
        raise HTTPException(status_code=404, detail="Không tìm thấy cuộc hội thoại để cập nhật")
    return res.json()[0]


@router.delete("/conversations/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """Xóa vĩnh viễn cuộc hội thoại và toàn bộ tin nhắn bên trong"""
    endpoint = f"{SUPABASE_URL}/rest/v1/conversations?id=eq.{conversation_id}&user_id=eq.{current_user.id}"
    res = requests.delete(endpoint, headers=_get_supabase_headers(), timeout=5.0)
    if res.status_code not in (200, 204):
        raise HTTPException(status_code=500, detail="Không thể xóa cuộc hội thoại")
    return {"status": "success", "message": "Đã xóa cuộc hội thoại thành công"}
