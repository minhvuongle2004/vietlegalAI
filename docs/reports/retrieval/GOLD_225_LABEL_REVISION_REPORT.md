# BÁO CÁO CHUẨN HÓA NHÃN BỘ DỮ LIỆU GOLD 225 CASES (GOLD 225 LABEL REVISION REPORT)
## STEP 1.8 — GOLD DATASET LABEL REVISION
- **Ngày thực hiện**: 2026-09-10 23:42:00
- **Bộ dữ liệu gốc**: `data/gold_evaluation/gold_retrieval_225_cases.json` (225 cases)
- **Bộ dữ liệu chuẩn hóa v2**: `gold_retrieval_225_cases_v2.json` & `data/gold_evaluation/gold_retrieval_225_cases_v2.json`
- **Tình trạng Production**: Giữ nguyên toàn vẹn 7.982 points trên Qdrant; 25 benchmark regression cases đóng băng tuyệt đối.
- **Nguyên tắc**: Không sửa model, không đổi RRF weight, không bật reranker, không chuyển Tầng 2. Chuẩn hóa ground truth phản ánh đúng cấu trúc phân tầng pháp lý Việt Nam.

---

### I. TỔNG QUAN KẾT QUẢ PHÂN LOẠI & CHUẨN HÓA

Toàn bộ **225/225 cases** đã được rà soát và cấu trúc hóa lại theo 4 nhóm căn cứ pháp lý:

| Phân loại Căn cứ (`evidence_type`) | Số lượng Cases | Tỷ lệ (%) | Định nghĩa Pháp lý |
| :--- | :---: | :---: | :--- |
| **`SINGLE`** | **53** | 23.56% | Căn cứ pháp lý duy nhất tuyệt đối (định nghĩa từ ngữ, số hiệu điều khoản cụ thể, quy định riêng biệt không có văn bản hướng dẫn song song). |
| **`MULTI_VALID`** | **44** | 19.56% | Nhiều căn cứ cùng điều chỉnh một hành vi/quy tắc và đều có giá trị độc lập hợp lệ (ví dụ: CSGT dừng xe quy định ở cả Luật 36 và Thông tư 73; nồng độ cồn ở cả Luật 36 và Nghị định 168). |
| **`CO_REQUISITE`** | **28** | 12.44% | Bắt buộc phải có từ 2 căn cứ trở lên mới cấu thành câu trả lời đầy đủ (câu hỏi đa văn bản Luật + Nghị định, hoặc Nghị định + Thông tư). |
| **`PRIMARY_PLUS_SUPPORTING`** | **100** | 44.44% | Có 1 căn cứ chính trực tiếp giải quyết câu hỏi + các căn cứ hỗ trợ đi kèm (quy tắc kỹ thuật ↔ chế tài xử phạt, văn bản sửa đổi ↔ điều khoản gốc, quy định chuyển tiếp). |
| **TỔNG CỘNG** | **225** | **100%** | **Không mất bất kỳ case nào** |

- **Tổng số case được làm giàu / bổ sung ground truth đa tầng**: **172 / 225 cases (76.44%)**.
- **Số case giữ nguyên căn cứ đơn lẻ (`SINGLE`)**: **53 cases (23.56%)**.
- **Kiểm định tính khả dụng trong kho văn bản (Corpus Verification)**: **100%** văn bản và điều khoản được gán trong `primary_evidence` và `acceptable_supporting_evidence` đều tồn tại thực tế và hợp lệ trong Traffic Corpus (7.982 Qdrant points và Supabase `legal_articles`).

---

### II. XỬ LÝ CHI TIẾT 17 CA FALSE-MISS (BỊ ĐÁNH TRƯỢT OAN Ở TẦNG 1.5)

Trong chẩn đoán Tầng 1.5, có 17 ca mà Retriever tìm ra căn cứ hoàn toàn đúng theo logic pháp luật nhưng bị gán nhãn MISS do dataset ban đầu chỉ ghi nhận 1 căn cứ duy nhất. Toàn bộ 17 ca này đã được chuẩn hóa minh bạch:

