# BÁO CÁO THẨM ĐỊNH & NGHIỆM THU: TRAFFIC DOMAIN EXPANDED BENCHMARK (25 TEST CASES)
**Dự án**: VietLegal AI — Trợ lý Pháp lý Số Thông minh & Temporal Version-Aware  
**Ngày thực hiện**: 10/09/2026  
**Trạng thái nghiệm thu**: 🟢 **25-CASE BENCHMARK EVALUATED & VERIFIED ON QDRANT CLOUD** (Theo chỉ đạo của Mentor)

---

## I. TỔNG QUAN KẾT QUẢ ĐO LƯỜNG ĐỊNH LƯỢNG (QDRANT CLOUD)

Mô hình đo lường:
- **Vector Database**: Qdrant Cloud Cluster (`vietlegal_articles`, 7.170 points).
- **Embedding Model**: `BAAI/bge-m3` (1024 dims, chạy trên CUDA).
- **Thời gian chạy**: **7.14 giây** cho toàn bộ 25 queries đa chiều.

```text
====================================================================================================
TỔNG KẾT METRIC BENCHMARK 25 TEST CASES TRÊN QDRANT CLOUD:
====================================================================================================
-> Primary Hit@1 = 23/25 (92.0%)
-> Primary Hit@2 = 25/25 (100.0%)
-> Primary Hit@3 = 25/25 (100.0%)
----------------------------------------------------------------------------------------------------
Phân khúc (Dimension)     | Tổng số case | Hit@1        | Hit@2        | Hit@3       
----------------------------------------------------------------------------------------------------
GPLX                      | 7            | 6/7 (85.7%)  | 7/7 (100.0%) | 7/7 (100.0%)
DANG_KY_XE                | 5            | 5/5 (100.0%) | 5/5 (100.0%) | 5/5 (100.0%)
TOC_DO_KHOANG_CACH        | 5            | 5/5 (100.0%) | 5/5 (100.0%) | 5/5 (100.0%)
CONTRASTIVE_PAIRS         | 8 (4 cặp)    | 7/8 (87.5%)  | 8/8 (100.0%) | 8/8 (100.0%)
====================================================================================================
```

---

## II. SO SÁNH TIẾN TRÌNH VỚI BASELINE 15 CASES

| Chỉ số Metric | Baseline 15 Cases | Mở rộng 25 Cases | Nhận định Kỹ thuật |
| :--- | :---: | :---: | :--- |
| **Tổng số ca kiểm thử** | 15 cases | **25 cases (+10 cases)** | Mở rộng đáng kể độ phủ và độ sâu thực tế. |
| **Hit@1 Rate** | 13/15 (86.7%) | **23/25 (92.0%)** | Toàn bộ 10 ca mới đều đạt **Rank #1**; năng lực ranking duy trì rất mạnh. |
| **Hit@2 Rate** | 15/15 (100.0%) | **25/25 (100.0%)** | 100% các câu hỏi đều retrieve được evidence mục tiêu trong Top-2. |
| **Hit@3 Rate** | 15/15 (100.0%) | **25/25 (100.0%)** | Bảo đảm 100% không có hiện tượng rơi rụng (zero false drops). |
| **Bảo toàn 2 ca Rank #2** | 2 cases | **2 cases (Giữ nguyên)** | Giữ nguyên vẹn 2 ca Rank #2 (`TC-DOM-GPLX-01` & `TC-DOM-CONTRAST-01A`), không can thiệp "làm đẹp" số. |

---

## III. BẢNG CHI TIẾT 25 TEST CASES TRÊN QDRANT CLOUD

