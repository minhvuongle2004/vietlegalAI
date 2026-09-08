from fastapi import APIRouter
from typing import Dict

router = APIRouter()


@router.get("/health", response_model=Dict[str, str])
async def health_check() -> Dict[str, str]:
    """Kiểm tra trạng thái sẵn sàng của Backend API"""
    return {
        "status": "healthy",
        "service": "VietLegal AI Backend Service",
        "version": "1.0.0",
    }
