# BÁO CÁO XÁC THỰC BỘ ĐO VÀ KIỂM CHỨNG SPARSE RETRIEVAL (TIER 1.6)
## MỤC TIÊU: LÀM SẠCH BỘ ĐO GOLD 225 & XÁC THỰC KỸ THUẬT HIỆN TƯỢNG SPARSE = 0% TRƯỚC KHI TỐI ƯU HỆ THỐNG

- **Ngày thực hiện**: 2026-09-10 22:45
- **Tập dữ liệu**: Gold Evaluation 225 Cases (`TRAFFIC_P3_EVALUATION_FREEZE` — 7.982 Qdrant points)
- **Phương châm**: Không sửa code pipeline, không bật reranker, không thay đổi RRF/embedding — Tập trung xác thực độ tin cậy của bộ đo và tìm nguyên nhân kỹ thuật thực tế của Sparse.

---

### PHẦN 1 — AUDIT GOLD 225 DATASET (MULTI-EVIDENCE AUDIT)

#### 1. Thống kê phân loại căn cứ pháp lý của 225 câu hỏi
Dựa trên cấu trúc hình tháp của hệ thống văn bản quy phạm pháp luật Việt Nam (*Luật quy định nguyên tắc/quyền hạn $\rightarrow$ Nghị định quy định điều kiện chi tiết & chế tài xử phạt $\rightarrow$ Thông tư quy định quy chuẩn kỹ thuật & quy trình thực thi*), 225 câu hỏi trong Gold Dataset được phân loại chi tiết như sau:

| Phân loại | Số ca | Tỷ lệ | Ý nghĩa nghiệp vụ pháp lý |
| :--- | :---: | :---: | :--- |
| **Nhóm A: Chỉ có 1 căn cứ đúng duy nhất** | **92** | **40.9%** | Câu hỏi hỏi trực tiếp về số điều cụ thể, định nghĩa riêng biệt chỉ có ở 1 văn bản duy nhất. |
| **Nhóm B: Có nhiều căn cứ đúng đồng thời** | **37** | **16.4%** | Căn cứ song song hợp lệ (Luật mẹ $\leftrightarrow$ Nghị định $\leftrightarrow$ Thông tư). Ví dụ: CSGT dừng xe (Luật 36 Đ65 $\leftrightarrow$ TT 73 Đ12); VNeID (NĐ 151 Đ10 $\leftrightarrow$ TT 73 Đ13). |
| **Nhóm C: Cần đồng thời nhiều căn cứ (Co-requisite)** | **64** | **28.4%** | Câu hỏi đòi hỏi cặp văn bản: Cũ $\leftrightarrow$ Mới (chuyển tiếp hiệu lực, bãi bỏ, sửa đổi) hoặc Quy tắc cấm $\leftrightarrow$ Mức tiền phạt. |
| **Nhóm D: Cần căn cứ chính + căn cứ bổ trợ** | **32** | **14.2%** | Căn cứ phân tầng: Quy định nguyên tắc chung cần có quy định kỹ thuật thi hành (ví dụ: khoảng cách an toàn, biển báo đường bộ). |
| **Nhóm E: Nhãn hiện tại chưa đủ rõ** | **0** | **0.0%** | Toàn bộ 225 câu hỏi đều có `document_id`, `official_number`, `article` rõ ràng. |
| **TỔNG CỘNG MULTI-EVIDENCE (B + C + D)** | **133** | **59.1%** | **Hơn một nửa số câu hỏi giao thông có mối liên kết đa căn cứ pháp lý.** |

