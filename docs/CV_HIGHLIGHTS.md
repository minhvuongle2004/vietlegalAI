# VIETLEGAL AI — ĐIỂM SÁNG DỰ ÁN DÀNH CHO CV / PORTFOLIO (CV HIGHLIGHTS)
## Dành cho vị trí: AI Engineer / GenAI Engineer / LLM Engineer

Tài liệu này tổng hợp các dòng mô tả thành tích (Resume Bullets) chuẩn định dạng **Google XYZ ("Accomplished [X] as measured by [Y], by doing [Z]")** cùng bộ câu hỏi phỏng vấn kỹ thuật chuyên sâu (*Technical Interview Talking Points*) có số liệu thực nghiệm minh chứng trung thực.

---

### I. CÁC DÒNG CV MẪU (READY-TO-USE RESUME BULLETS)

#### 📌 Lựa chọn 1: Trọng tâm Full-Stack RAG & System Architecture (Khuyên dùng)
> **AI Engineer — VietLegal AI (Production-Grade Legal RAG System)**
> - Xây dựng hệ thống Trợ lý Pháp lý RAG 2 tầng (Two-Stage Legal RAG) truy xuất trên corpus **42 văn bản quy phạm pháp luật (3.254 Điều, 7.982 Chunks)**, kết hợp **Clean Hybrid Search** (Dense BGE-M3 1024-dim + PostgreSQL GIN Full-Text Search qua Reciprocal Rank Fusion $k=60$) với mô hình **Cross-Encoder Reranker (`BAAI/bge-reranker-v2-m3`)**.
> - Tối ưu hóa suy luận Cross-Encoder trên phần cứng cục bộ bằng **CUDA FP16**, giảm độ trễ reranking **17,7 lần** (từ 10,06s xuống 569,7ms/truy vấn), nâng tỷ lệ **Hit@1 lên 40,89%** trên tập 225 câu hỏi Gold Benchmark V2 và đạt **100% Hit@3 & Hit@5** trên 25 ca Frozen Regression.
> - Thiết kế cơ chế Zero-Hallucination & Honest Abstention cho LLM (Google Gemini streaming), đạt **86,67% độ chính xác câu trả lời (52/60)**, **100% độ chuẩn xác trích dẫn (177/177 căn cứ)** và **100% tỷ lệ từ chối chuẩn xác (6/6)** đối với các truy vấn ngoài cơ sở dữ liệu.
> - Triển khai hệ thống Production hướng dịch vụ với **FastAPI async SSE Streaming**, phân quyền **Google OAuth 2.0 / Supabase**, bộ nhớ đệm Qdrant Cloud, Nginx Reverse Proxy và kiến trúc đóng gói hoàn chỉnh bằng **Docker Compose**.

---

#### 📌 Lựa chọn 2: Trọng tâm Information Retrieval, Ranking & Latency
> **GenAI / Machine Learning Engineer — VietLegal AI**
> - Thiết kế Pipeline truy xuất dữ liệu pháp quy phân cấp kết hợp bộ lọc nhận thức thời gian (**Temporal Validity Resolution**) xử lý chính xác các đạo luật hết hiệu lực hoặc chuyển tiếp hiệu lực (BLLĐ 2019, BHXH 2024, Luật TTATGT 2024).
> - Vận hành quy trình đánh giá thực nghiệm đa tầng: Tầng 1 (Retrieval & Reranking trên 225 cases Gold V2 và 25 regression cases), Tầng 2 (LLM Generation trên 60 cases phủ 10 danh mục nghiệp vụ pháp lý) với bộ đo lường tự động latency telemetry (~4,92s phản hồi end-to-end).
> - Triển khai giao diện hội thoại tương tác cao lấy cảm hứng từ ChatGPT (React/Vite), tích hợp **Interactive Citation Badges** cho phép click tra cứu trực tiếp toàn văn điều luật gốc qua **Article Inspection Modal**.

---

