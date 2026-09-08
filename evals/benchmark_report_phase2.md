# Báo cáo Kiểm thử Định lượng: VietLegal Reasoning Benchmark

- **Thời gian chạy**: `2026-09-08 23:27:18`
- **Tổng số Test Cases**: `48`
- **Tỷ lệ Trích xuất Đúng (Retrieval Recall)**: `100.0%`
- **Tỷ lệ Test Case Đạt (Pass Rate)**: `97.9%`

## 1. Bảng Điểm theo Từng Nhóm Logic Pháp lý (Category Breakdown)

| Nhóm Nghiệp vụ / Bẫy Logic | Số câu | Đạt Retrieval | Test Case Pass | Tỷ lệ Pass |
| :--- | :---: | :---: | :---: | :---: |
| **Cross-Document Reasoning (Đa văn bản)** | 8 | 8/8 | 8/8 | **100.0%** |
| **Boolean Logic AND/OR (Điều kiện tích lũy)** | 6 | 6/6 | 6/6 | **100.0%** |
| **Ngoại lệ vs Quy định chung (Exception/General)** | 4 | 4/4 | 4/4 | **100.0%** |
| **Tính toán Số học (Calculation)** | 6 | 6/6 | 5/6 | **83.3%** |
| **Thời hạn, Thời hiệu (Temporal Deadlines)** | 4 | 4/4 | 4/4 | **100.0%** |
| **Tra cứu Bảng biểu chuyển tiếp (Tabular Lookup)** | 2 | 2/2 | 2/2 | **100.0%** |
| **Temporal / Version-Aware Legal RAG (Đa phiên bản)** | 4 | 4/4 | 4/4 | **100.0%** |
| **Dân sự, Hợp đồng & Thừa kế (Bộ luật Dân sự 2015)** | 6 | 6/6 | 6/6 | **100.0%** |
| **Thuế TNCN, TNDN & Quản lý thuế (Cụm Thuế 2025/2026)** | 8 | 8/8 | 8/8 | **100.0%** |

> **Ghi chú về nhóm Calculation**: Đạt 5/6 (83.3%), cải thiện 1 case so với baseline trước Phase 2 (từ 4/6 lên 5/6).

## 2. Chi Tiết Từng Test Case

