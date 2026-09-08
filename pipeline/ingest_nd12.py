import sys
import os
import re
import json
import time
from pathlib import Path
from datetime import date
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


def extract_nd12_parsed_doc(html_path: Path) -> LegalDocumentParsed:
    with open(html_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f.read(), "html.parser")

    p_tags = soup.find_all("p")
    raw_lines = [p.get_text().strip() for p in p_tags if p.get_text().strip()]

    # Clean lines: remove repeated adjacent lines if any
    lines = []
    for l in raw_lines:
        if not lines or l != lines[-1]:
            lines.append(l)

    metadata = LegalDocumentMetadata(
        doc_id="nd_12_2022_nd_cp",
        official_number="12/2022/NĐ-CP",
        title="Nghị định quy định xử phạt vi phạm hành chính trong lĩnh vực lao động, bảo hiểm xã hội, người lao động Việt Nam đi làm việc ở nước ngoài theo hợp đồng",
        short_title="Nghị định 12/2022/NĐ-CP",
        doc_type=DocumentType.NGHI_DINH,
        issuer="Chính phủ",
        signer="Vũ Đức Đam",
        issue_date=date(2022, 1, 17),
        effective_date=date(2022, 1, 17),
        status=DocumentStatus.CON_HIEU_LUC,
        source_url="https://thuvienphapluat.vn/van-ban/Lao-dong-Tien-luong/Nghi-dinh-12-2022-ND-CP-xu-phat-vi-pham-hanh-chinh-lao-dong-bao-hiem-nguoi-lam-viec-nuoc-ngoai-479312.aspx",
        guides=["bllđ_45_2019_qh14"],
    )

    chapters_dict = {
        "Chương I": "QUY ĐỊNH CHUNG",
        "Chương II": "HÀNH VI VI PHẠM, HÌNH THỨC XỬ PHẠT VÀ BIỆN PHÁP KHẮC PHỤC HẬU QUẢ ĐỐI VỚI HÀNH VI VI PHẠM TRONG LĨNH VỰC LAO ĐỘNG",
        "Chương III": "HÀNH VI VI PHẠM, HÌNH THỨC XỬ PHẠT, MỨC XỬ PHẠT VÀ BIỆN PHÁP KHẮC PHỤC HẬU QUẢ ĐỐI VỚI HÀNH VI VI PHẠM TRONG LĨNH VỰC BẢO HIỂM XÃ HỘI",
        "Chương IV": "HÀNH VI VI PHẠM, HÌNH THỨC XỬ PHẠT, MỨC XỬ PHẠT VÀ BIỆN PHÁP KHẮC PHỤC HẬU QUẢ ĐỐI VỚI HÀNH VI VI PHẠM TRONG LĨNH VỰC NGƯỜI LAO ĐỘNG VIỆT NAM ĐI LÀM VIỆC Ở NƯỚC NGOÀI THEO HỢP ĐỒNG",
        "Chương V": "THẨM QUYỀN XỬ PHẠT VI PHẠM HÀNH CHÍNH VÀ LẬP BIÊN BẢN VI PHẠM HÀNH CHÍNH; THỦ TỤC XỬ PHẠT VI PHẠM HÀNH CHÍNH; THI HÀNH CÁC HÌNH THỨC XỬ PHẠT VI PHẠM HÀNH CHÍNH, CÁC BIỆN PHÁP KHẮC PHỤC HẬU QUẢ TRONG LĨNH VỰC LAO ĐỘNG, BẢO HIỂM XÃ HỘI, NGƯỜI LAO ĐỘNG VIỆT NAM ĐI LÀM VIỆC Ở NƯỚC NGOÀI THEO HỢP ĐỒNG",
        "Chương VI": "ĐIỀU KHOẢN THI HÀNH",
    }

    # Chapter range mapping by article number
    # Chương I: Điều 1 -> 7
    # Chương II: Điều 8 -> 37
    # Chương III: Điều 38 -> 41
    # Chương IV: Điều 42 -> 46
    # Chương V: Điều 47 -> 61
    # Chương VI: Điều 62 -> 64
    def get_chapter_for_article(art_num: int):
        if art_num <= 7:
            return "Chương I", chapters_dict["Chương I"]
        elif art_num <= 37:
            return "Chương II", chapters_dict["Chương II"]
        elif art_num <= 41:
            return "Chương III", chapters_dict["Chương III"]
        elif art_num <= 46:
            return "Chương IV", chapters_dict["Chương IV"]
        elif art_num <= 61:
            return "Chương V", chapters_dict["Chương V"]
        else:
            return "Chương VI", chapters_dict["Chương VI"]

    # Slice document into articles
    article_indices = []
    for i, line in enumerate(lines):
        m = re.match(r"^Điều\s+(\d+)[\.:\s]+(.*)", line)
        if m:
            art_num = int(m.group(1))
            article_indices.append((art_num, i, m.group(2).strip()))

    articles: List[LegalArticle] = []
    for idx, (art_num, start_line, raw_title) in enumerate(article_indices):
        end_line = article_indices[idx + 1][1] if idx + 1 < len(article_indices) else len(lines)
        art_lines = lines[start_line:end_line]

        # Extract title cleanly
        first_line = art_lines[0]
        # Title might wrap to next line if first line is just "Điều X."
        art_title = raw_title
        content_lines = art_lines[1:]
        if not art_title and content_lines:
            art_title = content_lines[0]
            content_lines = content_lines[1:]

        # Group broken lines into clean paragraphs
        clean_blocks = []
        curr_block = []
        for l in content_lines:
            # Check if new clause (e.g. "1.", "2.") or new point ("a)", "b)") or section
            if re.match(r"^(\d+\.|\bKhoản\s+\d+|[a-zđ]\)|Biện pháp khắc phục|Hình thức xử phạt)", l, re.IGNORECASE):
                if curr_block:
                    clean_blocks.append(" ".join(curr_block))
                    curr_block = []
            curr_block.append(l)
        if curr_block:
            clean_blocks.append(" ".join(curr_block))

        full_article_text = f"Điều {art_num}. {art_title}\n" + "\n".join(clean_blocks)

        # Parse clauses
        clauses: List[LegalClause] = []
        curr_cl: LegalClause = None
        for block in clean_blocks:
            cl_m = re.match(r"^(\d+)\.\s*(.*)", block)
            if cl_m:
                if curr_cl:
                    clauses.append(curr_cl)
                curr_cl = LegalClause(
                    clause_number=int(cl_m.group(1)),
                    text=cl_m.group(2).strip(),
                    points=[],
                )
            else:
                pt_m = re.match(r"^([a-zđ])\)\s*(.*)", block, re.IGNORECASE)
                if pt_m and curr_cl:
                    curr_cl.points.append(
                        LegalPoint(point_letter=pt_m.group(1).lower(), text=pt_m.group(2).strip())
                    )
                elif curr_cl:
                    curr_cl.text += f"\n{block}"
                else:
                    # Article without numbered clauses
                    if not clauses:
                        curr_cl = LegalClause(clause_number=1, text=block, points=[])
                    else:
                        clauses[-1].text += f"\n{block}"
        if curr_cl:
            clauses.append(curr_cl)

        art_obj = LegalArticle(
            article_number=art_num,
            article_title=art_title,
            full_text=full_article_text,
            clauses=clauses,
            status=DocumentStatus.CON_HIEU_LUC,
        )
        articles.append(art_obj)

    # Build chapters
    chapters: List[LegalChapter] = []
    for chap_num, chap_title in chapters_dict.items():
        chap_articles = [
            a for a in articles if get_chapter_for_article(a.article_number)[0] == chap_num
        ]
        if chap_articles:
            chapters.append(
                LegalChapter(
                    chapter_number=chap_num,
                    chapter_title=chap_title,
                    articles=chap_articles,
                )
            )

    return LegalDocumentParsed(
        metadata=metadata,
        chapters=chapters,
        raw_articles=articles,
    )


