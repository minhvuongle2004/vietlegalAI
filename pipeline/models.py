from datetime import date, datetime
from typing import List, Optional, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field


class DocumentType(str, Enum):
    HIEN_PHAP = "HIEN_PHAP"
    BO_LUAT = "BO_LUAT"
    LUAT = "LUAT"
    NGHI_QUYET = "NGHI_QUYET"
    PHAP_LENH = "PHAP_LENH"
    NGHI_DINH = "NGHI_DINH"
    QUYET_DINH = "QUYET_DINH"
    THONG_TU = "THONG_TU"
    OTHER = "OTHER"


class DocumentStatus(str, Enum):
    CON_HIEU_LUC = "CON_HIEU_LUC"
    HET_HIEU_LUC = "HET_HIEU_LUC"
    HET_HIEU_LUC_MOT_PHAN = "HET_HIEU_LUC_MOT_PHAN"
    CHUA_HIEU_LUC = "CHUA_HIEU_LUC"


class LegalPoint(BaseModel):
    """Điểm a, b, c trong một Khoản"""
    point_letter: str  # 'a', 'b', 'c'
    text: str


class LegalClause(BaseModel):
    """Khoản 1, 2, 3 trong một Điều"""
    clause_number: int  # 1, 2, 3
    text: str
    points: List[LegalPoint] = Field(default_factory=list)


class LegalArticle(BaseModel):
    """Điều luật (Đơn vị cơ sở của văn bản quy phạm pháp luật)"""
    article_number: int
    article_title: Optional[str] = None
    full_text: str
    clauses: List[LegalClause] = Field(default_factory=list)
    status: DocumentStatus = DocumentStatus.CON_HIEU_LUC
    amended_by: Optional[str] = None


class LegalChapter(BaseModel):
    """Chương / Mục trong văn bản"""
    chapter_number: str  # vd: 'Chương I'
    chapter_title: str
    articles: List[LegalArticle] = Field(default_factory=list)


class LegalDocumentMetadata(BaseModel):
    """Siêu dữ liệu định danh văn bản"""
    doc_id: str
    official_number: str
    title: str
    short_title: Optional[str] = None
    doc_type: DocumentType
    issuer: str
    signer: Optional[str] = None
    issue_date: date
    effective_date: date
    expiry_date: Optional[date] = None
    status: DocumentStatus = DocumentStatus.CON_HIEU_LUC
    source_url: Optional[str] = None
    replaces: List[str] = Field(default_factory=list)
    amended_by: List[str] = Field(default_factory=list)
    guided_by: List[str] = Field(default_factory=list)
    guides: List[str] = Field(default_factory=list)


class LegalDocumentParsed(BaseModel):
    """Văn bản hoàn chỉnh sau khi bóc tách cấu trúc"""
    metadata: LegalDocumentMetadata
    chapters: List[LegalChapter] = Field(default_factory=list)
    raw_articles: List[LegalArticle] = Field(default_factory=list)


class LegalChunkPayload(BaseModel):
    """Chunk dữ liệu sẵn sàng nạp vào Vector Database & Hybrid Search"""
    chunk_id: str
    doc_id: str
    doc_title: str
    official_number: str
    chapter: Optional[str] = None
    article_number: int
    article_title: Optional[str] = None
    clause_number: Optional[int] = None
    status: DocumentStatus
    effective_date: date
    expiry_date: Optional[date] = None
    context_header: str
    content: str
    full_search_text: str  # context_header + content
    scope_tags: List[str] = Field(default_factory=list)
