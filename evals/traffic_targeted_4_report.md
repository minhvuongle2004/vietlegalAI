# BÁO CÁO KẾT QUẢ KIỂM THỬ CÔ LẬP: TARGET ARTICLE HYDRATION
**Dự án:** VietLegal AI — Legal Domain Expansion (Phase 4A: Traffic Domain)  
**Ngày thực hiện:** 09/09/2026  
**Mục tiêu:** Kiểm chứng giải pháp **Target Article Hydration** trên 4 test cases từng FAILED ở đợt 1 (`TG-01`, `TG-02`, `TG-05`, `TG-10`) theo chỉ đạo trực tiếp của Người hướng dẫn.

---

## 1. TỔNG KẾT KẾT QUẢ KIỂM THỬ CÔ LẬP

> [!IMPORTANT]
> **KẾT QUẢ: 4/4 PASS (100.0%)**  
> Toàn bộ 4 test cases cô lập đã chuyển trạng thái từ **FAILED $\rightarrow$ PASSED**. Không có trường hợp nào bị ảo giác (hallucination) hoặc dính văn bản cũ.

| Test Case | Chủ đề vi phạm | Kết quả Đợt 1 | Kết quả Hiện tại | Context Length | TTFT | Total Latency | Điểm cốt lõi giải quyết |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **TG-01** | Xe máy vượt đèn đỏ | ❌ FAILED | **✅ PASSED** | 24,586 chars | 17.5s | 71.1s | Nạp đủ Khoản 7 (4-6tr) & Khoản 13 (trừ 4 điểm) Điều 7 NĐ 168 |
| **TG-02** | Ô tô quá tốc độ 25 km/h | ❌ FAILED | **✅ PASSED** | 27,313 chars | 14.3s | 64.7s | Nạp đủ Khoản 6 (6-8tr) & Khoản 16 (trừ 4 điểm) Điều 6 NĐ 168 |
| **TG-05** | Không có GPLX ô tô | ❌ FAILED | **✅ PASSED** | 17,982 chars | 12.5s | 43.0s | Nạp đủ Khoản 9 Điều 18 NĐ 168 (phạt 18-20 triệu) |
| **TG-10** | Ngược chiều cao tốc + Cồn | ❌ FAILED | **✅ PASSED** | 34,239 chars | 41.5s | 103.6s | Nạp Điều 6 + Điều 50: Tính đúng 48-60tr và trừ 10 điểm (cao nhất) |

---

## 2. PHÂN TÍCH KỸ THUẬT & NGUYÊN NHÂN SÂU XA ĐÃ XỬ LÝ

### 2.1. Cài đặt Target Article Hydration (Article-Aware Retrieval)
- **Cơ chế hoạt động:**
  Khi câu hỏi được phân tách thành các sub-queries có chỉ định `target_article` (ví dụ: NĐ 168 Điều 6, Điều 7, Điều 18; Luật 36 Điều 11, Điều 58), sau vòng chọn lọc cân bằng (`selected_items`), retriever sẽ kiểm tra độ dài chunk hiện tại. Nếu chunk chỉ là lát cắt ngắn (~1.200 ký tự) lấy từ Qdrant, hệ thống chủ động gọi Supabase `legal_articles` để nạp trực tiếp `full_text` (13k - 19k ký tự) vào `item["content"]`.
- **Cơ chế RAM Cache:** Tích hợp `self._full_article_cache` trong `HybridRetriever` giúp các truy vấn cùng Điều luật chỉ tốn 1 lần gọi REST API duy nhất (0ms cho các lần sau).

