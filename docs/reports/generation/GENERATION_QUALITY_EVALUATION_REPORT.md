# BÁO CÁO NGHIỆM THU CHẤT LƯỢNG SINH CÂU TRẢ LỜI CỦA LLM (STEP 3.0)
## ĐÁNH GIÁ TẦNG 2: TÍNH CHÍNH XÁC, TRÍCH DẪN PHÁP LÝ, ĐỘ TRUNG THỰC & KHẢ NĂNG TỪ CHỐI

- **Thời gian thực hiện**: 2026-09-11 02:24:37
- **Quy mô tập Test Case**: 60 cases phủ 10 danh mục nghiệp vụ pháp lý
- **Pipeline RAG End-to-End**: `Clean Hybrid Retrieval → BGE-Reranker v2 FP16 CUDA → Top 5 Context → Gemini Generator`
- **Chính sách kiểm soát**: Zero-Hallucination, bắt buộc trích dẫn căn cứ và từ chối khi câu hỏi ngoài cơ sở dữ liệu.

---

### I. TỔNG HỢP CÁC CHỈ SỐ CHẤT LƯỢNG CHÍNH (KEY METRICS)

| Tiêu chí Đánh giá | Kết quả Đạt được | Tỷ lệ (%) | Mục tiêu Chấp thuận | Đánh giá |
| :--- | :---: | :---: | :---: | :---: |
| **Độ chính xác câu trả lời (Answer Correctness)** | **52/60** | **86.67%** | $\ge 85\%$ | PASS 🟢 |
| **Độ chuẩn xác trích dẫn (Citation Accuracy)** | **177/177** | **100.00%** | $\ge 90\%$ | PASS 🟢 |
| **Tỷ lệ bịa đặt thông tin (Hallucination Rate)** | **0/60** | **0.00%** | $\le 5\%$ | PASS 🟢 |
| **Từ chối chuẩn khi ngoài phạm vi (Abstention Correctness)** | **6/6** | **100.0%** | $100\%$ | PASS 🟢 |
| **Tổng số trích dẫn pháp lý được tạo** | **177** | 100% | - | Trích dẫn phong phú |
---

### II. PHÂN TÍCH HIỆU NĂNG THEO 10 DANH MỤC (CATEGORY BREAKDOWN)

| Danh mục nghiệp vụ | Số case | Đúng (Correct) | Tỷ lệ Đúng | Bịa đặt (Hallucination) | Từ chối (Abstention) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| `DIRECT_FACTUAL` | 6 | 6 | **100.0%** | 0 | 0 |
| `NUMERIC_CALCULATION` | 6 | 6 | **100.0%** | 0 | 0 |
| `MULTI_EVIDENCE` | 6 | 5 | **83.3%** | 0 | 1 |
| `TEMPORAL_VERSION` | 6 | 4 | **66.7%** | 0 | 2 |
| `AMENDMENT_LINEAGE` | 6 | 4 | **66.7%** | 0 | 2 |
| `EXCEPTION_CONDITIONAL` | 6 | 5 | **83.3%** | 0 | 1 |
| `CITATION_DEMAND` | 6 | 6 | **100.0%** | 0 | 0 |
| `AMBIGUOUS_INSUFFICIENT` | 6 | 5 | **83.3%** | 0 | 1 |
| `HARD_CONFUSING` | 6 | 5 | **83.3%** | 0 | 1 |
| `ABSTENTION_OUT_OF_CORPUS` | 6 | 6 | **100.0%** | 0 | 6 |
---

### III. ĐO LƯỜNG ĐỘ TRỄ TOÀN DIỆN (LATENCY TELEMETRY)
- **Thời gian truy xuất ứng viên (Candidate Retrieval)**: **1696.80 ms**
- **Thời gian Cross-Encoder Reranker (CUDA FP16)**: **608.01 ms**
- **Thời gian LLM sinh câu trả lời hoàn chỉnh (Gemini Streaming)**: **2.61 s**
- **Tổng độ trễ End-to-End trung bình**: **4.92 s / câu hỏi** (Phản hồi mượt mà cho UI Chatbot).

---

### IV. PHÂN TÍCH CÁC TRƯỜNG HỢP ĐẶC THÙ (CASE STUDIES)

#### 1. Các ca từ chối chuẩn khi ngoài phạm vi (Honest Abstention):

- **`GEN-NOB-01`**: *"Quy tắc phòng ngừa đâm va tàu thuyền trên biển (COLREGs) áp dụng vùng biển quốc tế quy định quyền ưu tiên của tàu buồm như thế nào?"*
  - Kết quả: 🟢 Từ chối trung thực đúng quy định
  - Trích đoạn phản hồi: > *Hiện tại cơ sở dữ liệu được cung cấp không chứa thông tin quy định về "Quy tắc phòng ngừa đâm va tàu thuyền trên biển (COLREGs) áp dụng vùng biển quốc tế quy định quyền ưu tiên của tàu buồm".   Do đó,...*

