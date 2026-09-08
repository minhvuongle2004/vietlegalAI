import sys
import os
import re
import json
import time
from pathlib import Path
from datetime import date
from typing import List, Dict, Any, Tuple
import numpy as np

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
from pipeline.parsers.legal_hierarchical_parser import LegalHierarchicalParser
from pipeline.loaders.supabase_loader import SupabaseLegalLoader
from backend.app.services.rag.embeddings import get_embedding_service
from backend.app.services.rag.vector_store import QdrantVectorStore


ND01_CHAPTERS = [
    ("Chương I", "QUY ĐỊNH CHUNG", 1, 13),
    ("Chương II", "NHIỆM VỤ, QUYỀN HẠN CỦA CƠ QUAN ĐĂNG KÝ KINH DOANH VÀ QUẢN LÝ NHÀ NƯỚC VỀ ĐĂNG KÝ DOANH NGHIỆP, ĐĂNG KÝ HỘ KINH DOANH", 14, 17),
    ("Chương III", "ĐĂNG KÝ TÊN DOANH NGHIỆP, CHI NHÁNH, VĂN PHÒNG ĐẠI DIỆN, ĐỊA ĐIỂM KINH DOANH", 18, 20),
    ("Chương IV", "HỒ SƠ, TRÌNH TỰ, THỦ TỤC ĐĂNG KÝ DOANH NGHIỆP, ĐĂNG KÝ HOẠT ĐỘNG CHI NHÁNH, VĂN PHÒNG ĐẠI DIỆN, ĐỊA ĐIỂM KINH DOANH", 21, 41),
    ("Chương V", "ĐĂNG KÝ DOANH NGHIỆP QUA MẠNG THÔNG TIN ĐIỆN TỬ", 42, 46),
    ("Chương VI", "HỒ SƠ, TRÌNH TỰ, THỦ TỤC ĐĂNG KÝ THAY ĐỔI, THÔNG BÁO THAY ĐỔI NỘI DUNG ĐĂNG KÝ DOANH NGHIỆP", 47, 65),
    ("Chương VII", "HỒ SƠ, TRÌNH TỰ, THỦ TỤC ĐĂNG KÝ TẠM NGỪNG KINH DOANH, CẤP LẠI GIẤY CHỨNG NHẬN ĐĂNG KÝ DOANH NGHIỆP, GIẢI THỂ DOANH NGHIỆP, THU HỒI GIẤY CHỨNG NHẬN ĐĂNG KÝ DOANH NGHIỆP", 66, 78),
    ("Chương VIII", "HỘ KINH DOANH VÀ ĐĂNG KÝ HỘ KINH DOANH", 79, 94),
    ("Chương IX", "ĐIỀU KHOẢN THI HÀNH", 95, 101),
]

ND122_CHAPTERS = [
    ("Chương I", "QUY ĐỊNH CHUNG", 1, 5),
    ("Chương II", "HÀNH VI VI PHẠM HÀNH CHÍNH TRONG LĨNH VỰC ĐẦU TƯ, HÌNH THỨC XỬ PHẠT, MỨC XỬ PHẠT VÀ BIỆN PHÁP KHẮC PHỤC HẬU QUẢ", 6, 31),
    ("Chương III", "HÀNH VI VI PHẠM HÀNH CHÍNH TRONG LĨNH VỰC ĐẤU THẦU, HÌNH THỨC XỬ PHẠT, MỨC XỬ PHẠT VÀ BIỆN PHÁP KHẮC PHỤC HẬU QUẢ", 32, 42),
    ("Chương IV", "VI PHẠM HÀNH CHÍNH TRONG LĨNH VỰC ĐĂNG KÝ DOANH NGHIỆP, HÌNH THỨC XỬ PHẠT, MỨC XỬ PHẠT VÀ BIỆN PHÁP KHẮC PHỤC HẬU QUẢ", 43, 69),
    ("Chương V", "VI PHẠM HÀNH CHÍNH TRONG LĨNH VỰC QUY HOẠCH, HÌNH THỨC XỬ PHẠT, MỨC XỬ PHẠT VÀ BIỆN PHÁP KHẮC PHỤC HẬU QUẢ", 70, 72),
    ("Chương VI", "THẨM QUYỀN XỬ PHẠT VI PHẠM HÀNH CHÍNH", 73, 79),
    ("Chương VII", "ĐIỀU KHOẢN THI HÀNH", 80, 82),
]


