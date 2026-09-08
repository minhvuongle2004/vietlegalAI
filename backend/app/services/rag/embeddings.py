import os
import sys
from typing import List, Optional
from abc import ABC, abstractmethod
from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Nạp .env có fallback
try:
    from dotenv import load_dotenv
    load_dotenv(PROJECT_ROOT / ".env")
except ImportError:
    env_path = PROJECT_ROOT / ".env"
    if env_path.exists():
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


class BaseEmbeddingService(ABC):
    """Giao diện chuẩn cho các dịch vụ trích xuất Vector Embeddings"""

    @abstractmethod
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Nhúng danh sách văn bản thành danh sách vectors"""
        pass

    @abstractmethod
    def embed_query(self, query: str) -> List[float]:
        """Nhúng câu hỏi truy vấn của người dùng thành 1 vector"""
        pass

    @property
    @abstractmethod
    def dimension(self) -> int:
        """Số chiều của vector (vector dimension)"""
        pass


class LocalSentenceTransformerEmbedding(BaseEmbeddingService):
    """
    Embedding sử dụng mô hình BAAI/bge-m3 1024 chiều chuyên cho Retrieval đa ngôn ngữ & tiếng Việt.
    Tự động tận dụng GPU (CUDA) nếu khả dụng.
    """

    def __init__(self, model_name: str = "BAAI/bge-m3"):
        from sentence_transformers import SentenceTransformer
        import torch

        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"[*] Đang tải mô hình Embedding cục bộ: '{model_name}' trên thiết bị: {device}...")
        try:
            self.model = SentenceTransformer(model_name, device=device)
            if device == "cuda":
                self.model.half()
            self._dim = self.model.get_sentence_embedding_dimension()
        except Exception as e:
            print(f"[!] Lỗi khi nạp '{model_name}': {e}")
            raise e

        print(f"[+] Mô hình BGE-M3 sẵn sàng trên {device} (FP16: {device == 'cuda'})! Vector dimension = {self._dim}")

    def embed_texts(self, texts: List[str], batch_size: int = 8) -> List[List[float]]:
        # Chuẩn hóa về list floats (batch_size an toàn cho VRAM GPU)
        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=True,
            normalize_embeddings=True,
        )
        return embeddings.tolist()

    def embed_query(self, query: str) -> List[float]:
        embedding = self.model.encode(query, normalize_embeddings=True)
        return embedding.tolist()

    @property
    def dimension(self) -> int:
        return self._dim


class OpenAIEmbeddingService(BaseEmbeddingService):
    """Dùng OpenAI API text-embedding-3-small (1536 dims) nếu có API key"""

    def __init__(self, api_key: Optional[str] = None, model: str = "text-embedding-3-small"):
        from openai import OpenAI

        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("Thiếu OPENAI_API_KEY")
        self.client = OpenAI(api_key=self.api_key)
        self.model = model
        self._dim = 1536

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        res = self.client.embeddings.create(input=texts, model=self.model)
        return [item.embedding for item in res.data]

    def embed_query(self, query: str) -> List[float]:
        res = self.client.embeddings.create(input=[query], model=self.model)
        return res.data[0].embedding

    @property
    def dimension(self) -> int:
        return self._dim


def get_embedding_service() -> BaseEmbeddingService:
    """Factory chọn bộ embedding phù hợp nhất"""
    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key and openai_key.startswith("sk-") and len(openai_key) > 20:
        print("[*] Phát hiện OPENAI_API_KEY, sử dụng OpenAI text-embedding-3-small")
        return OpenAIEmbeddingService(api_key=openai_key)

    # Mặc định dùng BAAI/bge-m3 (1024 dims) miễn phí cục bộ trên GPU/CPU
    local_model = os.getenv("EMBEDDING_MODEL_NAME", "BAAI/bge-m3")
    return LocalSentenceTransformerEmbedding(model_name=local_model)