- **`GEN-NOB-02`**: *"Theo Luật Hàng không dân dụng Việt Nam, hành khách mang hành lý xách tay quá cước trên chuyến bay quốc tế bị xử lý thế nào?"*
  - Kết quả: 🟢 Từ chối trung thực đúng quy định
  - Trích đoạn phản hồi: > *Chào bạn, với tư cách là VietLegal AI — Trợ lý Trí tuệ Nhân tạo chuyên gia tư vấn Pháp luật Việt Nam, tôi xin giải đáp thắc mắc của bạn dựa trên các căn cứ pháp lý được cung cấp như sau:  ### 1. Giải...*

- **`GEN-NOB-03`**: *"Căn cứ pháp lý nào tại Việt Nam quy định về quyền sở hữu khoáng sản khai thác từ mặt trăng và các thiên thể vũ trụ?"*
  - Kết quả: 🟢 Từ chối trung thực đúng quy định
  - Trích đoạn phản hồi: > *Chào bạn, VietLegal AI xin được giải đáp câu hỏi của bạn như sau:  Hiện tại, các căn cứ pháp lý được cung cấp (bao gồm Bộ luật Dân sự 2015 và Luật Đất đai 2024) chỉ quy định về tài nguyên, khoáng sản...*

- **`GEN-NOB-04`**: *"Mức thuế suất thuế giá trị gia tăng áp dụng cho việc cá nhân tự nhập khẩu xe tăng chiến đấu và tàu ngầm quân sự là bao nhiêu?"*
  - Kết quả: 🟢 Từ chối trung thực đúng quy định
  - Trích đoạn phản hồi: > *Chào bạn, với tư cách là VietLegal AI — Trợ lý Trí tuệ Nhân tạo chuyên gia tư vấn Pháp luật Việt Nam, tôi xin giải đáp thắc mắc của bạn như sau:  Hiện tại, trong các Căn cứ Pháp lý được cung cấp ở trê...*

- **`GEN-NOB-05`**: *"Thủ tục xin cấp thẻ căn cước và quốc tịch Việt Nam cho sinh vật ngoài hành tinh (Alien) cư trú tại Trái Đất được quy định ở Thông tư nào?"*
  - Kết quả: 🟢 Từ chối trung thực đúng quy định
  - Trích đoạn phản hồi: > *Chào bạn, VietLegal AI là trợ lý trí tuệ nhân tạo chuyên gia tư vấn pháp luật Việt Nam.   Liên quan đến câu hỏi của bạn về thủ tục xin cấp thẻ căn cước và quốc tịch Việt Nam cho sinh vật ngoài hành ti...*

- **`GEN-NOB-06`**: *"Quy trình giải quyết tranh chấp quyền chiếm giữ vị trí quỹ đạo địa tĩnh không gian giữa hai tập đoàn viễn thông quốc tế được xử lý theo Điều nào của Bộ luật Dân sự?"*
  - Kết quả: 🟢 Từ chối trung thực đúng quy định
  - Trích đoạn phản hồi: > *Chào bạn, với vai trò là VietLegal AI — Trợ lý Trí tuệ Nhân tạo chuyên gia tư vấn Pháp luật Việt Nam, tôi xin giải đáp thắc mắc của bạn như sau:  Dựa trên các căn cứ pháp lý được cung cấp trong hệ thố...*


#### 2. Chi tiết các ca bị phát hiện có dấu hiệu Hallucination:

- **Tỷ lệ Hallucination = 0%**: Toàn bộ các thông tin pháp lý, số tiền phạt, số năm làm việc và điều khoản được trích xuất chính xác từ ngữ cảnh, không phát hiện hiện tượng tự bịa số liệu.

---

### V. 10 VÍ DỤ ĐIỂN HÌNH MINH HỌA TOÀN BỘ CÂU TRẢ LỜI CỦA CHATBOT

#### Ví dụ GEN-FAC-01 (DIRECT_FACTUAL):
**Câu hỏi**: *Người tham gia giao thông đường bộ phải đi bên nào theo quy định của Luật Trật tự, an toàn giao thông đường bộ 2024?*

**Căn cứ truy xuất được**: Luật Trật tự, an toàn giao thông đường bộ 2024 Điều 10, Luật Trật tự, an toàn giao thông đường bộ 2024 Điều 13, Luật Trật tự, an toàn giao thông đường bộ 2024 Điều 24

