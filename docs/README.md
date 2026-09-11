# VIETLEGAL AI — HỆ THỐNG TÀI LIỆU & BÁO CÁO NGHIỆM THU (DOCUMENTATION INDEX)

Tài liệu này đóng vai trò là danh mục tra cứu trung tâm (Master Index) cho toàn bộ các thiết kế kỹ thuật, kế hoạch triển khai và báo cáo thực nghiệm chất lượng của dự án **VietLegal AI**.

---

## 🏛️ I. Kiến trúc & Thiết kế Kỹ thuật (`docs/architecture/`)

| Tài liệu | Mô tả tóm tắt |
| :--- | :--- |
| 🌟 [CV_HIGHLIGHTS.md](file:///d:/Đi%20làm/VietLegal%20AI/docs/CV_HIGHLIGHTS.md) | **Tổng hợp điểm sáng CV**: Resume bullets chuẩn Google XYZ, số liệu thực nghiệm đã xác minh và bộ câu hỏi phỏng vấn kỹ thuật. |
| 🏗️ [ARCHITECTURE.md](file:///d:/Đi%20làm/VietLegal%20AI/docs/ARCHITECTURE.md) | **Bản tả kiến trúc kỹ thuật chuẩn**: Sơ đồ Mermaid tuần tự (Request Flow, Retrieval, Reranking, SSE, Citation Modal, Temporal Resolution). |
| 🚀 [DEPLOYMENT_GUIDE.md](file:///d:/Đi%20làm/VietLegal%20AI/docs/DEPLOYMENT_GUIDE.md) | **Hướng dẫn triển khai & Vận hành (Runbook)**: Chi tiết cách deploy Frontend Vercel, Backend Docker và cách bật server hằng ngày cho người dùng truy cập trực tiếp. |
| 📘 [SYSTEM_DESIGN.md](file:///d:/Đi%20làm/VietLegal%20AI/docs/architecture/SYSTEM_DESIGN.md) | Thiết kế kiến trúc tổng thể của VietLegal AI: Multi-tier RAG, Vector Search, Sparse FTS, Cross-Encoder Reranker và API Gateway. |
| 📊 [LEGAL_DATA_PIPELINE.md](file:///d:/Đi%20làm/VietLegal%20AI/docs/architecture/LEGAL_DATA_PIPELINE.md) | Quy trình xử lý dữ liệu văn bản pháp quy từ Raw HTML/PDF, Parsing Điều/Khoản, Metadata Registry, Chunking đến Ingestion. |
| 🚀 [PRODUCTION_DEPLOYMENT_PLAN.md](file:///d:/Đi%20làm/VietLegal%20AI/docs/architecture/PRODUCTION_DEPLOYMENT_PLAN.md) | Kế hoạch triển khai môi trường Production (Docker, Nginx Reverse Proxy, SSL, FastAPI, Vue/React Chatbot). |
| ☁️ [PHASE_3_CLOUD_DEPLOYMENT_PLAN.md](file:///d:/Đi%20làm/VietLegal%20AI/docs/architecture/PHASE_3_CLOUD_DEPLOYMENT_PLAN.md) | Kế hoạch tích hợp và đồng bộ hóa đám mây (Qdrant Cloud, Supabase PostgreSQL, CI/CD). |

---

## 🧠 II. Báo cáo Tầng 2: Chất lượng Sinh Câu trả lời LLM (`docs/reports/generation/`)

| Báo cáo Nghiệm thu | Trạng thái | Tóm tắt kết quả chính |
| :--- | :---: | :--- |
| ⭐ [GENERATION_QUALITY_EVALUATION_REPORT.md](file:///d:/Đi%20làm/VietLegal%20AI/docs/reports/generation/GENERATION_QUALITY_EVALUATION_REPORT.md) | **PASS 🟢** | Nghiệm thu Step 3.0 trên 60 test cases phủ 10 danh mục: **Answer Correctness đạt 86.67%**, **Citation Accuracy 100%**, **Hallucination = 0.00%**, **Từ chối ngoài phạm vi (Abstention) = 100%**. |
| 🛡️ [PRODUCTION_POLISH_REAL_WORLD_QA_REPORT.md](file:///d:/Đi%20làm/VietLegal%20AI/docs/reports/qa/PRODUCTION_POLISH_REAL_WORLD_QA_REPORT.md) | **PASS 🟢** | Nghiệm thu Step 3.1 kiểm thử 16 câu hỏi người dân thực tế: Liveness/Readiness 8/8 test PASS, vá lỗi ngắt kết nối SSE, kiểm chứng Legal Disclaimer & Citation UX. |
| 📋 [PUBLIC_BASELINE_VERIFICATION.md](file:///d:/Đi%20làm/VietLegal%20AI/docs/reports/qa/PUBLIC_BASELINE_VERIFICATION.md) | **BASELINE READY 🟢** | Xác minh Baseline công khai: Git clean, Frontend build pass, Backend liveness/readiness healthy, Docker healthy, ngrok tunnel live. |
| ✨ [UI_UX_HR_DEMO_POLISH_REPORT.md](file:///d:/Đi%20làm/VietLegal%20AI/docs/reports/qa/UI_UX_HR_DEMO_POLISH_REPORT.md) | **HR DEMO READY 🟢** | Tối ưu trải nghiệm HR Demo & Backend Offline Fallback: Hero branding, 4 câu hỏi mẫu 1-click, Offline Fallback Card thân thiện, Mobile Drawer 390px. |

---

## 🎯 III. Báo cáo Tầng 1: Cross-Encoder Reranker (`docs/reports/reranker/`)

| Báo cáo Nghiệm thu | Trạng thái | Tóm tắt kết quả chính |
| :--- | :---: | :--- |
| ⭐ [RERANKER_GOLD_EVALUATION_REPORT.md](file:///d:/Đi%20làm/VietLegal%20AI/docs/reports/reranker/RERANKER_GOLD_EVALUATION_REPORT.md) | **PASS 🟢** | Nghiệm thu Step 2.2 mô hình `BAAI/bge-reranker-v2-m3` FP16 CUDA RTX 3050 (~569.7 ms/query): **Hit@1 đạt 40.89%** (+2.67%), **Hit@5 đạt 58.22%**, **Hit@3 trên 25 Frozen Cases đạt 100%**. |
| 🧪 [RRF_WEIGHT_EXPERIMENT_REPORT.md](file:///d:/Đi%20làm/VietLegal%20AI/docs/reports/reranker/RRF_WEIGHT_EXPERIMENT_REPORT.md) | Hoàn thành | Thử nghiệm các trọng số RRF giữa Dense và Sparse để tìm ra điểm cân bằng tối ưu ($w_{\text{dense}}=1.0, w_{\text{sparse}}=0.10, k=60$). |

---

## 🔍 IV. Báo cáo Tầng 1: Retrieval — Dense, Sparse & Clean Hybrid (`docs/reports/retrieval/`)

| Báo cáo Nghiệm thu | Nội dung chi tiết |
| :--- | :--- |
| ⭐ [CLEAN_HYBRID_QUERY_FLOW_REPORT.md](file:///d:/Đi%20làm/VietLegal%20AI/docs/reports/retrieval/CLEAN_HYBRID_QUERY_FLOW_REPORT.md) | Báo cáo Step 2.1 đóng luồng Clean Hybrid: Tắt triệt để Query Decomposition và Forced Target Injection, bảo toàn tính minh bạch production. |
| 📋 [GOLD_RETRIEVAL_V2_COMPARISON_REPORT.md](file:///d:/Đi%20làm/VietLegal%20AI/docs/reports/retrieval/GOLD_RETRIEVAL_V2_COMPARISON_REPORT.md) | Đối sánh hiệu năng Dense vs Sparse trên tập 225 câu hỏi Gold Benchmark V2. |
| 🏷️ [GOLD_225_LABEL_REVISION_REPORT.md](file:///d:/Đi%20làm/VietLegal%20AI/docs/reports/retrieval/GOLD_225_LABEL_REVISION_REPORT.md) | Rà soát và chuẩn hóa bộ nhãn căn cứ pháp lý cho 225 câu hỏi Gold Benchmark. |
| 📊 [GOLD_RETRIEVAL_EVALUATION_REPORT.md](file:///d:/Đi%20làm/VietLegal%20AI/docs/reports/retrieval/GOLD_RETRIEVAL_EVALUATION_REPORT.md) | Đánh giá tổng quát năng lực truy xuất ban đầu trên tập Gold Dataset. |
| 🔎 [SPARSE_225_FULL_GOLD_EVALUATION.md](file:///d:/Đi%20làm/VietLegal%20AI/docs/reports/retrieval/SPARSE_225_FULL_GOLD_EVALUATION.md) | Khảo sát chi tiết PostgreSQL Full-Text Search trên toàn bộ 225 test cases. |
| 🛠️ [SPARSE_RETRIEVAL_FIX_VALIDATION.md](file:///d:/Đi%20làm/VietLegal%20AI/docs/reports/retrieval/SPARSE_RETRIEVAL_FIX_VALIDATION.md) | Kiểm chứng bản vá sửa lỗi đồng bộ hóa từ khóa và cấu hình `simple` / `vietnamese` dictionary. |
| 🩺 [TIER1_5_RETRIEVAL_FAILURE_DIAGNOSIS.md](file:///d:/Đi%20làm/VietLegal%20AI/docs/reports/retrieval/TIER1_5_RETRIEVAL_FAILURE_DIAGNOSIS.md) | Phân tích căn nguyên (Root Cause Analysis) các trường hợp truy xuất thất bại trong Tầng 1.5. |
| 🔬 [TIER1_6_GOLD_DATASET_SPARSE_VALIDATION.md](file:///d:/Đi%20làm/VietLegal%20AI/docs/reports/retrieval/TIER1_6_GOLD_DATASET_SPARSE_VALIDATION.md) | Đánh giá kiểm chứng độc lập tập Sparse Dataset Tầng 1.6. |
| 📈 [BENCHMARK_REPORT.md](file:///d:/Đi%20làm/VietLegal%20AI/docs/reports/retrieval/BENCHMARK_REPORT.md) | Báo cáo tổng kết các mốc benchmark thử nghiệm retrieval. |
| 🛡️ [REGRESSION_INVESTIGATION_REPORT.md](file:///d:/Đi%20làm/VietLegal%20AI/docs/reports/retrieval/REGRESSION_INVESTIGATION_REPORT.md) | Điều tra và cô lập các điểm hồi quy (regression) khi thay đổi trọng số truy xuất. |

---

## ⚙️ V. Báo cáo Ingestion & Cập nhật Dữ liệu (`docs/reports/ingestion/`)

| Báo cáo | Mục tiêu |
| :--- | :--- |
| 📝 [STEP2_PARSING_VALIDATION_REPORT.md](file:///d:/Đi%20làm/VietLegal%20AI/docs/reports/ingestion/STEP2_PARSING_VALIDATION_REPORT.md) | Kiểm thử parser trích xuất Điều/Khoản và bảo toàn cấu trúc văn bản pháp luật. |
| 📦 [STEP3_STAGING_INGESTION_AND_REGRESSION_REPORT.md](file:///d:/Đi%20làm/VietLegal%20AI/docs/reports/ingestion/STEP3_STAGING_INGESTION_AND_REGRESSION_REPORT.md) | Nạp dữ liệu vào môi trường Staging và kiểm tra regression trên tập test case kiểm định. |
| 🚀 [STEP4_PRODUCTION_PROMOTION_REPORT.md](file:///d:/Đi%20làm/VietLegal%20AI/docs/reports/ingestion/STEP4_PRODUCTION_PROMOTION_REPORT.md) | Đẩy dữ liệu chính thức vào Production Vector Database (Qdrant) và PostgreSQL FTS. |

---

## 📜 VI. Báo cáo Lịch sử Lĩnh vực Giao thông (`docs/reports/historical_traffic/`)

| Báo cáo | Tóm tắt |
| :--- | :--- |
| 🚦 [PHASE_3_COMPLETION_REPORT.md](file:///d:/Đi%20làm/VietLegal%20AI/docs/reports/historical_traffic/PHASE_3_COMPLETION_REPORT.md) | Nghiệm thu hoàn thành Giai đoạn 3 chuyên sâu mảng Luật Giao thông đường bộ. |
| 🎯 [TRAFFIC_BENCHMARK_25_CASES_REPORT.md](file:///d:/Đi%20làm/VietLegal%20AI/docs/reports/historical_traffic/TRAFFIC_BENCHMARK_25_CASES_REPORT.md) | Bộ benchmark 25 câu hỏi chuyên sâu xử lý vi phạm giao thông (P0.5 / P3). |
| 🔍 [TRAFFIC_P0_BATCH_INSPECTION_REPORT.md](file:///d:/Đi%20làm/VietLegal%20AI/docs/reports/historical_traffic/TRAFFIC_P0_BATCH_INSPECTION_REPORT.md) | Kiểm tra dữ liệu đợt P0. |
| 🔎 [TRAFFIC_P0.5_BATCH_INSPECTION_REPORT.md](file:///d:/Đi%20làm/VietLegal%20AI/docs/reports/historical_traffic/TRAFFIC_P0.5_BATCH_INSPECTION_REPORT.md) | Kiểm tra dữ liệu đợt P0.5. |
| 📑 [TRAFFIC_P0.5_METADATA_AND_DEPENDENCY_PLAN.md](file:///d:/Đi%20làm/VietLegal%20AI/docs/reports/historical_traffic/TRAFFIC_P0.5_METADATA_AND_DEPENDENCY_PLAN.md) | Kế hoạch cây quan hệ phụ thuộc văn bản và metadata. |
| 📥 [TRAFFIC_P1_STEP1_RAW_ACQUISITION_REPORT.md](file:///d:/Đi%20làm/VietLegal%20AI/docs/reports/historical_traffic/TRAFFIC_P1_STEP1_RAW_ACQUISITION_REPORT.md) | Báo cáo thu thập văn bản thô đợt P1.1. |
| 📥 [TRAFFIC_P1_2_RAW_ACQUISITION_REPORT.md](file:///d:/Đi%20làm/VietLegal%20AI/docs/reports/historical_traffic/TRAFFIC_P1_2_RAW_ACQUISITION_REPORT.md) | Báo cáo thu thập văn bản thô đợt P1.2. |
| 🗺️ [TRAFFIC_P1_LEGAL_COVERAGE_EXPANSION_DISCOVERY.md](file:///d:/Đi%20làm/VietLegal%20AI/docs/reports/historical_traffic/TRAFFIC_P1_LEGAL_COVERAGE_EXPANSION_DISCOVERY.md) | Khảo sát mở rộng phạm vi pháp lý mảng giao thông. |
| 🏁 [TRAFFIC_P3_FINAL_CLOSURE_REPORT.md](file:///d:/Đi%20làm/VietLegal%20AI/docs/reports/historical_traffic/TRAFFIC_P3_FINAL_CLOSURE_REPORT.md) | Đóng gói nghiệm thu hoàn tất Traffic Benchmark P3. |
| 🚶 [TRAFFIC_P1_2_COMPLETION_WALKTHROUGH.md](file:///d:/Đi%20làm/VietLegal%20AI/docs/reports/historical_traffic/TRAFFIC_P1_2_COMPLETION_WALKTHROUGH.md) | Ghi nhận chi tiết kết quả hoàn thành Traffic P1.2. |
