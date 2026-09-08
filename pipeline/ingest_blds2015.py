import os
import sys
import re
import json
from datetime import date
from pathlib import Path
from typing import List, Dict, Any, Optional

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from bs4 import BeautifulSoup
from pipeline.models import (
    LegalArticle,
    LegalClause,
    LegalChapter,
    LegalDocumentMetadata,
    LegalDocumentParsed,
    LegalChunkPayload,
    DocumentType,
    DocumentStatus,
)
from pipeline.loaders.supabase_loader import SupabaseLegalLoader
from backend.app.services.rag.embeddings import get_embedding_service
from backend.app.services.rag.vector_store import QdrantVectorStore


def parse_blds_2015(html_path: Path) -> LegalDocumentParsed:
    print(f"\n[*] Đang bóc tách 689 Điều luật từ: {html_path}...")
    with open(html_path, "r", encoding="utf-8") as f:
        html = f.read()

    soup = BeautifulSoup(html, "html.parser")
    elements = soup.find_all(["p", "div"])

    articles = {}
    current_art_num = None
    current_art_title = ""
    current_art_lines = []
    current_chapter = ""
    chapters_dict = {}

    for el in elements:
        text = re.sub(r"\s+", " ", el.get_text()).strip()
        if not text:
            continue

        # Chapter detection
        chap_m = re.match(r"^(?:Chương|CHƯƠNG)\s+([IVXLCDM\d]+)[\.:\s]*(.*)", text)
        if chap_m:
            current_chapter = f"Chương {chap_m.group(1)}: {chap_m.group(2).strip()}"
            if current_chapter not in chapters_dict:
                chapters_dict[current_chapter] = LegalChapter(
                    chapter_number=f"Chương {chap_m.group(1)}",
                    chapter_title=chap_m.group(2).strip(),
                    articles=[],
                )
            continue

        # Article heading detection
        art_m = re.match(r"^Điều\s+(\d+)[\.:\s]*(.*)", text)
        if art_m:
            num = int(art_m.group(1))
            if current_art_num is None or num == current_art_num + 1 or num not in articles:
                if current_art_num is not None and current_art_num not in articles:
                    articles[current_art_num] = {
                        "number": current_art_num,
                        "title": current_art_title,
                        "chapter": current_chapter,
                        "content": "\n".join(current_art_lines).strip(),
                    }
                current_art_num = num
                current_art_title = art_m.group(2).strip()
                current_art_lines = [text]
                continue

        if current_art_num is not None:
            if not current_art_lines or text != current_art_lines[-1]:
                current_art_lines.append(text)

    if current_art_num is not None and current_art_num not in articles:
        articles[current_art_num] = {
            "number": current_art_num,
            "title": current_art_title,
            "chapter": current_chapter,
            "content": "\n".join(current_art_lines).strip(),
        }

    raw_articles = []
    for k in sorted(articles.keys()):
        item = articles[k]
        # Bóc tách các khoản
        clauses = []
        clause_matches = re.split(r"(?:\n|^)(\d+\.\s+)", item["content"])
        if len(clause_matches) > 1:
            cl_prefix = ""
            for part in clause_matches:
                if re.match(r"^\d+\.\s+$", part):
                    cl_prefix = part
                    continue
                cl_text = cl_prefix + part.strip()
                cl_num_m = re.match(r"^(\d+)\.", cl_text)
                cl_num = int(cl_num_m.group(1)) if cl_num_m else len(clauses) + 1
                clauses.append(LegalClause(clause_number=cl_num, text=cl_text))
        else:
            clauses.append(LegalClause(clause_number=1, text=item["content"]))

        article_obj = LegalArticle(
            article_number=item["number"],
            article_title=item["title"],
            full_text=item["content"],
            clauses=clauses,
            status=DocumentStatus.CON_HIEU_LUC,
        )
        raw_articles.append(article_obj)
        if item["chapter"] in chapters_dict:
            chapters_dict[item["chapter"]].articles.append(article_obj)

    meta = LegalDocumentMetadata(
        doc_id="blds_91_2015_qh13",
        official_number="91/2015/QH13",
        title="Bộ luật Dân sự 2015",
        short_title="BLDS 2015",
        doc_type=DocumentType.LUAT,
        issuer="Quốc hội",
        issue_date=date(2015, 11, 24),
        effective_date=date(2017, 1, 1),
        expiry_date=None,
        status=DocumentStatus.CON_HIEU_LUC,
        source_url="https://thuvienphapluat.vn/van-ban/Quyen-dan-su/Bo-luat-dan-su-2015-296215.aspx",
    )

    print(f" [+] Đã bóc tách thành công {len(raw_articles)} / 689 Điều luật!")
    return LegalDocumentParsed(
        metadata=meta,
        chapters=list(chapters_dict.values()),
        raw_articles=raw_articles,
    )