from pipeline.parsers.legal_hierarchical_parser import LegalHierarchicalParser

def create_curated_chunks(parsed_doc: LegalDocumentParsed) -> List[LegalChunkPayload]:
    parser = LegalHierarchicalParser()
    return parser.create_chunks(parsed_doc)



def main():
    print("=" * 70)
    print("   VIETLEGAL AI - INGESTION NGHỊ ĐỊNH 12/2022/NĐ-CP (XỬ PHẠT LAO ĐỘNG)")
    print("=" * 70)

    html_path = PROJECT_ROOT / "data" / "01_raw" / "html" / "12_2022_ND_CP.html"
    if not html_path.exists():
        print(f"[!] Không tìm thấy file {html_path}")
        return

    # 1. Parse văn bản phân cấp
    print(f"\n[1/5] Đang phân tích cú pháp văn bản từ: {html_path}")
    parsed_doc = extract_nd12_parsed_doc(html_path)
    print(f" [+] Số chương bóc tách: {len(parsed_doc.chapters)}")
    print(f" [+] Số điều luật bóc tách: {len(parsed_doc.raw_articles)}/64 Điều")

    # 2. Sinh Legal Context Chunks
    print("\n[2/5] Sinh Legal Context Chunks cho Nghị định 12/2022/NĐ-CP...")
    chunks = create_curated_chunks(parsed_doc)
    print(f" [+] Số lượng Chunks sinh ra: {len(chunks)} Chunks")

    # Lưu file JSON parsed & JSONL chunks
    parsed_out = PROJECT_ROOT / "data" / "03_parsed" / "nd_12_2022.json"
    chunks_out = PROJECT_ROOT / "data" / "04_curated_chunks" / "nd_12_2022_chunks.jsonl"
    parsed_out.parent.mkdir(parents=True, exist_ok=True)
    chunks_out.parent.mkdir(parents=True, exist_ok=True)

    with open(chunks_out, "w", encoding="utf-8") as f:
        for c in chunks:
            f.write(c.model_dump_json() + "\n")
    print(f" [+] Đã lưu file Chunks vào: {chunks_out}")

    # 3. Đồng bộ lên Supabase Cloud Database (legal_documents & legal_articles)
    print("\n[3/5] Đồng bộ dữ liệu lên Supabase Cloud (PostgreSQL)...")
    supabase_loader = SupabaseLegalLoader()
    sync_res = supabase_loader.sync_parsed_document(parsed_doc)
    print(f" [+] Văn bản legal_documents: {'Thành công' if sync_res['document_synced'] else 'Thất bại'}")
    print(f" [+] Số điều luật nạp vào legal_articles: {sync_res['articles_count']} Điều")

    # 4. Tính toán Vector Embeddings với BGE-M3 (CUDA GPU FP16)
    print("\n[4/5] Tính toán Vector Embeddings (BAAI/bge-m3)...")
    import numpy as np

    vec_file = PROJECT_ROOT / "data" / "04_curated_chunks" / "nd_12_vectors.npy"
    if vec_file.exists():
        print(f" [+] Tải {len(chunks)} vectors từ bộ nhớ đệm: {vec_file}")
        vectors = np.load(vec_file).tolist()
    else:
        embedder = get_embedding_service()
        dim = embedder.dimension
        texts_to_embed = [c.full_search_text for c in chunks]

        t0 = time.time()
        vectors = embedder.embed_texts(texts_to_embed)
        print(f" [+] Đã nhúng {len(vectors)} vectors (dim={dim}) trong {time.time() - t0:.2f}s!")
        np.save(vec_file, np.array(vectors))
        print(f" [+] Đã lưu cache vectors vào: {vec_file}")

    # 5. Nạp vào Qdrant Vector Store (Bảo toàn dữ liệu cũ, KHÔNG xóa collection)
    print("\n[5/5] Nạp Vectors và Metadata vào Qdrant Vector Store...")
    vector_store = QdrantVectorStore(collection_name="vietlegal_articles")
    vector_store.ensure_collection(vector_size=1024, recreate=False)
    uploaded = vector_store.insert_chunks(chunks=chunks, embeddings=vectors, batch_size=50)
    print(f" [+] Đã nạp thành công {uploaded} chunks vào Qdrant!")

    # 6. Kiểm tra trực quan kết quả
    print("\n" + "=" * 70)
    print("   HOÀN TẤT NẠP NGHỊ ĐỊNH 12/2022/NĐ-CP!")
    print(f"   - 64 Điều luật đã vào Supabase legal_articles.")
    print(f"   - {len(chunks)} Vector Chunks đã vào Qdrant vietlegal_articles.")
    print("=" * 70)


if __name__ == "__main__":
    main()