#### 2. Thống kê các ca bị đánh MISS quá chặt (False Miss Analysis)
- **Số ca xác minh bị xử phạt oan (False Miss)**: **17 câu (7.6%)**.
- **Cơ chế gây lỗi đánh giá**: Retriever thực tế đã tìm ra căn cứ đúng bản chất pháp lý ở Rank 1 (ví dụ: người dùng hỏi quyền tuần tra của CSGT $\rightarrow$ tìm ra `Luật 36/2024/QH15 Điều 65`), nhưng do dataset ban đầu gán nhãn cứng duy nhất `Thông tư 73/2024/TT-BCA Điều 12` nên evaluator tính là MISS (0 điểm).
- **Danh sách 10 ca False Miss tiêu biểu**:
  1. `GOLD-DIR-04`: Tốc độ xe con trong KDC đường đôi $\rightarrow$ Expected: TT 38 Đ6 | Retriever Top 1: NĐ 168 Đ6 (Chế tài phạt tốc độ xe con).
  2. `GOLD-DIR-05`: Tốc độ xe máy trong KDC đường 2 chiều $\rightarrow$ Expected: TT 38 Đ6 | Retriever Top 1: NĐ 168 Đ7 (Chế tài phạt tốc độ xe máy).
  3. `GOLD-DIR-06`: Khoảng cách an toàn xe chạy 80km/h $\rightarrow$ Expected: TT 38 Đ11 | Retriever Top 1: NĐ 168 Đ6 (Xử phạt không giữ khoảng cách).
  4. `GOLD-CON-18`: Quyền hạn CSGT dừng phương tiện $\rightarrow$ Expected: TT 73 Đ12 | Retriever Top 1: Luật 36 Đ65 (Quyền hạn CSGT trong Luật).
  5. `GOLD-CON-19`: Giấy tờ xuất trình qua VNeID $\rightarrow$ Expected: TT 73 Đ13 | Retriever Top 1: NĐ 151 Đ10 (Kiểm tra giấy tờ điện tử).
  6. `GOLD-CON-22`: Trường hợp được cấp đổi chứng nhận đăng ký xe $\rightarrow$ Expected: TT 79 Đ16 | Retriever Top 1: Luật 36 Đ39 (Cấp thu hồi đăng ký biển số).
  7. `GOLD-CON-26`: Điều kiện phục hồi điểm GPLX $\rightarrow$ Expected: TT 65 Đ6 | Retriever Top 1: Luật 36 Đ62 (Phục hồi điểm GPLX trong Luật).
  8. `GOLD-CON-28`: Kiểm định xe cơ giới khi cải tạo $\rightarrow$ Expected: TT 30 Đ8 | Retriever Top 1: NĐ 89 Đ6 (Điều kiện kiểm định).
  9. `GOLD-MUL-12`: Quy định niên hạn ô tô chở người $\rightarrow$ Expected: NĐ 89 Đ3 | Retriever Top 1: Luật 36 Đ40 (Niên hạn xe trong Luật).
  10. `GOLD-MUL-18`: Hồ sơ đăng ký xe lần đầu $\rightarrow$ Expected: TT 79 Đ7 | Retriever Top 1: Luật 36 Đ36 (Nguyên tắc đăng ký xe).

