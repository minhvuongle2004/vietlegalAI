import React, { useState, useEffect } from 'react';
import { X, Search, Copy, Check, ExternalLink, BookOpen, ShieldCheck } from 'lucide-react';
import { API_BASE_URL } from '../lib/api';

export default function ArticleModal({ isOpen, onClose, initialArticleNumber, initialDocId }) {
  const [articleNumber, setArticleNumber] = useState(initialArticleNumber || 1);
  const [docId, setDocId] = useState(initialDocId || 'bllđ_45_2019_qh14');
  const [searchQuery, setSearchQuery] = useState('');
  const [article, setArticle] = useState(null);
  const [searchResults, setSearchResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [fetchError, setFetchError] = useState(false);
  const [copied, setCopied] = useState(false);
  const [mode, setMode] = useState(initialArticleNumber ? 'view' : 'browse');

  useEffect(() => {
    if (initialArticleNumber) {
      setArticleNumber(initialArticleNumber);
      if (initialDocId) setDocId(initialDocId);
      setMode('view');
      fetchArticle(initialArticleNumber, initialDocId);
    }
  }, [initialArticleNumber, initialDocId, isOpen]);

  const fetchArticle = async (num, dId = docId) => {
    setLoading(true);
    setFetchError(false);
    try {
      const url = dId
        ? `${API_BASE_URL}/api/v1/legal/articles/${num}?doc_id=${encodeURIComponent(dId)}`
        : `${API_BASE_URL}/api/v1/legal/articles/${num}`;
      const res = await fetch(url);
      if (res.ok) {
        const data = await res.json();
        setArticle(data);
        if (data.document_id) setDocId(data.document_id);
        setMode('view');
      } else {
        setArticle(null);
        setFetchError(true);
      }
    } catch (err) {
      console.error('Lỗi khi tải điều luật:', err);
      setArticle(null);
      setFetchError(true);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!searchQuery.trim()) return;

    // Nếu người dùng nhập số (ví dụ "25" hoặc "Điều 25")
    const matchNum = searchQuery.match(/\d+/);
    if (matchNum && searchQuery.length <= 10) {
      const num = parseInt(matchNum[0]);
      if (num >= 1 && num <= 220) {
        fetchArticle(num);
        return;
      }
    }

    // Tra cứu full-text search
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE_URL}/api/v1/legal/search?q=${encodeURIComponent(searchQuery)}`);
      if (res.ok) {
        const data = await res.json();
        setSearchResults(data);
        setMode('search');
      }
    } catch (err) {
      console.error('Lỗi tra cứu:', err);
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = () => {
    if (!article) return;
    const textToCopy = `${article.article_title}\n(${article.chapter_info || ''})\n\n${article.full_text}`;
    navigator.clipboard.writeText(textToCopy);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  if (!isOpen) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content fade-in" onClick={(e) => e.stopPropagation()}>
        {/* Modal Header */}
        <div className="modal-header">
          <div className="modal-title-group">
            <div className="brand-icon-wrapper" style={{ width: 34, height: 34 }}>
              <BookOpen size={18} />
            </div>
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                {(() => {
                  const currentDId = article?.document_id || docId;
                  if (currentDId?.includes('land') || currentDId?.includes('31_2024')) {
                    return (
                      <>
                        <span className="modal-title">Luật Đất đai 2024</span>
                        <span className="modal-badge" style={{ backgroundColor: 'rgba(217, 119, 6, 0.15)', color: '#f59e0b' }}>Luật số 31/2024/QH15</span>
                      </>
                    );
                  }
                  if (currentDId?.includes('housing') || currentDId?.includes('27_2023')) {
                    return (
                      <>
                        <span className="modal-title">Luật Nhà ở 2023</span>
                        <span className="modal-badge" style={{ backgroundColor: 'rgba(6, 182, 212, 0.15)', color: '#06b6d4' }}>Luật số 27/2023/QH15</span>
                      </>
                    );
                  }
                  if (currentDId?.includes('re_business') || currentDId?.includes('29_2023')) {
                    return (
                      <>
                        <span className="modal-title">Luật Kinh doanh Bất động sản 2023</span>
                        <span className="modal-badge" style={{ backgroundColor: 'rgba(16, 185, 129, 0.15)', color: '#10b981' }}>Luật số 29/2023/QH15</span>
                      </>
                    );
                  }
                  if (currentDId?.includes('investment') || currentDId?.includes('61_2020')) {
                    return (
                      <>
                        <span className="modal-title">Luật Đầu tư 2020</span>
                        <span className="modal-badge" style={{ backgroundColor: 'rgba(139, 92, 246, 0.15)', color: '#8b5cf6' }}>Luật số 61/2020/QH14</span>
                      </>
                    );
                  }
                  if (currentDId?.includes('tncn') || currentDId?.includes('109_2025')) {
                    return (
                      <>
                        <span className="modal-title">Luật Thuế thu nhập cá nhân 2025</span>
                        <span className="modal-badge" style={{ backgroundColor: 'rgba(14, 165, 233, 0.15)', color: '#38bdf8' }}>Luật số 109/2025/QH15</span>
                      </>
                    );
                  }
                  if (currentDId?.includes('tndn') || currentDId?.includes('67_2025')) {
                    return (
                      <>
                        <span className="modal-title">Luật Thuế thu nhập doanh nghiệp 2025</span>
                        <span className="modal-badge" style={{ backgroundColor: 'rgba(59, 130, 246, 0.15)', color: '#60a5fa' }}>Luật số 67/2025/QH15</span>
                      </>
                    );
                  }
                  if (currentDId?.includes('qlt') || currentDId?.includes('108_2025')) {
                    return (
                      <>
                        <span className="modal-title">Luật Quản lý thuế 2025</span>
                        <span className="modal-badge" style={{ backgroundColor: 'rgba(236, 72, 153, 0.15)', color: '#f472b6' }}>Luật số 108/2025/QH15</span>
                      </>
                    );
                  }
                  if (currentDId?.includes('blds') || currentDId?.includes('91_2015')) {
                    return (
                      <>
                        <span className="modal-title">Bộ luật Dân sự 2015</span>
                        <span className="modal-badge" style={{ backgroundColor: 'rgba(168, 85, 247, 0.15)', color: '#c084fc' }}>Luật số 91/2015/QH13</span>
                      </>
                    );
                  }
                  if (currentDId?.includes('bhxh_41') || currentDId?.includes('41_2024')) {
                    return (
                      <>
                        <span className="modal-title">Luật Bảo hiểm xã hội 2024</span>
                        <span className="modal-badge" style={{ backgroundColor: 'rgba(16, 185, 129, 0.15)', color: '#34d399' }}>Luật số 41/2024/QH15</span>
                      </>
                    );
                  }
                  if (currentDId?.includes('bhyt') || currentDId?.includes('51_2024')) {
                    return (
                      <>
                        <span className="modal-title">Luật Bảo hiểm y tế sửa đổi 2024</span>
                        <span className="modal-badge" style={{ backgroundColor: 'rgba(20, 184, 166, 0.15)', color: '#2dd4bf' }}>Luật số 51/2024/QH15</span>
                      </>
                    );
                  }
                  if (currentDId?.includes('bhxh') || currentDId?.includes('58')) {
                    return (
                      <>
                        <span className="modal-title">Luật Bảo hiểm xã hội 2014</span>
                        <span className="modal-badge" style={{ backgroundColor: 'rgba(5, 150, 105, 0.15)', color: '#34d399' }}>Luật số 58/2014/QH13</span>
                      </>
                    );
                  }
                  if (currentDId?.includes('vieclam') || currentDId?.includes('38')) {
                    return (
                      <>
                        <span className="modal-title">Luật Việc làm 2013</span>
                        <span className="modal-badge" style={{ backgroundColor: 'rgba(217, 119, 6, 0.15)', color: '#fbbf24' }}>Luật số 38/2013/QH13</span>
                      </>
                    );
                  }
                  if (currentDId?.includes('ldn') || currentDId?.includes('59')) {
                    return (
                      <>
                        <span className="modal-title">Luật Doanh nghiệp 2020</span>
                        <span className="modal-badge" style={{ backgroundColor: 'rgba(168, 85, 247, 0.15)', color: '#c084fc' }}>Luật số 59/2020/QH14</span>
                      </>
                    );
                  }
                  if (currentDId?.includes('74')) {
                    return (
                      <>
                        <span className="modal-title">Nghị định 74/2024/NĐ-CP</span>
                        <span className="modal-badge" style={{ backgroundColor: 'rgba(16, 185, 129, 0.15)', color: '#34d399' }}>Lương tối thiểu vùng</span>
                      </>
                    );
                  }
                  if (currentDId?.includes('135')) {
                    return (
                      <>
                        <span className="modal-title">Nghị định 135/2020/NĐ-CP</span>
                        <span className="modal-badge" style={{ backgroundColor: 'rgba(59, 130, 246, 0.15)', color: '#60a5fa' }}>Tuổi nghỉ hưu</span>
                      </>
                    );
                  }
                  if (currentDId?.includes('122')) {
                    return (
                      <>
                        <span className="modal-title">Nghị định 122/2021/NĐ-CP</span>
                        <span className="modal-badge" style={{ backgroundColor: 'rgba(244, 63, 94, 0.15)', color: '#fb7185' }}>Xử phạt KH&ĐT</span>
                      </>
                    );
                  }
                  if (currentDId?.includes('01')) {
                    return (
                      <>
                        <span className="modal-title">Nghị định 01/2021/NĐ-CP</span>
                        <span className="modal-badge" style={{ backgroundColor: 'rgba(6, 182, 212, 0.15)', color: '#22d3ee' }}>Đăng ký doanh nghiệp</span>
                      </>
                    );
                  }
                  if (currentDId?.includes('12')) {
                    return (
                      <>
                        <span className="modal-title">Nghị định 12/2022/NĐ-CP</span>
                        <span className="modal-badge" style={{ backgroundColor: 'rgba(239, 68, 68, 0.15)', color: '#f87171' }}>Xử phạt VPHC</span>
                      </>
                    );
                  }
                  if (currentDId?.includes('145')) {
                    return (
                      <>
                        <span className="modal-title">Nghị định 145/2020/NĐ-CP</span>
                        <span className="modal-badge">Hướng dẫn thi hành</span>
                      </>
                    );
                  }
                  return (
                    <>
                      <span className="modal-title">Bộ luật Lao động 2019</span>
                      <span className="modal-badge">Toàn văn 220 Điều</span>
                    </>
                  );
                })()}
              </div>
              <p style={{ fontSize: '0.78rem', color: '#94a3b8' }}>
                {(() => {
                  const currentDId = article?.document_id || docId;
                  if (currentDId?.includes('bhxh') || currentDId?.includes('58')) return 'Quy định về chế độ ốm đau, thai sản, tai nạn lao động, hưu trí, tử tuất, BHXH một lần';
                  if (currentDId?.includes('vieclam') || currentDId?.includes('38')) return 'Quy định chính sách hỗ trợ tạo việc làm, thông tin thị trường lao động và Bảo hiểm thất nghiệp';
                  if (currentDId?.includes('ldn') || currentDId?.includes('59')) return 'Quy định về thành lập, tổ chức quản lý, tổ chức lại, giải thể và hoạt động của doanh nghiệp';
                  if (currentDId?.includes('122')) return 'Quy định xử phạt vi phạm hành chính trong lĩnh vực kế hoạch và đầu tư (ĐKDN, góp vốn, đấu thầu)';
                  if (currentDId?.includes('01')) return 'Quy định chi tiết về hồ sơ, trình tự, thủ tục đăng ký doanh nghiệp, đăng ký hộ kinh doanh';
                  if (currentDId?.includes('74')) return 'Quy định mức lương tối thiểu theo tháng và giờ đối với người lao động theo hợp đồng';
                  if (currentDId?.includes('135')) return 'Quy định lộ trình và bảng tra cứu tuổi nghỉ hưu của người lao động';
                  if (currentDId?.includes('12')) return 'Quy định mức xử phạt vi phạm hành chính lĩnh vực lao động, bảo hiểm xã hội';
                  if (currentDId?.includes('145')) return 'Quy định chi tiết và hướng dẫn thi hành một số điều của Bộ luật Lao động';
                  return 'Căn cứ chuẩn hóa từ Luật số 45/2019/QH14';
                })()}
              </p>
            </div>
          </div>
          <button className="icon-btn" onClick={onClose} style={{ padding: '0.5rem' }}>
            <X size={20} />
          </button>
        </div>

        {/* Modal Body */}
        <div className="modal-body">
          {/* Search bar */}
          <form onSubmit={handleSearch} className="search-article-bar">
            <input
              type="text"
              className="search-input"
              placeholder="Nhập số điều (VD: 25) hoặc từ khóa (VD: thử việc, sa thải)..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
            <button type="submit" className="action-btn primary" disabled={loading}>
              <Search size={16} />
              <span>Tra cứu</span>
            </button>
          </form>

          {/* Direct Article Jump Quick Picker */}
          <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center', marginBottom: '1.25rem', overflowX: 'auto', paddingBottom: '4px' }}>
            <span style={{ fontSize: '0.75rem', color: '#64748b', whiteSpace: 'nowrap' }}>Điều phổ biến:</span>
            {[25, 36, 40, 41, 105, 113, 125, 137].map((num) => (
              <button
                key={num}
                onClick={() => fetchArticle(num)}
                className={`action-btn ${article?.article_number === num ? 'primary' : ''}`}
                style={{ fontSize: '0.75rem', padding: '0.25rem 0.6rem', whiteSpace: 'nowrap' }}
              >
                Điều {num}
              </button>
            ))}
          </div>

          {loading ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', padding: '2rem 0' }}>
              <div className="skeleton" style={{ height: '32px', width: '60%' }}></div>
              <div className="skeleton" style={{ height: '20px', width: '40%' }}></div>
              <div className="skeleton" style={{ height: '140px', width: '100%' }}></div>
            </div>
          ) : mode === 'search' && searchResults.length > 0 ? (
            <div>
              <p style={{ fontSize: '0.85rem', color: '#94a3b8', marginBottom: '0.75rem' }}>
                Tìm thấy {searchResults.length} điều luật liên quan:
              </p>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                {searchResults.map((item) => (
                  <div
                    key={item.article_number}
                    onClick={() => fetchArticle(item.article_number)}
                    className="prompt-card"
                    style={{ padding: '0.9rem 1.1rem' }}
                  >
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <span style={{ fontWeight: 700, color: 'var(--accent-cyan)' }}>
                        {item.article_title}
                      </span>
                      <span style={{ fontSize: '0.75rem', color: '#64748b' }}>
                        {item.chapter_info}
                      </span>
                    </div>
                    <p style={{ fontSize: '0.85rem', color: '#cbd5e1', lineClamp: 2, overflow: 'hidden' }}>
                      {item.full_text?.slice(0, 180)}...
                    </p>
                  </div>
                ))}
              </div>
            </div>
          ) : article ? (
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.75rem' }}>
                <div>
                  <h3 style={{ fontSize: '1.2rem', color: '#f8fafc', fontWeight: 700, marginBottom: '0.35rem' }}>
                    {article.article_title}
                  </h3>
                  {article.chapter_info && (
                    <span className="chapter-info-badge">
                      {article.chapter_info}
                    </span>
                  )}
                </div>
                <button
                  onClick={copyToClipboard}
                  className={`action-btn ${copied ? 'primary' : ''}`}
                  title="Sao chép toàn văn"
                >
                  {copied ? <Check size={14} /> : <Copy size={14} />}
                  <span>{copied ? 'Đã chép' : 'Sao chép'}</span>
                </button>
              </div>

              <div className="article-fulltext">
                {article.full_text}
              </div>

              <div style={{ marginTop: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.78rem', color: '#10b981' }}>
                <ShieldCheck size={14} />
                <span>Trạng thái: Đang có hiệu lực thi hành (Hiệu lực từ 01/01/2021)</span>
              </div>
            </div>
          ) : fetchError ? (
            <div style={{ textAlign: 'center', padding: '2.5rem 1rem', color: '#f59e0b' }}>
              <p style={{ fontWeight: 600, fontSize: '0.92rem', marginBottom: '0.5rem' }}>⚠️ Không thể tải toàn văn điều luật</p>
              <p style={{ fontSize: '0.84rem', color: '#94a3b8' }}>
                Máy chủ Backend demo hiện đang tạm ngưng hoặc chưa bật kết nối. Vui lòng thử lại sau khi backend online.
              </p>
            </div>
          ) : (
            <div style={{ textAlign: 'center', padding: '3rem 1rem', color: '#64748b' }}>
              <p>Chọn một Điều luật ở trên hoặc gõ từ khóa để tra cứu toàn văn.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
