# Báo cáo Kiểm thử Định lượng: VietLegal Reasoning Benchmark

- **Thời gian chạy**: `2026-09-09 03:49:56`
- **Tổng số Test Cases**: `56`
- **Tỷ lệ Trích xuất Đúng (Retrieval Recall)**: **100.0%** (56/56)
- **Tỷ lệ Test Case Đạt (Pass Rate)**: **100.0%** (56/56)

## 1. Bảng Điểm theo Từng Nhóm Logic Pháp lý (Category Breakdown)

| Nhóm Nghiệp vụ / Bẫy Logic | Số câu | Đạt Retrieval | Test Case Pass | Tỷ lệ Pass |
| :--- | :---: | :---: | :---: | :---: |
| **Cross-Document Reasoning (Đa văn bản)** | 8 | 8/8 | 8/8 | **100.0%** |
| **Boolean Logic AND/OR (Điều kiện tích lũy)** | 6 | 6/6 | 6/6 | **100.0%** |
| **Ngoại lệ vs Quy định chung (Exception/General)** | 4 | 4/4 | 4/4 | **100.0%** |
| **Tính toán Số học (Calculation)** | 6 | 6/6 | 6/6 | **100.0%** |
| **Thời hạn, Thời hiệu (Temporal Deadlines)** | 4 | 4/4 | 4/4 | **100.0%** |
| **Tra cứu Bảng biểu chuyển tiếp (Tabular Lookup)** | 2 | 2/2 | 2/2 | **100.0%** |
| **Temporal / Version-Aware Legal RAG (Đa phiên bản)** | 4 | 4/4 | 4/4 | **100.0%** |
| **Dân sự, Hợp đồng & Thừa kế (Bộ luật Dân sự 2015)** | 6 | 6/6 | 6/6 | **100.0%** |
| **Thuế TNCN, TNDN & Quản lý thuế (Cụm Thuế 2025/2026)** | 8 | 8/8 | 8/8 | **100.0%** |
| **Bất động sản, Nhà ở & Đầu tư (Cụm BĐS & Đầu tư Phase 3)** | 8 | 8/8 | 8/8 | **100.0%** |

> **Kết luận**: Tất cả 10 nhóm nghiệp vụ đều đạt tỷ lệ hoàn hảo 100% (56/56 cases).

## 2. Chi Tiết Từng Test Case

