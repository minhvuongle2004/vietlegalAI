import os
import sys
import re
from datetime import date
from pathlib import Path
from typing import List, Dict, Any

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


def parse_real_estate_doc(
    html_path: Path,
    doc_id: str,
    title: str,
    official_number: str,
    issue_date: date,
    effective_date: date,
    max_articles: int,
    scope_tags: List[str],
) -> LegalDocumentParsed:
    print(f"\n[*] Đang bóc tách văn bản {title} ({official_number}) từ {html_path}...")
    with open(html_path, "r", encoding="utf-8", errors="ignore") as f:
        html = f.read()

    soup = BeautifulSoup(html, "html.parser")
    for br in soup.find_all("br"):
        br.replace_with("\n")
    for p in soup.find_all(["p", "div", "tr"]):
        p.append("\n")

    raw_text = soup.get_text()

    # Normalize cases where "Điều" is followed by newlines and a number
    normalized_text = re.sub(r"Điều\s*\n+\s*(\d+)[\.:\s]", r"Điều \1. ", raw_text)
    lines = [line.strip() for line in normalized_text.splitlines() if line.strip()]

    articles = []
    current_art = None

    article_pattern = re.compile(r"^Điều\s+(\d+)[\.:\s]\s*(.*)", re.IGNORECASE)
    chapter_pattern = re.compile(r"^Chương\s+([IVXLCDM\d]+)[\.:\s]\s*(.*)", re.IGNORECASE)

    current_chapter = ""
    chapters_dict = {}
    expected_art = 1

    invalid_title_patterns = [
        r"^của\s+Luật",
        r"^của\s+Bộ\s+luật",
        r"^của\s+Nghị\s+định",
        r"^và\s+Điều",
        r"^hoặc\s+Điều",
        r"của\s+Luật\s+này",
        r"theo\s+quy\s+định",
    ]

    for line in lines:
        ch_match = chapter_pattern.match(line)
        if ch_match:
            current_chapter = f"Chương {ch_match.group(1)}: {ch_match.group(2).strip()}"
            if current_chapter not in chapters_dict:
                chapters_dict[current_chapter] = LegalChapter(
                    chapter_number=f"Chương {ch_match.group(1)}",
                    chapter_title=ch_match.group(2).strip() or f"Chương {ch_match.group(1)}",
                    articles=[],
                )
            continue

        art_match = article_pattern.match(line)
        is_real_article = False
        if art_match:
            art_num = int(art_match.group(1))
            art_title = art_match.group(2).strip()

            is_ref = any(re.search(pat, art_title, re.IGNORECASE) for pat in invalid_title_patterns)
            if not is_ref and (art_num == expected_art or (expected_art <= art_num <= expected_art + 2)):
                if art_num <= max_articles:
                    is_real_article = True
                    expected_art = art_num + 1

        if is_real_article:
            if current_art:
                articles.append(current_art)
            current_art = {
                "num": art_num,
                "title": art_title,
                "chapter": current_chapter,
                "lines": [line],
            }
        else:
            if current_art:
                current_art["lines"].append(line)

    if current_art:
        articles.append(current_art)

    print(f" [+] Đã bóc tách thành công {len(articles)}/{max_articles} Điều luật cho {title}!")

    # Convert to LegalArticle
    legal_articles = []
    for art_data in articles:
        art_num = art_data["num"]
        full_text = "\n".join(art_data["lines"]).strip()

        # Parse clauses
        clauses = []
        clause_blocks = []
        current_cl_num = None
        current_cl_lines = []

        clause_regex = re.compile(r"^(\d+)\.\s*(.*)")
        for line in art_data["lines"][1:]:  # skip title
            cl_m = clause_regex.match(line)
            if cl_m:
                if current_cl_num is not None:
                    clause_blocks.append((current_cl_num, "\n".join(current_cl_lines)))
                current_cl_num = int(cl_m.group(1))
                current_cl_lines = [line]
            else:
                if current_cl_num is not None:
                    current_cl_lines.append(line)
                else:
                    current_cl_lines.append(line)

        if current_cl_num is not None:
            clause_blocks.append((current_cl_num, "\n".join(current_cl_lines)))

        if not clause_blocks:
            clauses.append(LegalClause(clause_number=1, text=full_text))
        else:
            for cl_num, cl_text in clause_blocks:
                clauses.append(LegalClause(clause_number=cl_num, text=cl_text.strip()))

        la = LegalArticle(
            article_number=art_num,
            article_title=art_data["title"] or f"Điều {art_num}",
            full_text=full_text,
            clauses=clauses,
            status=DocumentStatus.CON_HIEU_LUC,
            effective_date=effective_date,
        )
        legal_articles.append(la)

        ch_name = art_data["chapter"]
        if ch_name in chapters_dict:
            chapters_dict[ch_name].articles.append(la)

    meta = LegalDocumentMetadata(
        doc_id=doc_id,
        title=title,
        official_number=official_number,
        doc_type=DocumentType.LUAT,
        issuer="Quốc hội",
        issue_date=issue_date,
        effective_date=effective_date,
        status=DocumentStatus.CON_HIEU_LUC,
        description=f"{title}, số hiệu {official_number}",
    )

    return LegalDocumentParsed(
        metadata=meta,
        chapters=list(chapters_dict.values()),
        raw_articles=legal_articles,
    )


