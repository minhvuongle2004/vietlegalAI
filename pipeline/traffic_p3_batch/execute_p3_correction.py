import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
import os
import re
import json
import time
import uuid
import hashlib
import requests
from pathlib import Path
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
load_dotenv(PROJECT_ROOT / ".env")

from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels
from backend.app.services.rag.embeddings import get_embedding_service

CLOUD_URL = os.getenv("QDRANT_URL")
CLOUD_API_KEY = os.getenv("QDRANT_API_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

PARSED_DIR = PROJECT_ROOT / "data" / "03_parsed" / "traffic_p3_batch"

def execute_correction():
    print("=" * 80)
    print("   TRAFFIC P3 TARGETED CORRECTION PIPELINE")
    print("   1. NĐ 158/2024 Full-Document (78 Articles + 13 Annexes + NĐ 218)")
    print("   2. NĐ 161/2024 Amendment Modeling (33 Articles + NĐ 105 Lineage)")
    print("=" * 80)

    sb_headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }

    # ---------------------------------------------------------
    # PART 1: NĐ 158/2024 FULL-DOCUMENT INGESTION (78 ARTICLES)
    # ---------------------------------------------------------
    print("\n>>> [1/5] Processing NĐ 158/2024 (78 Articles)...")
    with open(PARSED_DIR / "nd158_2024_full_78_articles.json", "r", encoding="utf-8") as f:
        nd158_articles = json.load(f)
    assert len(nd158_articles) == 78, f"Expected 78 articles, found {len(nd158_articles)}"

    doc_id_158 = "traffic_transport_158_2024_nd_cp"
    off_num_158 = "158/2024/NĐ-CP"
    title_158 = "Nghị định 158/2024/NĐ-CP quy định về hoạt động vận tải đường bộ"

    # 1.1 Update Supabase legal_documents for NĐ 158
    doc_158_payload = {
        "id": doc_id_158,
        "official_number": off_num_158,
        "title": title_158,
        "short_title": "Nghị định 158/2024/NĐ-CP",
        "doc_type": "NGHI_DINH",
        "issuer": "Chính phủ",
        "signer": "Trần Hồng Hà",
        "issue_date": "2024-12-18",
        "effective_date": "2025-01-01",
        "expiry_date": None,
        "status": "CON_HIEU_LUC",
        "source_url": "https://vanban.chinhphu.vn/?pageid=27160&docid=212082",
        "metadata": {
            "batch": "TRAFFIC_P3",
            "articles_count": 78,
            "annex_count": 13,
            "amended_by": ["218/2026/NĐ-CP"],
            "amendment_effective_date": "2026-08-10"
        }
    }
    # Check if exists
    r158 = requests.get(f"{SUPABASE_URL}/rest/v1/legal_documents?id=eq.{doc_id_158}", headers=sb_headers).json()
    if not r158:
        requests.post(f"{SUPABASE_URL}/rest/v1/legal_documents", headers=sb_headers, json=doc_158_payload)
        print("[+] Created NĐ 158 in legal_documents.")
    else:
        requests.patch(f"{SUPABASE_URL}/rest/v1/legal_documents?id=eq.{doc_id_158}", headers=sb_headers, json=doc_158_payload)
        print("[=] Updated NĐ 158 in legal_documents.")

    # 1.2 Upsert 78 articles in Supabase legal_articles
    r_existing_158 = requests.get(f"{SUPABASE_URL}/rest/v1/legal_articles?document_id=eq.{doc_id_158}&select=article_number", headers=sb_headers).json()
    existing_nums_158 = {x["article_number"] for x in r_existing_158}
    print(f"[*] Currently existing articles for NĐ 158 in Supabase: {len(existing_nums_158)}/78")

    to_insert_158 = []
    for a in nd158_articles:
        if a["article_number"] not in existing_nums_158:
            to_insert_158.append({
                "document_id": doc_id_158,
                "article_number": a["article_number"],
                "article_title": a["article_title"],
                "chapter_info": "QUY ĐỊNH VỀ HOẠT ĐỘNG VẬN TẢI ĐƯỜNG BỘ",
                "full_text": a["full_text"],
                "status": "CON_HIEU_LUC"
            })
    
    if to_insert_158:
        # Batch insert in chunks of 20
        for i in range(0, len(to_insert_158), 20):
            batch = to_insert_158[i:i+20]
            requests.post(f"{SUPABASE_URL}/rest/v1/legal_articles", headers=sb_headers, json=batch)
        print(f"[+] Inserted {len(to_insert_158)} newly added articles for NĐ 158.")
    else:
        print("[=] All 78 articles of NĐ 158 already exist in Supabase.")

    # ---------------------------------------------------------
    # PART 2: NĐ 161/2024 33 ARTICLES & NĐ 105 AMENDMENT MODELING
    # ---------------------------------------------------------
    print("\n>>> [2/5] Processing NĐ 161/2024 (33 Articles + NĐ 105 Lineage)...")
    with open(PARSED_DIR / "nd161_2024_full_33_articles.json", "r", encoding="utf-8") as f:
        nd161_articles = json.load(f)
    assert len(nd161_articles) == 33, f"Expected 33 articles, found {len(nd161_articles)}"

    doc_id_161 = "traffic_dangerous_goods_161_2024_nd_cp"
    off_num_161 = "161/2024/NĐ-CP"
    title_161 = "Nghị định 161/2024/NĐ-CP quy định Danh mục hàng hóa nguy hiểm, vận chuyển hàng hóa nguy hiểm và trình tự, thủ tục cấp giấy phép, cấp giấy chứng nhận hoàn thành chương trình tập huấn cho người lái xe hoặc người áp tải vận chuyển hàng hóa nguy hiểm trên đường bộ"

    # 2.1 Update Supabase legal_documents for NĐ 161
    doc_161_payload = {
        "id": doc_id_161,
        "official_number": off_num_161,
        "title": title_161,
        "short_title": "Nghị định 161/2024/NĐ-CP",
        "doc_type": "NGHI_DINH",
        "issuer": "Chính phủ",
        "signer": "Trần Hồng Hà",
        "issue_date": "2024-12-18",
        "effective_date": "2025-01-01",
        "expiry_date": None,
        "status": "HET_HIEU_LUC_MOT_PHAN",
        "source_url": "https://vanban.chinhphu.vn/?pageid=27160&docid=212085",
        "metadata": {
            "batch": "TRAFFIC_P3",
            "articles_count": 33,
            "document_role": "PARTIALLY_AFFECTED",
            "amended_by": ["105/2025/NĐ-CP"],
            "amendment_effective_date": "2025-07-01",
            "direct_amendment_details": {
                "source": "Nghị định 105/2025/NĐ-CP Điều 44",
                "repealed_provisions": ["Điều 14 Khoản 1", "Điều 19 (toàn bộ)"],
                "amended_provisions": ["Điều 14 Khoản 3", "Điều 23 (toàn bộ)"]
            },
            "authority_delegation_notes": {
                "source": "Nghị định 140/2025/NĐ-CP Điều 23 Khoản 9",
                "target_provision": "Điều 27 (Ủy ban nhân dân cấp tỉnh)"
            }
        }
    }
    requests.patch(f"{SUPABASE_URL}/rest/v1/legal_documents?id=eq.{doc_id_161}", headers=sb_headers, json=doc_161_payload)
    print("[+] Updated NĐ 161 in legal_documents with NĐ 105 lineage and 33 articles.")

    # 2.2 Upsert 33 articles in Supabase legal_articles
    r_existing_161 = requests.get(f"{SUPABASE_URL}/rest/v1/legal_articles?document_id=eq.{doc_id_161}&select=article_number", headers=sb_headers).json()
    existing_nums_161 = {x["article_number"] for x in r_existing_161}
    print(f"[*] Currently existing articles for NĐ 161 in Supabase: {len(existing_nums_161)}/33")

    to_insert_161 = []
    for a in nd161_articles:
        status = "CON_HIEU_LUC"
        if a["article_number"] == 19:
            status = "HET_HIEU_LUC"  # REPEALED by NĐ 105
        elif a["article_number"] in [14, 23]:
            status = "BI_SUA_DOI"    # AMENDED by NĐ 105

        if a["article_number"] not in existing_nums_161:
            to_insert_161.append({
                "document_id": doc_id_161,
                "article_number": a["article_number"],
                "article_title": a["article_title"],
                "chapter_info": "VẬN CHUYỂN HÀNG HÓA NGUY HIỂM",
                "full_text": a["full_text"],
                "status": status
            })
        else:
            # Update status for existing articles if needed (e.g. Điều 19, 14, 23)
            requests.patch(
                f"{SUPABASE_URL}/rest/v1/legal_articles?document_id=eq.{doc_id_161}&article_number=eq.{a['article_number']}",
                headers=sb_headers,
                json={"status": status}
            )

    if to_insert_161:
        requests.post(f"{SUPABASE_URL}/rest/v1/legal_articles", headers=sb_headers, json=to_insert_161)
        print(f"[+] Inserted {len(to_insert_161)} newly added articles for NĐ 161 (including Điều 33).")
    else:
        print("[=] All 33 articles of NĐ 161 verified in Supabase.")

    # ---------------------------------------------------------
    # PART 3: BUILD CHUNKS FOR STAGING
    # ---------------------------------------------------------
    print("\n>>> [3/5] Building Staging Chunks with Exact Temporal Intervals...")
    chunks = []

    # 3.1 NĐ 158/2024 Chunks
    # Text for Điều 7 v2 and Điều 19 v2 from NĐ 218
    d7_orig = next(a for a in nd158_articles if a["article_number"] == 7)
    d19_orig = next(a for a in nd158_articles if a["article_number"] == 19)

    d7_v2_text = d7_orig["full_text"] + "\n\n[Được sửa đổi, bổ sung bởi Điều 1 Khoản 1 Nghị định 218/2026/NĐ-CP có hiệu lực từ 10/08/2026]:\n4. Đơn vị kinh doanh vận tải hành khách theo hợp đồng và người lái xe không được đón, trả khách tại trụ sở chính, trụ sở chi nhánh, văn phòng đại diện hoặc địa điểm cố định khác do đơn vị kinh doanh vận tải thuê, hợp tác kinh doanh trên các tuyến đường phố; không được ấn định hành trình, lịch trình cố định để phục vụ cho nhiều hành khách hoặc nhiều người thuê vận tải khác nhau.\n5. Nghiêm cấm việc xác nhận đặt chỗ cho từng hành khách, gom khách, bán vé hoặc thu tiền trực tiếp của từng hành khách dưới mọi hình thức đối với xe kinh doanh vận tải theo hợp đồng.\n6. Từ ngày 01 tháng 01 năm 2028, đơn vị kinh doanh vận tải hành khách theo hợp đồng phải thực hiện kết nối, chia sẻ tự động dữ liệu về nội dung hợp đồng vận tải hành khách điện tử cho Cục Cảnh sát giao thông (Bộ Công an) và Cục Đường bộ Việt Nam trước khi thực hiện chuyến đi."
    d19_v2_text = d19_orig["full_text"] + "\n\n[Được bổ sung điểm đ vào khoản 2 bởi Điều 1 Khoản 2 Nghị định 218/2026/NĐ-CP có hiệu lực từ 10/08/2026]:\nđ) Đơn vị kinh doanh vận tải hành khách theo hợp đồng vi phạm quy định về việc đón, trả khách tại trụ sở chính, chi nhánh, văn phòng đại diện từ 03 lần trở lên trong thời gian 01 tháng hoặc tổ chức hoạt động gom khách, bán vé trá hình tuyến cố định."

    for a in nd158_articles:
        num = a["article_number"]
        if num == 7:
            # v1: [2025-01-01, 2026-08-10)
            cid_v1 = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{doc_id_158}:article_7:v1"))
            chunks.append({
                "chunk_id": cid_v1,
                "document_id": doc_id_158,
                "doc_id": doc_id_158,
                "official_number": off_num_158,
                "canonical_provision_id": f"{doc_id_158}:article_7",
                "version_id": "v1_original",
                "article_number": 7,
                "article_title": a["article_title"],
                "valid_from": "2025-01-01",
                "valid_to": "2026-08-10",
                "valid_interval": "[2025-01-01, 2026-08-10)",
                "legal_status": "CON_HIEU_LUC",
                "content": a["full_text"],
                "full_search_text": f"[{off_num_158}] Điều 7: {a['article_title']} (v1 trước 10/08/2026)\n{a['full_text']}",
                "batch": "TRAFFIC_P3"
            })
            # v2: [2026-08-10, +inf)
            cid_v2 = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{doc_id_158}:article_7:v2"))
            chunks.append({
                "chunk_id": cid_v2,
                "document_id": doc_id_158,
                "doc_id": doc_id_158,
                "official_number": off_num_158,
                "canonical_provision_id": f"{doc_id_158}:article_7",
                "version_id": "v2_amended_by_218_2026",
                "article_number": 7,
                "article_title": a["article_title"],
                "valid_from": "2026-08-10",
                "valid_to": None,
                "valid_interval": "[2026-08-10, +inf)",
                "legal_status": "CON_HIEU_LUC",
                "content": d7_v2_text,
                "full_search_text": f"[{off_num_158}] Điều 7: {a['article_title']} (v2 sửa đổi bởi NĐ 218/2026 từ 10/08/2026)\n{d7_v2_text}",
                "batch": "TRAFFIC_P3"
            })
        elif num == 19:
            # v1: [2025-01-01, 2026-08-10)
            cid_v1 = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{doc_id_158}:article_19:v1"))
            chunks.append({
                "chunk_id": cid_v1,
                "document_id": doc_id_158,
                "doc_id": doc_id_158,
                "official_number": off_num_158,
                "canonical_provision_id": f"{doc_id_158}:article_19",
                "version_id": "v1_original",
                "article_number": 19,
                "article_title": a["article_title"],
                "valid_from": "2025-01-01",
                "valid_to": "2026-08-10",
                "valid_interval": "[2025-01-01, 2026-08-10)",
                "legal_status": "CON_HIEU_LUC",
                "content": a["full_text"],
                "full_search_text": f"[{off_num_158}] Điều 19: {a['article_title']} (v1 trước 10/08/2026)\n{a['full_text']}",
                "batch": "TRAFFIC_P3"
            })
            # v2: [2026-08-10, +inf)
            cid_v2 = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{doc_id_158}:article_19:v2"))
            chunks.append({
                "chunk_id": cid_v2,
                "document_id": doc_id_158,
                "doc_id": doc_id_158,
                "official_number": off_num_158,
                "canonical_provision_id": f"{doc_id_158}:article_19",
                "version_id": "v2_amended_by_218_2026",
                "article_number": 19,
                "article_title": a["article_title"],
                "valid_from": "2026-08-10",
                "valid_to": None,
                "valid_interval": "[2026-08-10, +inf)",
                "legal_status": "CON_HIEU_LUC",
                "content": d19_v2_text,
                "full_search_text": f"[{off_num_158}] Điều 19: {a['article_title']} (v2 bổ sung điểm đ bởi NĐ 218/2026 từ 10/08/2026)\n{d19_v2_text}",
                "batch": "TRAFFIC_P3"
            })
        else:
            cid = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{doc_id_158}:article_{num}:v1"))
            chunks.append({
                "chunk_id": cid,
                "document_id": doc_id_158,
                "doc_id": doc_id_158,
                "official_number": off_num_158,
                "canonical_provision_id": f"{doc_id_158}:article_{num}",
                "version_id": "v1_current",
                "article_number": num,
                "article_title": a["article_title"],
                "valid_from": "2025-01-01",
                "valid_to": None,
                "valid_interval": "[2025-01-01, +inf)",
                "legal_status": "CON_HIEU_LUC",
                "content": a["full_text"],
                "full_search_text": f"[{off_num_158}] Điều {num}: {a['article_title']}\n{a['full_text']}",
                "batch": "TRAFFIC_P3"
            })

    # 3.2 NĐ 218/2026 Chunks
    doc_id_218 = "traffic_amendment_218_2026_nd_cp"
    off_num_218 = "218/2026/NĐ-CP"
    d1_218_text = "Điều 1. Sửa đổi, bổ sung một số điều của Nghị định số 158/2024/NĐ-CP:\n1. Sửa đổi, bổ sung khoản 4 và bổ sung khoản 5, khoản 6 vào Điều 7.\n2. Bổ sung điểm đ vào khoản 2 Điều 19."
    d2_218_text = "Điều 2. Hiệu lực thi hành:\n1. Nghị định này có hiệu lực thi hành từ ngày 10 tháng 08 năm 2026."
    for n_218, txt_218 in [(1, d1_218_text), (2, d2_218_text)]:
        chunks.append({
            "chunk_id": str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{doc_id_218}:article_{n_218}:v1")),
            "document_id": doc_id_218,
            "doc_id": doc_id_218,
            "official_number": off_num_218,
            "canonical_provision_id": f"{doc_id_218}:article_{n_218}",
            "version_id": "v1_current",
            "article_number": n_218,
            "article_title": "Hiệu lực thi hành" if n_218 == 2 else "Sửa đổi bổ sung NĐ 158/2024",
            "valid_from": "2026-08-10",
            "valid_to": None,
            "valid_interval": "[2026-08-10, +inf)",
            "legal_status": "CON_HIEU_LUC",
            "content": txt_218,
            "full_search_text": f"[{off_num_218}] Điều {n_218}\n{txt_218}",
            "batch": "TRAFFIC_P3"
        })

    # 3.3 NĐ 161/2024 Chunks (with NĐ 105/2025 Amendment Model)
    d14_orig = next(a for a in nd161_articles if a["article_number"] == 14)
    d19_orig = next(a for a in nd161_articles if a["article_number"] == 19)
    d23_orig = next(a for a in nd161_articles if a["article_number"] == 23)

    d14_v2_text = d14_orig["full_text"] + "\n\n[Được sửa đổi, bổ sung bởi Nghị định 105/2025/NĐ-CP Điều 44 có hiệu lực từ 01/07/2025]:\n- Bãi bỏ khoản 1 Điều 14 (thẩm quyền cấp giấy phép của Bộ Công an đối với hàng hóa nguy hiểm loại 1, 2, 3, 4, 9).\n- Sửa đổi khoản 3 Điều 14: Bộ Công Thương tổ chức cấp Giấy phép vận chuyển hàng hóa nguy hiểm các loại 1, 2, 3, 4, 5, 8, 9 (trừ trường hợp thuộc thẩm quyền của Bộ Quốc phòng và hóa chất bảo vệ thực vật)."
    d23_v2_text = d23_orig["full_text"] + "\n\n[Được sửa đổi, bổ sung bởi Nghị định 105/2025/NĐ-CP Điều 44 có hiệu lực từ 01/07/2025]:\n- Bộ Công Thương quản lý danh mục và tổ chức thực hiện việc cấp Giấy phép vận chuyển hàng hóa nguy hiểm các loại 1, 2, 3, 4, 5, 8, 9 theo quy định tại khoản 3 Điều 14 đã được sửa đổi."

    for a in nd161_articles:
        num = a["article_number"]
        if num == 14:
            # v1: [2025-01-01, 2025-07-01)
            chunks.append({
                "chunk_id": str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{doc_id_161}:article_14:v1")),
                "document_id": doc_id_161,
                "doc_id": doc_id_161,
                "official_number": off_num_161,
                "canonical_provision_id": f"{doc_id_161}:article_14",
                "version_id": "v1_original",
                "article_number": 14,
                "article_title": a["article_title"],
                "valid_from": "2025-01-01",
                "valid_to": "2025-07-01",
                "valid_interval": "[2025-01-01, 2025-07-01)",
                "legal_status": "CON_HIEU_LUC",
                "content": a["full_text"],
                "full_search_text": f"[{off_num_161}] Điều 14: {a['article_title']} (v1 trước 01/07/2025)\n{a['full_text']}",
                "batch": "TRAFFIC_P3"
            })
            # v2: [2025-07-01, +inf)
            chunks.append({
                "chunk_id": str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{doc_id_161}:article_14:v2")),
                "document_id": doc_id_161,
                "doc_id": doc_id_161,
                "official_number": off_num_161,
                "canonical_provision_id": f"{doc_id_161}:article_14",
                "version_id": "v2_amended_by_105_2025",
                "article_number": 14,
                "article_title": a["article_title"],
                "valid_from": "2025-07-01",
                "valid_to": None,
                "valid_interval": "[2025-07-01, +inf)",
                "legal_status": "CON_HIEU_LUC",
                "content": d14_v2_text,
                "full_search_text": f"[{off_num_161}] Điều 14: {a['article_title']} (v2 sửa đổi bởi NĐ 105/2025 từ 01/07/2025)\n{d14_v2_text}",
                "batch": "TRAFFIC_P3"
            })
        elif num == 19:
            # Điều 19 repealed from 2025-07-01
            chunks.append({
                "chunk_id": str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{doc_id_161}:article_19:v1")),
                "document_id": doc_id_161,
                "doc_id": doc_id_161,
                "official_number": off_num_161,
                "canonical_provision_id": f"{doc_id_161}:article_19",
                "version_id": "v1_original",
                "article_number": 19,
                "article_title": a["article_title"],
                "valid_from": "2025-01-01",
                "valid_to": "2025-07-01",
                "valid_interval": "[2025-01-01, 2025-07-01)",
                "legal_status": "HET_HIEU_LUC",
                "content": a["full_text"] + "\n\n[Bị bãi bỏ bởi Điều 44 Nghị định số 105/2025/NĐ-CP có hiệu lực từ ngày 01/07/2025]",
                "full_search_text": f"[{off_num_161}] Điều 19: {a['article_title']} (Bị bãi bỏ từ 01/07/2025 theo NĐ 105/2025)\n{a['full_text']}",
                "batch": "TRAFFIC_P3"
            })
        elif num == 23:
            # v1: [2025-01-01, 2025-07-01)
            chunks.append({
                "chunk_id": str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{doc_id_161}:article_23:v1")),
                "document_id": doc_id_161,
                "doc_id": doc_id_161,
                "official_number": off_num_161,
                "canonical_provision_id": f"{doc_id_161}:article_23",
                "version_id": "v1_original",
                "article_number": 23,
                "article_title": a["article_title"],
                "valid_from": "2025-01-01",
                "valid_to": "2025-07-01",
                "valid_interval": "[2025-01-01, 2025-07-01)",
                "legal_status": "CON_HIEU_LUC",
                "content": a["full_text"],
                "full_search_text": f"[{off_num_161}] Điều 23: {a['article_title']} (v1 trước 01/07/2025)\n{a['full_text']}",
                "batch": "TRAFFIC_P3"
            })
            # v2: [2025-07-01, +inf)
            chunks.append({
                "chunk_id": str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{doc_id_161}:article_23:v2")),
                "document_id": doc_id_161,
                "doc_id": doc_id_161,
                "official_number": off_num_161,
                "canonical_provision_id": f"{doc_id_161}:article_23",
                "version_id": "v2_amended_by_105_2025",
                "article_number": 23,
                "article_title": a["article_title"],
                "valid_from": "2025-07-01",
                "valid_to": None,
                "valid_interval": "[2025-07-01, +inf)",
                "legal_status": "CON_HIEU_LUC",
                "content": d23_v2_text,
                "full_search_text": f"[{off_num_161}] Điều 23: {a['article_title']} (v2 sửa đổi bởi NĐ 105/2025 từ 01/07/2025)\n{d23_v2_text}",
                "batch": "TRAFFIC_P3"
            })
        else:
            chunks.append({
                "chunk_id": str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{doc_id_161}:article_{num}:v1")),
                "document_id": doc_id_161,
                "doc_id": doc_id_161,
                "official_number": off_num_161,
                "canonical_provision_id": f"{doc_id_161}:article_{num}",
                "version_id": "v1_current",
                "article_number": num,
                "article_title": a["article_title"],
                "valid_from": "2025-01-01",
                "valid_to": None,
                "valid_interval": "[2025-01-01, +inf)",
                "legal_status": "CON_HIEU_LUC",
                "content": a["full_text"],
                "full_search_text": f"[{off_num_161}] Điều {num}: {a['article_title']}\n{a['full_text']}",
                "batch": "TRAFFIC_P3"
            })

    print(f"[+] Total chunks built for Staging: {len(chunks)} (NĐ 158: 80, NĐ 218: 2, NĐ 161: 35)")

    # ---------------------------------------------------------
    # PART 4: EMBEDDING & STAGING INGESTION
    # ---------------------------------------------------------
    print("\n>>> [4/5] Embedding chunks with BGE-M3 (CUDA FP16)...")
    embedder = get_embedding_service()
    texts = [c["full_search_text"] for c in chunks]
    vectors = embedder.embed_texts(texts)

    points = []
    for c, vec in zip(chunks, vectors):
        points.append(qmodels.PointStruct(id=c["chunk_id"], vector=vec, payload=c))

    client = QdrantClient(url=CLOUD_URL, api_key=CLOUD_API_KEY, timeout=30.0)
    print(f"[*] Upserting {len(points)} points into 'vietlegal_articles_staging'...")
    client.upsert(collection_name="vietlegal_articles_staging", points=points)
    print("[+] Staging upsert complete.")

    # ---------------------------------------------------------
    # PART 5: VALIDATION SUITE IN STAGING
    # ---------------------------------------------------------
    print("\n>>> [5/5] Executing Staging Validation Suite...")

    # Helper function for temporal activity
    def is_active(p, d):
        vf = p.payload.get("valid_from")
        vt = p.payload.get("valid_to")
        if not vf or vf > d: return False
        if vt and d >= vt: return False
        return True

    # 5.1 NĐ 158 Temporal Test (2026-05-01 vs 2026-08-10)
    d7_v1 = next(p for p in points if p.payload["doc_id"] == doc_id_158 and p.payload["canonical_provision_id"] == f"{doc_id_158}:article_7" and p.payload["version_id"] == "v1_original")
    d7_v2 = next(p for p in points if p.payload["doc_id"] == doc_id_158 and p.payload["canonical_provision_id"] == f"{doc_id_158}:article_7" and p.payload["version_id"] == "v2_amended_by_218_2026")
    
    assert is_active(d7_v1, "2026-05-01") is True, "NĐ 158 Điều 7 v1 should be active before 2026-08-10"
    assert is_active(d7_v2, "2026-05-01") is False, "NĐ 158 Điều 7 v2 should be inactive before 2026-08-10"
    assert is_active(d7_v1, "2026-08-10") is False, "NĐ 158 Điều 7 v1 should be inactive from 2026-08-10"
    assert is_active(d7_v2, "2026-08-10") is True, "NĐ 158 Điều 7 v2 should be active from 2026-08-10"
    print("  [+] NĐ 158 Temporal Test (2026-05-01 vs 2026-08-10): PASS")

    # 5.2 NĐ 161 Temporal Test (2025-06-30 vs 2025-07-01)
    d14_v1 = next(p for p in points if p.payload["doc_id"] == doc_id_161 and p.payload["canonical_provision_id"] == f"{doc_id_161}:article_14" and p.payload["version_id"] == "v1_original")
    d14_v2 = next(p for p in points if p.payload["doc_id"] == doc_id_161 and p.payload["canonical_provision_id"] == f"{doc_id_161}:article_14" and p.payload["version_id"] == "v2_amended_by_105_2025")
    d19 = next(p for p in points if p.payload["doc_id"] == doc_id_161 and p.payload["canonical_provision_id"] == f"{doc_id_161}:article_19")
    
    assert is_active(d14_v1, "2025-06-30") is True, "NĐ 161 Điều 14 v1 should be active before 2025-07-01"
    assert is_active(d14_v2, "2025-06-30") is False, "NĐ 161 Điều 14 v2 should be inactive before 2025-07-01"
    assert is_active(d14_v1, "2025-07-01") is False, "NĐ 161 Điều 14 v1 should be inactive from 2025-07-01"
    assert is_active(d14_v2, "2025-07-01") is True, "NĐ 161 Điều 14 v2 should be active from 2025-07-01"
    assert is_active(d19, "2025-06-30") is True, "NĐ 161 Điều 19 should be active before 2025-07-01"
    assert is_active(d19, "2025-07-01") is False, "NĐ 161 Điều 19 should be REPEALED from 2025-07-01"
    assert d19.payload["legal_status"] == "HET_HIEU_LUC", "Điều 19 legal_status must be HET_HIEU_LUC"
    print("  [+] NĐ 161 Temporal & Repeal Test (2025-06-30 vs 2025-07-01): PASS")

    # 5.3 Coverage Checks
    r_check_158 = requests.get(f"{SUPABASE_URL}/rest/v1/legal_articles?document_id=eq.{doc_id_158}&select=id", headers=sb_headers).json()
    r_check_161 = requests.get(f"{SUPABASE_URL}/rest/v1/legal_articles?document_id=eq.{doc_id_161}&select=id", headers=sb_headers).json()
    assert len(r_check_158) == 78, f"NĐ 158 coverage error: expected 78, found {len(r_check_158)}"
    assert len(r_check_161) == 33, f"NĐ 161 coverage error: expected 33, found {len(r_check_161)}"
    print(f"  [+] Supabase Coverage: NĐ 158 = {len(r_check_158)}/78, NĐ 161 = {len(r_check_161)}/33: PASS")

    # 5.4 Promote to Production
    print("\n>>> PROMOTING VALIDATED POINTS TO PRODUCTION...")
    prod_before = client.get_collection("vietlegal_articles").points_count
    print(f"[*] Production points BEFORE promotion: {prod_before}")
    client.upsert(collection_name="vietlegal_articles", points=points)
    time.sleep(2)
    prod_after = client.get_collection("vietlegal_articles").points_count
    print(f"[*] Production points AFTER promotion:  {prod_after} (+{prod_after - prod_before})")
    print("\n[+] TARGETED CORRECTION AND PROMOTION SUCCESSFULLY EXECUTED!")

if __name__ == "__main__":
    execute_correction()
