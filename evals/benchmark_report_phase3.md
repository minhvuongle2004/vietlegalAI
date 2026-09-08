# Báo cáo Kiểm thử Định lượng: VietLegal Reasoning Benchmark

- **Thời gian chạy**: `2026-09-09 00:58:52`
- **Tổng số Test Cases**: `56`
- **Tỷ lệ Trích xuất Đúng (Retrieval Recall)**: `94.6%`
- **Tỷ lệ Test Case Đạt (Pass Rate)**: `92.9%`

## 1. Bảng Điểm theo Từng Nhóm Logic Pháp lý (Category Breakdown)

| Nhóm Nghiệp vụ / Bẫy Logic | Số câu | Đạt Retrieval | Test Case Pass | Tỷ lệ Pass |
| :--- | :---: | :---: | :---: | :---: |
| **Cross-Document Reasoning (Đa văn bản)** | 8 | 6/8 | 6/8 | **75.0%** |
| **Boolean Logic AND/OR (Điều kiện tích lũy)** | 6 | 6/6 | 6/6 | **100.0%** |
| **Ngoại lệ vs Quy định chung (Exception/General)** | 4 | 4/4 | 4/4 | **100.0%** |
| **Tính toán Số học (Calculation)** | 6 | 6/6 | 5/6 | **83.3%** |
| **Thời hạn, Thời hiệu (Temporal Deadlines)** | 4 | 3/4 | 3/4 | **75.0%** |
| **Tra cứu Bảng biểu chuyển tiếp (Tabular Lookup)** | 2 | 2/2 | 2/2 | **100.0%** |
| **Temporal / Version-Aware Legal RAG (Đa phiên bản)** | 4 | 4/4 | 4/4 | **100.0%** |
| **Dân sự, Hợp đồng & Thừa kế (Bộ luật Dân sự 2015)** | 6 | 6/6 | 6/6 | **100.0%** |
| **Thuế TNCN, TNDN & Quản lý thuế (Cụm Thuế 2025/2026)** | 8 | 8/8 | 8/8 | **100.0%** |
| **Bất động sản, Nhà ở & Đầu tư (Cụm BĐS & Đầu tư Phase 3)** | 8 | 8/8 | 8/8 | **100.0%** |

> **Ghi chú về nhóm Calculation**: Đạt 5/6 (83.3%), cải thiện 1 case so với baseline trước Phase 2 (từ 4/6 lên 5/6).

## 2. Chi Tiết Từng Test Case