def build_chunks(doc: LegalDocumentParsed, scope_tags: List[str]) -> List[LegalChunkPayload]:
    meta = doc.metadata
    chunks = []

    art_to_ch = {}
    for ch in doc.chapters:
        for a in ch.articles:
            art_to_ch[a.article_number] = f"{ch.chapter_number}: {ch.chapter_title}"

    for art in doc.raw_articles:
        ch_info = art_to_ch.get(art.article_number, "")
        header_base = f"[{meta.title}] {ch_info} - Điều {art.article_number}: {art.article_title or ''}".strip()

        # Chunk toàn văn điều nếu ngắn (<= 1400 chars hoặc <= 1 khoản)
        if len(art.full_text) <= 1400 or len(art.clauses) <= 1:
            chunks.append(
                LegalChunkPayload(
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
                    scope_tags=scope_tags,
                )
            )
        else:
            # Chunk toàn văn tổng quát (trích đoạn đầu để cover context rộng)
            chunks.append(
                LegalChunkPayload(
                    chunk_id=f"{meta.doc_id}_D{art.article_number}_FULL",
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
                    context_header=f"Điều {art.article_number}: {art.article_title or ''} (Toàn văn)",
                    content=art.full_text[:1200],
                    full_search_text=f"{header_base} (Toàn văn)\n{art.full_text[:1200]}",
                    scope_tags=scope_tags,
                )
            )

            # Gom các khoản nhỏ vào chunk
            current_text = ""
            current_clauses = []
            for cl in art.clauses:
                if len(current_text) + len(cl.text) < 1200:
                    current_text += ("\n" if current_text else "") + cl.text
                    current_clauses.append(cl.clause_number)
                else:
                    if current_text:
                        cl_desc = (
                            f"Khoản {current_clauses[0]}-{current_clauses[-1]}"
                            if len(current_clauses) > 1
                            else f"Khoản {current_clauses[0]}"
                        )
                        chunks.append(
                            LegalChunkPayload(
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
                                scope_tags=scope_tags,
                            )
                        )
                    current_text = cl.text
                    current_clauses = [cl.clause_number]

            if current_text:
                cl_desc = (
                    f"Khoản {current_clauses[0]}-{current_clauses[-1]}"
                    if len(current_clauses) > 1
                    else f"Khoản {current_clauses[0]}"
                )
                chunks.append(
                    LegalChunkPayload(
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
                        scope_tags=scope_tags,
                    )
                )

    return chunks


