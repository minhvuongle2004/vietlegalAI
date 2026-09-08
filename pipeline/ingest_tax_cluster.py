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


def parse_tax_doc(html_path: Path, doc_id: str, title: str, official_number: str, eff_date: date, max_articles: int, scope_tags: List[str]) -> LegalDocumentParsed:
    print(f"\n[*] Đang bóc tách văn bản {title} ({official_number}) từ {html_path}...")
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
                    chapter_title=chap_m.group(2).strip() or f"Chương {chap_m.group(1)}",
                    articles=[],
                )
            continue

        # Article detection: Điều X. hoặc Điều X: hoặc Điều X
        art_m = re.match(r"^(?:Điều|ĐIỀU)\s+(\d+)[\.:\s]*(.*)", text)
        if art_m:
            art_num = int(art_m.group(1))
            if art_num <= max_articles and (current_art_num is None or art_num == current_art_num + 1):
                # Save previous article
                if current_art_num is not None and current_art_num not in articles:
                    articles[current_art_num] = {
                        "num": current_art_num,
                        "title": current_art_title,
                        "chapter": current_chapter,
                        "lines": current_art_lines,
                    }

                current_art_num = art_num
                current_art_title = art_m.group(2).strip()
                current_art_lines = [text]
                continue

        if current_art_num is not None:
            current_art_lines.append(text)

    # Save last article
    if current_art_num is not None and current_art_num not in articles and current_art_num <= max_articles:
        articles[current_art_num] = {
            "num": current_art_num,
            "title": current_art_title,
            "chapter": current_chapter,
            "lines": current_art_lines,
        }

    print(f" [+] Đã bóc tách được {len(articles)}/{max_articles} Điều luật.")

    # Convert to LegalArticle objects
    legal_articles = []
    for art_num in sorted(articles.keys()):
        art_data = articles[art_num]
        full_text = "\n".join(art_data["lines"]).strip()

        # Parse clauses
        clauses = []
        clause_blocks = []
        current_cl_num = None
        current_cl_lines = []

        clause_regex = re.compile(r"^(\d+)\.\s*(.*)")
        for line in art_data["lines"][1:]:  # skip title line
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
            effective_date=eff_date,
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
        issue_date=date(2025, 12, 10) if "109" in doc_id else date(2025, 6, 20),
        effective_date=eff_date,
        status=DocumentStatus.CON_HIEU_LUC,
        description=f"{title}, ban hành theo Luật số {official_number}",
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

        # Chunk toàn văn điều (<= 1400 chars hoặc <= 1 khoản)
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
                scope_tags=scope_tags,
            ))
        else:
            # Chunk toàn văn tổng quát
            chunks.append(LegalChunkPayload(
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
            ))

            # Gom các khoản
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
                            scope_tags=scope_tags,
                        ))
                    current_text = cl.text
                    current_clauses = [cl.clause_number]

            if current_text and current_clauses:
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
                    scope_tags=scope_tags,
                ))

    return chunks


def main():
    print("=" * 80)
    print("   INGESTION PIPELINE: CỤM THUẾ 2025/2026 (TNCN, TNDN, QUẢN LÝ THUẾ)")
    print("=" * 80)

    tax_configs = [
        {
            "html": PROJECT_ROOT / "data" / "01_raw" / "html" / "109_2025_QH15.html",
            "id": "tncn_109_2025_qh15",
            "title": "Luật Thuế thu nhập cá nhân 2025",
            "number": "109/2025/QH15",
            "date": date(2026, 7, 1),
            "max": 29,
            "tags": ["thuế", "thuế tncn", "thu nhập cá nhân", "giảm trừ gia cảnh", "tiền lương", "biểu thuế"]
        },
        {
            "html": PROJECT_ROOT / "data" / "01_raw" / "html" / "67_2025_QH15.html",
            "id": "tndn_67_2025_qh15",
            "title": "Luật Thuế thu nhập doanh nghiệp 2025",
            "number": "67/2025/QH15",
            "date": date(2025, 10, 1),
            "max": 20,
            "tags": ["thuế", "thuế tndn", "thu nhập doanh nghiệp", "chi phí được trừ", "thuế suất", "doanh nghiệp"]
        },
        {
            "html": PROJECT_ROOT / "data" / "01_raw" / "html" / "108_2025_QH15.html",
            "id": "qlt_108_2025_qh15",
            "title": "Luật Quản lý thuế 2025",
            "number": "108/2025/QH15",
            "date": date(2026, 7, 1),
            "max": 53,
            "tags": ["thuế", "quản lý thuế", "kê khai", "nộp thuế", "chậm nộp", "xử phạt"]
        }
    ]

    loader = SupabaseLegalLoader()
    all_chunks = []

    # 1. Parse & Upload Supabase
    for cfg in tax_configs:
        if not cfg["html"].exists():
            print(f"[!] Không tìm thấy file: {cfg['html']}")
            return

        doc = parse_tax_doc(
            html_path=cfg["html"],
            doc_id=cfg["id"],
            title=cfg["title"],
            official_number=cfg["number"],
            eff_date=cfg["date"],
            max_articles=cfg["max"],
            scope_tags=cfg["tags"]
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
    print(f" TỔNG SỐ CHUNKS MỚI CỦA CỤM THUẾ CẦN VECTOR HÓA: {len(all_chunks)} chunks")
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
    print(f"\n[+] HOÀN TẤT INGESTION CỤM THUẾ 2025/2026 THÀNH CÔNG RỰC RỠ!")
    print(f"    - Vector Points ban đầu: {before_count}")
    print(f"    - Vector Points bổ sung: +{len(all_chunks)}")
    print(f"    - Vector Points hiện tại: {after_count}")
    print("=" * 80)


if __name__ == "__main__":
    main()
