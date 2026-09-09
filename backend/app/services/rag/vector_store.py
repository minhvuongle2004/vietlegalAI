import os
import sys
import uuid
from typing import List, Dict, Any, Optional
from pathlib import Path
from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

from pipeline.models import LegalChunkPayload


class QdrantVectorStore:
    """
    Trình quản lý cơ sở dữ liệu Vector (Qdrant Vector Store).
    Hỗ trợ kết nối Docker/Cloud hoặc tự động Fallback sang Embedded Storage trên đĩa.
    """

    def __init__(
        self,
        collection_name: str = "vietlegal_articles",
        url: Optional[str] = None,
        host: Optional[str] = None,
        port: int = 6333,
        api_key: Optional[str] = None,
    ):
        self.collection_name = collection_name
        self.url = url or os.getenv("QDRANT_URL")
        self.host = host or os.getenv("QDRANT_HOST", "localhost")
        self.port = int(os.getenv("QDRANT_PORT", str(port)))
        self.api_key = api_key or os.getenv("QDRANT_API_KEY")

        self.client = self._init_client()

    def _init_client(self) -> QdrantClient:
        is_production = os.getenv("ENVIRONMENT", "development").lower() == "production"

        # 1. Kết nối qua QDRANT_URL (Dành cho Qdrant Cloud hoặc Remote Service)
        if self.url:
            try:
                client = QdrantClient(
                    url=self.url,
                    api_key=self.api_key if self.api_key else None,
                    timeout=5.0,
                )
                client.get_collections()
                print(f"[+] Kết nối Qdrant Cloud thành công: {self.url}")
                return client
            except Exception as e:
                print(f"[!] Lỗi kết nối Qdrant URL ({self.url}): {e}")
                if is_production:
                    raise RuntimeError(f"Không thể kết nối Qdrant Cloud trong môi trường Production: {e}")

        # 2. Nếu ở môi trường local development và có sẵn thư mục data/qdrant_storage, ưu tiên dùng Local Storage
        local_storage = PROJECT_ROOT / "data" / "qdrant_storage"
        if not is_production and not self.api_key and local_storage.exists() and any(local_storage.iterdir()):
            try:
                print(f"[*] Sử dụng Qdrant Local Embedded Storage tại: {local_storage}")
                return QdrantClient(path=str(local_storage))
            except Exception as lock_err:
                print(f"[!] Local storage đã bị tiến trình khác chiếm quyền lock: {lock_err}. Tiếp tục thử kết nối Server...")

        # 3. Thử kết nối qua Host & Port (Docker / Self-hosted Qdrant)
        try:
            client = QdrantClient(
                host=self.host,
                port=self.port,
                api_key=self.api_key if self.api_key else None,
                timeout=3.0,
            )
            client.get_collections()
            print(f"[+] Kết nối Qdrant Host:Port thành công ({self.host}:{self.port})")
            return client
        except Exception as e:
            if is_production:
                raise RuntimeError(
                    f"Không thể kết nối Qdrant Server ({self.host}:{self.port}) trong môi trường Production: {e}. "
                    f"Vui lòng cấu hình QDRANT_URL hoặc QDRANT_HOST chính xác để tránh lỗi file lock."
                )
            print(f"[!] Qdrant Server không khả dụng, fallback sang Local Embedded Storage: {e}")
            try:
                local_storage.mkdir(parents=True, exist_ok=True)
                return QdrantClient(path=str(local_storage))
            except Exception as final_e:
                print(f"[!] Local Storage đang bị tiến trình khác chiếm quyền lock ({final_e}). Tạm thời sử dụng In-Memory client cho tiến trình phụ...")
                return QdrantClient(":memory:")

    def ensure_collection(self, vector_size: int, recreate: bool = False):
        """Khởi tạo collection nếu chưa tồn tại hoặc tái tạo mới"""
        collections = self.client.get_collections().collections
        collection_names = [c.name for c in collections]

        if self.collection_name in collection_names:
            if recreate:
                print(f"[*] Đang xóa và tạo lại collection '{self.collection_name}'...")
                self.client.delete_collection(self.collection_name)
            else:
                print(f"[+] Collection '{self.collection_name}' đã sẵn sàng.")
                return

        print(f"[*] Đang tạo mới collection '{self.collection_name}' (vector size = {vector_size}, distance = Cosine)...")
        self.client.create_collection(
            collection_name=self.collection_name,
            vectors_config=qmodels.VectorParams(
                size=vector_size,
                distance=qmodels.Distance.COSINE,
            ),
        )

        # Tạo Index cho Payload để lọc cực nhanh (Metadata Filtering)
        for field in ["doc_id", "article_number", "status"]:
            try:
                self.client.create_payload_index(
                    collection_name=self.collection_name,
                    field_name=field,
                    field_schema=qmodels.PayloadSchemaType.KEYWORD,
                )
            except Exception:
                pass

        print(f"[+] Đã tạo xong collection '{self.collection_name}' kèm bộ chỉ mục Metadata!")

    def insert_chunks(
        self,
        chunks: List[LegalChunkPayload],
        embeddings: List[List[float]],
        batch_size: int = 50,
    ) -> int:
        """Nạp danh sách Chunks và Vectors vào Qdrant"""
        if len(chunks) != len(embeddings):
            raise ValueError("Số lượng chunks và embeddings phải bằng nhau!")

        points = []
        for chunk, vector in zip(chunks, embeddings):
            # Tạo UUID ngẫu nhiên có định danh duy nhất theo chunk_id
            point_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, chunk.chunk_id))
            payload = {
                "chunk_id": chunk.chunk_id,
                "doc_id": chunk.doc_id,
                "doc_title": chunk.doc_title,
                "official_number": chunk.official_number,
                "chapter": chunk.chapter,
                "article_number": chunk.article_number,
                "article_title": chunk.article_title,
                "clause_number": chunk.clause_number,
                "status": chunk.status.value,
                "effective_date": chunk.effective_date.isoformat(),
                "expiry_date": chunk.expiry_date.isoformat() if chunk.expiry_date else None,
                "context_header": chunk.context_header,
                "content": chunk.content,
                "full_search_text": chunk.full_search_text,
                "scope_tags": chunk.scope_tags,
            }
            points.append(
                qmodels.PointStruct(
                    id=point_id,
                    vector=vector,
                    payload=payload,
                )
            )

        # Upload theo từng batch
        total_uploaded = 0
        for i in range(0, len(points), batch_size):
            batch = points[i : i + batch_size]
            self.client.upsert(collection_name=self.collection_name, points=batch)
            total_uploaded += len(batch)

        print(f"[+] Đã nạp thành công {total_uploaded} vectors vào collection '{self.collection_name}'!")
        return total_uploaded

    def search_similar(
        self,
        query_vector: List[float],
        limit: int = 5,
        as_of_date: Optional[str] = None,
        status_filter: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Tìm kiếm các vector có độ tương đồng Cosine cao nhất với câu hỏi kèm bộ lọc Temporal / Status"""
        from datetime import datetime
        query_filter = None
        must_conditions = []
        should_conditions = []

        if as_of_date:
            try:
                dt = datetime.fromisoformat(as_of_date)
                must_conditions.append(
                    qmodels.FieldCondition(key="effective_date", range=qmodels.DatetimeRange(lte=dt))
                )
                should_conditions.extend([
                    qmodels.IsNullCondition(is_null=qmodels.PayloadField(key="expiry_date")),
                    qmodels.FieldCondition(key="expiry_date", range=qmodels.DatetimeRange(gte=dt)),
                ])
            except Exception as e:
                print(f"[!] Lỗi parse as_of_date '{as_of_date}': {e}")
        elif status_filter:
            must_conditions.append(
                qmodels.FieldCondition(
                    key="status",
                    match=qmodels.MatchValue(value=status_filter),
                )
            )

        if must_conditions or should_conditions:
            query_filter = qmodels.Filter(
                must=must_conditions if must_conditions else None,
                should=should_conditions if should_conditions else None,
            )

        # Hỗ trợ cả API search cũ và query_points mới của Qdrant
        if hasattr(self.client, "query_points"):
            results = self.client.query_points(
                collection_name=self.collection_name,
                query=query_vector,
                limit=limit,
                query_filter=query_filter,
                with_payload=True,
            ).points
        else:
            results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                limit=limit,
                query_filter=query_filter,
                with_payload=True,
            )

        formatted = []
        for r in results:
            formatted.append({
                "score": r.score,
                "chunk_id": r.payload.get("chunk_id"),
                "doc_id": r.payload.get("doc_id", "bllđ_45_2019_qh14"),
                "doc_title": r.payload.get("doc_title", "Bộ luật Lao động 2019"),
                "article_number": r.payload.get("article_number"),
                "article_title": r.payload.get("article_title"),
                "clause_number": r.payload.get("clause_number"),
                "chapter": r.payload.get("chapter"),
                "context_header": r.payload.get("context_header"),
                "content": r.payload.get("content"),
                "effective_date": r.payload.get("effective_date"),
                "effective_from": r.payload.get("effective_from") or r.payload.get("effective_date"),
                "effective_to": r.payload.get("effective_to") or r.payload.get("expiry_date"),
                "amended_by": r.payload.get("amended_by"),
                "status": r.payload.get("status"),
            })
        return formatted

    def close(self):
        """Đóng kết nối để giải phóng tài nguyên"""
        try:
            self.client.close()
        except Exception:
            pass
