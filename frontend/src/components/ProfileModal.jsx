import React from 'react';
import { X, Sparkles, User, Mail, Shield, LogOut, ChevronRight, Sliders, Database, Zap, Edit2 } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export default function ProfileModal({ isOpen, onClose }) {
  const { user, signOut } = useAuth();

  if (!isOpen) return null;

  const fullName = user?.user_metadata?.full_name || 'Lê Minh Vương';
  const email = user?.email || 'vuong8aqhqlna@gmail.com';
  const avatarUrl = user?.user_metadata?.avatar_url;

  // Lấy 2 chữ cái đầu nếu không có avatar ảnh
  const getInitials = (name) => {
    if (!name) return 'LV';
    const parts = name.trim().split(' ');
    if (parts.length === 1) return parts[0].substring(0, 2).toUpperCase();
    return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
  };

  return (
    <div className="profile-modal-backdrop" onClick={onClose}>
      <div className="profile-modal-sheet" onClick={(e) => e.stopPropagation()}>
        {/* Nút đóng tròn góc trên bên phải */}
        <button className="profile-modal-close-btn" onClick={onClose} aria-label="Đóng">
          <X size={20} />
        </button>

        {/* Phần Avatar tròn với icon chỉnh sửa */}
        <div className="profile-avatar-container">
          <div className="profile-avatar-wrapper">
            {avatarUrl ? (
              <img src={avatarUrl} alt={fullName} className="profile-avatar-img" />
            ) : (
              <div className="profile-avatar-initials">{getInitials(fullName)}</div>
            )}
            <div className="profile-avatar-badge" title="Chỉnh sửa hồ sơ">
              <Edit2 size={12} />
            </div>
          </div>
          <h2 className="profile-user-name">{fullName}</h2>
        </div>

        {/* Thẻ Nâng cấp tính năng */}
        <div className="profile-upgrade-card">
          <div className="profile-upgrade-info">
            <h4 className="profile-upgrade-title">Làm được nhiều hơn với VietLegal AI</h4>
            <p className="profile-upgrade-desc">
              Trải nghiệm mô hình Reranker chuyên sâu GPU và tra cứu văn bản không giới hạn.
            </p>
          </div>
          <button className="profile-upgrade-btn" onClick={() => alert('Phiên bản Public Beta đang miễn phí toàn bộ tính năng!')}>
            Nâng cấp
          </button>
        </div>

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
              <div className="profile-menu-text">Bộ nhớ hội thoại</div>
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
                <span className="profile-menu-val">Miễn phí (Public Beta)</span>
              </div>
              <ChevronRight size={16} className="profile-menu-arrow" />
            </div>

            {/* Nút Đăng xuất */}
            {user && (
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
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
