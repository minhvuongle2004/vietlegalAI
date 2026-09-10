# BÁO CÁO ĐÁNH GIÁ LẠI DENSE VÀ SPARSE TRÊN GROUND TRUTH CHUẨN HÓA V2
## STEP 1.9 — RE-RUN GOLD RETRIEVAL ON REVISED GROUND TRUTH

- **Ngày thực hiện**: 2026-09-11 00:15:00
- **Tập dữ liệu chuẩn hóa**: `gold_retrieval_225_cases_v2.json` & `data/gold_evaluation/gold_retrieval_225_cases_v2.json`
- **Số lượng cases**: 225 / 225 cases (100% bảo toàn)
- **Tình trạng Production**: 7.982 Qdrant points giữ nguyên tuyệt đối; 25 benchmark regression cases đóng băng độc lập.
- **Ràng buộc tuân thủ**: Không sửa Dense, không sửa Sparse, không chạy RRF, không đổi weight, không bật Reranker, không sửa Query Decomposition.

---

### I. BẢNG SO SÁNH HIỆU NĂNG V1 VS. V2 (METRIC CHANGE AFTER GROUND-TRUTH REVISION)

> [!NOTE]
> **Quy chuẩn diễn giải**: Sự thay đổi chỉ số giữa V1 và V2 dưới đây là **"Metric change after ground-truth revision"** (thay đổi thước đo sau khi chuẩn hóa ground-truth phản ánh đúng cấu trúc đa tầng pháp luật Việt Nam), **không phải** do can thiệp hay tối ưu hóa thuật toán truy xuất.

| Bộ truy xuất (Retrieval Mode) | Metric | Ground Truth V1 (Đơn nhãn) | Ground Truth V2 (Đa tầng chuẩn hóa) | Thay đổi (V2 vs V1) | Ghi chú kỹ thuật |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Dense-only** *(BGE-M3 trên Qdrant)* | **Hit@1** | 78 / 225 (**34.67%**) | **86 / 225 (38.22%)** | **+8 cases (+3.55%)** | 8 case tìm đúng luật mẹ/quy tắc thay thế ngay ở Rank 1 |
| | **Hit@3** | 106 / 225 (**47.11%**) | **115 / 225 (51.11%)** | **+9 cases (+4.00%)** | Đã vượt mốc 50% Top-3 |
| | **Hit@5** | 114 / 225 (**50.67%**) | **123 / 225 (54.67%)** | **+9 cases (+4.00%)** | 123 cases trúng căn cứ pháp lý hợp lệ trong Top 5 |
| **Sparse-only** *(PostgreSQL FTS Supabase)* | **Hit@1** | 8 / 225 (**3.56%**) | **13 / 225 (5.78%)** | **+5 cases (+2.22%)** | Bắt trúng từ vựng của các văn bản hướng dẫn/luật mẹ |
| | **Hit@3** | 12 / 225 (**5.33%**) | **20 / 225 (8.89%)** | **+8 cases (+3.56%)** | Cải thiện độ phủ từ khóa ở Top 3 |
| | **Hit@5** | 18 / 225 (**8.00%**) | **23 / 225 (10.22%)** | **+5 cases (+2.22%)** | Vượt mốc 10% ở Top 5 |

---

### II. HIỆU NĂNG THEO TỪNG LOẠI CĂN CỨ PHÁP LÝ (BY EVIDENCE TYPE)

Ground Truth V2 phân loại rõ ràng 4 nhóm căn cứ, giúp đánh giá chính xác hành vi của Dense và Sparse:

#### 1. Dense-only Retrieval:
| Phân loại (`evidence_type`) | Số ca | Hit@1 | Hit@3 | Hit@5 | Đánh giá chi tiết |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **`SINGLE`** | 53 | 14 (26.4%) | 19 (35.8%) | 20 (37.7%) | Căn cứ duy nhất; khó hơn do không có văn bản thay thế |
| **`MULTI_VALID`** | 44 | 18 (40.9%) | 25 (56.8%) | 27 (61.4%) | Hiệu năng cao vượt trội: 18 ca trúng Primary, 11 ca trúng Supporting |
| **`CO_REQUISITE`** | 28 | 7 (25.0%) | 13 (46.4%) | 13 (46.4%) | Có **8/28 cases (28.6%)** trúng ĐẦY ĐỦ cả bộ required evidence trong Top 5 |
| **`PRIMARY_PLUS_SUPPORTING`** | 100 | 47 (47.0%) | 58 (58.0%) | 63 (63.0%) | 63 ca trúng Primary; 18 ca đồng thời tìm thấy cả Supporting trong Top 5 |