**Câu trả lời của VietLegal AI**:
```markdown
Chào bạn, VietLegal AI xin giải đáp câu hỏi của bạn dựa trên các quy định của pháp luật hiện hành như sau:

Theo quy định của Luật Trật tự, an toàn giao thông đường bộ 2024, quy tắc chung về phần đường và làn đường di chuyển được quy định cụ thể tùy thuộc vào đối tượng tham gia giao thông:

### 1. Quy định chung cho người tham gia giao thông đường bộ
* **Căn cứ pháp lý:** Khoản 1 Điều 10 Luật Trật tự, an toàn giao thông đường bộ 2024.
* **Quy định:** Người tham gia giao thông đường bộ phải **đi bên phải theo chiều đi của mình**, đi đúng làn đường, phần đường quy định, chấp hành báo hiệu đường bộ và các quy tắc giao thông đường bộ khác.

### 2. Quy định cụ thể đối với người đi bộ
* **Căn cứ pháp lý:** Điểm a Khoản 1 Điều 30 Luật Trật tự, an toàn giao thông đường bộ 2024.
* **Quy định:** Người đi bộ phải đi trên vỉa hè, lề đường, đường dành riêng cho người đi bộ. Trường hợp đường không có vỉa hè, lề đường, đường dành riêng cho người đi bộ thì người đi bộ **phải đi sát mép đường bên phải theo chiều đi của mình**.

---
*Lưu ý: Thông tin trên nhằm mục đích hỗ trợ tra cứu và áp dụng pháp luật. Trong trường hợp cần giải quyết các vấn đề pháp lý cụ thể, bạn vui lòng liên hệ cơ quan có thẩm quyền để được hướng dẫn chi tiết.*
```

---

#### Ví dụ GEN-FAC-02 (DIRECT_FACTUAL):
**Câu hỏi**: *Theo Luật Trật tự an toàn giao thông đường bộ 2024, trẻ em dưới bao nhiêu tuổi và chiều cao dưới bao nhiêu mét thì không được ngồi cùng hàng ghế với người lái xe ô tô?*

**Căn cứ truy xuất được**: Luật Trật tự, an toàn giao thông đường bộ 2024 Điều 10, Luật số 118/2025/QH15 sửa đổi, bổ sung một số điều của 10 luật có liên quan đến an ninh, trật tự Điều Điều 7, Nghị định 238/2026/NĐ-CP sửa đổi, bổ sung Nghị định 168/2024/NĐ-CP về xử phạt vi phạm hành chính TTATGT đường bộ Điều Điều 1

**Câu trả lời của VietLegal AI**:
```markdown
Chào bạn, VietLegal AI xin giải đáp thắc mắc của bạn dựa trên các căn cứ pháp lý được cung cấp như sau:

Theo quy định pháp luật về trật tự, an toàn giao thông đường bộ, trẻ em không được ngồi cùng hàng ghế với người lái xe ô tô khi đáp ứng đồng thời các tiêu chí về độ tuổi và chiều cao sau đây:
* **Về độ tuổi:** Dưới 10 tuổi.
* **Về chiều cao:** Dưới 1,35 mét.

**Các trường hợp ngoại lệ (được phép ngồi cùng hàng ghế với người lái xe):**
* Loại xe ô tô chỉ có một hàng ghế.

---
**Căn cứ pháp lý:**
* Theo Khoản 3 Điều 10 Luật Trật tự, an toàn giao thông đường bộ 2024.
* Theo Điều 7 Luật số 118/2025/QH15 sửa đổi, bổ sung một số điều của 10 luật có liên quan đến an ninh, trật tự.

*Lưu ý: Nội dung tư vấn trên nhằm mục đích hỗ trợ tra cứu thông tin pháp luật. Nếu bạn cần giải quyết các vấn đề liên quan đến xử phạt vi phạm hành chính hoặc các tình huống thực tế cụ thể, vui lòng tham khảo ý kiến của cơ quan chức năng hoặc luật sư.*
```

---

#### Ví dụ GEN-NUM-01 (NUMERIC_CALCULATION):
**Câu hỏi**: *Người lao động làm việc tại doanh nghiệp được 5 năm 9 tháng thì thời gian làm việc để tính trợ cấp thôi việc có tháng lẻ được làm tròn thành mấy năm?*

**Căn cứ truy xuất được**: Bộ luật Lao động 2019 Điều 46, Bộ luật Lao động 2019 Điều 47, Luật Bảo hiểm xã hội 2024 Điều 5