def build_chunks(doc: LegalDocumentParsed) -> List[LegalChunkPayload]:
    meta = doc.metadata
    chunks = []

    # Map article to chapter
    art_to_ch = {}
    for ch in doc.chapters:
        for a in ch.articles:
            art_to_ch[a.article_number] = f"{ch.chapter_number}: {ch.chapter_title}"

    for art in doc.raw_articles:
        ch_info = art_to_ch.get(art.article_number, "")
        header_base = f"[{meta.title}] {ch_info} - Điều {art.article_number}: {art.article_title or ''}".strip()

        # Nếu điều ngắn hoặc trung bình (<= 1400 chars) -> 1 chunk đại diện trọn vẹn
        if len(art.full_text) <= 1400 or len(art.clauses) <= 1:
            chunks.append(LegalChunkPayload(
                chunk_id=f"{meta.doc_id}_D{art.article_number}",
                doc_id=meta.doc_id,
                doc_title=meta.title,
                official_number=meta.official_number,
                chapter=ch_info,
                article_number=art.article_number,
                article_title=art.article_title,
                clause_number=None,
                status=art.status,
                effective_date=meta.effective_date,
                expiry_date=meta.expiry_date,
                context_header=f"Điều {art.article_number}: {art.article_title or ''}",
                content=art.full_text,
                full_search_text=f"{header_base}\n{art.full_text}",
                scope_tags=["dân sự", "hợp đồng", "tài sản", "thừa kế", "bồi thường"],
            ))
        else:
            # Điều dài -> Gom theo nhóm khoản để vừa vặn ngữ cảnh vector
            current_text = ""
            current_clauses = []
            for cl in art.clauses:
                if len(current_text) + len(cl.text) < 1200:
                    current_text += ("\n" if current_text else "") + cl.text
                    current_clauses.append(cl.clause_number)
                else:
                    if current_text:
                        cl_desc = f"Khoản {current_clauses[0]}-{current_clauses[-1]}" if len(current_clauses) > 1 else f"Khoản {current_clauses[0]}"
                        chunks.append(LegalChunkPayload(
                            chunk_id=f"{meta.doc_id}_D{art.article_number}_K{current_clauses[0]}",
                            doc_id=meta.doc_id,
                            doc_title=meta.title,
                            official_number=meta.official_number,
                            chapter=ch_info,
                            article_number=art.article_number,
                            article_title=art.article_title,
                            clause_number=current_clauses[0],
                            status=art.status,
                            effective_date=meta.effective_date,
                            expiry_date=meta.expiry_date,
                            context_header=f"Điều {art.article_number}: {art.article_title or ''} ({cl_desc})",
                            content=current_text,
                            full_search_text=f"{header_base} ({cl_desc})\n{current_text}",
                            scope_tags=["dân sự", "hợp đồng", "tài sản", "thừa kế", "bồi thường"],
                        ))
                    current_text = cl.text
                    current_clauses = [cl.clause_number]

            if current_text:
                cl_desc = f"Khoản {current_clauses[0]}-{current_clauses[-1]}" if len(current_clauses) > 1 else f"Khoản {current_clauses[0]}"
                chunks.append(LegalChunkPayload(
                    chunk_id=f"{meta.doc_id}_D{art.article_number}_K{current_clauses[0]}",
                    doc_id=meta.doc_id,
                    doc_title=meta.title,
                    official_number=meta.official_number,
                    chapter=ch_info,
                    article_number=art.article_number,
                    article_title=art.article_title,
                    clause_number=current_clauses[0],
                    status=art.status,
                    effective_date=meta.effective_date,
                    expiry_date=meta.expiry_date,
                    context_header=f"Điều {art.article_number}: {art.article_title or ''} ({cl_desc})",
                    content=current_text,
                    full_search_text=f"{header_base} ({cl_desc})\n{current_text}",
                    scope_tags=["dân sự", "hợp đồng", "tài sản", "thừa kế", "bồi thường"],
                ))

    return chunks