def parse_generic_decree(
    html_path: Path,
    metadata: LegalDocumentMetadata,
    chapter_defs: List[Tuple[str, str, int, int]],
) -> LegalDocumentParsed:
    with open(html_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f.read(), "html.parser")

    for t in soup.find_all("table"):
        t.decompose()

    p_tags = [" ".join(p.get_text().split()) for p in soup.find_all("p") if p.get_text().strip()]
    lines = []
    for l in p_tags:
        if not lines or l != lines[-1]:
            lines.append(l)

    art_indices = []
    for i, l in enumerate(lines):
        m = re.match(r"^Điều\s+(\d+)[\.:\s]+(.*)", l)
        if m:
            art_num = int(m.group(1))
            raw_title = m.group(2).strip()
            art_indices.append((art_num, i, raw_title))

    articles: List[LegalArticle] = []
    for idx, (art_num, start_i, raw_title) in enumerate(art_indices):
        end_i = art_indices[idx + 1][1] if idx + 1 < len(art_indices) else len(lines)
        art_lines = lines[start_i:end_i]

        art_title = raw_title
        content_lines = art_lines[1:]
        if not art_title and content_lines:
            art_title = content_lines[0]
            content_lines = content_lines[1:]

        clean_blocks = []
        curr_block = []
        for l in content_lines:
            if re.match(r"^(\d+\.|\bKhoản\s+\d+|[a-zđ]\)|Biện pháp khắc phục|Hình thức xử phạt)", l, re.IGNORECASE):
                if curr_block:
                    clean_blocks.append(" ".join(curr_block))
                    curr_block = []
            curr_block.append(l)
        if curr_block:
            clean_blocks.append(" ".join(curr_block))

        full_text = f"Điều {art_num}. {art_title}\n" + "\n".join(clean_blocks)

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
                    if not clauses:
                        curr_cl = LegalClause(clause_number=1, text=block, points=[])
                    else:
                        clauses[-1].text += f"\n{block}"
        if curr_cl:
            clauses.append(curr_cl)

        art_obj = LegalArticle(
            article_number=art_num,
            article_title=f"Điều {art_num}. {art_title}",
            full_text=full_text,
            clauses=clauses,
            status=DocumentStatus.CON_HIEU_LUC,
        )
        articles.append(art_obj)

    chapters: List[LegalChapter] = []
    for chap_id, chap_title, start_art, end_art in chapter_defs:
        chap_articles = [a for a in articles if start_art <= a.article_number <= end_art]
        chapters.append(
            LegalChapter(
                chapter_number=chap_id,
                chapter_title=chap_title,
                articles=chap_articles,
            )
        )

    return LegalDocumentParsed(
        metadata=metadata,
        chapters=chapters,
        raw_articles=articles,
    )


