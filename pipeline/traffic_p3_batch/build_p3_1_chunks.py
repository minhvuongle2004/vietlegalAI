import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
import os
import json
import uuid
from pathlib import Path
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
load_dotenv(PROJECT_ROOT / ".env")

OUT_DIR = PROJECT_ROOT / "data" / "03_parsed" / "traffic_p3_batch"
OUT_DIR.mkdir(parents=True, exist_ok=True)
CHUNKS_FILE = OUT_DIR / "p3_1_chunks.json"

def build_p3_1_chunks():
    print("=" * 80)
    print("   BUILDING CHUNKS FOR P3.1: NĐ 168/2024 + NĐ 238/2026")
    print("=" * 80)

    doc_id_168 = "traffic_penalty_168_2024_nd_cp"
    off_168 = "168/2024/NĐ-CP"
    title_168 = "Nghị định 168/2024/NĐ-CP xử phạt vi phạm hành chính TTATGT và trừ điểm GPLX"
    url_168 = "https://vanban.chinhphu.vn/?pageid=27160&docid=212171"
    sha_168 = "56a0a0af1548ae6aee0bf903b64d577370760a25cb77e11c4f34c9f773952ae0"

    doc_id_238 = "traffic_penalty_amendment_238_2026_nd_cp"
    off_238 = "238/2026/NĐ-CP"
    title_238 = "Nghị định 238/2026/NĐ-CP sửa đổi, bổ sung Nghị định 168/2024/NĐ-CP về xử phạt vi phạm hành chính TTATGT đường bộ"
    url_238 = "https://vanban.chinhphu.vn/?pageid=27160&docid=212450"
    sha_238 = "36ca5dd9b7f482644edc35a79551d9a1b6017ebc400867f2d091c03c79ccb896"

    chunks = []

    # 1. Điều 5 NĐ 168
    # v1_original
    c5_v1_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{doc_id_168}:article_5:v1_original"))
    c5_v1_text = """Điều 5. Xử phạt người điều khiển xe ô tô và các loại xe tương tự xe ô tô vi phạm quy tắc giao thông đường bộ
1. Phạt tiền từ 200.000 đồng đến 400.000 đồng đối với một trong các hành vi vi phạm sau đây...
3. Phạt tiền từ 800.000 đồng đến 1.000.000 đồng đối với một trong các hành vi vi phạm sau đây..."""
    chunks.append({
        "chunk_id": c5_v1_id,
        "document_id": doc_id_168,
        "doc_id": doc_id_168,
        "official_number": off_168,
        "doc_title": title_168,
        "canonical_provision_id": f"{doc_id_168}:article_5",
        "version_id": "v1_original",
        "unit_type": "ARTICLE",
        "article_number": 5,
        "chapter": "Chương II",
        "chapter_title": "HÀNH VI VI PHẠM, HÌNH THỨC, MỨC XỬ PHẠT",
        "article_title": "Xử phạt người điều khiển xe ô tô vi phạm quy tắc giao thông",
        "effective_date": "2025-01-01",
        "valid_from": "2025-01-01",
        "valid_to": "2026-08-15",
        "valid_interval": "[2025-01-01, 2026-08-15)",
        "legal_status": "BI_SUA_DOI",
        "scope_tags": ["TRAFFIC_P3", "XU_PHAT_VPHC", "ND168_ORIGINAL"],
        "source_url": url_168,
        "source_hash": sha_168,
        "context_header": f"{off_168} > Điều 5. Xử phạt người điều khiển xe ô tô [Hiệu lực: 01/01/2025 - 15/08/2026]",
        "content": c5_v1_text,
        "full_search_text": f"{off_168} > Điều 5 (Bản gốc)\n{c5_v1_text}"
    })

    # v2_nd238
    c5_v2_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{doc_id_168}:article_5:v2_nd238"))
    c5_v2_text = """Điều 5. Xử phạt người điều khiển xe ô tô vi phạm quy tắc giao thông (Sửa đổi bởi NĐ 238/2026/NĐ-CP)
[Bổ sung điểm q vào khoản 1 và điểm h vào khoản 3 bởi Nghị định số 238/2026/NĐ-CP có hiệu lực từ 15/08/2026]
1. Phạt tiền từ 200.000 đồng đến 400.000 đồng đối với hành vi vi phạm... điểm q: Vi phạm quy định về làn đường ưu tiên.
3. Phạt tiền từ 800.000 đồng đến 1.000.000 đồng... điểm h: Không nhường đường cho xe xin vượt khi có đủ điều kiện an toàn."""
    chunks.append({
        "chunk_id": c5_v2_id,
        "document_id": doc_id_168,
        "doc_id": doc_id_168,
        "official_number": off_168,
        "doc_title": title_168,
        "canonical_provision_id": f"{doc_id_168}:article_5",
        "version_id": "v2_nd238",
        "unit_type": "ARTICLE",
        "article_number": 5,
        "chapter": "Chương II",
        "chapter_title": "HÀNH VI VI PHẠM, HÌNH THỨC, MỨC XỬ PHẠT",
        "article_title": "Xử phạt người điều khiển xe ô tô vi phạm quy tắc giao thông",
        "effective_date": "2026-08-15",
        "valid_from": "2026-08-15",
        "valid_to": None,
        "valid_interval": "[2026-08-15, null)",
        "legal_status": "CON_HIEU_LUC",
        "amendment_source": "NĐ 238/2026/NĐ-CP Điều 1 Khoản 1",
        "scope_tags": ["TRAFFIC_P3", "XU_PHAT_VPHC", "ND238_OVERLAY"],
        "source_url": url_238,
        "source_hash": sha_238,
        "context_header": f"{off_168} > Điều 5 [Sửa đổi từ 15/08/2026 bởi NĐ 238/2026]",
        "content": c5_v2_text,
        "full_search_text": f"{off_168} > Điều 5 (NĐ 238/2026)\n{c5_v2_text}"
    })

    # 2. Điều 13 NĐ 168
    # v1_original
    c13_v1_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{doc_id_168}:article_13:v1_original"))
    c13_v1_text = """Điều 13. Xử phạt hành vi vi phạm quy định về biển số xe
8. Phạt tiền từ 14.000.000 đồng đến 16.000.000 đồng đối với hành vi sử dụng biển số xe giả, không do cơ quan có thẩm quyền cấp."""
    chunks.append({
        "chunk_id": c13_v1_id,
        "document_id": doc_id_168,
        "doc_id": doc_id_168,
        "official_number": off_168,
        "doc_title": title_168,
        "canonical_provision_id": f"{doc_id_168}:article_13",
        "version_id": "v1_original",
        "unit_type": "ARTICLE",
        "article_number": 13,
        "chapter": "Chương II",
        "chapter_title": "HÀNH VI VI PHẠM, HÌNH THỨC, MỨC XỬ PHẠT",
        "article_title": "Xử phạt hành vi vi phạm quy định về biển số xe",
        "effective_date": "2025-01-01",
        "valid_from": "2025-01-01",
        "valid_to": "2026-08-15",
        "valid_interval": "[2025-01-01, 2026-08-15)",
        "legal_status": "BI_SUA_DOI",
        "scope_tags": ["TRAFFIC_P3", "BIEN_SO_XE", "ND168_ORIGINAL"],
        "source_url": url_168,
        "source_hash": sha_168,
        "context_header": f"{off_168} > Điều 13. Xử phạt vi phạm biển số xe [Hiệu lực: 01/01/2025 - 15/08/2026]",
        "content": c13_v1_text,
        "full_search_text": f"{off_168} > Điều 13 (Bản gốc)\n{c13_v1_text}"
    })

    # v2_nd238
    c13_v2_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{doc_id_168}:article_13:v2_nd238"))
    c13_v2_text = """Điều 13. Xử phạt hành vi vi phạm quy định về biển số xe (Sửa đổi bởi NĐ 238/2026)
8. Phạt tiền từ 20.000.000 đồng đến 26.000.000 đồng đối với hành vi sản xuất, mua bán, sử dụng biển số xe giả hoặc cố ý làm thay đổi, che lấp, làm sai lệch chữ, số trên biển số xe."""
    chunks.append({
        "chunk_id": c13_v2_id,
        "document_id": doc_id_168,
        "doc_id": doc_id_168,
        "official_number": off_168,
        "doc_title": title_168,
        "canonical_provision_id": f"{doc_id_168}:article_13",
        "version_id": "v2_nd238",
        "unit_type": "ARTICLE",
        "article_number": 13,
        "chapter": "Chương II",
        "chapter_title": "HÀNH VI VI PHẠM, HÌNH THỨC, MỨC XỬ PHẠT",
        "article_title": "Xử phạt hành vi vi phạm quy định về biển số xe",
        "effective_date": "2026-08-15",
        "valid_from": "2026-08-15",
        "valid_to": None,
        "valid_interval": "[2026-08-15, null)",
        "legal_status": "CON_HIEU_LUC",
        "amendment_source": "NĐ 238/2026/NĐ-CP Điều 1 Khoản 2",
        "scope_tags": ["TRAFFIC_P3", "BIEN_SO_XE", "ND238_OVERLAY"],
        "source_url": url_238,
        "source_hash": sha_238,
        "context_header": f"{off_168} > Điều 13 [Sửa đổi từ 15/08/2026 bởi NĐ 238/2026]",
        "content": c13_v2_text,
        "full_search_text": f"{off_168} > Điều 13 (NĐ 238/2026)\n{c13_v2_text}"
    })

    # 3. Điều 14 NĐ 168
    # v1_original
    c14_v1_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{doc_id_168}:article_14:v1_original"))
    c14_v1_text = """Điều 14. Xử phạt vi phạm điều kiện vận tải đường bộ
Xử phạt các hành vi vi phạm về kinh doanh và điều kiện kinh doanh vận tải hành khách, hàng hóa bằng xe ô tô..."""
    chunks.append({
        "chunk_id": c14_v1_id,
        "document_id": doc_id_168,
        "doc_id": doc_id_168,
        "official_number": off_168,
        "doc_title": title_168,
        "canonical_provision_id": f"{doc_id_168}:article_14",
        "version_id": "v1_original",
        "unit_type": "ARTICLE",
        "article_number": 14,
        "chapter": "Chương II",
        "chapter_title": "HÀNH VI VI PHẠM, HÌNH THỨC, MỨC XỬ PHẠT",
        "article_title": "Xử phạt vi phạm điều kiện vận tải",
        "effective_date": "2025-01-01",
        "valid_from": "2025-01-01",
        "valid_to": "2026-08-15",
        "valid_interval": "[2025-01-01, 2026-08-15)",
        "legal_status": "BI_SUA_DOI",
        "scope_tags": ["TRAFFIC_P3", "VAN_TAI", "ND168_ORIGINAL"],
        "source_url": url_168,
        "source_hash": sha_168,
        "context_header": f"{off_168} > Điều 14. Xử phạt vi phạm điều kiện vận tải [Hiệu lực: 01/01/2025 - 15/08/2026]",
        "content": c14_v1_text,
        "full_search_text": f"{off_168} > Điều 14 (Bản gốc)\n{c14_v1_text}"
    })

    # v2_nd238
    c14_v2_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{doc_id_168}:article_14:v2_nd238"))
    c14_v2_text = """Điều 14. Xử phạt vi phạm điều kiện vận tải (Bổ sung bởi NĐ 238/2026)
6a. Phạt tiền từ 12.000.000 đồng đến 14.000.000 đồng đối với cá nhân, từ 24.000.000 đồng đến 28.000.000 đồng đối với tổ chức vi phạm không truyền dữ liệu giám sát hành trình, hình ảnh camera về Cục Đường bộ Việt Nam theo quy định."""
    chunks.append({
        "chunk_id": c14_v2_id,
        "document_id": doc_id_168,
        "doc_id": doc_id_168,
        "official_number": off_168,
        "doc_title": title_168,
        "canonical_provision_id": f"{doc_id_168}:article_14",
        "version_id": "v2_nd238",
        "unit_type": "ARTICLE",
        "article_number": 14,
        "chapter": "Chương II",
        "chapter_title": "HÀNH VI VI PHẠM, HÌNH THỨC, MỨC XỬ PHẠT",
        "article_title": "Xử phạt vi phạm điều kiện vận tải",
        "effective_date": "2026-08-15",
        "valid_from": "2026-08-15",
        "valid_to": None,
        "valid_interval": "[2026-08-15, null)",
        "legal_status": "CON_HIEU_LUC",
        "amendment_source": "NĐ 238/2026/NĐ-CP Điều 1 Khoản 3",
        "scope_tags": ["TRAFFIC_P3", "VAN_TAI", "ND238_OVERLAY"],
        "source_url": url_238,
        "source_hash": sha_238,
        "context_header": f"{off_168} > Điều 14 [Bổ sung từ 15/08/2026 bởi NĐ 238/2026]",
        "content": c14_v2_text,
        "full_search_text": f"{off_168} > Điều 14 (NĐ 238/2026)\n{c14_v2_text}"
    })

    # 4. NĐ 238 Điều 1 & Điều 2 Chunks
    c238_1_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{doc_id_238}:article_1:v1"))
    chunks.append({
        "chunk_id": c238_1_id,
        "document_id": doc_id_238,
        "doc_id": doc_id_238,
        "official_number": off_238,
        "doc_title": title_238,
        "canonical_provision_id": f"{doc_id_238}:article_1",
        "version_id": "v1_original",
        "unit_type": "ARTICLE",
        "article_number": 1,
        "chapter": "Chương I",
        "chapter_title": "QUY ĐỊNH CHUNG",
        "article_title": "Sửa đổi, bổ sung một số điều của Nghị định số 168/2024/NĐ-CP",
        "effective_date": "2026-08-15",
        "valid_from": "2026-08-15",
        "valid_to": None,
        "valid_interval": "[2026-08-15, null)",
        "legal_status": "CON_HIEU_LUC",
        "scope_tags": ["TRAFFIC_P3", "AMENDMENT", "ND238"],
        "source_url": url_238,
        "source_hash": sha_238,
        "context_header": f"{off_238} > Điều 1. Sửa đổi, bổ sung một số điều của Nghị định số 168/2024/NĐ-CP",
        "content": """Điều 1. Sửa đổi, bổ sung một số điều của Nghị định số 168/2024/NĐ-CP:
1. Bổ sung điểm q vào khoản 1 và điểm h vào khoản 3 Điều 5 (Xử phạt người điều khiển xe ô tô vi phạm quy tắc giao thông).
2. Sửa đổi, bổ sung khoản 8 Điều 13 (Xử phạt hành vi vi phạm quy định về biển số xe).
3. Bổ sung khoản 6a vào Điều 14 (Xử phạt vi phạm điều kiện vận tải).""",
        "full_search_text": f"{off_238} > Điều 1\nĐiều 1. Sửa đổi, bổ sung một số điều của Nghị định số 168/2024/NĐ-CP"
    })

    c238_2_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{doc_id_238}:article_2:v1"))
    chunks.append({
        "chunk_id": c238_2_id,
        "document_id": doc_id_238,
        "doc_id": doc_id_238,
        "official_number": off_238,
        "doc_title": title_238,
        "canonical_provision_id": f"{doc_id_238}:article_2",
        "version_id": "v1_original",
        "unit_type": "ARTICLE",
        "article_number": 2,
        "chapter": "Chương I",
        "chapter_title": "QUY ĐỊNH CHUNG",
        "article_title": "Hiệu lực thi hành",
        "effective_date": "2026-08-15",
        "valid_from": "2026-08-15",
        "valid_to": None,
        "valid_interval": "[2026-08-15, null)",
        "legal_status": "CON_HIEU_LUC",
        "scope_tags": ["TRAFFIC_P3", "HIEU_LUC", "ND238"],
        "source_url": url_238,
        "source_hash": sha_238,
        "context_header": f"{off_238} > Điều 2. Hiệu lực thi hành",
        "content": "Điều 2. Hiệu lực thi hành: Nghị định này có hiệu lực thi hành kể từ ngày 15 tháng 08 năm 2026.",
        "full_search_text": f"{off_238} > Điều 2\nĐiều 2. Hiệu lực thi hành kể từ ngày 15/08/2026."
    })

    with open(CHUNKS_FILE, "w", encoding="utf-8") as f:
        json.dump(chunks, f, ensure_ascii=False, indent=2)

    print(f"[+] Generated {len(chunks)} chunks for P3.1 in {CHUNKS_FILE}")
    return chunks

if __name__ == "__main__":
    build_p3_1_chunks()
