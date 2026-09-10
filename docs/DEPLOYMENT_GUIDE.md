# VIETLEGAL AI — HƯỚNG DẪN TRIỂN KHAI & VẬN HÀNH (DEPLOYMENT & OPERATIONAL RUNBOOK)

> **Mục tiêu tài liệu**: Hướng dẫn chi tiết từng bước cách deploy Frontend (Vercel), Backend (Docker), và quy trình khởi động hệ thống hàng ngày để người dùng ngoài internet có thể truy cập link Vercel và trò chuyện trực tiếp với chatbot AI.

---

## 🗺️ TỔNG QUAN KIẾN TRÚC TRIỂN KHAI (HYBRID CLOUD ARCHITECTURE)

Hệ thống VietLegal AI được thiết kế theo mô hình lai (Hybrid Cloud Deployment) nhằm tối ưu chi phí ($0) nhưng vẫn đảm bảo trải nghiệm Production mượt mà:

```
[ Người Dùng / Nhà Tuyển Dụng ]
             │
             ▼ HTTPS (Toàn cầu)
   ┌──────────────────────────────────────────────┐
   │        FRONTEND: Vercel Global Edge          │
   │    https://vietlegal-ai-orcin.vercel.app     │
   └──────────────────────────────────────────────┘
             │
             ▼ SSE Streaming (HTTPS)
   ┌──────────────────────────────────────────────┐
   │        REVERSE PROXY / SECURE TUNNEL         │
   │  https://sylphlike-rufus-malonyl.ngrok-free.dev│
   │            (hoặc Cloudflare Tunnel)          │
   └──────────────────────────────────────────────┘
             │
             ▼ Chuyển tiếp về Cổng 8888
   ┌──────────────────────────────────────────────┐
   │     MÁY HOST CỤC BỘ (DOCKER ENVIRONMENT)    │
   │                                              │
   │  ┌────────────────────────────────────────┐  │
   │  │ vietlegal_backend (FastAPI Port 8888)  │  │
   │  │ • PyTorch + BGE-M3 (Embedding)        │  │
   │  │ • BAAI/bge-reranker-v2-m3 (Reranker)   │  │
   │  │ • SSE Streaming & SlowAPI Limiter     │  │
   │  └───────────────────┬────────────────────┘  │
   │                      │                       │
   │  ┌───────────────────┴────────────────────┐  │
   │  │ vietlegal_qdrant (Vector DB Port 6333) │  │
   │  └────────────────────────────────────────┘  │
   └──────────────────────┬───────────────────────┘
                          │
            ┌─────────────┴─────────────┐
            ▼                           ▼
 ┌──────────────────────┐   ┌──────────────────────┐
 │    SUPABASE CLOUD    │   │  GOOGLE GEMINI API   │
 │ PostgreSQL Full-Text │   │ gemini-1.5-flash-lite│
 │ Auth, Conversations  │   │ Sinh câu trả lời RAG │
 └──────────────────────┘   └──────────────────────┘
```

---

## ⚡ PHẦN 1: QUY TRÌNH KHỞI ĐỘNG HÀNG NGÀY ĐỂ DEMO (DAILY RUNBOOK)

Khi anh muốn gửi link Vercel cho bạn bè hoặc nhà tuyển dụng hỏi trực tiếp, anh chỉ cần thực hiện **3 bước trong 30 giây**:

### Bước 1: Khởi động Docker Desktop
- Mở ứng dụng **Docker Desktop** trên Windows.
- Đảm bảo biểu tượng cá voi ở góc dưới thanh Taskbar chuyển sang màu xanh lá cây (*Docker Engine running*).

### Bước 2: Bật Backend Docker
Mở PowerShell tại thư mục dự án (`d:\Đi làm\VietLegal AI`) và chạy:
```powershell
docker compose up -d backend
```
> **Kiểm tra nhanh**: Gõ `curl http://localhost:8888/health` thấy trả về `{"status":"alive"}` là Backend đã sẵn sàng.

