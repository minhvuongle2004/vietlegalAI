# BÁO CÁO KẾT QUẢ BENCHMARK GENERATION & REASONING — PHASE 4A TRAFFIC

- **Tổng số test cases**: 10
- **Test Case Pass Rate**: 10/10 (100.0%) — tất cả 10 case đều vượt ngưỡng đánh giá reasoning của benchmark
- **Retrieval Success Rate**: 10/10 (100.0%)
- **Individual Keyword Coverage**: TG-01: 75%, TG-02: 100%, TG-03: 100%, TG-04: 88%, TG-05: 100%, TG-06: 86%, TG-07: 88%, TG-08: 100%, TG-09: 83%, TG-10: 100% (Trung bình: 92.0%)
- **Forbidden / Hallucination Rate**: 0% (100% Sạch văn bản cũ và từ cấm)

## Bảng tổng hợp chi tiết 10 Test Cases

| ID | Nhóm | Tiêu đề | Retrieval | Reasoning (KW) | Forbidden | Version | Kết quả | Latency |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| `TG-01` | TRAFFIC_PENALTY | Xe máy vượt đèn đỏ: Mức phạt tiền và trừ điểm GPLX | ✅ | ✅ (75%) | ✅ Sạch | ✅ | **PASSED** ✅ | 65.04s |
| `TG-02` | TRAFFIC_PENALTY_CALCULATION | Ô tô quá tốc độ 25 km/h: Phạt tiền và trừ điểm GPLX | ✅ | ✅ (100%) | ✅ Sạch | ✅ | **PASSED** ✅ | 54.18s |
| `TG-03` | TRAFFIC_ALCOHOL | Nồng độ cồn xe máy mức 1: Quy định cấm tuyệt đối và mức phạt | ✅ | ✅ (100%) | ✅ Sạch | ✅ | **PASSED** ✅ | 143.55s |
| `TG-04` | TRAFFIC_SAFETY | Mũ bảo hiểm: Mức phạt tiền và các trường hợp ngoại lệ không phạt | ✅ | ✅ (88%) | ✅ Sạch | ✅ | **PASSED** ✅ | 201.85s |
| `TG-05` | TRAFFIC_LICENSE | Không có Giấy phép lái xe ô tô hoặc GPLX không phù hợp | ✅ | ✅ (100%) | ✅ Sạch | ✅ | **PASSED** ✅ | 42.98s |
| `TG-06` | TRAFFIC_LICENSE_POINTS | Hệ thống điểm GPLX: Tổng số điểm và nguyên tắc trừ điểm khi vi phạm nhiều lỗi | ✅ | ✅ (86%) | ✅ Sạch | ✅ | **PASSED** ✅ | 45.33s |
| `TG-07` | TRAFFIC_LICENSE_RECOVERY | Phục hồi điểm GPLX: Điều kiện tự động phục hồi và thủ tục kiểm tra kiến thức | ✅ | ✅ (88%) | ✅ Sạch | ✅ | **PASSED** ✅ | 37.24s |
| `TG-08` | TRAFFIC_CROSS_DOCUMENT | Lùi xe trên đường cao tốc: Quy tắc cấm theo Luật 36 và Chế tài phạt theo NĐ 168 | ✅ | ✅ (100%) | ✅ Sạch | ✅ | **PASSED** ✅ | 145.90s |
| `TG-09` | TRAFFIC_TEMPORAL | Hiệu lực văn bản và Thời điểm áp dụng: NĐ 168/2024 và mốc chuyển tiếp | ✅ | ✅ (83%) | ✅ Sạch | ✅ | **PASSED** ✅ | 76.47s |
| `TG-10` | TRAFFIC_COMPLEX | Hành vi phức hợp: Đi ngược chiều trên cao tốc + Nồng độ cồn và Xử lý cộng dồn điểm GPLX | ✅ | ✅ (100%) | ✅ Sạch | ✅ | **PASSED** ✅ | 103.64s |

