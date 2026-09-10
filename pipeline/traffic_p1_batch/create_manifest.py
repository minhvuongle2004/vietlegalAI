import sys
import hashlib
import json
from datetime import datetime
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

RAW_DIR = Path("data/01_raw/traffic_p1_batch")

DOC_METADATA = [
    {
        "filename": "73_2024_TT_BCA.html",
        "source_document_id": "traffic_police_patrol_73_2024_tt_bca",
        "official_number": "73/2024/TT-BCA",
        "title": "Thông tư số 73/2024/TT-BCA quy định về công tác tuần tra, kiểm soát, xử lý vi phạm hành chính về trật tự, an toàn giao thông đường bộ của Cảnh sát giao thông",
        "source_authority": "Bộ Công an",
        "issue_date": "2024-11-15",
        "effective_date": "2025-01-01",
        "source_url": "https://chinhphu.vn/van-ban-chinh-phu-73-2024-TT-BCA",
        "source_status": "Còn hiệu lực",
        "source_status_authority": "CSDL Quốc gia về VBPL",
        "normalized_status": "CURRENT_CORE",
        "legal_status": "CURRENT",
        "ingestion_status": "CORE",
        "document_role": "PRIMARY",
        "source_articles_count": 33,
        "notes": "Quy định 4 trường hợp CSGT được dừng xe (Điều 11); kiểm tra VNeID (Điều 12); bãi bỏ TT 32/2023 và bãi bỏ Điều 1 TT 28/2024 (Điều 32)."
    },
    {
        "filename": "89_2026_ND_CP.html",
        "source_document_id": "traffic_inspection_framework_89_2026_nd_cp",
        "official_number": "89/2026/NĐ-CP",
        "title": "Nghị định số 89/2026/NĐ-CP quy định về điều kiện kinh doanh dịch vụ kiểm định xe cơ giới, tổ chức hoạt động của cơ sở đăng kiểm và niên hạn sử dụng xe cơ giới",
        "source_authority": "Chính phủ",
        "issue_date": "2026-05-20",
        "effective_date": "2026-07-01",
        "source_url": "https://chinhphu.vn/van-ban-chinh-phu-89-2026-ND-CP",
        "source_status": "Chưa có hiệu lực (hiệu lực từ 01/07/2026)",
        "source_status_authority": "Cổng Thông tin điện tử Chính phủ / Công báo",
        "normalized_status": "CURRENT_CORE",
        "legal_status": "CURRENT",
        "ingestion_status": "CORE",
        "document_role": "PRIMARY",
        "source_articles_count": 27,
        "notes": "Quy định khung điều kiện kinh doanh đăng kiểm, niên hạn xe tải 25 năm, xe khách 20 năm (Chương III)."
    },
    {
        "filename": "30_2026_TT_BXD.html",
        "source_document_id": "traffic_inspection_procedures_30_2026_tt_bxd",
        "official_number": "30/2026/TT-BXD",
        "title": "Thông tư số 30/2026/TT-BXD quy định về kiểm định an toàn kỹ thuật và bảo vệ môi trường phương tiện giao thông cơ giới đường bộ",
        "source_authority": "Bộ Xây dựng",
        "issue_date": "2026-05-28",
        "effective_date": "2026-07-01",
        "source_url": "https://chinhphu.vn/van-ban-chinh-phu-30-2026-TT-BXD",
        "source_status": "Chưa có hiệu lực (hiệu lực từ 01/07/2026)",
        "source_status_authority": "Bộ Xây dựng / Công báo",
        "normalized_status": "CURRENT_CORE",
        "legal_status": "CURRENT",
        "ingestion_status": "CORE",
        "document_role": "PRIMARY",
        "source_articles_count": 32,
        "notes": "Thay thế trực tiếp TT 47/2024/TT-BGTVT từ 01/07/2026 (Điều 32); cấp chứng nhận kiểm định điện tử qua VNeID; miễn khám lại khi đổi biển số/sang tên; quy định các phụ kiện không coi là cải tạo xe."
    },
    {
        "filename": "65_2024_TT_BCA.html",
        "source_document_id": "traffic_points_recovery_65_2024_tt_bca",
        "official_number": "65/2024/TT-BCA",
        "title": "Thông tư số 65/2024/TT-BCA quy định về kiểm tra kiến thức pháp luật về trật tự, an toàn giao thông đường bộ để được phục hồi điểm giấy phép lái xe",
        "source_authority": "Bộ Công an",
        "issue_date": "2024-11-12",
        "effective_date": "2025-01-01",
        "source_url": "https://chinhphu.vn/van-ban-chinh-phu-65-2024-TT-BCA",
        "source_status": "Còn hiệu lực",
        "source_status_authority": "CSDL Quốc gia về VBPL",
        "normalized_status": "CURRENT_CORE",
        "legal_status": "CURRENT",
        "ingestion_status": "CORE",
        "document_role": "PRIMARY",
        "source_articles_count": 11,
        "notes": "Văn bản gốc quy định thủ tục, điều kiện kiểm tra phục hồi điểm GPLX sau ít nhất 6 tháng (được sửa đổi bổ sung bởi TT 105/2026/TT-BCA)."
    },
    {
        "filename": "12_2025_TT_BXD.html",
        "source_document_id": "traffic_weight_limits_12_2025_tt_bxd",
        "official_number": "12/2025/TT-BXD",
        "title": "Thông tư số 12/2025/TT-BXD quy định về tải trọng, khổ giới hạn của đường bộ; lưu hành xe quá tải trọng, xe quá khổ giới hạn, xe bánh xích trên đường bộ",
        "source_authority": "Bộ Xây dựng",
        "issue_date": "2025-05-15",
        "effective_date": "2025-07-01",
        "source_url": "https://chinhphu.vn/van-ban-chinh-phu-12-2025-TT-BXD",
        "source_status": "Còn hiệu lực (sửa đổi bởi TT 19/2026/TT-BXD)",
        "source_status_authority": "Bộ Xây dựng / CSDL Quốc gia về VBPL",
        "normalized_status": "CURRENT_CORE",
        "legal_status": "CURRENT",
        "ingestion_status": "CORE",
        "document_role": "PRIMARY",
        "source_articles_count": 31,
        "notes": "Văn bản gốc quy định tải trọng trục đơn 10t, trục kép 11-18t, trục ba 21-24t, tổng trọng lượng xe thân liền, xe đầu kéo và cấp Giấy phép lưu hành xe."
    },
    {
        "filename": "19_2026_TT_BXD.html",
        "source_document_id": "traffic_weight_amendment_19_2026_tt_bxd",
        "official_number": "19/2026/TT-BXD",
        "title": "Thông tư số 19/2026/TT-BXD sửa đổi, bổ sung một số điều của Thông tư số 12/2025/TT-BXD về tải trọng, khổ giới hạn đường bộ",
        "source_authority": "Bộ Xây dựng",
        "issue_date": "2026-05-08",
        "effective_date": "2026-07-01",
        "source_url": "https://chinhphu.vn/van-ban-chinh-phu-19-2026-TT-BXD",
        "source_status": "Chưa có hiệu lực (hiệu lực từ 01/07/2026)",
        "source_status_authority": "Bộ Xây dựng / Công báo",
        "normalized_status": "CURRENT_CORE",
        "legal_status": "CURRENT",
        "ingestion_status": "CORE",
        "document_role": "AMENDMENT_SOURCE",
        "source_articles_count": 3,
        "notes": "Sửa đổi Điều 5, Điều 7, Điều 16 của TT 12/2025: nâng tải trọng trục kép có bóng hơi lên 19t, nâng tổng trọng lượng xe đầu kéo 5 trục dùng bóng hơi trên cao tốc lên 45t, rút ngắn cấp phép online xuống 24h."
    },
    {
        "filename": "26_2026_VBHN_BXD.html",
        "source_document_id": "traffic_weight_consolidated_26_2026_vbhn_bxd",
        "official_number": "26/VBHN-BXD",
        "title": "Văn bản hợp nhất số 26/VBHN-BXD hợp nhất Thông tư số 12/2025/TT-BXD và Thông tư số 19/2026/TT-BXD về tải trọng, khổ giới hạn đường bộ",
        "source_authority": "Bộ Xây dựng",
        "issue_date": "2026-06-02",
        "effective_date": "2026-07-01",
        "source_url": "https://chinhphu.vn/van-ban-chinh-phu-26-VBHN-BXD",
        "source_status": "Văn bản hợp nhất đối chiếu",
        "source_status_authority": "Bộ Xây dựng",
        "normalized_status": "CONSOLIDATED_REFERENCE",
        "legal_status": "CURRENT",
        "ingestion_status": "REFERENCE_ONLY",
        "document_role": "CONSOLIDATED_REFERENCE",
        "source_articles_count": 31,
        "notes": "Dùng làm cơ sở đối chiếu toàn văn xác thực việc tích hợp các điều khoản sửa đổi giữa TT 12 và TT 19."
    },
    {
        "filename": "28_2024_TT_BCA.html",
        "source_document_id": "traffic_police_amendment_28_2024_tt_bca",
        "official_number": "28/2024/TT-BCA",
        "title": "Thông tư số 28/2024/TT-BCA sửa đổi, bổ sung một số điều của Thông tư số 32/2023/TT-BCA và Thông tư số 24/2023/TT-BCA",
        "source_authority": "Bộ Công an",
        "issue_date": "2024-06-29",
        "effective_date": "2024-07-01",
        "source_url": "https://chinhphu.vn/van-ban-chinh-phu-28-2024-TT-BCA",
        "source_status": "Còn hiệu lực",
        "source_status_authority": "CSDL Quốc gia về VBPL",
        "normalized_status": "PARTIALLY_AFFECTED",
        "legal_status": "PROVISION-HISTORICAL",
        "ingestion_status": "CORE",
        "document_role": "PRIMARY",
        "source_articles_count": 4,
        "notes": "Mô hình hóa Provision-Level: Điều 1 bãi bỏ bởi TT 73, Điều 2 bãi bỏ bởi TT 79 (current_retrieval_eligible: false); Điều 3-4 còn hiệu lực (current_retrieval_eligible: true, primary_current_core: false)."
    }
]

