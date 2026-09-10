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


LEGAL_DOCUMENT_TEMPORAL_REGISTRY = {
    # Mảng Giao thông đường bộ - Hiệu lực thời gian chuẩn hóa
    "108/2026/TT-BCA": {"effective_from": "2026-07-01", "effective_to": None},
    "traffic_driving_license_108_2026_tt_bca": {"effective_from": "2026-07-01", "effective_to": None},
    "12/2025/TT-BCA": {"effective_from": "2025-03-01", "effective_to": "2026-06-30", "transition_until": "2027-02-28"},
    "traffic_driving_license_12_2025_tt_bca": {"effective_from": "2025-03-01", "effective_to": "2026-06-30", "transition_until": "2027-02-28"},
    "79/2024/TT-BCA": {"effective_from": "2025-01-01", "effective_to": None},
    "traffic_vehicle_registration_79_2024_tt_bca": {"effective_from": "2025-01-01", "effective_to": None},
    "13/2025/TT-BCA": {"effective_from": "2025-03-01", "effective_to": None},
    "traffic_amendment_13_2025_tt_bca": {"effective_from": "2025-03-01", "effective_to": None},
    "51/2025/TT-BCA": {"effective_from": "2025-07-01", "effective_to": None},
    "traffic_amendment_51_2025_tt_bca": {"effective_from": "2025-07-01", "effective_to": None},
    "38/2024/TT-BGTVT": {"effective_from": "2025-01-01", "effective_to": None},
    "traffic_speed_distance_38_2024_tt_bgtvt": {"effective_from": "2025-01-01", "effective_to": None},
    "105/2026/TT-BCA": {"effective_from": "2026-07-01", "effective_to": None},
    "traffic_points_recovery_105_2026_tt_bca": {"effective_from": "2026-07-01", "effective_to": None},
    "73/2024/TT-BCA": {"effective_from": "2025-01-01", "effective_to": None},
    "traffic_patrol_inspection_73_2024_tt_bca": {"effective_from": "2025-01-01", "effective_to": None},
    "65/2024/TT-BCA": {"effective_from": "2025-01-01", "effective_to": None},
    "traffic_points_recovery_65_2024_tt_bca": {"effective_from": "2025-01-01", "effective_to": None},
    "28/2024/TT-BCA": {"effective_from": "2024-07-01", "effective_to": None},
    "traffic_amendment_28_2024_tt_bca": {"effective_from": "2024-07-01", "effective_to": None},
    "89/2026/NĐ-CP": {"effective_from": "2026-07-01", "effective_to": None},
    "traffic_vehicle_lifespan_89_2026_nd_cp": {"effective_from": "2026-07-01", "effective_to": None},
    "30/2026/TT-BXD": {"effective_from": "2026-07-01", "effective_to": None},
    "traffic_vehicle_inspection_30_2026_tt_bxd": {"effective_from": "2026-07-01", "effective_to": None},
    "12/2025/TT-BXD": {"effective_from": "2025-03-01", "effective_to": None},
    "traffic_road_weight_12_2025_tt_bxd": {"effective_from": "2025-03-01", "effective_to": None},
    "19/2026/TT-BXD": {"effective_from": "2026-05-15", "effective_to": None},
    "traffic_amendment_19_2026_tt_bxd": {"effective_from": "2026-05-15", "effective_to": None},
    "36/2024/QH15": {"effective_from": "2025-01-01", "effective_to": None},
    "traffic_order_36_2024_qh15": {"effective_from": "2025-01-01", "effective_to": None},
    "168/2024/NĐ-CP": {"effective_from": "2025-01-01", "effective_to": None},
    "traffic_penalty_168_2024_nd_cp": {"effective_from": "2025-01-01", "effective_to": None},
    "238/2026/NĐ-CP": {"effective_from": "2026-07-01", "effective_to": None},
    "traffic_penalty_amendment_238_2026_nd_cp": {"effective_from": "2026-07-01", "effective_to": None},
    # Batch P1.2
    "94/2026/NĐ-CP": {"effective_from": "2026-07-01", "effective_to": None},
    "traffic_driver_training_94_2026_nd_cp": {"effective_from": "2026-07-01", "effective_to": None},
    "241/2026/NĐ-CP": {"effective_from": "2026-07-01", "effective_to": None},
    "traffic_road_infra_amendment_241_2026_nd_cp": {"effective_from": "2026-07-01", "effective_to": None},
    "45/2026/TT-BXD": {"effective_from": "2026-07-01", "effective_to": None},
    "traffic_inspection_amendment_45_2026_tt_bxd": {"effective_from": "2026-07-01", "effective_to": None},
    "51/2024/TT-BGTVT": {"effective_from": "2025-01-01", "effective_to": None},
    "traffic_road_signs_qcvn41_51_2024_tt_bgtvt": {"effective_from": "2025-01-01", "effective_to": None},
}


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
        dense_weight: float = 1.0,
        sparse_weight: float = 0.1,
        enable_query_decomposition: Optional[bool] = None,
    ):
        self.vector_store = vector_store or QdrantVectorStore()
        self.embedding_service = embedding_service or get_embedding_service()
        self.rrf_k = rrf_constant
        self.dense_weight = dense_weight
        self.sparse_weight = sparse_weight

        # Feature flag for Query Decomposition (Default: False as determined by Gold Retrieval failure diagnosis)
        if enable_query_decomposition is not None:
            self.enable_query_decomposition = enable_query_decomposition
        else:
            self.enable_query_decomposition = os.getenv("ENABLE_QUERY_DECOMPOSITION", "false").lower() in ("true", "1", "yes")

        # Supabase config cho BM25 search & Target Article Hydration
        self.supabase_url = os.getenv("SUPABASE_URL", "").rstrip("/")
        self.supabase_key = os.getenv("SUPABASE_KEY", "")
        self._full_article_cache: Dict[tuple, Dict[str, Any]] = {}

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
                    "target_article": 44,
                    "sub_query": (
                        "sáp nhập hợp nhất chia tách cơ cấu lại doanh nghiệp "
                        "phương án sử dụng lao động Điều 44 "
                        "Bộ luật Lao động 2019"
                    ),
                },
                {
                    "category": "redundancy_allowance_bllđ",
                    "doc_keyword": "bllđ",
                    "target_article": 47,
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
                    "target_article": 8,
                    "sub_query": (
                        "thời gian làm việc để tính trợ cấp mất việc làm "
                        "Điều 8 Nghị định 145/2020/NĐ-CP"
                    ),
                },
            ])

        # ------------------------------------------------------------
        # Cross-Document Intent: Trợ cấp thôi việc (BLLĐ) vs Trợ cấp thất nghiệp (Luật Việc làm) (TC-02)
        # BLLĐ 2019: Điều 46, Điều 47 | Luật Việc làm 2013: Điều 49, 50
        # ------------------------------------------------------------
        is_severance_vs_bhtn_intent = (
            ("thôi việc" in q_lower or "trợ cấp thôi việc" in q_lower)
            and ("thất nghiệp" in q_lower or "trợ cấp thất nghiệp" in q_lower or "bhtn" in q_lower)
            and any(k in q_lower for k in ["khác nhau", "phân biệt", "ai chi trả", "hai khoản", "cả hai", "chế độ nào", "quyền lợi nào"])
        )

        if is_severance_vs_bhtn_intent:
            sub_queries.extend([
                {
                    "category": "severance_allowance",
                    "doc_keyword": "bllđ",
                    "target_article": 46,
                    "sub_query": (
                        "trách nhiệm chi trả điều kiện thời gian làm việc tính trợ cấp thôi việc Điều 46 "
                        "Bộ luật Lao động 2019"
                    ),
                },
                {
                    "category": "unemployment_benefit",
                    "doc_keyword": "vieclam",
                    "target_article": 50,
                    "sub_query": (
                        "quỹ bảo hiểm thất nghiệp điều kiện mức thời gian hưởng trợ cấp thất nghiệp Điều 49 Điều 50 "
                        "Luật Việc làm 2013"
                    ),
                },
            ])

        # ------------------------------------------------------------
        # Legal Dependency Intent: Tính tiền trợ cấp thôi việc / thời gian làm việc có tháng lẻ (TC-19)
        # BLLĐ 2019: Điều 46 (Căn cứ chung)
        # NĐ 145/2020: Điều 8 (Quy định chi tiết thời gian làm việc & làm tròn tháng lẻ)
        # ------------------------------------------------------------
        severance_calc_keywords = [
            "tính trợ cấp thôi việc",
            "tính tiền trợ cấp thôi việc",
            "thời gian làm việc để tính trợ cấp",
            "tháng lẻ",
            "làm tròn",
        ]
        is_severance_calc_intent = (
            any(kw in q_lower for kw in severance_calc_keywords)
            or (
                ("trợ cấp thôi việc" in q_lower or "thôi việc" in q_lower)
                and any(t in q_lower for t in ["làm việc từ", "đến ngày", "tháng lẻ", "làm tròn", "bao nhiêu năm", "bao nhiêu tháng", "phải trả"])
            )
        ) and not is_severance_vs_bhtn_intent

        if is_severance_calc_intent:
            sub_queries.extend([
                {
                    "category": "severance_allowance",
                    "doc_keyword": "bllđ",
                    "target_article": 46,
                    "sub_query": (
                        "trách nhiệm chi trả điều kiện mức hưởng trợ cấp thôi việc Điều 46 "
                        "Bộ luật Lao động 2019"
                    ),
                },
                {
                    "category": "severance_working_time",
                    "doc_keyword": "145",
                    "target_article": 8,
                    "sub_query": (
                        "thời gian làm việc để tính trợ cấp thôi việc "
                        "thời gian lẻ tháng quy định làm tròn "
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

        if has_bhtn and not is_severance_vs_bhtn_intent:
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
            and not is_severance_vs_bhtn_intent
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
        # Nhóm 4: Nghỉ hưu / Tuổi nghỉ hưu vs Thời điểm hưởng hưu trí (TC-20)
        # ------------------------------------------------------------
        is_retirement_timing_intent = (
            any(kw in q_lower for kw in ["thời điểm hưởng", "bắt đầu hưởng", "ngày hưởng", "thời điểm nghỉ hưu", "thời điểm bắt đầu hưởng"])
            or ("thời điểm" in q_lower and ("hưu" in q_lower or "nghỉ hưu" in q_lower or "hưu trí" in q_lower))
        )

        is_retirement_age_lookup = (
            any(kw in q_lower for kw in ["sinh năm", "sinh tháng", "tháng sinh", "năm sinh", "bao nhiêu tuổi", "độ tuổi nào", "lộ trình", "bảng tra cứu", "phụ lục i", "phụ lục 1", "phụ lục ii", "điều 169"])
            or ("tuổi nghỉ hưu" in q_lower and any(kw in q_lower for kw in ["nam", "nữ", "bao nhiêu", "năm nào", "thời điểm nào", "lộ trình", "là bao nhiêu"]))
        )

        if is_retirement_timing_intent:
            sub_queries.append({
                "category": "retirement_timing",
                "doc_keyword": "135",
                "target_article": 3,
                "sub_query": (
                    "thời điểm nghỉ hưu thời điểm hưởng chế độ hưu trí "
                    "ngày đầu tiên của tháng liền kề Điều 3 "
                    "Nghị định 135/2020/NĐ-CP"
                ),
            })
        elif is_retirement_age_lookup and not (has_bhxh and has_bhtn):
            sub_queries.append({
                "category": "retirement_age_lookup",
                "doc_keyword": "135",
                "sub_query": (
                    "tuổi nghỉ hưu điều kiện hưởng lương hưu "
                    "Điều 169 Bộ luật Lao động Nghị định 135"
                ),
            })

        # Nhóm 5: Xử phạt vi phạm hành chính trong lĩnh vực lao động (NĐ 12/2022)
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

        is_traffic_query = any(
            kw in q_lower
            for kw in [
                "giao thông", "mũ bảo hiểm", "xe máy", "mô tô", "ô tô",
                "đèn đỏ", "tốc độ", "gplx", "bằng lái", "đường bộ", "trừ điểm"
            ]
        )

        # Nếu đã xử lý riêng intent chậm đóng BHXH hoặc vi phạm giao thông thì không tạo sub-query NĐ12 lao động.
        if has_penalty and not is_late_bhxh_intent and not is_traffic_query:
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

        # ------------------------------------------------------------
        # Nhóm 10: Cụm Bất động sản & Đầu tư (Phase 3)
        # ------------------------------------------------------------
        # 10.1. Đặt cọc mua bán nhà ở hình thành trong tương lai (tối đa 5% giá bán)
        if any(kw in q_lower for kw in ["đặt cọc", "tiền đặt cọc", "mức đặt cọc", "5%", "năm phần trăm", "giữ chỗ"]) and any(kw in q_lower for kw in ["bất động sản", "nhà ở", "hình thành trong tương lai", "chung cư", "chủ đầu tư", "kinh doanh bất động sản"]):
            sub_queries.append({
                "category": "re_deposit_limit",
                "doc_keyword": "re_business",
                "target_article": 23,
                "sub_query": (
                    "nguyên tắc kinh doanh nhà ở công trình xây dựng hình thành trong tương lai thu tiền đặt cọc không quá 5% giá bán cho thuê mua đủ điều kiện "
                    "Điều 23 Luật Kinh doanh bất động sản 29/2023/QH15"
                ),
            })
            if any(kw in q_lower for kw in ["dân sự", "328", "blds", "tự do thỏa thuận"]):
                sub_queries.append({
                    "category": "re_deposit_civil_comparison",
                    "doc_keyword": "blds",
                    "target_article": 328,
                    "sub_query": (
                        "quy định về đặt cọc xử lý tài sản đặt cọc thỏa thuận của các bên "
                        "Điều 328 Bộ luật Dân sự 2015"
                    ),
                })

        # 10.2. Điều kiện mở bán nhà ở hình thành trong tương lai & Nghiệm thu móng
        if any(kw in q_lower for kw in ["điều kiện bán", "mở bán", "đưa vào kinh doanh", "nghiệm thu phần móng", "nghiệm thu móng", "bảo lãnh", "giấy phép xây dựng"]) and any(kw in q_lower for kw in ["hình thành trong tương lai", "nhà ở", "công trình", "chung cư", "kinh doanh bất động sản"]):
            sub_queries.append({
                "category": "re_future_house_conditions",
                "doc_keyword": "re_business",
                "target_article": 24,
                "sub_query": (
                    "điều kiện của nhà ở công trình xây dựng hình thành trong tương lai được đưa vào kinh doanh giấy phép xây dựng biên bản nghiệm thu phần móng bảo lãnh ngân hàng "
                    "Điều 24 Luật Kinh doanh bất động sản 29/2023/QH15"
                ),
            })

        # 10.3. Điều kiện chuyển nhượng quyền sử dụng đất (Điều 45 Luật Đất đai 2024)
        if any(kw in q_lower for kw in ["chuyển nhượng quyền sử dụng đất", "điều kiện chuyển nhượng", "chuyển nhượng đất", "thực hiện các quyền"]) and any(kw in q_lower for kw in ["đất đai", "quyền sử dụng đất", "giấy chứng nhận", "sổ đỏ"]):
            sub_queries.append({
                "category": "land_transfer_conditions",
                "doc_keyword": "land",
                "target_article": 45,
                "sub_query": (
                    "điều kiện thực hiện các quyền chuyển đổi chuyển nhượng cho thuê thừa kế tặng cho quyền sử dụng đất Giấy chứng nhận không tranh chấp không kê biên còn thời hạn sử dụng đất "
                    "Điều 45 Luật Đất đai 31/2024/QH15"
                ),
            })

        # 10.4. Bảng giá đất & Nguyên tắc định giá đất thị trường (Điều 158, 159 Luật Đất đai 2024)
        if any(kw in q_lower for kw in ["bảng giá đất", "định giá đất", "khung giá đất", "nguyên tắc thị trường", "ban hành bảng giá đất", "giá đất"]):
            sub_queries.extend([
                {
                    "category": "land_valuation_principles",
                    "doc_keyword": "land",
                    "target_article": 158,
                    "sub_query": (
                        "nguyên tắc căn cứ phương pháp định giá đất theo nguyên tắc thị trường "
                        "Điều 158 Luật Đất đai 31/2024/QH15"
                    ),
                },
                {
                    "category": "land_price_table",
                    "doc_keyword": "land",
                    "target_article": 159,
                    "sub_query": (
                        "bảng giá đất do Ủy ban nhân dân cấp tỉnh xây dựng Hội đồng nhân dân thông qua ban hành áp dụng từ ngày 01 tháng 01 năm 2026 điều chỉnh bổ sung hàng năm "
                        "Điều 159 Luật Đất đai 31/2024/QH15"
                    ),
                },
            ])

        # 10.5. Nhà ở xã hội: Đối tượng, điều kiện hưởng & Thời hạn 5 năm chuyển nhượng
        if any(kw in q_lower for kw in ["nhà ở xã hội", "noxh", "mua nhà ở xã hội", "thuê mua nhà ở xã hội"]):
            if any(kw in q_lower for kw in ["đối tượng", "điều kiện", "thu nhập", "chưa có nhà"]):
                sub_queries.extend([
                    {
                        "category": "housing_social_target",
                        "doc_keyword": "housing",
                        "target_article": 76,
                        "sub_query": (
                            "đối tượng được hưởng chính sách hỗ trợ về nhà ở xã hội người có công hộ nghèo cận nghèo thu nhập thấp công nhân "
                            "Điều 76 Luật Nhà ở 27/2023/QH15"
                        ),
                    },
                    {
                        "category": "housing_social_conditions",
                        "doc_keyword": "housing",
                        "target_article": 78,
                        "sub_query": (
                            "điều kiện được hưởng chính sách hỗ trợ về nhà ở xã hội điều kiện về nhà ở và điều kiện về thu nhập "
                            "Điều 78 Luật Nhà ở 27/2023/QH15"
                        ),
                    },
                ])
            if any(kw in q_lower for kw in ["bán lại", "chuyển nhượng", "5 năm", "05 năm", "bán nhà"]):
                sub_queries.append({
                    "category": "housing_social_resale_5years",
                    "doc_keyword": "housing",
                    "target_article": 89,
                    "sub_query": (
                        "bán lại chuyển nhượng nhà ở xã hội thời hạn tối thiểu 05 năm kể từ ngày thanh toán hết tiền mua chỉ được bán lại cho chủ đầu tư hoặc nộp tiền sử dụng đất "
                        "Điều 89 Luật Nhà ở 27/2023/QH15"
                    ),
                })

        # 10.6. Chấp thuận chủ trương đầu tư & Giao đất qua đấu giá / đấu thầu dự án
        if any(kw in q_lower for kw in ["chấp thuận chủ trương đầu tư", "chủ trương đầu tư", "lựa chọn nhà đầu tư"]) and any(kw in q_lower for kw in ["đất", "giao đất", "đấu giá", "đấu thầu", "dự án"]):
            sub_queries.extend([
                {
                    "category": "investment_project_approval",
                    "doc_keyword": "investment",
                    "target_article": 32,
                    "sub_query": (
                        "thẩm quyền chấp thuận chủ trương đầu tư của Ủy ban nhân dân cấp tỉnh đối với dự án đầu tư xây dựng nhà ở khu đô thị "
                        "Điều 32 Điều 29 Luật Đầu tư 61/2020/QH14"
                    ),
                },
                {
                    "category": "land_auction_bidding",
                    "doc_keyword": "land",
                    "target_article": 125,
                    "sub_query": (
                        "giao đất cho thuê đất thông qua đấu giá quyền sử dụng đất đấu thầu lựa chọn nhà đầu tư thực hiện dự án có sử dụng đất "
                        "Điều 125 Điều 126 Luật Đất đai 31/2024/QH15"
                    ),
                },
            ])

        # ============================================================
        # 11. CỤM PHÁP LUẬT GIAO THÔNG ĐƯỜNG BỘ (PHASE 4A)
        # ============================================================
        traffic_triggers = [
            "giao thông", "xe máy", "mô tô", "ô tô", "xe gắn máy", "xe tải", "xe khách",
            "vượt đèn đỏ", "đèn đỏ", "đèn vàng", "đèn tín hiệu", "tốc độ", "quá tốc độ",
            "nồng độ cồn", "mũ bảo hiểm", "bằng lái", "gplx", "giấy phép lái xe",
            "trừ điểm", "tước bằng", "tước gplx", "phục hồi điểm", "đường cao tốc",
            "tai nạn giao thông", "đăng ký xe", "biển số", "đi ngược chiều", "làn đường",
            "01/01/2025", "15/08/2026", "01/08/2026", "168/2024", "238/2026", "quy định này áp dụng từ"
        ]

        if any(kw in q_lower for kw in traffic_triggers):
            is_car = bool(re.search(r"(?<!m)ô\s*tô", q_lower) or any(kw in q_lower for kw in ["xe con", "xe tải", "xe khách", "xe 4 bánh", "bốn bánh"]))
            is_bike = any(kw in q_lower for kw in ["xe máy", "mô tô", "xe gắn máy", "xe 2 bánh", "hai bánh"])

            # 11.1. Intent: Vượt đèn đỏ / Chấp hành hiệu lệnh đèn tín hiệu giao thông
            if any(kw in q_lower for kw in ["vượt đèn đỏ", "đèn đỏ", "đèn vàng", "tín hiệu giao thông", "hiệu lệnh của đèn"]):
                if is_car:
                    sub_queries.extend([
                        {
                            "category": "traffic_penalty_car_red_light",
                            "doc_keyword": "traffic_penalty",
                            "target_article": 6,
                            "sub_query": (
                                "người điều khiển xe ô tô không chấp hành hiệu lệnh của đèn tín hiệu giao thông vượt đèn đỏ mức phạt tiền "
                                "Điều 6 Nghị định 168/2024/NĐ-CP"
                            ),
                        },
                        {
                            "category": "traffic_rule_signals",
                            "doc_keyword": "traffic_order",
                            "target_article": 11,
                            "sub_query": (
                                "chấp hành báo hiệu đường bộ hiệu lệnh của đèn tín hiệu giao thông tín hiệu đỏ vàng xanh "
                                "Điều 11 Luật Trật tự an toàn giao thông đường bộ 36/2024/QH15"
                            ),
                        },
                    ])
                else:
                    sub_queries.extend([
                        {
                            "category": "traffic_penalty_bike_red_light",
                            "doc_keyword": "traffic_penalty",
                            "target_article": 7,
                            "sub_query": (
                                "người điều khiển xe mô tô xe gắn máy không chấp hành hiệu lệnh của đèn tín hiệu giao thông vượt đèn đỏ mức phạt tiền "
                                "Điều 7 Nghị định 168/2024/NĐ-CP"
                            ),
                        },
                        {
                            "category": "traffic_rule_signals",
                            "doc_keyword": "traffic_order",
                            "target_article": 11,
                            "sub_query": (
                                "chấp hành báo hiệu đường bộ hiệu lệnh của đèn tín hiệu giao thông tín hiệu đỏ vàng xanh "
                                "Điều 11 Luật Trật tự an toàn giao thông đường bộ 36/2024/QH15"
                            ),
                        },
                    ])

            # 11.2. Intent: Vi phạm tốc độ (Chạy quá tốc độ quy định) & Trừ điểm GPLX
            if any(kw in q_lower for kw in ["tốc độ", "quá tốc độ", "km/h", "chạy quá"]):
                if is_bike:
                    sub_queries.extend([
                        {
                            "category": "traffic_penalty_bike_speed",
                            "doc_keyword": "traffic_penalty",
                            "target_article": 7,
                            "sub_query": (
                                "người điều khiển xe mô tô xe gắn máy chạy quá tốc độ quy định mức phạt tiền trừ điểm GPLX "
                                "Điều 7 Nghị định 168/2024/NĐ-CP"
                            ),
                        },
                        {
                            "category": "traffic_rule_speed",
                            "doc_keyword": "traffic_order",
                            "target_article": 12,
                            "sub_query": (
                                "chấp hành quy định về tốc độ và khoảng cách an toàn giữa các xe khi tham gia giao thông "
                                "Điều 12 Luật Trật tự an toàn giao thông đường bộ 36/2024/QH15"
                            ),
                        },
                    ])
                else:
                    sub_queries.extend([
                        {
                            "category": "traffic_penalty_car_speed",
                            "doc_keyword": "traffic_penalty",
                            "target_article": 6,
                            "sub_query": (
                                "người điều khiển xe ô tô chạy quá tốc độ quy định từ 20 km/h mức phạt tiền và trừ điểm giấy phép lái xe "
                                "Điều 6 Nghị định 168/2024/NĐ-CP"
                            ),
                        },
                        {
                            "category": "traffic_rule_speed",
                            "doc_keyword": "traffic_order",
                            "target_article": 12,
                            "sub_query": (
                                "chấp hành quy định về tốc độ và khoảng cách an toàn giữa các xe khi tham gia giao thông "
                                "Điều 12 Luật Trật tự an toàn giao thông đường bộ 36/2024/QH15"
                            ),
                        },
                    ])

            # 11.3. Intent: Vi phạm nồng độ cồn / Rượu bia
            if any(kw in q_lower for kw in ["nồng độ cồn", "rượu bia", "uống rượu", "uống bia", "khí thở", "máu"]):
                if is_car:
                    sub_queries.extend([
                        {
                            "category": "traffic_penalty_car_alcohol",
                            "doc_keyword": "traffic_penalty",
                            "target_article": 6,
                            "sub_query": (
                                "xử phạt người điều khiển xe ô tô trong máu hoặc hơi thở có nồng độ cồn mức phạt tiền trừ điểm tước GPLX "
                                "Điều 6 Nghị định 168/2024/NĐ-CP"
                            ),
                        },
                        {
                            "category": "traffic_rule_prohibited_alcohol",
                            "doc_keyword": "traffic_order",
                            "target_article": 9,
                            "sub_query": (
                                "nghiêm cấm điều khiển phương tiện tham gia giao thông đường bộ mà trong máu hoặc hơi thở có nồng độ cồn "
                                "Điều 9 Luật Trật tự an toàn giao thông đường bộ 36/2024/QH15"
                            ),
                        },
                    ])
                else:
                    sub_queries.extend([
                        {
                            "category": "traffic_penalty_bike_alcohol",
                            "doc_keyword": "traffic_penalty",
                            "target_article": 7,
                            "sub_query": (
                                "xử phạt người điều khiển xe mô tô xe gắn máy trong máu hoặc hơi thở có nồng độ cồn mức phạt tiền trừ điểm "
                                "Điều 7 Nghị định 168/2024/NĐ-CP"
                            ),
                        },
                        {
                            "category": "traffic_rule_prohibited_alcohol",
                            "doc_keyword": "traffic_order",
                            "target_article": 9,
                            "sub_query": (
                                "nghiêm cấm điều khiển phương tiện tham gia giao thông đường bộ mà trong máu hoặc hơi thở có nồng độ cồn "
                                "Điều 9 Luật Trật tự an toàn giao thông đường bộ 36/2024/QH15"
                            ),
                        },
                    ])

            # 11.4. Intent: Không đội mũ bảo hiểm / Chở người không đội mũ bảo hiểm
            if any(kw in q_lower for kw in ["mũ bảo hiểm", "nón bảo hiểm", "cài quai"]):
                sub_queries.extend([
                    {
                        "category": "traffic_penalty_helmet",
                        "doc_keyword": "traffic_penalty",
                        "target_article": 7,
                        "sub_query": (
                            "không đội mũ bảo hiểm cho người đi mô tô xe máy hoặc chở người không đội mũ bảo hiểm mức phạt tiền "
                            "Điều 7 Nghị định 168/2024/NĐ-CP"
                        ),
                    },
                    {
                        "category": "traffic_rule_helmet",
                        "doc_keyword": "traffic_order",
                        "target_article": 33,
                        "sub_query": (
                            "người lái xe mô tô hai bánh xe gắn máy người được chở phải đội mũ bảo hiểm có cài quai đúng quy cách "
                            "Điều 33 Luật Trật tự an toàn giao thông đường bộ 36/2024/QH15"
                        ),
                    },
                ])

            # 11.5. Intent: Trừ điểm & Phục hồi điểm Giấy phép lái xe (12 điểm)
            if any(kw in q_lower for kw in ["trừ điểm", "phục hồi điểm", "12 điểm", "điểm gplx", "điểm giấy phép lái xe", "hết điểm", "bị trừ hết điểm"]):
                sub_queries.extend([
                    {
                        "category": "license_points_rule",
                        "doc_keyword": "traffic_order",
                        "target_article": 58,
                        "sub_query": (
                            "điểm của giấy phép lái xe 12 điểm trừ điểm phục hồi đủ 12 điểm sau 12 tháng kiểm tra kiến thức "
                            "Điều 58 Luật Trật tự an toàn giao thông đường bộ 36/2024/QH15"
                        ),
                    },
                    {
                        "category": "license_points_procedure",
                        "doc_keyword": "traffic_penalty",
                        "target_article": [50, 51],
                        "sub_query": (
                            "trừ điểm phục hồi điểm giấy phép lái xe trình tự thủ tục kiểm tra kiến thức pháp luật trật tự an toàn giao thông "
                            "Điều 51 Điều 50 Nghị định 168/2024/NĐ-CP"
                        ),
                    },
                ])

            # 11.6. Intent: Tước quyền sử dụng GPLX & Vi phạm điều kiện người điều khiển
            if any(kw in q_lower for kw in ["tước gplx", "tước bằng", "không có gplx", "không có bằng", "không có giấy phép lái xe", "sai loại gplx", "không phù hợp", "quên bằng", "hết hạn gplx"]):
                sub_queries.extend([
                    {
                        "category": "license_suspension_conditions",
                        "doc_keyword": "traffic_penalty",
                        "target_article": 18,
                        "sub_query": (
                            "xử phạt người điều khiển phương tiện vi phạm điều kiện không có giấy phép lái xe sử dụng giấy phép lái xe không phù hợp "
                            "Điều 18 Nghị định 168/2024/NĐ-CP"
                        ),
                    },
                    {
                        "category": "license_classification",
                        "doc_keyword": "traffic_order",
                        "target_article": [56, 57],
                        "sub_query": (
                            "điều kiện của người lái xe và phân hạng giấy phép lái xe hạng A1 hạng A hạng B1 hạng B hạng C "
                            "Điều 56 Điều 57 Luật Trật tự an toàn giao thông đường bộ 36/2024/QH15"
                        ),
                    },
                ])

            # 11.7. Intent: Tai nạn giao thông đường bộ & Cứu nạn
            if any(kw in q_lower for kw in ["tai nạn giao thông", "gây tai nạn", "cứu nạn", "giải quyết tai nạn"]):
                sub_queries.extend([
                    {
                        "category": "traffic_accident_responsibilities",
                        "doc_keyword": "traffic_order",
                        "target_article": 79,
                        "sub_query": (
                            "trách nhiệm của cơ quan tổ chức cá nhân khi xảy ra tai nạn giao thông đường bộ dừng xe giữ nguyên hiện trường "
                            "Điều 79 Luật Trật tự an toàn giao thông đường bộ 36/2024/QH15"
                        ),
                    },
                ])

            # 11.8. Intent: Đường cao tốc, lùi xe, đi ngược chiều trên cao tốc
            if any(kw in q_lower for kw in ["lùi xe", "ngược chiều", "quay đầu"]) and any(kw in q_lower for kw in ["cao tốc", "đường cao tốc"]):
                sub_queries.extend([
                    {
                        "category": "traffic_highway_penalty",
                        "doc_keyword": "traffic_penalty",
                        "target_article": 6,
                        "sub_query": (
                            "người điều khiển xe ô tô lùi xe trên đường cao tốc đi ngược chiều trên đường cao tốc mức phạt tiền và trừ điểm giấy phép lái xe "
                            "Điều 6 Nghị định 168/2024/NĐ-CP"
                        ),
                    },
                    {
                        "category": "traffic_highway_order_rule",
                        "doc_keyword": "traffic_order",
                        "target_article": [16, 25],
                        "sub_query": (
                            "quy tắc giao thông trên đường cao tốc không được lùi xe đi ngược chiều quay đầu xe trên đường cao tốc "
                            "Điều 16 Điều 25 Luật Trật tự an toàn giao thông đường bộ 36/2024/QH15"
                        ),
                    },
                ])
            elif any(kw in q_lower for kw in ["kết cấu hạ tầng", "thu phí", "trạm dừng nghỉ", "quản lý vận hành", "đường bộ"]):
                sub_queries.extend([
                    {
                        "category": "road_highway_management",
                        "doc_keyword": "road",
                        "target_article": 45,
                        "sub_query": (
                            "quy định về đường bộ cao tốc đầu tư xây dựng quản lý vận hành khai thác thu phí sử dụng đường cao tốc "
                            "Điều 45 Luật Đường bộ 35/2024/QH15"
                        ),
                    },
                ])

            # 11.9. Intent: Sát hạch lái xe ô tô, thi mô phỏng, giấy phép lái xe (Temporal-Aware TT12 vs TT108)
            if any(kw in q_lower for kw in ["sát hạch", "thi mô phỏng", "phần mềm mô phỏng", "bài thi mô phỏng", "thi lái xe", "thi bằng lái", "đổi giấy phép lái xe", "cấp lại giấy phép lái xe"]):
                if as_of_date and as_of_date < "2026-07-01":
                    sub_queries.extend([
                        {
                            "category": "traffic_driving_license_exam_pre_amendment",
                            "doc_keyword": "traffic_driving_license_12",
                            "target_article": 14,
                            "sub_query": (
                                "nội dung sát hạch lái xe ô tô bắt buộc thi mô phỏng trên máy tính 4 phần thi lý thuyết mô phỏng sa hình đường trường "
                                "Điều 14 Thông tư 12/2025/TT-BCA"
                            ),
                        },
                        {
                            "category": "traffic_driving_license_exam_exemption",
                            "doc_keyword": "traffic_driving_license_12",
                            "target_article": 12,
                            "sub_query": (
                                "miễn sát hạch lý thuyết lái xe mô tô A1 A cho người đã có bằng lái xe ô tô "
                                "Điều 12 Thông tư 12/2025/TT-BCA"
                            ),
                        },
                    ])
                else:
                    sub_queries.extend([
                        {
                            "category": "traffic_driving_license_exam_post_amendment",
                            "doc_keyword": "traffic_driving_license_108",
                            "target_article": 15,
                            "sub_query": (
                                "nội dung và quy trình sát hạch lái xe chính thức bãi bỏ thi mô phỏng tình huống giao thông đạt lý thuyết mới thi thực hành "
                                "Điều 15 Thông tư 108/2026/TT-BCA"
                            ),
                        },
                        {
                            "category": "traffic_driving_license_transition",
                            "doc_keyword": "traffic_driving_license_108",
                            "target_article": 35,
                            "sub_query": (
                                "điều khoản chuyển tiếp đào tạo sát hạch lái xe khai giảng trước ngày 01 tháng 07 năm 2026 tiếp tục áp dụng Thông tư 12/2025 đến 28/02/2027 "
                                "Điều 35 Thông tư 108/2026/TT-BCA"
                            ),
                        },
                        {
                            "category": "traffic_driving_license_renewal",
                            "doc_keyword": "traffic_driving_license_108",
                            "target_article": 22,
                            "sub_query": (
                                "cấp lại đổi giấy phép lái xe quá hạn sử dụng dưới 30 ngày từ 01 năm trở lên "
                                "Điều 22 Thông tư 108/2026/TT-BCA"
                            ),
                        },
                    ])

            # 11.10. Intent: Temporal Version-Aware: Mốc chuyển tiếp hiệu lực chung của Luật/Nghị định
            elif (
                any(kw in q_lower for kw in ["hiệu lực thi hành", "thời điểm có hiệu lực", "kể từ ngày có hiệu lực", "bãi bỏ nghị định", "điều khoản chuyển tiếp"])
                or ("hiệu lực" in q_lower and any(kw in q_lower for kw in ["luật", "nghị định"]))
            ):
                sub_queries.extend([
                    {
                        "category": "traffic_temporal_order_effective",
                        "doc_keyword": "traffic_order",
                        "target_article": 88,
                        "sub_query": (
                            "hiệu lực thi hành của Luật Trật tự an toàn giao thông đường bộ từ ngày 01 tháng 01 năm 2025 "
                            "Điều 88 Luật Trật tự an toàn giao thông đường bộ 36/2024/QH15"
                        ),
                    },
                    {
                        "category": "traffic_temporal_penalty_effective",
                        "doc_keyword": "traffic_penalty",
                        "target_article": [52, 53, 54],
                        "sub_query": (
                            "hiệu lực thi hành từ ngày 01 tháng 01 năm 2025 sửa đổi bãi bỏ Nghị định 100/2019/NĐ-CP sửa đổi năm 2026 điều khoản chuyển tiếp "
                            "Điều 52 Điều 53 Điều 54 Nghị định 168/2024/NĐ-CP"
                        ),
                    },
                ])

        return sub_queries


    def _dense_search(self, query: str, limit: int = 15, as_of_date: Optional[str] = None) -> List[Dict[str, Any]]:
        """Tìm kiếm theo vector ngữ nghĩa trên Qdrant có hỗ trợ Temporal Filtering"""
        query_vector = self.embedding_service.embed_query(query)
        results = self.vector_store.search_similar(query_vector=query_vector, limit=limit, as_of_date=as_of_date)
        return results

    def _sparse_search_postgresql_fts(self, query: str, limit: int = 30, as_of_date: Optional[str] = None, domain: str = "traffic") -> List[Dict[str, Any]]:
        """
        Tìm kiếm toàn văn trên Supabase PostgreSQL (PostgreSQL Full-Text Search - FTS).
        - Sử dụng PostgreSQL Full-Text Search (tsvector / wfts websearch_to_tsquery).
        - Bắt buộc lọc theo domain (mặc định 'traffic'), ngăn chặn 100% tài liệu ngoại ngành.
        - Hỗ trợ temporal filtering theo as_of_date.
        - Trích xuất từ khóa pháp lý thực chất, không hardcode số Điều và không xuyên tạc câu hỏi.
        - Tái xếp hạng theo mức độ bao phủ từ vựng, trùng khớp tiêu đề và mật độ từ khóa.
        """
        if not self.supabase_url or not self.supabase_key:
            return []

        headers = {
            "apikey": self.supabase_key,
            "Authorization": f"Bearer {self.supabase_key}",
        }
        endpoint = f"{self.supabase_url}/rest/v1/legal_articles"

        # 1. Khởi tạo / lấy danh sách văn bản giao thông hợp lệ từ Supabase
        # Đảm bảo 100% không bao giờ lấy văn bản ngoài ngành Giao thông
        traffic_docs = getattr(self, "_cached_traffic_docs", None)
        if traffic_docs is None:
            try:
                r_doc = requests.get(
                    f"{self.supabase_url}/rest/v1/legal_documents?select=id,official_number,title,effective_date,expiry_date",
                    headers=headers,
                    timeout=5,
                )
                if r_doc.status_code == 200:
                    traffic_docs = {
                        d["id"]: d for d in r_doc.json()
                        if d["id"] != "bhyt_51_2024_qh15" and ("traffic" in d["id"] or "road" in d["id"])
                    }
                    self._cached_traffic_docs = traffic_docs
            except Exception as e:
                print(f"[!] Lỗi tải danh mục legal_documents: {e}")
                traffic_docs = {}

        if not traffic_docs:
            return []

        # 2. Lọc theo thời gian hiệu lực (temporal filtering)
        valid_traffic_ids = []
        for did, dinfo in traffic_docs.items():
            eff = dinfo.get("effective_date")
            exp = dinfo.get("expiry_date")
            if as_of_date:
                if eff and eff > as_of_date:
                    continue
                if exp and exp < as_of_date:
                    continue
            valid_traffic_ids.append(did)

        if not valid_traffic_ids:
            valid_traffic_ids = list(traffic_docs.keys())

        # 3. Chuẩn hóa câu hỏi và trích xuất từ khóa thực chất
        q_clean = re.sub(r"[^\w\s]", " ", query.lower())
        raw_tokens = q_clean.split()

        doc_meta_words = {
            "luật", "nghị", "định", "thông", "tư", "điều", "khoản", "điểm", "chương", "mục",
            "quy", "định", "pháp", "văn", "bản", "số", "năm", "nào", "mấy", "bao", "nhiêu",
            "2024", "2025", "2026", "qh14", "qh15", "bca", "bgtvt", "bxd", "cp", "tt", "nd",
            "trật", "tự", "an", "toàn", "giao", "thông", "đường", "bộ", "việt", "nam"
        }

        question_fillers = {
            "là", "gì", "ở", "đâu", "khi", "có", "được", "không", "thế", "như", "theo", "của",
            "trong", "vào", "ngày", "tại", "cho", "về", "thì", "phải", "những", "hỏi", "biết",
            "cho", "em", "mình", "ai", "trước", "tiên", "các", "đối", "với", "ra", "sao"
        }

        all_stop = doc_meta_words | question_fillers

        tokens = [w for w in raw_tokens if w not in all_stop and len(w) > 1]
        if len(tokens) < 2:
            tokens = [w for w in raw_tokens if w not in question_fillers and len(w) > 1]
        if not tokens:
            tokens = ["giao", "thông"]

        # 4. Nhận diện văn bản đích nếu câu hỏi có nhắc đích danh văn bản
        target_doc_id = None
        q_normalized_text = " ".join(raw_tokens)
        doc_hints = [
            ("trật tự an toàn giao thông", "traffic_order_36_2024_qh15", "36/2024/QH15"),
            ("luật 36", "traffic_order_36_2024_qh15", "36/2024/QH15"),
            ("luật đường bộ", "road_35_2024_qh15", "35/2024/QH15"),
            ("luật 35", "road_35_2024_qh15", "35/2024/QH15"),
            ("168 2024", "traffic_penalty_168_2024_nd_cp", "168/2024/NĐ-CP"),
            ("nghị định 168", "traffic_penalty_168_2024_nd_cp", "168/2024/NĐ-CP"),
            ("158 2024", "traffic_transport_158_2024_nd_cp", "158/2024/NĐ-CP"),
            ("nghị định 158", "traffic_transport_158_2024_nd_cp", "158/2024/NĐ-CP"),
            ("151 2024", "traffic_guideline_151_2024_nd_cp", "151/2024/NĐ-CP"),
            ("nghị định 151", "traffic_guideline_151_2024_nd_cp", "151/2024/NĐ-CP"),
            ("38 2024", "traffic_speed_distance_38_2024_tt_bgtvt", "38/2024/TT-BGTVT"),
            ("thông tư 38", "traffic_speed_distance_38_2024_tt_bgtvt", "38/2024/TT-BGTVT"),
            ("73 2024", "traffic_police_patrol_73_2024_tt_bca", "73/2024/TT-BCA"),
            ("thông tư 73", "traffic_police_patrol_73_2024_tt_bca", "73/2024/TT-BCA"),
            ("79 2024", "traffic_vehicle_registration_79_2024_tt_bca", "79/2024/TT-BCA"),
            ("thông tư 79", "traffic_vehicle_registration_79_2024_tt_bca", "79/2024/TT-BCA"),
            ("12 2025", "traffic_driving_license_12_2025_tt_bca", "12/2025/TT-BCA"),
            ("108 2026", "traffic_driving_license_108_2026_tt_bca", "108/2026/TT-BCA"),
            ("89 2026", "traffic_inspection_framework_89_2026_nd_cp", "89/2026/NĐ-CP"),
            ("30 2026", "traffic_inspection_procedures_30_2026_tt_bxd", "30/2026/TT-BXD"),
            ("65 2024", "traffic_points_recovery_65_2024_tt_bca", "65/2024/TT-BCA"),
            ("105 2026", "traffic_points_recovery_105_2026_tt_bca", "105/2026/TT-BCA"),
            ("51 2024", "traffic_road_signs_qcvn41_51_2024_tt_bgtvt", "51/2024/TT-BGTVT"),
        ]
        for pattern, did, off in doc_hints:
            if pattern in q_normalized_text:
                target_doc_id = did
                break

        if target_doc_id and target_doc_id in valid_traffic_ids:
            doc_filter = f"eq.{target_doc_id}"
        else:
            doc_filter = f"in.({','.join(valid_traffic_ids)})"

        # 5. Truy vấn Supabase PostgreSQL FTS bằng wfts
        search_terms = " ".join(tokens[:3])
        params = {
            "document_id": doc_filter,
            "full_text": f"wfts.{search_terms}",
            "select": "document_id,article_number,article_title,full_text,chapter_info",
            "limit": "30",
        }

        hits = []
        try:
            r = requests.get(endpoint, headers=headers, params=params, timeout=5)
            if r.status_code == 200:
                hits = r.json()
        except Exception as e:
            print(f"[!] Lỗi truy vấn PostgreSQL FTS: {e}")

        # Fallback nếu không có kết quả với 3 từ
        if not hits and len(tokens) > 2:
            params["full_text"] = f"wfts.{' '.join(tokens[:2])}"
            try:
                r = requests.get(endpoint, headers=headers, params=params, timeout=5)
                if r.status_code == 200:
                    hits = r.json()
            except Exception:
                pass

        # 6. Xếp hạng và chấm điểm ứng viên FTS
        scored = []
        q_lower = query.lower()
        art_match = re.search(r"điều\s*(\d+)", q_lower)
        target_art_num = art_match.group(1) if art_match else None

        for h in hits:
            did = h.get("document_id", "")
            title_lower = (h.get("article_title") or "").lower()
            text_lower = (h.get("full_text") or "").lower()
            art_num_str = str(h.get("article_number") or "")

            score = 0.0
            if target_doc_id and target_doc_id == did:
                score += 6.0

            for i in range(len(tokens) - 1):
                bg = f"{tokens[i]} {tokens[i+1]}"
                if bg in title_lower:
                    score += 4.0

            for t in tokens:
                if t in title_lower:
                    score += 2.0

            for t in tokens:
                if t in text_lower:
                    c = text_lower.count(t)
                    score += min(c * 0.25, 3.0)

            if target_art_num and target_art_num == art_num_str:
                score += 10.0

            scored.append((score, h))

        scored.sort(key=lambda x: x[0], reverse=True)

        # 7. Trả về định dạng đầy đủ cho Sparse Retrieval
        results = []
        seen_keys = set()
        for sc, h in scored:
            did = h.get("document_id", "")
            art_num = h.get("article_number")
            key = f"{did}_{art_num}"
            if key in seen_keys:
                continue
            seen_keys.add(key)

            dinfo = traffic_docs.get(did, {})
            doc_title = self._get_doc_title(did)
            official_number = dinfo.get("official_number", "N/A")

            results.append({
                "doc_id": did,
                "document_id": did,
                "official_number": official_number,
                "doc_title": doc_title,
                "article": art_num,
                "article_number": art_num,
                "article_title": h.get("article_title"),
                "chapter": h.get("chapter_info"),
                "content": h.get("full_text"),
                "chunk_id": f"{did}_art_{art_num}",
                "score": round(sc, 2),
                "metadata": {
                    "search_type": "postgresql_full_text_search",
                    "domain": "traffic",
                    "effective_date": dinfo.get("effective_date"),
                    "expiry_date": dinfo.get("expiry_date"),
                },
                "context_header": f"{doc_title}. {h.get('chapter_info', '')}. Điều {art_num}: {h.get('article_title')}",
            })
            if len(results) >= limit:
                break

        return results

    def _sparse_search_bm25(self, query: str, limit: int = 30, as_of_date: Optional[str] = None) -> List[Dict[str, Any]]:
        """Deprecated alias: Chuyển tiếp sang PostgreSQL Full-Text Search chuẩn"""
        return self._sparse_search_postgresql_fts(query, limit=limit, as_of_date=as_of_date)

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
        elif "land" in doc_id or "31_2024" in doc_id:
            return "Luật Đất đai 2024"
        elif "housing" in doc_id or "27_2023" in doc_id:
            return "Luật Nhà ở 2023"
        elif "re_business" in doc_id or "29_2023" in doc_id:
            return "Luật Kinh doanh Bất động sản 2023"
        elif "investment" in doc_id or "61_2020" in doc_id:
            return "Luật Đầu tư 2020"
        elif "traffic_order" in doc_id or "36_2024" in doc_id:
            return "Luật Trật tự, an toàn giao thông đường bộ 2024"
        elif "traffic_penalty" in doc_id or "168_2024" in doc_id:
            return "Nghị định 168/2024/NĐ-CP"
        elif "traffic_guideline" in doc_id or "151_2024" in doc_id:
            return "Nghị định 151/2024/NĐ-CP"
        elif "traffic_transport" in doc_id or "158_2024" in doc_id:
            return "Nghị định 158/2024/NĐ-CP"
        elif "traffic_dangerous_goods" in doc_id or "161_2024" in doc_id:
            return "Nghị định 161/2024/NĐ-CP"
        elif "traffic_driver_training" in doc_id or "94_2026" in doc_id:
            return "Nghị định 94/2026/NĐ-CP"
        elif "traffic_inspection_framework" in doc_id or "89_2026" in doc_id:
            return "Nghị định 89/2026/NĐ-CP"
        elif "traffic_police_patrol" in doc_id or "73_2024" in doc_id:
            return "Thông tư 73/2024/TT-BCA"
        elif "traffic_points_recovery" in doc_id or "65_2024" in doc_id:
            return "Thông tư 65/2024/TT-BCA"
        elif "traffic_road_signs" in doc_id or "51_2024" in doc_id:
            return "Thông tư 51/2024/TT-BGTVT"
        elif "traffic_speed_distance" in doc_id or "38_2024" in doc_id:
            return "Thông tư 38/2024/TT-BGTVT"
        elif "traffic_vehicle_registration" in doc_id or "79_2024" in doc_id:
            return "Thông tư 79/2024/TT-BCA"
        elif "road" in doc_id or "35_2024" in doc_id:
            return "Luật Đường bộ 2024"
        elif "bllđ" in doc_id or "bld" in doc_id:
            return "Bộ luật Lao động 2019"
        return "Văn bản Quy phạm Pháp luật"

    def _get_full_article_from_supabase(self, doc_id: str, article_number: int) -> Optional[Dict[str, Any]]:
        """Lấy toàn văn Điều luật từ Supabase legal_articles để hydrate target article"""
        cache_key = (doc_id, int(article_number))
        if cache_key in self._full_article_cache:
            return self._full_article_cache[cache_key]

        if not self.supabase_url or not self.supabase_key:
            return None

        headers = {
            "apikey": self.supabase_key,
            "Authorization": f"Bearer {self.supabase_key}",
        }
        endpoint = f"{self.supabase_url}/rest/v1/legal_articles"
        params = {
            "document_id": f"eq.{doc_id}",
            "article_number": f"eq.{article_number}",
            "select": "document_id,article_number,article_title,full_text,chapter_info,status",
            "limit": "1",
        }
        try:
            res = requests.get(endpoint, headers=headers, params=params, timeout=5)
            if res.status_code == 200:
                rows = res.json()
                if rows and rows[0].get("full_text"):
                    self._full_article_cache[cache_key] = rows[0]
                    return rows[0]
        except Exception as e:
            print(f"[!] Lỗi hydrate article {doc_id} Điều {article_number}: {e}")
    @staticmethod
    def _clean_art_num(val: Any) -> str:
        if val is None:
            return ""
        digits = re.findall(r'\d+', str(val))
        return digits[0] if digits else str(val).strip()

    def _hydrate_target_articles(
        self,
        items: List[Dict[str, Any]],
        sub_query_configs: List[Dict[str, Any]],
        query: str = "",
        use_clause_extraction: bool = True,
    ) -> List[Dict[str, Any]]:
        """
        Target Article Hydration (Article-Aware Retrieval) & Deterministic Target Clause Extraction:
        Đối với các evidence items thuộc Target Articles đã được xác định qua query decomposition:
        1. Nạp full_text của Điều luật từ Supabase legal_articles.
        2. Nếu use_clause_extraction=True: Sử dụng DeterministicClauseExtractor để bóc tách chính xác
           các Khoản/Điểm trúng đích và chế tài liên đới, rút gọn context từ 15k-35k chars xuống 2k-5k chars
           nhằm giảm sâu TTFT và Input Tokens, đồng thời tự động fallback về full_text nếu không đảm bảo evidence.
        """
        if not items or not sub_query_configs:
            return items

        targets = []
        for cfg in sub_query_configs:
            tgt = cfg.get("target_article")
            if not tgt:
                continue
            doc_kw = cfg.get("doc_keyword", "").lower()
            if isinstance(tgt, list):
                for t in tgt:
                    targets.append((doc_kw, self._clean_art_num(t)))
            else:
                targets.append((doc_kw, self._clean_art_num(tgt)))

        hydrated_count = 0
        for item in items:
            doc_id = item.get("doc_id", "")
            art_num = item.get("article_number")
            if not art_num or not doc_id:
                continue

            art_num_clean = self._clean_art_num(art_num)
            is_target = any(
                doc_kw in doc_id.lower() and art_num_clean == t_art
                for doc_kw, t_art in targets
            )

            if is_target:
                try:
                    num_int = int(art_num_clean)
                except (ValueError, TypeError):
                    continue
                full_art = self._get_full_article_from_supabase(doc_id, num_int)
                if full_art and full_art.get("full_text"):
                    full_text = full_art["full_text"]
                    curr_content = item.get("content", "")
                    if len(full_text) > len(curr_content):
                        old_len = len(curr_content)
                        item["is_hydrated"] = True
                        if full_art.get("article_title"):
                            item["article_title"] = full_art["article_title"]
                        if full_art.get("chapter_info"):
                            item["chapter"] = full_art["chapter_info"]
                        doc_title = item.get("doc_title") or self._get_doc_title(doc_id)
                        item["doc_title"] = doc_title
                        item["context_header"] = (
                            f"{doc_title}. {item.get('chapter', '')}. "
                            f"Điều {art_num}: {item.get('article_title', '')}"
                        ).strip()

                        # Deterministic Target Clause Extraction
                        if use_clause_extraction and query:
                            from backend.app.services.rag.clause_parser import DeterministicClauseExtractor
                            art_title = full_art.get("article_title") or item.get("article_title", "")
                            compact_text, is_ext = DeterministicClauseExtractor.extract_relevant_context(
                                article_number=num_int,
                                article_title=art_title,
                                full_text=full_text,
                                query=query,
                                doc_id=doc_id,
                            )
                            if is_ext and len(compact_text) > 0:
                                item["content"] = compact_text
                                item["is_clause_extracted"] = True
                                print(f"  [+] Target Clause Extraction: {doc_id} Điều {art_num} -> rút gọn {len(full_text):,} ký tự xuống {len(compact_text):,} ký tự (giảm {(1 - len(compact_text)/len(full_text))*100:.1f}%).")
                            else:
                                item["content"] = full_text
                                item["is_clause_extracted"] = False
                                print(f"  [~] Target Clause Fallback: {doc_id} Điều {art_num} -> giữ nguyên {len(full_text):,} ký tự (Evidence-Preserving).")
                        else:
                            item["content"] = full_text
                            item["is_clause_extracted"] = False
                            print(f"  [+] Target Article Hydration (Full): {doc_id} Điều {art_num} -> nạp {len(full_text):,} ký tự (thay thế chunk {old_len:,} ký tự).")

                        hydrated_count += 1

        return items

    def _is_candidate_effective_at(self, item: Dict[str, Any], as_of_date: Optional[str]) -> bool:
        """
        Kiểm tra một điều khoản/văn bản có đang phát sinh hiệu lực tại mốc thời gian as_of_date hay không.
        """
        if not as_of_date:
            return True

        doc_id = str(item.get("doc_id", "") or "")
        off_num = str(item.get("official_number", "") or "")
        doc_title = str(item.get("doc_title", "") or "")

        eff_from = item.get("effective_date") or item.get("effective_from")
        eff_to = item.get("expiry_date") or item.get("effective_to")
        trans_until = None

        relations = item.get("relations")
        if isinstance(relations, dict):
            replaces = relations.get("replaces")
            if replaces and isinstance(replaces, list) and len(replaces) > 0:
                rep_info = replaces[0]
                if not eff_from and rep_info.get("replacement_date"):
                    eff_from = rep_info.get("replacement_date")
                trans = rep_info.get("transition_provision")
                if trans and trans.get("expiration_date"):
                    trans_until = trans.get("expiration_date")
            replaced_by = relations.get("replaced_by")
            if replaced_by and isinstance(replaced_by, list) and len(replaced_by) > 0:
                rep_by = replaced_by[0]
                if not eff_to and rep_by.get("effective_date"):
                    eff_to = rep_by.get("effective_date")

        # Fallback từ LEGAL_DOCUMENT_TEMPORAL_REGISTRY
        for k, reg in LEGAL_DOCUMENT_TEMPORAL_REGISTRY.items():
            if k in doc_id or k in off_num or k in doc_title:
                if not eff_from:
                    eff_from = reg.get("effective_from")
                if not eff_to:
                    eff_to = reg.get("effective_to")
                if not trans_until:
                    trans_until = reg.get("transition_until")
                break

        # 1. Nếu văn bản chưa phát sinh hiệu lực (effective_from > as_of_date)
        if eff_from and str(eff_from)[:10] > as_of_date:
            return False

        # 2. Nếu văn bản đã bị thay thế / hết hiệu lực trước as_of_date (effective_to < as_of_date)
        if eff_to and str(eff_to)[:10] < as_of_date:
            if trans_until and as_of_date <= str(trans_until)[:10]:
                return True
            return False

        return True

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        use_reranker: bool = False,
        as_of_date: Optional[str] = None,
        use_clause_extraction: bool = True,
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

        # 1. Query Decomposition (Tách ý định pháp lý nếu được bật bởi Feature Flag)
        if self.enable_query_decomposition:
            sub_query_configs = self._decompose_query(query, as_of_date=as_of_date)
        else:
            sub_query_configs = []
        is_multi_intent = len(sub_query_configs) >= 2

        doc_store: Dict[str, Dict[str, Any]] = {}
        rrf_scores: Dict[str, float] = {}

        # 1. Thu thập ứng viên từ Dense Retrieval (Query gốc + các Sub-queries nếu bật decomposition)
        search_queries = [query]
        if self.enable_query_decomposition:
            for item in sub_query_configs:
                search_queries.append(item["sub_query"])

        for q_idx, q_text in enumerate(search_queries):
            hits = self._dense_search(q_text, limit=15, as_of_date=as_of_date)
            seen_dense_articles = set()
            dense_rank = 1
            for hit in hits:
                art_num = hit.get("article_number")
                if not art_num:
                    continue
                doc_id = hit.get("doc_id", "bllđ_45_2019_qh14")
                key = f"{doc_id}_{art_num}"
                weight = self.dense_weight if q_idx == 0 else 1.3
                if key not in seen_dense_articles:
                    seen_dense_articles.add(key)
                    rrf_scores[key] = rrf_scores.get(key, 0.0) + (weight / (self.rrf_k + dense_rank))
                    dense_rank += 1

                # Ưu tiên chunk có nội dung dài/đầy đủ hơn
                if key not in doc_store or len(hit.get("content", "")) > len(doc_store[key].get("content", "")):
                    doc_store[key] = hit

        # 2. Thu thập ứng viên từ Sparse Search (PostgreSQL Full-Text Search)
        sparse_hits = self._sparse_search_postgresql_fts(query, limit=35, as_of_date=as_of_date)
        seen_sparse_articles = set()
        sparse_rank = 1
        for hit in sparse_hits:
            art_num = hit.get("article_number")
            if not art_num:
                continue
            doc_id = hit.get("doc_id", "bllđ_45_2019_qh14")
            key = f"{doc_id}_{art_num}"
            if key not in seen_sparse_articles:
                seen_sparse_articles.add(key)
                rrf_scores[key] = rrf_scores.get(key, 0.0) + (self.sparse_weight / (self.rrf_k + sparse_rank))
                sparse_rank += 1

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

        # Bảo toàn Target Evidence từ sub_query_configs vào candidate pool (nếu có sub_query_configs)
        target_keys = set()
        if self.enable_query_decomposition and sub_query_configs:
            for cfg in sub_query_configs:
                tgt = cfg.get("target_article")
                if tgt:
                    tgt_strs = {self._clean_art_num(t) for t in (tgt if isinstance(tgt, list) else [tgt])}
                    doc_kw = cfg.get("doc_keyword", "").lower()
                    for k, v in doc_store.items():
                        if doc_kw in v.get("doc_id", "").lower() and self._clean_art_num(v.get("article_number")) in tgt_strs:
                            target_keys.add(k)

        candidate_pool_size = max(20, len(sub_query_configs) * 7) if is_multi_intent else (top_k * 2)
        candidate_pool = []
        selected_pool_keys = set()

        # 1. Đảm bảo các target articles luôn có mặt trong candidate pool
        for key in target_keys:
            if key in doc_store:
                item = doc_store[key].copy()
                item["rrf_score"] = rrf_scores.get(key, 0.0)
                candidate_pool.append(item)
                selected_pool_keys.add(key)

        # 2. Lấy thêm các ứng viên RRF cao nhất cho đến khi đủ candidate_pool_size
        for key, score in sorted_articles:
            if len(candidate_pool) >= candidate_pool_size:
                break
            if key not in selected_pool_keys and key in doc_store:
                selected_pool_keys.add(key)
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

        # Temporal Validity Resolution (Phân giải tính hiệu lực thời gian theo as_of_date)
        if as_of_date and final_ranked:
            effective_candidates = []
            non_effective_candidates = []
            for item in final_ranked:
                if self._is_candidate_effective_at(item, as_of_date):
                    effective_candidates.append(item)
                else:
                    item_copy = item.copy()
                    item_copy["temporal_status"] = "CHUA_CO_HIEU_LUC_TAI_AS_OF_DATE"
                    non_effective_candidates.append(item_copy)
            final_ranked = effective_candidates + non_effective_candidates

        # 5. Phân bổ cân bằng đa văn bản (Balanced Cross-Document Representation)
        effective_top_k = max(top_k, 5) if is_multi_intent else top_k

        if is_multi_intent and sub_query_configs:
            selected_items = []
            selected_keys = set()

            # Vòng 1: Chọn tất cả target articles hoặc chunk tốt nhất của từng chủ đề/văn bản
            for cfg in sub_query_configs:
                doc_kw = cfg["doc_keyword"]
                target_art = cfg.get("target_article")
                category_hits = [c for c in final_ranked if doc_kw in c.get("doc_id", "").lower()]

                if target_art:
                    targets = target_art if isinstance(target_art, list) else [target_art]
                    target_str_set = {self._clean_art_num(t) for t in targets}
                    for h in category_hits:
                        if self._clean_art_num(h.get("article_number")) in target_str_set:
                            key = f"{h.get('doc_id')}_{h.get('article_number')}"
                            if key not in selected_keys:
                                selected_keys.add(key)
                                selected_items.append(h)

                # Nếu chưa chọn được item nào cho category này thì fallback chọn hit đầu tiên
                has_cat_chosen = any(doc_kw in it.get("doc_id", "").lower() for it in selected_items)
                if not has_cat_chosen:
                    for hit in category_hits:
                        key = f"{hit.get('doc_id')}_{hit.get('article_number')}"
                        if key not in selected_keys:
                            selected_keys.add(key)
                            selected_items.append(hit)
                            break

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

            final_candidates = selected_items
        else:
            final_candidates = final_ranked[:effective_top_k]

        # Target Article Hydration & Chuẩn hóa Title Mapping chính thức
        hydrated_results = self._hydrate_target_articles(
            final_candidates, sub_query_configs, query=query, use_clause_extraction=use_clause_extraction
        )
        for item in hydrated_results:
            doc_id = item.get("doc_id", "")
            doc_title = self._get_doc_title(doc_id)
            item["doc_title"] = doc_title
            art_num = item.get("article_number", "")
            art_title = item.get("article_title", "")
            chap = item.get("chapter", "")
            chap_str = f". {chap}" if chap else ""
            item["context_header"] = f"{doc_title}{chap_str}. Điều {art_num}: {art_title}".strip()

        return hydrated_results

    def close(self):
        """Đóng kết nối Vector Store khi kết thúc"""
        if hasattr(self.vector_store, "close"):
            self.vector_store.close()