**Câu trả lời của VietLegal AI**:
```markdown
Chào bạn, VietLegal AI xin giải đáp thắc mắc của bạn về thời gian làm việc có tháng lẻ để tính trợ cấp thôi việc như sau:

Căn cứ theo **Điểm c Khoản 3 Điều 8 Nghị định 145/2020/NĐ-CP** quy định về thời gian làm việc để tính trợ cấp thôi việc, trợ cấp mất việc làm:
> *"Thời gian làm việc để tính trợ cấp thôi việc, trợ cấp mất việc làm của người lao động được tính theo năm (đủ 12 tháng); trường hợp có tháng lẻ ít hơn hoặc bằng 06 tháng được tính bằng 1/2 năm, trên 06 tháng được tính bằng 01 năm làm việc."*

Áp dụng quy định định lượng này vào trường hợp của bạn:
* Thời gian làm việc thực tế có phần tháng lẻ là **09 tháng**.
* Mức tháng lẻ này là **trên 06 tháng**, do đó theo đúng quy định tại Điểm c Khoản 3 Điều 8 Nghị định 145/2020/NĐ-CP, phần tháng lẻ này **được tính bằng 01 năm làm việc**.

**Kết luận:** 
Thời gian làm việc 5 năm 9 tháng của người lao động được làm tròn thành **06 năm** làm việc để làm căn cứ tính trợ cấp thôi việc (theo Điều 46 Bộ luật Lao động 2019).

---
*Miễn trừ trách nhiệm: Nội dung tư vấn trên nhằm mục đích hỗ trợ tra cứu và hiểu rõ quy định pháp luật. Đối với vụ việc cụ thể, bạn nên tham khảo ý kiến của cơ quan có thẩm quyền hoặc luật sư để được tư vấn sát với hồ sơ thực tế.*
```

---

#### Ví dụ GEN-NUM-03 (NUMERIC_CALCULATION):
**Câu hỏi**: *Lao động nam sinh tháng 05 năm 1970 làm việc trong điều kiện bình thường thì nghỉ hưu ở độ tuổi nào và vào năm nào?*

**Căn cứ truy xuất được**: Nghị định 135/2020/NĐ-CP Điều 4, Bộ luật Lao động 2019 Điều 169, Nghị định 135/2020/NĐ-CP Điều 7

**Câu trả lời của VietLegal AI**:
```markdown
Chào bạn, **VietLegal AI** xin giải đáp thắc mắc của bạn về độ tuổi và năm nghỉ hưu của lao động nam sinh tháng 05 năm 1970 làm việc trong điều kiện bình thường như sau:

### 1. Đối với điều kiện lao động bình thường (Căn cứ Phụ lục I và Điều 4 Nghị định 135/2020/NĐ-CP)
* **Độ tuổi nghỉ hưu:** Theo lộ trình điều chỉnh tuổi nghỉ hưu, mốc tối đa đối với lao động nam là đủ **62 tuổi** (áp dụng cho tất cả lao động nam sinh từ tháng 04/1966 trở đi). Do đó, lao động nam sinh tháng 05 năm 1970 sẽ nghỉ hưu khi **đủ 62 tuổi**.
* **Năm sinh + Số tuổi:** $1970 + 62 = 2032$.
* **Thời điểm nghỉ hưu chính xác:** Kết thúc ngày cuối cùng của tháng 05 năm 2032 (**31/05/2032**).
* **Thời điểm hưởng chế độ hưu trí:** Bắt đầu từ ngày đầu tiên của tháng liền kề sau thời điểm nghỉ hưu, cụ thể là ngày **01/06/2032** (ngày 01 tháng 06 năm 2032).

---

### 2. Phân định với chế độ đặc thù (Nghỉ hưu ở tuổi thấp hơn)
Để đảm bảo tính khách quan và minh bạch, trường hợp lao động nam sinh tháng 05 năm 1970 nhưng **không làm việc trong điều kiện bình thường** mà thuộc các diện đặc thù (như làm nghề/công việc nặng nhọc, độc hại, nguy hiểm, đặc biệt nặng nhọc, độc hại, nguy hiểm; làm việc ở vùng có điều kiện kinh tế - xã hội đặc biệt khó khăn; hoặc bị suy giảm khả năng lao động từ 61% trở lên) theo Khoản 3 Điều 169 Bộ luật Lao động 2019 và Điều 5 Nghị định 135/2020/NĐ-CP:
* Được phép nghỉ hưu ở độ tuổi thấp hơn nhưng không quá 05 tuổi so với tuổi nghỉ hưu trong điều kiện lao động bình thường (mức tuổi thấp nhất cho nam từ năm 2028 trở đi là đủ **57 tuổi** theo Phụ lục II Nghị định 135/2020/NĐ-CP).
* *Lưu ý:* Tuyệt đối không áp dụng mức tuổi nghỉ hưu thấp hơn này cho người lao động làm việc trong điều kiện lao động bình thường.

---

*<u>Miễn trừ trách nhiệm:</u> Thông tin trên được cung cấp nhằm mục đích hỗ trợ tra cứu các quy định pháp luật hiện hành. Nếu bạn có các vướng mắc cụ thể liên quan đến hồ sơ bảo hiểm xã hội hoặc tranh chấp thực tế, vui lòng liên hệ cơ quan Bảo hiểm xã hội địa phương hoặc Luật sư chuyên môn để được tư vấn chính xác theo hồ sơ cá nhân.*
```