#### 📌 Lựa chọn 3: Phiên bản Tiếng Anh (English CV Bullets)
> **AI / GenAI Engineer — VietLegal AI (Vietnamese Legal RAG Assistant)**
> - Engineered an end-to-end production legal RAG system over **42 statutory codes and decrees (3,254 articles, 7,982 vector chunks)** utilizing **Clean Hybrid Search** (BGE-M3 Dense + PostgreSQL GIN BM25 via RRF $k=60$) and **Cross-Encoder Reranking (`BAAI/bge-reranker-v2-m3`)**.
> - Accelerated cross-encoder reranker inference via **CUDA FP16** on an RTX 3050 GPU, yielding a **17.7x latency reduction** (10.06s down to 569.7ms/query), lifting **Hit@1 to 40.89%** on 225 Gold V2 benchmark cases, and maintaining **100% Hit@3 / Hit@5** on 25 frozen regression cases.
> - Formulated a grounded prompt & verification pipeline with Google Gemini streaming, achieving **86.67% answer correctness (52/60)**, **100% legal citation fidelity (177/177 grounded citations)**, and **100% honest abstention (6/6)** on out-of-corpus queries with zero hallucinations.
> - Deployed production-ready microservices with **FastAPI asynchronous SSE streaming**, **Google OAuth 2.0 / Supabase**, Qdrant Cloud Vector Store, Nginx, and full **Docker Compose** containerization.

---

### II. BỘ SỐ LIỆU ĐỊNH LƯỢNG ĐÃ ĐƯỢC THẨM ĐỊNH (VERIFIED BENCHMARK DATA)

*Lưu ý ứng viên: Chỉ sử dụng các số liệu đã được kiểm chứng dưới đây trong buổi phỏng vấn, tuyệt đối không nói quá "100% accuracy overall" hoặc "không bao giờ bịa đặt trong mọi trường hợp".*

| Metric | Giá trị thực tế đạt được | Phạm vi tập kiểm thử tương ứng |
| :--- | :---: | :--- |
| **Quy mô Corpus** | **42 Luật/Nghị định · 3.254 Điều · 7.982 Chunks** | Số hóa từ nguồn cổng thông tin Chính phủ |
| **Gold V2 Retrieval Benchmark** | **Hit@1 = 40.89%** (92/225 cases)<br>**Hit@5 = 58.22%** (131/225 cases) | Tập 225 câu hỏi chuẩn hóa đa ngành pháp luật |
| **Clean Hybrid Coverage** | **Hit@5 = 58.67%** (132/225 cases) | Mở rộng ứng viên hiệu quả hơn Dense-only (+4.0%) |
| **Frozen Regression Stability** | **Hit@3 = 100% · Hit@5 = 100%** | Tập 25 câu hỏi P0.5/P3 mảng giao thông bất biến |
| **Tốc độ GPU vs CPU Reranker** | **569.7 ms vs 10,061.6 ms (Nhanh hơn 17.7x)** | Pool 10 ứng viên, FP16 CUDA RTX 3050 vs CPU |
| **Độ đúng câu trả lời (Correctness)** | **86.67%** (52/60 cases) | Tập 60 cases Step 3.0 phủ 10 danh mục nghiệp vụ |
| **Độ chuẩn xác trích dẫn (Citations)** | **100.00%** (177/177 trích dẫn) | 100% căn cứ đều có trong context và đúng văn bản |
| **Tỷ lệ bịa đặt (Hallucination)** | **0.00%** (0/60 cases) | Không phát hiện số liệu tự chế hay điều luật ảo |
| **Từ chối ngoài phạm vi (Abstention)**| **100.00%** (6/6 cases Category J) | Từ chối trung thực khi câu hỏi ngoài cơ sở dữ liệu |
| **Độ trễ toàn trình End-to-End** | **~4.92 giây / câu hỏi** | Retrieval (1.7s) + Rerank (0.6s) + LLM Gen (2.6s) |
| **Backend Stability & Resilience** | **8/8 bài kiểm tra PASS 100%** | Liveness, Readiness, Schema Validation, Auth, 429 |

---