| ID | Nhóm | Tiêu đề Test Case | Retrieval | Keyword Match | Độ trễ | Kết quả |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: |
| `TC-01` | cross_document | Nghỉ việc hưởng BHXH một lần vs Trợ cấp thất nghiệp | ✅ | 100% | 24778ms | **PASSED** |
| `TC-02` | cross_document | Phân biệt Trợ cấp thôi việc (BLLĐ) và Trợ cấp thất nghiệp (Luật Việc làm) | ❌ | 40% | 21963ms | **FAILED** |
| `TC-03` | cross_document | Sa thải trái luật: Bồi thường theo BLLĐ và Mức phạt vi phạm theo NĐ 12 | ✅ | 100% | 16716ms | **PASSED** |
| `TC-04` | cross_document | Chế độ thai sản của Lao động nữ và Bảo lưu bảo hiểm | ✅ | 100% | 15045ms | **PASSED** |
| `TC-05` | boolean_logic | Điều kiện hưởng Trợ cấp thất nghiệp (AND Logic bắt buộc) | ✅ | 75% | 15139ms | **PASSED** |
| `TC-06` | boolean_logic | Điều kiện xử lý kỷ luật Sa thải (AND/OR Logic) | ✅ | 100% | 22012ms | **PASSED** |
| `TC-07` | boolean_logic | Điều kiện hưởng BHXH một lần (OR Logic giữa các trường hợp) | ✅ | 100% | 15511ms | **PASSED** |
| `TC-08` | exception_vs_general | Tuổi nghỉ hưu Nam sinh năm 1970 (Điều kiện bình thường vs Ngoại lệ) | ✅ | 100% | 15824ms | **PASSED** |
| `TC-09` | exception_vs_general | Thời gian thử việc tối đa (Quy định chung vs HĐLĐ dưới 1 tháng) | ✅ | 100% | 18451ms | **PASSED** |
| `TC-10` | exception_vs_general | Giới hạn làm thêm giờ (Mốc chung 200h vs Ngoại lệ 300h) | ✅ | 83% | 29507ms | **PASSED** |
| `TC-11` | arithmetic_calculation | Tính số tháng hưởng Trợ cấp thất nghiệp theo thâm niên 6 năm | ✅ | 100% | 15126ms | **PASSED** |
| `TC-12` | arithmetic_calculation | Tính tiền lương làm thêm giờ vào ngày nghỉ Lễ, Tết (300%) | ✅ | 100% | 25248ms | **PASSED** |
| `TC-13` | arithmetic_calculation | Tính ngày nghỉ phép năm tăng thêm theo thâm niên | ✅ | 75% | 22875ms | **PASSED** |
| `TC-14` | temporal_deadlines | Thời hạn báo trước khi đơn phương chấm dứt HĐLĐ không xác định thời hạn | ✅ | 100% | 18401ms | **PASSED** |
| `TC-15` | temporal_deadlines | Thời hiệu xử lý kỷ luật lao động (Quy định 6 tháng vs 12 tháng) | ✅ | 100% | 23085ms | **PASSED** |
| `TC-16` | tabular_lookup | Tra cứu tuổi nghỉ hưu Nữ sinh tháng 7/1972 (Phụ lục I NĐ 135) | ✅ | 100% | 14328ms | **PASSED** |
| `TC-17` | cross_document | Chấm dứt HĐLĐ vì lý do thay đổi cơ cấu: Phương án sử dụng lao động & Trợ cấp mất việc làm | ❌ | 80% | 22727ms | *PARTIAL* |
| `TC-18` | boolean_logic | Bảo hiểm thất nghiệp: Đơn phương chấm dứt HĐLĐ trái pháp luật | ✅ | 75% | 21238ms | **PASSED** |
| `TC-19` | arithmetic_calculation | Tính tiền trợ cấp thôi việc khi có thời gian lẻ tháng | ✅ | 20% | 16292ms | *PARTIAL* |
| `TC-20` | temporal_deadlines | Thời điểm bắt đầu hưởng lương hưu hàng tháng | ❌ | 100% | 14585ms | *PARTIAL* |
| `TC-21` | cross_document | Chậm đóng BHXH: Trách nhiệm theo BLLĐ và Mức phạt theo NĐ 12 | ✅ | 60% | 16755ms | **PASSED** |
| `TC-22` | boolean_logic | Các trường hợp tạm hoãn HĐLĐ (Điều 30 BLLĐ) | ✅ | 100% | 16409ms | **PASSED** |
| `TC-23` | exception_vs_general | Tiền lương làm việc vào ban đêm và làm thêm giờ ban đêm | ✅ | 100% | 23164ms | **PASSED** |
| `TC-24` | arithmetic_calculation | Nghĩa vụ bồi thường khi NSDLĐ đơn phương chấm dứt HĐLĐ trái pháp luật | ✅ | 75% | 15395ms | **PASSED** |
| `TC-25` | temporal_deadlines | Thời hạn thanh toán quyền lợi khi chấm dứt HĐLĐ | ✅ | 100% | 15530ms | **PASSED** |
| `TC-26` | cross_document | Hồ sơ đăng ký thay đổi người đại diện theo pháp luật của Công ty TNHH | ✅ | 60% | 15544ms | **PASSED** |
| `TC-27` | boolean_logic | Điều kiện người lao động nước ngoài làm việc tại Việt Nam | ✅ | 75% | 16179ms | **PASSED** |
| `TC-28` | tabular_lookup | Tra cứu tuổi nghỉ hưu Nam sinh tháng 3/1966 (Phụ lục I NĐ 135) | ✅ | 100% | 14809ms | **PASSED** |
| `TC-29` | arithmetic_calculation | Tiền lương ngừng việc do sự cố điện nước hoặc thiên tai | ✅ | 100% | 21098ms | **PASSED** |
| `TC-30` | cross_document | Bồi thường tai nạn lao động do lỗi của người lao động | ✅ | 50% | 14879ms | **PASSED** |
| `TC-31` | temporal_version | Rút BHXH một lần trước ngày 01/07/2025 (Áp dụng Luật BHXH 2014) | ✅ | 100% | 15921ms | **PASSED** |
| `TC-32` | temporal_version | Rút BHXH một lần từ ngày 01/07/2025 (Áp dụng Luật BHXH 2024) | ✅ | 100% | 13592ms | **PASSED** |
| `TC-33` | temporal_version | Thời gian đóng BHXH tối thiểu hưởng lương hưu 15 năm (Luật BHXH 2024) | ✅ | 100% | 20885ms | **PASSED** |
| `TC-34` | temporal_version | Quyền lợi và phạm vi điều chỉnh theo Luật BHYT sửa đổi 2024 (số 51/2024/QH15) | ✅ | 100% | 7662ms | **PASSED** |
| `TC-35` | civil_law | Đặt cọc và Xử lý tài sản đặt cọc khi vi phạm hợp đồng (Điều 328) | ✅ | 100% | 16216ms | **PASSED** |
| `TC-36` | civil_law | Mức trần lãi suất vay tài sản tối đa 20%/năm (Điều 468) | ✅ | 100% | 13215ms | **PASSED** |
| `TC-37` | civil_law | Thời hiệu khởi kiện yêu cầu bồi thường thiệt hại ngoài hợp đồng (Điều 588) | ✅ | 80% | 13631ms | **PASSED** |
| `TC-38` | civil_law | Người thừa kế không phụ thuộc vào nội dung của di chúc (Điều 644) | ✅ | 80% | 10951ms | **PASSED** |
| `TC-39` | civil_law | Điều kiện có hiệu lực của giao dịch dân sự & Hậu quả vô hiệu (Điều 117, 131) | ✅ | 100% | 14184ms | **PASSED** |
| `TC-40` | civil_law | Thời điểm mở thừa kế và thời hiệu chia di sản bất động sản 30 năm (Điều 611, 623) | ✅ | 100% | 19752ms | **PASSED** |
| `TC-41` | tax_law | Biểu thuế luỹ tiến từng phần 5 bậc và tính thuế TNCN từ tiền lương (Điều 9) | ✅ | 100% | 19788ms | **PASSED** |
| `TC-42` | tax_law | Mức giảm trừ gia cảnh cho bản thân và người phụ thuộc (Điều 10) | ✅ | 100% | 19609ms | **PASSED** |
| `TC-43` | tax_law | Mức thuế suất thuế TNDN phổ thông 20% và mức ưu đãi theo doanh thu (Điều 10) | ✅ | 100% | 15187ms | **PASSED** |
| `TC-44` | tax_law | Điều kiện các khoản chi được trừ khi tính thuế TNDN (Điều 9) | ✅ | 80% | 20835ms | **PASSED** |
| `TC-45` | tax_law | Thời hạn nộp thuế và nộp hồ sơ khai thuế theo Luật Quản lý thuế 2025 (Điều 14) | ✅ | 100% | 14412ms | **PASSED** |
| `TC-46` | tax_law | Mức tính tiền chậm nộp tiền thuế 0,03%/ngày (Điều 16) | ✅ | 60% | 17731ms | **PASSED** |
| `TC-47` | tax_law | Cross-Document: Nghĩa vụ nộp thuế TNDN và Chế tài tính tiền chậm nộp thuế | ✅ | 100% | 22660ms | **PASSED** |
| `TC-48` | tax_law | Temporal Version-Aware: Đổi mới Biểu thuế 5 bậc và Giảm trừ gia cảnh Luật Thuế TNCN 2025 | ✅ | 80% | 20099ms | **PASSED** |
| `TC-49` | real_estate_law | Mức đặt cọc tối đa khi mua bán nhà ở hình thành trong tương lai (Điều 23) | ✅ | 100% | 19786ms | **PASSED** |
| `TC-50` | real_estate_law | Điều kiện bán nhà ở hình thành trong tương lai và nghiệm thu móng (Điều 24) | ✅ | 75% | 16360ms | **PASSED** |
| `TC-51` | real_estate_law | Điều kiện thực hiện các quyền chuyển nhượng quyền sử dụng đất (Điều 45) | ✅ | 100% | 16200ms | **PASSED** |
| `TC-52` | real_estate_law | Bỏ khung giá đất và nguyên tắc ban hành bảng giá đất hàng năm (Điều 158, 159) | ✅ | 100% | 25091ms | **PASSED** |
| `TC-53` | real_estate_law | Đối tượng và điều kiện hưởng chính sách nhà ở xã hội (Điều 76, 78) | ✅ | 100% | 24905ms | **PASSED** |
| `TC-54` | real_estate_law | Thời hạn tối thiểu 5 năm không được bán lại nhà ở xã hội (Điều 89) | ✅ | 75% | 17691ms | **PASSED** |
| `TC-55` | real_estate_law | Cross-Document: Đặt cọc mua bán căn hộ tương lai (Kinh doanh BĐS Đ23 vs BLDS Đ328) | ✅ | 100% | 24384ms | **PASSED** |
| `TC-56` | real_estate_law | Cross-Document: Chấp thuận chủ trương đầu tư và giao đất qua đấu giá/đấu thầu (Đầu tư Đ29, 32 vs Đất đai Đ125, 126) | ✅ | 100% | 26817ms | **PASSED** |