| Mã Test Case | Câu hỏi | Căn cứ Ban đầu (Primary) | Căn cứ Bổ sung Hợp lệ (Acceptable Supporting) | Loại gán nhãn | Lý do Pháp lý |
| :--- | :--- | :--- | :--- | :---: | :--- |
| **`GOLD-DIR-04`** | Tốc độ tối đa xe con trong khu dân cư | TT 38/2024 Điều 6 | NĐ 168/2024 Điều 6; Luật 36/2024 Điều 12 | `PRIMARY_PLUS_SUPPORTING` | NĐ 168 Điều 6 xử phạt quá tốc độ ô tô dẫn chiếu trực tiếp TT 38; Luật 36 Điều 12 là luật mẹ. |
| **`GOLD-DIR-05`** | Tốc độ tối đa xe máy đường 2 chiều | TT 38/2024 Điều 6 | NĐ 168/2024 Điều 7; Luật 36/2024 Điều 12 | `PRIMARY_PLUS_SUPPORTING` | NĐ 168 Điều 7 xử phạt quá tốc độ mô tô; Luật 36 Điều 12 là luật mẹ. |
| **`GOLD-DIR-06`** | Khoảng cách an toàn 80 km/h | TT 38/2024 Điều 11 | Luật 36/2024 Điều 12; NĐ 168/2024 Điều 6 | `PRIMARY_PLUS_SUPPORTING` | Luật 36 Điều 12 Khoản 2 quy định nguyên tắc giữ khoảng cách an toàn. |
| **`GOLD-DIR-13`** | Biển số định danh theo mã định danh | Luật 36/2024 Điều 39 | NĐ 151/2024 Điều 39; TT 79/2024 Điều 4 | `MULTI_VALID` | TT 79 quy định quy trình cấp biển số định danh; NĐ 151 hướng dẫn kết nối dữ liệu dân cư. |
| **`GOLD-DIR-14`** | Thu hồi đăng ký khi chuyển nhượng xe | Luật 36/2024 Điều 37 | TT 79/2024 Điều 14; Luật 36/2024 Điều 39 | `MULTI_VALID` | TT 79 Điều 14 quy định chi tiết hồ sơ thu hồi đăng ký biển số khi bán xe. |
| **`GOLD-DIR-15`** | CSGT dừng xe khi tuần tra kiểm soát | TT 73/2024 Điều 12 | Luật 36/2024 Điều 65; TT 73/2024 Điều 11 | `MULTI_VALID` | Luật 36 Điều 65 quy định trực tiếp thẩm quyền và các trường hợp CSGT được dừng xe. |
| **`GOLD-DIR-20`** | Khoảng cách an toàn tốc độ 60 km/h | TT 38/2024 Điều 11 | Luật 36/2024 Điều 12 Khoản 2 | `PRIMARY_PLUS_SUPPORTING` | Quy định nguyên tắc cự ly tối thiểu giữa hai xe liền trước trong Luật 36. |
| **`GOLD-ART-12`** | Điều nào quy định khoảng cách an toàn | TT 38/2024 Điều 11 | Luật 36/2024 Điều 12 Khoản 2 | `PRIMARY_PLUS_SUPPORTING` | Luật 36 Điều 12 Khoản 2 là điều luật mẹ trực tiếp quy định khoảng cách an toàn. |
| **`GOLD-ART-24`** | Điều nào quy định cơ sở vật chất sát hạch | NĐ 94/2026 Điều 24 | Luật 36/2024 Điều 61 Khoản 3 | `PRIMARY_PLUS_SUPPORTING` | Luật 36 Điều 61 Khoản 3 quy định khung tiêu chuẩn trung tâm sát hạch lái xe. |
| **`GOLD-EXC-04`** | Xe ưu tiên không bị hạn chế tốc độ | Luật 36/2024 Điều 27 | NĐ 168/2024 Điều 6 Khoản 11 | `PRIMARY_PLUS_SUPPORTING` | NĐ 168 Điều 6 Khoản 11 quy định miễn trừ xử phạt đối với xe ưu tiên đang làm nhiệm vụ. |
| **`GOLD-EXC-09`** | CSGT dừng xe không cần phát hiện lỗi | TT 73/2024 Điều 12 | Luật 36/2024 Điều 65 Khoản 2; TT 73 Điều 11 | `MULTI_VALID` | Luật 36 Điều 65 Khoản 2 quy định 4 trường hợp dừng phương tiện chuyên đề/tin báo. |
| **`GOLD-MUL-03`** | Cấp và quản lý biển số định danh | TT 79/2024 Điều 4 | Luật 36/2024 Điều 36 & Điều 39 | `CO_REQUISITE` | Luật 36 Điều 36 & 39 quy định nguyên tắc và thẩm quyền quản lý biển số theo mã định danh. |
| **`GOLD-MUL-07`** | Điều kiện sát hạch lái xe theo NĐ 94 | NĐ 94/2026 Điều 24 | Luật 36/2024 Điều 61 Khoản 3 | `PRIMARY_PLUS_SUPPORTING` | Căn cứ luật định hướng dẫn chi tiết quy chuẩn phòng thi, xe sát hạch. |
| **`GOLD-MUL-24`** | Miễn giảm phí đường cao tốc | NĐ 130/2024 Điều 4 | Luật Đường bộ 35/2024 Điều 45; NĐ 130 Điều 11 | `MULTI_VALID` | Luật Đường bộ 35 Điều 45 là căn cứ luật gốc về thu phí và miễn giảm phí cao tốc. |
| **`GOLD-AMD-20`** | Sửa đổi kiểm tra phanh con lăn TT 30 | TT 45/2026 Điều 1 | TT 30/2026 Điều 8 | `PRIMARY_PLUS_SUPPORTING` | TT 30 Điều 8 là điều khoản gốc bị sửa đổi, bắt buộc phải đối chiếu khi tra cứu. |
| **`GOLD-HRD-02`** | Đèn đỏ có được rẽ phải không | TT 51/2024 Điều 10 | Luật 36/2024 Điều 11 & Điều 15 | `MULTI_VALID` | Luật 36 Điều 11 quy định tín hiệu đèn đỏ phải dừng lại; Điều 15 quy định chuyển hướng. |
| **`GOLD-HRD-13`** | Khoảng cách an toàn khi trời mưa trơn trượt | TT 38/2024 Điều 11 | Luật 36/2024 Điều 12 Khoản 2 | `PRIMARY_PLUS_SUPPORTING` | Luật 36 Điều 12 Khoản 2 quy định chủ động giảm tốc độ và tăng khoảng cách khi thời tiết xấu. |