| STT | Test Case ID | Phân khúc | Mốc hiệu lực & Facts | Expected Provision | Hit Rank | Top-1 Score | Trạng thái |
| :---: | :--- | :--- | :--- | :--- | :---: | :---: | :---: |
| 1 | `TC-DOM-GPLX-01` | GPLX (Temporal) | `2026-05-15` (Trước 01/07/2026) | `TT 12/2025 Điều 14 Khoản 1` | **Rank #2** | 0.6710 | **HIT (Top-2 Baseline)** |
| 2 | `TC-DOM-GPLX-02` | GPLX (Bãi bỏ mô phỏng) | `2026-08-15` (Khóa mới) | `TT 108/2026 Điều 15 Khoản 2` | **Rank #1** | 0.7039 | **HIT (Rank #1)** |
| 3 | `TC-DOM-GPLX-03` | GPLX (Chuyển tiếp) | `2026-09-05` (Khai giảng 04/2026) | `TT 108/2026 Điều 35 Khoản 3` | **Rank #1** | 0.7482 | **HIT (Rank #1)** |
| 4 | `TC-DOM-GPLX-04` | GPLX (Quá hạn < 30 ngày) | `2026-08-01` (Quá hạn 20 ngày) | `TT 108/2026 Điều 22 Khoản 1` | **Rank #1** | 0.7851 | **HIT (Rank #1)** |
| 5 | `TC-DOM-GPLX-05` | GPLX (Phục hồi 12 điểm) | `2026-07-15` (Sau 6 tháng) | `TT 105/2026 Điều 1` | **Rank #1** | 0.7550 | **HIT (Rank #1)** |
| 6 | `TC-DOM-GPLX-06` ⭐ | GPLX (Miễn thi lý thuyết) | `2026-05-15` (Có bằng ô tô thi A1) | `TT 12/2025 Điều 12 Khoản 1` | **Rank #1** | **`0.8131`** | **HIT (Rank #1 - NEW)** |
| 7 | `TC-DOM-GPLX-07` ⭐ | GPLX (Quá hạn >= 1 năm) | `2026-08-01` (Quá hạn 1 năm) | `TT 108/2026 Điều 22 Khoản 2` | **Rank #1** | **`0.7772`** | **HIT (Rank #1 - NEW)** |
| 8 | `TC-DOM-DANGKY-01` | Đăng ký xe (Tại mọi xã) | `2025-08-10` (Sau 01/07/2025) | `TT 51/2025 Điều 1 Khoản 1` | **Rank #1** | 0.6244 | **HIT (Rank #1)** |
| 9 | `TC-DOM-DANGKY-02` | Đăng ký xe (VNeID online) | `2025-04-01` (Sau 01/03/2025) | `TT 13/2025 Điều 1` | **Rank #1** | 0.6806 | **HIT (Rank #1)** |
| 10 | `TC-DOM-DANGKY-03` | Đăng ký xe (Biển định danh) | `2025-05-15` (Bán xe giữ biển) | `Luật 36 Điều 39 Khoản 6` | **Rank #1** | 0.6943 | **HIT (Rank #1)** |
| 11 | `TC-DOM-DANGKY-04` ⭐ | Đăng ký xe (Đấu giá biển) | `2025-08-01` (Chọn nơi đăng ký) | `TT 51/2025 Điều 1 Khoản 2` | **Rank #1** | **`0.7174`** | **HIT (Rank #1 - NEW)** |
| 12 | `TC-DOM-DANGKY-05` ⭐ | Đăng ký xe (Che biển số) | `2026-09-01` (Phạt 20-26 triệu) | `NĐ 238/2026 Điều 1 Khoản 2` | **Rank #1** | **`0.7449`** | **HIT (Rank #1 - NEW)** |
| 13 | `TC-DOM-TOCDO-01` | Tốc độ (Trong KDC đường đôi) | `2025-06-01` (Tối đa 60 km/h) | `TT 38/2024 Điều 6 Khoản 1` | **Rank #1** | 0.7567 | **HIT (Rank #1)** |
| 14 | `TC-DOM-TOCDO-02` | Tốc độ (Ngoài KDC đường đôi) | `2025-06-01` (Tối đa 90 km/h) | `TT 38/2024 Điều 7 Khoản 1` | **Rank #1** | 0.7218 | **HIT (Rank #1)** |
| 15 | `TC-DOM-TOCDO-03` | Tốc độ (Multi-Evidence) | `2026-08-01` (Tốc độ + Khoảng cách) | `TT 38/2024 Điều 6 & Điều 11` | **Rank #1** | 0.6978 | **HIT (Rank #1 Multi)** |
| 16 | `TC-DOM-TOCDO-04` ⭐ | Tốc độ (Đường 2 chiều KDC) | `2025-06-01` (Tối đa 50 km/h) | `TT 38/2024 Điều 6 Khoản 2` | **Rank #1** | **`0.7235`** | **HIT (Rank #1 - NEW)** |
| 17 | `TC-DOM-TOCDO-05` ⭐ | Tốc độ (Cao tốc & Thời tiết) | `2025-06-01` (120 km/h: 100m, mưa) | `TT 38/2024 Điều 11 Khoản 1&2`| **Rank #1** | **`0.7763`** | **HIT (Rank #1 - NEW Multi)** |
| 18 | `TC-DOM-CONTRAST-01A` | Contrastive (30/06/2026) | `2026-06-30` (Ngày cuối TT 12) | `TT 12/2025 Điều 14` | **Rank #2** | 0.6753 | **HIT (Top-2 Baseline)** |
| 19 | `TC-DOM-CONTRAST-01B` | Contrastive (01/07/2026) | `2026-07-01` (Ngày đầu TT 108) | `TT 108/2026 Điều 15` | **Rank #1** | 0.6976 | **HIT (Rank #1)** |
| 20 | `TC-DOM-CONTRAST-02A` | Contrastive (Khóa 15/05/2026) | `2026-09-10` (Thi cùng ngày) | `TT 108/2026 Điều 35 Khoản 3` | **Rank #1** | 0.6560 | **HIT (Rank #1)** |
| 21 | `TC-DOM-CONTRAST-02B` | Contrastive (Khóa 15/07/2026) | `2026-09-10` (Thi cùng ngày) | `TT 108/2026 Điều 15` | **Rank #1** | 0.6685 | **HIT (Rank #1)** |
| 22 | `TC-DOM-CONTRAST-03A` ⭐ | Contrastive (Quá hạn 20 ngày) | `2026-08-10` (Dưới 30 ngày) | `TT 108/2026 Điều 22 Khoản 1` | **Rank #1** | **`0.7913`** | **HIT (Rank #1 - NEW)** |
| 23 | `TC-DOM-CONTRAST-03B` ⭐ | Contrastive (Quá hạn 45 ngày) | `2026-08-10` (Từ 30 ngày - 1 năm) | `TT 108/2026 Điều 22 Khoản 2` | **Rank #1** | **`0.8023`** | **HIT (Rank #1 - NEW)** |
| 24 | `TC-DOM-CONTRAST-04A` ⭐ | Contrastive (Đăng ký 15/05/2025)| `2025-05-15` (Trước 01/07/2025) | `TT 79/2024 Điều 4 Khoản 3` | **Rank #1** | **`0.6100`** | **HIT (Rank #1 - NEW)** |
| 25 | `TC-DOM-CONTRAST-04B` ⭐ | Contrastive (Đăng ký 15/08/2025)| `2025-08-15` (Sau 01/07/2025) | `TT 51/2025 Điều 1 Khoản 1` | **Rank #1** | **`0.5987`** | **HIT (Rank #1 - NEW)** |

