import re
from typing import List, Dict, Any, Optional, Set, Tuple


class LegalPoint:
    """Đại diện cho một Điểm trong Khoản (ví dụ: Điểm a, Điểm b, Điểm c...)"""

    def __init__(self, point_char: str, content: str):
        self.point_char = point_char.strip().lower()
        self.content = content.strip()

    def __repr__(self):
        return f"<Point {self.point_char}) len={len(self.content)}>"


class LegalClause:
    """Đại diện cho một Khoản trong Điều luật (ví dụ: Khoản 1, Khoản 2, Khoản 16...)"""

    def __init__(self, clause_number: int, header: str, raw_text: str):
        self.clause_number = clause_number
        self.header = header.strip()
        self.raw_text = raw_text.strip()
        self.points: Dict[str, LegalPoint] = {}
        self._parse_points()

    def _parse_points(self):
        """Phân tích các Điểm a), b), c)... bên trong Khoản"""
        # Pattern nhận diện điểm đầu dòng: a), b), c), ..., đ)
        pattern = re.compile(r"(?:^|\n)\s*([a-zđ])\)\s+", re.IGNORECASE)
        matches = list(pattern.finditer(self.raw_text))
        if not matches:
            return

        for i, match in enumerate(matches):
            p_char = match.group(1).lower()
            start_pos = match.end()
            end_pos = matches[i + 1].start() if i + 1 < len(matches) else len(self.raw_text)
            p_content = self.raw_text[start_pos:end_pos].strip()
            self.points[p_char] = LegalPoint(point_char=p_char, content=p_content)

    def format_clause(self, selected_points: Optional[Set[str]] = None) -> str:
        """Định dạng lại văn bản Khoản; nếu có selected_points chỉ format các điểm đó"""
        if not selected_points or not self.points:
            return f"{self.clause_number}. {self.raw_text}"

        lines = [f"{self.clause_number}. {self.header}"]
        for p_char in sorted(selected_points):
            if p_char in self.points:
                lines.append(f"  {p_char}) {self.points[p_char].content}")
        return "\n".join(lines)

    def __repr__(self):
        return f"<Clause {self.clause_number} points={list(self.points.keys())} len={len(self.raw_text)}>"


class ParsedLegalArticle:
    """Biểu diễn toàn bộ Điều luật sau khi phân tích cú pháp"""

    def __init__(self, article_number: int, article_title: str, full_text: str):
        self.article_number = article_number
        self.article_title = article_title
        self.full_text = full_text
        self.preamble: str = ""
        self.clauses: Dict[int, LegalClause] = {}
        self._parse_clauses()

    def _parse_clauses(self):
        """Phân tách toàn văn Điều luật thành danh sách các Khoản"""
        # Pattern nhận diện đầu Khoản: 1. , 2. , 3. ... ở đầu dòng hoặc sau \n
        pattern = re.compile(r"(?:^|\n)\s*(\d+)\.\s+", re.MULTILINE)
        matches = list(pattern.finditer(self.full_text))

        if not matches:
            return

        self.preamble = self.full_text[: matches[0].start()].strip()

        for i, match in enumerate(matches):
            c_num = int(match.group(1))
            start_pos = match.end()
            end_pos = matches[i + 1].start() if i + 1 < len(matches) else len(self.full_text)
            raw_chunk = self.full_text[start_pos:end_pos].strip()

            # Tách header dòng đầu tiên của Khoản nếu có các Điểm
            lines = raw_chunk.split("\n", 1)
            first_line = lines[0].strip()

            self.clauses[c_num] = LegalClause(
                clause_number=c_num,
                header=first_line,
                raw_text=raw_chunk,
            )


