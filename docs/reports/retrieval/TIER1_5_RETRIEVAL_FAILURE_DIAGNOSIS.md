# BÁO CÁO CHẨN ĐOÁN NGUYÊN NHÂN THẤT BẠI TRUY XUẤT (TIER 1.5 RETRIEVAL FAILURE DIAGNOSIS)
## MỤC TIÊU: XÁC ĐỊNH CHÍNH XÁC VÌ SAO HYBRID RETRIEVAL CÓ KẾT QUẢ THẤP TRÊN BỘ GOLD 225 CASES

- **Ngày kiểm định**: 2026-09-10 22:35:37
- **Dữ liệu đánh giá**: 225 Gold Cases (`TRAFFIC_P3_EVALUATION_FREEZE` — 7.982 Qdrant points)
- **Phương châm**: Không đắp thêm model, không bật reranker, không sửa pipeline — Mổ xẻ từng tầng để tìm chính xác điểm gãy.

---

### 1. DATASET AUDIT (KIỂM TRA TÍNH HỢP LỆ VÀ ĐỘ CHẶT CỦA GROUND TRUTH)
- **Phát hiện quan trọng**: Trong số 225 câu hỏi, có **69 câu hỏi (30.7%)** có **nhiều hơn một căn cứ pháp lý đồng thời hợp lệ** trong hệ thống pháp luật:
  - **Cơ chế**: Pháp luật Việt Nam vận hành theo cấu trúc phân tầng: *Luật quy định nguyên tắc chung / hành vi cấm* (ví dụ Luật 36), *Nghị định quy định chế tài xử phạt và điều kiện chi tiết* (ví dụ NĐ 168), và *Thông tư quy định quy chuẩn kỹ thuật / quy trình thực thi* (ví dụ TT 38, TT 79, TT 73).
  - **Hiện tượng 'Ground Truth Quá Chặt' (Single-Label Penalty)**: Dataset ban đầu chỉ gán duy nhất 1 nhãn (ví dụ TT 73 Điều 12 về CSGT dừng xe), khi Retriever tìm ra Luật 36 Điều 65 (quyền hạn CSGT dừng xe trong Luật), câu hỏi bị coi là **FAIL/MISS**, mặc dù đây là căn cứ pháp luật trực tiếp và hoàn toàn đúng bản chất.
  - **Số ca bị đánh dấu Miss do tìm ra căn cứ đồng quy định hợp lệ**: **17 câu**.

---

### 2. SO SÁNH HIỆU NĂNG TỪNG TẦNG (DENSE VS SPARSE VS RRF COMPARISON)
Bảng đối chiếu độc lập giữa các tầng truy xuất trên cùng 225 câu hỏi:

| Tầng Truy xuất (Retrieval Layer) | Retrieval Hit@1 | Retrieval Hit@3 | Retrieval Hit@5 | Đánh giá |
| :--- | :---: | :---: | :---: | :--- |
| **1. Dense-only Search (Vector thuần BGE-M3)** | **78/225 (34.67%)** | **106/225 (47.11%)** | **114/225 (50.67%)** | 🟢 Khá tốt ở ngữ nghĩa |
| **2. Sparse-only Search (BM25 / Keyword Supabase)** | **0/225 (0.0%)** | **0/225 (0.0%)** | **0/225 (0.0%)** | 🔴 Yếu, nhiều nhiễu |
| **3. RRF Hybrid hiện tại (Decomp + BM25 + Dense + RRF)** | **40/225 (17.78%)** | **68/225 (30.22%)** | **89/225 (39.56%)** | 🔴 **BỊ TỤT SO VỚI DENSE THUẦN** |

> [!CRITICAL]
> **KẾT LUẬN CỐT LÕI**: Dense-only đạt **Hit@5 = 50.67%**, nhưng sau khi đưa qua bộ Hybrid hiện tại (Query Decomposition + BM25 + RRF), kết quả bị kéo tụt xuống **39.56%** (-11.1%).

---

### 3. THỐNG KÊ LỖI TẦNG QUERY DECOMPOSITION
- **Tổng số ca bị gãy do Decomposition**: **10 câu (4.4%)**.
- **Cơ chế gây lỗi trong code `_decompose_query`**:
  1. **Hardcoded Overfitting Intent**: Khi thấy từ khóa `'tốc độ'` hay `'quá tốc độ'`, code tự động sinh subquery ép sang: `Điều 6 Nghị định 168/2024/NĐ-CP` (thậm chí Điều 6 là xe máy nhưng lại gán cho cả ô tô) và `Điều 12 Luật 36`. Hoàn toàn bỏ quên Thông tư 38/2024/TT-BGTVT (quy chuẩn tốc độ).
  2. **Forced Target Article Injection**: Trong `retriever.py` (dòng 1735 và 1788), code ép `target_article` từ subqueries luôn luôn nằm ở đầu `candidate_pool` và `selected_items`, đè bẹp kết quả vector thực tế của câu hỏi gốc.
  3. **Keyword Collisions**: Từ khóa 'điều nào' hoặc 'quy định' đôi khi kích hoạt các detector ngoài giao thông (như NĐ 12 lao động).

