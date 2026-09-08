import os
import sys
import re
from typing import List, Dict, Any, Optional
from pathlib import Path
import requests

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.services.rag.embeddings import get_embedding_service, BaseEmbeddingService
from backend.app.services.rag.vector_store import QdrantVectorStore


class HybridRetriever:
    """
    Bộ truy xuất kết hợp tiên tiến (Advanced Multi-Intent Hybrid Search Retriever):
    1. Multi-Intent / Cross-Document Decomposition: Tự động phân tách câu hỏi đa chủ đề thành các Sub-queries.
    2. Dense Search: Vector search trên từng sub-query bằng BGE-M3 (chống Semantic Drift).
    3. Sparse Search: Trích xuất số hiệu Điều luật và cụm từ chuyên ngành qua Supabase.
    4. Full-Content Prioritization: Luôn lưu giữ chunk có nội dung đầy đủ và hoàn chỉnh nhất.
    5. Balanced Representation: Phân bổ công bằng quota vào Context cho từng văn bản luật liên quan.
    """

    def __init__(
        self,
        vector_store: Optional[QdrantVectorStore] = None,
        embedding_service: Optional[BaseEmbeddingService] = None,
        rrf_constant: int = 60,
    ):
        self.vector_store = vector_store or QdrantVectorStore()
        self.embedding_service = embedding_service or get_embedding_service()
        self.rrf_k = rrf_constant

        # Supabase config cho BM25 search
        self.supabase_url = os.getenv("SUPABASE_URL", "").rstrip("/")
        self.supabase_key = os.getenv("SUPABASE_KEY", "")

    def _decompose_query(self, query: str, as_of_date: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Phát hiện các ý định pháp lý độc lập trong câu hỏi đa văn bản / phức hợp
        (Cross-Document) và sinh ra các sub-queries trọng tâm có hỗ trợ Temporal / Version-Aware.

        Chiến lược:
        1. Ưu tiên nhận diện các legal intent có quan hệ phụ thuộc giữa nhiều văn bản.
        2. Nếu không thuộc cross-document intent đặc thù thì dùng các detector
           hiện tại (BHXH, BHTN, HĐLĐ, nghỉ hưu, xử phạt, kỷ luật).
        """
        q_lower = query.lower()
        sub_queries = []

        # ============================================================
        # 0. CROSS-DOCUMENT LEGAL DEPENDENCIES
        # ============================================================

        # ------------------------------------------------------------
        # Intent A: Cơ cấu lại doanh nghiệp / sáp nhập / chia tách
        # + dôi dư lao động / phương án sử dụng lao động
        #
        # BLLĐ 2019: Điều 44, Điều 47
        # NĐ 145/2020: Điều 8
        # ------------------------------------------------------------
        restructuring_keywords = [
            "sáp nhập",
            "hợp nhất",
            "chia",
            "tách",
            "chuyển nhượng",
            "chuyển quyền sở hữu",
            "cơ cấu lại",
            "cơ cấu lại lao động",
        ]

        redundant_labor_keywords = [
            "dôi dư lao động",
            "lao động dôi dư",
            "phải cho",
            "cho người lao động thôi việc",
            "cho người lao động nghỉ việc",
            "phương án sử dụng lao động",
            "trợ cấp mất việc",
            "mất việc làm",
        ]

        is_restructuring_intent = (
            any(kw in q_lower for kw in restructuring_keywords)
            and any(kw in q_lower for kw in redundant_labor_keywords)
        )

        if is_restructuring_intent:
            sub_queries.extend([
                {
                    "category": "restructuring_bllđ",
                    "doc_keyword": "bllđ",
                    "sub_query": (
                        "sáp nhập hợp nhất chia tách cơ cấu lại doanh nghiệp "
                        "phương án sử dụng lao động Điều 44 "
                        "Bộ luật Lao động 2019"
                    ),
                },
                {
                    "category": "redundancy_allowance_bllđ",
                    "doc_keyword": "bllđ",
                    "sub_query": (
                        "dôi dư lao động cho người lao động thôi việc "
                        "trợ cấp mất việc làm Điều 47 "
                        "mức trợ cấp mất việc làm "
                        "Bộ luật Lao động 2019"
                    ),
                },
                {
                    "category": "restructuring_nd145",
                    "doc_keyword": "145",
                    "sub_query": (
                        "phương án sử dụng lao động "
                        "Điều 8 Nghị định 145/2020/NĐ-CP"
                    ),
                },
            ])

        # ------------------------------------------------------------
        # Intent B: Chậm / thiếu / trốn đóng BHXH + xử phạt
        #
        # BLLĐ 2019: Điều 168
        # NĐ 12/2022: Điều 39
        # ------------------------------------------------------------
        late_bhxh_keywords = [
            "chậm đóng bảo hiểm xã hội",
            "chậm đóng bhxh",
            "đóng bhxh chậm",
            "nợ bảo hiểm xã hội",
            "nợ bhxh",
            "trốn đóng bảo hiểm xã hội",
            "trốn đóng bhxh",
            "không đóng bảo hiểm xã hội",
            "không đóng bhxh",
            "thiếu đóng bảo hiểm xã hội",
            "thiếu đóng bhxh",
        ]

        is_late_bhxh_intent = any(
            kw in q_lower for kw in late_bhxh_keywords
        )

        if is_late_bhxh_intent:
            sub_queries.extend([
                {
                    "category": "late_bhxh_bllđ",
                    "doc_keyword": "bllđ",
                    "sub_query": (
                        "trách nhiệm của người sử dụng lao động "
                        "tham gia đóng bảo hiểm xã hội bắt buộc "
                        "cho người lao động Điều 168 Bộ luật Lao động 2019"
                    ),
                },
                {
                    "category": "late_bhxh_penalty",
                    "doc_keyword": "nd_12",
                    "sub_query": (
                        "vi phạm quy định về đóng bảo hiểm xã hội bắt buộc "
                        "chậm đóng thiếu đóng trốn đóng "
                        "mức phạt tiền người sử dụng lao động "
                        "Điều 39 Nghị định 12/2022/NĐ-CP"
                    ),
                },
            ])

        # ------------------------------------------------------------
        # Intent C: Thay đổi người đại diện theo pháp luật
        #
        # LDN 2020: Điều 12
        # NĐ 01/2021: Điều 50
        # ------------------------------------------------------------
        legal_representative_keywords = [
            "thay đổi người đại diện theo pháp luật",
            "đổi người đại diện theo pháp luật",
            "thay người đại diện theo pháp luật",
            "người đại diện theo pháp luật",
        ]

        is_legal_representative_change = any(
            kw in q_lower for kw in legal_representative_keywords
        )

        if is_legal_representative_change:
            sub_queries.extend([
                {
                    "category": "legal_representative_ldn",
                    "doc_keyword": "ldn",
                    "sub_query": (
                        "người đại diện theo pháp luật "
                        "quyền nghĩa vụ thay đổi người đại diện "
                        "Điều 12 Luật Doanh nghiệp 2020"
                    ),
                },
                {
                    "category": "legal_representative_nd01",
                    "doc_keyword": "01_2021",
                    "sub_query": (
                        "hồ sơ đăng ký thay đổi người đại diện theo pháp luật "
                        "công ty trách nhiệm hữu hạn hai thành viên "
                        "Điều 50 Nghị định 01/2021/NĐ-CP"
                    ),
                },
            ])

        # ------------------------------------------------------------
        # Cross-Document Intent: Thuế TNDN + Quản lý thuế (Chậm nộp thuế TNDN)
        # ------------------------------------------------------------
        is_late_tndn_intent = (
            ("tndn" in q_lower or "thuế thu nhập doanh nghiệp" in q_lower)
            and ("chậm nộp" in q_lower or "quá hạn" in q_lower or "quản lý thuế" in q_lower)
        )
        if is_late_tndn_intent:
            sub_queries.extend([
                {
                    "category": "cross_tax_tndn",
                    "doc_keyword": "tndn",
                    "sub_query": (
                        "nghĩa vụ người nộp thuế thu nhập doanh nghiệp mức thuế suất thuế thu nhập doanh nghiệp 20% "
                        "Điều 2 Điều 10 Điều 11 Luật Thuế thu nhập doanh nghiệp 67/2025/QH15"
                    ),
                },
                {
                    "category": "cross_tax_qlt",
                    "doc_keyword": "qlt",
                    "sub_query": (
                        "thời hạn nộp thuế khoản thu khác xử lý đối với việc chậm nộp tiền thuế mức tính tiền chậm nộp 0,03% ngày "
                        "Điều 14 Điều 16 Luật Quản lý thuế 108/2025/QH15"
                    ),
                },
            ])

        # ============================================================
        # 1. CÁC DETECTOR HIỆN TẠI
        # ============================================================

        # ------------------------------------------------------------
        # Nhóm 1: Bảo hiểm xã hội / BHXH một lần
        # ------------------------------------------------------------
        has_bhxh = any(
            kw in q_lower
            for kw in [
                "bhxh",
                "bảo hiểm xã hội",
                "bhxh một lần",
                "rút bhxh",
                "điều 60",
                "điều 61",
                "điều 77",
            ]
        )

        # Nếu đã nhận diện một intent cross-document cụ thể về
        # chậm đóng BHXH thì không sinh thêm sub-query BHXH,
        # vì đây không phải tài liệu chính của câu hỏi.
        if has_bhxh and not is_late_bhxh_intent:
            if as_of_date and as_of_date >= "2025-07-01":
                if any(kw in q_lower for kw in ["lương hưu", "nghỉ hưu", "hưu trí", "điều 64", "15 năm"]):
                    sub_queries.append({
                        "category": "bhxh",
                        "doc_keyword": "bhxh",
                        "sub_query": (
                            "điều kiện hưởng lương hưu thời gian đóng bảo hiểm xã hội bắt buộc tối thiểu 15 năm "
                            "Điều 64 Luật Bảo hiểm xã hội 2024"
                        ),
                    })
                else:
                    sub_queries.append({
                        "category": "bhxh",
                        "doc_keyword": "bhxh",
                        "sub_query": (
                            "chế độ điều kiện hưởng bảo hiểm xã hội một lần rút một lần "
                            "Điều 70 Điều 102 Luật Bảo hiểm xã hội 2024"
                        ),
                    })
            else:
                sub_queries.append({
                    "category": "bhxh",
                    "doc_keyword": "bhxh",
                    "sub_query": (
                        "chế độ điều kiện hưởng bảo hiểm xã hội một lần "
                        "Điều 60 Điều 77 Luật Bảo hiểm xã hội 2014"
                    ),
                })

        # ------------------------------------------------------------
        # Nhóm 2: Bảo hiểm thất nghiệp / Trợ cấp thất nghiệp
        # ------------------------------------------------------------
        bhtn_keywords = [
            "bhtn",
            "thất nghiệp",
            "bảo hiểm thất nghiệp",
            "trợ cấp thất nghiệp",
            "điều 49",
            "điều 50",
            "điều 51",
            "điều 53",
        ]

        has_bhtn = any(
            kw in q_lower
            for kw in bhtn_keywords
        )

        bhtn_negated_patterns = [
            "không thuộc diện tham gia bhtn",
            "không tham gia bhtn",
            "không thuộc đối tượng tham gia bhtn",
            "không đóng bhtn",
            "không tham gia bảo hiểm thất nghiệp",
            "không đóng bảo hiểm thất nghiệp",
        ]

        bhtn_negated = any(
            pattern in q_lower
            for pattern in bhtn_negated_patterns
        )

        if bhtn_negated:
            has_bhtn = False

        if has_bhtn:
            sub_queries.append({
                "category": "bhtn",
                "doc_keyword": "vieclam",
                "sub_query": (
                    "điều kiện thời gian mức hưởng trợ cấp "
                    "bảo hiểm thất nghiệp Điều 49 Điều 50 Điều 51 "
                    "Luật Việc làm 2013"
                ),
            })

        # ------------------------------------------------------------
        # Nhóm 3: HĐLĐ / Thôi việc / Mất việc
        # ------------------------------------------------------------
        has_hdld = any(
            kw in q_lower
            for kw in [
                "chấm dứt hợp đồng",
                "thôi việc",
                "mất việc",
                "sa thải",
                "đơn phương",
                "hợp đồng lao động",
            ]
        )

        # Nếu đã có cross-document restructuring intent thì
        # sub-query BLLĐ đã được tạo với phạm vi chính xác hơn.
        if (
            has_hdld
            and not (has_bhxh and has_bhtn)
            and not is_restructuring_intent
            and not is_late_bhxh_intent
        ):
            sub_queries.append({
                "category": "hdld",
                "doc_keyword": "bllđ",
                "sub_query": (
                    "quyền lợi nghĩa vụ khi chấm dứt hợp đồng lao động "
                    "trợ cấp thôi việc mất việc làm "
                    "Bộ luật Lao động 2019"
                ),
            })

        # ------------------------------------------------------------
        # Nhóm 4: Nghỉ hưu / Tuổi nghỉ hưu
        # ------------------------------------------------------------
        has_retirement = any(
            kw in q_lower
            for kw in [
                "tuổi nghỉ hưu",
                "nghỉ hưu",
                "hưu trí",
                "lương hưu",
                "điều 169",
                "nghị định 135",
            ]
        )

        if has_retirement and not (has_bhxh and has_bhtn):
            sub_queries.append({
                "category": "retirement",
                "doc_keyword": "135",
                "sub_query": (
                    "tuổi nghỉ hưu điều kiện hưởng lương hưu "
                    "Điều 169 Bộ luật Lao động Nghị định 135"
                ),
            })

        # ------------------------------------------------------------
        # Nhóm 5: Xử phạt vi phạm hành chính
        # ------------------------------------------------------------
        has_penalty = any(
            kw in q_lower
            for kw in [
                "xử phạt",
                "phạt tiền",
                "mức phạt",
                "vi phạm hành chính",
                "nghị định 12",
            ]
        )

        # Nếu đã xử lý riêng intent chậm đóng BHXH thì NĐ12
        # đã được sinh ở cross-document section.
        if has_penalty and not is_late_bhxh_intent:
            sub_queries.append({
                "category": "penalty",
                "doc_keyword": "nd_12",
                "sub_query": (
                    "xử phạt vi phạm hành chính mức phạt tiền "
                    "Nghị định 12"
                ),
            })

        # ------------------------------------------------------------
        # Nhóm 6: Xử lý kỷ luật lao động / Sa thải
        # ------------------------------------------------------------
        has_discipline = any(
            kw in q_lower
            for kw in [
                "kỷ luật lao động",
                "sa thải",
                "xử lý kỷ luật",
                "họp kỷ luật",
                "điều 122",
                "điều 125",
            ]
        )

        if has_discipline:
            sub_queries.append({
                "category": "discipline",
                "doc_keyword": "bllđ",
                "sub_query": (
                    "nguyên tắc trình tự thủ tục xử lý kỷ luật lao động "
                    "sa thải Điều 122 Điều 125 "
                    "Bộ luật Lao động 2019"
                ),
            })

        # ------------------------------------------------------------
        # Nhóm 7: Bảo hiểm y tế (BHYT)
        # ------------------------------------------------------------
        has_bhyt = any(
            kw in q_lower
            for kw in [
                "bhyt",
                "bảo hiểm y tế",
                "khám chữa bệnh bảo hiểm y tế",
                "kcb bhyt",
                "thẻ bhyt",
                "mức hưởng bhyt",
                "thông tuyến",
                "chuyển tuyến",
            ]
        )
        if has_bhyt:
            sub_queries.append({
                "category": "bhyt",
                "doc_keyword": "bhyt",
                "sub_query": (
                    "quyền lợi mức hưởng khám chữa bệnh bảo hiểm y tế "
                    "Luật Bảo hiểm y tế sửa đổi 2024"
                ),
            })

        # ------------------------------------------------------------
        # Nhóm 8: Bộ luật Dân sự 2015 (Hợp đồng, Đặt cọc, Vay tài sản, Bồi thường, Thừa kế)
        # ------------------------------------------------------------
        # 8.1. Đặt cọc
        if any(kw in q_lower for kw in ["đặt cọc", "phạt cọc", "tiền cọc", "điều 328"]):
            sub_queries.append({
                "category": "deposit_blds",
                "doc_keyword": "blds",
                "sub_query": (
                    "quy định về đặt cọc xử lý tài sản đặt cọc phạt cọc khi từ chối giao kết thực hiện hợp đồng "
                    "Điều 328 Bộ luật Dân sự 2015"
                ),
            })

        # 8.2. Vay tài sản & Lãi suất
        if any(kw in q_lower for kw in ["vay tài sản", "cho vay", "lãi suất vay", "trần lãi suất", "lãi suất 20%", "điều 468"]):
            sub_queries.append({
                "category": "loan_interest_blds",
                "doc_keyword": "blds",
                "sub_query": (
                    "hợp đồng vay tài sản trần mức lãi suất vay tối đa 20% một năm "
                    "Điều 468 Bộ luật Dân sự 2015"
                ),
            })

        # 8.3. Bồi thường thiệt hại ngoài hợp đồng
        if any(kw in q_lower for kw in ["bồi thường thiệt hại ngoài hợp đồng", "thiệt hại ngoài hợp đồng", "thời hiệu bồi thường", "điều 584", "điều 588"]):
            sub_queries.append({
                "category": "tort_damages_blds",
                "doc_keyword": "blds",
                "sub_query": (
                    "căn cứ phát sinh trách nhiệm và thời hiệu khởi kiện yêu cầu bồi thường thiệt hại ngoài hợp đồng 03 năm "
                    "Điều 584 Điều 588 Bộ luật Dân sự 2015"
                ),
            })

        # 8.4. Thừa kế & Di chúc
        if any(kw in q_lower for kw in ["thừa kế", "di chúc", "chia di sản", "mở thừa kế", "không phụ thuộc", "điều 611", "điều 623", "điều 644"]):
            sub_queries.append({
                "category": "inheritance_blds",
                "doc_keyword": "blds",
                "sub_query": (
                    "thừa kế theo di chúc theo pháp luật mở thừa kế thời hiệu chia di sản thừa kế 30 năm người thừa kế không phụ thuộc vào nội dung của di chúc "
                    "Điều 611 Điều 623 Điều 644 Bộ luật Dân sự 2015"
                ),
            })

        # 8.5. Giao dịch dân sự vô hiệu
        if any(kw in q_lower for kw in ["giao dịch dân sự", "vô hiệu", "hợp đồng vô hiệu", "điều kiện có hiệu lực", "điều 117", "điều 131"]):
            sub_queries.append({
                "category": "invalid_transaction_blds",
                "doc_keyword": "blds",
                "sub_query": (
                    "điều kiện có hiệu lực của giao dịch dân sự và hậu quả pháp lý của giao dịch dân sự vô hiệu "
                    "Điều 117 Điều 131 Bộ luật Dân sự 2015"
                ),
            })

        # ------------------------------------------------------------
        # Nhóm 9: Cụm Thuế 2025/2026 (Thuế TNCN, Thuế TNDN, Luật Quản lý thuế)
        # ------------------------------------------------------------
        # 9.1. Thuế TNCN: Biểu thuế luỹ tiến từng phần & Tính thuế tiền lương
        if any(kw in q_lower for kw in ["biểu thuế luỹ tiến", "biểu thuế lũy tiến", "bậc thuế", "thuế suất tncn", "lũy tiến từng phần", "thuế thu nhập cá nhân đối với thu nhập từ tiền lương", "điều 9"]):
            sub_queries.extend([
                {
                    "category": "tncn_progressive_tax",
                    "doc_keyword": "tncn",
                    "target_article": 9,
                    "sub_query": (
                        "biểu thuế luỹ tiến từng phần bậc 1 bậc 2 bậc 3 bậc 4 bậc 5 thuế suất 5% 10% 20% 30% 35% "
                        "Điều 9 Luật Thuế thu nhập cá nhân 109/2025/QH15"
                    ),
                },
                {
                    "category": "tncn_salary_tax",
                    "doc_keyword": "tncn",
                    "target_article": 8,
                    "sub_query": (
                        "thuế thu nhập cá nhân đối với thu nhập từ tiền lương tiền công cá nhân cư trú thu nhập tính thuế "
                        "Điều 8 Luật Thuế thu nhập cá nhân 109/2025/QH15"
                    ),
                },
            ])

        # 9.2. Thuế TNCN: Giảm trừ gia cảnh
        if any(kw in q_lower for kw in ["giảm trừ gia cảnh", "người phụ thuộc", "giảm trừ bản thân", "15,5 triệu", "6,2 triệu", "nuôi dưỡng", "điều 10"]):
            sub_queries.append({
                "category": "tncn_deduction",
                "doc_keyword": "tncn",
                "sub_query": (
                    "mức giảm trừ gia cảnh người nộp thuế 15,5 triệu đồng người phụ thuộc 6,2 triệu đồng nguyên tắc giảm trừ "
                    "Điều 10 Luật Thuế thu nhập cá nhân 109/2025/QH15"
                ),
            })

        # 9.3. Thuế TNDN: Thuế suất phổ thông & Ưu đãi
        if any(kw in q_lower for kw in ["thuế suất tndn", "thuế suất thuế thu nhập doanh nghiệp", "tndn 20%", "doanh thu dưới 3 tỷ", "thuế suất 15%", "thuế suất 17%", "điều 10"]):
            sub_queries.append({
                "category": "tndn_rate",
                "doc_keyword": "tndn",
                "sub_query": (
                    "thuế suất thuế thu nhập doanh nghiệp 20% doanh nghiệp có tổng doanh thu năm không quá 3 tỷ 15% từ trên 3 đến 50 tỷ 17% "
                    "Điều 10 Luật Thuế thu nhập doanh nghiệp 67/2025/QH15"
                ),
            })

        # 9.4. Thuế TNDN: Chi phí được trừ & Hóa đơn chứng từ
        if any(kw in q_lower for kw in ["chi phí được trừ", "chi phí không được trừ", "khoản chi được trừ", "hóa đơn", "thanh toán không dùng tiền mặt", "điều 9"]):
            sub_queries.append({
                "category": "tndn_deductible_expenses",
                "doc_keyword": "tndn",
                "sub_query": (
                    "các khoản chi được trừ và không được trừ khi xác định thu nhập chịu thuế TNDN hóa đơn chứng từ "
                    "Điều 9 Luật Thuế thu nhập doanh nghiệp 67/2025/QH15"
                ),
            })

        # 9.5. Quản lý thuế: Thời hạn nộp thuế & Tờ khai
        if any(kw in q_lower for kw in ["thời hạn nộp thuế", "thời hạn nộp tờ khai", "thời hạn khai thuế", "hồ sơ khai thuế", "tờ khai quý", "quyết toán năm", "điều 12", "điều 14"]):
            sub_queries.append({
                "category": "qlt_filing_deadline",
                "doc_keyword": "qlt",
                "sub_query": (
                    "thời hạn nộp thuế chậm nhất là ngày cuối cùng của thời hạn nộp hồ sơ khai thuế khai theo quý quyết toán năm "
                    "Điều 14 Điều 12 Luật Quản lý thuế 108/2025/QH15"
                ),
            })

        # 9.6. Quản lý thuế: Xử lý chậm nộp tiền thuế 0,03%/ngày
        if any(kw in q_lower for kw in ["chậm nộp", "tiền chậm nộp", "0,03%", "0,03%/ngày", "chậm nộp tiền thuế", "điều 16"]):
            sub_queries.append({
                "category": "qlt_late_payment",
                "doc_keyword": "qlt",
                "sub_query": (
                    "xử lý đối với việc chậm nộp tiền thuế mức tính tiền chậm nộp bằng 0,03% ngày tính trên số tiền thuế chậm nộp "
                    "Điều 16 Luật Quản lý thuế 108/2025/QH15"
                ),
            })

        return sub_queries


    def _dense_search(self, query: str, limit: int = 15, as_of_date: Optional[str] = None) -> List[Dict[str, Any]]:
        """Tìm kiếm theo vector ngữ nghĩa trên Qdrant có hỗ trợ Temporal Filtering"""
        query_vector = self.embedding_service.embed_query(query)
        results = self.vector_store.search_similar(query_vector=query_vector, limit=limit, as_of_date=as_of_date)
        return results

    def _sparse_search_bm25(self, query: str, limit: int = 30, as_of_date: Optional[str] = None) -> List[Dict[str, Any]]:
        """Tìm kiếm từ khóa và số hiệu điều luật chính xác trên Supabase có hỗ trợ Temporal Filtering"""
        if not self.supabase_url or not self.supabase_key:
            return []

        headers = {
            "apikey": self.supabase_key,
            "Authorization": f"Bearer {self.supabase_key}",
        }
        endpoint = f"{self.supabase_url}/rest/v1/legal_articles"
        results = []
        seen_keys = set()

        # Lấy danh sách doc_ids hợp lệ theo as_of_date từ legal_documents nếu có
        valid_doc_ids = None
        if as_of_date:
            try:
                doc_params = {
                    "select": "id",
                    "effective_date": f"lte.{as_of_date}",
                    "or": f"(expiry_date.is.null,expiry_date.gte.{as_of_date})",
                }
                r_doc = requests.get(
                    f"{self.supabase_url}/rest/v1/legal_documents",
                    headers=headers,
                    params=doc_params,
                    timeout=5,
                )
                if r_doc.status_code == 200:
                    valid_doc_ids = set(d["id"] for d in r_doc.json())
            except Exception as e:
                print(f"[!] Lỗi truy vấn legal_documents theo thời gian: {e}")

        # 1. Trích xuất các số hiệu Điều được nhắc đến trực tiếp (ví dụ: 'Điều 60', 'Điều 49')
        art_nums = re.findall(r"(?:điều|khoản)\s*(\d+)", query.lower())
        q_l = query.lower()
        if any(term in q_l for term in ["biểu thuế luỹ tiến", "biểu thuế lũy tiến", "biểu thuế 5 bậc"]):
            art_nums.extend(["9", "8"])
        if "giảm trừ gia cảnh" in q_l:
            art_nums.append("10")
        if "chi phí được trừ" in q_l or "khoản chi được trừ" in q_l:
            art_nums.append("9")
        if "chậm nộp" in q_l:
            art_nums.append("16")
        if "thời hạn nộp thuế" in q_l:
            art_nums.append("14")

        for num_str in set(art_nums):
            try:
                num = int(num_str)
                params = {
                    "article_number": f"eq.{num}",
                    "select": "document_id,article_number,article_title,full_text,chapter_info,status",
                    "limit": "25",
                }
                res = requests.get(endpoint, headers=headers, params=params, timeout=5)
                if res.status_code == 200:
                    for a in res.json():
                        doc_id = a.get("document_id", "")
                        if valid_doc_ids is not None and doc_id not in valid_doc_ids:
                            continue
                        key = f"{doc_id}_{a.get('article_number')}"
                        if key not in seen_keys:
                            seen_keys.add(key)
                            doc_title = self._get_doc_title(doc_id)
                            results.append({
                                "doc_id": doc_id,
                                "doc_title": doc_title,
                                "article_number": a.get("article_number"),
                                "article_title": a.get("article_title"),
                                "chapter": a.get("chapter_info"),
                                "content": a.get("full_text"),
                                "context_header": f"{doc_title}. {a.get('chapter_info')}. Điều {a.get('article_number')}: {a.get('article_title')}",
                            })
            except Exception as e:
                print(f"[!] Lỗi truy vấn điều số: {e}")

        # 2. Tìm kiếm theo tiêu đề bài viết (article_title ilike) cho các cụm từ pháp lý quan trọng
        target_phrases = []
        q_lower = query.lower()
        if "bảo hiểm xã hội một lần" in q_lower or "bhxh một lần" in q_lower or "rút bhxh" in q_lower:
            target_phrases.append("bảo hiểm xã hội một lần")
        if "trợ cấp thất nghiệp" in q_lower or "bảo hiểm thất nghiệp" in q_lower:
            target_phrases.append("thất nghiệp")
        if "nghỉ hưu" in q_lower or "hưu trí" in q_lower:
            target_phrases.append("nghỉ hưu")
        if "biểu thuế" in q_lower or "lũy tiến" in q_lower or "luỹ tiến" in q_lower:
            target_phrases.append("biểu thuế")
        if "giảm trừ gia cảnh" in q_lower:
            target_phrases.append("giảm trừ")
        if "chậm nộp" in q_lower:
            target_phrases.append("chậm nộp")

        for phrase in target_phrases:
            try:
                params = {
                    "article_title": f"ilike.*{phrase}*",
                    "select": "document_id,article_number,article_title,full_text,chapter_info,status",
                    "limit": "5",
                }
                res = requests.get(endpoint, headers=headers, params=params, timeout=5)
                if res.status_code == 200:
                    for a in res.json():
                        doc_id = a.get("document_id", "")
                        if valid_doc_ids is not None and doc_id not in valid_doc_ids:
                            continue
                        key = f"{doc_id}_{a.get('article_number')}"
                        if key not in seen_keys:
                            seen_keys.add(key)
                            doc_title = self._get_doc_title(doc_id)
                            results.append({
                                "doc_id": doc_id,
                                "doc_title": doc_title,
                                "article_number": a.get("article_number"),
                                "article_title": a.get("article_title"),
                                "chapter": a.get("chapter_info"),
                                "content": a.get("full_text"),
                                "context_header": f"{doc_title}. {a.get('chapter_info')}. Điều {a.get('article_number')}: {a.get('article_title')}",
                            })
            except Exception as e:
                print(f"[!] Lỗi truy vấn cụm từ: {e}")

        return results[:limit]

    def _get_doc_title(self, doc_id: str) -> str:
        """Quy đổi mã văn bản sang tên chính thức đầy đủ"""
        if "bhxh_41" in doc_id or "41_2024" in doc_id:
            return "Luật Bảo hiểm xã hội 2024"
        elif "bhxh" in doc_id:
            return "Luật Bảo hiểm xã hội 2014"
        elif "bhyt" in doc_id or "51_2024" in doc_id:
            return "Luật Bảo hiểm y tế sửa đổi 2024"
        elif "vieclam" in doc_id:
            return "Luật Việc làm 2013"
        elif "145" in doc_id:
            return "Nghị định 145/2020/NĐ-CP"
        elif "135" in doc_id:
            return "Nghị định 135/2020/NĐ-CP"
        elif "122" in doc_id:
            return "Nghị định 122/2021/NĐ-CP"
        elif "nd_12" in doc_id:
            return "Nghị định 12/2022/NĐ-CP"
        elif "01_2021" in doc_id:
            return "Nghị định 01/2021/NĐ-CP"
        elif "ldn" in doc_id:
            return "Luật Doanh nghiệp 2020"
        elif "blds" in doc_id or "91_2015" in doc_id:
            return "Bộ luật Dân sự 2015"
        elif "tncn" in doc_id or "109_2025" in doc_id:
            return "Luật Thuế thu nhập cá nhân 2025"
        elif "tndn" in doc_id or "67_2025" in doc_id:
            return "Luật Thuế thu nhập doanh nghiệp 2025"
        elif "qlt" in doc_id or "108_2025" in doc_id:
            return "Luật Quản lý thuế 2025"
        elif "bllđ" in doc_id or "bld" in doc_id:
            return "Bộ luật Lao động 2019"
        return "Văn bản Quy phạm Pháp luật"

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        use_reranker: bool = False,
        as_of_date: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Thực thi Multi-Intent Hybrid Search và phân bổ ngữ cảnh cân bằng (Balanced Context Allocation)
        có hỗ trợ Temporal / Version-Aware:
        1. Query Decomposition & Temporal Inference: Tách các ý định pháp lý và xác định mốc thời gian áp dụng.
        2. Multi-branch Dense Search + Accurate Sparse BM25 Search kèm Temporal Filter.
        3. Full-Text Merging: Luôn ưu tiên chunk có nội dung đầy đủ nhất của mỗi Điều luật.
        4. Cross-Encoder Reranking: Chấm điểm tương quan ngữ nghĩa.
        5. Balanced Diversity Context Allocation: Đảm bảo công bằng quota cho mỗi văn bản luật.
        """
        # Tự động suy luận mốc thời gian áp dụng từ câu hỏi nếu chưa truyền
        if not as_of_date:
            q_lower = query.lower()
            if any(term in q_lower for term in ["trước 01/07/2025", "trước ngày 01/07/2025", "trước tháng 7/2025", "trước 2025", "năm 2024", "năm 2023", "năm 2022", "luật cũ", "luật 2014"]):
                as_of_date = "2024-12-31"
            elif any(term in q_lower for term in ["từ 01/07/2025", "từ ngày 01/07/2025", "sau ngày 01/07/2025", "sau 01/07/2025", "luật 2024", "luật bhxh 2024", "luật mới", "năm 2026"]):
                as_of_date = "2026-09-08"
            else:
                as_of_date = "2026-09-08"

        sub_query_configs = self._decompose_query(query, as_of_date=as_of_date)
        is_multi_intent = len(sub_query_configs) >= 2

        doc_store: Dict[str, Dict[str, Any]] = {}
        rrf_scores: Dict[str, float] = {}

        # 1. Thu thập ứng viên từ Dense Retrieval (Query gốc + các Sub-queries)
        search_queries = [query]
        for item in sub_query_configs:
            search_queries.append(item["sub_query"])

        for q_idx, q_text in enumerate(search_queries):
            hits = self._dense_search(q_text, limit=15, as_of_date=as_of_date)
            for rank, hit in enumerate(hits, start=1):
                art_num = hit.get("article_number")
                if not art_num:
                    continue
                doc_id = hit.get("doc_id", "bllđ_45_2019_qh14")
                key = f"{doc_id}_{art_num}"
                weight = 1.0 if q_idx == 0 else 1.3
                rrf_scores[key] = rrf_scores.get(key, 0.0) + (weight / (self.rrf_k + rank))

                # Ưu tiên chunk có nội dung dài/đầy đủ hơn
                if key not in doc_store or len(hit.get("content", "")) > len(doc_store[key].get("content", "")):
                    doc_store[key] = hit

        # 2. Thu thập ứng viên từ Sparse Search (BM25 & Title Match & Article Number)
        sparse_hits = self._sparse_search_bm25(query, limit=15, as_of_date=as_of_date)
        for rank, hit in enumerate(sparse_hits, start=1):
            art_num = hit.get("article_number")
            if not art_num:
                continue
            doc_id = hit.get("doc_id", "bllđ_45_2019_qh14")
            key = f"{doc_id}_{art_num}"
            rrf_scores[key] = rrf_scores.get(key, 0.0) + (1.3 / (self.rrf_k + rank))

            # Luôn ưu tiên chunk từ Supabase vì chứa full_text đầy đủ các khoản
            if key not in doc_store or len(hit.get("content", "")) > len(doc_store[key].get("content", "")):
                doc_store[key] = hit

        # 3. Lọc bỏ các Điều hưu trí gây nhiễu nếu câu hỏi hỏi về BHXH một lần khi nghỉ việc (không hỏi lương hưu)
        q_lower = query.lower()
        is_bhxh_mot_lan_query = ("bhxh một lần" in q_lower or "bảo hiểm xã hội một lần" in q_lower or "rút bhxh" in q_lower) and "tuổi nghỉ hưu" not in q_lower and "lương hưu" not in q_lower and "hưu trí" not in q_lower

        filtered_scores = {}
        for key, score in rrf_scores.items():
            if is_bhxh_mot_lan_query and any(key.endswith(f"_{noise}") for noise in [58, 75]):
                continue  # Loại bỏ hoàn toàn Điều 58, 75 hưu trí để không cướp chỗ của Điều 60
            filtered_scores[key] = score

        # Sắp xếp theo điểm RRF tổng hợp
        sorted_articles = sorted(filtered_scores.items(), key=lambda x: x[1], reverse=True)

        candidate_pool_size = 40 if is_multi_intent else (top_k * 4 if use_reranker else top_k * 2)
        candidate_pool = []
        for key, score in sorted_articles[:candidate_pool_size]:
            item = doc_store[key].copy()
            item["rrf_score"] = score
            candidate_pool.append(item)


        # 4. Rerank bằng Cross-Encoder (Reranker)
        final_ranked = candidate_pool
        if use_reranker and candidate_pool:
            try:
                from backend.app.services.rag.reranker import get_reranker_service
                reranker = get_reranker_service()
                final_ranked = reranker.rerank(query=query, candidates=candidate_pool, top_k=len(candidate_pool))
            except Exception as e:
                print(f"[!] Reranker lỗi, fallback về RRF: {e}")

        # 5. Phân bổ cân bằng đa văn bản (Balanced Cross-Document Representation)
        effective_top_k = max(top_k, 5) if is_multi_intent else top_k

        if is_multi_intent and sub_query_configs:
            selected_items = []
            selected_keys = set()

            # Vòng 1: Chọn chunk tốt nhất của từng chủ đề/văn bản
            for cfg in sub_query_configs:
                doc_kw = cfg["doc_keyword"]
                target_art = cfg.get("target_article")
                category_hits = [c for c in final_ranked if doc_kw in c.get("doc_id", "").lower()]

                matched_target = None
                if target_art:
                    for h in category_hits:
                        if h.get("article_number") == target_art:
                            matched_target = h
                            break

                chosen = matched_target if (matched_target and f"{matched_target.get('doc_id')}_{matched_target.get('article_number')}" not in selected_keys) else None
                if not chosen:
                    for hit in category_hits:
                        key = f"{hit.get('doc_id')}_{hit.get('article_number')}"
                        if key not in selected_keys:
                            chosen = hit
                            break

                if chosen:
                    key = f"{chosen.get('doc_id')}_{chosen.get('article_number')}"
                    selected_keys.add(key)
                    selected_items.append(chosen)

            # Vòng 2: Lấy thêm chunk thứ 2 của từng chủ đề nếu còn slot
            for cfg in sub_query_configs:
                if len(selected_items) >= effective_top_k:
                    break
                doc_kw = cfg["doc_keyword"]
                category_hits = [c for c in final_ranked if doc_kw in c.get("doc_id", "").lower()]
                for hit in category_hits[1:3]:
                    key = f"{hit.get('doc_id')}_{hit.get('article_number')}"
                    if key not in selected_keys and len(selected_items) < effective_top_k:
                        selected_keys.add(key)
                        selected_items.append(hit)

            # Vòng 3: Lấp đầy các slot còn lại theo thứ tự điểm rerank/RRF cao nhất
            for item in final_ranked:
                if len(selected_items) >= effective_top_k:
                    break
                key = f"{item.get('doc_id')}_{item.get('article_number')}"
                if key not in selected_keys:
                    selected_keys.add(key)
                    selected_items.append(item)

            return selected_items

        return final_ranked[:effective_top_k]

    def close(self):
        """Đóng kết nối Vector Store khi kết thúc"""
        if hasattr(self.vector_store, "close"):
            self.vector_store.close()