class DeterministicClauseExtractor:
    """
    Bộ bóc tách Khoản/Điểm tất định (Deterministic Clause Extractor):
    Tuân thủ tuyệt đối nguyên tắc:
    1. Không dùng LLM -> Tốc độ vài mili-giây, zero cost, zero latency overhead.
    2. Minimal Sufficient Evidence: Giữ đúng Khoản vi phạm + Khoản trừ điểm GPLX / Chế tài bổ sung liên đới.
    3. Evidence Validator & Fallback: Luôn fallback về full text nếu việc lọc không đảm bảo an toàn pháp lý.
    """

    @classmethod
    def parse_article(cls, article_number: int, article_title: str, full_text: str) -> ParsedLegalArticle:
        return ParsedLegalArticle(article_number, article_title, full_text)

    @classmethod
    def extract_relevant_context(
        cls,
        article_number: int,
        article_title: str,
        full_text: str,
        query: str,
        doc_id: str = "",
    ) -> Tuple[str, bool]:
        """
        Trích xuất các Khoản/Điểm trúng đích cho câu hỏi.
        Trả về tuple: (extracted_text, is_extracted).
        Nếu fallback về full_text thì is_extracted = False.
        """
        if not full_text or len(full_text) < 300:
            return full_text, False

        parsed = cls.parse_article(article_number, article_title, full_text)
        if not parsed.clauses:
            return full_text, False

        q_lower = query.lower()
        selected_clause_nums: Set[int] = set()
        selected_points_map: Dict[int, Set[str]] = {}

        # =========================================================================
        # 1. LỚP 2: TARGET RESOLVER — TÌM KIẾM HÀNH VI VI PHẠM TRỰC TIẾP (DIRECT MATCH)
        # =========================================================================
        # Các nhóm hành vi phổ biến và từ khóa nhận diện chuyên sâu
        keywords_speed = ["tốc độ", "quá tốc độ", "km/h"]
        keywords_red_light = ["đèn đỏ", "tín hiệu giao thông", "hiệu lệnh của đèn"]
        keywords_alcohol = ["nồng độ cồn", "hơi thở", "khí thở", "miligam", "rượu, bia", "uống rượu"]
        keywords_wrong_way_highway = ["ngược chiều", "đường cao tốc", "cao tốc"]
        keywords_helmet = ["mũ bảo hiểm"]
        keywords_license_point_rule = ["trừ điểm giấy phép lái xe", "nhiều hành vi", "trừ nhiều điểm nhất"]

        is_speed_query = any(k in q_lower for k in keywords_speed)
        is_red_light_query = any(k in q_lower for k in keywords_red_light)
        is_alcohol_query = any(k in q_lower for k in keywords_alcohol)
        is_wrong_way_highway_query = any(k in q_lower for k in keywords_wrong_way_highway)

        # Trích xuất số tốc độ cụ thể nếu có (ví dụ 25 km/h, 15 km/h...)
        speed_match = re.search(r"(\d+)\s*km\s*/\s*h", q_lower)
        target_speed = int(speed_match.group(1)) if speed_match else None

        # Trích xuất nồng độ cồn cụ thể nếu có (ví dụ 0,35 mg)
        alcohol_match = re.search(r"(\d+[,\.]\d+)\s*(?:mg|miligam)", q_lower)
        target_alcohol_mg = float(alcohol_match.group(1).replace(",", ".")) if alcohol_match else None

        for c_num, clause in parsed.clauses.items():
            c_text_lower = clause.raw_text.lower()

            # Bỏ qua các khoản quy định về trừ điểm / chế tài bổ sung ở vòng này (sẽ resolve ở cross-reference)
            if "trừ điểm giấy phép lái xe" in c_text_lower and "phạt tiền từ" not in c_text_lower:
                continue
            if "hình thức xử phạt bổ sung" in c_text_lower and "phạt tiền từ" not in c_text_lower:
                continue

            match_clause = False

            # Case A: Vượt đèn đỏ
            if is_red_light_query:
                if any(k in c_text_lower for k in ["đèn tín hiệu", "hiệu lệnh của đèn", "tín hiệu giao thông"]):
                    if "phạt tiền từ" in c_text_lower or "phạt" in c_text_lower:
                        # Chỉ chọn điểm có liên quan đến đèn tín hiệu
                        has_red_light_pt = False
                        for p_char, pt in clause.points.items():
                            if any(k in pt.content.lower() for k in ["đèn tín hiệu", "hiệu lệnh của đèn", "tín hiệu giao thông"]):
                                selected_points_map.setdefault(c_num, set()).add(p_char)
                                has_red_light_pt = True
                        if has_red_light_pt or not clause.points:
                            match_clause = True

            # Case B: Tốc độ
            if is_speed_query and not match_clause:
                if "tốc độ" in c_text_lower:
                    if target_speed is not None:
                        # 1. Khung dạng "trên X km/h đến Y km/h" hoặc "từ X km/h đến Y km/h"
                        bracket_match = re.search(r"(?:từ|trên)\s*(\d+)\s*km/h\s*(?:đến|tới)\s*(\d+)\s*km/h", c_text_lower)
                        if bracket_match:
                            low_b = int(bracket_match.group(1))
                            high_b = int(bracket_match.group(2))
                            if low_b <= target_speed <= high_b:
                                match_clause = True
                                for p_char, pt in clause.points.items():
                                    if f"{low_b}" in pt.content.lower() and f"{high_b}" in pt.content.lower():
                                        selected_points_map.setdefault(c_num, set()).add(p_char)
                        # 2. Khung dạng "trên X km/h" (ví dụ trên 35 km/h)
                        above_match = re.search(r"(?:trên|vượt quá)\s*(\d+)\s*km/h", c_text_lower)
                        if above_match and not match_clause:
                            above_b = int(above_match.group(1))
                            if target_speed > above_b and "đến" not in c_text_lower.split(above_match.group(0))[1][:20]:
                                match_clause = True
                                for p_char, pt in clause.points.items():
                                    if f"{above_b}" in pt.content.lower():
                                        selected_points_map.setdefault(c_num, set()).add(p_char)
                    else:
                        # Nếu không có số km/h cụ thể trong câu hỏi, chỉ lấy các khoản quy định chạy quá tốc độ
                        if "chạy quá tốc độ quy định" in c_text_lower:
                            match_clause = True

            # Case C: Nồng độ cồn
            if is_alcohol_query:
                if any(k in c_text_lower for k in ["nồng độ cồn", "khí thở", "miligam", "trong máu"]):
                    if target_alcohol_mg is not None:
                        # Kiểm tra dải nồng độ cồn:
                        if target_alcohol_mg <= 0.25:
                            if "chưa vượt quá" in c_text_lower or "chưa quá" in c_text_lower:
                                match_clause = True
                                for p_char, pt in clause.points.items():
                                    if "chưa vượt quá" in pt.content.lower():
                                        selected_points_map.setdefault(c_num, set()).add(p_char)
                        elif 0.25 < target_alcohol_mg <= 0.4:
                            if "0,25" in c_text_lower and "0,4" in c_text_lower:
                                match_clause = True
                                for p_char, pt in clause.points.items():
                                    if "0,25" in pt.content.lower() and "0,4" in pt.content.lower():
                                        selected_points_map.setdefault(c_num, set()).add(p_char)
                        elif target_alcohol_mg > 0.4:
                            if "vượt quá 0,4" in c_text_lower or "vượt quá 80" in c_text_lower:
                                match_clause = True
                                for p_char, pt in clause.points.items():
                                    if "vượt quá 0,4" in pt.content.lower():
                                        selected_points_map.setdefault(c_num, set()).add(p_char)
                    else:
                        match_clause = True

            # Case D: Ngược chiều trên cao tốc
            if is_wrong_way_highway_query:
                if "ngược chiều" in c_text_lower and any(k in c_text_lower for k in ["cao tốc", "đường cao tốc"]):
                    has_hwy_pt = False
                    for p_char, pt in clause.points.items():
                        if "ngược chiều" in pt.content.lower() and any(k in pt.content.lower() for k in ["cao tốc", "đường cao tốc"]):
                            selected_points_map.setdefault(c_num, set()).add(p_char)
                            has_hwy_pt = True
                    if has_hwy_pt or not clause.points:
                        match_clause = True

            if match_clause:
                selected_clause_nums.add(c_num)

        # Nếu không bắt được bằng rule chuyên sâu, tìm kiếm lexical overlap cơ bản
        if not selected_clause_nums:
            for c_num, clause in parsed.clauses.items():
                c_text_lower = clause.raw_text.lower()
                # Tìm các câu hỏi trực diện
                overlap_count = sum(1 for word in q_lower.split() if len(word) > 3 and word in c_text_lower)
                if overlap_count >= 3 and ("phạt tiền" in c_text_lower or "phạt" in c_text_lower):
                    selected_clause_nums.add(c_num)

        # =========================================================================
        # 2. LỚP 2 (TIẾP): CROSS-REFERENCE RESOLUTION (CHẾ TÀI TRỪ ĐIỂM / PHẠT BỔ SUNG)
        # =========================================================================
        # Quét các Khoản quy định về trừ điểm GPLX hoặc phạt bổ sung
        penalty_clause_nums: Set[int] = set()
        for c_num, clause in parsed.clauses.items():
            c_text_lower = clause.raw_text.lower()
            if any(k in c_text_lower for k in ["trừ điểm giấy phép lái xe", "hình thức xử phạt bổ sung", "tước quyền sử dụng"]):
                penalty_clause_nums.add(c_num)

        # Trong các penalty clauses, tìm các Điểm viện dẫn đến selected_clause_nums
        for p_cnum in penalty_clause_nums:
            penalty_clause = parsed.clauses[p_cnum]
            has_relevant_point = False

            for pt_char, pt in penalty_clause.points.items():
                pt_text_lower = pt.content.lower()

                # Kiểm tra xem Điểm này có viện dẫn tới các Khoản đã chọn không
                # Ví dụ: "khoản 6", "khoản 7", "khoản 9", "khoản 11"
                for sel_cnum in selected_clause_nums:
                    ref_clause_pattern = rf"khoản\s+{sel_cnum}\b"
                    if re.search(ref_clause_pattern, pt_text_lower):
                        # Nếu có lọc điểm cụ thể ở Khoản vi phạm, xem Điểm chế tài có khớp không
                        sel_points = selected_points_map.get(sel_cnum, set())
                        if sel_points:
                            # Kiểm tra xem có trỏ đúng điểm không, hoặc trỏ cả khoản
                            point_matched = False
                            for sp in sel_points:
                                ref_point_pattern = rf"điểm\s+{sp}\b"
                                if re.search(ref_point_pattern, pt_text_lower):
                                    point_matched = True
                                    break
                            # Nếu cả khoản bị trừ điểm (ví dụ: "khoản 6... Điều này bị trừ")
                            if f"khoản {sel_cnum}" in pt_text_lower and "điểm" not in pt_text_lower.split(f"khoản {sel_cnum}")[0][-15:]:
                                point_matched = True

                            if point_matched:
                                selected_points_map.setdefault(p_cnum, set()).add(pt_char)
                                has_relevant_point = True
                        else:
                            selected_points_map.setdefault(p_cnum, set()).add(pt_char)
                            has_relevant_point = True

            if has_relevant_point or (not penalty_clause.points and any(f"khoản {sc}" in penalty_clause.raw_text.lower() for sc in selected_clause_nums)):
                selected_clause_nums.add(p_cnum)

        # =========================================================================
        # 3. LỚP 3: EVIDENCE VALIDATOR & COMPACT CONTEXT ASSEMBLER
        # =========================================================================
        # Quy tắc Fallback An Toàn Tuyệt Đối:
        # Nếu không trích xuất được khoản nào, hoặc Điều luật quá ngắn, hoặc Điều 50 (nguyên tắc xử lý tổng thể)
        if not selected_clause_nums:
            return full_text, False

        # Đối với các điều luật có tính nguyên tắc chung như Điều 50 (Trừ điểm GPLX khi vi phạm nhiều hành vi)
        # Nếu query hỏi nhiều hành vi, chỉ trích xuất Khoản 1 Điều 50 (Khoản chứa điểm b cốt lõi)
        if article_number == 50 and 1 in parsed.clauses:
            selected_clause_nums = {1}

        # Lắp ghép các Khoản đã chọn
        compact_blocks = []
        doc_header = f"Điều {article_number}. {article_title}"
        compact_blocks.append(doc_header)
        compact_blocks.append("[CÁC ĐIỀU KHOẢN TRÍCH XUẤT ÁP DỤNG TRỰC TIẾP]:")

        sorted_clauses = sorted(selected_clause_nums)
        for c_num in sorted_clauses:
            clause = parsed.clauses[c_num]
            sel_pts = selected_points_map.get(c_num)
            formatted = clause.format_clause(selected_points=sel_pts)
            compact_blocks.append(formatted)

        compact_text = "\n\n".join(compact_blocks).strip()

        # Evidence Validator:
        # Kiểm tra nếu độ dài kết quả trích xuất < 150 chars hoặc quá hụt
        if len(compact_text) < 150:
            return full_text, False

        # Kiểm tra nếu câu hỏi hỏi phạt tiền mà không có chữ 'đồng' trong compact_text
        if ("phạt bao nhiêu tiền" in q_lower or "mức phạt" in q_lower) and "đồng" not in compact_text:
            return full_text, False

        return compact_text, True