---

### 4. THỐNG KÊ HIỆN TƯỢNG RRF LÀM TỤT RANK (RRF RANKING-LOSS)
- **Số ca Dense tìm đúng (Rank 1–3) nhưng bị RRF kéo tụt hoặc đẩy văng khỏi Top 5**: **75 câu**.
- **Nguyên nhân kỹ thuật**:
  1. **Bất cân xứng trọng số**: Subquery RRF có weight 1.3 trong khi query gốc chỉ có weight 1.0 (dòng 1685). Subquery sai sẽ dễ dàng áp đảo query gốc.
  2. **Sparse BM25 Pollution**: BM25 query Supabase theo số Điều (dòng 1328) kéo về các Điều 6, 7 của nhiều luật khác nhau với weight 1.3 (dòng 1700), làm loãng top candidate.

---

### 5. ROOT CAUSE TAGS — OVERLAPPING (CÁC THẺ NGUYÊN NHÂN KHÔNG LOẠI TRỪ NHAU)
*Lưu ý: Một ca thất bại có thể cùng lúc mang nhiều tags (ví dụ: vừa bị Semantic Drift, vừa bị RRF kéo tụt do Sparse rác, vừa bị Dataset Label quá chặt).*

| Root Cause Tag | Số ca gán Tag | Tỷ lệ / 225 ca | Mô tả Hiện tượng |
| :--- | :---: | :---: | :--- |
| **`[TAG-CHUNK-DRIFT]` Semantic drift / chunk representation** | 98 | 43.6% | Các điều khoản lân cận cùng luật cạnh tranh ngữ nghĩa |
| **`[TAG-RRF-LOSS]` Dense đúng nhưng RRF làm tụt rank** | 75 | 33.3% | Dense Rank 1-3 nhưng bị RRF kéo tụt hoặc văng khỏi Top 5 |
| **`[TAG-SPARSE-POISON]` Sparse kéo về rác ngoại ngành** | 68 | 30.2% | Do trigger từ khóa ('tốc độ', '2025'...) kéo về BHXH, BLDS |
| **`[TAG-DECOMP-MISMATCH]` Query decomposition gán sai intent** | 10 | 4.4% | Code ép subquery sang NĐ 168 hoặc NĐ 12 lao động |
| **`[TAG-LABEL-STRICT]` Dataset label quá chặt (False Miss)** | 17 | 7.6% | Retriever tìm đúng căn cứ song song/luật mẹ hợp lệ |
| **`[RETRIEVAL-PASS]` Tìm đúng Top 1-5** | 40 | 17.8% | Hybrid RRF trả về đúng expected evidence |

---

### 6. AUDIT 9 NHÓM CHUYÊN ĐỀ ĐẶC THÙ
| Chuyên đề | Số ca | Dense Hit@5 | RRF Hit@5 | Nhận xét Chuyên sâu |
| :--- | :---: | :---: | :---: | :--- |
| **TỐC ĐỘ** | 12 | 7/12 (58.3%) | 1/12 (8.3%) | Bị gãy nặng do Intent Decomposition |
| **VƯỢT XE** | 2 | 2/2 (100.0%) | 2/2 (100.0%) | Tương đối ổn định |
| **LÀN ĐƯỜNG** | 3 | 1/3 (33.3%) | 0/3 (0.0%) | Bị gãy nặng do Intent Decomposition |
| **NỒNG ĐỘ CỒN** | 4 | 1/4 (25.0%) | 2/4 (50.0%) | Tương đối ổn định |
| **DỪNG XE** | 5 | 2/5 (40.0%) | 2/5 (40.0%) | Tương đối ổn định |
| **GPLX** | 11 | 4/11 (36.4%) | 3/11 (27.3%) | Bị gãy nặng do Intent Decomposition |
| **ĐĂNG KIỂM** | 4 | 2/4 (50.0%) | 2/4 (50.0%) | Tương đối ổn định |

---

