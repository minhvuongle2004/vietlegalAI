import React from 'react';
import { X, User, Mail, Shield, LogOut, ChevronRight, Sliders, Database, Zap, Edit2, LogIn } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

// Logo Google chuẩn
const GoogleIcon = () => (
  <svg width="18" height="18" viewBox="0 0 24 24">
    <path
      fill="#4285F4"
      d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
    />
    <path
      fill="#34A853"
      d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
    />
    <path
      fill="#FBBC05"
      d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z"
    />
    <path
      fill="#EA4335"
      d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z"
    />
  </svg>
);

export default function ProfileModal({ isOpen, onClose }) {
  const { user, signInWithGoogle, signOut } = useAuth();

  if (!isOpen) return null;

  const isLoggedIn = !!user;
  const fullName = isLoggedIn
    ? (user.user_metadata?.full_name || user.user_metadata?.name || user.email?.split('@')[0] || 'Người dùng')
    : 'Khách trải nghiệm';
  const email = isLoggedIn ? user.email : 'Chưa đăng nhập';
  const avatarUrl = user?.user_metadata?.avatar_url;

  // Lấy 2 chữ cái đầu nếu có tên thật
  const getInitials = (name) => {
    if (!name || name === 'Khách trải nghiệm') return null;
    const parts = name.trim().split(' ');
    if (parts.length === 1) return parts[0].substring(0, 2).toUpperCase();
    return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
  };

  const initials = getInitials(fullName);

  return (
    <div className="profile-modal-backdrop" onClick={onClose}>
      <div className="profile-modal-sheet" onClick={(e) => e.stopPropagation()}>
        {/* Nút đóng tròn góc trên bên phải */}
        <button className="profile-modal-close-btn" onClick={onClose} aria-label="Đóng">
          <X size={20} />
        </button>

        {/* Phần Avatar tròn */}
        <div className="profile-avatar-container">
          <div className="profile-avatar-wrapper">
            {isLoggedIn && avatarUrl ? (
              <img src={avatarUrl} alt={fullName} className="profile-avatar-img" />
            ) : isLoggedIn && initials ? (
              <div className="profile-avatar-initials">{initials}</div>
            ) : (
              <div className="profile-avatar-guest">
                <User size={38} color="#9ca3af" />
              </div>
            )}
            {isLoggedIn && (
              <div className="profile-avatar-badge" title="Tài khoản đã xác thực">
                <Edit2 size={12} />
              </div>
            )}
          </div>
          <h2 className="profile-user-name">{fullName}</h2>
          <span className="profile-user-sub">
            {isLoggedIn ? 'Tài khoản Google đã kết nối' : 'Đang sử dụng phiên bản Khách'}
          </span>
        </div>

        {/* Thẻ Nâng cấp / Đăng nhập CTA */}
        {!isLoggedIn ? (
          <div className="profile-upgrade-card" style={{ border: '1px solid #3b82f6', background: 'rgba(59, 130, 246, 0.08)' }}>
            <div className="profile-upgrade-info">
              <h4 className="profile-upgrade-title">Đăng nhập tài khoản</h4>
              <p className="profile-upgrade-desc">
                Đồng bộ lịch sử tra cứu trên Cloud và tiếp tục đoạn chat trên mọi thiết bị.
              </p>
            </div>
            <button
              className="profile-upgrade-btn"
              style={{ background: '#ffffff', color: '#1f1f1f', display: 'flex', alignItems: 'center', gap: '6px' }}
              onClick={() => {
                onClose();
                signInWithGoogle();
              }}
            >
              <GoogleIcon />
              <span>Đăng nhập</span>
            </button>
          </div>
        ) : (
          <div className="profile-upgrade-card">
            <div className="profile-upgrade-info">
              <h4 className="profile-upgrade-title">Làm được nhiều hơn với VietLegal AI</h4>
              <p className="profile-upgrade-desc">
                Trải nghiệm mô hình Reranker chuyên sâu GPU và tra cứu văn bản không giới hạn.
              </p>
            </div>
            <button className="profile-upgrade-btn" onClick={() => alert('Phiên bản Public Beta đang mở miễn phí toàn bộ tính năng!')}>
              Nâng cấp
            </button>
          </div>
        )}

        {/* Nhóm tùy chỉnh */}
        <div className="profile-section">
          <h3 className="profile-section-title">Tùy chỉnh VietLegal AI</h3>
          <div className="profile-menu-group">
            <div className="profile-menu-item">
              <div className="profile-menu-icon">
                <Sliders size={18} />
              </div>
              <div className="profile-menu-text">Cá nhân hóa</div>
              <ChevronRight size={16} className="profile-menu-arrow" />
            </div>
            <div className="profile-menu-item">
              <div className="profile-menu-icon">
                <Database size={18} />
              </div>
              <div className="profile-menu-text">Bộ nhớ hội thoại {isLoggedIn ? '(Cloud)' : '(Local)'}</div>
              <ChevronRight size={16} className="profile-menu-arrow" />
            </div>
            <div className="profile-menu-item">
              <div className="profile-menu-icon">
                <Zap size={18} />
              </div>
              <div className="profile-menu-text">Chế độ phản hồi (Tiêu chuẩn / GPU)</div>
              <ChevronRight size={16} className="profile-menu-arrow" />
            </div>
          </div>
        </div>

        {/* Nhóm Tài khoản */}
        <div className="profile-section">
          <h3 className="profile-section-title">Tài khoản</h3>
          <div className="profile-menu-group">
            <div className="profile-menu-item">
              <div className="profile-menu-icon">
                <Mail size={18} />
              </div>
              <div className="profile-menu-col">
                <span className="profile-menu-label">Email</span>
                <span className="profile-menu-val">{email}</span>
              </div>
              <ChevronRight size={16} className="profile-menu-arrow" />
            </div>

            <div className="profile-menu-item">
              <div className="profile-menu-icon">
                <Shield size={18} />
              </div>
              <div className="profile-menu-col">
                <span className="profile-menu-label">Gói dịch vụ</span>
                <span className="profile-menu-val">
                  {isLoggedIn ? 'Miễn phí (Public Beta)' : 'Khách dùng thử'}
                </span>
              </div>
              <ChevronRight size={16} className="profile-menu-arrow" />
            </div>

            {/* Hành động Đăng nhập hoặc Đăng xuất */}
            {isLoggedIn ? (
              <div
                className="profile-menu-item profile-logout-item"
                onClick={async () => {
                  await signOut();
                  onClose();
                }}
              >
                <div className="profile-menu-icon profile-logout-icon">
                  <LogOut size={18} />
                </div>
                <div className="profile-menu-text profile-logout-text">Đăng xuất</div>
              </div>
            ) : (
              <div
                className="profile-menu-item"
                onClick={async () => {
                  onClose();
                  signInWithGoogle();
                }}
              >
                <div className="profile-menu-icon">
                  <GoogleIcon />
                </div>
                <div className="profile-menu-text" style={{ color: '#38bdf8', fontWeight: 600 }}>
                  Đăng nhập bằng Google
                </div>
                <ChevronRight size={16} className="profile-menu-arrow" />
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
