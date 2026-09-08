import re
from typing import List, Optional, Tuple
from pipeline.models import (
    LegalArticle,
    LegalClause,
    LegalPoint,
    LegalChapter,
    LegalDocumentMetadata,
    LegalDocumentParsed,
    LegalChunkPayload,
    DocumentStatus,
)


class LegalHierarchicalParser:
    """
    Parser sử dụng Regular Expression và Finite State Machine
    để phân tách văn bản quy phạm pháp luật Việt Nam thành cấu trúc cây:
    Văn bản -> Chương -> Điều -> Khoản -> Điểm.
    """

    RE_CHAPTER = re.compile(
        r"^(CHƯƠNG\s+[IVXLCDM\d]+)(?:[\s.:\n\-]+(.*))?$", re.IGNORECASE
    )
    RE_ARTICLE = re.compile(
        r"^Điều\s+(\d+)[\s.:\-]+(.*)$", re.IGNORECASE
    )
    RE_CLAUSE = re.compile(r"^(\d+)\.\s+(.*)$")
    RE_POINT = re.compile(r"^([a-zđ])\)\s+(.*)$", re.IGNORECASE)

    # Các cụm từ rác thường gặp cần loại bỏ
    RE_BOILERPLATE = re.compile(
        r"(CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM|Độc lập - Tự do - Hạnh phúc|Nơi nhận:|CHỦ TỊCH QUỐC HỘI|THỦ TƯỚNG CHÍNH PHỦ)",
        re.IGNORECASE,
    )

    def parse(self, raw_text: str, metadata: LegalDocumentMetadata) -> LegalDocumentParsed:
        lines = [line.strip() for line in raw_text.splitlines() if line.strip()]

        chapters: List[LegalChapter] = []
        all_articles: List[LegalArticle] = []

        current_chapter_num = "Chương I"
        current_chapter_title = "Những quy định chung"
        current_chapter_articles: List[LegalArticle] = []

        current_article: Optional[LegalArticle] = None
        current_clause: Optional[LegalClause] = None
        pending_chapter_title = False

        for line in lines:
            # 1. Bỏ qua các dòng boilerplate vô nghĩa
            if self.RE_BOILERPLATE.search(line) and len(line) < 80:
                continue

            # 2. Kiểm tra Chương
            chapter_match = self.RE_CHAPTER.match(line)
            if chapter_match:
                # Đóng điều luật cũ nếu có
                if current_article:
                    if current_clause:
                        current_article.clauses.append(current_clause)
                        current_clause = None
                    current_chapter_articles.append(current_article)
                    all_articles.append(current_article)
                    current_article = None

                # Đóng chương cũ nếu có điều luật
                if current_chapter_articles:
                    chapters.append(
                        LegalChapter(
                            chapter_number=current_chapter_num,
                            chapter_title=current_chapter_title,
                            articles=current_chapter_articles,
                        )
                    )
                    current_chapter_articles = []

                current_chapter_num = chapter_match.group(1).strip()
                title_part = chapter_match.group(2)
                if title_part and title_part.strip():
                    current_chapter_title = title_part.strip()
                    pending_chapter_title = False
                else:
                    current_chapter_title = "Quy định"
                    pending_chapter_title = True
                continue

            # Nếu đang chờ dòng tiếp theo là tiêu đề của chương
            if pending_chapter_title:
                if not self.RE_ARTICLE.match(line) and not self.RE_CHAPTER.match(line):
                    current_chapter_title = line.strip()
                    pending_chapter_title = False
                    continue
                pending_chapter_title = False

            # 3. Kiểm tra Điều
            article_match = self.RE_ARTICLE.match(line)
            if article_match:
                if current_article:
                    if current_clause:
                        current_article.clauses.append(current_clause)
                        current_clause = None
                    current_chapter_articles.append(current_article)
                    all_articles.append(current_article)

                art_num = int(article_match.group(1))
                art_title = article_match.group(2).strip() or None

                current_article = LegalArticle(
                    article_number=art_num,
                    article_title=art_title,
                    full_text=line,
                    clauses=[],
                    status=DocumentStatus.CON_HIEU_LUC,
                )
                continue

            # Nếu chưa vào Điều nào (phần mở đầu/căn cứ), bỏ qua hoặc lưu vào prelude
            if not current_article:
                continue

            # Cập nhật full_text của Điều
            current_article.full_text += f"\n{line}"

            # 4. Kiểm tra Khoản (vd: 1. , 2. )
            clause_match = self.RE_CLAUSE.match(line)
            if clause_match:
                if current_clause:
                    current_article.clauses.append(current_clause)

                cl_num = int(clause_match.group(1))
                cl_text = clause_match.group(2).strip()
                current_clause = LegalClause(
                    clause_number=cl_num, text=cl_text, points=[]
                )
                continue

            # 5. Kiểm tra Điểm (vd: a) , b) )
            point_match = self.RE_POINT.match(line)
            if point_match and current_clause:
                p_letter = point_match.group(1).lower()
                p_text = point_match.group(2).strip()
                current_clause.points.append(
                    LegalPoint(point_letter=p_letter, text=p_text)
                )
                continue

            # Dòng văn bản bình thường nối tiếp nội dung
            if current_clause:
                current_clause.text += f" {line}"
            elif current_article:
                # Điều không phân khoản (chỉ có 1 đoạn văn duy nhất)
                if not current_article.clauses:
                    current_clause = LegalClause(
                        clause_number=1, text=line, points=[]
                    )
                else:
                    current_article.clauses[-1].text += f" {line}"

        # Đóng điều và chương cuối cùng
        if current_article:
            if current_clause:
                current_article.clauses.append(current_clause)
            current_chapter_articles.append(current_article)
            all_articles.append(current_article)

        if current_chapter_articles:
            chapters.append(
                LegalChapter(
                    chapter_number=current_chapter_num,
                    chapter_title=current_chapter_title,
                    articles=current_chapter_articles,
                )
            )

        return LegalDocumentParsed(
            metadata=metadata, chapters=chapters, raw_articles=all_articles
        )

    def create_chunks(
        self, parsed_doc: LegalDocumentParsed
    ) -> List[LegalChunkPayload]:
        """
        Tạo danh sách các chunk có gắn Context Header sẵn sàng đẩy vào Vector Database.
        """
        chunks: List[LegalChunkPayload] = []
        meta = parsed_doc.metadata

        # Map article to chapter
        article_to_chapter = {}
        for ch in parsed_doc.chapters:
            for art in ch.articles:
                article_to_chapter[art.article_number] = f"{ch.chapter_number}: {ch.chapter_title}"

        for art in parsed_doc.raw_articles:
            chapter_info = article_to_chapter.get(art.article_number, "Quy định chung")
            context_header = (
                f"Văn bản: {meta.title} (Số hiệu: {meta.official_number}). "
                f"{chapter_info}. "
                f"Điều {art.article_number}: {art.article_title or ''}."
            )

            # Nếu Điều ngắn (< 1500 ký tự) -> Lưu nguyên Điều thành 1 Chunk
            if len(art.full_text) <= 1500 or not art.clauses:
                chunk_id = f"{meta.doc_id}_d{art.article_number}"
                chunks.append(
                    LegalChunkPayload(
                        chunk_id=chunk_id,
                        doc_id=meta.doc_id,
                        doc_title=meta.short_title or meta.title,
                        official_number=meta.official_number,
                        chapter=chapter_info,
                        article_number=art.article_number,
                        article_title=art.article_title,
                        clause_number=None,
                        status=art.status,
                        effective_date=meta.effective_date,
                        expiry_date=meta.expiry_date,
                        context_header=context_header,
                        content=art.full_text,
                        full_search_text=f"{context_header}\n{art.full_text}",
                        scope_tags=[meta.doc_type.value.lower()],
                    )
                )
            else:
                # Nếu Điều quá dài -> Tách nhỏ theo từng Khoản nhưng LUÔN gắn Context Header
                for cl in art.clauses:
                    chunk_id = f"{meta.doc_id}_d{art.article_number}_k{cl.clause_number}"
                    clause_content = f"Khoản {cl.clause_number}: {cl.text}"
                    if cl.points:
                        points_text = "\n".join(
                            [f"{p.point_letter}) {p.text}" for p in cl.points]
                        )
                        clause_content += f"\n{points_text}"

                    chunks.append(
                        LegalChunkPayload(
                            chunk_id=chunk_id,
                            doc_id=meta.doc_id,
                            doc_title=meta.short_title or meta.title,
                            official_number=meta.official_number,
                            chapter=chapter_info,
                            article_number=art.article_number,
                            article_title=art.article_title,
                            clause_number=cl.clause_number,
                            status=art.status,
                            effective_date=meta.effective_date,
                            expiry_date=meta.expiry_date,
                            context_header=context_header,
                            content=clause_content,
                            full_search_text=f"{context_header}\n{clause_content}",
                            scope_tags=[meta.doc_type.value.lower()],
                        )
                    )

        return chunks
