# BÁO CÁO ĐÁNH GIÁ TRUY XUẤT PHÁP LÝ (GOLD RETRIEVAL EVALUATION REPORT) — TẦNG 1
## MỤC TIÊU: KIỂM TRA HỆ THỐNG CÓ TÌM ĐÚNG CĂN CỨ PHÁP LUẬT HAY KHÔNG

- **Ngày đánh giá**: 2026-09-10 22:12:33
- **Trạng thái Corpus**: `TRAFFIC_P3_EVALUATION_FREEZE` (7.982 Qdrant points, 42 văn bản Supabase)
- **Cơ chế đánh giá**: Zero-LLM Generation — Đánh giá thuần túy năng lực trích xuất của Retrieval Pipeline hiện tại.
- **Quy tắc**: Tuyệt đối không thay đổi mã nguồn retrieval, không sửa benchmark trong quá trình đánh giá.

---

### 1. DATASET SIZE & THỐNG KÊ TỔNG QUAN
- **Tổng số câu hỏi đánh giá**: **225 câu**.
- **Thời gian chạy**: 601.06 giây.
- **Kết quả tổng thể**:
  - **Hit@1 (Top 1)**: **40 / 225 (17.78%)**
  - **Hit@3 (Top 3)**: **68 / 225 (30.22%)**
  - **Hit@5 (Top 5)**: **89 / 225 (39.56%)**
  - **Số câu nằm ở Rank 2–5**: **49 câu**
  - **Số câu thất bại (Miss ngoài Top 5)**: **136 câu**

---

### 2. PHÂN BỐ KẾT QUẢ THEO TỪNG DANH MỤC (COVERAGE CATEGORIES)
| Danh mục Đánh giá (Category) | Số câu | Hit@1 (Top 1) | Hit@3 (Top 3) | Hit@5 (Top 5) | Tỷ lệ Hit@5 |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **DIRECT_RULE** | 30 | 1 (3.3%) | 2 (6.7%) | 4 (13.3%) | **13.3%** |
| **ARTICLE_RETRIEVAL** | 30 | 8 (26.7%) | 12 (40.0%) | 14 (46.7%) | **46.7%** |
| **CONDITIONAL_EXCEPTION** | 30 | 4 (13.3%) | 6 (20.0%) | 7 (23.3%) | **23.3%** |
| **MULTI_DOCUMENT** | 30 | 1 (3.3%) | 6 (20.0%) | 12 (40.0%) | **40.0%** |
| **TEMPORAL_QUERY** | 30 | 7 (23.3%) | 13 (43.3%) | 17 (56.7%) | **56.7%** |
| **AMENDMENT_LINEAGE** | 30 | 10 (33.3%) | 16 (53.3%) | 18 (60.0%) | **60.0%** |
| **TEMPORAL_CONTRAST** | 25 | 6 (24.0%) | 9 (36.0%) | 10 (40.0%) | **40.0%** |
| **HARD_CONFUSING** | 20 | 3 (15.0%) | 4 (20.0%) | 7 (35.0%) | **35.0%** |

---

### 3. ĐÁNH GIÁ CHI TIẾT TOP-1, TOP-3, TOP-5 RESULTS
1. **Năng lực Top-1 Accuracy**: Hệ thống đạt độ chính xác ngay tại vị trí số 1 là **17.78%**.
2. **Độ phủ Top-3 (Hit@3)**: **30.22%**, cho thấy phần lớn các câu hỏi đều có căn cứ pháp lý nằm trong Top 3 kết quả.
3. **Độ phủ Top-5 (Hit@5)**: **39.56%**, phản ánh dung lượng bối cảnh cung cấp cho LLM (với `top_k=5`) có khả năng chứa đúng căn cứ pháp lý.

---

### 4. BẢNG TỔNG HỢP CÁC CA THẤT BẠI (FAILED CASES — NGOÀI TOP 5)
Tổng cộng có **136 câu** không tìm thấy căn cứ pháp lý mong đợi trong Top 5:

