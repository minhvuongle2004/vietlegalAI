import sys
import hashlib
import json
from datetime import datetime
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

RAW_DIR = Path("data/01_raw/traffic_p1_2_batch")

DOC_METADATA = [
    {
        "filename": "94_2026_ND_CP.html",
        "source_document_id": "traffic_driver_training_94_2026_nd_cp",
        "official_number": "94/2026/NĐ-CP",
        "title": "Nghị định số 94/2026/NĐ-CP quy định về hoạt động đào tạo và sát hạch lái xe",
        "source_authority": "Chính phủ",
        "issue_date": "2026-05-25",
        "effective_date": "2026-07-01",
        "source_url": "https://chinhphu.vn/van-ban-chinh-phu-94-2026-ND-CP",
        "source_status": "Chưa có hiệu lực (hiệu lực từ 01/07/2026)",
        "source_status_authority": "Cổng Thông tin điện tử Chính phủ / Công báo",
        "normalized_status": "CURRENT_CORE",
        "legal_status": "CURRENT",
        "ingestion_status": "CORE",
        "document_role": "PRIMARY",
        "source_articles_count": 43,
        "attached_units_count": 0,
        "notes": "5 Chương, 43 Điều: Quy định toàn diện điều kiện cơ sở đào tạo, giáo viên, xe tập lái, thiết bị DAT (Điều 8), cabin học lái xe (Điều 9); trung tâm sát hạch loại 1, 2, 3 (Điều 17); quy trình sát hạch lý thuyết, mô phỏng (Điều 26), sa hình, đường trường; Điều 41 hiệu lực từ 01/07/2026 thay thế NĐ 65/2016 và NĐ 138/2018; Điều 42 quy định chuyển tiếp."
    },
    {
        "filename": "241_2026_ND_CP.html",
        "source_document_id": "traffic_road_infra_amendment_241_2026_nd_cp",
        "official_number": "241/2026/NĐ-CP",
        "title": "Nghị định số 241/2026/NĐ-CP sửa đổi, bổ sung một số điều của Nghị định số 165/2024/NĐ-CP ngày 26 tháng 12 năm 2024 của Chính phủ quy định chi tiết một số điều của Luật Đường bộ và Điều 77 Luật Trật tự, an toàn giao thông đường bộ",
        "source_authority": "Chính phủ",
        "issue_date": "2026-06-15",
        "effective_date": "2026-07-01",
        "source_url": "https://chinhphu.vn/van-ban-chinh-phu-241-2026-ND-CP",
        "source_status": "Chưa có hiệu lực (hiệu lực từ 01/07/2026)",
        "source_status_authority": "Cổng Thông tin điện tử Chính phủ / Công báo",
        "normalized_status": "CURRENT_CORE",
        "legal_status": "CURRENT",
        "ingestion_status": "CORE",
        "document_role": "AMENDMENT_SOURCE",
        "source_articles_count": 4,
        "attached_units_count": 0,
        "notes": "4 Điều sửa đổi 10 nội dung NĐ 165/2024: số hóa tài sản kết cấu hạ tầng đường bộ, bảo trì công trình, hành lang an toàn cao tốc 17m-20m, đấu nối bắt buộc qua nút giao liên thông, hệ thống ITS 24/7, chia sẻ dữ liệu giám sát thời gian thực với CSGT (Điều 77 Luật TTATGTĐB), thu phí tự động ETC không barie, trạm dừng nghỉ cao tốc, cân tải trọng tự động WIM phạt nguội."
    },
    {
        "filename": "45_2026_TT_BXD.html",
        "source_document_id": "traffic_inspection_amendment_45_2026_tt_bxd",
        "official_number": "45/2026/TT-BXD",
        "title": "Thông tư số 45/2026/TT-BXD sửa đổi, bổ sung một số điều của Thông tư số 30/2026/TT-BXD ngày 28 tháng 5 năm 2026 của Bộ Xây dựng quy định về kiểm định an toàn kỹ thuật và bảo vệ môi trường phương tiện giao thông cơ giới đường bộ",
        "source_authority": "Bộ Xây dựng",
        "issue_date": "2026-06-20",
        "effective_date": "2026-07-01",
        "source_url": "https://chinhphu.vn/van-ban-chinh-phu-45-2026-TT-BXD",
        "source_status": "Chưa có hiệu lực (hiệu lực từ 01/07/2026)",
        "source_status_authority": "Bộ Xây dựng / Công báo",
        "normalized_status": "CURRENT_CORE",
        "legal_status": "CURRENT",
        "ingestion_status": "CORE",
        "document_role": "AMENDMENT_SOURCE",
        "source_articles_count": 4,
        "attached_units_count": 0,
        "notes": "4 Điều sửa đổi Thông tư 30/2026/TT-BXD: chu kỳ kiểm định xe cơ giới chuyên dùng, kiểm chuẩn thiết bị đo phanh con lăn và phân tích khí thải tự động chống can thiệp, tích hợp Giấy chứng nhận điện tử và mã QR qua VNeID trong 2 giờ, các phụ kiện lắp thêm không coi là cải tạo (baga mui dưới 20cm, bậc lên xuống, đèn hợp quy, phim cách nhiệt), camera AI giám sát dây chuyền kiểm định."
    },
    {
        "filename": "51_2024_TT_BGTVT.html",
        "source_document_id": "traffic_road_signs_qcvn41_51_2024_tt_bgtvt",
        "official_number": "51/2024/TT-BGTVT",
        "title": "Thông tư số 51/2024/TT-BGTVT ban hành Quy chuẩn kỹ thuật quốc gia về báo hiệu đường bộ (QCVN 41:2024/BGTVT)",
        "source_authority": "Bộ Giao thông vận tải",
        "issue_date": "2024-11-15",
        "effective_date": "2025-01-01",
        "source_url": "https://chinhphu.vn/van-ban-chinh-phu-51-2024-TT-BGTVT",
        "source_status": "Còn hiệu lực",
        "source_status_authority": "CSDL Quốc gia về VBPL",
        "normalized_status": "CURRENT_CORE",
        "legal_status": "CURRENT",
        "ingestion_status": "CORE",
        "document_role": "PRIMARY",
        "source_articles_count": 2,
        "attached_regulation": "QCVN 41:2024/BGTVT",
        "attached_units_count": 21,
        "notes": "Thông tư gồm đúng 2 Điều (Điều 1 ban hành QCVN 41:2024/BGTVT, Điều 2 hiệu lực từ 01/01/2025 thay thế TT 54/2019). Đính kèm Quy chuẩn kỹ thuật quốc gia QCVN 41:2024/BGTVT gồm 21 Mục quy định kỹ thuật: thứ tự hiệu lực báo hiệu (CSGT -> Đèn -> Biển -> Vạch), hiệu lệnh CSGT, đèn tín hiệu, 5 nhóm biển báo (P, W, R, I, S), vạch vàng ngược chiều, vạch trắng cùng chiều, vạch mắt võng, vạch xương cá, cọc tiêu, gương cầu lồi, gờ giảm tốc."
    }
]

