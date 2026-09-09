import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.jsx'
import { AuthProvider } from './context/AuthContext'

// Tự động bỏ qua màn hình chờ của tunnel khi gọi API
const _nativeFetch = window.fetch;
window.fetch = async (input, init = {}) => {
  const headers = new Headers(init.headers || {});
  headers.set('ngrok-skip-browser-warning', 'true');
  return _nativeFetch(input, { ...init, headers });
};

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <AuthProvider>
      <App />
    </AuthProvider>
  </StrictMode>,
)