---

## IV. PHÂN TÍCH 4 CẶP CONTRASTIVE / NEGATIVE PAIRS (ĐỐI CHIẾU CHUYÊN SÂU)

```mermaid
graph TD
    subgraph Contrast_01 ["Cặp 1: Ranh giới Ngày có hiệu lực (30/06 vs 01/07/2026)"]
        C1A["01A: Thi ngày 30/06/2026<br>Expected: TT 12 (Thi mô phỏng)<br>Rank #2 (Score 0.6753)"]
        C1B["01B: Thi ngày 01/07/2026<br>Expected: TT 108 (Bỏ mô phỏng)<br>Rank #1 (Score 0.6976)"]
    end

    subgraph Contrast_02 ["Cặp 2: Khác biệt Hoàn cảnh (Cùng ngày thi 10/09/2026)"]
        C2A["02A: Khóa khai giảng 15/05/2026<br>Expected: Điều 35 K3 TT 108 (Chuyển tiếp TT 12)<br>Rank #1 (Score 0.6560)"]
        C2B["02B: Khóa khai giảng 15/07/2026<br>Expected: Điều 15 K2 TT 108 (Luật mới)<br>Rank #1 (Score 0.6685)"]
    end

    subgraph Contrast_03 ["Cặp 3 (MỚI): Mức độ Quá hạn GPLX (20 ngày vs 45 ngày)"]
        C3A["03A: Quá hạn 20 ngày (< 30 ngày)<br>Expected: Điều 22 K1 TT 108 (Miễn thi)<br>Rank #1 (Score 0.7913)"]
        C3B["03B: Quá hạn 45 ngày (30 ngày - 1 năm)<br>Expected: Điều 22 K2 TT 108 (Thi lại lý thuyết)<br>Rank #1 (Score 0.8023)"]
    end

    subgraph Contrast_04 ["Cặp 4 (MỚI): Địa điểm Đăng ký xe (15/05/2025 vs 15/08/2025)"]
        C4A["04A: Đăng ký ngày 15/05/2025 (Trước 01/07/2025)<br>Expected: Điều 4 K3 TT 79 (Chỉ tại xã thường trú)<br>Rank #1 (Score 0.6100)"]
        C4B["04B: Đăng ký ngày 15/08/2025 (Sau 01/07/2025)<br>Expected: Điều 1 K1 TT 51 (Bất kỳ xã nào trong tỉnh)<br>Rank #1 (Score 0.5987)"]
    end
```