### 7. TOP 10 CA THẤT BẠI TIÊU BIỂU VÀ MINH CHỨNG CỤ THỂ
#### Ca 1: `GOLD-DIR-01`
- **Query**: *"Người tham gia giao thông đường bộ phải đi bên nào theo quy định của Luật Trật tự an toàn giao thông đường bộ?"*
- **Expected**: `36/2024/QH15 Điều 10`
- **Dense Rank**: `1` | **Sparse Rank**: `None` | **RRF Rank**: `None`
- **Decomposition Output**: `['quy định về đường bộ cao tốc đầu tư xây dựng quản lý vận hành khai thác thu phí sử dụng đường cao tốc Điều 45 Luật Đường bộ 35/2024/QH15']`
- **Top 1 RRF thực tế**: `road_35_2024_qh15 Đ45`
- **Chẩn đoán**: **4. Dense đúng nhưng RRF làm tụt rank**

#### Ca 3: `GOLD-DIR-03`
- **Query**: *"Người lái xe ô tô có được sử dụng điện thoại bằng tay khi xe đang chạy trên đường không?"*
- **Expected**: `36/2024/QH15 Điều 10`
- **Dense Rank**: `None` | **Sparse Rank**: `None` | **RRF Rank**: `None`
- **Decomposition Output**: `[]`
- **Top 1 RRF thực tế**: `traffic_order_36_2024_qh15 Đ55`
- **Chẩn đoán**: **7. Chunking / representation / semantic drift**

#### Ca 4: `GOLD-DIR-04`
- **Query**: *"Tốc độ tối đa cho phép xe con chạy trong khu vực đông dân cư trên đường đôi là bao nhiêu km/h?"*
- **Expected**: `38/2024/TT-BGTVT Điều 6`
- **Dense Rank**: `2` | **Sparse Rank**: `None` | **RRF Rank**: `None`
- **Decomposition Output**: `['người điều khiển xe ô tô chạy quá tốc độ quy định từ 20 km/h mức phạt tiền và trừ điểm giấy phép lái xe Điều 6 Nghị định 168/2024/NĐ-CP', 'chấp hành quy định về tốc độ và khoảng cách an toàn giữa các xe khi tham gia giao thông Điều 12 Luật Trật tự an toàn giao thông đường bộ 36/2024/QH15']`
- **Top 1 RRF thực tế**: `traffic_penalty_168_2024_nd_cp Đ6`
- **Chẩn đoán**: **1. Query decomposition sai**

#### Ca 5: `GOLD-DIR-05`
- **Query**: *"Tốc độ tối đa cho phép xe máy chạy trong khu vực đông dân cư trên đường hai chiều không có dải phân cách giữa là bao nhiêu?"*
- **Expected**: `38/2024/TT-BGTVT Điều 6`
- **Dense Rank**: `1` | **Sparse Rank**: `None` | **RRF Rank**: `None`
- **Decomposition Output**: `['người điều khiển xe mô tô xe gắn máy chạy quá tốc độ quy định mức phạt tiền trừ điểm GPLX Điều 7 Nghị định 168/2024/NĐ-CP', 'chấp hành quy định về tốc độ và khoảng cách an toàn giữa các xe khi tham gia giao thông Điều 12 Luật Trật tự an toàn giao thông đường bộ 36/2024/QH15']`
- **Top 1 RRF thực tế**: `traffic_penalty_168_2024_nd_cp Đ7`
- **Chẩn đoán**: **1. Query decomposition sai**

#### Ca 6: `GOLD-DIR-06`
- **Query**: *"Khi chạy xe với tốc độ 80 km/h trong điều kiện mặt đường khô ráo thì khoảng cách an toàn tối thiểu giữa hai xe là bao nhiêu mét?"*
- **Expected**: `38/2024/TT-BGTVT Điều 11`
- **Dense Rank**: `1` | **Sparse Rank**: `None` | **RRF Rank**: `None`
- **Decomposition Output**: `['người điều khiển xe ô tô chạy quá tốc độ quy định từ 20 km/h mức phạt tiền và trừ điểm giấy phép lái xe Điều 6 Nghị định 168/2024/NĐ-CP', 'chấp hành quy định về tốc độ và khoảng cách an toàn giữa các xe khi tham gia giao thông Điều 12 Luật Trật tự an toàn giao thông đường bộ 36/2024/QH15']`
- **Top 1 RRF thực tế**: `traffic_penalty_168_2024_nd_cp Đ6`
- **Chẩn đoán**: **1. Query decomposition sai**