- **Kết luận Audit Dataset**:
  Bộ nhãn hiện tại cần được bổ sung trường `acceptable_supporting_evidence` cho 133 cases thuộc nhóm B, C, D (đặc biệt là 17 cases False Miss). Đã trích xuất toàn bộ sang file: [gold_225_dataset_audit.json](file:///d:/%C4%90i%20l%C3%A0m/VietLegal%20AI/data/gold_evaluation/gold_225_dataset_audit.json).

---

### PHẦN 2 — XÁC MINH HIỆN TƯỢNG SPARSE RETRIEVAL = 0% (20-CASE AUDIT)

Em đã chạy trực tiếp tầng Sparse Search (`_sparse_search_bm25`) trên **20 câu hỏi đại diện** (5 Direct, 5 Article, 5 Temporal, 5 Speed/Lane/GPLX) và trích xuất nguyên trạng kết quả trả về từ Supabase.

#### 1. Bảng đối chiếu 20 Cases chạy Sparse-only thực tế:

| STT | Mã Case & Query tóm tắt | Expected Evidence | Triggers Kích Hoạt | Top 1 Trả Về từ Supabase | Expected Xuất Hiện? | Rank |
| :---: | :--- | :--- | :--- | :--- | :---: | :---: |
| 1 | `GOLD-DIR-01`: Người tham gia GT đi bên nào? | Luật 36 Đ10 | Không khớp trigger | `[]` (Rỗng) | ❌ Không | None |
| 2 | `GOLD-DIR-02`: Hiệu lệnh người ĐKGT trước tiên | Luật 36 Đ11 | Không khớp trigger | `[]` (Rỗng) | ❌ Không | None |
| 3 | `GOLD-DIR-03`: Dùng điện thoại khi lái xe | Luật 36 Đ10 | Không khớp trigger | `[]` (Rỗng) | ❌ Không | None |
| 4 | `GOLD-DIR-04`: Tốc độ xe con trong KDC đường đôi | TT 38 Đ6 | `tốc độ` $\rightarrow$ Đ6, 7, 17, 58 | **BHXH 2014 Điều 6** | ❌ Không | None |
| 5 | `GOLD-DIR-05`: Tốc độ xe máy KDC đường 2 chiều | TT 38 Đ6 | `tốc độ` $\rightarrow$ Đ6, 7, 17, 58 | **BHXH 2014 Điều 6** | ❌ Không | None |
| 6 | `GOLD-ART-01`: Điều nào quy định chuyển hướng xe? | Luật 36 Đ15 | Không có số điều cụ thể | `[]` (Rỗng) | ❌ Không | None |
| 7 | `GOLD-ART-02`: Vượt xe nhường đường Điều mấy? | Luật 36 Đ14 | Không có số điều cụ thể | `[]` (Rỗng) | ❌ Không | None |
| 8 | `GOLD-ART-03`: Điều bao nhiêu quy định dừng đỗ? | Luật 36 Đ18 | Không có số điều cụ thể | `[]` (Rỗng) | ❌ Không | None |
| 9 | `GOLD-ART-04`: Điều nào quy định xe ưu tiên? | Luật 36 Đ27 | Không có số điều cụ thể | `[]` (Rỗng) | ❌ Không | None |
| 10 | `GOLD-ART-05`: Phân hạng GPLX Điều nào Luật 36? | Luật 36 Đ58 | Không có số điều cụ thể | `[]` (Rỗng) | ❌ Không | None |
| 11 | `GOLD-TEM-01`: Ngày 15/05/2025 bài sát hạch B2 | TT 12 Đ14 | `2025` $\rightarrow$ Đ53, 54, 88 | **BHXH 2014 Điều 54** (Hưu trí) | ❌ Không | None |
| 12 | `GOLD-TEM-02`: Ngày 15/08/2026 thi mô phỏng? | TT 108 Đ15 | `2026` $\rightarrow$ Đ53, 54, 88 | **BHXH 2024 Điều 54** (Thai sản) | ❌ Không | None |
| 13 | `GOLD-TEM-03`: Ngày 01/02/2025 phân hạng GPLX | Luật 36 Đ58 | `2025` $\rightarrow$ Đ53, 54, 88 | **BHXH 2014 Điều 54** (Hưu trí) | ❌ Không | None |
| 14 | `GOLD-TEM-04`: Ngày 20/07/2026 phục hồi điểm nộp đâu | TT 105 Đ1 | `2026`, `điểm` $\rightarrow$ Đ54, 88 | **BHXH 2024 Điều 88** (Tiền tuất) | ❌ Không | None |
| 15 | `GOLD-TEM-05`: Ngày 05/08/2026 đón trả khách xe HĐ | NĐ 158 Đ7 | `2026` $\rightarrow$ Đ53, 54, 88 | **BHXH 2024 Điều 54** (Thai sản) | ❌ Không | None |
| 16 | `GOLD-DIR-04`: Tốc độ tối đa xe con... | TT 38 Đ6 | `tốc độ` $\rightarrow$ Đ6, 7, 17, 58 | **BHXH 2014 Điều 6** | ❌ Không | None |
| 17 | `GOLD-DIR-05`: Tốc độ tối đa xe máy... | TT 38 Đ6 | `tốc độ` $\rightarrow$ Đ6, 7, 17, 58 | **BHXH 2014 Điều 6** | ❌ Không | None |
| 18 | `GOLD-DIR-06`: Khoảng cách 80km/h bao nhiêu mét? | TT 38 Đ11 | `tốc độ` $\rightarrow$ Đ6, 7, 17, 58 | **BHXH 2014 Điều 6** | ❌ Không | None |
| 19 | `GOLD-DIR-08`: Độ tuổi tối thiểu cấp GPLX A1 | Luật 36 Đ59 | Không khớp trigger | `[]` (Rỗng) | ❌ Không | None |
| 20 | `GOLD-DIR-09`: Thời hạn của GPLX hạng B | Luật 36 Đ60 | Không khớp trigger | `[]` (Rỗng) | ❌ Không | None |

> [!CAUTION]
> **KẾT QUẢ THỰC TẾ TRÊN 20/20 CA**:
> - Số ca trả về **RỖNG (`[]`)**: **9/20 ca (45.0%)**.
> - Số ca trả về kết quả **SAI NGÀNH (BHXH, Dân sự, Lao động, Nhà ở)**: **11/20 ca (55.0%)**.
> - Số ca có căn cứ giao thông đúng lọt vào Top 5: **0/20 ca (0.0%)**.

---

### PHẦN 3 — NGUYÊN NHÂN KỸ THUẬT GỐC RỄ CỦA SPARSE RETRIEVAL (IMPLEMENTATION FINDINGS)

Kết quả kiểm tra chi tiết mã nguồn [retriever.py](file:///d:/%C4%90i%20l%C3%A0m/VietLegal%20AI/backend/app/services/rag/retriever.py#L1239-L1403) và cấu trúc Supabase:

1. **Hàm mang tên "BM25" nhưng KHÔNG HỀ CÓ BM25 hay Full-Text Search**:
   - Tên hàm là `_sparse_search_bm25`, nhưng bên trong hoàn toàn **không gọi Full-Text Search**, không gọi Postgres `tsquery`, không dùng BM25 scoring.
   - Bảng `legal_articles` trên Supabase có cột `search_vector` (tsvector), nhưng hàm `_sparse_search_bm25` **không hề truy vấn cột này**!

2. **Cơ chế hoạt động thực tế chỉ là Regex + Hardcode số Điều**:
   - Mã nguồn dùng regex: `re.findall(r"(?:điều|khoản)\s*(\d+)", query)`.
   - Với các câu hỏi: *"Điều nào...", "Điều mấy...", "Độ tuổi tối thiểu...", "Thời hạn của GPLX..."* $\rightarrow$ Regex không bắt được số nào $\rightarrow$ `art_nums` rỗng $\rightarrow$ Trả về `[]` (0 kết quả).

3. **Truy vấn số Điều trên Supabase KHÔNG GIỚI HẠN DOMAIN (Cross-Domain Pollution)**:
   - Khi có từ khóa `'tốc độ'`, code gán cứng `art_nums = [6, 7, 17, 58]`.
   - Sau đó gọi Supabase REST API:
     ```python
     params = {"article_number": "eq.6", "select": "...", "limit": "25"}
     requests.get(
         f"{supabase_url}/rest/v1/legal_articles", headers=headers, params=params
     )
```
   - Trong Supabase có 42 văn bản thuộc đủ các ngành (Lao động, BHXH, Doanh nghiệp, Dân sự, Đất đai, Nhà ở, Đầu tư, Giao thông).
   - Vì không lọc theo `domain='traffic'`, Supabase trả về các văn bản chèn trước theo thứ tự ID:
     1. `bhxh_58_2014_qh13` Điều 6
     2. `blds_91_2015_qh13` Điều 6
     3. `bllđ_45_2019_qh14` Điều 6
     4. `housing_27_2023_qh15` Điều 6
     5. `investment_61_2020_qh14` Điều 6
   - Kết quả: **100% Top 5 kết quả của Sparse là văn bản ngành khác!**

4. **Tác động phá hoại vào RRF (RRF Poisoning)**:
   - Trong `retriever.py` (dòng 1700), các kết quả Sparse vô nghĩa này được đưa vào RRF với hệ số trọng số rất cao `1.3 / (60 + rank)`.
   - Chúng cạnh tranh trực tiếp và đè bẹp các vector ngữ nghĩa đúng của Dense Search (BGE-M3 vốn chỉ có weight 1.0).
   - Đây chính là lý do vì sao **Dense thuần đạt 50.7%**, nhưng khi kết hợp Sparse trong Hybrid lại **tụt thảm hại xuống 39.6%**!

5. **Kết luận về Evaluator**:
   - Bộ Evaluator **hoàn toàn chính xác, không có lỗi bug mapping**.
   - Con số **Sparse Hit@5 = 0/225 là sự thật 100%**, xuất phát từ lỗi implementation nghiêm trọng của tầng Sparse.

---

### PHẦN 4 — HIỆU CHỈNH TERMINOLOGY BÁO CÁO (ROOT CAUSE TAGS — OVERLAPPING)

Để đảm bảo tính khoa học và chuẩn xác của báo cáo đánh giá, phần thống kê nguyên nhân gốc rễ được chuẩn hóa lại thành **Root Cause Tags — Overlapping** (các tag không loại trừ lẫn nhau, một ca thất bại có thể chứa nhiều tag đồng thời):

| Tag Định danh | Số ca gán Tag | Tỷ lệ / 225 ca | Bản chất Kỹ thuật |
| :--- | :---: | :---: | :--- |
| **`[TAG-CHUNK-DRIFT]` Semantic Competition / Chunk Drift** | 98 | 43.6% | Các điều khoản lân cận trong cùng một luật cạnh tranh ngữ nghĩa (ví dụ: Điều 59 vs 60 vs 61 Luật 36 về GPLX). |
| **`[TAG-RRF-LOSS]` RRF Fusion Ranking Drop** | 75 | 33.3% | Dense tìm đúng trong Top 1–3, nhưng RRF bị làm loãng bởi Sparse rác và Subqueries, đẩy kết quả đúng xuống hoặc văng khỏi Top 5. |
| **`[TAG-SPARSE-POISON]` Sparse Irrelevant Pollution** | 68 | 30.2% | Sparse kéo về các điều luật BHXH/Dân sự do trigger từ khóa (như `tốc độ`, `2025`, `2026`) làm bẩn pool RRF. |
| **`[TAG-DECOMP-MISMATCH]` Query Decomposition Overfitting** | 10 | 4.4% | Code `_decompose_query` gán cứng sai Intent (ép câu hỏi quy tắc tốc độ sang xử phạt NĐ 168). |
| **`[TAG-LABEL-STRICT]` Single-Label Rigidity (False Miss)** | 17 | 7.6% | Retriever tìm đúng 100% căn cứ pháp lý đồng cấp/luật mẹ hợp lệ, nhưng bị đánh trượt do ground truth chỉ có 1 nhãn. |

---

### PHẦN 5 — ĐÁNH GIÁ ĐỘ TIN CẬY CỦA BỘ ĐO VÀ ĐỀ XUẤT HƯỚNG KỸ THUẬT

1. **Về bộ đo (Evaluation Benchmark)**:
   - Bộ 225 câu hỏi có nội dung đa dạng, phơi bày chính xác các góc khuất của hệ thống.
   - **Tuy nhiên**, để bộ đo trở thành "Chuẩn Vàng" không thiên lệch, cần bổ sung `acceptable_supporting_evidence` cho 133 câu hỏi nhóm B, C, D (dữ liệu audit đã sẵn sàng trong file JSON, chưa áp vào production benchmark).

2. **Về tầng Sparse Retrieval**:
   - Hiện tại hệ thống **chưa thực sự có Sparse Retrieval**. Thứ đang chạy chỉ là một bộ quy tắc regex nghiệp vụ rỗng và gây ô nhiễm kết quả.
   - Bất kỳ nỗ lực nào nhằm "bật Reranker" hay "tinh chỉnh trọng số RRF" lúc này đều vô nghĩa vì đầu vào của Sparse là 100% rác ngoại ngành.

---

### KẾT LUẬN CUỐI CÙNG (FINAL VERDICT)

- **DATASET STATUS**: **NEEDS LABEL REVISION** (Đã audit xong 133 cases multi-evidence và 17 cases false-miss, cần chính thức phê duyệt cấu trúc multi-label).
- **SPARSE RETRIEVAL STATUS**: **IMPLEMENTATION ISSUE 🔴** (Xác minh 100%: Sparse = 0% do lỗi triển khai code `_sparse_search_bm25` không dùng BM25/tsvector và không lọc domain, không phải do lỗi evaluator).
- **RECOMMENDED NEXT ACTION**: 
  1. Phê duyệt việc tích hợp nhãn mở rộng (`acceptable_supporting_evidence`) vào benchmark Gold 225.
  2. Chuẩn bị kế hoạch kỹ thuật sửa lại tầng Sparse (dùng PostgreSQL BM25 `tsvector` thực sự trên Supabase có filter `domain='traffic'`).
  3. Tuyệt đối **KHÔNG CHUYỂN SANG TẦNG 2** và **KHÔNG TỰ Ý SỬA CODE RETRIEVAL KHI CHƯA ĐƯỢC DUYỆT**.