def main():
    print("=" * 80)
    print("   INGESTION PIPELINE: CỤM BẤT ĐỘNG SẢN & ĐẦU TƯ (PHASE 3)")
    print("=" * 80)

    re_configs = [
        {
            "html": PROJECT_ROOT / "data" / "01_raw" / "html" / "31_2024_QH15.html",
            "id": "land_31_2024_qh15",
            "title": "Luật Đất đai 2024",
            "number": "31/2024/QH15",
            "issue_date": date(2024, 1, 18),
            "effective_date": date(2024, 8, 1),
            "max": 260,
            "tags": ["dat_dai", "bat_dong_san", "giao_dat", "thu_hoi_dat", "bang_gia_dat", "so_do", "chuyen_nhuong"],
        },
        {
            "html": PROJECT_ROOT / "data" / "01_raw" / "html" / "27_2023_QH15.html",
            "id": "housing_27_2023_qh15",
            "title": "Luật Nhà ở 2023",
            "number": "27/2023/QH15",
            "issue_date": date(2023, 11, 27),
            "effective_date": date(2024, 8, 1),
            "max": 198,
            "tags": ["nha_o", "nha_o_xa_hoi", "chung_cu", "so_huu_nha_o", "kinh_phi_bao_tri", "ban_quan_tri"],
        },
        {
            "html": PROJECT_ROOT / "data" / "01_raw" / "html" / "29_2023_QH15.html",
            "id": "re_business_29_2023_qh15",
            "title": "Luật Kinh doanh Bất động sản 2023",
            "number": "29/2023/QH15",
            "issue_date": date(2023, 11, 28),
            "effective_date": date(2024, 8, 1),
            "max": 83,
            "tags": ["kinh_doanh_bds", "bat_dong_san", "dat_coc_5_phan_tram", "nha_o_hinh_thanh_trong_tuong_lai", "bao_lanh_ngan_hang"],
        },
        {
            "html": PROJECT_ROOT / "data" / "01_raw" / "html" / "61_2020_QH14.html",
            "id": "investment_61_2020_qh14",
            "title": "Luật Đầu tư 2020",
            "number": "61/2020/QH14",
            "issue_date": date(2020, 6, 17),
            "effective_date": date(2021, 1, 1),
            "max": 77,
            "tags": ["dau_tu", "chu_truong_dau_tu", "nha_dau_tu", "du_an_dau_tu", "uu_dai_dau_tu", "chap_thuan_dau_tu"],
        },
    ]

    loader = SupabaseLegalLoader()
    all_chunks = []

    # 1. Parse & Upload Supabase
    for cfg in re_configs:
        if not cfg["html"].exists():
            print(f"[!] Không tìm thấy file: {cfg['html']}")
            return

        doc = parse_real_estate_doc(
            html_path=cfg["html"],
            doc_id=cfg["id"],
            title=cfg["title"],
            official_number=cfg["number"],
            issue_date=cfg["issue_date"],
            effective_date=cfg["effective_date"],
            max_articles=cfg["max"],
            scope_tags=cfg["tags"],
        )

        doc_chunks = build_chunks(doc, cfg["tags"])
        all_chunks.extend(doc_chunks)
        print(f" [+] Tạo được {len(doc_chunks)} chunks cho {cfg['title']}")

        # Upload Supabase
        print(f" [*] Đồng bộ lên Supabase: {cfg['title']}...")
        loader.upsert_document(doc)
        arts_count = loader.upsert_articles(doc)
        print(f" [+] Đã lưu {arts_count} Điều luật lên Supabase!")

    print(f"\n================================================================================")
    print(f" TỔNG SỐ CHUNKS MỚI CỦA CỤM BẤT ĐỘNG SẢN & ĐẦU TƯ: {len(all_chunks)} chunks")
    print(f"================================================================================")

    # 2. Vectorization & Qdrant Upsert
    print(f"\n[*] Khởi tạo QdrantVectorStore & BGE-M3 Embedding Service...")
    vector_store = QdrantVectorStore()
    embedding_service = get_embedding_service()

    before_info = vector_store.client.get_collection(vector_store.collection_name)
    before_count = before_info.points_count
    print(f" [*] Số lượng vector trước khi nạp: {before_count} points.")

    print(f"\n[*] Đang tạo embeddings cho {len(all_chunks)} chunks bằng BGE-M3 (batch_size=8)...")
    texts_to_embed = [c.full_search_text for c in all_chunks]
    embeddings = embedding_service.embed_texts(texts_to_embed, batch_size=8)
    print(f" [+] Đã hoàn tất vector hóa {len(embeddings)} vectors!")

    print(f"\n[*] Đang nạp {len(all_chunks)} chunks vào Qdrant collection '{vector_store.collection_name}'...")
    vector_store.insert_chunks(
        chunks=all_chunks,
        embeddings=embeddings,
        batch_size=50,
    )

    after_info = vector_store.client.get_collection(vector_store.collection_name)
    after_count = after_info.points_count
    print(f"\n[+] HOÀN TẤT INGESTION CỤM BẤT ĐỘNG SẢN & ĐẦU TƯ THÀNH CÔNG!")
    print(f"    - Vector Points ban đầu: {before_count}")
    print(f"    - Vector Points bổ sung: +{len(all_chunks)}")
    print(f"    - Vector Points hiện tại: {after_count}")
    print("=" * 80)


if __name__ == "__main__":
    main()
