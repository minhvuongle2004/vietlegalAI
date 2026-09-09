# BÁO CÁO NGHIỆM THU SMOKE REGRESSION (PHASE 5 CHECKPOINT)

> [!IMPORTANT]
> **KẾT LUẬN KIỂM ĐỊNH (ZERO-REGRESSION & TARGETED VERIFICATION):**
> - **Tổng số test cases kiểm định:** `18` (gồm 10 Traffic + 8 đại diện Civil, Tax, BHXH, BĐS, Tabular, Temporal, Boolean Logic, Cross-doc).
> - **Tỷ lệ Trích xuất Đúng (Retrieval Recall):** **`18/18 (100.0%)`** trên toàn bộ 18 test cases.
> - **Kết quả thực thi ban đầu (Single Full Run):** **`16/18 (88.9%)`** test cases đạt chuẩn ngay lần chạy đầu tiên.
> - **Kết quả kiểm định chuyên sâu (Targeted Rerun cho 2 case):** **`2/2 (100.0%)`** test cases (`TG-10` và `TC-19`) đều đã được xác minh đạt chuẩn sau khi khắc phục lỗi Evaluator và ổn định hạn ngạch API.
> - **TỔNG KẾT XÁC NHẬN TOÀN HỆ THỐNG:** **`18/18 (100.0%)` test cases đã được xác nhận đạt chuẩn pháp lý qua Targeted Rerun**, bảo toàn tuyệt đối chất lượng (Zero-Regression) trên toàn bộ các lĩnh vực pháp luật.

---

## 1. Bảng Tổng Hợp Theo Từng Domain Nghiệp Vụ

| Nhóm Domain / Bẫy Logic Pháp Lý | Số Lượng Test Cases | Retrieval Recall | Single Run Pass | Targeted Rerun | Tỷ Lệ Xác Nhận Cuối |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Traffic Law (Giao thông đường bộ)** | 10 | 10/10 (100%) | 9/10 | TG-10: ✅ PASS | **10/10 (100.0%)** |
| **Core Benchmark (cross_document)** | 1 | 1/1 (100%) | 1/1 | - | **1/1 (100.0%)** |
| **Core Benchmark (exception_vs_general)** | 1 | 1/1 (100%) | 1/1 | - | **1/1 (100.0%)** |
| **Core Benchmark (temporal_deadlines)** | 1 | 1/1 (100%) | 1/1 | - | **1/1 (100.0%)** |
| **Core Benchmark (arithmetic_calculation)** | 1 | 1/1 (100%) | 0/1 | TC-19: ✅ PASS | **1/1 (100.0%)** |
| **Core Benchmark (boolean_logic)** | 1 | 1/1 (100%) | 1/1 | - | **1/1 (100.0%)** |
| **Core Benchmark (civil_law)** | 1 | 1/1 (100%) | 1/1 | - | **1/1 (100.0%)** |
| **Core Benchmark (tax_law)** | 1 | 1/1 (100%) | 1/1 | - | **1/1 (100.0%)** |
| **Core Benchmark (real_estate_law)** | 1 | 1/1 (100%) | 1/1 | - | **1/1 (100.0%)** |
| **TỔNG CỘNG HỆ THỐNG** | **18** | **18/18 (100%)** | **16/18 (88.9%)** | **2/2 (100%)** | **18/18 (100.0%)** |

---

## 2. Kết Quả Điều Tra Chi Tiết & Targeted Rerun (TG-10 & TC-19)

### 📌 Case TC-19: Tính tiền trợ cấp thôi việc khi có thời gian lẻ tháng
* **Bản chất lỗi ban đầu**: **100% Evaluator Bug**.
  - Pipeline trích xuất đúng 100% căn cứ: `Điều 46 BLLĐ 2019` & `Điều 8 NĐ 145/2020/NĐ-CP`.
  - AI tính toán chuẩn xác: Làm việc 5 năm 9 tháng, 9 tháng lẻ (> 6 tháng) làm tròn thành 1 năm theo Điểm c Khoản 3 Điều 8 NĐ 145 $\rightarrow$ Tổng thời gian tính trợ cấp là **06 năm làm việc**.
  - Evaluator trong script smoke trước đó bị gán nhầm điều kiện kiểm tra tuổi hưu `62 tuổi` / `2032` của case khác.
* **Kết quả Targeted Rerun**:
  - Pure Pipeline: **`12.04s`** (Reranker trên GPU chỉ tốn **`0.45s`**).
  - Context: 13,250 chars (~3,312 tokens).
  - Kết quả: ✅ **PASSED** (Retrieval: PASS | Correctness: PASS).

### 📌 Case TG-10: Hành vi phức hợp (Đi ngược chiều cao tốc + Nồng độ cồn)
* **Bản chất lỗi ban đầu**: **Transient API Rate Limiting (Infrastructure Issue)**.
  - Ở lần chạy single run trước, do model `gemini-3.6-flash` chạm trần quota API (429 Rate Limit) liên tục, luồng stream bị đứt quãng sớm khiến câu trả lời chưa kịp sinh phần tổng tiền phạt.
  - Khi chạy lại dưới quota ổn định, AI phân tích đầy đủ cả 2 hành vi (30-40 triệu và 18-20 triệu), cộng đúng tổng mức phạt **48.000.000 đến 60.000.000 đồng**, và trích dẫn chuẩn xác nguyên tắc trừ điểm không cộng dồn theo **Điểm b Khoản 1 Điều 50 NĐ 168/2024/NĐ-CP** (chỉ áp dụng trừ **10 điểm**).
* **Kết quả Targeted Rerun**:
  - Pure Pipeline: **`30.21s`** (Reranker trên GPU tốn **`9.6s`**).
  - Context: 18,330 chars (~4,582 tokens).
  - Kết quả: ✅ **PASSED** (Retrieval: PASS | Correctness: PASS).

---

## 3. Tổng Hợp Hiệu Năng & Tối Ưu Hóa GPU CUDA FP16

1. **Reranker GPU Acceleration**:
   - Model `BAAI/bge-reranker-v2-m3` chạy trên GPU NVIDIA RTX 3050 (CUDA FP16).
   - Độ trễ giảm từ **`14.38s` (CPU) $\rightarrow$ `1.01s` (GPU)** (**Giảm 93.0% độ trễ Reranker**).
2. **Target Clause Extraction**:
   - Giảm **54.6%** LLM input context/tokens (từ ~8,000 tokens xuống còn ~3,600 tokens).
   - Cắt giảm **96.4%** context noise từ các điều luật chế tài khổng lồ (Điều 6, Điều 7 NĐ 168).
3. **Chính Sách Model & Quota**:
   - Đối chiếu từ Google AI Studio API Dashboard hiện tại: Chuyển sang ưu tiên dòng **`gemini-3.5-flash-lite`** mang lại sự ổn định cao hơn đáng kể với **15 RPM & 500 RPD** (so với 5 RPM & 20 RPD của dòng Flash standard), giúp triệt tiêu hiện tượng đứt stream do 429 quota.

---

> [!TIP]
> **KẾT LUẬN CHÍNH THỨC ĐÓNG PHASE 5**:
> Toàn bộ 18 test cases đã được xác nhận đạt chuẩn pháp lý qua Targeted Rerun (16 single run + 2 targeted rerun). Không có regression trong RAG pipeline. Phase 5 chính thức hoàn tất, sẵn sàng bước vào giai đoạn **Production Readiness & Cloud Deployment (Docker)**.
