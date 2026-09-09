import React, { useState, useRef, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import {
  Scale,
  Send,
  Plus,
  Trash2,
  BookOpen,
  PanelLeftClose,
  PanelLeftOpen,
  Check,
  Copy,
  ExternalLink,
  Zap,
  ArrowUp,
  Cpu,
  LogOut,
  User,
  Menu,
  Settings,
} from 'lucide-react';
import ArticleModal from './components/ArticleModal';
import ProfileModal from './components/ProfileModal';
import LoginPromptModal from './components/LoginPromptModal';
import { useAuth } from './context/AuthContext';
import { API_BASE_URL } from './lib/api';
import './App.css';

// Logo Google SVG chuẩn
const GoogleIcon = () => (
  <svg className="google-icon-svg" viewBox="0 0 24 24">
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

const SAMPLE_QUESTIONS = [
  {
    title: 'Thời gian thử việc',
    sub: 'Quy định tối đa đối với trình độ đại học',
    query: 'Thời gian thử việc tối đa là bao lâu đối với vị trí công việc cần trình độ đại học trở lên?',
  },
  {
    title: 'Nghỉ việc riêng',
    sub: 'Kết hôn, người thân mất hưởng nguyên lương',
    query: 'Bản thân người lao động kết hôn thì được nghỉ việc riêng hưởng nguyên lương mấy ngày?',
  },
  {
    title: 'Tiền lương làm thêm giờ',
    sub: 'Mức tính làm thêm ban đêm ngày nghỉ lễ',
    query: 'Tiền lương làm thêm giờ vào ban ngày và ban đêm trong ngày nghỉ lễ, tết được tính ít nhất bằng bao nhiêu phần trăm?',
  },
  {
    title: 'Xử lý kỷ luật sa thải',
    sub: 'Tự ý bỏ việc bao nhiêu ngày thì bị sa thải',
    query: 'Người lao động tự ý bỏ việc bao nhiêu ngày cộng dồn trong một tháng thì có thể bị áp dụng hình thức sa thải?',
  },
  {
    title: 'Hưởng trợ cấp thất nghiệp',
    sub: 'Điều kiện hưởng trợ cấp thất nghiệp theo Luật Việc làm',
    query: 'Mức hưởng trợ cấp thất nghiệp hằng tháng được tính thế nào theo Luật Việc làm 2013 và tối đa bao nhiêu tháng?',
  },
  {
    title: 'Rút BHXH một lần',
    sub: 'Điều kiện hưởng BHXH một lần theo Luật BHXH',
    query: 'Người lao động được hưởng bảo hiểm xã hội một lần trong những trường hợp nào theo quy định của Luật Bảo hiểm xã hội 2014?',
  },
];

export default function App() {
  // Auth State
  const { user, session, loading: authLoading, signInWithGoogle, signOut } = useAuth();
  const [userMenuOpen, setUserMenuOpen] = useState(false);

  // Sidebar & Conversations State
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [isMobileDrawerOpen, setIsMobileDrawerOpen] = useState(false);
  const [isProfileModalOpen, setIsProfileModalOpen] = useState(false);
  const [isLoginPromptOpen, setIsLoginPromptOpen] = useState(false);
  const [conversations, setConversations] = useState([]);
  const [currentChatId, setCurrentChatId] = useState(null);

  // Active Chat State
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [useReranker, setUseReranker] = useState(false);
  const [copiedId, setCopiedId] = useState(null);

  // Modal State
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [inspectArticleNumber, setInspectArticleNumber] = useState(null);
  const [inspectDocId, setInspectDocId] = useState(null);

  const messagesEndRef = useRef(null);
  const textareaRef = useRef(null);

  // 1. Tải danh sách conversations từ Cloud nếu đã đăng nhập, ngược lại lấy từ localStorage
  useEffect(() => {
    if (user && session?.access_token) {
      fetchCloudConversations();
    } else {
      try {
        const local = localStorage.getItem('vietlegal_conversations');
        setConversations(local ? JSON.parse(local) : []);
      } catch {
        setConversations([]);
      }
    }
  }, [user, session]);

  const fetchCloudConversations = async () => {
    if (!session?.access_token) return;
    try {
      const res = await fetch(`${API_BASE_URL}/api/v1/conversations`, {
        headers: { Authorization: `Bearer ${session.access_token}` },
      });
      if (res.ok) {
        const data = await res.json();
        setConversations(data);
      }
    } catch (err) {
      console.warn('Lỗi khi tải danh sách hội thoại từ cloud:', err);
    }
  };

  // Cuộn xuống cuối tin nhắn
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Tự động co giãn chiều cao textarea
  const handleInputChange = (e) => {
    setInput(e.target.value);
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 180)}px`;
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  // Tạo phiên chat mới
  const handleNewChat = async () => {
    setCurrentChatId(null);
    setMessages([]);
    setInput('');
    setIsMobileDrawerOpen(false);
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }
  };

  // Chọn một phiên chat cũ từ sidebar
  const handleSelectConversation = async (conv) => {
    setCurrentChatId(conv.id);
    setInput('');
    setIsMobileDrawerOpen(false);

    if (user && session?.access_token) {
      try {
        const res = await fetch(`${API_BASE_URL}/api/v1/conversations/${conv.id}`, {
          headers: { Authorization: `Bearer ${session.access_token}` },
        });
        if (res.ok) {
          const data = await res.json();
          // Convert database messages to UI format
          const formatted = (data.messages || []).map((m) => ({
            id: m.id,
            sender: m.role,
            text: m.content,
            citations: m.citations || [],
            latencyMs: m.latency_ms,
            timestamp: new Date(m.created_at).toLocaleTimeString('vi-VN', {
              hour: '2-digit',
              minute: '2-digit',
            }),
          }));
          setMessages(formatted);
          return;
        }
      } catch (e) {
        console.warn('Lỗi khi tải chi tiết cuộc hội thoại từ cloud:', e);
      }
    }

    // Fallback nếu dùng local
    setMessages(conv.messages || []);
  };

  // Xóa một phiên chat
  const handleDeleteConversation = async (e, id) => {
    e.stopPropagation();

    if (user && session?.access_token) {
      try {
        await fetch(`${API_BASE_URL}/api/v1/conversations/${id}`, {
          method: 'DELETE',
          headers: { Authorization: `Bearer ${session.access_token}` },
        });
      } catch (err) {
        console.warn('Lỗi khi xóa cuộc hội thoại trên cloud:', err);
      }
    }

    const updated = conversations.filter((c) => c.id !== id);
    setConversations(updated);
    if (!user) {
      localStorage.setItem('vietlegal_conversations', JSON.stringify(updated));
    }
    if (currentChatId === id) {
      handleNewChat();
    }
  };

  // Gửi tin nhắn
  const handleSend = async (customQuery) => {
    const queryText = (customQuery || input).trim();
    if (!queryText || loading) return;

    // Giới hạn 2 câu hỏi miễn phí đối với khách chưa đăng nhập Google
    if (!user) {
      const guestQueryCount = parseInt(localStorage.getItem('vietlegal_guest_query_count') || '0', 10);
      if (guestQueryCount >= 2) {
        setIsLoginPromptOpen(true);
        return;
      }
      localStorage.setItem('vietlegal_guest_query_count', (guestQueryCount + 1).toString());
    }

    setInput('');
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }

    const userMessageId = `user-${Date.now()}`;
    const assistantMessageId = `ai-${Date.now()}`;

    const userMsg = {
      id: userMessageId,
      sender: 'user',
      text: queryText,
      timestamp: new Date().toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' }),
    };

    const aiPlaceholder = {
      id: assistantMessageId,
      sender: 'assistant',
      text: '',
      citations: [],
      isStreaming: true,
      latencyMs: null,
      mode: useReranker ? 'rerank' : 'fast',
      timestamp: new Date().toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' }),
    };

    const newMessages = [...messages, userMsg, aiPlaceholder];
    setMessages(newMessages);
    setLoading(true);

    // Xử lý Conversation ID (Cloud hoặc Local)
    let activeId = currentChatId;
    const title = queryText.length > 32 ? queryText.slice(0, 32) + '...' : queryText;

    if (!activeId) {
      if (user && session?.access_token) {
        try {
          const res = await fetch(`${API_BASE_URL}/api/v1/conversations`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              Authorization: `Bearer ${session.access_token}`,
            },
            body: JSON.stringify({ title }),
          });
          if (res.ok) {
            const newConv = await res.json();
            activeId = newConv.id;
            setCurrentChatId(activeId);
            setConversations((prev) => [newConv, ...prev]);
          }
        } catch (e) {
          console.warn('Lỗi khi tạo conversation trên cloud:', e);
        }
      }

      if (!activeId) {
        activeId = `conv-${Date.now()}`;
        setCurrentChatId(activeId);
        const newLocal = [{ id: activeId, title, createdAt: Date.now(), messages: newMessages }, ...conversations];
        setConversations(newLocal);
        localStorage.setItem('vietlegal_conversations', JSON.stringify(newLocal));
      }
    }

    try {
      const headers = { 'Content-Type': 'application/json' };
      if (session?.access_token) {
        headers['Authorization'] = `Bearer ${session.access_token}`;
      }

      const response = await fetch(`${API_BASE_URL}/api/v1/chat/completions`, {
        method: 'POST',
        headers,
        body: JSON.stringify({
          query: queryText,
          conversation_id: activeId,
          top_k: 3,
          use_reranker: useReranker,
        }),
      });

      if (!response.ok) {
        throw new Error(`Lỗi phản hồi máy chủ: HTTP ${response.status}`);
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder('utf-8');
      let accumulatedText = '';
      let citations = [];
      let buffer = '';

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        let currentEvent = 'message';

        for (const line of lines) {
          const trimmed = line.trim();
          if (!trimmed) continue;

          if (trimmed.startsWith('event:')) {
            currentEvent = trimmed.replace('event:', '').trim();
          } else if (trimmed.startsWith('data:')) {
            const dataStr = trimmed.replace('data:', '').trim();
            try {
              const dataObj = JSON.parse(dataStr);

              if (currentEvent === 'citations' && dataObj.citations) {
                citations = dataObj.citations;
                setMessages((prev) =>
                  prev.map((m) =>
                    m.id === assistantMessageId ? { ...m, citations } : m
                  )
                );
              } else if (currentEvent === 'token' && dataObj.token) {
                accumulatedText += dataObj.token;
                setMessages((prev) =>
                  prev.map((m) =>
                    m.id === assistantMessageId ? { ...m, text: accumulatedText } : m
                  )
                );
              } else if (currentEvent === 'done') {
                setMessages((prev) =>
                  prev.map((m) =>
                    m.id === assistantMessageId
                      ? { ...m, isStreaming: false, latencyMs: dataObj.latency_ms }
                      : m
                  )
                );
              }
            } catch (err) {
              console.warn('Lỗi phân tích cú pháp SSE JSON:', err);
            }
          }
        }
      }
    } catch (err) {
      console.error('Lỗi khi gọi API chat:', err);
      setMessages((prev) =>
        prev.map((m) =>
          m.id === assistantMessageId
            ? {
                ...m,
                isStreaming: false,
                text: `⚠️ **Không thể kết nối đến máy chủ AI:**\n${err.message}. Vui lòng kiểm tra lại backend service.`,
              }
            : m
        )
      );
    } finally {
      setLoading(false);
    }
  };

  const openArticleModal = (num, dId = null) => {
    setInspectArticleNumber(num);
    setInspectDocId(dId);
    setIsModalOpen(true);
  };

  const copyMessageText = (id, text) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  // Profile data
  const userMetadata = user?.user_metadata || {};
  const userName = userMetadata.full_name || userMetadata.name || user?.email?.split('@')[0] || (user ? 'Người dùng' : 'Khách');
  const userAvatar = userMetadata.avatar_url || userMetadata.picture;
  const userEmail = user?.email || '';

  return (
    <div className="chatgpt-layout">
      {/* Mobile Drawer Backdrop */}
      {isMobileDrawerOpen && (
        <div
          className="mobile-drawer-backdrop"
          onClick={() => setIsMobileDrawerOpen(false)}
        />
      )}

      {/* Left Sidebar */}
      <aside className={`chatgpt-sidebar ${!sidebarOpen ? 'collapsed' : ''} ${isMobileDrawerOpen ? 'mobile-open' : ''}`}>
        <div className="sidebar-header">
          <div className="sidebar-brand">
            <div className="sidebar-brand-icon">
              <Scale size={16} />
            </div>
            <span>VietLegal AI</span>
          </div>

          <button
            className="icon-button"
            onClick={() => setSidebarOpen(false)}
            title="Thu gọn thanh bên"
          >
            <PanelLeftClose size={18} />
          </button>
        </div>

        {/* New Chat Button */}
        <button className="new-chat-btn" onClick={handleNewChat}>
          <Plus size={16} />
          <span>Đoạn chat mới</span>
        </button>

        {/* Quick Nav Tools */}
        <div className="sidebar-nav-list">
          <button
            className="nav-item"
            onClick={() => openArticleModal(1)}
            title="Tra cứu toàn văn điều luật"
          >
            <BookOpen size={16} />
            <span>Tra cứu điều luật</span>
          </button>
        </div>

        {/* Chat History List */}
        <div className="sidebar-history">
          {conversations.length > 0 && (
            <>
              <div className="history-section-title">
                {user ? 'Lịch sử Cloud' : 'Gần đây'}
              </div>
              {conversations.map((conv) => (
                <button
                  key={conv.id}
                  className={`history-item ${currentChatId === conv.id ? 'active' : ''}`}
                  onClick={() => handleSelectConversation(conv)}
                  title={conv.title}
                >
                  <span className="history-item-title">{conv.title}</span>
                  <span
                    className="history-item-delete"
                    onClick={(e) => handleDeleteConversation(e, conv.id)}
                    title="Xóa đoạn chat này"
                  >
                    <Trash2 size={14} />
                  </span>
                </button>
              ))}
            </>
          )}
        </div>

        {/* User Account / Login Footer */}
        <div className="sidebar-footer" style={{ position: 'relative' }}>
          {user ? (
            <>
              <button
                className="user-profile-btn"
                onClick={() => setUserMenuOpen(!userMenuOpen)}
                title="Tùy chọn tài khoản"
              >
                {userAvatar ? (
                  <img src={userAvatar} alt="Avatar" className="user-avatar-img" />
                ) : (
                  <div className="user-avatar-badge">{userName.slice(0, 2).toUpperCase()}</div>
                )}
                <div className="user-profile-info">
                  <span className="user-name">{userName}</span>
                  <span className="user-role">Tài khoản Google</span>
                </div>
              </button>

              {/* User Menu Popover */}
              {userMenuOpen && (
                <div className="user-menu-popover">
                  <div className="user-menu-header">
                    <div style={{ fontWeight: 600, fontSize: '0.82rem' }}>{userName}</div>
                    <div className="user-menu-email">{userEmail}</div>
                  </div>
                  <button
                    className="user-menu-item logout"
                    onClick={() => {
                      setUserMenuOpen(false);
                      signOut();
                    }}
                  >
                    <LogOut size={14} />
                    <span>Đăng xuất</span>
                  </button>
                </div>
              )}
            </>
          ) : (
            <button
              className="google-login-btn"
              onClick={signInWithGoogle}
              title="Đăng ký hoặc đăng nhập duy nhất bằng Google"
            >
              <GoogleIcon />
              <span>Tiếp tục với Google</span>
            </button>
          )}
        </div>
        {/* Mobile Sidebar Bottom Actions (ChatGPT iOS Style - Image 2) */}
        <div className="mobile-sidebar-actions">
          <button className="mobile-new-chat-pill" onClick={handleNewChat}>
            <Plus size={18} />
            <span>Đoạn chat</span>
          </button>
          <button
            className="mobile-settings-btn"
            onClick={() => {
              setIsMobileDrawerOpen(false);
              setIsProfileModalOpen(true);
            }}
            aria-label="Cài đặt tài khoản"
          >
            <Settings size={20} />
          </button>
        </div>
      </aside>

      {/* Main Chat Area */}
      <main className="chatgpt-main">
        {/* Mobile Topbar (ChatGPT iOS Style - Image 3) */}
        <header className="mobile-topbar">
          <button
            className="mobile-round-btn"
            onClick={() => setIsMobileDrawerOpen(true)}
            aria-label="Mở Menu"
          >
            <Menu size={20} />
          </button>

          <button
            className={`mobile-mode-badge ${useReranker ? 'deep' : ''}`}
            onClick={() => setUseReranker(!useReranker)}
            title="Chuyển chế độ suy luận"
          >
            {useReranker ? <Cpu size={14} /> : <Zap size={14} />}
            <span>{useReranker ? 'Chuyên sâu (GPU)' : 'Tiêu chuẩn'}</span>
          </button>

          <button
            className="mobile-round-btn"
            onClick={handleNewChat}
            aria-label="Đoạn chat mới"
          >
            <Plus size={20} />
          </button>
        </header>

        {/* Desktop Top Navbar */}
        <div className="main-navbar desktop-only-navbar">
          <div className="nav-left-section">
            {!sidebarOpen && (
              <button
                className="icon-button"
                onClick={() => setSidebarOpen(true)}
                title="Mở thanh bên"
              >
                <PanelLeftOpen size={18} />
              </button>
            )}

            {/* Mode Switcher Pill (ChatGPT Style) */}
            <div className="mode-switch-pill">
              <button
                className={`mode-option ${!useReranker ? 'active' : ''}`}
                onClick={() => setUseReranker(false)}
                title="Chế độ tìm kiếm nhanh chuẩn xác (~300ms)"
              >
                <Zap size={13} />
                <span>Tiêu chuẩn</span>
              </button>
              <button
                className={`mode-option ${useReranker ? 'active' : ''}`}
                onClick={() => setUseReranker(true)}
                title="Kích hoạt BGE-Reranker trên GPU RTX 3050 soi xét từng điều luật"
              >
                <Cpu size={13} />
                <span>Chuyên sâu (GPU)</span>
              </button>
            </div>
          </div>

          <div className="nav-right-section" style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            {!user && (
              <button className="google-nav-btn" onClick={signInWithGoogle}>
                <GoogleIcon />
                <span>Đăng nhập</span>
              </button>
            )}

            {messages.length > 0 && (
              <button className="icon-button" onClick={handleNewChat} title="Bắt đầu đoạn chat mới">
                <Plus size={18} />
              </button>
            )}
          </div>
        </div>

        {/* Chat Messages or Welcome Screen */}
        {messages.length === 0 ? (
          /* Welcome Screen (Centered like ChatGPT) */
          <div className="welcome-center">
            <h1 className="welcome-heading">Hôm nay bạn cần hỗ trợ pháp lý gì?</h1>

            {/* Centered Input Box */}
            <div className="input-container" style={{ marginBottom: '16px' }}>
              <textarea
                ref={textareaRef}
                rows={2}
                className="input-textarea"
                placeholder="Hỏi bất kỳ điều gì về quy định pháp luật..."
                value={input}
                onChange={handleInputChange}
                onKeyDown={handleKeyDown}
                disabled={loading}
              />

              <div className="input-actions-bar">
                <div className="input-left-tools">
                  <button
                    className={`tool-tag-btn ${useReranker ? 'active-gpu' : ''}`}
                    onClick={() => setUseReranker(!useReranker)}
                  >
                    {useReranker ? <Cpu size={13} /> : <Zap size={13} />}
                    <span>{useReranker ? 'Reranker GPU' : 'Tiêu chuẩn'}</span>
                  </button>
                </div>

                <button
                  className="send-button"
                  onClick={() => handleSend()}
                  disabled={!input.trim() || loading}
                  title="Gửi câu hỏi"
                >
                  <ArrowUp size={16} />
                </button>
              </div>
            </div>

            <div className="input-disclaimer" style={{ marginTop: '24px' }}>
              ⚠️ <strong>Khuyến cáo pháp lý:</strong> VietLegal AI là trợ lý tra cứu & suy luận quy định pháp luật tự động. Mọi câu trả lời chỉ mang tính chất tham khảo, không thay thế cho ý kiến tư vấn pháp lý chính thức từ Luật sư hoặc cơ quan Nhà nước có thẩm quyền.
            </div>
          </div>
        ) : (
          /* Message List */
          <div className="messages-container">
            {messages.map((msg) => (
              <div key={msg.id} className="message-row">
                <div className="message-inner">
                  <div className={`message-avatar ${msg.sender}`}>
                    {msg.sender === 'user' ? (
                      userAvatar ? (
                        <img src={userAvatar} alt="User" style={{ width: '100%', height: '100%', borderRadius: '50%' }} />
                      ) : (
                        userName.slice(0, 2).toUpperCase()
                      )
                    ) : (
                      <Scale size={16} />
                    )}
                  </div>

                  <div className="message-body">
                    <div className="message-sender-name">
                      {msg.sender === 'user' ? (user ? userName : 'Bạn') : 'VietLegal AI'}
                    </div>

                    <div className="markdown-content">
                      <ReactMarkdown>{msg.text}</ReactMarkdown>
                      {msg.isStreaming && <span className="typing-dot" style={{ marginLeft: '4px' }}></span>}
                    </div>

                    {/* Citations Tag Pills */}
                    {msg.citations && msg.citations.length > 0 && (
                      <div className="citations-wrapper">
                        <span className="citations-label">Căn cứ:</span>
                        {msg.citations.map((cite, i) => (
                          <button
                            key={i}
                            className="citation-pill"
                            onClick={() => openArticleModal(cite.article_number, cite.doc_id)}
                            title={`Xem toàn văn: ${cite.article_title} (${cite.doc_title || 'Luật'})`}
                          >
                            <span className="citation-pill-num">
                              {(() => {
                                const d = cite.doc_id || '';
                                if (d.includes('land') || d.includes('31_2024')) return 'Luật Đất đai';
                                if (d.includes('housing') || d.includes('27_2023')) return 'Luật Nhà ở';
                                if (d.includes('re_business') || d.includes('29_2023')) return 'Luật KDBĐS';
                                if (d.includes('investment') || d.includes('61_2020')) return 'Luật Đầu tư';
                                if (d.includes('tncn') || d.includes('109_2025')) return 'Thuế TNCN';
                                if (d.includes('tndn') || d.includes('67_2025')) return 'Thuế TNDN';
                                if (d.includes('qlt') || d.includes('108_2025')) return 'Quản lý thuế';
                                if (d.includes('blds') || d.includes('91_2015')) return 'BL Dân sự';
                                if (d.includes('bhxh_41') || d.includes('41_2024')) return 'BHXH 2024';
                                if (d.includes('bhyt') || d.includes('51_2024')) return 'BHYT 2024';
                                if (d.includes('bhxh') || d.includes('58')) return 'Luật BHXH';
                                if (d.includes('vieclam') || d.includes('38')) return 'Luật Việc làm';
                                if (d.includes('ldn') || d.includes('59')) return 'Luật DN';
                                if (d.includes('122')) return 'NĐ 122';
                                if (d.includes('01')) return 'NĐ 01';
                                if (d.includes('12')) return 'NĐ 12';
                                if (d.includes('145')) return 'NĐ 145';
                                if (d.includes('74')) return 'NĐ 74';
                                if (d.includes('135')) return 'NĐ 135';
                                return 'BLLĐ';
                              })()} • Điều {cite.article_number}
                            </span>
                            <span>{cite.article_title.replace(`Điều ${cite.article_number}. `, '')}</span>
                            <ExternalLink size={10} style={{ opacity: 0.6 }} />
                          </button>
                        ))}
                      </div>
                    )}

                    {/* Message Actions */}
                    {msg.sender === 'assistant' && !msg.isStreaming && (
                      <div className="message-footer">
                        <button
                          className="action-icon-btn"
                          onClick={() => copyMessageText(msg.id, msg.text)}
                          title="Sao chép câu trả lời"
                        >
                          {copiedId === msg.id ? <Check size={14} color="#10a37f" /> : <Copy size={14} />}
                        </button>
                        {msg.latencyMs && <span>{msg.latencyMs}ms</span>}
                        <span>•</span>
                        <span>{msg.mode === 'rerank' ? 'Chuyên sâu (GPU)' : 'Tiêu chuẩn'}</span>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))}
            <div ref={messagesEndRef} />
          </div>
        )}

        {/* Bottom Input Area when in Chat */}
        {messages.length > 0 && (
          <div className="input-area-wrapper">
            <div className="input-container">
              <textarea
                ref={textareaRef}
                rows={1}
                className="input-textarea"
                placeholder="Nhắn tin cho VietLegal AI..."
                value={input}
                onChange={handleInputChange}
                onKeyDown={handleKeyDown}
                disabled={loading}
              />

              <div className="input-actions-bar">
                <div className="input-left-tools">
                  <button
                    className={`tool-tag-btn ${useReranker ? 'active-gpu' : ''}`}
                    onClick={() => setUseReranker(!useReranker)}
                  >
                    {useReranker ? <Cpu size={13} /> : <Zap size={13} />}
                    <span>{useReranker ? 'Reranker GPU' : 'Tiêu chuẩn'}</span>
                  </button>
                </div>

                <button
                  className="send-button"
                  onClick={() => handleSend()}
                  disabled={!input.trim() || loading}
                  title="Gửi câu hỏi"
                >
                  <ArrowUp size={16} />
                </button>
              </div>
            </div>

            <div className="input-disclaimer">
              ⚠️ <strong>Khuyến cáo pháp lý:</strong> VietLegal AI là trợ lý tra cứu & suy luận tự động. Mọi thông tin chỉ mang tính chất tham khảo, không thay thế ý kiến tư vấn pháp lý chính thức từ Luật sư hoặc cơ quan có thẩm quyền.
            </div>
          </div>
        )}
      </main>

      {/* User Profile / Settings Modal (ChatGPT iOS Style - Image 1) */}
      <ProfileModal
        isOpen={isProfileModalOpen}
        onClose={() => setIsProfileModalOpen(false)}
      />

      {/* Login Required Modal (Sau 2 câu hỏi miễn phí của khách) */}
      <LoginPromptModal
        isOpen={isLoginPromptOpen}
        onClose={() => setIsLoginPromptOpen(false)}
      />

      {/* Article Inspection Modal */}
      <ArticleModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        initialArticleNumber={inspectArticleNumber}
        initialDocId={inspectDocId}
      />
    </div>
  );
}