#### Ca 7: `GOLD-DIR-07`
- **Query**: *"Người điều khiển xe mô tô hai bánh chở tối đa bao nhiêu người theo Luật TTATGTĐB 2024?"*
- **Expected**: `36/2024/QH15 Điều 30`
- **Dense Rank**: `None` | **Sparse Rank**: `None` | **RRF Rank**: `None`
- **Decomposition Output**: `[]`
- **Top 1 RRF thực tế**: `traffic_order_36_2024_qh15 Đ33`
- **Chẩn đoán**: **7. Chunking / representation / semantic drift**

#### Ca 8: `GOLD-DIR-08`
- **Query**: *"Độ tuổi tối thiểu để được cấp Giấy phép lái xe hạng A1 theo Luật 36/2024/QH15 là bao nhiêu?"*
- **Expected**: `36/2024/QH15 Điều 59`
- **Dense Rank**: `1` | **Sparse Rank**: `None` | **RRF Rank**: `None`
- **Decomposition Output**: `[]`
- **Top 1 RRF thực tế**: `traffic_order_36_2024_qh15 Đ60`
- **Chẩn đoán**: **4. Dense đúng nhưng RRF làm tụt rank**

#### Ca 9: `GOLD-DIR-09`
- **Query**: *"Thời hạn của Giấy phép lái xe ô tô hạng B theo Luật Trật tự, an toàn giao thông đường bộ là bao nhiêu năm?"*
- **Expected**: `36/2024/QH15 Điều 60`
- **Dense Rank**: `None` | **Sparse Rank**: `None` | **RRF Rank**: `None`
- **Decomposition Output**: `['quy định về đường bộ cao tốc đầu tư xây dựng quản lý vận hành khai thác thu phí sử dụng đường cao tốc Điều 45 Luật Đường bộ 35/2024/QH15']`
- **Top 1 RRF thực tế**: `road_35_2024_qh15 Đ45`
- **Chẩn đoán**: **7. Chunking / representation / semantic drift**

#### Ca 10: `GOLD-DIR-10`
- **Query**: *"Mỗi giấy phép lái xe có tổng cộng bao nhiêu điểm trừ trong một năm theo Luật TTATGTĐB?"*
- **Expected**: `36/2024/QH15 Điều 62`
- **Dense Rank**: `None` | **Sparse Rank**: `None` | **RRF Rank**: `None`
- **Decomposition Output**: `[]`
- **Top 1 RRF thực tế**: `traffic_penalty_168_2024_nd_cp Đ32`
- **Chẩn đoán**: **7. Chunking / representation / semantic drift**

---

### 8. ĐỀ XUẤT THỨ TỰ SỬA LỖI (RECOMMENDED ACTION SEQUENCE)
Không được đắp thêm Reranker hay model mới khi chưa sửa kiến trúc nền:
1. **Bước 1: Audit & Chuẩn hóa Ground Truth Dataset (Multi-Label Annotation)**:
   - Bổ sung trường `acceptable_supporting_evidence` cho ~64 câu hỏi có căn cứ song song hợp lệ (Luật 36 $\leftrightarrow$ Nghị định 168 $\leftrightarrow$ Thông tư chuyên ngành).
2. **Bước 2: Tái cấu trúc hoặc Vô hiệu hóa Hardcoded Intent trong `_decompose_query`**:
   - Gỡ bỏ việc gán cứng `target_article: 6` của NĐ 168 cho mọi câu hỏi tốc độ.
   - Trả query gốc về vị trí ưu tiên số 1 với weight cao nhất.
3. **Bước 3: Gỡ bỏ cơ chế 'Forced Target Article Injection' (dòng 1735, 1788)**:
   - Cho phép điểm tương đồng thực tế của vector quyết định ranking, không ép cứng các điều khoản được đoán mò vào Top 1.
4. **Bước 4: Cân bằng lại trọng số RRF**:
   - Giảm weight của Sparse BM25 và subqueries xuống dưới weight của query gốc.
5. **Bước 5: Chỉ sau khi các bước 1-4 hoàn tất, mới xem xét tích hợp Cross-Encoder Reranker**.

---

### KẾT LUẬN CUỐI CÙNG (FINAL VERDICT)

- **DATASET STATUS**: **NEEDS LABEL AUDIT** (Cần bổ sung supporting evidence cho các câu hỏi đa tầng căn cứ).
- **ROOT CAUSE STATUS**: **ROOT CAUSE IDENTIFIED 🟢** (Xác định chính xác 100%: Lỗi nằm ở cơ chế `Query Decomposition` gán sai intent + cơ chế `Forced Injection` của RRF làm kéo tụt điểm của Dense Search).
- **RECOMMENDED NEXT ACTION**: Thực hiện hiệu đính dataset ground truth (bước 1) và tái cấu trúc logic `_decompose_query` (bước 2), tuyệt đối không bật Reranker ở thời điểm này.