import os
import sys
import re
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


def parse_traffic_doc(
    html_path: Path,
    doc_id: str,
    title: str,
    official_number: str,
    doc_type: DocumentType,
    issue_date: date,
    effective_date: date,
    max_articles: int,
    scope_tags: List[str],
    amended_by: Optional[str] = None,
) -> LegalDocumentParsed:
    print(f"\n[*] Đang bóc tách văn bản: {title} ({official_number}) từ {html_path.name}...")
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

    articles_raw_dict = {}

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
            articles_raw_dict[art_num] = {
                "title": art_title,
                "chapter": current_chapter,
                "lines": [],
            }
        else:
            if expected_art > 1:
                cur_key = expected_art - 1
                if cur_key in articles_raw_dict:
                    articles_raw_dict[cur_key]["lines"].append(line)

    legal_articles = []
    for art_num in sorted(articles_raw_dict.keys()):
        art_data = articles_raw_dict[art_num]
        full_text = "\n".join(art_data["lines"]).strip()

        # Parse clauses (Khoản 1, Khoản 2, hoặc 1. , 2. )
        clauses = []
        clause_pattern = re.compile(r"^(?:Khoản\s+)?(\d+)[\.\)]\s*(.*)", re.IGNORECASE)
        clause_blocks = []
        current_cl_num = None
        current_cl_lines = []

        for l in art_data["lines"]:
            cl_m = clause_pattern.match(l)
            if cl_m and (current_cl_num is None or int(cl_m.group(1)) == current_cl_num + 1):
                if current_cl_num is not None:
                    clause_blocks.append((current_cl_num, "\n".join(current_cl_lines).strip()))
                current_cl_num = int(cl_m.group(1))
                current_cl_lines = [cl_m.group(2).strip() or l]
            else:
                current_cl_lines.append(l)

        if current_cl_num is not None:
            clause_blocks.append((current_cl_num, "\n".join(current_cl_lines).strip()))

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
        doc_type=doc_type,
        issuer="Chính phủ" if doc_type == DocumentType.NGHI_DINH else "Quốc hội",
        issue_date=issue_date,
        effective_date=effective_date,
        status=DocumentStatus.CON_HIEU_LUC,
        description=f"{title}, số hiệu {official_number}",
        amended_by=[amended_by] if amended_by else [],
    )

    return LegalDocumentParsed(
        metadata=meta,
        chapters=list(chapters_dict.values()),
        raw_articles=legal_articles,
    )