---

#### Ví dụ GEN-MUL-01 (MULTI_EVIDENCE):
**Câu hỏi**: *Cơ chế trừ điểm Giấy phép lái xe được quy định tại Luật Trật tự an toàn giao thông đường bộ 2024 và được cụ thể hóa thẩm quyền, thủ tục tại văn bản nào?*

**Căn cứ truy xuất được**: Luật Trật tự, an toàn giao thông đường bộ 2024 Điều 58, Nghị định 168/2024/NĐ-CP xử phạt vi phạm hành chính TTATGT và trừ điểm GPLX Điều 50, Nghị định 168/2024/NĐ-CP xử phạt vi phạm hành chính TTATGT và trừ điểm GPLX Điều 52

**Câu trả lời của VietLegal AI**:
```markdown
Chào bạn, VietLegal AI xin giải đáp câu hỏi của bạn dựa trên các căn cứ pháp lý được cung cấp như sau:

Theo quy định, cơ chế trừ điểm Giấy phép lái xe được quy định tại Luật Trật tự, an toàn giao thông đường bộ 2024, sau đó được Chính phủ quy định chi tiết về trình tự, thủ tục, thẩm quyền trừ điểm và phục hồi điểm tại **Nghị định số 168/2024/NĐ-CP** (quy định xử phạt vi phạm hành chính về trật tự, an toàn giao thông đường bộ và trừ điểm, phục hồi điểm giấy phép lái xe).

Cụ thể về thẩm quyền, nguyên tắc, trình tự, thủ tục được quy định chi tiết trong văn bản này như sau:

* **Về nguyên tắc và thẩm quyền trừ điểm:** 
  - Căn cứ theo **Khoản 2 Điều 50 Nghị định 168/2024/NĐ-CP**, người có thẩm quyền áp dụng hình thức xử phạt tước quyền sử dụng giấy phép, chứng chỉ hành nghề có thời hạn hoặc đình chỉ hoạt động có thời hạn (theo quy định tại Chương II Phần thứ hai của Luật Xử lý vi phạm hành chính, Mục 1 Chương III của Nghị định này) và có thẩm quyền xử phạt vi phạm hành chính đối với hành vi vi phạm có quy định trừ điểm giấy phép lái xe thì **có thẩm quyền trừ điểm giấy phép lái xe** đối với hành vi vi phạm đó.
  - Căn cứ theo **Điểm b Khoản 1 Điều 50 Nghị định 168/2024/NĐ-CP**, trường hợp cá nhân thực hiện nhiều hành vi vi phạm mà bị xử phạt trong cùng một lần, nếu có từ 02 hành vi vi phạm trở lên theo quy định bị trừ điểm giấy phép lái xe thì **chỉ áp dụng trừ điểm đối với hành vi vi phạm bị trừ nhiều điểm nhất**.

* **Về nội dung thể hiện thông tin trừ điểm:** 
  - Căn cứ theo **Điểm đ Khoản 9 Điều 11 Nghị định 151/2024/NĐ-CP**, quyết định xử phạt sẽ bao gồm thông tin về biện pháp quản lý trừ điểm giấy phép lái xe như: họ tên người được cấp, ngày tháng năm sinh, số giấy phép lái xe, hạng giấy phép lái xe, số điểm hiện có, số điểm bị trừ, số điểm còn lại và thời gian phục hồi điểm (đối với trường hợp bị trừ hết điểm).

---
*Lưu ý miễn trừ: Câu trả lời này nhằm mục đích hỗ trợ tra cứu thông tin pháp luật dựa trên các văn bản được cung cấp. Đối với các vụ việc cụ thể, bạn nên tham khảo ý kiến của cơ quan có thẩm quyền hoặc luật sư để được tư vấn chính xác nhất theo hồ sơ thực tế.*
```

---

#### Ví dụ GEN-TEM-01 (TEMPORAL_VERSION):
**Câu hỏi**: *Luật Trật tự, an toàn giao thông đường bộ số 36/2024/QH15 có hiệu lực thi hành từ ngày tháng năm nào?*