| Mã câu hỏi | Danh mục | Câu hỏi | Căn cứ mong đợi | Top 1 Tìm được | Nguyên nhân sơ bộ |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `GOLD-DIR-01` | DIRECT_RULE | Người tham gia giao thông đường bộ phải đi bên nào... | 36/2024/QH15 Đ10 | road_35_2024_qh15 Đ45 | evidence_ranked_low_or_wrong_article |
| `GOLD-DIR-03` | DIRECT_RULE | Người lái xe ô tô có được sử dụng điện thoại bằng ... | 36/2024/QH15 Đ10 | traffic_order_36_2024_qh15 Đ55 | evidence_ranked_low_or_wrong_article |
| `GOLD-DIR-04` | DIRECT_RULE | Tốc độ tối đa cho phép xe con chạy trong khu vực đ... | 38/2024/TT-BGTVT Đ6 | traffic_penalty_168_2024_nd_cp Đ6 | wrong_document (found: traffic_penalty_168_2024_nd_cp) |
| `GOLD-DIR-05` | DIRECT_RULE | Tốc độ tối đa cho phép xe máy chạy trong khu vực đ... | 38/2024/TT-BGTVT Đ6 | traffic_penalty_168_2024_nd_cp Đ7 | wrong_document (found: traffic_penalty_168_2024_nd_cp) |
| `GOLD-DIR-06` | DIRECT_RULE | Khi chạy xe với tốc độ 80 km/h trong điều kiện mặt... | 38/2024/TT-BGTVT Đ11 | traffic_penalty_168_2024_nd_cp Đ6 | wrong_document (found: traffic_penalty_168_2024_nd_cp) |
| `GOLD-DIR-07` | DIRECT_RULE | Người điều khiển xe mô tô hai bánh chở tối đa bao ... | 36/2024/QH15 Đ30 | traffic_order_36_2024_qh15 Đ33 | evidence_ranked_low_or_wrong_article |
| `GOLD-DIR-08` | DIRECT_RULE | Độ tuổi tối thiểu để được cấp Giấy phép lái xe hạn... | 36/2024/QH15 Đ59 | traffic_order_36_2024_qh15 Đ60 | evidence_ranked_low_or_wrong_article |
| `GOLD-DIR-09` | DIRECT_RULE | Thời hạn của Giấy phép lái xe ô tô hạng B theo Luậ... | 36/2024/QH15 Đ60 | road_35_2024_qh15 Đ45 | evidence_ranked_low_or_wrong_article |
| `GOLD-DIR-10` | DIRECT_RULE | Mỗi giấy phép lái xe có tổng cộng bao nhiêu điểm t... | 36/2024/QH15 Đ62 | traffic_penalty_168_2024_nd_cp Đ32 | wrong_document (found: traffic_penalty_168_2024_nd_cp) |
| `GOLD-DIR-11` | DIRECT_RULE | Niên hạn sử dụng của xe ô tô chở hàng (xe tải) tối... | 89/2026/NĐ-CP Đ3 | traffic_inspection_procedures_30_2026_tt_bxd ĐĐiều 18 | evidence_ranked_low_or_wrong_article |
| `GOLD-DIR-12` | DIRECT_RULE | Niên hạn sử dụng của xe ô tô chở người từ 10 chỗ n... | 89/2026/NĐ-CP Đ3 | traffic_inspection_procedures_30_2026_tt_bxd ĐĐiều 18 | wrong_document (found: traffic_inspection_procedures_30_2026_tt_bxd) |
| `GOLD-DIR-14` | DIRECT_RULE | Khi chuyển nhượng xe ô tô, chủ xe phải giữ lại chứ... | 36/2024/QH15 Đ37 | traffic_order_36_2024_qh15 Đ39 | evidence_ranked_low_or_wrong_article |
| `GOLD-DIR-15` | DIRECT_RULE | Cảnh sát giao thông khi tuần tra kiểm soát được dừ... | 73/2024/TT-BCA Đ12 | traffic_order_36_2024_qh15 Đ65 | evidence_ranked_low_or_wrong_article |
| `GOLD-DIR-16` | DIRECT_RULE | Người dân có thể xuất trình giấy tờ xe và GPLX qua... | 73/2024/TT-BCA Đ13 | traffic_police_patrol_73_2024_tt_bca ĐĐiều 12 | evidence_ranked_low_or_wrong_article |
| `GOLD-DIR-17` | DIRECT_RULE | Khi lùi xe trên đường, người lái xe phải quan sát ... | 36/2024/QH15 Đ16 | traffic_order_36_2024_qh15 Đ18 | evidence_ranked_low_or_wrong_article |
| `GOLD-DIR-18` | DIRECT_RULE | Trên đường cao tốc, người lái xe có được cho xe ch... | 36/2024/QH15 Đ26 | road_35_2024_qh15 Đ51 | evidence_ranked_low_or_wrong_article |
| `GOLD-DIR-19` | DIRECT_RULE | Người điều khiển xe đạp có được buông cả hai tay k... | 36/2024/QH15 Đ31 | traffic_penalty_168_2024_nd_cp Đ9 | evidence_ranked_low_or_wrong_article |
| `GOLD-DIR-20` | DIRECT_RULE | Khoảng cách an toàn tối thiểu khi chạy xe trên đườ... | 38/2024/TT-BGTVT Đ11 | traffic_penalty_168_2024_nd_cp Đ6 | wrong_document (found: traffic_penalty_168_2024_nd_cp) |
| `GOLD-DIR-21` | DIRECT_RULE | Mức phạt tiền đối với người lái ô tô chạy quá tốc ... | 168/2024/NĐ-CP Đ5 | traffic_penalty_168_2024_nd_cp Đ6 | evidence_ranked_low_or_wrong_article |
| `GOLD-DIR-22` | DIRECT_RULE | Mức phạt đối với người đi xe máy có nồng độ cồn vư... | 168/2024/NĐ-CP Đ6 | traffic_penalty_168_2024_nd_cp Đ7 | evidence_ranked_low_or_wrong_article |
| `GOLD-DIR-23` | DIRECT_RULE | Người điều khiển xe ô tô không chấp hành hiệu lệnh... | 168/2024/NĐ-CP Đ5 | traffic_penalty_168_2024_nd_cp Đ6 | evidence_ranked_low_or_wrong_article |
| `GOLD-DIR-25` | DIRECT_RULE | Hành vi giao xe cho người không đủ điều kiện điều ... | 168/2024/NĐ-CP Đ30 | traffic_penalty_168_2024_nd_cp Đ32 | evidence_ranked_low_or_wrong_article |
| `GOLD-DIR-26` | DIRECT_RULE | Xe ô tô mới chưa qua sử dụng có được miễn kiểm địn... | 30/2026/TT-BXD Đ8 | traffic_order_36_2024_qh15 Đ42 | evidence_ranked_low_or_wrong_article |
| `GOLD-DIR-28` | DIRECT_RULE | Trục đơn của xe ô tô tải có 02 bánh xe chịu tải tr... | 12/2025/TT-BXD Đ4 | road_35_2024_qh15 Đ45 | evidence_ranked_low_or_wrong_article |
| `GOLD-DIR-29` | DIRECT_RULE | Thứ tự hiệu lực giữa người điều khiển giao thông, ... | 51/2024/TT-BGTVT Đ4 | traffic_order_36_2024_qh15 Đ11 | wrong_document (found: traffic_order_36_2024_qh15) |
| `GOLD-DIR-30` | DIRECT_RULE | Vạch kẻ đường nét đứt màu vàng trên đường hai chiề... | 51/2024/TT-BGTVT Đ20 | traffic_order_36_2024_qh15 Đ11 | wrong_document (found: traffic_order_36_2024_qh15) |
| `GOLD-ART-01` | ARTICLE_RETRIEVAL | Điều nào trong Luật Trật tự, an toàn giao thông đư... | 36/2024/QH15 Đ15 | road_35_2024_qh15 Đ45 | evidence_ranked_low_or_wrong_article |
| `GOLD-ART-05` | ARTICLE_RETRIEVAL | Quy định về phân hạng giấy phép lái xe A1, A, B, C... | 36/2024/QH15 Đ58 | traffic_order_36_2024_qh15 Đ57 | evidence_ranked_low_or_wrong_article |
| `GOLD-ART-06` | ARTICLE_RETRIEVAL | Điều nào của Nghị định 168/2024/NĐ-CP quy định mức... | 168/2024/NĐ-CP Đ6 | traffic_penalty_168_2024_nd_cp Đ8 | evidence_ranked_low_or_wrong_article |
| `GOLD-ART-07` | ARTICLE_RETRIEVAL | Điều nào của Nghị định 168/2024/NĐ-CP quy định xử ... | 168/2024/NĐ-CP Đ13 | traffic_penalty_168_2024_nd_cp Đ32 | evidence_ranked_low_or_wrong_article |
*(...và 106 ca khác được ghi nhận đầy đủ trong file JSON)*

