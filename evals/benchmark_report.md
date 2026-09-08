# Báo cáo Kiểm thử Định lượng: VietLegal Reasoning Benchmark

- **Thời gian chạy**: `2026-09-08 22:05:56`
- **Tổng số Test Cases**: `40`
- **Tỷ lệ Trích xuất Đúng (Retrieval Recall)**: `100.0%`
- **Tỷ lệ Test Case Đạt (Pass Rate)**: `100.0%`

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

## 2. Chi Tiết Từng Test Case

| ID | Nhóm | Tiêu đề Test Case | Retrieval | Keyword Match | Độ trễ | Kết quả |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: |
| `TC-01` | cross_document | Nghỉ việc hưởng BHXH một lần vs Trợ cấp thất nghiệp | ✅ | 83% | 9961ms | **PASSED** |
| `TC-02` | cross_document | Phân biệt Trợ cấp thôi việc (BLLĐ) và Trợ cấp thất nghiệp (Luật Việc làm) | ✅ | 100% | 9495ms | **PASSED** |
| `TC-03` | cross_document | Sa thải trái luật: Bồi thường theo BLLĐ và Mức phạt vi phạm theo NĐ 12 | ✅ | 100% | 9556ms | **PASSED** |
| `TC-04` | cross_document | Chế độ thai sản của Lao động nữ và Bảo lưu bảo hiểm | ✅ | 100% | 11759ms | **PASSED** |
| `TC-05` | boolean_logic | Điều kiện hưởng Trợ cấp thất nghiệp (AND Logic bắt buộc) | ✅ | 75% | 7110ms | **PASSED** |
| `TC-06` | boolean_logic | Điều kiện xử lý kỷ luật Sa thải (AND/OR Logic) | ✅ | 100% | 12776ms | **PASSED** |
| `TC-07` | boolean_logic | Điều kiện hưởng BHXH một lần (OR Logic giữa các trường hợp) | ✅ | 100% | 7503ms | **PASSED** |
| `TC-08` | exception_vs_general | Tuổi nghỉ hưu Nam sinh năm 1970 (Điều kiện bình thường vs Ngoại lệ) | ✅ | 100% | 13517ms | **PASSED** |
| `TC-09` | exception_vs_general | Thời gian thử việc tối đa (Quy định chung vs HĐLĐ dưới 1 tháng) | ✅ | 100% | 8649ms | **PASSED** |
| `TC-10` | exception_vs_general | Giới hạn làm thêm giờ (Mốc chung 200h vs Ngoại lệ 300h) | ✅ | 83% | 9262ms | **PASSED** |
| `TC-11` | arithmetic_calculation | Tính số tháng hưởng Trợ cấp thất nghiệp theo thâm niên 6 năm | ✅ | 100% | 9878ms | **PASSED** |
| `TC-12` | arithmetic_calculation | Tính tiền lương làm thêm giờ vào ngày nghỉ Lễ, Tết (300%) | ✅ | 100% | 5501ms | **PASSED** |
| `TC-13` | arithmetic_calculation | Tính ngày nghỉ phép năm tăng thêm theo thâm niên | ✅ | 100% | 6596ms | **PASSED** |
| `TC-14` | temporal_deadlines | Thời hạn báo trước khi đơn phương chấm dứt HĐLĐ không xác định thời hạn | ✅ | 100% | 25845ms | **PASSED** |
| `TC-15` | temporal_deadlines | Thời hiệu xử lý kỷ luật lao động (Quy định 6 tháng vs 12 tháng) | ✅ | 100% | 6357ms | **PASSED** |
| `TC-16` | tabular_lookup | Tra cứu tuổi nghỉ hưu Nữ sinh tháng 7/1972 (Phụ lục I NĐ 135) | ✅ | 100% | 14609ms | **PASSED** |
| `TC-17` | cross_document | Chấm dứt HĐLĐ vì lý do thay đổi cơ cấu: Phương án sử dụng lao động & Trợ cấp mất việc làm | ✅ | 80% | 10748ms | **PASSED** |
| `TC-18` | boolean_logic | Bảo hiểm thất nghiệp: Đơn phương chấm dứt HĐLĐ trái pháp luật | ✅ | 75% | 7770ms | **PASSED** |
| `TC-19` | arithmetic_calculation | Tính tiền trợ cấp thôi việc khi có thời gian lẻ tháng | ✅ | 80% | 18546ms | **PASSED** |
| `TC-20` | temporal_deadlines | Thời điểm bắt đầu hưởng lương hưu hàng tháng | ✅ | 75% | 14102ms | **PASSED** |
| `TC-21` | cross_document | Chậm đóng BHXH: Trách nhiệm theo BLLĐ và Mức phạt theo NĐ 12 | ✅ | 100% | 7969ms | **PASSED** |
| `TC-22` | boolean_logic | Các trường hợp tạm hoãn HĐLĐ (Điều 30 BLLĐ) | ✅ | 100% | 6291ms | **PASSED** |
| `TC-23` | exception_vs_general | Tiền lương làm việc vào ban đêm và làm thêm giờ ban đêm | ✅ | 100% | 8429ms | **PASSED** |
| `TC-24` | arithmetic_calculation | Nghĩa vụ bồi thường khi NSDLĐ đơn phương chấm dứt HĐLĐ trái pháp luật | ✅ | 75% | 8455ms | **PASSED** |
| `TC-25` | temporal_deadlines | Thời hạn thanh toán quyền lợi khi chấm dứt HĐLĐ | ✅ | 67% | 9365ms | **PASSED** |
| `TC-26` | cross_document | Hồ sơ đăng ký thay đổi người đại diện theo pháp luật của Công ty TNHH | ✅ | 80% | 9283ms | **PASSED** |
| `TC-27` | boolean_logic | Điều kiện người lao động nước ngoài làm việc tại Việt Nam | ✅ | 100% | 7049ms | **PASSED** |
| `TC-28` | tabular_lookup | Tra cứu tuổi nghỉ hưu Nam sinh tháng 3/1966 (Phụ lục I NĐ 135) | ✅ | 100% | 7721ms | **PASSED** |
| `TC-29` | arithmetic_calculation | Tiền lương ngừng việc do sự cố điện nước hoặc thiên tai | ✅ | 100% | 6036ms | **PASSED** |
| `TC-30` | cross_document | Bồi thường tai nạn lao động do lỗi của người lao động | ✅ | 50% | 6325ms | **PASSED** |
| `TC-31` | temporal_version | Rút BHXH một lần trước ngày 01/07/2025 (Áp dụng Luật BHXH 2014) | ✅ | 100% | 8456ms | **PASSED** |
| `TC-32` | temporal_version | Rút BHXH một lần từ ngày 01/07/2025 (Áp dụng Luật BHXH 2024) | ✅ | 100% | 7639ms | **PASSED** |
| `TC-33` | temporal_version | Thời gian đóng BHXH tối thiểu hưởng lương hưu 15 năm (Luật BHXH 2024) | ✅ | 100% | 10278ms | **PASSED** |
| `TC-34` | temporal_version | Quyền lợi và phạm vi điều chỉnh theo Luật BHYT sửa đổi 2024 (số 51/2024/QH15) | ✅ | 100% | 8116ms | **PASSED** |
| `TC-35` | civil_law | Đặt cọc và Xử lý tài sản đặt cọc khi vi phạm hợp đồng (Điều 328) | ✅ | 100% | 8034ms | **PASSED** |
| `TC-36` | civil_law | Mức trần lãi suất vay tài sản tối đa 20%/năm (Điều 468) | ✅ | 100% | 7002ms | **PASSED** |
| `TC-37` | civil_law | Thời hiệu khởi kiện yêu cầu bồi thường thiệt hại ngoài hợp đồng (Điều 588) | ✅ | 80% | 6162ms | **PASSED** |
| `TC-38` | civil_law | Người thừa kế không phụ thuộc vào nội dung của di chúc (Điều 644) | ✅ | 100% | 5874ms | **PASSED** |
| `TC-39` | civil_law | Điều kiện có hiệu lực của giao dịch dân sự & Hậu quả vô hiệu (Điều 117, 131) | ✅ | 83% | 8464ms | **PASSED** |
| `TC-40` | civil_law | Thời điểm mở thừa kế và thời hiệu chia di sản bất động sản 30 năm (Điều 611, 623) | ✅ | 100% | 15729ms | **PASSED** |