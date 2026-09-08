import sys
import os
import re
import json
import time
from pathlib import Path
from datetime import date
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


def parse_html_to_lines(html_path: Path) -> List[str]:
    with open(html_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f.read(), "html.parser")
    p_tags = soup.find_all(["p", "div"])
    raw_lines = [re.sub(r"\s+", " ", p.get_text()).strip() for p in p_tags if p.get_text().strip()]
    lines = []
    for l in raw_lines:
        if not lines or l != lines[-1]:
            lines.append(l)
    return lines


def extract_chapters_from_lines(lines: List[str]) -> List[Dict[str, Any]]:
    chapters = []
    for i, l in enumerate(lines):
        m = re.match(r"^Chương\s+([IVXLCDM\d]+)[\.:\s]*(.*)", l, re.IGNORECASE)
        if m:
            num = m.group(1).upper()
            title = m.group(2).strip()
            if not title and i + 1 < len(lines):
                title = lines[i + 1].strip()
            chapters.append({
                "chapter_index": len(chapters) + 1,
                "chapter_number": f"Chương {num}",
                "chapter_title": title,
                "line_idx": i
            })
    return chapters


def parse_legal_law_document(
    html_path: Path,
    metadata: LegalDocumentMetadata,
    expected_articles: int
) -> LegalDocumentParsed:
    lines = parse_html_to_lines(html_path)
    raw_chapters = extract_chapters_from_lines(lines)

    # Tìm vị trí bắt đầu của từng Điều
    art_indices = []
    for i, l in enumerate(lines):
        m = re.match(r"^Điều\s+(\d+)[\.:\s]*(.*)", l)
        if m:
            art_num = int(m.group(1))
            raw_title = m.group(2).strip()
            art_indices.append((art_num, i, raw_title))

    # Lọc bỏ trùng điều (chỉ lấy điều xuất hiện đầu tiên)
    unique_art_indices = []
    seen_art_nums = set()
    for art_num, i, raw_title in art_indices:
        if art_num not in seen_art_nums:
            seen_art_nums.add(art_num)
            unique_art_indices.append((art_num, i, raw_title))

    articles: List[LegalArticle] = []

    # Ghép Điều vào Chương tương ứng
    for idx, (art_num, start_i, raw_title) in enumerate(unique_art_indices):
        end_i = unique_art_indices[idx + 1][1] if idx + 1 < len(unique_art_indices) else len(lines)
        art_lines = lines[start_i:end_i]

        art_title = raw_title
        content_lines = art_lines[1:]
        if not art_title and content_lines:
            art_title = content_lines[0]
            content_lines = content_lines[1:]

        # Gom khối các khoản, điểm
        clean_blocks = []
        curr_block = []
        for l in content_lines:
            # Bắt đầu Khoản (1., 2.) hoặc Điểm (a), b))
            if re.match(r"^(\d+\.|\bKhoản\s+\d+|[a-zđ]\))", l, re.IGNORECASE):
                if curr_block:
                    clean_blocks.append(" ".join(curr_block))
                    curr_block = []
            curr_block.append(l)
        if curr_block:
            clean_blocks.append(" ".join(curr_block))

        full_text = f"Điều {art_num}. {art_title}\n" + "\n".join(clean_blocks)

        # Tách Khoản & Điểm
        clauses: List[LegalClause] = []
        curr_cl: Optional[LegalClause] = None
        for block in clean_blocks:
            cl_m = re.match(r"^(\d+)\.\s*(.*)", block, re.DOTALL)
            if cl_m:
                if curr_cl:
                    clauses.append(curr_cl)
                cl_num = int(cl_m.group(1))
                cl_text = cl_m.group(2).strip()
                curr_cl = LegalClause(
                    clause_number=cl_num,
                    text=f"{cl_num}. {cl_text}",
                    points=[]
                )
            elif curr_cl:
                pt_m = re.match(r"^([a-zđ])\)\s*(.*)", block, re.IGNORECASE | re.DOTALL)
                if pt_m:
                    curr_cl.points.append(LegalPoint(
                        point_letter=pt_m.group(1).lower(),
                        text=pt_m.group(2).strip()
                    ))
                else:
                    curr_cl.text += " " + block.strip()
            else:
                pass
        if curr_cl:
            clauses.append(curr_cl)

        article_obj = LegalArticle(
            article_number=art_num,
            article_title=art_title,
            full_text=full_text,
            clauses=clauses,
        )
        articles.append(article_obj)

    # Đóng gói Chapters
    parsed_chapters: List[LegalChapter] = []
    if raw_chapters:
        for c_idx, c in enumerate(raw_chapters):
            c_start = c["line_idx"]
            c_end = raw_chapters[c_idx + 1]["line_idx"] if c_idx + 1 < len(raw_chapters) else len(lines)
            chap_arts = []
            for art_idx, (art_num, start_i, _) in enumerate(unique_art_indices):
                if c_start <= start_i < c_end:
                    chap_arts.append(articles[art_idx])
            parsed_chapters.append(LegalChapter(
                chapter_number=c["chapter_number"],
                chapter_title=c["chapter_title"],
                articles=chap_arts
            ))
    else:
        parsed_chapters.append(LegalChapter(
            chapter_number="Chương I",
            chapter_title="Toàn văn",
            articles=articles
        ))

    return LegalDocumentParsed(
        metadata=metadata,
        chapters=parsed_chapters,
        raw_articles=articles
    )