def main():
    print("=" * 70)
    print("   VIETLEGAL AI - INGESTION NGHỊ ĐỊNH 01/2021 & NGHỊ ĐỊNH 122/2021")
    print("=" * 70)

    # 1. Khai báo Metadata
    meta_nd01 = LegalDocumentMetadata(
        doc_id="nd_01_2021_nd_cp",
        official_number="01/2021/NĐ-CP",
        title="Nghị định về đăng ký doanh nghiệp",
        short_title="Nghị định 01/2021/NĐ-CP",
        doc_type=DocumentType.NGHI_DINH,
        issuer="Chính phủ",
        signer="Nguyễn Xuân Phúc",
        issue_date=date(2021, 1, 4),
        effective_date=date(2021, 1, 4),
        status=DocumentStatus.CON_HIEU_LUC,
        source_url="https://thuvienphapluat.vn/van-ban/Doanh-nghiep/Nghi-dinh-01-2021-ND-CP-dang-ky-doanh-nghiep-283247.aspx",
        guides=["ldn_59_2020_qh14"],
        replaces=["78/2015/NĐ-CP", "108/2018/NĐ-CP"],
    )

    meta_nd122 = LegalDocumentMetadata(
        doc_id="nd_122_2021_nd_cp",
        official_number="122/2021/NĐ-CP",
        title="Nghị định quy định về xử phạt vi phạm hành chính trong lĩnh vực kế hoạch và đầu tư",
        short_title="Nghị định 122/2021/NĐ-CP",
        doc_type=DocumentType.NGHI_DINH,
        issuer="Chính phủ",
        signer="Lê Minh Khái",
        issue_date=date(2021, 12, 28),
        effective_date=date(2022, 1, 1),
        status=DocumentStatus.CON_HIEU_LUC,
        source_url="https://thuvienphapluat.vn/van-ban/Dau-tu/Nghi-dinh-122-2021-ND-CP-xu-phat-vi-pham-hanh-chinh-linh-vuc-ke-hoach-285024.aspx",
        guides=["ldn_59_2020_qh14"],
        replaces=["50/2016/NĐ-CP"],
    )

    p_nd01 = PROJECT_ROOT / "data" / "01_raw" / "html" / "01_2021_ND_CP.html"
    p_nd122 = PROJECT_ROOT / "data" / "01_raw" / "html" / "122_2021_ND_CP.html"

    docs_to_ingest = [
        ("Nghị định 01/2021/NĐ-CP (Đăng ký doanh nghiệp)", p_nd01, meta_nd01, ND01_CHAPTERS),
        ("Nghị định 122/2021/NĐ-CP (Xử phạt VPHC kế hoạch và đầu tư)", p_nd122, meta_nd122, ND122_CHAPTERS),
    ]

    all_chunks: List[LegalChunkPayload] = []
    parser = LegalHierarchicalParser()
    curated_dir = PROJECT_ROOT / "data" / "04_curated_chunks"
    curated_dir.mkdir(parents=True, exist_ok=True)

    # 2. Bóc tách và Chunking
    for doc_name, html_path, meta, chap_defs in docs_to_ingest:
        print(f"\n[1/4] Bóc tách văn bản: {doc_name}...")
        parsed_doc = parse_generic_decree(html_path, meta, chap_defs)
        print(f" [+] Số chương: {len(parsed_doc.chapters)}, Số điều luật: {len(parsed_doc.raw_articles)}")

        chunks = parser.create_chunks(parsed_doc)
        print(f" [+] Sinh thành công: {len(chunks)} chunks phân cấp.")
        all_chunks.extend(chunks)

        jsonl_path = curated_dir / f"{meta.doc_id}_chunks.jsonl"
        with open(jsonl_path, "w", encoding="utf-8") as f:
            for c in chunks:
                f.write(c.model_dump_json() + "\n")
        print(f" [+] Đã lưu file: {jsonl_path.name}")

        # Đồng bộ Supabase
        print(f" [+] Đồng bộ dữ liệu {meta.short_title} lên Supabase...")
        supabase_loader = SupabaseLegalLoader()
        res = supabase_loader.sync_parsed_document(parsed_doc)
        print(f"     -> doc_synced={res['document_synced']}, articles={res['articles_count']}")

    # 3. Tính Vector Embeddings với BAAI/bge-m3 (CUDA GPU FP16)
    print(f"\n[2/4] Tính toán Vector Embeddings cho {len(all_chunks)} Chunks bằng BAAI/bge-m3...")
    vec_path = curated_dir / "enterprise_decrees_vectors.npy"
    if vec_path.exists():
        print(f" [+] Tải {len(all_chunks)} vectors từ bộ nhớ đệm: {vec_path.name}")
        vectors = np.load(vec_path).tolist()
    else:
        embed_service = get_embedding_service()
        texts_to_embed = [c.full_search_text for c in all_chunks]
        t0 = time.time()
        embed_service.model.max_seq_length = 2048
        raw_vecs = embed_service.model.encode(
            texts_to_embed,
            batch_size=4,
            normalize_embeddings=True,
            show_progress_bar=True,
        )
        vectors = raw_vecs.tolist()
        elapsed = time.time() - t0
        print(f" [+] Đã tạo thành công {len(vectors)} vectors (dim={len(vectors[0])}) trong {elapsed:.2f}s!")
        np.save(vec_path, np.array(vectors, dtype=np.float32))
        print(f" [+] Đã lưu cache vectors vào: {vec_path.name}")

    # 4. Nạp vào Qdrant Vector Store (Bảo toàn dữ liệu cũ: recreate=False)
    print(f"\n[3/4] Nạp Vector Chunks vào Qdrant Vector Store (recreate=False)...")
    vector_store = QdrantVectorStore(collection_name="vietlegal_articles")
    vector_store.ensure_collection(vector_size=1024, recreate=False)
    uploaded = vector_store.insert_chunks(chunks=all_chunks, embeddings=vectors, batch_size=50)
    print(f" [+] Đã nạp thành công {uploaded} chunks vào Qdrant!")

    total_vectors = vector_store.client.count(collection_name=vector_store.collection_name).count
    print(f" [+] Qdrant collection 'vietlegal_articles' hiện có tổng cộng: {total_vectors} vectors!")

    print("\n" + "=" * 70)
    print("[SUCCESS] ĐÃ HOÀN TẤT NẠP NGHỊ ĐỊNH 01/2021 VÀ NGHỊ ĐỊNH 122/2021!")
    print(f"          - 101 Điều (NĐ 01) + 82 Điều (NĐ 122) = 183 Điều luật mới.")
    print(f"          - {len(all_chunks)} Vector Chunks mới đã vào Qdrant (Tổng vector: {total_vectors}).")
    print("=" * 70)


if __name__ == "__main__":
    main()
