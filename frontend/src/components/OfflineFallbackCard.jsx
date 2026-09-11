import React, { useState } from 'react';
import {
  CloudOff,
  Clock,
  AlertTriangle,
  RotateCw,
  Copy,
  Check,
  Mail,
  Smartphone,
  LogIn,
  AlertCircle,
  HelpCircle,
} from 'lucide-react';

export default function OfflineFallbackCard({
  errorType = 'offline',
  onRetry,
  onLogin,
}) {
  const [copiedItem, setCopiedItem] = useState(null);

  const copyToClipboard = (text, type) => {
    navigator.clipboard.writeText(text);
    setCopiedItem(type);
    setTimeout(() => setCopiedItem(null), 2500);
  };

  // 1. BACKEND OFFLINE (Trường hợp chủ đạo khi máy tác giả tắt hoặc chưa bật tunnel)
  if (errorType === 'offline') {
    return (
      <div className="offline-fallback-card fade-in">
        <div className="offline-card-header">
          <div className="offline-icon-badge">
            <CloudOff size={20} className="text-amber-400" />
          </div>
          <div className="offline-header-text">
            <div className="offline-title">VietLegal AI đang tạm offline 😅</div>
            <div className="offline-subtitle">Backend Demo chạy trên máy trạm cục bộ</div>
          </div>
          <span className="offline-status-pill">Local Engine Offline</span>
        </div>

        <div className="offline-card-body">
          <p className="offline-lead-text">
            Backend demo hiện đang được vận hành trên máy cá nhân của tác giả nên đôi lúc hệ thống sẽ được tạm ngưng khi chủ nhân tắt máy.
          </p>

          <div className="offline-callout-box">
            <div className="offline-callout-title">
              💡 <strong>Bạn muốn trải nghiệm đầy đủ tính năng tra cứu & suy luận RAG?</strong>
            </div>
            <p className="offline-callout-desc">
              Hãy liên hệ trực tiếp với tác giả để được bật máy chủ demo ngay lập tức:
            </p>

            <div className="offline-contact-grid">
              <div className="contact-item">
                <div className="contact-item-left">
                  <Smartphone size={16} className="contact-icon text-sky-400" />
                  <span className="contact-label">Zalo / SĐT:</span>
                  <strong className="contact-value">0353234113</strong>
                </div>
                <button
                  type="button"
                  className="contact-action-btn"
                  onClick={() => copyToClipboard('0353234113', 'zalo')}
                  title="Sao chép số Zalo"
                >
                  {copiedItem === 'zalo' ? (
                    <>
                      <Check size={13} color="#10b981" />
                      <span className="copied-text">Đã chép!</span>
                    </>
                  ) : (
                    <>
                      <Copy size={13} />
                      <span>Sao chép</span>
                    </>
                  )}
                </button>
              </div>

              <div className="contact-item">
                <div className="contact-item-left">
                  <Mail size={16} className="contact-icon text-purple-400" />
                  <span className="contact-label">Email:</span>
                  <strong className="contact-value">vuong8aqhqlna@gmail.com</strong>
                </div>
                <div className="contact-buttons-group">
                  <a
                    href="mailto:vuong8aqhqlna@gmail.com?subject=[VietLegal%20AI]%20Y%C3%AAu%20c%E1%BA%A7u%20b%E1%BA%ADt%20Demo%20Backend"
                    className="contact-action-btn mail-link"
                    title="Mở ứng dụng Email"
                  >
                    <Mail size={13} />
                    <span>Mở Mail</span>
                  </a>
                  <button
                    type="button"
                    className="contact-action-btn"
                    onClick={() => copyToClipboard('vuong8aqhqlna@gmail.com', 'email')}
                    title="Sao chép Email"
                  >
                    {copiedItem === 'email' ? (
                      <>
                        <Check size={13} color="#10b981" />
                        <span className="copied-text">Đã chép!</span>
                      </>
                    ) : (
                      <>
                        <Copy size={13} />
                        <span>Sao chép</span>
                      </>
                    )}
                  </button>
                </div>
              </div>
            </div>
          </div>

          <div className="offline-footer-note">
            <span className="offline-humor-text">
              ✨ <em>Bạn vừa bắt gặp mình đúng lúc chủ nhân đang tắt máy 😄</em>
            </span>

            {onRetry && (
              <button
                type="button"
                className="offline-retry-btn"
                onClick={onRetry}
                title="Thử kết nối lại với máy chủ"
              >
                <RotateCw size={14} />
                <span>Thử kết nối lại</span>
              </button>
            )}
          </div>
        </div>
      </div>
    );
  }

  // 2. TIMEOUT
  if (errorType === 'timeout') {
    return (
      <div className="error-card timeout-card fade-in">
        <div className="error-card-header">
          <Clock size={18} className="text-amber-400" />
          <span className="error-title">Yêu cầu phản hồi quá thời gian chờ (Timeout)</span>
        </div>
        <p className="error-desc">
          Mô hình Cross-Encoder Reranker hoặc bộ truy xuất ngữ nghĩa đang xử lý khối lượng dữ liệu lớn hoặc đường truyền mạng tạm thời bị nghẽn.
        </p>
        {onRetry && (
          <button type="button" className="error-action-btn" onClick={onRetry}>
            <RotateCw size={14} />
            <span>Thử lại câu hỏi này</span>
          </button>
        )}
      </div>
    );
  }

  // 3. RATE LIMIT (429)
  if (errorType === 'rate_limit') {
    return (
      <div className="error-card rate-limit-card fade-in">
        <div className="error-card-header">
          <AlertTriangle size={18} className="text-amber-400" />
          <span className="error-title">Giới hạn tần suất gọi API (Rate Limit)</span>
        </div>
        <p className="error-desc">
          Hệ thống đang áp dụng giới hạn an toàn <strong>20 câu hỏi / phút</strong> để bảo vệ tài nguyên AI. Vui lòng nghỉ ngơi vài giây rồi thử lại nhé.
        </p>
        {onRetry && (
          <button type="button" className="error-action-btn" onClick={onRetry}>
            <RotateCw size={14} />
            <span>Thử lại ngay</span>
          </button>
        )}
      </div>
    );
  }

  // 4. AUTH EXPIRED (401)
  if (errorType === 'auth_expired') {
    return (
      <div className="error-card auth-card fade-in">
        <div className="error-card-header">
          <LogIn size={18} className="text-sky-400" />
          <span className="error-title">Phiên đăng nhập đã hết hạn</span>
        </div>
        <p className="error-desc">
          Thông tin xác thực Google của bạn đã hết hiệu lực. Hãy đăng nhập lại để tiếp tục lưu trữ lịch sử và trò chuyện không giới hạn.
        </p>
        {onLogin && (
          <button type="button" className="error-action-btn primary" onClick={onLogin}>
            <LogIn size={14} />
            <span>Đăng nhập lại bằng Google</span>
          </button>
        )}
      </div>
    );
  }

  // 5. SERVER / UPSTREAM ERROR (500/502)
  return (
    <div className="error-card server-card fade-in">
      <div className="error-card-header">
        <AlertCircle size={18} className="text-rose-400" />
        <span className="error-title">Dịch vụ AI gặp sự cố tạm thời</span>
      </div>
      <p className="error-desc">
        Hệ thống không thể hoàn tất quá trình sinh văn bản từ LLM. Bạn vui lòng bấm thử lại hoặc đặt lại câu hỏi ngắn gọn hơn.
      </p>
      {onRetry && (
        <button type="button" className="error-action-btn" onClick={onRetry}>
          <RotateCw size={14} />
          <span>Thử lại</span>
        </button>
      )}
    </div>
  );
}