### 2.2. Hai phát hiện then chốt trong quá trình thực nghiệm
1. **Phát hiện Substring Collision ("mô tô" vs "ô tô"):**
   - Trong `retriever.py`, điều kiện kiểm tra `is_car = any(kw in q_lower for kw in ["ô tô", ...])` đã vô tình bắt trúng từ `"xe mô tô"` vì chuỗi con `"mô tô"` chứa `"ô tô"`.
   - Hậu quả: Mọi câu hỏi về xe mô tô (như TG-01) bị nhận định nhầm là xe ô tô, dẫn tới việc hệ thống định tuyến sang Điều 6 thay vì Điều 7.
   - Giải pháp: Áp dụng regex `re.search(r"(?<!m)ô\s*tô", q_lower)` loại trừ tiền tố "m", giúp TG-01 định tuyến chuẩn xác 100% về Điều 7.
2. **Phát hiện Pháp lý quan trọng tại Điều 50 Nghị định 168/2024/NĐ-CP (Trừ điểm nhiều hành vi):**
   - Trước đây, benchmark giả định nguyên tắc trừ điểm là "cộng dồn điểm các hành vi: 10 + 6 = 16 điểm rồi trừ hết 12 điểm trần".
   - Khi được nạp toàn văn Điều 50 từ Supabase, Gemini đã trích xuất đúng nguyên văn Điểm b Khoản 1 Điều 50 NĐ 168:  
     > *"Trường hợp cá nhân thực hiện nhiều hành vi vi phạm hành chính... nếu có từ 02 hành vi vi phạm trở lên theo quy định bị trừ điểm giấy phép lái xe thì **chỉ áp dụng trừ điểm đối với hành vi vi phạm bị trừ nhiều điểm nhất**"*.
   - Do cả 2 hành vi (ngược chiều cao tốc và cồn mức 2) đều có mức trừ cao nhất là 10 điểm, tài xế **bị trừ 10 điểm** (còn 2 điểm trên GPLX).
   - Về tiền phạt: Mức phạt cồn mức 2 của ô tô theo NĐ 168 được tăng lên **18.000.000 - 20.000.000 đồng** (thay vì 16-18 triệu của NĐ 100 cũ). Tổng mức phạt tiền cộng dồn đạt **48.000.000 đến 60.000.000 đồng**.

---

## 3. ĐO LƯỜNG HIỆU NĂNG THEO CẢNH BÁO CỦA MENTOR

| Metric | TG-01 | TG-02 | TG-05 | TG-10 | Trung bình |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Context Length (chars)** | 24,586 | 27,313 | 17,982 | 34,239 | **26,030** (~6,500 tokens) |
| **Retrieval + Hydrate Time** | 50.1s | 47.9s | 22.8s | 53.6s | **43.6s** *(chủ yếu do CPU Reranker)* |
| **Time to First Token (TTFT)**| 17.5s | 14.3s | 12.5s | 41.5s | **21.4s** |
| **Total Generation Time** | 21.0s | 16.8s | 20.2s | 50.1s | **27.0s** |
| **Tỷ lệ trúng Keywords** | 8/8 (100%) | 6/7 (85.7%) | 6/6 (100%) | 12/12 (100%) | **96.4%** |

> [!NOTE]
> Thời gian retrieval lớn (20s - 50s) hiện tại chủ yếu do mô hình Cross-Encoder Reranker (`BAAI/bge-reranker-v2-m3`) đang chạy trên CPU với batch 35 candidate pairs. Dự kiến có thể giảm đáng kể latency sau khi tối ưu reranker/device hoặc áp dụng Target Clause Extraction; mức 3–5 giây là mục tiêu cần được kiểm chứng bằng benchmark.

---

## 4. BẰNG CHỨNG CÂU TRẢ LỜI SINH RA TỪ MÔ HÌNH