def build_traffic_chunks(doc: LegalDocumentParsed, scope_tags: List[str]) -> List[LegalChunkPayload]:
    meta = doc.metadata
    chunks = []

    art_to_ch = {}
    for ch in doc.chapters:
        for a in ch.articles:
            art_to_ch[a.article_number] = f"{ch.chapter_number}: {ch.chapter_title}"

    for art in doc.raw_articles:
        ch_info = art_to_ch.get(art.article_number, "")
        header_base = f"[{meta.title}] {ch_info} - Điều {art.article_number}: {art.article_title or ''}".strip()

        # Chunk toàn văn điều nếu ngắn (<= 1500 ký tự hoặc <= 1 khoản)
        if len(art.full_text) <= 1500 or len(art.clauses) <= 1:
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
            # 1. Chunk tổng quát điều (tóm lược đầu để bắt các truy vấn broad)
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
                    context_header=f"Điều {art.article_number}: {art.article_title or ''} (Tổng quan)",
                    content=art.full_text[:1200],
                    full_search_text=f"{header_base} (Tổng quan)\n{art.full_text[:1200]}",
                    scope_tags=scope_tags,
                )
            )

            # 2. Xử lý chuyên sâu cho từng Khoản với Triplet Header
            # Đặc biệt nếu là Nghị định xử phạt (NĐ 168), các Khoản quy định mức phạt hoặc trừ điểm rất dài
            for cl in art.clauses:
                # Trích xuất tóm tắt chế tài nếu có (ví dụ "Phạt tiền từ ... đến ...", "Bị tước quyền...", "Bị trừ điểm...")
                penalty_summary = ""
                first_line = cl.text.split("\n")[0] if cl.text else ""
                if "phạt tiền" in first_line.lower():
                    m_fine = re.search(r"phạt tiền từ\s+[^đến]+đến\s+[^đồng]+đồng", first_line, re.IGNORECASE)
                    if m_fine:
                        penalty_summary = f"[{m_fine.group(0).upper()}]"
                elif "trừ điểm" in first_line.lower():
                    penalty_summary = "[TRỪ ĐIỂM GIẤY PHÉP LÁI XE]"
                elif "tước quyền" in first_line.lower():
                    penalty_summary = "[TƯỚC QUYỀN SỬ DỤNG GIẤY PHÉP LÁI XE]"

                cl_header = f"{header_base} - Khoản {cl.clause_number} {penalty_summary}".strip()

                # Nếu khoản vừa phải (<= 1400 chars), lưu trọn vẹn
                if len(cl.text) <= 1400:
                    chunks.append(
                        LegalChunkPayload(
                            chunk_id=f"{meta.doc_id}_D{art.article_number}_K{cl.clause_number}",
                            doc_id=meta.doc_id,
                            doc_title=meta.title,
                            official_number=meta.official_number,
                            chapter=ch_info,
                            article_number=art.article_number,
                            article_title=art.article_title,
                            clause_number=cl.clause_number,
                            status=art.status,
                            effective_date=meta.effective_date,
                            expiry_date=meta.expiry_date,
                            context_header=f"Điều {art.article_number}: {art.article_title or ''} - Khoản {cl.clause_number}",
                            content=cl.text,
                            full_search_text=f"{cl_header}\n{cl.text}",
                            scope_tags=scope_tags,
                        )
                    )
                else:
                    # Khoản quá dài (chứa 10-30 điểm vi phạm a, b, c, d...):
                    # Tách thành các sub-chunk điểm vi phạm theo Triplet Header
                    sub_lines = cl.text.split("\n")
                    sub_chunk_lines = []
                    sub_part = 1

                    for sl in sub_lines:
                        sub_chunk_lines.append(sl)
                        cur_sub_len = sum(len(x) for x in sub_chunk_lines)
                        # Cắt khi đạt khoảng 1000 ký tự tại ranh giới điểm vi phạm
                        if cur_sub_len >= 1000 and re.match(r"^[a-zđ]\)", sl.strip(), re.I):
                            sub_text = "\n".join(sub_chunk_lines).strip()
                            chunks.append(
                                LegalChunkPayload(
                                    chunk_id=f"{meta.doc_id}_D{art.article_number}_K{cl.clause_number}_P{sub_part}",
                                    doc_id=meta.doc_id,
                                    doc_title=meta.title,
                                    official_number=meta.official_number,
                                    chapter=ch_info,
                                    article_number=art.article_number,
                                    article_title=art.article_title,
                                    clause_number=cl.clause_number,
                                    status=art.status,
                                    effective_date=meta.effective_date,
                                    expiry_date=meta.expiry_date,
                                    context_header=f"Điều {art.article_number}: {art.article_title or ''} - Khoản {cl.clause_number} (Phần {sub_part})",
                                    content=sub_text,
                                    full_search_text=f"{cl_header} (Phần {sub_part})\n{sub_text}",
                                    scope_tags=scope_tags,
                                )
                            )
                            sub_part += 1
                            sub_chunk_lines = []

                    if sub_chunk_lines:
                        sub_text = "\n".join(sub_chunk_lines).strip()
                        chunks.append(
                            LegalChunkPayload(
                                chunk_id=f"{meta.doc_id}_D{art.article_number}_K{cl.clause_number}_P{sub_part}",
                                doc_id=meta.doc_id,
                                doc_title=meta.title,
                                official_number=meta.official_number,
                                chapter=ch_info,
                                article_number=art.article_number,
                                article_title=art.article_title,
                                clause_number=cl.clause_number,
                                status=art.status,
                                effective_date=meta.effective_date,
                                expiry_date=meta.expiry_date,
                                context_header=f"Điều {art.article_number}: {art.article_title or ''} - Khoản {cl.clause_number} (Phần {sub_part})",
                                content=sub_text,
                                full_search_text=f"{cl_header} (Phần {sub_part})\n{sub_text}",
                                scope_tags=scope_tags,
                            )
                        )

    return chunks