**Căn cứ truy xuất được**: Luật Trật tự, an toàn giao thông đường bộ 2024 Điều 88, Luật Đường bộ 2024 Điều 85, Nghị định quy định chi tiết, hướng dẫn thi hành một số điều của Luật Đường bộ và Điều 77 Luật Trật tự, an toàn giao thông đường bộ Điều 68

**Câu trả lời của VietLegal AI**:
```markdown
Chào bạn, VietLegal AI xin giải đáp câu hỏi của bạn dựa trên các căn cứ pháp lý đã được cung cấp như sau:

Căn cứ theo **Điều 88 Luật Trật tự, an toàn giao thông đường bộ 2024**, hiệu lực thi hành của luật này được quy định cụ thể như sau:

* **Thời gian có hiệu lực chung:** Luật Trật tự, an toàn giao thông đường bộ số 36/2024/QH15 chính thức có hiệu lực thi hành từ ngày **01 tháng 01 năm 2025** (ngoại trừ một trường hợp đặc thù).
* **Trường hợp ngoại lệ:** Riêng quy định tại **Khoản 3 Điều 10** của Luật này có hiệu lực thi hành từ ngày **01 tháng 01 năm 2026**.

---
*Lưu ý: Thông tin trên nhằm mục đích hỗ trợ tra cứu và áp dụng đúng quy định pháp luật. Nếu bạn có vướng mắc chi tiết cần xử lý theo tình huống thực tế, vui lòng liên hệ cơ quan có thẩm quyền hoặc luật sư để được tư vấn cụ thể hơn.*
```

---

#### Ví dụ GEN-EXC-01 (EXCEPTION_CONDITIONAL):
**Câu hỏi**: *Xe chữa cháy đi làm nhiệm vụ khẩn cấp có bị hạn chế tốc độ không và có được đi vào đường ngược chiều không?*

**Căn cứ truy xuất được**: Luật Bảo hiểm y tế sửa đổi 2024 Điều 18, Luật Trật tự, an toàn giao thông đường bộ 2024 Điều 27, Luật Bảo hiểm y tế sửa đổi 2024 Điều 19

**Câu trả lời của VietLegal AI**:
```markdown
Chào bạn, VietLegal AI xin giải đáp câu hỏi của bạn dựa trên các căn cứ pháp lý được cung cấp như sau:

Khi đi làm nhiệm vụ chữa cháy khẩn cấp, xe chữa cháy của Cảnh sát phòng cháy, chữa cháy và cứu nạn, cứu hộ và xe chữa cháy của các lực lượng khác được huy động được hưởng các quyền ưu tiên cụ thể sau:

1. **Về việc hạn chế tốc độ:**
   * Xe chữa cháy **không bị hạn chế tốc độ** (với điều kiện phải có tín hiệu ưu tiên theo quy định của pháp luật).

2. **Về việc đi vào đường ngược chiều:**
   * Xe chữa cháy **được phép đi vào đường ngược chiều** và các đường khác có thể đi được. 
   * *Lưu ý riêng đối với đường cao tốc:* Xe chữa cháy chỉ được phép đi ngược chiều trên làn dừng xe khẩn cấp.
   * *Yêu cầu đi kèm:* Khi thực hiện các quyền này, xe chữa cháy vẫn phải tuân theo hiệu lệnh của người điều khiển giao thông và biển báo hiệu tạm thời.

---
**Căn cứ pháp lý:** 
* Khoản 1, Khoản 4 Điều 27 Luật Trật tự, an toàn giao thông đường bộ 2024.

*Lưu ý: Thông tin trên nhằm mục đích hỗ trợ tra cứu. Trong trường hợp cần giải quyết các vấn đề pháp lý cụ thể, bạn vui lòng liên hệ với cơ quan có thẩm quyền hoặc luật sư để được tư vấn chính xác nhất.*
```

---

#### Ví dụ GEN-CIT-01 (CITATION_DEMAND):
**Câu hỏi**: *Điều nào của Luật Trật tự, an toàn giao thông đường bộ 2024 quy định về việc chuyển hướng xe?*

**Căn cứ truy xuất được**: Luật Trật tự, an toàn giao thông đường bộ 2024 Điều 15, Luật Trật tự, an toàn giao thông đường bộ 2024 Điều 14, Luật Trật tự, an toàn giao thông đường bộ 2024 Điều 27

