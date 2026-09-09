// Cấu hình Base URL linh hoạt cho Backend API
// Trong môi trường Local Dev (localhost:5173): để trống (Vite proxy tự động chuyển tiếp /api sang localhost:8000)
// Trong môi trường Cloud (Vercel): trỏ về tunnel URL công khai
const isLocalDev = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
export const API_BASE_URL = (
  import.meta.env.VITE_API_BASE_URL ||
  (isLocalDev ? '' : 'https://sylphlike-rufus-malonyl.ngrok-free.dev')
).replace(/\/$/, '');

