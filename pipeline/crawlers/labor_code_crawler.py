import sys
import io
import os
import re
import json
import time
from pathlib import Path
from datetime import date
from typing import List, Dict, Any, Tuple
import requests
from bs4 import BeautifulSoup

# Đảm bảo UTF-8 cho Windows console
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

# Đảm bảo project root trong sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from pipeline.models import (
    LegalDocumentMetadata,
    DocumentType,
    DocumentStatus,
    LegalDocumentParsed,
)
from pipeline.parsers.legal_hierarchical_parser import LegalHierarchicalParser
from pipeline.loaders.supabase_loader import SupabaseLegalLoader


class LaborCode2019Crawler:
    """
    Crawler thu thập toàn văn Bộ luật Lao động 2019 (Luật số 45/2019/QH14)
    gồm đầy đủ 17 Chương và 220 Điều từ nguồn chính thống Wikisource tiếng Việt.
    """

    BASE_URL = "https://vi.wikisource.org/wiki/B%E1%BB%99_lu%E1%BA%ADt_Lao_%C4%91%E1%BB%99ng_n%C6%B0%E1%BB%9Bc_C%E1%BB%99ng_h%C3%B2a_x%C3%A3_h%E1%BB%99i_ch%E1%BB%A7_ngh%C4%A9a_Vi%E1%BB%87t_Nam_2019"
    HEADERS = {
        "User-Agent": "VietLegalBot/1.0 (VietLegal AI Education & Research; contact@vietlegal.ai)"
    }

    def __init__(self):
        self.raw_dir = PROJECT_ROOT / "data" / "01_raw" / "html" / "bllđ_2019"
        self.extracted_dir = PROJECT_ROOT / "data" / "02_extracted"
        self.parsed_dir = PROJECT_ROOT / "data" / "03_parsed"
        self.chunks_dir = PROJECT_ROOT / "data" / "04_curated_chunks"

        for d in [self.raw_dir, self.extracted_dir, self.parsed_dir, self.chunks_dir]:
            d.mkdir(parents=True, exist_ok=True)

    def get_metadata(self) -> LegalDocumentMetadata:
        return LegalDocumentMetadata(
            doc_id="bllđ_45_2019_qh14",
            official_number="45/2019/QH14",
            title="Bộ luật Lao động năm 2019",
            short_title="Bộ luật Lao động 2019",
            doc_type=DocumentType.BO_LUAT,
            issuer="Quốc hội",
            signer="Nguyễn Thị Kim Ngân",
            issue_date=date(2019, 11, 20),
            effective_date=date(2021, 1, 1),
            status=DocumentStatus.CON_HIEU_LUC,
            source_url=self.BASE_URL,
            replaces=["bllđ_10_2012_qh13"],
            amended_by=[],
            guided_by=[
                "nd_145_2020_nd_cp",
                "nd_135_2020_nd_cp",
                "nd_12_2022_nd_cp",
            ],
            guides=[],
        )

    def fetch_chapter_urls(self) -> List[Tuple[str, str]]:
        """Lấy danh sách link 17 chương của Bộ luật Lao động 2019"""
        print(f"[*] Đang kết nối tới trang chính: {self.BASE_URL}")
        res = requests.get(self.BASE_URL, headers=self.HEADERS, timeout=15)
        res.raise_for_status()

        soup = BeautifulSoup(res.text, "html.parser")
        subpages: List[Tuple[str, str]] = []

        prefix = "B%E1%BB%99_lu%E1%BA%ADt_Lao_%C4%91%E1%BB%99ng_n%C6%B0%E1%BB%9Bc_C%E1%BB%99ng_h%C3%B2a_x%C3%A3_h%E1%BB%99i_ch%E1%BB%A7_ngh%C4%A9a_Vi%E1%BB%87t_Nam_2019/"
        for a in soup.find_all("a"):
            href = a.get("href", "")
            if prefix in href:
                title = a.text.strip()
                url = "https://vi.wikisource.org" + href
                if url not in [s[1] for s in subpages]:
                    subpages.append((title, url))

        print(f"[+] Tìm thấy {len(subpages)} chương văn bản.")
        return subpages

    def crawl_and_assemble(self) -> str:
        """Cào từng chương và ghép thành văn bản đầy đủ"""
        subpages = self.fetch_chapter_urls()
        full_text_blocks = []

        for idx, (ch_title, ch_url) in enumerate(subpages, start=1):
            print(f" -> [{idx}/{len(subpages)}] Đang tải {ch_title}...")
            res = requests.get(ch_url, headers=self.HEADERS, timeout=15)
            soup = BeautifulSoup(res.text, "html.parser")

            content = soup.find("div", {"class": "mw-parser-output"})
            if not content:
                continue

            # Dọn dẹp thẻ rác của wiki
            for tag in content.find_all(["span"], {"class": "mw-editsection"}):
                tag.decompose()
            for tag in content.find_all(["table"], {"class": "toc"}):
                tag.decompose()

            # Lưu bản HTML thô của từng chương
            ch_raw_file = self.raw_dir / f"chuong_{idx:02d}.html"
            ch_raw_file.write_text(str(content), encoding="utf-8")

            # Chuẩn hóa khoảng trắng & text
            chapter_text = content.get_text(separator="\n")
            lines = [l.strip() for l in chapter_text.splitlines() if l.strip()]
            full_text_blocks.append("\n".join(lines))
            time.sleep(0.3)  # Lịch sự tránh gây tải cho server

        full_assembled_text = "\n\n".join(full_text_blocks)

        # Lưu văn bản đã tổng hợp vào 02_extracted
        extracted_file = self.extracted_dir / "bllđ_2019.txt"
        extracted_file.write_text(full_assembled_text, encoding="utf-8")
        print(f"[+] Đã lưu toàn văn bản thô: {extracted_file} ({len(full_assembled_text):,} ký tự)")

        return full_assembled_text

    def run(self, upload_supabase: bool = True) -> LegalDocumentParsed:
        print("=" * 70)
        print("   VIETLEGAL AI - PIPELINE THU THẬP BỘ LUẬT LAO ĐỘNG 2019")
        print("=" * 70)

        # 1. Cào và tổng hợp text
        raw_text = self.crawl_and_assemble()
        metadata = self.get_metadata()

        # 2. Bóc tách phân cấp bằng LegalHierarchicalParser
        print("\n[*] Đang bóc tách cấu trúc Chương, Điều, Khoản, Điểm...")
        parser = LegalHierarchicalParser()
        parsed_doc = parser.parse(raw_text, metadata)

        # 3. QA Gate: Kiểm định chất lượng dữ liệu
        print("\n[*] Đang kiểm định chất lượng dữ liệu (QA Gate)...")
        articles = parsed_doc.raw_articles
        art_nums = sorted([a.article_number for a in articles])

        print(f" -> Tổng số Điều trích xuất: {len(articles)}")
        print(f" -> Dãy số Điều: từ Điều {min(art_nums)} đến Điều {max(art_nums)}")

        # Kiểm tra tính toàn vẹn 220 Điều
        missing_articles = [i for i in range(1, 221) if i not in art_nums]
        if missing_articles:
            print(f"[!] CẢNH BÁO: Còn thiếu các Điều: {missing_articles}")
        else:
            print(" -> [QA PASS] ĐỦ 100% 220/220 ĐIỀU LUẬT KHÔNG BỊ KHUYẾT THIẾU!")

        # 4. Lưu dữ liệu JSON phân cấp
        parsed_file = self.parsed_dir / "bllđ_2019.json"
        with open(parsed_file, "w", encoding="utf-8") as f:
            json.dump(parsed_doc.model_dump(mode="json"), f, ensure_ascii=False, indent=2)
        print(f"[+] Đã lưu file cấu trúc JSON: {parsed_file}")

        # 5. Sinh Legal Chunks sẵn sàng cho Vector Database
        chunks = parser.create_chunks(parsed_doc)
        chunks_file = self.chunks_dir / "bllđ_2019_chunks.jsonl"
        with open(chunks_file, "w", encoding="utf-8") as f:
            for c in chunks:
                f.write(json.dumps(c.model_dump(mode="json"), ensure_ascii=False) + "\n")
        print(f"[+] Đã tạo {len(chunks)} chunks chuẩn: {chunks_file}")

        # 6. Đồng bộ lên Supabase Cloud
        if upload_supabase:
            print("\n[*] Đang nạp toàn bộ 220 Điều luật vào Supabase Cloud...")
            loader = SupabaseLegalLoader()
            res = loader.sync_parsed_document(parsed_doc)

            print("\n" + "=" * 70)
            print("   KẾT QUẢ ĐỒNG BỘ SUPABASE THÀNH CÔNG")
            print("=" * 70)
            print(f" -> Mã văn bản: {res['doc_id']}")
            print(f" -> Trạng thái nạp legal_documents: {res['document_synced']}")
            print(f" -> Tổng số Điều luật đã nạp vào legal_articles: {res['articles_count']}/220")
            print("\n🎉 Bạn có thể mở Supabase Table Editor để tra cứu toàn bộ 220 Điều luật!")

        return parsed_doc


def main():
    crawler = LaborCode2019Crawler()
    crawler.run(upload_supabase=True)


if __name__ == "__main__":
    main()
