import os
import requests
from typing import Optional, Dict, Any
from fastapi import Header, HTTPException, status
from pydantic import BaseModel

SUPABASE_URL = os.getenv("SUPABASE_URL", "").rstrip("/")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")


class AuthenticatedUser(BaseModel):
    id: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    provider: Optional[str] = "google"


def _verify_supabase_token(token: str) -> Optional[AuthenticatedUser]:
    """
    Xác thực token JWT với dịch vụ Supabase Auth.
    Gọi GET /auth/v1/user để lấy thông tin tài khoản người dùng từ Google OAuth.
    """
    if not SUPABASE_URL or not SUPABASE_KEY or not token:
        return None

    try:
        endpoint = f"{SUPABASE_URL}/auth/v1/user"
        headers = {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {token}",
        }
        res = requests.get(endpoint, headers=headers, timeout=5.0)
        if res.status_code == 200:
            user_data = res.json()
            user_meta = user_data.get("user_metadata", {})
            full_name = (
                user_meta.get("full_name")
                or user_meta.get("name")
                or (user_data.get("email", "").split("@")[0] if user_data.get("email") else "Người dùng")
            )
            avatar_url = user_meta.get("avatar_url") or user_meta.get("picture")

            return AuthenticatedUser(
                id=user_data.get("id"),
                email=user_data.get("email"),
                full_name=full_name,
                avatar_url=avatar_url,
                provider=user_data.get("app_metadata", {}).get("provider", "google"),
            )
        return None
    except Exception as e:
        print(f"[!] Lỗi khi xác thực token Supabase: {e}")
        return None


async def get_current_user_optional(
    authorization: Optional[str] = Header(None),
) -> Optional[AuthenticatedUser]:
    """Dependency trích xuất user nếu có token (cho phép cả khách vãng lai)"""
    if not authorization or not authorization.startswith("Bearer "):
        return None

    token = authorization.replace("Bearer ", "").strip()
    return _verify_supabase_token(token)


async def get_current_user(
    authorization: Optional[str] = Header(None),
) -> AuthenticatedUser:
    """Dependency bắt buộc phải đăng nhập (dành cho API quản lý hội thoại cá nhân)"""
    user = await get_current_user_optional(authorization)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Phiên đăng nhập không hợp lệ hoặc đã hết hạn. Vui lòng đăng nhập lại bằng Google.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user