### Bước 3: Mở Tunnel công khai (Ngrok)
Mở một cửa sổ Terminal mới và chạy:
```powershell
ngrok http 8888 --domain=sylphlike-rufus-malonyl.ngrok-free.dev
```

### 🎉 HOÀN TẤT!
Lúc này, bất kỳ ai trên thế giới đều có thể truy cập vào link:
👉 **https://vietlegal-ai-orcin.vercel.app**
và hỏi đáp pháp lý trực tiếp với đầy đủ trích dẫn điều luật theo thời gian thực!

---

## 🌐 PHẦN 2: HƯỚNG DẪN DEPLOY FRONTEND LÊN VERCEL

Frontend được viết bằng React 18 + Vite và được tự động build & deploy thông qua GitHub Webhook của Vercel.

### 1. Cấu hình dự án trên Vercel Dashboard
1. Truy cập vào [Vercel Dashboard](https://vercel.com/dashboard) và đăng nhập bằng tài khoản GitHub.
2. Bấm **Add New...** -> **Project** -> Chọn repository `minhvuongle2004/vietlegalAI`.
3. Tại phần **Configure Project**:
   - **Framework Preset**: Chọn `Vite`.
   - **Root Directory**: Bấm `Edit` và chọn thư mục `frontend` *(Rất quan trọng, không để trống)*.
   - **Build Command**: `npm run build` *(mặc định)*.
   - **Output Directory**: `dist` *(mặc định)*.

### 2. Thiết lập Biến môi trường (Environment Variables)
Trong mục **Environment Variables** trên Vercel, cấu hình các key sau:

| Tên biến (Key) | Giá trị (Value) | Mục đích |
| :--- | :--- | :--- |
| `VITE_SUPABASE_URL` | `https://llinrxwekykjmdrrpxtn.supabase.co` | Kết nối Supabase Auth & lịch sử chat |
| `VITE_SUPABASE_ANON_KEY` | `eyJhbGciOiJIUz...` *(Lấy từ file frontend/.env)* | Khóa xác thực phía client |
| `VITE_API_BASE_URL` | `https://sylphlike-rufus-malonyl.ngrok-free.dev` | URL Backend công khai |

### 3. Cơ chế Tự động Deploy (CI/CD)
- Mỗi khi anh chạy lệnh `git push origin main`, Vercel sẽ tự động kéo commit mới nhất về, cài đặt dependencies và đóng gói thành công trong khoảng 30-45 giây.
- Nếu cần cập nhật biến môi trường: Vào tab **Deployments** -> Bấm nút **3 chấm** tại bản build mới nhất -> Chọn **Redeploy**.

---

## 🐳 PHẦN 3: HƯỚNG DẪN DEPLOY & REBUILD BACKEND (DOCKER)

Backend của VietLegal AI đóng gói toàn bộ FastAPI, PyTorch (CPU-optimized), BGE-M3 và BGE-Reranker.

### 1. Chuẩn bị file `.env` tại thư mục gốc
Đảm bảo file `.env` tại thư mục gốc dự án có đầy đủ các thông tin bí mật:
```env
ENVIRONMENT=development
PORT=8000
HOST=0.0.0.0

# Qdrant Vector DB
QDRANT_URL=http://qdrant:6333
QDRANT_COLLECTION_NAME=vietlegal_articles

# Supabase
SUPABASE_URL=https://llinrxwekykjmdrrpxtn.supabase.co
SUPABASE_KEY=eyJhbGciOi...
DATABASE_URL=postgresql://postgres.llinrxwekykjmdrrpxtn:[PASSWORD]@aws-0-ap-southeast-1.pooler.supabase.com:6543/postgres

# Google Gemini LLM
GEMINI_API_KEY=AIzaSy...
GEMINI_MODEL=gemini-1.5-flash-lite

# CORS cho phép Vercel gọi về
BACKEND_CORS_ORIGINS=https://vietlegal-ai-orcin.vercel.app,https://sylphlike-rufus-malonyl.ngrok-free.dev,http://localhost:5173,http://localhost:80
```

### 2. Build và khởi chạy bằng Docker Compose
Khi có code mới cần cập nhật lên container:
```powershell
# 1. Dọn dẹp container và network cũ
docker compose down

# 2. Rebuild lại image chứa code mới nhất và khởi chạy ngầm
docker compose up -d --build backend
```

### 3. Kiểm tra tính sẵn sàng (Healthcheck Verification)
Sau khi container khởi động khoảng 15-20 giây (thời gian nạp mô hình vào RAM), chạy kiểm tra:
```powershell
# 1. Kiểm tra trạng thái container
docker ps

# 2. Kiểm tra endpoint liveness
Invoke-RestMethod -Uri "http://localhost:8888/health"

# 3. Kiểm tra toàn diện kết nối các dịch vụ
Invoke-RestMethod -Uri "http://localhost:8888/api/v1/health"
```
Kết quả mong đợi:
```json
{
  "status": "healthy",
  "service": "VietLegal AI",
  "environment": "development",
  "components": {
    "supabase": "connected",
    "qdrant": "connected (collection: True)",
    "llm_provider": "Google Gemini (gemini-3.5-flash-lite)"
  }
}
```

---

## 🛡️ PHẦN 4: THAY THẾ BẰNG CLOUDFLARE TUNNEL (TÙY CHỌN NÂNG CAO)

Nếu sau này anh muốn sử dụng **Cloudflare Tunnel** thay thế cho ngrok:

1. Mở Cloudflare Zero Trust Dashboard -> **Networks** -> **Tunnels**.
2. Tạo Tunnel mới hoặc chọn Tunnel hiện có.
3. Trong tab **Public Hostname**:
   - **Subdomain**: `api` (hoặc tên tùy chọn)
   - **Domain**: chọn domain của anh (ví dụ: `yourdomain.com`)
   - **Service Type**: `HTTP`
   - **URL**: `localhost:8888`
4. Cập nhật biến môi trường trên Vercel:
   - Đặt `VITE_API_BASE_URL` = `https://api.yourdomain.com`
   - Redeploy lại trên Vercel.

---

## 🛠️ PHẦN 5: XỬ LÝ SỰ CỐ THƯỜNG GẶP (TROUBLESHOOTING)

### 1. Lỗi Docker: `network ... not found`
- **Hiện tượng**: Khởi động container báo lỗi mạng không tìm thấy do ID mạng cũ bị xóa.
- **Cách xử lý**:
  ```powershell
  docker compose down
  docker compose up -d backend
  ```

### 2. Lỗi Ngrok: `ERR_NGROK_3200: endpoint is offline`
- **Hiện tượng**: Trang web trên Vercel báo không kết nối được máy chủ, console F12 báo lỗi mạng.
- **Nguyên nhân**: Quên bật ngrok hoặc ngrok bị tắt giữa chừng.
- **Cách xử lý**: Chạy lại lệnh:
  ```powershell
  ngrok http 8888 --domain=sylphlike-rufus-malonyl.ngrok-free.dev
  ```

### 3. Giao diện Vercel bị treo ở trạng thái "Đang suy nghĩ..." (Streaming hang)
- **Nguyên nhân**: Mạng chập chờn làm ngắt kết nối SSE stream giữa chừng.
- **Đã khắc phục**: Phiên bản mới nhất đã có cơ chế tự động bắt lỗi `onerror` trong React và ngắt cờ `isStreaming` để người dùng không bị kẹt nút bấm. Nếu vẫn gặp, chỉ cần F5 tải lại trang.

### 4. Kiểm tra Logs thời gian thực của Backend
Nếu cần xem chi tiết quá trình chatbot truy xuất luật hoặc log lỗi khi người dùng gửi câu hỏi:
```powershell
docker logs -f vietlegal_backend
```
*(Bấm `Ctrl + C` để thoát chế độ xem log).*
