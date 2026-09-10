# VIETLEGAL AI — BẢN TẢ KIẾN TRÚC HỆ THỐNG (SYSTEM ARCHITECTURE SPECIFICATION)

Tài liệu này mô tả chi tiết toàn bộ thiết kế kỹ thuật, luồng xử lý dữ liệu và cơ chế vận hành nội tại của hệ thống **VietLegal AI (Production-Grade Legal RAG)**.

---

## 🏗️ 1. Kiến Trúc Tổng Thể (High-Level Architecture)

```mermaid
graph TB
    subgraph Client ["Frontend Layer (React + Vite)"]
        UI["ChatGPT Dark UI / Mobile Responsive"]
        AuthModal["Login & Profile Modal"]
        ArtModal["Article Inspection Modal"]
    end

    subgraph Gateway ["Reverse Proxy & Security Layer"]
        Nginx["Nginx Reverse Proxy (Rate Limit / SSL / CORS)"]
    end

    subgraph AppServer ["Backend Core (FastAPI Asynchronous)"]
        ChatAPI["/api/v1/chat/completions (SSE Stream)"]
        HealthAPI["/health (Liveness) & /api/v1/health (Readiness)"]
        AuthMid["Supabase JWT Auth & Guest Counter"]
    end

    subgraph TwoStageRAG ["Two-Stage Legal Retrieval & Reasoning"]
        subgraph Stage1 ["Stage 1: Clean Hybrid Retrieval"]
            DenseRet["Dense Vector Search\n(BGE-M3 1024-dim Cosine)"]
            SparseRet["Sparse FTS\n(PostgreSQL GIN tsvector 'simple')"]
            RRF["Reciprocal Rank Fusion\n(k=60, w_dense=1.0, w_sparse=0.10)"]
        end

        subgraph Stage2 ["Stage 2: Cross-Encoder Reranking"]
            Reranker["BAAI/bge-reranker-v2-m3\n(CUDA FP16 on RTX 3050)"]
        end

        subgraph Generator ["Stage 3: Grounded Generation"]
            PromptEng["Legal Grounded Prompting\n(Zero-Hallucination Constraints)"]
            LLM["Google Gemini (Streaming API)"]
        end
    end

    subgraph Storage ["Persistent & Cloud Storage Layer"]
        Qdrant["Qdrant Cloud\n(7,982 points / 1024-dim)"]
        Supabase["Supabase PostgreSQL\n(Legal Docs, Auth, Chat History)"]
    end

    UI -->|HTTPS / WSS| Nginx
    Nginx -->|Proxy Pass| AppServer
    ChatAPI --> Stage1
    DenseRet <-->|gRPC / REST| Qdrant
    SparseRet <-->|SQL / BM25| Supabase
    DenseRet --> RRF
    SparseRet --> RRF
    RRF -->|Top 10 Candidates| Stage2
    Reranker -->|Top 5 Context Chunks| Generator
    Generator -->|Token Stream SSE| ChatAPI
    ArtModal <-->|GET /api/v1/legal/articles| Supabase
    AuthMid <-->|Validate JWT| Supabase
```

---

## 🔄 2. Chi Tiết Các Luồng Xử Lý (Core Request Flows)

### A. Luồng Đàm Thoại & Sinh Câu Trả Lời (Chat Completion & Streaming Flow)

```mermaid
sequenceDiagram
    autonumber
    actor User as Người Dùng
    participant FE as React Frontend
    participant API as FastAPI Backend
    participant Ret as Hybrid Retriever
    participant RR as Cross-Encoder Reranker
    participant Gen as Gemini LLM
    participant DB as Supabase DB

    User->>FE: Gõ câu hỏi & bấm Gửi
    FE->>API: POST /api/v1/chat/completions (query, as_of_date, use_reranker)
    API->>DB: Lưu tin nhắn User vào bảng `messages`
    
    API->>Ret: retrieve(query, top_k=10, as_of_date)
    par Song song truy xuất
        Ret->>Qdrant: Dense Search (BGE-M3 Embeddings)
        Ret->>DB: Sparse Search (PostgreSQL GIN BM25)
    end
    Ret->>Ret: Trộn kết quả qua RRF (k=60) -> Top 10 ứng viên
    
    alt Có bật Reranker (Chuyên sâu)
        API->>RR: rerank(query, 10 candidates, top_k=5)
        RR-->>API: Top 5 chunks chuẩn xác nhất (CUDA FP16: ~600ms)
    else Chế độ Tiêu chuẩn (Fast)
        Ret-->>API: Cắt lấy Top 5 chunks từ RRF
    end

    API-->>FE: SSE event: 'citations' (Danh sách căn cứ đính kèm)
    FE->>FE: Render Citation Pills trên giao diện
    
    API->>Gen: generate_answer_stream(query, top5_context)
    loop Đọc luồng token thời gian thực
        Gen-->>API: yield token
        API-->>FE: SSE event: 'token' {token: "..."}
        FE->>FE: Nối chuỗi & cuộn xuống mượt mà
    end

    API->>DB: Lưu câu trả lời Assistant vào bảng `messages`
    API-->>FE: SSE event: 'done' {status: "completed", latency_ms: ...}
    FE->>FE: Tắt typing indicator (isStreaming = false)
```

---

### B. Luồng Nhận Thức Thời Gian & Sửa Đổi Pháp Luật (Temporal & Version Resolution Flow)