def main():
    print("=" * 80)
    print("   INGESTION PIPELINE: CỤM GIAO THÔNG ĐƯỜNG BỘ (PHASE 4A - BƯỚC 1)")
    print("=" * 80)

    traffic_configs = [
        {
            "html": PROJECT_ROOT / "data" / "01_raw" / "html" / "36_2024_QH15.html",
            "id": "traffic_order_36_2024_qh15",
            "title": "Luật Trật tự, an toàn giao thông đường bộ 2024",
            "number": "36/2024/QH15",
            "doc_type": DocumentType.LUAT,
            "issue_date": date(2024, 6, 27),
            "effective_date": date(2025, 1, 1),
            "max": 89,
            "amended_by": None,
            "tags": [
                "giao_thong",
                "trat_tu_an_toan_giao_thong",
                "quy_tac_giao_thong",
                "giay_phep_lai_xe",
                "12_diem_gplx",
                "den_do",
                "toc_do",
                "nong_do_con",
                "mu_bao_hiem",
            ],
        },
        {
            "html": PROJECT_ROOT / "data" / "01_raw" / "html" / "35_2024_QH15.html",
            "id": "road_35_2024_qh15",
            "title": "Luật Đường bộ 2024",
            "number": "35/2024/QH15",
            "doc_type": DocumentType.LUAT,
            "issue_date": date(2024, 6, 27),
            "effective_date": date(2025, 1, 1),
            "max": 86,
            "amended_by": None,
            "tags": [
                "giao_thong",
                "duong_bo",
                "ket_cau_ha_tang",
                "duong_cao_toc",
                "van_tai_duong_bo",
                "phan_loai_duong",
            ],
        },
        {
            "html": PROJECT_ROOT / "data" / "01_raw" / "html" / "168_2024_ND_CP.html",
            "id": "traffic_penalty_168_2024_nd_cp",
            "title": "Nghị định 168/2024/NĐ-CP xử phạt vi phạm hành chính TTATGT và trừ điểm GPLX",
            "number": "168/2024/NĐ-CP",
            "doc_type": DocumentType.NGHI_DINH,
            "issue_date": date(2024, 12, 26),
            "effective_date": date(2025, 1, 1),
            "max": 55,
            "amended_by": "nd_238_2026_nd_cp",
            "tags": [
                "giao_thong",
                "xu_phat_giao_thong",
                "muc_phat_tien",
                "tru_diem_gplx",
                "tuoc_gplx",
                "xe_o_to",
                "xe_may",
                "nong_do_con",
                "toc_do",
                "vuot_den_do",
            ],
        },
        {
            "html": PROJECT_ROOT / "data" / "01_raw" / "html" / "151_2024_ND_CP.html",
            "id": "traffic_guideline_151_2024_nd_cp",
            "title": "Nghị định 151/2024/NĐ-CP hướng dẫn Luật Trật tự an toàn giao thông đường bộ",
            "number": "151/2024/NĐ-CP",
            "doc_type": DocumentType.NGHI_DINH,
            "issue_date": date(2024, 11, 15),
            "effective_date": date(2025, 1, 1),
            "max": 39,
            "amended_by": None,
            "tags": [
                "giao_thong",
                "huong_dan_giao_thong",
                "co_so_du_lieu_gt",
                "xe_uu_tien",
                "thiet_bi_giam_sat",
                "quy_giam_thieu_thiet_hai",
            ],
        },
    ]

    loader = SupabaseLegalLoader()
    all_chunks = []
    doc_stats = []

    # 1. Parse, tạo chunks & Upload Supabase
    for cfg in traffic_configs:
        if not cfg["html"].exists():
            print(f"[!] Không tìm thấy file: {cfg['html']}")
            return

        doc = parse_traffic_doc(
            html_path=cfg["html"],
            doc_id=cfg["id"],
            title=cfg["title"],
            official_number=cfg["number"],
            doc_type=cfg["doc_type"],
            issue_date=cfg["issue_date"],
            effective_date=cfg["effective_date"],
            max_articles=cfg["max"],
            scope_tags=cfg["tags"],
            amended_by=cfg["amended_by"],
        )

        doc_chunks = build_traffic_chunks(doc, cfg["tags"])
        all_chunks.extend(doc_chunks)
        print(f" [+] Tạo được {len(doc_chunks)} chunks cho {cfg['title']}")

        # Upload Supabase
        print(f" [*] Đồng bộ lên Supabase: {cfg['title']}...")
        loader.upsert_document(doc)
        arts_count = loader.upsert_articles(doc)
        print(f" [+] Đã lưu {arts_count} Điều luật lên Supabase!")

        doc_stats.append({
            "id": cfg["id"],
            "title": cfg["title"],
            "number": cfg["number"],
            "articles": arts_count,
            "chunks": len(doc_chunks),
            "effective_from": cfg["effective_date"].isoformat(),
            "effective_to": None,
            "status": "CON_HIEU_LUC",
            "amended_by": cfg["amended_by"],
        })

    print(f"\n================================================================================")
    print(f" TỔNG SỐ CHUNKS MỚI CỦA CỤM GIAO THÔNG (4 VĂN BẢN): {len(all_chunks)} chunks")
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
    print(f"\n[+] HOÀN TẤT INGESTION BƯỚC 1 CỤM GIAO THÔNG THÀNH CÔNG!")
    print(f"    - Vector Points ban đầu: {before_count}")
    print(f"    - Vector Points bổ sung: +{len(all_chunks)}")
    print(f"    - Vector Points hiện tại: {after_count}")
    print("=" * 80)

    # 3. In bảng số liệu nghiệm thu cho Mentor
    print("\n" + "=" * 80)
    print("   BÁO CÁO KẾT QUẢ NGHIỆM THU BƯỚC 1 (GỬI MENTOR)")
    print("=" * 80)
    print(f"{'Văn bản':<35} | {'Số hiệu':<15} | {'Số Điều':<8} | {'Số Chunks':<10} | {'Hiệu lực từ':<12} | {'Trạng thái'}")
    print("-" * 105)
    for s in doc_stats:
        print(f"{s['title'][:33]:<35} | {s['number']:<15} | {s['articles']:<8} | {s['chunks']:<10} | {s['effective_from']:<12} | {s['status']}")
    print("-" * 105)
    total_arts = sum(s['articles'] for s in doc_stats)
    total_chk = sum(s['chunks'] for s in doc_stats)
    print(f"{'TỔNG CỘNG 4 VĂN BẢN':<35} | {'':<15} | {total_arts:<8} | {total_chk:<10} | {'':<12} |")
    print("=" * 105)


if __name__ == "__main__":
    main()