def create_curated_chunks(parsed_doc: LegalDocumentParsed) -> List[LegalChunkPayload]:
    """
    Tạo chunks phân cấp:
    1. LUÔN LUÔN tạo Chunk ARTICLE_FULL cho mỗi Điều luật (đảm bảo không bị sót toàn bộ ngữ cảnh của Điều).
    2. Nếu Điều có từ 2 Khoản trở lên, tạo THÊM các Chunk CLAUSE chi tiết cho từng Khoản.
    """
    chunks: List[LegalChunkPayload] = []
    meta = parsed_doc.metadata

    # Map article_number -> chapter_info
    article_to_chapter = {}
    for ch in parsed_doc.chapters:
        for art in ch.articles:
            article_to_chapter[art.article_number] = f"{ch.chapter_number}: {ch.chapter_title}"

    for art in parsed_doc.raw_articles:
        chapter_info = article_to_chapter.get(art.article_number, "Quy định chung")
        context_header = (
            f"Văn bản: {meta.title} (Số hiệu: {meta.official_number}). "
            f"{chapter_info}. "
            f"Điều {art.article_number}: {art.article_title or ''}."
        )

        # 1. Chunk Toàn văn Điều luật (LUÔN CÓ)
        chunk_id_full = f"{meta.doc_id}_d{art.article_number}"
        chunks.append(
            LegalChunkPayload(
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
                scope_tags=[meta.doc_type.value.lower()],
            )
        )

        # 2. Nếu Điều có nhiều Khoản, tạo thêm chunk chi tiết cho từng Khoản
        if len(art.clauses) > 1:
            for cl in art.clauses:
                chunk_id_cl = f"{meta.doc_id}_d{art.article_number}_k{cl.clause_number}"
                clause_content = f"Khoản {cl.clause_number}: {cl.text}"
                if cl.points:
                    points_text = "\n".join([f"{p.point_letter}) {p.text}" for p in cl.points])
                    clause_content += f"\n{points_text}"

                chunks.append(
                    LegalChunkPayload(
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
                        context_header=context_header,
                        content=clause_content,
                        full_search_text=f"{context_header}\n{clause_content}",
                        scope_tags=[meta.doc_type.value.lower()],
                    )
                )

    return chunks


def ingest_document(
    html_path: Path,
    metadata: LegalDocumentMetadata,
    expected_articles: int,
    vec_cache_name: str,
    supabase_loader: SupabaseLegalLoader,
    vector_store: QdrantVectorStore,
    embedder: Any,
):
    print("\n" + "=" * 70)
    print(f"   INGESTING: {metadata.short_title} ({metadata.official_number})")
    print("=" * 70)

    # 1. Phân tích cú pháp
    print(f"[1/4] Đang bóc tách văn bản từ {html_path.name}...")
    parsed_doc = parse_legal_law_document(html_path, metadata, expected_articles)
    print(f" [+] Số chương bóc tách: {len(parsed_doc.chapters)}")
    print(f" [+] Số điều bóc tách: {len(parsed_doc.raw_articles)}/{expected_articles} Điều")

    # 2. Sinh Legal Context Chunks
    print(f"[2/4] Sinh Legal Context Chunks...")
    chunks = create_curated_chunks(parsed_doc)
    print(f" [+] Tổng số chunks sinh ra: {len(chunks)}")

    # Lưu bản parsed và chunks ra file
    doc_slug = metadata.doc_id
    parsed_out = PROJECT_ROOT / "data" / "03_parsed" / f"{doc_slug}.json"
    chunks_out = PROJECT_ROOT / "data" / "04_curated_chunks" / f"{doc_slug}_chunks.jsonl"
    parsed_out.parent.mkdir(parents=True, exist_ok=True)
    chunks_out.parent.mkdir(parents=True, exist_ok=True)

    with open(chunks_out, "w", encoding="utf-8") as f:
        for c in chunks:
            f.write(c.model_dump_json() + "\n")
    print(f" [+] Đã lưu file Chunks vào: {chunks_out.name}")

    # 3. Đồng bộ Supabase Cloud
    print(f"[3/4] Đồng bộ Supabase Cloud (legal_documents & legal_articles)...")
    sync_res = supabase_loader.sync_parsed_document(parsed_doc)
    print(f" [+] Supabase Document: {'OK' if sync_res['document_synced'] else 'FAIL'}")
    print(f" [+] Supabase Articles Synced: {sync_res['articles_count']} Điều")

    # 4. Tính toán Vector Embeddings BGE-M3 (CUDA FP16)
    print(f"[4/4] Tính toán Vectors BGE-M3 & Nạp Qdrant...")
    import numpy as np

    vec_file = PROJECT_ROOT / "data" / "04_curated_chunks" / f"{vec_cache_name}.npy"
    cached_vecs = np.load(vec_file) if vec_file.exists() else None
    if cached_vecs is not None and len(cached_vecs) == len(chunks):
        print(f" [+] Tải {len(chunks)} vectors từ bộ nhớ đệm: {vec_file.name}")
        vectors = cached_vecs.tolist()
    else:
        dim = embedder.dimension
        texts_to_embed = [c.full_search_text for c in chunks]
        t0 = time.time()
        vectors = embedder.embed_texts(texts_to_embed)
        print(f" [+] Đã nhúng {len(vectors)} vectors (dim={dim}) trong {time.time() - t0:.2f}s!")
        np.save(vec_file, np.array(vectors))
        print(f" [+] Đã lưu cache vectors vào: {vec_file.name}")

    uploaded = vector_store.insert_chunks(chunks=chunks, embeddings=vectors, batch_size=50)
    print(f" [+] Đã nạp thành công {uploaded} chunks vào Qdrant vietlegal_articles!")
    return len(parsed_doc.raw_articles), len(chunks)