#### 2. Sparse-only Retrieval:
| Phân loại (`evidence_type`) | Số ca | Hit@1 | Hit@3 | Hit@5 | Đánh giá chi tiết |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **`SINGLE`** | 53 | 1 (1.9%) | 1 (1.9%) | 2 (3.8%) | FTS yếu khi câu hỏi diễn giải ngữ nghĩa không trùng từ khóa |
| **`MULTI_VALID`** | 44 | 5 (11.4%) | 9 (20.5%) | 10 (22.7%) | Đạt 22.7% ở Top 5 nhờ bắt được từ vựng ở văn bản song hành |
| **`CO_REQUISITE`** | 28 | 0 (0.0%) | 2 (7.1%) | 2 (7.1%) | Chỉ có 1 ca đạt trọn bộ required evidence trong Top 5 |
| **`PRIMARY_PLUS_SUPPORTING`** | 100 | 7 (7.0%) | 8 (8.0%) | 9 (9.0%) | 9 ca trúng Primary; 14 ca trúng Supporting |

---

### III. THEO DÕI TÁC ĐỘNG TRÊN 17 CA FALSE-MISS

Toàn bộ 17 ca được chỉ ra trong chẩn đoán Tầng 1.5 (từng bị đánh MISS oan ở bộ đánh giá cũ) đã được kiểm chứng chi tiết:

| Mã Test Case | Câu hỏi tóm tắt | Dense V1 | Dense V2 | Sparse V2 | Căn cứ được công nhận trong V2 |
| :--- | :--- | :---: | :---: | :---: | :--- |
| **`GOLD-DIR-04`** | Tốc độ ô tô con khu dân cư | PASS (r=2) | **PASS (r=2)** | MISS | Primary (TT 38 Điều 6) |
| **`GOLD-DIR-05`** | Tốc độ xe máy đường 2 chiều | PASS (r=1) | **PASS (r=1)** | MISS | Primary (TT 38 Điều 6) |
| **`GOLD-DIR-06`** | Khoảng cách an toàn 80 km/h | PASS (r=1) | **PASS (r=1)** | MISS | Primary (TT 38 Đ11) + Supporting (Luật 36 Đ12) |
| **`GOLD-DIR-13`** | Biển số định danh theo mã định danh | MISS | MISS | **PASS (r=1)** | **Sparse cứu thành công ở Rank 1** (TT 79 Đ4) |
| **`GOLD-DIR-14`** | Thu hồi đăng ký khi chuyển nhượng xe | MISS | **PASS (r=1)** | MISS | **Cứu ở Rank 1**: Luật 36 Đ37 (`SUPPORTING_PARENT_LAW`) |
| **`GOLD-DIR-15`** | CSGT dừng xe khi tuần tra kiểm soát | MISS | **PASS (r=1)** | MISS | **Cứu ở Rank 1**: Luật 36 Đ65 (`SUPPORTING_PARENT_LAW`) |
| **`GOLD-DIR-20`** | Khoảng cách an toàn 60 km/h | PASS (r=1) | **PASS (r=1)** | MISS | Primary (TT 38 Đ11) + Supporting (Luật 36 Đ12) |
| **`GOLD-ART-12`** | Điều nào quy định khoảng cách an toàn | PASS (r=1) | **PASS (r=1)** | MISS | Primary (TT 38 Đ11) + Supporting (Luật 36 Đ12) |
| **`GOLD-ART-24`** | Cơ sở vật chất sát hạch lái xe | PASS (r=1) | **PASS (r=1)** | MISS | Primary (NĐ 94 Đ24) |
| **`GOLD-EXC-04`** | Xe ưu tiên không bị hạn chế tốc độ | PASS (r=1) | **PASS (r=1)** | MISS | Primary (Luật 36 Đ27) |
| **`GOLD-EXC-09`** | CSGT dừng xe không cần phát hiện lỗi | MISS | **PASS (r=1)** | MISS | **Cứu ở Rank 1**: Luật 36 Đ65 (`SUPPORTING_PARENT_LAW`) |
| **`GOLD-MUL-03`** | Cấp và quản lý biển số định danh | MISS | MISS | MISS | Dense trúng 2 Supporting nhưng chưa đủ bộ Co-Requisite |
| **`GOLD-MUL-07`** | Sát hạch lái xe theo NĐ 94 | PASS (r=1) | **PASS (r=1)** | MISS | Primary (NĐ 94 Đ24) |
| **`GOLD-MUL-24`** | Miễn giảm phí đường cao tốc | MISS | MISS | **PASS (r=1)** | **Sparse cứu thành công ở Rank 1** (NĐ 130 Đ4) |
| **`GOLD-AMD-20`** | Sửa đổi kiểm tra phanh con lăn TT 30 | PASS (r=1) | **PASS (r=1)** | MISS | Primary (TT 45 Đ1) |
| **`GOLD-HRD-02`** | Đèn đỏ có được rẽ phải không | MISS | **PASS (r=1)** | MISS | **Cứu ở Rank 1**: Luật 36 Đ11 (`SUPPORTING_PARENT_LAW`) |
| **`GOLD-HRD-13`** | Khoảng cách an toàn khi trời mưa | PASS (r=1) | **PASS (r=1)** | MISS | Primary (TT 38 Đ11) + Supporting (Luật 36 Đ12) |