| ID | Nhóm | Tiêu đề Test Case | Retrieval | Keyword Match | Độ trễ (giây) | Kết quả |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: |
| `TC-01` | cross_document | Nghỉ việc hưởng BHXH một lần vs Trợ cấp thất nghiệp | ✅ | 100% | 60.69s | **PASSED** |
| `TC-02` | cross_document | Phân biệt Trợ cấp thôi việc (BLLĐ) và Trợ cấp thất nghiệp (Luật Việc làm) | ✅ | 100% | 82.97s | **PASSED** |
| `TC-03` | cross_document | Sa thải trái luật: Bồi thường theo BLLĐ và Mức phạt vi phạm theo NĐ 12 | ✅ | 100% | 63.45s | **PASSED** |
| `TC-04` | cross_document | Chế độ thai sản của Lao động nữ và Bảo lưu bảo hiểm | ✅ | 100% | 35.47s | **PASSED** |
| `TC-05` | boolean_logic | Điều kiện hưởng Trợ cấp thất nghiệp (AND Logic bắt buộc) | ✅ | 100% | 32.37s | **PASSED** |
| `TC-06` | boolean_logic | Điều kiện xử lý kỷ luật Sa thải (AND/OR Logic) | ✅ | 100% | 71.42s | **PASSED** |
| `TC-07` | boolean_logic | Điều kiện hưởng BHXH một lần (OR Logic giữa các trường hợp) | ✅ | 100% | 33.47s | **PASSED** |
| `TC-08` | exception_vs_general | Tuổi nghỉ hưu Nam sinh năm 1970 (Điều kiện bình thường vs Ngoại lệ) | ✅ | 100% | 35.73s | **PASSED** |
| `TC-09` | exception_vs_general | Thời gian thử việc tối đa (Quy định chung vs HĐLĐ dưới 1 tháng) | ✅ | 100% | 32.77s | **PASSED** |
| `TC-10` | exception_vs_general | Giới hạn làm thêm giờ (Mốc chung 200h vs Ngoại lệ 300h) | ✅ | 83% | 66.74s | **PASSED** |
| `TC-11` | arithmetic_calculation | Tính số tháng hưởng Trợ cấp thất nghiệp theo thâm niên 6 năm | ✅ | 100% | 32.80s | **PASSED** |
| `TC-12` | arithmetic_calculation | Tính tiền lương làm thêm giờ vào ngày nghỉ Lễ, Tết (300%) | ✅ | 100% | 70.39s | **PASSED** |
| `TC-13` | arithmetic_calculation | Tính ngày nghỉ phép năm tăng thêm theo thâm niên | ✅ | 50% | 35.33s | **PASSED** |
| `TC-14` | temporal_deadlines | Thời hạn báo trước khi đơn phương chấm dứt HĐLĐ không xác định thời hạn | ✅ | 100% | 35.03s | **PASSED** |
| `TC-15` | temporal_deadlines | Thời hiệu xử lý kỷ luật lao động (Quy định 6 tháng vs 12 tháng) | ✅ | 100% | 65.68s | **PASSED** |
| `TC-16` | tabular_lookup | Tra cứu tuổi nghỉ hưu Nữ sinh tháng 7/1972 (Phụ lục I NĐ 135) | ✅ | 100% | 36.92s | **PASSED** |
| `TC-17` | cross_document | Chấm dứt HĐLĐ vì lý do thay đổi cơ cấu: Phương án sử dụng lao động & Trợ cấp mất việc làm | ✅ | 100% | 72.80s | **PASSED** |
| `TC-18` | boolean_logic | Bảo hiểm thất nghiệp: Đơn phương chấm dứt HĐLĐ trái pháp luật | ✅ | 75% | 61.71s | **PASSED** |
| `TC-19` | arithmetic_calculation | Tính tiền trợ cấp thôi việc khi có thời gian lẻ tháng | ✅ | 60% | 73.66s | **PASSED** |
| `TC-20` | temporal_deadlines | Thời điểm bắt đầu hưởng lương hưu hàng tháng | ✅ | 100% | 37.00s | **PASSED** |
| `TC-21` | cross_document | Chậm đóng BHXH: Trách nhiệm theo BLLĐ và Mức phạt theo NĐ 12 | ✅ | 100% | 38.06s | **PASSED** |
| `TC-22` | boolean_logic | Các trường hợp tạm hoãn HĐLĐ (Điều 30 BLLĐ) | ✅ | 100% | 36.61s | **PASSED** |
| `TC-23` | exception_vs_general | Tiền lương làm việc vào ban đêm và làm thêm giờ ban đêm | ✅ | 100% | 71.89s | **PASSED** |
| `TC-24` | arithmetic_calculation | Nghĩa vụ bồi thường khi NSDLĐ đơn phương chấm dứt HĐLĐ trái pháp luật | ✅ | 75% | 35.88s | **PASSED** |
| `TC-25` | temporal_deadlines | Thời hạn thanh toán quyền lợi khi chấm dứt HĐLĐ | ✅ | 100% | 35.42s | **PASSED** |
| `TC-26` | cross_document | Hồ sơ đăng ký thay đổi người đại diện theo pháp luật của Công ty TNHH | ✅ | 80% | 35.49s | **PASSED** |
| `TC-27` | boolean_logic | Điều kiện người lao động nước ngoài làm việc tại Việt Nam | ✅ | 75% | 36.02s | **PASSED** |
| `TC-28` | tabular_lookup | Tra cứu tuổi nghỉ hưu Nam sinh tháng 3/1966 (Phụ lục I NĐ 135) | ✅ | 100% | 34.78s | **PASSED** |
| `TC-29` | arithmetic_calculation | Tiền lương ngừng việc do sự cố điện nước hoặc thiên tai | ✅ | 100% | 69.77s | **PASSED** |
| `TC-30` | cross_document | Bồi thường tai nạn lao động do lỗi của người lao động | ✅ | 50% | 35.51s | **PASSED** |
| `TC-31` | temporal_version | Rút BHXH một lần trước ngày 01/07/2025 (Áp dụng Luật BHXH 2014) | ✅ | 100% | 38.01s | **PASSED** |
| `TC-32` | temporal_version | Rút BHXH một lần từ ngày 01/07/2025 (Áp dụng Luật BHXH 2024) | ✅ | 100% | 29.30s | **PASSED** |
| `TC-33` | temporal_version | Thời gian đóng BHXH tối thiểu hưởng lương hưu 15 năm (Luật BHXH 2024) | ✅ | 100% | 67.80s | **PASSED** |
| `TC-34` | temporal_version | Quyền lợi và phạm vi điều chỉnh theo Luật BHYT sửa đổi 2024 (số 51/2024/QH15) | ✅ | 100% | 12.29s | **PASSED** |
| `TC-35` | civil_law | Đặt cọc và Xử lý tài sản đặt cọc khi vi phạm hợp đồng (Điều 328) | ✅ | 100% | 36.04s | **PASSED** |
| `TC-36` | civil_law | Mức trần lãi suất vay tài sản tối đa 20%/năm (Điều 468) | ✅ | 100% | 28.46s | **PASSED** |
| `TC-37` | civil_law | Thời hiệu khởi kiện yêu cầu bồi thường thiệt hại ngoài hợp đồng (Điều 588) | ✅ | 80% | 33.75s | **PASSED** |
| `TC-38` | civil_law | Người thừa kế không phụ thuộc vào nội dung của di chúc (Điều 644) | ✅ | 100% | 23.44s | **PASSED** |
| `TC-39` | civil_law | Điều kiện có hiệu lực của giao dịch dân sự & Hậu quả vô hiệu (Điều 117, 131) | ✅ | 100% | 44.80s | **PASSED** |
| `TC-40` | civil_law | Thời điểm mở thừa kế và thời hiệu chia di sản bất động sản 30 năm (Điều 611, 623) | ✅ | 100% | 67.05s | **PASSED** |
| `TC-41` | tax_law | Biểu thuế luỹ tiến từng phần 5 bậc và tính thuế TNCN từ tiền lương (Điều 9) | ✅ | 100% | 59.38s | **PASSED** |
| `TC-42` | tax_law | Mức giảm trừ gia cảnh cho bản thân và người phụ thuộc (Điều 10) | ✅ | 100% | 66.52s | **PASSED** |
| `TC-43` | tax_law | Mức thuế suất thuế TNDN phổ thông 20% và mức ưu đãi theo doanh thu (Điều 10) | ✅ | 100% | 35.34s | **PASSED** |
| `TC-44` | tax_law | Điều kiện các khoản chi được trừ khi tính thuế TNDN (Điều 9) | ✅ | 80% | 73.39s | **PASSED** |
| `TC-45` | tax_law | Thời hạn nộp thuế và nộp hồ sơ khai thuế theo Luật Quản lý thuế 2025 (Điều 14) | ✅ | 100% | 35.17s | **PASSED** |
| `TC-46` | tax_law | Mức tính tiền chậm nộp tiền thuế 0,03%/ngày (Điều 16) | ✅ | 100% | 37.01s | **PASSED** |
| `TC-47` | tax_law | Cross-Document: Nghĩa vụ nộp thuế TNDN và Chế tài tính tiền chậm nộp thuế | ✅ | 100% | 72.31s | **PASSED** |
| `TC-48` | tax_law | Temporal Version-Aware: Đổi mới Biểu thuế 5 bậc và Giảm trừ gia cảnh Luật Thuế TNCN 2025 | ✅ | 60% | 74.08s | **PASSED** |
| `TC-49` | real_estate_law | Mức đặt cọc tối đa khi mua bán nhà ở hình thành trong tương lai (Điều 23) | ✅ | 75% | 66.83s | **PASSED** |
| `TC-50` | real_estate_law | Điều kiện bán nhà ở hình thành trong tương lai và nghiệm thu móng (Điều 24) | ✅ | 75% | 36.01s | **PASSED** |
| `TC-51` | real_estate_law | Điều kiện thực hiện các quyền chuyển nhượng quyền sử dụng đất (Điều 45) | ✅ | 100% | 36.41s | **PASSED** |
| `TC-52` | real_estate_law | Bỏ khung giá đất và nguyên tắc ban hành bảng giá đất hàng năm (Điều 158, 159) | ✅ | 100% | 65.00s | **PASSED** |
| `TC-53` | real_estate_law | Đối tượng và điều kiện hưởng chính sách nhà ở xã hội (Điều 76, 78) | ✅ | 100% | 72.00s | **PASSED** |
| `TC-54` | real_estate_law | Thời hạn tối thiểu 5 năm không được bán lại nhà ở xã hội (Điều 89) | ✅ | 75% | 36.64s | **PASSED** |
| `TC-55` | real_estate_law | Cross-Document: Đặt cọc mua bán căn hộ tương lai (Kinh doanh BĐS Đ23 vs BLDS Đ328) | ✅ | 100% | 72.12s | **PASSED** |
| `TC-56` | real_estate_law | Cross-Document: Chấp thuận chủ trương đầu tư và giao đất qua đấu giá/đấu thầu (Đầu tư Đ29, 32 vs Đất đai Đ125, 126) | ✅ | 100% | 71.24s | **PASSED** |