## Đánh giá chi tiết các Case Trọng điểm (Mentor Focus)

### Case TG-04: Mũ bảo hiểm: Mức phạt tiền và các trường hợp ngoại lệ không phạt
- **Query**: Người điều khiển xe máy chở người ngồi sau không đội mũ bảo hiểm cho người đi mô tô, xe máy thì bị phạt bao nhiêu tiền và trường hợp nào chở người không đội mũ bảo hiểm thì không bị xử phạt?
- **Special Checks**: TG-04 Exception Reasoning: ✅ ĐẠT
- **Answer Excerpt**: Chào bạn, VietLegal AI xin trả lời câu hỏi của bạn về mức phạt và các trường hợp không bị xử phạt đối với hành vi chở người không đội mũ bảo hiểm như sau:

---

### 1. Mức phạt tiền đối với người điều khiển xe máy chở người không đội mũ bảo hiểm

- **Mức phạt tiền:** Phạt tiền từ **400.000 đồng đến 600.000 đồng**.
- **Căn cứ pháp lý:** Theo **Điểm i Khoản 2 Điều 7 Nghị định 168/2024/NĐ-CP**, người...

### Case TG-07: Phục hồi điểm GPLX: Điều kiện tự động phục hồi và thủ tục kiểm tra kiến thức
- **Query**: Giấy phép lái xe bị trừ điểm thì sau bao lâu được tự động phục hồi đủ 12 điểm? Nếu bị trừ hết điểm thì người có GPLX phải làm gì để được phục hồi điểm?
- **Special Checks**: TG-07 Two-branch Recovery: ✅ ĐẠT (đủ 2 nhánh)
- **Answer Excerpt**: Chào bạn,

Về việc giấy phép lái xe (GPLX) bị trừ điểm và cách phục hồi điểm, VietLegal AI xin giải đáp như sau:

---

### 1. Thời gian phục hồi tự động đủ 12 điểm

Theo quy định, GPLX của bạn sẽ được tự động phục hồi đủ 12 điểm trong trường hợp chưa bị trừ hết điểm và không bị trừ thêm điểm trong một khoảng thời gian nhất định.

Cụ thể:
*   **Thời gian phục hồi:** Giấy phép lái xe được phục hồi đ...

### Case TG-09: Hiệu lực văn bản và Thời điểm áp dụng: NĐ 168/2024 và mốc chuyển tiếp
- **Query**: Quy định xử phạt vi phạm hành chính về giao thông đường bộ tại Nghị định 168/2024/NĐ-CP có hiệu lực thi hành từ thời điểm nào? Đối với các điều khoản được sửa đổi, bổ sung bởi Nghị định 238/2026/NĐ-CP có hiệu lực từ ngày 15/08/2026 thì trường hợp hành vi vi phạm xảy ra vào tháng 03/2026 sẽ áp dụng theo văn bản nào?
- **Special Checks**: TG-09 Temporal Reasoning: ✅ ĐẠT
- **Answer Excerpt**: Chào bạn, tôi là VietLegal AI — Trợ lý Trí tuệ Nhân tạo chuyên gia tư vấn Pháp luật Việt Nam. Dựa trên các căn cứ pháp lý được cung cấp, tôi xin giải đáp chi tiết câu hỏi của bạn về hiệu lực thi hành và quy định chuyển tiếp áp dụng xử phạt vi phạm hành chính như sau:

---

### 1. Hiệu lực thi hành của Nghị định 168/2024/NĐ-CP

Căn cứ theo quy định tại **Điều 53 Nghị định 168/2024/NĐ-CP**, hiệu lực...

### Case TG-10: Hành vi phức hợp: Đi ngược chiều trên cao tốc + Nồng độ cồn và Xử lý cộng dồn điểm GPLX
- **Query**: 
- **Special Checks**: 
- **Answer Excerpt**: ...