> [!IMPORTANT]
> **Nhận xét then chốt**:
> - Trong 17 ca này, **10 ca** vốn đã được Dense tìm thấy ở Rank 1–2 ngay từ đầu (nhưng ở pipeline cũ bị RRF kéo tụt).
> - **4 ca** (`GOLD-DIR-14`, `GOLD-DIR-15`, `GOLD-EXC-09`, `GOLD-HRD-02`) trước đây bị đánh MISS vì Dense trả về luật mẹ (Luật 36), nay đã được công nhận **PASS ngay tại Rank 1** hoàn toàn xứng đáng.
> - **2 ca** (`GOLD-DIR-13`, `GOLD-MUL-24`) Dense bị trượt, nhưng **Sparse FTS lại tìm đúng chính xác ở Rank 1**!

---

### IV. TÍNH BỔ TRỢ (COMPLEMENTARITY ANALYSIS): DENSE VS. SPARSE

Phân tích giao thoa kết quả giữa Dense-only và Sparse-only trên toàn bộ 225 cases ở Top 5:

| Trạng thái Giao thoa | Số lượng Cases | Tỷ lệ (%) | Ý nghĩa Kiến trúc |
| :--- | :---: | :---: | :--- |
| **Dense PASS / Sparse FAIL** | **105** | **46.67%** | Dense vượt trội về hiểu ngữ nghĩa, suy luận câu hỏi gián tiếp |
| **Dense FAIL / Sparse PASS** | **5** | **2.22%** | **Vùng cứu hộ then chốt của Sparse (Lexical Anchor)** |
| **Cả hai cùng PASS** | **18** | **8.00%** | Vùng đồng thuận cao giữa từ khóa từ vựng và vector ngữ nghĩa |
| **Cả hai cùng FAIL** | **97** | **43.11%** | Các ca phức tạp (Temporal contrast đa mốc, thuật ngữ bẫy) |
| **Cận trên lý thuyết (Dense OR Sparse)** | **128 / 225** | **56.89%** | **Tiềm năng tối đa nếu kết hợp Hybrid hoàn hảo** |

#### Danh sách 5 ca Dense FAIL nhưng được Sparse cứu thành công:
1. **`[GOLD-DIR-11]` (Sparse Rank 2)**: *"Niên hạn sử dụng của xe ô tô chở hàng (xe tải) tối đa là bao nhiêu năm?"*
   - Căn cứ: `89/2026/NĐ-CP Điều 3`
   - Dense bị phân tán bởi từ khóa niên hạn chung; Sparse bắt trúng từ vựng "niên hạn sử dụng xe ô tô chở hàng".
2. **`[GOLD-DIR-12]` (Sparse Rank 2)**: *"Niên hạn sử dụng của xe ô tô chở người từ 10 chỗ ngồi trở lên tối đa là bao nhiêu năm?"*
   - Căn cứ: `89/2026/NĐ-CP Điều 3`
   - Sparse bắt trúng cụm từ vựng chính xác số chỗ ngồi và loại xe trong NĐ 89.
3. **`[GOLD-DIR-13]` (Sparse Rank 1)**: *"Biển số xe cơ giới được cấp và quản lý theo mã định danh của ai?"*
   - Căn cứ: `79/2024/TT-BCA Điều 4`
   - Dense tìm Luật 36; Sparse FTS bắt trúng trực tiếp câu chữ trong Thông tư 79.