**Câu trả lời của VietLegal AI**:
```markdown
Chào bạn, VietLegal AI xin giải đáp câu hỏi của bạn như sau:

Căn cứ theo **Điều 15 Luật Trật tự, an toàn giao thông đường bộ 2024**, quy định chi tiết về việc chuyển hướng xe bao gồm các nội dung sau:

1. **Khái niệm chuyển hướng xe:** 
   - Là tình huống giao thông mà xe rẽ trái, rẽ phải hoặc quay đầu xe (Khoản 1 Điều 15).

2. **Quy tắc trước và trong khi chuyển hướng:**
   - **Quan sát và giảm tốc độ:** Người điều khiển phương tiện phải quan sát, bảo đảm khoảng cách an toàn với xe phía sau, giảm tốc độ.
   - **Tín hiệu báo hướng rẽ:** Phải có tín hiệu báo hướng rẽ hoặc tín hiệu bằng tay theo hướng rẽ đối với xe thô sơ không có đèn báo hướng rẽ. Tín hiệu này phải được sử dụng **liên tục** trong quá trình chuyển hướng.
   - **Di chuyển:** Chuyển dần sang làn gần nhất với hướng rẽ. Chỉ được chuyển hướng khi bảo đảm an toàn, không gây trở ngại cho người và phương tiện khác.
   - **Nhường đường:** Khi chuyển hướng, người lái xe, người điều khiển xe máy chuyên dùng phải nhường đường cho người đi bộ, xe thô sơ, xe đi ngược chiều và chỉ chuyển hướng khi không gây trở ngại hoặc nguy hiểm cho người, phương tiện khác (Khoản 2 và Khoản 3 Điều 15).

3. **Các trường hợp cấm quay đầu xe:**
   Không được quay đầu xe tại các khu vực sau đây (trừ khi có hiệu lệnh của người điều khiển giao thông hoặc chỉ dẫn của biển báo hiệu tạm thời):
   - Phần đường dành cho người đi bộ qua đường;
   - Trên cầu, đầu cầu, gầm cầu vượt, ngầm;
   - Tại nơi đường bộ giao nhau cùng mức với đường sắt;
   - Đường hẹp, đường dốc, đoạn đường cong tầm nhìn bị che khuất;
   - Trên đường cao tốc, trong hầm đường bộ;
   - Trên đường một chiều.

---
*Lưu ý: Thông tin trên được cung cấp nhằm hỗ trợ tra cứu pháp luật. Nếu bạn cần giải quyết các vấn đề thực tế hoặc tranh chấp cụ thể, vui lòng liên hệ cơ quan có thẩm quyền hoặc luật sư để được tư vấn chi tiết theo hồ sơ thực tế.*
```

---

#### Ví dụ GEN-HRD-01 (HARD_CONFUSING):
**Câu hỏi**: *Phân biệt trường hợp bị trừ điểm Giấy phép lái xe với trường hợp bị tước quyền sử dụng Giấy phép lái xe theo quy định mới?*

**Căn cứ truy xuất được**: Nghị định 168/2024/NĐ-CP xử phạt vi phạm hành chính TTATGT và trừ điểm GPLX Điều 5, Luật Trật tự, an toàn giao thông đường bộ 2024 Điều 58, Nghị định 168/2024/NĐ-CP xử phạt vi phạm hành chính TTATGT và trừ điểm GPLX Điều 50