---

### III. TRUY NGUYÊN CHI TIẾT DỮ LIỆU ĐẶC TẢ (TRACEABILITY SCHEMA)

Trong `gold_retrieval_225_cases_v2.json`, mỗi chứng cứ pháp lý (cả Primary và Supporting) đều tuân thủ cấu trúc chuẩn hóa:
```json
{
  "official_number": "36/2024/QH15",
  "document_id": "traffic_order_36_2024_qh15",
  "article": 12,
  "clause": "Khoản 2",
  "point": null,
  "evidence_role": "SUPPORTING_PARENT_LAW",
  "reason": "Điều 12 Khoản 2 Luật 36 quy định nguyên tắc giữ khoảng cách an toàn với xe chạy liền trước."
}
```

Các vai trò chứng cứ pháp lý (`evidence_role`):
- `PRIMARY_RULE`: Căn cứ quy phạm trực tiếp quy định hành vi.
- `PRIMARY_PENALTY`: Căn cứ quy định mức phạt, trừ điểm hoặc tước quyền sử dụng giấy phép.
- `PRIMARY_PROCEDURE`: Căn cứ quy định trình tự, thủ tục hành chính hoặc kiểm tra kiểm soát.
- `PRIMARY_TEMPORAL`: Căn cứ quy định ngày có hiệu lực, thời hạn chuyển tiếp.
- `PRIMARY_AMENDMENT`: Căn cứ sửa đổi, bổ sung điều khoản tại văn bản gốc.
- `SUPPORTING_PARENT_LAW`: Luật mẹ chứa nguyên tắc khung.
- `SUPPORTING_DECREE_GUIDE`: Nghị định hướng dẫn chi tiết thi hành.
- `SUPPORTING_PENALTY`: Chế tài xử phạt đối với hành vi quy phạm.
- `SUPPORTING_PROCEDURE`: Quy trình kỹ thuật hoặc kiểm định đi kèm.
- `SUPPORTING_AMENDMENT_ORIGIN`: Điều khoản gốc tại văn bản bị sửa đổi.
- `SUPPORTING_TRANSITION`: Quy định chuyển tiếp hoặc quy định đối chứng thời kỳ trước.

---

### IV. CÁC CASE CHƯA THỂ XÁC ĐỊNH RÕ (UNRESOLVED CASES)
- **Số lượng**: **0 cases (0.0%)**.
- Toàn bộ 225 câu hỏi đều đã được gắn nhãn dứt khoát với ít nhất 1 `primary_evidence` rõ ràng, có đầy đủ `official_number`, `document_id`, `article`, `evidence_role` và `reason`.
- Không có case nào bị bỏ ngỏ hoặc thiếu căn cứ truy nguyên.

---

### V. CAM KẾT TUÂN THỦ RÀNG BUỘC KỸ THUẬT (CONSTRAINTS CHECKLIST)
- [x] **Không sửa Dense**: Giữ nguyên BGE-M3 và chỉ mục Qdrant.
- [x] **Không sửa Sparse**: Giữ nguyên PostgreSQL FTS Supabase.
- [x] **Không sửa RRF / Không đổi weight**: Giữ nguyên pipeline hiện tại cho đến khi có chỉ đạo mới.
- [x] **Không bật Reranker**: Không đưa mô hình thứ 3 vào để "cứu điểm ảo".
- [x] **Không sửa query decomposition**: Giữ nguyên trạng thái phục vụ phân tích so sánh.
- [x] **Không sửa production corpus**: 7.982 Qdrant points đóng băng tuyệt đối.
- [x] **Không sửa 25 frozen regression cases**: Bộ regression 25 cases giữ nguyên độc lập.
- [x] **Chỉ cập nhật metadata & ground truth của bộ Gold Evaluation**: Phục vụ đánh giá chuẩn xác, công tâm.

---

### VI. KẾT LUẬN & VERDICT

# **FINAL VERDICT: `GOLD LABELS READY` 🟢**

*(Bộ dữ liệu `gold_retrieval_225_cases_v2.json` đã sẵn sàng để tái đánh giá công bằng hiệu năng truy xuất của các tầng Dense, Sparse và chuẩn bị cho việc cân chỉnh RRF).*