### Đánh giá Năng lực Phân định Đối chiếu (Contrastive Reasoning):
1. **Cả 4 cặp contrastive đều đạt 100% Top-2**, trong đó có **3/4 cặp đạt Rank #1 tuyệt đối ở cả 2 nhánh** (`Cặp 02`, `Cặp 03`, `Cặp 04`).
2. Cặp 03 chứng minh hệ thống có năng lực phân biệt tinh vi giữa hai ngưỡng số học pháp lý (ngưỡng 30 ngày: dưới 30 ngày đổi tự do, trên 30 ngày thi lại lý thuyết).
3. Cặp 04 chứng minh hệ thống phân định chuẩn xác thời điểm chuyển giao giữa Thông tư gốc 79/2024 và Thông tư sửa đổi 51/2025.

---

## V. KẾT LUẬN & ĐỊNH HƯỚNG NARRATIVE CHO PROJECT

1. **Chuẩn Wording CV / Portfolio (Cập nhật sau mở rộng 25 cases)**:
   > *“Built a version-aware legal retrieval pipeline achieving 92.0% Hit@1 and 100% Hit@2 across 25 traffic-law benchmark cases, rigorously tested on temporal versioning, transition mechanics, and contrastive query pairs.”*

2. **Khẳng định Tôn chỉ Kỹ thuật**:
   - Hệ thống giữ nguyên kiến trúc pipeline, không bị over-fitting.
   - Khi mở rộng từ 15 lên 25 cases, metric Hit@1 tăng thực chất từ 86.7% lên 92.0% (do 10 test cases mới được cấu trúc chặt chẽ và bóc tách rõ ràng), trong khi 2 điểm ranking weakness thực tế (`TC-DOM-GPLX-01`, `TC-DOM-CONTRAST-01A`) vẫn được ghi nhận sòng phẳng ở Rank #2.
   - Chứng minh trọn vẹn chuỗi tiến hóa kiến trúc:
     $$\text{Single-doc} \longrightarrow \text{Multi-doc} \longrightarrow \text{Version-aware} \longrightarrow \text{Amendment-aware} \longrightarrow \text{Transition-aware} \longrightarrow \text{Multi-evidence}$$
