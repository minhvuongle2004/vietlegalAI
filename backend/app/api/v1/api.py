from fastapi import APIRouter
from backend.app.api.v1.endpoints import health, chat, legal, conversations

api_router = APIRouter()
api_router.include_router(health.router, tags=["Health"])
api_router.include_router(chat.router, tags=["Chat"])
api_router.include_router(legal.router, tags=["Legal"])
api_router.include_router(conversations.router, tags=["Conversations"])