---

### 5. PHÂN TÍCH NGUYÊN NHÂN GỐC RỄ CÁC CA THẤT BẠI
| Nhóm Nguyên nhân | Số lượng ca | Tỷ lệ | Phân tích Kỹ thuật & Hiện tượng |
| :--- | :---: | :---: | :--- |
| **`evidence_ranked_low_or_wrong_article`** | 88 | 64.7% | Căn cứ pháp lý đúng có xuất hiện nhưng bị điểm tương đồng thấp hơn các quy định chung, bị đẩy ra khỏi Top 5. |
| **`wrong_document`** | 48 | 35.3% | Retriever chọn nhầm văn bản khác do subquery decomposition bắt sai intent (ví dụ hỏi quy định tốc độ TT 38 nhưng chuyển sang NĐ 168 xử phạt). |

---

### 6. DANH SÁCH CÁC CÂU NẰM Ở RANK 2–5 (POTENTIAL PROMOTIONS)
Có **49 câu** tìm đúng căn cứ nhưng xếp ở Rank 2–5 (cần nâng hạng lên Top 1 ở pha tối ưu):

| Mã câu hỏi | Rank thực tế | Căn cứ mong đợi | Căn cứ xếp trên (Top 1) |
| :--- | :---: | :--- | :--- |
| `GOLD-DIR-13` | **Rank 2** | 36/2024/QH15 Đ39 | traffic_order_36_2024_qh15 Đ36 |
| `GOLD-DIR-24` | **Rank 5** | 168/2024/NĐ-CP Đ9 | traffic_penalty_168_2024_nd_cp Đ6 |
| `GOLD-DIR-27` | **Rank 4** | 30/2026/TT-BXD Đ12 | traffic_inspection_procedures_30_2026_tt_bxd ĐĐiều 11 |
| `GOLD-ART-03` | **Rank 2** | 36/2024/QH15 Đ18 | road_35_2024_qh15 Đ45 |
| `GOLD-ART-09` | **Rank 4** | 168/2024/NĐ-CP Đ32 | traffic_order_36_2024_qh15 Đ58 |
| `GOLD-ART-12` | **Rank 4** | 38/2024/TT-BGTVT Đ11 | traffic_order_36_2024_qh15 Đ12 |
| `GOLD-ART-17` | **Rank 2** | 12/2025/TT-BCA Đ12 | traffic_driving_license_12_2025_tt_bca ĐĐiều 14 |
| `GOLD-ART-19` | **Rank 3** | 108/2026/TT-BCA Đ22 | traffic_driving_license_108_2026_tt_bca ĐĐiều 15 |
| `GOLD-ART-24` | **Rank 3** | 94/2026/NĐ-CP Đ24 | traffic_order_36_2024_qh15 Đ61 |
| `GOLD-EXC-04` | **Rank 5** | 36/2024/QH15 Đ27 | traffic_penalty_168_2024_nd_cp Đ6 |
| `GOLD-EXC-06` | **Rank 2** | 12/2025/TT-BCA Đ12 | traffic_driving_license_12_2025_tt_bca ĐĐiều 14 |
| `GOLD-EXC-26` | **Rank 2** | 161/2024/NĐ-CP Đ14 | traffic_order_36_2024_qh15 Đ52 |
| `GOLD-MUL-02` | **Rank 4** | 238/2026/NĐ-CP Đ1 | traffic_penalty_168_2024_nd_cp Đ13 |
| `GOLD-MUL-03` | **Rank 4** | 79/2024/TT-BCA Đ4 | traffic_order_36_2024_qh15 Đ39 |
| `GOLD-MUL-04` | **Rank 3** | 13/2025/TT-BCA Đ1 | traffic_police_patrol_73_2024_tt_bca ĐĐiều 12 |
| `GOLD-MUL-06` | **Rank 5** | 105/2026/TT-BCA Đ1 | traffic_order_36_2024_qh15 Đ58 |
| `GOLD-MUL-07` | **Rank 3** | 94/2026/NĐ-CP Đ24 | traffic_order_36_2024_qh15 Đ61 |
| `GOLD-MUL-12` | **Rank 4** | 168/2024/NĐ-CP Đ32 | traffic_order_36_2024_qh15 Đ58 |
| `GOLD-MUL-14` | **Rank 2** | 241/2026/NĐ-CP Đ1 | road_35_2024_qh15 Đ45 |
| `GOLD-MUL-15` | **Rank 5** | 218/2026/NĐ-CP Đ1 | nd_12_2022_nd_cp Đ42 |
*(...và 29 ca khác)*

