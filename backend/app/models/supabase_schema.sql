-- ====================================================================
-- VietLegal AI - Supabase Database Schema
-- Hướng dẫn: Copy toàn bộ nội dung file này vào Supabase -> SQL Editor -> Nhấn "Run"
-- ====================================================================

-- 1. Bảng lưu trữ văn bản pháp luật gốc (Legal Documents)
CREATE TABLE IF NOT EXISTS legal_documents (
    id VARCHAR(100) PRIMARY KEY, -- vd: 'bllđ_45_2019_qh14'
    official_number VARCHAR(100) NOT NULL, -- vd: '45/2019/QH14'
    title TEXT NOT NULL,
    short_title VARCHAR(255),
    doc_type VARCHAR(50) NOT NULL, -- 'BO_LUAT', 'LUAT', 'NGHI_DINH', 'THONG_TU'
    issuer VARCHAR(100) NOT NULL, -- 'Quốc hội', 'Chính phủ'
    signer VARCHAR(100),
    issue_date DATE NOT NULL,
    effective_date DATE NOT NULL,
    expiry_date DATE,
    status VARCHAR(30) DEFAULT 'CON_HIEU_LUC', -- 'CON_HIEU_LUC', 'HET_HIEU_LUC'
    source_url TEXT,
    raw_content TEXT,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- 2. Bảng lưu trữ từng Điều luật (Articles) phục vụ BM25 Lexical Search & Trích dẫn
CREATE TABLE IF NOT EXISTS legal_articles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id VARCHAR(100) REFERENCES legal_documents(id) ON DELETE CASCADE,
    article_number INT NOT NULL,
    article_title TEXT,
    full_text TEXT NOT NULL,
    chapter_info TEXT,
    status VARCHAR(30) DEFAULT 'CON_HIEU_LUC',
    search_vector tsvector GENERATED ALWAYS AS (to_tsvector('simple', full_text)) STORED,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- Tạo Index GIN để tăng tốc độ tìm kiếm từ khóa BM25 toàn văn
CREATE INDEX IF NOT EXISTS idx_legal_articles_search ON legal_articles USING GIN(search_vector);
CREATE INDEX IF NOT EXISTS idx_legal_articles_doc_num ON legal_articles(document_id, article_number);

-- 3. Bảng quản lý phiên hội thoại (Conversations)
CREATE TABLE IF NOT EXISTS conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(255) DEFAULT 'Tư vấn pháp lý mới',
    user_id UUID, -- Liên kết với auth.users của Supabase nếu dùng Supabase Auth
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- 4. Bảng lưu lịch sử tin nhắn hỏi đáp (Messages)
CREATE TABLE IF NOT EXISTS messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID REFERENCES conversations(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL, -- 'user', 'assistant', 'system'
    content TEXT NOT NULL,
    citations JSONB DEFAULT '[]'::jsonb, -- Căn cứ pháp lý: [{doc_title, article_num, clause, excerpt}]
    tokens_used INT DEFAULT 0,
    latency_ms INT DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_messages_conversation_id ON messages(conversation_id);

-- 5. Bảng thu thập phản hồi người dùng (Message Feedback & RAG Evaluation)
CREATE TABLE IF NOT EXISTS message_feedback (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    message_id UUID REFERENCES messages(id) ON DELETE CASCADE,
    rating INT CHECK (rating IN (-1, 1)), -- 1: Thích/Hữu ích, -1: Không thích/Sai luật
    feedback_category VARCHAR(50), -- 'INACCURATE_LAW', 'WRONG_CITATION', 'HALLUCINATION', 'HELPFUL'
    comment TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_feedback_message_id ON message_feedback(message_id);

-- 6. Phân quyền và Row Level Security (RLS)
-- Vì đây là dữ liệu văn bản pháp luật công khai và phục vụ pipeline backend nạp dữ liệu:
ALTER TABLE legal_documents DISABLE ROW LEVEL SECURITY;
ALTER TABLE legal_articles DISABLE ROW LEVEL SECURITY;
ALTER TABLE conversations DISABLE ROW LEVEL SECURITY;
ALTER TABLE messages DISABLE ROW LEVEL SECURITY;
ALTER TABLE message_feedback DISABLE ROW LEVEL SECURITY;