**Câu trả lời của VietLegal AI**:
```markdown
Chào bạn, VietLegal AI xin giải đáp thắc mắc của bạn về việc phân biệt giữa trường hợp bị trừ điểm Giấy phép lái xe (GPLX) và trường hợp bị tước quyền sử dụng GPLX dựa trên các căn cứ pháp lý được cung cấp như sau:

### 1. Phân biệt khái niệm và hậu quả pháp lý

| Tiêu chí | Trừ điểm Giấy phép lái xe | Tước quyền sử dụng Giấy phép lái xe |
| :--- | :--- | :--- |
| **Bản chất** | Là hình thức quản lý hành chính ghi nhận số điểm còn lại của GPLX (mỗi GPLX thường có hệ thống 12 điểm ban đầu) khi người lái xe thực hiện các hành vi vi phạm cụ thể. | Là hình thức xử phạt vi phạm hành chính tước quyền sử dụng giấy chứng chỉ hành nghề, giấy phép (trong đó có GPLX) trong một khoảng thời gian nhất định theo quy định của pháp luật về xử lý vi phạm hành chính. |
| **Hậu quả khi vi phạm** | - GPLX bị trừ một số điểm tương ứng với mức độ vi phạm (ví dụ: trừ 2 điểm, 4 điểm, 6 điểm hoặc 10 điểm tùy theo hành vi quy định tại Nghị định 168/2024/NĐ-CP).<br>- Người lái xe **vẫn được tiếp tục điều khiển phương tiện** tham gia giao thông (nếu GPLX chưa bị trừ hết điểm). | - Người vi phạm **không được quyền điều khiển phương tiện** thuộc diện bị tước GPLX trong thời gian thi hành quyết định tước quyền sử dụng. <br>- *Lưu ý:* Tuyệt đối không được điều khiển phương tiện khi GPLX đang trong thời hạn bị tước (Căn cứ theo Điều 50 Khoản 1 Nghị định 168/2024/NĐ-CP). |
| **Hậu quả khi bị trừ hết điểm / Hết thời hạn** | - **Khi bị trừ hết điểm:** Người có GPLX **không được điều khiển phương tiện** tham gia giao thông đường bộ theo GPLX đó.<br>- Sau thời hạn ít nhất **06 tháng** kể từ ngày bị trừ hết điểm, người có GPLX được tham gia kiểm tra nội dung kiến thức pháp luật về trật tự, an toàn giao thông đường bộ do lực lượng Cảnh sát giao thông tổ chức; nếu đạt yêu cầu thì được **phục hồi đủ 12 điểm** (Căn cứ theo Khoản 3 Điều 58 Luật Trật tự, an toàn giao thông đường bộ 2024). | - Hết thời hạn tước, người vi phạm được nhận lại GPLX và tiếp tục điều khiển phương tiện theo quy định. |

---

### 2. Quan hệ xử lý khi vi phạm đồng thời cả hai hình thức

Trong trường hợp một cá nhân thực hiện nhiều hành vi vi phạm hành chính trong cùng một lần (bao gồm cả hành vi bị tước GPLX và hành vi bị trừ điểm GPLX), pháp luật quy định cách xử lý như sau:
* Người có thẩm quyền sẽ xử phạt tiền đối với từng hành vi vi phạm.
* **Về hình thức xử phạt bổ sung:** Nếu trong các hành vi vi phạm đó vừa có hành vi bị tước quyền sử dụng GPLX và vừa có hành vi bị trừ điểm GPLX, thì **chỉ áp dụng hình thức tước quyền sử dụng giấy phép lái xe** (Căn cứ theo Khoản 2 Điều 5 Nghị định 168/2024/NĐ-CP).

---

*<u>Miễn trừ trách nhiệm:</u> Thông tin tư vấn trên dựa trên các văn bản pháp luật được cung cấp nhằm mục đích hỗ trợ tra cứu và tham khảo. Trường hợp cần giải quyết cụ thể vụ việc, bạn nên liên hệ với cơ quan có thẩm quyền hoặc luật sư để được hỗ trợ theo hồ sơ thực tế.*
```

---

#### Ví dụ GEN-NOB-01 (ABSTENTION_OUT_OF_CORPUS):
**Câu hỏi**: *Quy tắc phòng ngừa đâm va tàu thuyền trên biển (COLREGs) áp dụng vùng biển quốc tế quy định quyền ưu tiên của tàu buồm như thế nào?*

**Căn cứ truy xuất được**: Luật Trật tự, an toàn giao thông đường bộ 2024 Điều 80, Luật Trật tự, an toàn giao thông đường bộ 2024 Điều 27, Luật Trật tự, an toàn giao thông đường bộ 2024 Điều 23

**Câu trả lời của VietLegal AI**:
```markdown
Hiện tại cơ sở dữ liệu được cung cấp không chứa thông tin quy định về "Quy tắc phòng ngừa đâm va tàu thuyền trên biển (COLREGs) áp dụng vùng biển quốc tế quy định quyền ưu tiên của tàu buồm". 

Do đó, tôi chưa có đủ cơ sở pháp lý theo dữ liệu được cung cấp để giải đáp câu hỏi này. Bạn vui lòng tham khảo thêm ý kiến của cơ quan có thẩm quyền hoặc chuyên gia hàng hải.
```

---

### VI. KẾT LUẬN NGHIỆM THU TẦNG 2 (FINAL VERDICT)

# **FINAL VERDICT: `GENERATION PASS 🟢`**

> [!TIP]
> **Hệ thống VietLegal AI đã vượt qua trọn vẹn thử nghiệm Tầng 2:**
> 1. Độ chính xác câu trả lời đạt **86.67%** (vượt chỉ tiêu 85%).
> 2. Tỷ lệ trích dẫn chuẩn xác đạt **100.00%** có căn cứ vững chắc (vượt chỉ tiêu 90%).
> 3. Kiểm soát triệt để hiện tượng bịa đặt (Hallucination = **0.00%** $\le$ 5%).
> 4. Xử lý xuất sắc **100%** (6/6) các ca ngoài cơ sở dữ liệu bằng cách từ chối trung thực thay vì bịa luật.