4. **`[GOLD-MUL-24]` (Sparse Rank 1)**: *"Quy định về thu phí sử dụng đường bộ cao tốc theo Nghị định 130 và các trường hợp miễn phí gồm những gì?"*
   - Căn cứ: `130/2024/NĐ-CP Điều 4`
   - Sparse bắt trúng số hiệu văn bản "Nghị định 130" và từ khóa "thu phí cao tốc" đưa thẳng lên Rank 1.
5. **`[GOLD-AMD-27]` (Sparse Rank 1)**: *"Văn bản nào sửa đổi quy định phân cấp thẩm quyền đăng kiểm xe cơ giới theo Thông tư 30/2026/TT-BXD?"*
   - Căn cứ: `45/2026/TT-BXD Điều 1`
   - Sparse có lợi thế tuyệt đối khi truy vấn chứa số hiệu văn bản sửa đổi và từ khóa "thẩm quyền đăng kiểm".

---

### V. TRẢ LỜI 5 CÂU HỎI TRỌNG TÂM CỦA STEP 1.9

#### 1. Thực lực Dense-only trên ground truth mới?
- **Hit@1 = 38.22% (86/225)**, **Hit@3 = 51.11% (115/225)**, **Hit@5 = 54.67% (123/225)**.
- Dense-only là trụ cột cốt lõi mạnh nhất hiện tại, tự thân giải quyết được hơn một nửa số ca câu hỏi thực tế trong Top 5 mà không cần bất kỳ thủ thuật biến đổi truy vấn nào.

#### 2. Thực lực Sparse-only trên ground truth mới?
- **Hit@1 = 5.78% (13/225)**, **Hit@3 = 8.89% (20/225)**, **Hit@5 = 10.22% (23/225)**.
- Sparse FTS đơn thuần còn khiêm tốn (khoảng 10%), nhưng đóng vai trò là chiếc neo từ vựng chính xác (Lexical Anchor) cho các truy vấn có số hiệu văn bản cụ thể hoặc thuật ngữ chuyên ngành định lượng (niên hạn, số chỗ ngồi).

#### 3. Metric thay đổi bao nhiêu do label revision?
- **Dense**: Tăng +3.55% ở Hit@1, +4.00% ở Hit@3, +4.00% ở Hit@5.
- **Sparse**: Tăng +2.22% ở Hit@1, +3.56% ở Hit@3, +2.22% ở Hit@5.
- Sự thay đổi này giải phóng những ca bị đánh trượt oan (false-miss) do hệ thống tìm ra luật mẹ hoặc văn bản quy định đồng thời có giá trị pháp lý tương đương.

#### 4. Dense và Sparse bổ trợ nhau ở đâu?
- Cận trên lý thuyết khi kết hợp Dense hoặc Sparse đạt **56.89% (128/225)**.
- Sparse hỗ trợ giải cứu ít nhất 5 ca mà Dense hoàn toàn bất lực (đặc biệt là các câu hỏi mang tính từ điển kỹ thuật: số năm niên hạn, số hiệu thông tư sửa đổi phân cấp thẩm quyền).

#### 5. Có đủ cơ sở để bắt đầu RRF experiment chưa?
- **HOÀN TOÀN ĐỦ CƠ SỞ**. 
- Chúng ta đã có:
  1. Bộ dữ liệu Ground Truth V2 chuẩn hóa, minh bạch, phân loại rành mạch.
  2. Baseline Dense-only đo đạc độc lập đáng tin cậy (Hit@5 = 54.67%).
  3. Baseline Sparse FTS đo đạc độc lập không rác ngoại ngành (Hit@5 = 10.22%).
  4. Hiểu rõ nguyên nhân RRF trước đây bị sụt giảm (do trọng số Sparse bị thổi phồng lấn át Dense + ô nhiễm subqueries sinh tự động).
  5. Mục tiêu RRF mới: Lấy Dense làm nòng cốt (weight cao), dùng Sparse làm bổ trợ tinh gọn, tiến tới mục tiêu cận trên 56.89%+.

---

### VI. KẾT LUẬN & VERDICT

# **FINAL VERDICT: `READY FOR RRF EXPERIMENT` 🟢**

*(Hai tệp dữ liệu chi tiết đã được xuất đầy đủ tại `dense_225_v2_results.json` và `sparse_225_v2_results.json`)*.