def build_manifest():
    manifest_docs = []
    total_core_articles = 0

    for item in DOC_METADATA:
        file_path = RAW_DIR / item["filename"]
        if not file_path.exists():
            print(f"Error: File {file_path} not found!")
            continue
        
        raw_bytes = file_path.read_bytes()
        sha256_hash = hashlib.sha256(raw_bytes).hexdigest()
        size_bytes = len(raw_bytes)
        
        doc_entry = {
            "source_document_id": item["source_document_id"],
            "official_number": item["official_number"],
            "filename": item["filename"],
            "relative_path": f"data/01_raw/traffic_p1_batch/{item['filename']}",
            "source_authority": item["source_authority"],
            "title": item["title"],
            "issue_date": item["issue_date"],
            "effective_date": item["effective_date"],
            "source_url": item["source_url"],
            "retrieved_at": datetime.now().isoformat(),
            "content_type": "text/html; charset=utf-8",
            "sha256": sha256_hash,
            "size_bytes": size_bytes,
            "legal_status": item["legal_status"],
            "ingestion_status": item["ingestion_status"],
            "document_role": item["document_role"],
            "source_status": item["source_status"],
            "source_status_authority": item["source_status_authority"],
            "normalized_status": item["normalized_status"],
            "source_articles_count": item["source_articles_count"],
            "notes": item["notes"],
            "status": "RAW_IMMUTABLE_SEALED"
        }
        manifest_docs.append(doc_entry)
        if item["ingestion_status"] == "CORE" and item["legal_status"] == "CURRENT":
            total_core_articles += item["source_articles_count"]

    manifest = {
        "batch_name": "Traffic P1 Legal Coverage Expansion Batch",
        "created_at": datetime.now().isoformat(),
        "total_documents": len(manifest_docs),
        "core_documents_count": 6,
        "total_core_articles_count": total_core_articles,
        "seal_algorithm": "SHA-256 (Raw Bytes)",
        "documents": manifest_docs
    }

    manifest_path = RAW_DIR / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[SUCCESS] Manifest created at {manifest_path}")
    print(f"Total documents: {len(manifest_docs)}")
    print(f"Total Core articles count: {total_core_articles} (Expected: 137)")

build_manifest()
