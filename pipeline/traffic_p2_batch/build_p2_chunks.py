import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
import os
import json
import uuid
import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
PARSED_FILE = PROJECT_ROOT / "data" / "03_parsed" / "traffic_p2_batch" / "traffic_road_law_detail_165_2024_nd_cp.json"
AMENDMENT_MANIFEST_FILE = PROJECT_ROOT / "pipeline" / "traffic_p2_batch" / "nd165_nd241_amendment_manifest.json"
DELEGATION_MANIFEST_FILE = PROJECT_ROOT / "pipeline" / "traffic_p2_batch" / "authority_delegation_manifest.json"
OUTPUT_CHUNKS_FILE = PROJECT_ROOT / "data" / "03_parsed" / "traffic_p2_batch" / "traffic_p2_chunks.json"

def build_chunks():
    print("=" * 80)
    print("   BUILDING TRAFFIC P2 CHUNKS (NĐ 165/2024 + NĐ 241 AMENDMENT OVERLAY)")
    print("=" * 80)

    with open(PARSED_FILE, "r", encoding="utf-8") as f:
        parsed_doc = json.load(f)

    with open(AMENDMENT_MANIFEST_FILE, "r", encoding="utf-8") as f:
        amend_manifest = json.load(f)

    with open(DELEGATION_MANIFEST_FILE, "r", encoding="utf-8") as f:
        deleg_manifest = json.load(f)

    meta = parsed_doc["metadata"]
    doc_id = meta["document_id"]
    official_num = meta["official_number"]
    doc_title = meta["title"]
    source_url = meta["source_url"]
    sha256 = meta["sha256"]

    # Index amendment mappings by target article
    amended_articles = {}
    for item in amend_manifest.get("target_mappings_exact", []):
        t_art = item["target_article"] # e.g. "Điều 4", "Điều 52a"
        match = re.search(r'\d+[a-z]?', t_art)
        if match:
            art_key = match.group()
            amended_articles[art_key] = item

    # Index delegations by target article
    delegations_by_art = {}
    for item in deleg_manifest.get("nd140_authority_delegations", []):
        match = re.search(r'\d+', item.get("target_article", ""))
        if match:
            art_int = int(match.group())
            delegations_by_art.setdefault(art_int, []).append(item)

    chunks = []

    # 1. PROCESS ARTICLES (1 -> 70)
    for art in parsed_doc["articles"]:
        art_num = art["article_number"]
        art_title = art["article_title"]
        chap = art["chapter"]
        chap_title = art["chapter_title"]
        raw_body = art["raw_text"]
        clauses = art["clauses"]

        art_key = str(art_num)
        is_amended = art_key in amended_articles
        amend_info = amended_articles.get(art_key)
        deleg_info = delegations_by_art.get(art_num, [])

        context_header = f"{official_num} > {chap}: {chap_title} > Điều {art_num}. {art_title}"

        # Determine intervals
        if not is_amended:
            # UNAMENDED ARTICLE: single chunk, valid [2025-01-01, null)
            chunk_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{doc_id}:article_{art_num}:v1_original"))
            full_search = f"{context_header}\n{raw_body}"
            chunks.append({
                "chunk_id": chunk_id,
                "document_id": doc_id,
                "doc_id": doc_id,
                "official_number": official_num,
                "doc_title": doc_title,
                "canonical_provision_id": f"{doc_id}:article_{art_num}",
                "version_id": "v1_original",
                "unit_type": "ARTICLE",
                "article_number": art_num,
                "clause_number": None,
                "point_number": None,
                "annex_number": None,
                "chapter": chap,
                "chapter_title": chap_title,
                "article_title": art_title,
                "effective_date": "2025-01-01",
                "valid_from": "2025-01-01",
                "valid_to": None,
                "valid_interval": "[2025-01-01, null)",
                "legal_status": "CON_HIEU_LUC",
                "scope_tags": ["TRAFFIC_P2", "KCHT_DUONG_BO", "ND165_ORIGINAL"],
                "source_url": source_url,
                "source_hash": sha256,
                "authority_delegation": deleg_info if deleg_info else None,
                "procedural_overlay": None,
                "context_header": context_header,
                "content": raw_body,
                "full_search_text": full_search
            })
        else:
            # AMENDED ARTICLE: v1_original [2025-01-01, 2026-07-01)
            chunk_id_v1 = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{doc_id}:article_{art_num}:v1_original"))
            full_search_v1 = f"{context_header} (Bản gốc)\n{raw_body}"
            chunks.append({
                "chunk_id": chunk_id_v1,
                "document_id": doc_id,
                "doc_id": doc_id,
                "official_number": official_num,
                "doc_title": doc_title,
                "canonical_provision_id": f"{doc_id}:article_{art_num}",
                "version_id": "v1_original",
                "unit_type": "ARTICLE",
                "article_number": art_num,
                "clause_number": None,
                "point_number": None,
                "annex_number": None,
                "chapter": chap,
                "chapter_title": chap_title,
                "article_title": art_title,
                "effective_date": "2025-01-01",
                "valid_from": "2025-01-01",
                "valid_to": "2026-07-01",
                "valid_interval": "[2025-01-01, 2026-07-01)",
                "legal_status": "BI_SUA_DOI",
                "scope_tags": ["TRAFFIC_P2", "KCHT_DUONG_BO", "ND165_ORIGINAL", "AMENDED_BY_ND241"],
                "source_url": source_url,
                "source_hash": sha256,
                "authority_delegation": deleg_info if deleg_info else None,
                "procedural_overlay": None,
                "context_header": f"{context_header} [Hiệu lực: 01/01/2025 - 01/07/2026]",
                "content": raw_body,
                "full_search_text": full_search_v1
            })

            # v2_nd241 [2026-07-01, null)
            chunk_id_v2 = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{doc_id}:article_{art_num}:v2_nd241"))
            amended_note = f"[Sửa đổi, bổ sung bởi {amend_info['amendment_article']} Nghị định 241/2026/NĐ-CP có hiệu lực từ 01/07/2026]"
            content_v2 = f"{amended_note}\n{raw_body}"
            full_search_v2 = f"{context_header} (Sửa đổi bởi NĐ 241/2026)\n{content_v2}"
            chunks.append({
                "chunk_id": chunk_id_v2,
                "document_id": doc_id,
                "doc_id": doc_id,
                "official_number": official_num,
                "doc_title": doc_title,
                "canonical_provision_id": f"{doc_id}:article_{art_num}",
                "version_id": "v2_nd241",
                "unit_type": "ARTICLE",
                "article_number": art_num,
                "clause_number": None,
                "point_number": None,
                "annex_number": None,
                "chapter": chap,
                "chapter_title": chap_title,
                "article_title": art_title,
                "effective_date": "2026-07-01",
                "valid_from": "2026-07-01",
                "valid_to": None,
                "valid_interval": "[2026-07-01, null)",
                "legal_status": "CON_HIEU_LUC",
                "scope_tags": ["TRAFFIC_P2", "KCHT_DUONG_BO", "ND241_OVERLAY"],
                "source_url": "https://chinhphu.vn/vanban/241-2026-nd-cp",
                "source_hash": amend_manifest["metadata"]["source_document"]["raw_sha256"],
                "amendment_source": f"NĐ 241/2026/NĐ-CP {amend_info['amendment_article']}",
                "authority_delegation": deleg_info if deleg_info else None,
                "context_header": f"{context_header} [Hiệu lực từ 01/07/2026 (NĐ 241/2026)]",
                "content": content_v2,
                "full_search_text": full_search_v2
            })

    # 2. SPECIAL PROVISIONS

    # A. Điều 17(1)(d) - Repealed point
    chunk_id_17_1_d = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{doc_id}:article_17:clause_1:point_d:v1_original"))
    pt_17_1_d_content = "Điểm d Khoản 1 Điều 17: Các bản vẽ thiết kế kết cấu và biện pháp thi công công trình đường bộ được gia cường (đối với trường hợp gia cường công trình đường bộ)."
    chunks.append({
        "chunk_id": chunk_id_17_1_d,
        "document_id": doc_id,
        "doc_id": doc_id,
        "official_number": official_num,
        "doc_title": doc_title,
        "canonical_provision_id": f"{doc_id}:article_17:clause_1:point_d",
        "version_id": "v1_original",
        "unit_type": "POINT",
        "article_number": 17,
        "clause_number": 1,
        "point_number": "d",
        "annex_number": None,
        "chapter": "Chương III",
        "chapter_title": "PHẦN ĐẤT ĐỂ BẢO VỆ, BẢO TRÌ ĐƯỜNG BỘ; HÀNH LANG AN TOÀN ĐƯỜNG BỘ",
        "article_title": "Hồ sơ đề nghị chấp thuận vị trí...",
        "effective_date": "2025-01-01",
        "valid_from": "2025-01-01",
        "valid_to": "2026-07-01",
        "valid_interval": "[2025-01-01, 2026-07-01)",
        "legal_status": "BI_BAI_BO",
        "repealed_by": "NĐ 241/2026/NĐ-CP Điều 25 Khoản 5",
        "scope_tags": ["TRAFFIC_P2", "REPEALED_PROVISION", "ND165_ORIGINAL"],
        "source_url": source_url,
        "source_hash": sha256,
        "context_header": f"{official_num} > Điều 17 Khoản 1 Điểm d [Bị bãi bỏ từ 01/07/2026 bởi NĐ 241]",
        "content": pt_17_1_d_content,
        "full_search_text": f"{official_num} > Điều 17 Khoản 1 Điểm d\n{pt_17_1_d_content}"
    })

    # B. Điều 52a - Added article
    chunk_id_52a = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{doc_id}:article_52a:v2_nd241"))
    art_52a_content = """Điều 52a. Đầu tư, xây dựng, nâng cấp, mở rộng công trình trạm dừng nghỉ trên đường cao tốc
1. Việc đầu tư, xây dựng, nâng cấp, mở rộng công trình trạm dừng nghỉ trên đường cao tốc phải tuân thủ quy chuẩn kỹ thuật quốc gia về trạm dừng nghỉ và quy hoạch kết cấu hạ tầng giao thông đường bộ được phê duyệt.
2. Chủ đầu tư dự án đường cao tốc có trách nhiệm tổ chức lập, thẩm định và phê duyệt thiết kế xây dựng trạm dừng nghỉ đồng bộ với dự án đường cao tốc.
3. Việc quản lý, vận hành và khai thác trạm dừng nghỉ thực hiện theo phương thức xã hội hóa hoặc theo quy định của pháp luật về quản lý, sử dụng tài sản công.
4. Ủy ban nhân dân cấp tỉnh nơi có trạm dừng nghỉ phối hợp với cơ quan quản lý đường cao tốc trong công tác giải phóng mặt bằng, kết nối giao thông và bảo đảm an ninh trật tự khu vực trạm dừng nghỉ.
5. Bộ Xây dựng hướng dẫn tiêu chuẩn kỹ thuật, định mức kinh tế kỹ thuật trong đầu tư, xây dựng và quản lý vận hành trạm dừng nghỉ."""
    chunks.append({
        "chunk_id": chunk_id_52a,
        "document_id": doc_id,
        "doc_id": doc_id,
        "official_number": official_num,
        "doc_title": doc_title,
        "canonical_provision_id": f"{doc_id}:article_52a",
        "version_id": "v2_nd241",
        "unit_type": "ARTICLE",
        "article_number": 52,
        "clause_number": None,
        "point_number": None,
        "annex_number": None,
        "chapter": "Chương VI",
        "chapter_title": "ĐƯỜNG CAO TỐC",
        "article_title": "Đầu tư, xây dựng, nâng cấp, mở rộng công trình trạm dừng nghỉ trên đường cao tốc",
        "effective_date": "2026-07-01",
        "valid_from": "2026-07-01",
        "valid_to": None,
        "valid_interval": "[2026-07-01, null)",
        "legal_status": "CON_HIEU_LUC",
        "added_by": "NĐ 241/2026/NĐ-CP Điều 21",
        "scope_tags": ["TRAFFIC_P2", "ND241_ADDITION", "TRAM_DUNG_NGHI"],
        "source_url": "https://chinhphu.vn/vanban/241-2026-nd-cp",
        "source_hash": amend_manifest["metadata"]["source_document"]["raw_sha256"],
        "context_header": f"{official_num} > Chương VI > Điều 52a [Bổ sung từ 01/07/2026 bởi NĐ 241/2026]",
        "content": art_52a_content,
        "full_search_text": f"{official_num} > Chương VI > Điều 52a\n{art_52a_content}"
    })

    # 3. PROCESS ANNEXES (I -> X)
    for annex in parsed_doc["annexes"]:
        ann_num = annex["annex_number"] # e.g. "Phụ lục I"
        ann_roman = annex["annex_roman"]
        ann_title = annex["title"]
        forms = annex["forms"]
        raw_ann_text = annex["raw_text"]

        context_ann = f"{official_num} > {ann_num}: {ann_title}"

        # If annex has individual forms, chunk each form
        if forms:
            for f in forms:
                f_code = f["form_code"]
                f_title = f["form_title"]
                
                # Check lineage from NĐ 241
                is_replaced_by_241 = ann_roman in ["I", "III", "IV", "V", "VI"]
                
                # v1_original
                c_id_v1 = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{doc_id}:{ann_num}:{f_code}:v1_original"))
                f_content_v1 = f"{f_code}: {f_title}\n(Ban hành kèm theo Nghị định số 165/2024/NĐ-CP ngày 26/12/2024 của Chính phủ)"
                chunks.append({
                    "chunk_id": c_id_v1,
                    "document_id": doc_id,
                    "doc_id": doc_id,
                    "official_number": official_num,
                    "doc_title": doc_title,
                    "canonical_provision_id": f"{doc_id}:{ann_num}:{f_code}",
                    "version_id": "v1_original",
                    "unit_type": "FORM",
                    "article_number": None,
                    "clause_number": None,
                    "point_number": None,
                    "annex_number": ann_num,
                    "effective_date": "2025-01-01",
                    "valid_from": "2025-01-01",
                    "valid_to": "2026-07-01" if is_replaced_by_241 else None,
                    "valid_interval": "[2025-01-01, 2026-07-01)" if is_replaced_by_241 else "[2025-01-01, null)",
                    "legal_status": "BI_SUA_DOI" if is_replaced_by_241 else "CON_HIEU_LUC",
                    "scope_tags": ["TRAFFIC_P2", "ANNEX_FORM", "ND165_ORIGINAL"],
                    "source_url": source_url,
                    "source_hash": meta["annex_sha256"],
                    "context_header": f"{context_ann} > {f_code}",
                    "content": f_content_v1,
                    "full_search_text": f"{context_ann} > {f_code}\n{f_content_v1}"
                })

                # v2_nd241 (if replaced or added)
                if is_replaced_by_241:
                    c_id_v2 = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{doc_id}:{ann_num}:{f_code}:v2_nd241"))
                    f_content_v2 = f"{f_code}: {f_title}\n(Thay thế bởi Nghị định số 241/2026/NĐ-CP có hiệu lực từ 01/07/2026)"
                    chunks.append({
                        "chunk_id": c_id_v2,
                        "document_id": doc_id,
                        "doc_id": doc_id,
                        "official_number": official_num,
                        "doc_title": doc_title,
                        "canonical_provision_id": f"{doc_id}:{ann_num}:{f_code}",
                        "version_id": "v2_nd241",
                        "unit_type": "FORM",
                        "article_number": None,
                        "clause_number": None,
                        "point_number": None,
                        "annex_number": ann_num,
                        "effective_date": "2026-07-01",
                        "valid_from": "2026-07-01",
                        "valid_to": None,
                        "valid_interval": "[2026-07-01, null)",
                        "legal_status": "CON_HIEU_LUC",
                        "scope_tags": ["TRAFFIC_P2", "ANNEX_FORM", "ND241_OVERLAY"],
                        "source_url": "https://chinhphu.vn/vanban/241-2026-nd-cp",
                        "source_hash": amend_manifest["metadata"]["source_document"]["raw_sha256"],
                        "context_header": f"{context_ann} > {f_code} [Thay thế từ 01/07/2026 bởi NĐ 241]",
                        "content": f_content_v2,
                        "full_search_text": f"{context_ann} > {f_code} (NĐ 241/2026)\n{f_content_v2}"
                    })

            # For Phụ lục I: NĐ 241 adds Mẫu 03 and Mẫu 04
            if ann_roman == "I":
                for added_form in [
                    ("Mẫu 03", "Tờ trình về việc đề nghị điều chỉnh giao Ủy ban nhân dân cấp tỉnh quản lý tuyến, đoạn tuyến quốc lộ"),
                    ("Mẫu 04", "Quyết định về việc điều chỉnh giao Ủy ban nhân dân cấp tỉnh quản lý tuyến, đoạn tuyến quốc lộ")
                ]:
                    af_code, af_title = added_form
                    af_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{doc_id}:Phụ lục I:{af_code}:v2_nd241"))
                    af_content = f"{af_code}: {af_title}\n(Bổ sung bởi Nghị định số 241/2026/NĐ-CP có hiệu lực từ 01/07/2026)"
                    chunks.append({
                        "chunk_id": af_id,
                        "document_id": doc_id,
                        "doc_id": doc_id,
                        "official_number": official_num,
                        "doc_title": doc_title,
                        "canonical_provision_id": f"{doc_id}:Phụ lục I:{af_code}",
                        "version_id": "v2_nd241",
                        "unit_type": "FORM",
                        "article_number": None,
                        "clause_number": None,
                        "point_number": None,
                        "annex_number": "Phụ lục I",
                        "effective_date": "2026-07-01",
                        "valid_from": "2026-07-01",
                        "valid_to": None,
                        "valid_interval": "[2026-07-01, null)",
                        "legal_status": "CON_HIEU_LUC",
                        "scope_tags": ["TRAFFIC_P2", "ANNEX_FORM", "ND241_ADDITION"],
                        "source_url": "https://chinhphu.vn/vanban/241-2026-nd-cp",
                        "source_hash": amend_manifest["metadata"]["source_document"]["raw_sha256"],
                        "context_header": f"{official_num} > Phụ lục I > {af_code} [Bổ sung từ 01/07/2026 bởi NĐ 241]",
                        "content": af_content,
                        "full_search_text": f"{official_num} > Phụ lục I > {af_code} (NĐ 241/2026)\n{af_content}"
                    })

        else:
            # Annex without separate forms (Technical table/guidance: II, VII, IX, X)
            is_pl_x = ann_roman == "X"
            is_pl_ii = ann_roman == "II"

            # v1_original
            c_id_v1 = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{doc_id}:{ann_num}:v1_original"))
            chunks.append({
                "chunk_id": c_id_v1,
                "document_id": doc_id,
                "doc_id": doc_id,
                "official_number": official_num,
                "doc_title": doc_title,
                "canonical_provision_id": f"{doc_id}:{ann_num}",
                "version_id": "v1_original",
                "unit_type": "ANNEX",
                "article_number": None,
                "clause_number": None,
                "point_number": None,
                "annex_number": ann_num,
                "effective_date": "2025-01-01",
                "valid_from": "2025-01-01",
                "valid_to": "2026-07-01" if (is_pl_x or is_pl_ii) else None,
                "valid_interval": "[2025-01-01, 2026-07-01)" if (is_pl_x or is_pl_ii) else "[2025-01-01, null)",
                "legal_status": "BI_THAY_THE" if (is_pl_x or is_pl_ii) else "CON_HIEU_LUC",
                "scope_tags": ["TRAFFIC_P2", "ANNEX_TECHNICAL", "ND165_ORIGINAL"],
                "source_url": source_url,
                "source_hash": meta["annex_sha256"],
                "context_header": context_ann,
                "content": raw_ann_text[:1500] if len(raw_ann_text) > 1500 else raw_ann_text,
                "full_search_text": f"{context_ann}\n{raw_ann_text[:1500]}"
            })

            # v2 for Phụ lục X (replaced by Phụ lục VII NĐ 241) and Phụ lục II (replaced by Phụ lục II NĐ 241)
            if is_pl_x:
                c_id_v2_x = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{doc_id}:Phụ lục X:v2_nd241"))
                content_pl_x_v2 = "Phụ lục X: Thông tin trong cơ sở dữ liệu về kết cấu hạ tầng đường bộ đã đưa vào khai thác\n(Được thay thế bởi Phụ lục VII ban hành kèm theo Nghị định số 241/2026/NĐ-CP có hiệu lực từ 01/07/2026 theo quy định tại điểm h khoản 4 Điều 25)."
                chunks.append({
                    "chunk_id": c_id_v2_x,
                    "document_id": doc_id,
                    "doc_id": doc_id,
                    "official_number": official_num,
                    "doc_title": doc_title,
                    "canonical_provision_id": f"{doc_id}:Phụ lục X",
                    "version_id": "v2_nd241",
                    "unit_type": "ANNEX",
                    "article_number": None,
                    "clause_number": None,
                    "point_number": None,
                    "annex_number": "Phụ lục X",
                    "effective_date": "2026-07-01",
                    "valid_from": "2026-07-01",
                    "valid_to": None,
                    "valid_interval": "[2026-07-01, null)",
                    "legal_status": "CON_HIEU_LUC",
                    "replacement_lineage": "Phụ lục VII NĐ 241/2026/NĐ-CP",
                    "scope_tags": ["TRAFFIC_P2", "ANNEX_TECHNICAL", "ND241_OVERLAY"],
                    "source_url": "https://chinhphu.vn/vanban/241-2026-nd-cp",
                    "source_hash": amend_manifest["metadata"]["source_document"]["raw_sha256"],
                    "context_header": f"{official_num} > Phụ lục X [Thay thế từ 01/07/2026 bởi Phụ lục VII NĐ 241]",
                    "content": content_pl_x_v2,
                    "full_search_text": f"{official_num} > Phụ lục X (Thay thế bởi Phụ lục VII NĐ 241)\n{content_pl_x_v2}"
                })

            if is_pl_ii:
                c_id_v2_ii = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{doc_id}:Phụ lục II:v2_nd241"))
                content_pl_ii_v2 = "Phụ lục II: Quy trình, phương pháp, tiêu chí đánh giá mức độ tiềm ẩn tai nạn giao thông, xác định điểm đen, điểm tiềm ẩn tai nạn giao thông đường bộ\n(Được thay thế bởi Phụ lục II ban hành kèm theo Nghị định số 241/2026/NĐ-CP có hiệu lực từ 01/07/2026 theo quy định tại điểm b khoản 4 Điều 25)."
                chunks.append({
                    "chunk_id": c_id_v2_ii,
                    "document_id": doc_id,
                    "doc_id": doc_id,
                    "official_number": official_num,
                    "doc_title": doc_title,
                    "canonical_provision_id": f"{doc_id}:Phụ lục II",
                    "version_id": "v2_nd241",
                    "unit_type": "ANNEX",
                    "article_number": None,
                    "clause_number": None,
                    "point_number": None,
                    "annex_number": "Phụ lục II",
                    "effective_date": "2026-07-01",
                    "valid_from": "2026-07-01",
                    "valid_to": None,
                    "valid_interval": "[2026-07-01, null)",
                    "legal_status": "CON_HIEU_LUC",
                    "replacement_lineage": "Phụ lục II NĐ 241/2026/NĐ-CP",
                    "scope_tags": ["TRAFFIC_P2", "ANNEX_TECHNICAL", "ND241_OVERLAY"],
                    "source_url": "https://chinhphu.vn/vanban/241-2026-nd-cp",
                    "source_hash": amend_manifest["metadata"]["source_document"]["raw_sha256"],
                    "context_header": f"{official_num} > Phụ lục II [Thay thế từ 01/07/2026 bởi NĐ 241]",
                    "content": content_pl_ii_v2,
                    "full_search_text": f"{official_num} > Phụ lục II (NĐ 241/2026)\n{content_pl_ii_v2}"
                })

    with open(OUTPUT_CHUNKS_FILE, "w", encoding="utf-8") as f:
        json.dump(chunks, f, ensure_ascii=False, indent=2)

    print(f"\n[+] Successfully generated {len(chunks)} chunks!")
    print(f"    - Output file: {OUTPUT_CHUNKS_FILE}")

    # Stats breakdown
    unit_types = {}
    statuses = {}
    valid_froms = {}
    for c in chunks:
        ut = c["unit_type"]
        unit_types[ut] = unit_types.get(ut, 0) + 1
        st = c["legal_status"]
        statuses[st] = statuses.get(st, 0) + 1
        vf = c["valid_from"]
        valid_froms[vf] = valid_froms.get(vf, 0) + 1

    print("\n[+] Breakdown by Unit Type:", unit_types)
    print("[+] Breakdown by Legal Status:", statuses)
    print("[+] Breakdown by Valid From Date:", valid_froms)

if __name__ == "__main__":
    build_chunks()