### TG-01 (Xe máy vượt đèn đỏ)
```markdown
Chào bạn, căn cứ theo các quy định tại Luật Trật tự, an toàn giao thông đường bộ 2024 và Nghị định 168/2024/NĐ-CP:
1. Trường hợp không gây tai nạn:
- Mức phạt tiền: Phạt tiền từ 4.000.000 đồng đến 6.000.000 đồng (theo Điểm c Khoản 7 Điều 7 Nghị định 168/2024/NĐ-CP).
- Trừ điểm Giấy phép lái xe: Bị trừ 04 điểm trên Giấy phép lái xe (theo Điểm b Khoản 13 Điều 7 Nghị định 168/2024/NĐ-CP).
2. Trường hợp gây tai nạn giao thông:
- Phạt tiền từ 10.000.000 đồng đến 14.000.000 đồng (Điểm b Khoản 10 Điều 7) và trừ 10 điểm GPLX (Điểm d Khoản 13 Điều 7).
```

### TG-02 (Ô tô quá tốc độ 25 km/h)
```markdown
Căn cứ theo quy định tại Nghị định số 168/2024/NĐ-CP:
1. Mức phạt tiền:
- Hành vi điều khiển xe ô tô chạy quá tốc độ quy định trên 20 km/h đến 35 km/h bị phạt tiền từ 6.000.000 đồng đến 8.000.000 đồng (Điểm a Khoản 6 Điều 6).
2. Trừ điểm Giấy phép lái xe:
- Bị trừ 04 điểm Giấy phép lái xe (Điểm b Khoản 16 Điều 6 Nghị định 168/2024/NĐ-CP).
```

### TG-05 (Không có GPLX ô tô)
```markdown
Căn cứ theo Khoản 9 Điều 18 Nghị định 168/2024/NĐ-CP:
1. Trường hợp sử dụng GPLX không phù hợp với loại xe đang điều khiển:
- Phạt tiền từ 18.000.000 đồng đến 20.000.000 đồng (Điểm a Khoản 9 Điều 18).
2. Trường hợp không có Giấy phép lái xe:
- Phạt tiền từ 18.000.000 đồng đến 20.000.000 đồng (Điểm b Khoản 9 Điều 18).
```

### TG-10 (Ngược chiều cao tốc + Cồn 0,35 mg/l)
```markdown
Tài xế thực hiện 02 hành vi vi phạm theo Nghị định 168/2024/NĐ-CP:
1. Đi ngược chiều trên đường cao tốc: Phạt 30.000.000 - 40.000.000 đồng (Điểm đ Khoản 11 Điều 6).
2. Nồng độ cồn 0,35 mg/l: Phạt 18.000.000 - 20.000.000 đồng (Điểm a Khoản 9 Điều 6).
- Tổng mức phạt tiền chung: Từ 48.000.000 đồng đến 60.000.000 đồng (áp dụng nguyên tắc cộng dồn phạt tiền).
- Trừ điểm GPLX: Theo Điểm b Khoản 1 Điều 50 NĐ 168, chỉ áp dụng trừ điểm đối với hành vi bị trừ nhiều điểm nhất -> Bị trừ 10 điểm (chứ không cộng dồn thành 20 điểm).
- Số điểm còn lại: 12 - 10 = 2 điểm. Nếu không vi phạm trong 12 tháng sẽ được phục hồi đủ 12 điểm (Điều 58 Luật 36).
```

---

## 5. KẾT LUẬN & ĐỀ XUẤT BƯỚC TIẾP THEO
1. **Kết luận:** Phương pháp **Target Article Hydration** đã chứng minh hoàn toàn chuẩn xác, giải quyết triệt để vấn đề "Article-level deduplication giữ nhầm chunk ngắn" đối với các Điều luật chế tài dài. 
2. **Kế hoạch tiếp theo:**
   - Hoàn tất Bước 1: 4/4 cases cô lập đã PASS.
   - Sẵn sàng chuyển sang **Bước 2: Xử lý TG-09 (Title Mapping / Header Slug)**:
     Quy đổi slug header `traffic_penalty_168_2024_nd_cp` thành tên chuẩn tiếng Việt `"Nghị định 168/2024/NĐ-CP"` trong context header, sau đó test riêng `TG-09`.
