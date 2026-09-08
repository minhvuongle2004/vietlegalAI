import os
import sys
import re
import fitz
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

from pipeline.models import (
    LegalArticle,
    LegalClause,
    LegalPoint,
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
from qdrant_client.http import models as qmodels


def extract_clean_lines_from_pdf(pdf_path: Path) -> List[str]:
    """Trích xuất danh sách dòng sạch từ PDF, loại bỏ số trang và header Công báo"""
    doc = fitz.open(pdf_path)
    lines = []
    for p in doc:
        txt = p.get_text()
        for l in txt.split("\n"):
            l_str = l.strip()
            if l_str and not re.match(r"^CÔNG BÁO/Số|^\d+$", l_str):
                lines.append(l_str)
    return lines


def parse_bhxh_2024(pdf_path: Path) -> LegalDocumentParsed:
    print("\n[*] Đang bóc tách toàn văn Luật BHXH 2024 (41/2024/QH15)...")
    lines = extract_clean_lines_from_pdf(pdf_path)

    # 1. Bóc tách Chương
    chapters_raw = []
    for i, l in enumerate(lines):
        m = re.match(r"^Chương\s+([IVXLCDM\d]+)[\.:\s]*(.*)", l, re.IGNORECASE)
        if m:
            num = m.group(1).upper()
            title = m.group(2).strip()
            if not title and i + 1 < len(lines):
                title = lines[i + 1].strip()
            chapters_raw.append({
                "chapter_number": f"Chương {num}",
                "chapter_title": title,
                "line_idx": i
            })

    # 2. Bóc tách 141 Điều
    arts_dict = {}
    curr_art = None
    for i, l in enumerate(lines):
        m = re.match(r"^Điều\s+(\d+)[\.:\s]+(.*)", l)
        if m:
            num = int(m.group(1))
            if num not in arts_dict and (curr_art is None or num == curr_art + 1 or num <= 141):
                curr_art = num
                arts_dict[num] = {
                    "number": num,
                    "title": m.group(2).strip(),
                    "lines": [l],
                    "line_idx": i,
                }
                continue
        if curr_art:
            arts_dict[curr_art]["lines"].append(l)

    print(f" [+] Tìm thấy {len(arts_dict)}/141 Điều luật trong Luật BHXH 2024.")

    parsed_articles: List[LegalArticle] = []
    for art_num in sorted(arts_dict.keys()):
        item = arts_dict[art_num]
        art_lines = item["lines"]
        raw_title = item["title"]

        content_lines = art_lines[1:]
        if not raw_title and content_lines:
            raw_title = content_lines[0].strip()
            content_lines = content_lines[1:]

        full_text = "\n".join(art_lines).strip()

        # Bóc tách Khoản
        clauses = []
        clause_starts = []
        for idx, cl_line in enumerate(content_lines):
            cm = re.match(r"^(\d+)\.\s*(.*)", cl_line)
            if cm:
                clause_starts.append((int(cm.group(1)), idx, cm.group(2).strip()))

        if clause_starts:
            for c_idx, (cl_num, start_c, cl_first_line) in enumerate(clause_starts):
                end_c = clause_starts[c_idx + 1][1] if c_idx + 1 < len(clause_starts) else len(content_lines)
                cl_lines = content_lines[start_c:end_c]
                cl_text = "\n".join(cl_lines).strip()

                # Bóc tách Điểm
                points = []
                for pl in cl_lines:
                    pm = re.match(r"^([a-zđ])\)\s*(.*)", pl, re.IGNORECASE)
                    if pm:
                        points.append(LegalPoint(point_letter=pm.group(1).lower(), text=pm.group(2).strip()))

                clauses.append(LegalClause(clause_number=cl_num, text=cl_text, points=points))
        else:
            clauses.append(LegalClause(clause_number=1, text=full_text, points=[]))

        parsed_articles.append(LegalArticle(
            article_number=art_num,
            article_title=raw_title,
            full_text=full_text,
            clauses=clauses,
            status=DocumentStatus.CON_HIEU_LUC,
        ))

    # Ghép Chương
    parsed_chapters = []
    if chapters_raw:
        for c_idx, c in enumerate(chapters_raw):
            c_start = c["line_idx"]
            c_end = chapters_raw[c_idx + 1]["line_idx"] if c_idx + 1 < len(chapters_raw) else len(lines)
            chap_arts = [
                art for art in parsed_articles
                if c_start <= arts_dict[art.article_number]["line_idx"] < c_end
            ]
            parsed_chapters.append(LegalChapter(
                chapter_number=c["chapter_number"],
                chapter_title=c["chapter_title"],
                articles=chap_arts,
            ))

    metadata = LegalDocumentMetadata(
        doc_id="bhxh_41_2024_qh15",
        official_number="41/2024/QH15",
        title="Luật Bảo hiểm xã hội 2024",
        short_title="Luật Bảo hiểm xã hội 2024",
        doc_type=DocumentType.LUAT,
        issuer="Quốc hội",
        issue_date=date(2024, 6, 29),
        effective_date=date(2025, 7, 1),
        expiry_date=None,
        status=DocumentStatus.CON_HIEU_LUC,
        replaces=["bhxh_58_2014_qh13"],
    )

    return LegalDocumentParsed(
        metadata=metadata,
        chapters=parsed_chapters,
        raw_articles=parsed_articles,
    )


def parse_bhyt_2024(pdf_path: Path) -> LegalDocumentParsed:
    print("\n[*] Đang bóc tách toàn văn Luật sửa đổi Luật BHYT 2024 (51/2024/QH15)...")
    lines = extract_clean_lines_from_pdf(pdf_path)

    arts_dict = {}
    curr_art = None
    for i, l in enumerate(lines):
        m = re.match(r"^Điều\s+(\d+)[\.:\s]+(.*)", l)
        if m:
            num = int(m.group(1))
            # Luật 51 có 3 Điều: Điều 1 (Sửa đổi BHYT), Điều 2, Điều 3
            if num in [1, 2, 3] and num not in arts_dict:
                curr_art = num
                arts_dict[num] = {
                    "number": num,
                    "title": m.group(2).strip(),
                    "lines": [l],
                }
                continue
        if curr_art:
            arts_dict[curr_art]["lines"].append(l)

    print(f" [+] Tìm thấy {len(arts_dict)}/3 Điều luật trong Luật BHYT 2024.")

    parsed_articles: List[LegalArticle] = []
    for art_num in sorted(arts_dict.keys()):
        item = arts_dict[art_num]
        art_lines = item["lines"]
        raw_title = item["title"]
        full_text = "\n".join(art_lines).strip()

        # Bóc tách các Khoản sửa đổi (Điều 1 có ~40 khoản sửa đổi các Điều của Luật BHYT)
        clauses = []
        clause_starts = []
        for idx, cl_line in enumerate(art_lines[1:]):
            cm = re.match(r"^(\d+)\.\s*(.*)", cl_line)
            if cm:
                clause_starts.append((int(cm.group(1)), idx + 1, cm.group(2).strip()))

        if clause_starts:
            for c_idx, (cl_num, start_c, cl_first_line) in enumerate(clause_starts):
                end_c = clause_starts[c_idx + 1][1] if c_idx + 1 < len(clause_starts) else len(art_lines)
                cl_lines = art_lines[start_c:end_c]
                cl_text = "\n".join(cl_lines).strip()
                clauses.append(LegalClause(clause_number=cl_num, text=cl_text, points=[]))
        else:
            clauses.append(LegalClause(clause_number=1, text=full_text, points=[]))

        parsed_articles.append(LegalArticle(
            article_number=art_num,
            article_title=raw_title,
            full_text=full_text,
            clauses=clauses,
            status=DocumentStatus.CON_HIEU_LUC,
        ))

    metadata = LegalDocumentMetadata(
        doc_id="bhyt_51_2024_qh15",
        official_number="51/2024/QH15",
        title="Luật sửa đổi, bổ sung một số điều của Luật Bảo hiểm y tế 2024",
        short_title="Luật Bảo hiểm y tế sửa đổi 2024",
        doc_type=DocumentType.LUAT,
        issuer="Quốc hội",
        issue_date=date(2024, 11, 27),
        effective_date=date(2025, 7, 1),
        expiry_date=None,
        status=DocumentStatus.CON_HIEU_LUC,
    )

    return LegalDocumentParsed(
        metadata=metadata,
        chapters=[LegalChapter(chapter_number="Chương I", chapter_title="Toàn văn", articles=parsed_articles)],
        raw_articles=parsed_articles,
    )


def build_chunks(parsed_doc: LegalDocumentParsed) -> List[LegalChunkPayload]:
    chunks: List[LegalChunkPayload] = []
    meta = parsed_doc.metadata

    article_to_chapter = {}
    for ch in parsed_doc.chapters:
        for art in ch.articles:
            article_to_chapter[art.article_number] = f"{ch.chapter_number}: {ch.chapter_title}"

    for art in parsed_doc.raw_articles:
        chapter_info = article_to_chapter.get(art.article_number, "Toàn văn")
        context_header = (
            f"Văn bản: {meta.title} (Số hiệu: {meta.official_number}). "
            f"{chapter_info}. "
            f"Điều {art.article_number}: {art.article_title or ''}."
        )

        # 1. Chunk ARTICLE_FULL (luôn có)
        chunk_id_full = f"{meta.doc_id}_d{art.article_number}"
        chunks.append(LegalChunkPayload(
            chunk_id=chunk_id_full,
            doc_id=meta.doc_id,
            doc_title=meta.short_title or meta.title,
            official_number=meta.official_number,
            chapter=chapter_info,
            article_number=art.article_number,
            article_title=art.article_title,
            clause_number=None,
            status=art.status,
            effective_date=meta.effective_date,
            expiry_date=meta.expiry_date,
            context_header=context_header,
            content=art.full_text,
            full_search_text=f"{context_header}\n{art.full_text}",
            scope_tags=[meta.doc_type.value.lower(), "temporal_phase1"],
        ))

        # 2. Chunk từng Khoản nếu có nhiều khoản
        if len(art.clauses) > 1:
            for cl in art.clauses:
                # Bỏ qua khoản quá ngắn (< 30 ký tự)
                if len(cl.text) < 30:
                    continue
                chunk_id_cl = f"{meta.doc_id}_d{art.article_number}_k{cl.clause_number}"
                cl_header = f"{context_header} Khoản {cl.clause_number}."
                chunks.append(LegalChunkPayload(
                    chunk_id=chunk_id_cl,
                    doc_id=meta.doc_id,
                    doc_title=meta.short_title or meta.title,
                    official_number=meta.official_number,
                    chapter=chapter_info,
                    article_number=art.article_number,
                    article_title=art.article_title,
                    clause_number=cl.clause_number,
                    status=art.status,
                    effective_date=meta.effective_date,
                    expiry_date=meta.expiry_date,
                    context_header=cl_header,
                    content=cl.text,
                    full_search_text=f"{cl_header}\n{cl.text}",
                    scope_tags=[meta.doc_type.value.lower(), "temporal_phase1"],
                ))

    return chunks


def update_qdrant_existing_bhxh2014(vector_store: QdrantVectorStore):
    """Cập nhật payload của các point bhxh_58_2014_qh13 trong Qdrant sang HET_HIEU_LUC và expiry_date 2025-06-30"""
    print("\n[*] Cập nhật payload cho các chunk Luật BHXH 2014 trong Qdrant...")
    try:
        vector_store.client.set_payload(
            collection_name=vector_store.collection_name,
            payload={
                "expiry_date": "2025-06-30",
                "status": "HET_HIEU_LUC",
            },
            points=qmodels.Filter(
                must=[
                    qmodels.FieldCondition(
                        key="doc_id",
                        match=qmodels.MatchValue(value="bhxh_58_2014_qh13"),
                    )
                ]
            ),
        )
        print("[+] Đã cập nhật thành công payload Qdrant cho bhxh_58_2014_qh13 (HET_HIEU_LUC, expiry_date: 2025-06-30)")
    except Exception as e:
        print(f"[!] Lỗi khi cập nhật Qdrant payload: {e}")


def main():
    print("=" * 70)
    print("   INGESTION PHASE 1: LUẬT BHXH 2024 & LUẬT BHYT 2024")
    print("=" * 70)

    pdf_bhxh = PROJECT_ROOT / "data" / "01_raw" / "pdf" / "41_2024_QH15.pdf"
    pdf_bhyt = PROJECT_ROOT / "data" / "01_raw" / "pdf" / "51_2024_QH15.pdf"

    if not pdf_bhxh.exists() or not pdf_bhyt.exists():
        print("[!] Không tìm thấy file PDF tải về.")
        return

    # 1. Bóc tách cấu trúc
    doc_bhxh = parse_bhxh_2024(pdf_bhxh)
    doc_bhyt = parse_bhyt_2024(pdf_bhyt)

    # 2. Tạo chunks
    chunks_bhxh = build_chunks(doc_bhxh)
    chunks_bhyt = build_chunks(doc_bhyt)
    all_chunks = chunks_bhxh + chunks_bhyt
    print(f"\n[+] Tổng số chunks tạo mới: {len(all_chunks)} ({len(chunks_bhxh)} BHXH 2024, {len(chunks_bhyt)} BHYT 2024)")

    # 3. Nạp vào Supabase (legal_documents, legal_articles)
    print("\n[*] Nạp dữ liệu vào Supabase...")
    loader = SupabaseLegalLoader()
    loader.upsert_document(doc_bhxh)
    loader.upsert_articles(doc_bhxh)
    loader.upsert_document(doc_bhyt)
    loader.upsert_articles(doc_bhyt)
    print("[+] Đã lưu văn bản và điều luật mới vào Supabase!")

    # 4. Cập nhật Qdrant: Cập nhật Luật cũ + Nạp Luật mới
    print("\n[*] Khởi tạo QdrantVectorStore & Embedding Service...")
    vector_store = QdrantVectorStore()
    embedding_service = get_embedding_service()

    # Cập nhật points cũ của BHXH 2014
    update_qdrant_existing_bhxh2014(vector_store)

    # Nạp chunks mới vào Qdrant
    print(f"\n[*] Đang tạo embeddings cho {len(all_chunks)} chunks mới bằng BGE-M3 (batch_size=4)...")
    texts_to_embed = [c.full_search_text for c in all_chunks]
    embeddings = embedding_service.embed_texts(texts_to_embed, batch_size=4)

    print(f"\n[*] Đang nạp {len(all_chunks)} chunks mới vào Qdrant...")
    vector_store.insert_chunks(
        chunks=all_chunks,
        embeddings=embeddings,
        batch_size=50,
    )

    print("\n[DONE] Hoàn tất Ingestion Phase 1 thành công rực rỡ!")


if __name__ == "__main__":
    main()
