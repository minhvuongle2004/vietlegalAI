// Cấu hình Base URL linh hoạt cho Backend API
// Trong môi trường Local Dev: để trống (Vite proxy tự động chuyển tiếp /api sang localhost:8000)
// Trong môi trường Production (Vercel/Netlify): nạp từ biến môi trường VITE_API_BASE_URL (ví dụ: https://api.vietlegal.vn)
export const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || '').replace(/\/$/, '');