### III. BỘ CÂU HỎI TRẢ LỜI PHỎNG VẤN CHUYÊN SÂU (INTERVIEW TALKING POINTS)

#### 1. Tại sao cần kết hợp Dense + Sparse (Hybrid Search) thay vì chỉ dùng Vector Search?
> *"Trong lĩnh vực pháp lý, người dùng thường hỏi chính xác mã số hiệu ('Nghị định 168', 'Điều 328'), tên tiền phạt hoặc từ ngữ pháp lý đặc thù. Vector Search (Dense Embedding) tuy nắm bắt ngữ nghĩa tổng thể rất tốt nhưng hay bỏ sót các từ khóa số hiệu hiếm gặp. Ngược lại, Sparse (BM25 trên PostgreSQL) bắt chính xác 100% từ khóa số hiệu nhưng yếu về từ đồng nghĩa. Chúng tôi dùng RRF (Reciprocal Rank Fusion) với $k=60$, trọng số $w_{\text{dense}}=1.0, w_{\text{sparse}}=0.10$ để tận dụng sức mạnh mở rộng ứng viên của Sparse mà không làm loãng độ chính xác của Dense."*

#### 2. Vai trò của Cross-Encoder Reranker là gì và bạn giải quyết vấn đề độ trễ như thế nào?
> *"Bi-Encoder (BGE-M3) mã hóa câu hỏi và văn bản độc lập nên tốc độ truy xuất rất nhanh qua Vector Index, nhưng không có sự tương tác giữa từng token của câu hỏi với văn bản. Cross-Encoder (`bge-reranker-v2-m3`) ghép chung `(query, document)` qua toàn bộ các lớp Transformer Self-Attention nên khả năng nhận định mức độ phù hợp vượt trội.*
> *Tuy nhiên, Cross-Encoder trên CPU rất chậm (~10,06 giây cho 10 chunks). Tôi đã tối ưu bằng cách nạp mô hình vào GPU với kiểu dữ liệu bán chính xác FP16 (Half Precision), kéo độ trễ xuống chỉ còn ~569,7 ms (nhanh gấp 17,7 lần). Nhờ đó, Hit@1 được đẩy từ 32,44% lên 40,89% trên 225 câu hỏi thực nghiệm mà không làm tắc nghẽn trải nghiệm đàm thoại."*

#### 3. Làm thế nào để hệ thống kiểm soát hiện tượng Hallucination và xử lý câu hỏi ngoài dữ liệu?
> *"Chúng tôi áp dụng chiến lược 'Grounded Context Enforcement':*
> 1. *System Prompt đặt điều kiện tiên quyết: LLM chỉ được kết luận dựa trên các trích đoạn văn bản được cung cấp trong ngữ cảnh Top-5 Reranked.*
> 2. *Ràng buộc cấu trúc trích dẫn: Mọi điều khẳng định phải gắn liền với 'Căn cứ: [Văn bản] [Điều khoản]'.*
> 3. *Chính sách từ chối trung thực (Honest Abstention): Nếu ngữ cảnh không có thông tin hoặc câu hỏi thuộc lĩnh vực ngoài cơ sở dữ liệu (ví dụ: hàng hải quốc tế, luật không gian), mô hình được lập trình trả lời từ chối lịch sự thay vì cố gắng suy diễn. Trong bài kiểm thử Step 3.0, 6/6 trường hợp ngoài corpus đều được từ chối chuẩn xác."*

#### 4. Hệ thống xử lý bài toán hiệu lực thời gian (Temporal Awareness) như thế nào?
> *"Pháp luật Việt Nam thường xuyên sửa đổi, thay thế (ví dụ: Luật TTATGT 2024 thay thế Luật GTĐB 2008 từ 01/01/2025; BHXH 2024 có hiệu lực từ 01/07/2025). Hệ thống có trường `as_of_date` và `LEGAL_DOCUMENT_TEMPORAL_REGISTRY` để xác định hiệu lực tại thời điểm người dùng quan tâm, tự động lọc các văn bản chưa có hiệu lực hoặc đã bị bãi bỏ tại mốc thời gian đó."*