def main():
    print("=" * 80)
    print("   INGESTION PIPELINE: BỘ LUẬT DÂN SỰ 2015 (91/2015/QH13)")
    print("=" * 80)

    html_file = PROJECT_ROOT / "data" / "01_raw" / "html" / "91_2015_QH13.html"
    if not html_file.exists():
        print(f"[!] Không tìm thấy file: {html_file}")
        return

    # 1. Bóc tách văn bản
    doc_blds = parse_blds_2015(html_file)
    chunks_blds = build_chunks(doc_blds)
    print(f" [+] Tổng số chunks tạo mới: {len(chunks_blds)}")

    # 2. Đồng bộ lên Supabase
    print("\n[1/3] Đang nạp văn bản & 689 Điều luật lên Supabase...")
    loader = SupabaseLegalLoader()
    doc_ok = loader.upsert_document(doc_blds)
    if not doc_ok:
        print("[!] Lỗi khi nạp document vào Supabase.")
        return
    arts_count = loader.upsert_articles(doc_blds)
    print(f" [+] Đã lưu thành công {arts_count} Điều luật lên Supabase!")

    # 3. Vectorization bằng BGE-M3
    print(f"\n[2/3] Khởi tạo QdrantVectorStore & BGE-M3 Embedding Service...")
    vector_store = QdrantVectorStore()
    embedding_service = get_embedding_service()

    before_info = vector_store.client.get_collection(vector_store.collection_name)
    before_count = before_info.points_count
    print(f" [*] Số lượng vector trước khi nạp: {before_count} points.")

    print(f"\n[*] Đang tạo embeddings cho {len(chunks_blds)} chunks bằng BGE-M3 (batch_size=8)...")
    texts_to_embed = [c.full_search_text for c in chunks_blds]
    embeddings = embedding_service.embed_texts(texts_to_embed, batch_size=8)
    print(f" [+] Đã hoàn tất vector hóa {len(embeddings)} vectors!")

    # 4. Nạp vào Qdrant
    print(f"\n[3/3] Đang nạp {len(chunks_blds)} chunks vào Qdrant collection '{vector_store.collection_name}'...")
    vector_store.insert_chunks(
        chunks=chunks_blds,
        embeddings=embeddings,
        batch_size=50,
    )

    after_info = vector_store.client.get_collection(vector_store.collection_name)
    after_count = after_info.points_count
    print(f"\n[+] HOÀN TẤT INGESTION BỘ LUẬT DÂN SỰ 2015 THÀNH CÔNG RỰC RỠ!")
    print(f"    - Vector Points ban đầu: {before_count}")
    print(f"    - Vector Points bổ sung: +{len(chunks_blds)}")
    print(f"    - Vector Points hiện tại: {after_count}")
    print("=" * 80)


if __name__ == "__main__":
    main()
