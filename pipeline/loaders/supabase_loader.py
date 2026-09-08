import os
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional
import requests
from dotenv import load_dotenv

# Đảm bảo import được models
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from pipeline.models import LegalDocumentParsed, LegalArticle

# Nạp file .env (có fallback tự động đọc nếu môi trường chưa cài python-dotenv)
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
                    k = k.strip()
                    v = v.strip().strip('"').strip("'")
                    os.environ.setdefault(k, v)


class SupabaseLegalLoader:
    """
    Module nạp dữ liệu văn bản pháp luật vào Supabase Database.
    Sử dụng Supabase REST API (nhanh, nhẹ, không phụ thuộc C-drivers).
    """

    def __init__(self, supabase_url: Optional[str] = None, supabase_key: Optional[str] = None):
        self.supabase_url = (supabase_url or os.getenv("SUPABASE_URL", "")).rstrip("/")
        self.supabase_key = supabase_key or os.getenv("SUPABASE_KEY", "")

        if not self.supabase_url or not self.supabase_key:
            raise ValueError("Thiếu SUPABASE_URL hoặc SUPABASE_KEY trong file .env")

        self.headers = {
            "apikey": self.supabase_key,
            "Authorization": f"Bearer {self.supabase_key}",
            "Content-Type": "application/json",
            "Prefer": "resolution=merge-duplicates",  # Upsert nếu trùng khóa chính
        }

    def upsert_document(self, parsed_doc: LegalDocumentParsed) -> bool:
        """Lưu hoặc cập nhật thông tin văn bản gốc vào bảng legal_documents"""
        meta = parsed_doc.metadata
        payload = {
            "id": meta.doc_id,
            "official_number": meta.official_number,
            "title": meta.title,
            "short_title": meta.short_title,
            "doc_type": meta.doc_type.value,
            "issuer": meta.issuer,
            "signer": meta.signer,
            "issue_date": meta.issue_date.isoformat(),
            "effective_date": meta.effective_date.isoformat(),
            "expiry_date": meta.expiry_date.isoformat() if meta.expiry_date else None,
            "status": meta.status.value,
            "source_url": meta.source_url,
            "metadata": {
                "replaces": meta.replaces,
                "amended_by": meta.amended_by,
                "guided_by": meta.guided_by,
                "guides": meta.guides,
            },
        }

        endpoint = f"{self.supabase_url}/rest/v1/legal_documents"
        res = requests.post(endpoint, json=payload, headers=self.headers)
        if res.status_code in (200, 201):
            return True
        print(f"[!] Lỗi khi nạp legal_documents: {res.status_code} - {res.text}")
        return False

    def upsert_articles(self, parsed_doc: LegalDocumentParsed) -> int:
        """Nạp toàn bộ danh sách các Điều luật vào bảng legal_articles"""
        meta = parsed_doc.metadata

        # Map article to chapter
        art_to_chapter = {}
        for ch in parsed_doc.chapters:
            for art in ch.articles:
                art_to_chapter[art.article_number] = f"{ch.chapter_number}: {ch.chapter_title}"

        articles_payload = []
        for art in parsed_doc.raw_articles:
            articles_payload.append({
                "document_id": meta.doc_id,
                "article_number": art.article_number,
                "article_title": art.article_title,
                "full_text": art.full_text,
                "chapter_info": art_to_chapter.get(art.article_number, ""),
                "status": art.status.value,
            })

        if not articles_payload:
            return 0

        endpoint = f"{self.supabase_url}/rest/v1/legal_articles"

        # 1. Xóa các điều luật cũ của văn bản này để tránh trùng lặp
        del_headers = {
            "apikey": self.supabase_key,
            "Authorization": f"Bearer {self.supabase_key}",
        }
        requests.delete(f"{endpoint}?document_id=eq.{meta.doc_id}", headers=del_headers)

        # 2. Nạp theo từng Batch 50 bản ghi
        batch_size = 50
        total_inserted = 0
        for i in range(0, len(articles_payload), batch_size):
            batch = articles_payload[i : i + batch_size]
            res = requests.post(endpoint, json=batch, headers=self.headers)
            if res.status_code in (200, 201):
                total_inserted += len(batch)
            else:
                print(f"[!] Lỗi batch {i}-{i+len(batch)}: {res.status_code} - {res.text}")

        return total_inserted

    def sync_parsed_document(self, parsed_doc: LegalDocumentParsed) -> Dict[str, Any]:
        """Đồng bộ hoàn chỉnh cả văn bản và các điều luật vào Supabase"""
        doc_ok = self.upsert_document(parsed_doc)
        articles_count = self.upsert_articles(parsed_doc) if doc_ok else 0
        return {
            "doc_id": parsed_doc.metadata.doc_id,
            "document_synced": doc_ok,
            "articles_count": articles_count,
        }
