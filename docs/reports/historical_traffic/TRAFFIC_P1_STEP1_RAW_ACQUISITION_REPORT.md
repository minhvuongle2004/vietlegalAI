# BÁO CÁO NGHIỆM THU BƯỚC 1: OFFICIAL SOURCE ACQUISITION & SHA-256 MANIFEST
## Dự án: VietLegal AI – Mở rộng Legal Coverage Mảng Giao thông đường bộ (Traffic P1)
**Thời gian hoàn thành:** 10/09/2026  
**Thư mục lưu trữ RAW:** `data/01_raw/traffic_p1_batch/`  
**Tập tin Niêm phong:** [`data/01_raw/traffic_p1_batch/manifest.json`](file:///d:/Đi%20làm/VietLegal%20AI/data/01_raw/traffic_p1_batch/manifest.json)  
**Trạng thái Thẩm định:** 🟢 **100% PASSED (8/8 Văn bản, 137/137 Điều nguồn Core được niêm phong)**

---

## I. TỔNG QUAN KẾT QUẢ THỰC HIỆN BƯỚC 1

Tuân thủ nghiêm ngặt chỉ đạo của Mentor:
1. **Full-document scope**: Thu thập toàn văn toàn bộ **137 Điều nguồn** thuộc 6 văn bản Current Core (không cắt gọt hay chọn lọc riêng lẻ từng điều).
2. **Immutable RAW & SHA-256 Manifest**: Mỗi file văn bản gốc được lưu trữ nguyên trạng và tính toán mã băm SHA-256 trực tiếp trên chuỗi byte gốc.
3. **Mô hình hóa Phân loại 3 Chiều (Multi-Dimensional Classification)**:
   - `LEGAL STATUS`: CURRENT | HISTORICAL | PROVISION-HISTORICAL
   - `INGESTION STATUS`: CORE | KNOWN_GAP | REFERENCE_ONLY
   - `DOCUMENT ROLE`: PRIMARY | AMENDMENT_SOURCE | CONSOLIDATED_REFERENCE
4. **Tách biệt `source_status` và `normalized_status`**: Ghi nhận nguyên văn trạng thái từ CSDL Quốc gia/Cơ quan ban hành, tách rời trạng thái chuẩn hóa nội bộ của hệ thống.
5. **Bảo toàn 100% Baseline**: Collection Production trên Qdrant Cloud (7.170 points) và 25 cases benchmark baseline được đóng băng hoàn toàn, không bị tác động.

---

## II. BẢNG DANH MỤC 8 VĂN BẢN VÀ MÃ BĂM SHA-256 NIÊM PHONG

| Ký hiệu Văn bản | Tên File RAW | Số Điều | Phân loại 3 Chiều | SHA-256 (Raw Bytes Hash) | Trạng thái Thẩm tra |
| :--- | :--- | :---: | :--- | :--- | :---: |
| **73/2024/TT-BCA** | `73_2024_TT_BCA.html` | 33 | `CURRENT` · `CORE` · `PRIMARY` | `ff1caf01926a56fc0379b279cde1f5f999a3dce9a4b29519e6f62e9bdd162ab7` | 🟢 **PASS** |
| **89/2026/NĐ-CP** | `89_2026_ND_CP.html` | 27 | `CURRENT` · `CORE` · `PRIMARY` | `c2d87332d998aa38f1dd54247af213657892918ad6679334d52fd9602b99d4d5` | 🟢 **PASS** |
| **30/2026/TT-BXD** | `30_2026_TT_BXD.html` | 32 | `CURRENT` · `CORE` · `PRIMARY` | `73500e10c8f77369e8472bc4f359c6be1a8666f5fa96c68930169ce2a02f00d2` | 🟢 **PASS** |
| **65/2024/TT-BCA** | `65_2024_TT_BCA.html` | 11 | `CURRENT` · `CORE` · `PRIMARY` | `83a7773a743bf12e220762f7163cb6d4818cd32a08cb1de30b1b953a8a88db65` | 🟢 **PASS** |
| **12/2025/TT-BXD** | `12_2025_TT_BXD.html` | 31 | `CURRENT` · `CORE` · `PRIMARY` | `c5beb95de897f1d14d1c622b73fe660124d89d7c1244efe38623ee501bde7267` | 🟢 **PASS** |
| **19/2026/TT-BXD** | `19_2026_TT_BXD.html` | 3 | `CURRENT` · `CORE` · `AMENDMENT_SOURCE` | `71037c7283c9a484e61ddaac68cc8c35c929d63d6e1095ac0d88ab15b9de7038` | 🟢 **PASS** |
| **26/VBHN-BXD** | `26_2026_VBHN_BXD.html`| 31 | `CURRENT` · `REFERENCE_ONLY` · `CONSOLIDATED_REFERENCE` | `510ba81fdce37b1b460ee00e41723ec8868a88d6b7deeb568e9260567e6444b3` | 🟢 **PASS** |
| **28/2024/TT-BCA** | `28_2024_TT_BCA.html` | 4 | `PROVISION-HISTORICAL` · `CORE` · `PRIMARY` | `4e0bed01bd06f5e6bf7935e05545185d1865ef7bfa7a66c1e368c25940fde916` | 🟢 **PASS** |

> **Tổng kết:**
> - **6 Current Core Documents:** 33 + 27 + 32 + 11 + 31 + 3 = **Đúng 137 Điều nguồn**.
> - **1 Consolidated Reference:** 31 Điều.
> - **1 Provision-Historical Document:** 4 Điều (Điều 1-2 bãi bỏ, Điều 3-4 còn hiệu lực).

---

## III. CHI TIẾT MÔ HÌNH HÓA DỮ LIỆU ĐẶC BIỆT

### 1. Cụm CSGT: TT 73/2024 & Granular Repeal TT 28/2024
- `73_2024_TT_BCA.html`: Toàn văn 33 Điều, chứa:
  - **Điều 11**: 4 trường hợp Cảnh sát giao thông được dừng phương tiện.
  - **Điều 12**: Kiểm soát thông tin giấy tờ trên môi trường điện tử (VNeID); tước/tạm giữ giấy tờ điện tử trên cơ sở dữ liệu.
  - **Điều 32**: Khoản 2 bãi bỏ toàn bộ TT 32/2023 và bãi bỏ Điều 1 TT 28/2024.
- `28_2024_TT_BCA.html`: Toàn văn 4 Điều, được quản lý ở provision level:
  - `source_status`: `"Còn hiệu lực"` (nguyên văn CSDL Quốc gia về VBPL).
  - `normalized_status`: `"PARTIALLY_AFFECTED"`.
  - **Điều 1**: `legal_status: REPEALED`, `current_retrieval_eligible: false`.
  - **Điều 2**: `legal_status: REPEALED`, `current_retrieval_eligible: false`.
  - **Điều 3 & 4**: `legal_status: ACTIVE`, `current_retrieval_eligible: true`, `primary_current_core: false` *(bảo đảm truy xuất được khi hỏi đích danh, không gây nhiễu ranking tuần tra CSGT)*.

### 2. Cụm Đăng kiểm: Lineage TT 30/2026 thay thế TT 47/2024 & NĐ 89/2026
- `89_2026_ND_CP.html`: 27 Điều quy định điều kiện cơ sở đăng kiểm và niên hạn xe cơ giới (xe tải 25 năm, xe khách 20 năm).
- `30_2026_TT_BXD.html`: 32 Điều quy định quy trình kiểm định số hóa:
  - **Điều 6**: Miễn kiểm định lần đầu xe mới sản xuất trong 03 năm.
  - **Điều 9**: Cấp Giấy chứng nhận và Tem kiểm định điện tử qua VNeID.
  - **Điều 10**: Miễn kiểm định lại khi đổi biển số, sang tên đổi chủ, chuyển vùng.
  - **Điều 11**: Lắp thêm baga mui, cản trước/sau dưới 4cm, đèn chính hãng công suất tương đương... không coi là cải tạo và không phải khám lại xe.
  - **Điều 32**: Thay thế trực tiếp TT 47/2024/TT-BGTVT từ ngày 01/07/2026.

### 3. Cụm Tải trọng: TT 12/2025, TT 19/2026 & 26/VBHN-BXD
- `12_2025_TT_BXD.html`: 31 Điều quy định tải trọng trục đơn (10t), trục kép (11-18t), trục ba (21-24t), tổng trọng lượng xe và quy trình cấp phép lưu hành.
- `19_2026_TT_BXD.html`: 3 Điều sửa đổi trực tiếp:
  - Sửa Khoản 2 Điều 5: Cụm trục kép trang bị hệ thống treo khí nén (bóng hơi) nâng lên mức tối đa **19,0 tấn**.
  - Sửa Khoản 3 Điều 7: Đoàn xe đầu kéo 5 trục dùng bóng hơi trên cao tốc nâng lên **45,0 tấn**.
  - Sửa Điều 16: Rút ngắn thời gian cấp phép lưu hành trực tuyến xuống **24 giờ**.
- `26_2026_VBHN_BXD.html`: 31 Điều đối chiếu xác thực hợp nhất hoàn hảo.

---

## IV. KẾT QUẢ XÁC MINH MANIFEST (AUTOMATED VERIFICATION)

Script tự động [`pipeline/traffic_p1_batch/verify_raw_manifest.py`](file:///d:/Đi%20làm/VietLegal%20AI/pipeline/traffic_p1_batch/verify_raw_manifest.py) đã thực hiện kiểm tra đối chiếu chéo độc lập:
```text
Verifying Manifest: Traffic P1 Legal Coverage Expansion Batch
Total documents: 8
Reported Core Articles: 137

[PASS] 73_2024_TT_BCA.html: SHA-256 match: True | Articles: 33/33
[PASS] 89_2026_ND_CP.html:  SHA-256 match: True | Articles: 27/27
[PASS] 30_2026_TT_BXD.html: SHA-256 match: True | Articles: 32/32
[PASS] 65_2024_TT_BCA.html: SHA-256 match: True | Articles: 11/11
[PASS] 12_2025_TT_BXD.html: SHA-256 match: True | Articles: 31/31
[PASS] 19_2026_TT_BXD.html: SHA-256 match: True | Articles: 3/3
[PASS] 26_2026_VBHN_BXD.html: SHA-256 match: True | Articles: 31/31
[PASS] 28_2024_TT_BCA.html: SHA-256 match: True | Articles: 4/4

============================================================
Overall Verification Result: 100% PASSED
Total Current Core Articles Verified: 137 / 137
============================================================
```

---

## V. KẾ HOẠCH BƯỚC TIẾP THEO: BƯỚC 2 (FULL-DOCUMENT PARSER)

Bước 1 đã hoàn thành trọn vẹn, đúng 100% cam kết với Mentor. Hệ thống sẵn sàng bước sang:
1. **Bước 2: Full-Document Clause Parser & Provision-Level Metadata**:
   - Bóc tách toàn văn 137 Điều nguồn + các điều khoản liên quan thành cấu trúc JSON chuẩn mực trong `data/03_parsed/traffic_p1_batch/`.
   - Áp dụng triệt để nguyên tắc chunking soft target (~75 words), bảo toàn tính toàn vẹn ngữ nghĩa của Khoản, Điểm, Exception và Bảng quy định.
   - Gắn quan hệ `replaces`, `amends`, `effective_date`, `source_status` / `normalized_status`.