```mermaid
graph TD
    Q[Câu hỏi người dùng + as_of_date] --> CheckDate{Có chỉ định as_of_date?}
    CheckDate -->|Có| UseSpecified[Sử dụng mốc as_of_date yêu cầu]
    CheckDate -->|Không| InferDate[Auto-infer: Mặc định thời điểm hiện tại]
    
    UseSpecified --> RegistryCheck[Tra cứu LEGAL_DOCUMENT_TEMPORAL_REGISTRY]
    InferDate --> RegistryCheck
    
    RegistryCheck --> FilterSuperseded[Loại bỏ văn bản đã hết hiệu lực trước as_of_date]
    RegistryCheck --> FilterPending[Loại bỏ văn bản chưa có hiệu lực tại as_of_date]
    
    FilterSuperseded --> ActivePool[Danh mục văn bản đang có hiệu lực áp dụng]
    FilterPending --> ActivePool
    
    ActivePool --> HybridSearch[Chạy Hybrid Search có lọc theo metadata hiệu lực]
```

*Ví dụ điển hình*:
- Với câu hỏi về quy định xử phạt giao thông đường bộ trước ngày **01/01/2025**: Hệ thống tra cứu theo **Nghị định 100/2019/NĐ-CP**.
- Với câu hỏi áp dụng từ ngày **01/01/2025 trở đi**: Hệ thống tự động chuyển tiếp sang **Luật Trật tự, an toàn giao thông đường bộ 2024** và **Nghị định 168/2024/NĐ-CP**.

---

### C. Luồng Tra Cứu Toàn Văn Điều Luật Gốc (Interactive Citation Modal Flow)

```mermaid
sequenceDiagram
    autonumber
    actor User as Người Dùng
    participant FE as React UI
    participant Modal as ArticleModal
    participant API as FastAPI (/api/v1/legal)
    participant DB as Supabase DB

    User->>FE: Click vào Citation Pill (Ví dụ: "Luật TTATGT Điều 11")
    FE->>Modal: openArticleModal(article_number=11, doc_id="ttatgt_36_2024")
    Modal->>API: GET /api/v1/legal/articles?doc_id=...&article_number=11
    API->>DB: SELECT title, content, chapter FROM legal_articles WHERE ...
    DB-->>API: Toàn văn điều luật & metadata phân cấp
    API-->>Modal: JSON payload (article_title, full_content, lineage)
    Modal->>Modal: Render toàn văn điều luật, làm nổi bật từ khóa liên quan
    Modal-->>User: Hiển thị giao diện đọc chuyên sâu (không reload trang)
```

---

### D. Cơ Chế Chống Treo Stream & Phục Hồi Lỗi (Graceful Degradation & SSE Resilience)

1. **Client Disconnect (`request.is_disconnected()`)**:
   - Khi người dùng đóng tab hoặc chuyển trang giữa lúc mô hình đang sinh câu trả lời, backend phát hiện tín hiệu ngắt kết nối và lập tức hủy bỏ luồng sinh (`abort generation`), tiết kiệm tài nguyên GPU và chi phí token.
2. **Upstream Exception Handling**:
   - Nếu Gemini API gặp sự cố giới hạn hạn mức (HTTP 429 Quota) hoặc mạng gián đoạn, backend bắt giữ ngoại lệ, gửi token cảnh báo thân thiện đến giao diện người dùng và phát sự kiện `done` (kèm trạng thái lỗi) thay vì ngắt luồng đột ngột.
   - Frontend luôn bảo đảm tắt cờ `isStreaming = false` ngay khi bộ đọc `reader.read()` kết thúc, loại bỏ hoàn toàn hiện tượng con trỏ nhấp nháy treo vô hạn.

---

## 🗄️ 3. Thiết Kế Cơ Sở Dữ Liệu & Chỉ Mục (Database & Index Schema)

### A. Qdrant Cloud Collection (`vietlegal_articles`)
- **Số lượng vectors**: **7.982 điểm** (Points)
- **Kích thước vector**: **1024 chiều** (Cosine Distance)
- **Mô hình trích xuất đặc trưng**: `BAAI/bge-m3` (Multilingual / Vietnamese Dense Embedding)
- **Payload Schema**:
  ```json
  {
    "doc_id": "ttatgt_36_2024_qh15",
    "doc_title": "Luật Trật tự, an toàn giao thông đường bộ 2024",
    "article_number": 11,
    "article_title": "Chấp hành báo hiệu đường bộ",
    "chapter": "Chương II: Quy tắc giao thông đường bộ",
    "context_header": "Luật Trật tự, an toàn giao thông đường bộ 2024 > Chương II > Điều 11",
    "effective_date": "2025-01-01",
    "status": "CURRENT"
  }
  ```

### B. PostgreSQL Supabase Table (`legal_articles`)
- **Bảng**: `legal_articles`
- **Chỉ mục tìm kiếm toàn văn**: GIN Index trên cột tính toán `tsvector`:
  ```sql
  CREATE INDEX idx_legal_articles_fts ON legal_articles 
  USING GIN (to_tsvector('simple', title || ' ' || content));
  ```
- **Từ điển tìm kiếm**: Sử dụng cấu hình từ điển `simple` để giữ nguyên vẹn các ký tự số hiệu, dấu gạch chéo (`168/2024/NĐ-CP`) và tiếng Việt có dấu.