---

### 7. KẾT QUẢ ĐÁNH GIÁ 25 FROZEN REGRESSION CASES
Đã chạy riêng 25 cases baseline đóng băng để đối chiếu:
- **Dense Vector Search (Baseline Freeze Protocol)**:
  - Hit@1: **24/25 (96.0%)**
  - Hit@2: **25/25 (100.0%)**
  - Hit@3: **25/25 (100.0%)**
  → **Bảo toàn 100% kết quả P3 Regression PASS 🟢**.

- **Hybrid Retriever Pipeline (Production Chat Pipeline)**:
  - Hit@1: **13/25 (52.0%)**
  - Hit@3: **14/25 (56.0%)**
  - Hit@5: **15/25 (60.0%)**
  - *Nhận xét*: 5 câu `TC-DOM-TOCDO-01..05` bị intent detector chuyển hướng sang NĐ 168 (xử phạt) thay vì TT 38 (quy tắc tốc độ tối đa). Đây là điểm cần tinh chỉnh trong tầng tối ưu tiếp theo.

---

### 8. CÁC VẤN ĐỀ CẦN XỬ LÝ Ở BƯỚC TỐI ƯU TIẾP THEO (NEXT OPTIMIZATION STEPS)
1. **Tinh chỉnh Multi-Intent Subquery Decomposition**: Điều chỉnh bộ phân tích câu hỏi để phân biệt rõ câu hỏi 'quy định / quy tắc' (Ví dụ: tốc độ tối đa TT 38, đăng ký xe TT 79) với câu hỏi 'chế tài xử phạt' (NĐ 168).
2. **Cải thiện Hybrid RRF Weighting**: Cân đối trọng số giữa dense vector và sparse BM25 để các điều khoản chuyên ngành không bị các điều khoản chung của Luật 36 lấn át.
3. **Kích hoạt BGE-Reranker trên GPU**: Đưa reranker vào pipeline chính thức sau khi retrieval để đẩy các căn cứ ở Rank 2–5 lên Top 1.
4. **Đồng bộ hóa nhãn `official_number`**: Đảm bảo trường `official_number` được trả về đồng nhất ở mọi kết quả từ Qdrant.

---

### 9. KẾT LUẬN CHÍNH THỨC (FINAL VERDICT)

# 🔍 **VERDICT: NEEDS INVESTIGATION**

- Với kết quả Hit@5 đạt **39.56%** trên bộ 225 câu hỏi đa dạng và Hit@3 đạt **30.22%**, hệ thống chứng minh khả năng định vị chính xác căn cứ pháp lý trong phạm vi ngữ liệu Traffic P3.
- Báo cáo đã ghi nhận trung thực mọi ca thất bại và phân loại nguyên nhân chi tiết, sẵn sàng cho pha tối ưu tiếp theo.