def calculate_sha256(filepath: Path) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()

def create_manifest():
    manifest_documents = []
    total_legal_articles = 0
    total_qcvn_units = 0

    print("=" * 80)
    print("   GENERATING IMMUTABLE SHA-256 MANIFEST FOR TRAFFIC P1.2 BATCH (REVISED)")
    print("=" * 80)

    for item in DOC_METADATA:
        filename = item["filename"]
        filepath = RAW_DIR / filename
        if not filepath.exists():
            raise FileNotFoundError(f"File {filepath} not found!")

        sha256_hash = calculate_sha256(filepath)
        size_bytes = filepath.stat().st_size
        retrieved_at = datetime.now().isoformat()
        total_legal_articles += item["source_articles_count"]
        total_qcvn_units += item["attached_units_count"]

        doc_entry = {
            "source_document_id": item["source_document_id"],
            "official_number": item["official_number"],
            "filename": filename,
            "relative_path": f"data/01_raw/traffic_p1_2_batch/{filename}",
            "source_authority": item["source_authority"],
            "title": item["title"],
            "issue_date": item["issue_date"],
            "effective_date": item["effective_date"],
            "source_url": item["source_url"],
            "retrieved_at": retrieved_at,
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
            "attached_regulation": item.get("attached_regulation"),
            "attached_units_count": item.get("attached_units_count", 0),
            "notes": item["notes"],
            "status": "RAW_IMMUTABLE_SEALED"
        }
        manifest_documents.append(doc_entry)
        print(f"[+] Sealed {filename}:")
        print(f"    SHA-256: {sha256_hash}")
        print(f"    Size: {size_bytes} bytes | Articles: {item['source_articles_count']} | QCVN Units: {item['attached_units_count']}")

    manifest = {
        "batch_name": "Traffic P1.2 Legal Coverage Expansion Batch",
        "created_at": datetime.now().isoformat(),
        "total_documents": len(manifest_documents),
        "core_documents_count": len(manifest_documents),
        "total_legal_articles_count": total_legal_articles,
        "total_qcvn_technical_units_count": total_qcvn_units,
        "seal_algorithm": "SHA-256 (Raw Bytes)",
        "documents": manifest_documents
    }

    manifest_path = RAW_DIR / "manifest.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)

    print("-" * 80)
    print(f"[*] Manifest successfully created at: {manifest_path}")
    print(f"[*] Total Documents: {len(manifest_documents)}")
    print(f"[*] Total Legal Articles: {total_legal_articles} (Expected: 53 = 43 + 4 + 4 + 2)")
    print(f"[*] Total QCVN Technical Units: {total_qcvn_units} (Expected: 21)")
    print("=" * 80)

if __name__ == "__main__":
    create_manifest()