def main():
    print("=" * 70)
    print("   VIETLEGAL AI - NẠP DỮ LIỆU CỤM 3: BẢO HIỂM XÃ HỘI & VIỆC LÀM")
    print("=" * 70)

    # 1. Định nghĩa Metadata Luật BHXH 2014
    meta_bhxh = LegalDocumentMetadata(
        doc_id="bhxh_58_2014_qh13",
        official_number="58/2014/QH13",
        title="Luật Bảo hiểm xã hội",
        short_title="Luật Bảo hiểm xã hội 2014",
        doc_type=DocumentType.LUAT,
        issuer="Quốc hội",
        signer="Nguyễn Sinh Hùng",
        issue_date=date(2014, 11, 20),
        effective_date=date(2016, 1, 1),
        status=DocumentStatus.CON_HIEU_LUC,
        source_url="https://thuvienphapluat.vn/van-ban/Bao-hiem/Luat-Bao-hiem-xa-hoi-2014-259700.aspx",
    )

    # 2. Định nghĩa Metadata Luật Việc làm 2013
    meta_vieclam = LegalDocumentMetadata(
        doc_id="vieclam_38_2013_qh13",
        official_number="38/2013/QH13",
        title="Luật Việc làm",
        short_title="Luật Việc làm 2013",
        doc_type=DocumentType.LUAT,
        issuer="Quốc hội",
        signer="Nguyễn Sinh Hùng",
        issue_date=date(2013, 11, 16),
        effective_date=date(2015, 1, 1),
        status=DocumentStatus.CON_HIEU_LUC,
        source_url="https://thuvienphapluat.vn/van-ban/Lao-dong-Tien-luong/Luat-viec-lam-nam-2013-215628.aspx",
    )

    supabase_loader = SupabaseLegalLoader()
    vector_store = QdrantVectorStore(collection_name="vietlegal_articles")
    vector_store.ensure_collection(vector_size=1024, recreate=False)
    embedder = get_embedding_service()

    # Nạp Luật Bảo hiểm xã hội 2014
    bhxh_html = PROJECT_ROOT / "data" / "01_raw" / "html" / "58_2014_QH13.html"
    bhxh_arts, bhxh_chunks = ingest_document(
        html_path=bhxh_html,
        metadata=meta_bhxh,
        expected_articles=125,
        vec_cache_name="bhxh_58_vectors",
        supabase_loader=supabase_loader,
        vector_store=vector_store,
        embedder=embedder,
    )

    # Nạp Luật Việc làm 2013
    vieclam_html = PROJECT_ROOT / "data" / "01_raw" / "html" / "38_2013_QH13.html"
    vl_arts, vl_chunks = ingest_document(
        html_path=vieclam_html,
        metadata=meta_vieclam,
        expected_articles=62,
        vec_cache_name="vieclam_38_vectors",
        supabase_loader=supabase_loader,
        vector_store=vector_store,
        embedder=embedder,
    )

    print("\n" + "=" * 70)
    print("   HOÀN TẤT NẠP TOÀN BỘ CỤM 3 (BHXH & VIỆC LÀM)!")
    print(f"   - Luật BHXH 2014: {bhxh_arts} Điều | {bhxh_chunks} Vector Chunks")
    print(f"   - Luật Việc làm 2013: {vl_arts} Điều | {vl_chunks} Vector Chunks")
    print(f"   - Tổng cộng thêm mới: {bhxh_arts + vl_arts} Điều | {bhxh_chunks + vl_chunks} Chunks")
    print("=" * 70)


if __name__ == "__main__":
    main()