| ID | Nhóm | Tiêu đề Test Case | Retrieval | Keyword Match | Độ trễ | Kết quả |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: |
| `TC-01` | cross_document | Nghỉ việc hưởng BHXH một lần vs Trợ cấp thất nghiệp | ✅ | 100% | 38759ms | **PASSED** |
| `TC-02` | cross_document | Phân biệt Trợ cấp thôi việc (BLLĐ) và Trợ cấp thất nghiệp (Luật Việc làm) | ✅ | 100% | 30201ms | **PASSED** |
| `TC-03` | cross_document | Sa thải trái luật: Bồi thường theo BLLĐ và Mức phạt vi phạm theo NĐ 12 | ✅ | 100% | 27224ms | **PASSED** |
| `TC-04` | cross_document | Chế độ thai sản của Lao động nữ và Bảo lưu bảo hiểm | ✅ | 100% | 21864ms | **PASSED** |
| `TC-05` | boolean_logic | Điều kiện hưởng Trợ cấp thất nghiệp (AND Logic bắt buộc) | ✅ | 100% | 18992ms | **PASSED** |
| `TC-06` | boolean_logic | Điều kiện xử lý kỷ luật Sa thải (AND/OR Logic) | ✅ | 100% | 31315ms | **PASSED** |
| `TC-07` | boolean_logic | Điều kiện hưởng BHXH một lần (OR Logic giữa các trường hợp) | ✅ | 100% | 26711ms | **PASSED** |
| `TC-08` | exception_vs_general | Tuổi nghỉ hưu Nam sinh năm 1970 (Điều kiện bình thường vs Ngoại lệ) | ✅ | 100% | 19371ms | **PASSED** |
| `TC-09` | exception_vs_general | Thời gian thử việc tối đa (Quy định chung vs HĐLĐ dưới 1 tháng) | ✅ | 100% | 21098ms | **PASSED** |
| `TC-10` | exception_vs_general | Giới hạn làm thêm giờ (Mốc chung 200h vs Ngoại lệ 300h) | ✅ | 83% | 26589ms | **PASSED** |
| `TC-11` | arithmetic_calculation | Tính số tháng hưởng Trợ cấp thất nghiệp theo thâm niên 6 năm | ✅ | 100% | 22744ms | **PASSED** |
| `TC-12` | arithmetic_calculation | Tính tiền lương làm thêm giờ vào ngày nghỉ Lễ, Tết (300%) | ✅ | 100% | 12045ms | **PASSED** |
| `TC-13` | arithmetic_calculation | Tính ngày nghỉ phép năm tăng thêm theo thâm niên | ✅ | 100% | 9640ms | **PASSED** |
| `TC-14` | temporal_deadlines | Thời hạn báo trước khi đơn phương chấm dứt HĐLĐ không xác định thời hạn | ✅ | 100% | 9475ms | **PASSED** |
| `TC-15` | temporal_deadlines | Thời hiệu xử lý kỷ luật lao động (Quy định 6 tháng vs 12 tháng) | ✅ | 100% | 17211ms | **PASSED** |
| `TC-16` | tabular_lookup | Tra cứu tuổi nghỉ hưu Nữ sinh tháng 7/1972 (Phụ lục I NĐ 135) | ✅ | 100% | 11733ms | **PASSED** |
| `TC-17` | cross_document | Chấm dứt HĐLĐ vì lý do thay đổi cơ cấu: Phương án sử dụng lao động & Trợ cấp mất việc làm | ✅ | 100% | 13699ms | **PASSED** |
| `TC-18` | boolean_logic | Bảo hiểm thất nghiệp: Đơn phương chấm dứt HĐLĐ trái pháp luật | ✅ | 75% | 10826ms | **PASSED** |
| `TC-19` | arithmetic_calculation | Tính tiền trợ cấp thôi việc khi có thời gian lẻ tháng | ✅ | 20% | 9617ms | *PARTIAL* |
| `TC-20` | temporal_deadlines | Thời điểm bắt đầu hưởng lương hưu hàng tháng | ✅ | 100% | 19869ms | **PASSED** |
| `TC-21` | cross_document | Chậm đóng BHXH: Trách nhiệm theo BLLĐ và Mức phạt theo NĐ 12 | ✅ | 100% | 10927ms | **PASSED** |
| `TC-22` | boolean_logic | Các trường hợp tạm hoãn HĐLĐ (Điều 30 BLLĐ) | ✅ | 100% | 26563ms | **PASSED** |
| `TC-23` | exception_vs_general | Tiền lương làm việc vào ban đêm và làm thêm giờ ban đêm | ✅ | 100% | 12776ms | **PASSED** |
| `TC-24` | arithmetic_calculation | Nghĩa vụ bồi thường khi NSDLĐ đơn phương chấm dứt HĐLĐ trái pháp luật | ✅ | 75% | 10797ms | **PASSED** |
| `TC-25` | temporal_deadlines | Thời hạn thanh toán quyền lợi khi chấm dứt HĐLĐ | ✅ | 100% | 9706ms | **PASSED** |
| `TC-26` | cross_document | Hồ sơ đăng ký thay đổi người đại diện theo pháp luật của Công ty TNHH | ✅ | 80% | 12436ms | **PASSED** |
| `TC-27` | boolean_logic | Điều kiện người lao động nước ngoài làm việc tại Việt Nam | ✅ | 75% | 11204ms | **PASSED** |
| `TC-28` | tabular_lookup | Tra cứu tuổi nghỉ hưu Nam sinh tháng 3/1966 (Phụ lục I NĐ 135) | ✅ | 100% | 11259ms | **PASSED** |
| `TC-29` | arithmetic_calculation | Tiền lương ngừng việc do sự cố điện nước hoặc thiên tai | ✅ | 100% | 21243ms | **PASSED** |
| `TC-30` | cross_document | Bồi thường tai nạn lao động do lỗi của người lao động | ✅ | 50% | 8718ms | **PASSED** |
| `TC-31` | temporal_version | Rút BHXH một lần trước ngày 01/07/2025 (Áp dụng Luật BHXH 2014) | ✅ | 100% | 11991ms | **PASSED** |
| `TC-32` | temporal_version | Rút BHXH một lần từ ngày 01/07/2025 (Áp dụng Luật BHXH 2024) | ✅ | 100% | 9861ms | **PASSED** |
| `TC-33` | temporal_version | Thời gian đóng BHXH tối thiểu hưởng lương hưu 15 năm (Luật BHXH 2024) | ✅ | 100% | 11781ms | **PASSED** |
| `TC-34` | temporal_version | Quyền lợi và phạm vi điều chỉnh theo Luật BHYT sửa đổi 2024 (số 51/2024/QH15) | ✅ | 100% | 9868ms | **PASSED** |
| `TC-35` | civil_law | Đặt cọc và Xử lý tài sản đặt cọc khi vi phạm hợp đồng (Điều 328) | ✅ | 100% | 9126ms | **PASSED** |
| `TC-36` | civil_law | Mức trần lãi suất vay tài sản tối đa 20%/năm (Điều 468) | ✅ | 100% | 8988ms | **PASSED** |
| `TC-37` | civil_law | Thời hiệu khởi kiện yêu cầu bồi thường thiệt hại ngoài hợp đồng (Điều 588) | ✅ | 80% | 8382ms | **PASSED** |
| `TC-38` | civil_law | Người thừa kế không phụ thuộc vào nội dung của di chúc (Điều 644) | ✅ | 80% | 9043ms | **PASSED** |
| `TC-39` | civil_law | Điều kiện có hiệu lực của giao dịch dân sự & Hậu quả vô hiệu (Điều 117, 131) | ✅ | 100% | 10009ms | **PASSED** |
| `TC-40` | civil_law | Thời điểm mở thừa kế và thời hiệu chia di sản bất động sản 30 năm (Điều 611, 623) | ✅ | 100% | 9603ms | **PASSED** |
| `TC-41` | tax_law | Biểu thuế luỹ tiến từng phần 5 bậc và tính thuế TNCN từ tiền lương (Điều 9) | ✅ | 100% | 12248ms | **PASSED** |
| `TC-42` | tax_law | Mức giảm trừ gia cảnh cho bản thân và người phụ thuộc (Điều 10) | ✅ | 100% | 10190ms | **PASSED** |
| `TC-43` | tax_law | Mức thuế suất thuế TNDN phổ thông 20% và mức ưu đãi theo doanh thu (Điều 10) | ✅ | 100% | 8923ms | **PASSED** |
| `TC-44` | tax_law | Điều kiện các khoản chi được trừ khi tính thuế TNDN (Điều 9) | ✅ | 100% | 13585ms | **PASSED** |
| `TC-45` | tax_law | Thời hạn nộp thuế và nộp hồ sơ khai thuế theo Luật Quản lý thuế 2025 (Điều 14) | ✅ | 100% | 11694ms | **PASSED** |
| `TC-46` | tax_law | Mức tính tiền chậm nộp tiền thuế 0,03%/ngày (Điều 16) | ✅ | 100% | 10451ms | **PASSED** |
| `TC-47` | tax_law | Cross-Document: Nghĩa vụ nộp thuế TNDN và Chế tài tính tiền chậm nộp thuế | ✅ | 100% | 12178ms | **PASSED** |
| `TC-48` | tax_law | Temporal Version-Aware: Đổi mới Biểu thuế 5 bậc và Giảm trừ gia cảnh Luật Thuế TNCN 2025 | ✅ | 100% | 14754ms | **PASSED** |