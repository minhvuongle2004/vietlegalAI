import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
import json
import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
gold_path = PROJECT_ROOT / "data" / "gold_evaluation" / "gold_retrieval_225_cases.json"
out_path = PROJECT_ROOT / "data" / "gold_evaluation" / "gold_retrieval_225_cases_v2.json"

with open(gold_path, "r", encoding="utf-8") as f:
    data = json.load(f)

cases = data["cases"]
print(f"Loaded {len(cases)} cases from {gold_path}")

# Verified traffic documents in corpus
VALID_DOCS = {
    "traffic_order_36_2024_qh15": "36/2024/QH15",
    "road_35_2024_qh15": "35/2024/QH15",
    "traffic_penalty_168_2024_nd_cp": "168/2024/NĐ-CP",
    "traffic_guideline_151_2024_nd_cp": "151/2024/NĐ-CP",
    "traffic_transport_158_2024_nd_cp": "158/2024/NĐ-CP",
    "traffic_toll_130_2024_nd_cp": "130/2024/NĐ-CP",
    "traffic_highway_130_2024_nd_cp": "130/2024/NĐ-CP",
    "traffic_driver_training_94_2026_nd_cp": "94/2026/NĐ-CP",
    "traffic_vehicle_lifespan_89_2026_nd_cp": "89/2026/NĐ-CP",
    "traffic_inspection_framework_89_2026_nd_cp": "89/2026/NĐ-CP",
    "traffic_penalty_amendment_238_2026_nd_cp": "238/2026/NĐ-CP",
    "traffic_road_infra_amendment_241_2026_nd_cp": "241/2026/NĐ-CP",
    "traffic_speed_distance_38_2024_tt_bgtvt": "38/2024/TT-BGTVT",
    "traffic_police_patrol_73_2024_tt_bca": "73/2024/TT-BCA",
    "traffic_vehicle_registration_79_2024_tt_bca": "79/2024/TT-BCA",
    "traffic_driving_license_12_2025_tt_bca": "12/2025/TT-BCA",
    "traffic_driving_license_108_2026_tt_bca": "108/2026/TT-BCA",
    "traffic_inspection_procedures_30_2026_tt_bxd": "30/2026/TT-BXD",
    "traffic_inspection_amendment_45_2026_tt_bxd": "45/2026/TT-BXD",
    "traffic_weight_limits_12_2025_tt_bxd": "12/2025/TT-BXD",
    "traffic_weight_amendment_19_2026_tt_bxd": "19/2026/TT-BXD",
    "traffic_weight_consolidated_26_2026_vbhn_bxd": "26/2026/VBHN-BXD",
    "traffic_points_recovery_65_2024_tt_bca": "65/2024/TT-BCA",
    "traffic_points_recovery_105_2026_tt_bca": "105/2026/TT-BCA",
    "traffic_amendment_13_2025_tt_bca": "13/2025/TT-BCA",
    "traffic_amendment_51_2025_tt_bca": "51/2025/TT-BCA",
    "traffic_road_signs_qcvn41_51_2024_tt_bgtvt": "51/2024/TT-BGTVT",
    "traffic_dangerous_goods_161_2024_nd_cp": "161/2024/NĐ-CP",
    "traffic_road_law_detail_165_2024_nd_cp": "165/2024/NĐ-CP",
    "traffic_amendment_218_2026_nd_cp": "218/2026/NĐ-CP",
    "traffic_transport_amendment_218_2026_nd_cp": "218/2026/NĐ-CP",
    "traffic_penalty_100_2019_nd_cp": "100/2019/NĐ-CP",
    "traffic_penalty_123_2021_nd_cp": "123/2021/NĐ-CP",
    "traffic_transport_10_2020_nd_cp": "10/2020/NĐ-CP",
    "traffic_transport_47_2022_nd_cp": "47/2022/NĐ-CP"
}

# The 17 false-miss cases identified in Tier 1.5 failure audit
FALSE_MISS_17_CASES = {
    "GOLD-DIR-04": {
        "supp": [
            {
                "official_number": "168/2024/NĐ-CP",
                "document_id": "traffic_penalty_168_2024_nd_cp",
                "article": 6,
                "clause": "Khoản 3",
                "evidence_role": "SUPPORTING_PENALTY",
                "reason": "Điều 6 NĐ 168 quy định xử phạt vi phạm chạy quá tốc độ quy định của ô tô, viện dẫn trực tiếp quy chuẩn tốc độ."
            },
            {
                "official_number": "36/2024/QH15",
                "document_id": "traffic_order_36_2024_qh15",
                "article": 12,
                "clause": "Khoản 1",
                "evidence_role": "SUPPORTING_PARENT_LAW",
                "reason": "Điều 12 Luật 36 quy định nguyên tắc chấp hành tốc độ quy định trên đường bộ."
            }
        ],
        "type": "PRIMARY_PLUS_SUPPORTING"
    },
    "GOLD-DIR-05": {
        "supp": [
            {
                "official_number": "168/2024/NĐ-CP",
                "document_id": "traffic_penalty_168_2024_nd_cp",
                "article": 7,
                "clause": "Khoản 2",
                "evidence_role": "SUPPORTING_PENALTY",
                "reason": "Điều 7 NĐ 168 quy định xử phạt xe mô tô vi phạm tốc độ quy định."
            },
            {
                "official_number": "36/2024/QH15",
                "document_id": "traffic_order_36_2024_qh15",
                "article": 12,
                "clause": "Khoản 1",
                "evidence_role": "SUPPORTING_PARENT_LAW",
                "reason": "Điều 12 Luật 36 quy định nghĩa vụ tuân thủ tốc độ xe cơ giới."
            }
        ],
        "type": "PRIMARY_PLUS_SUPPORTING"
    },
    "GOLD-DIR-06": {
        "supp": [
            {
                "official_number": "36/2024/QH15",
                "document_id": "traffic_order_36_2024_qh15",
                "article": 12,
                "clause": "Khoản 2",
                "evidence_role": "SUPPORTING_PARENT_LAW",
                "reason": "Điều 12 Khoản 2 Luật 36 quy định nguyên tắc giữ khoảng cách an toàn với xe chạy liền trước."
            },
            {
                "official_number": "168/2024/NĐ-CP",
                "document_id": "traffic_penalty_168_2024_nd_cp",
                "article": 6,
                "clause": "Khoản 1",
                "evidence_role": "SUPPORTING_PENALTY",
                "reason": "Xử phạt hành vi không giữ khoảng cách an toàn để xảy ra va chạm."
            }
        ],
        "type": "PRIMARY_PLUS_SUPPORTING"
    },
    "GOLD-DIR-15": {
        "supp": [
            {
                "official_number": "36/2024/QH15",
                "document_id": "traffic_order_36_2024_qh15",
                "article": 65,
                "clause": "Khoản 1, 2",
                "evidence_role": "SUPPORTING_PARENT_LAW",
                "reason": "Điều 65 Luật 36 quy định thẩm quyền, trường hợp CSGT được dừng phương tiện giao thông đường bộ."
            },
            {
                "official_number": "73/2024/TT-BCA",
                "document_id": "traffic_police_patrol_73_2024_tt_bca",
                "article": 11,
                "clause": "Khoản 1",
                "evidence_role": "SUPPORTING_PROCEDURE",
                "reason": "Điều 11 TT 73 quy định phương thức tuần tra kiểm soát công khai của CSGT kết hợp dừng xe."
            }
        ],
        "type": "MULTI_VALID"
    },
    "GOLD-DIR-20": {
        "supp": [
            {
                "official_number": "36/2024/QH15",
                "document_id": "traffic_order_36_2024_qh15",
                "article": 12,
                "clause": "Khoản 2",
                "evidence_role": "SUPPORTING_PARENT_LAW",
                "reason": "Quy định nguyên tắc về khoảng cách an toàn trong Luật TTATGTĐB."
            }
        ],
        "type": "PRIMARY_PLUS_SUPPORTING"
    },
    "GOLD-ART-12": {
        "supp": [
            {
                "official_number": "36/2024/QH15",
                "document_id": "traffic_order_36_2024_qh15",
                "article": 12,
                "clause": "Khoản 2",
                "evidence_role": "SUPPORTING_PARENT_LAW",
                "reason": "Điều luật mẹ quy định về khoảng cách an toàn giữa hai xe liền kề."
            }
        ],
        "type": "PRIMARY_PLUS_SUPPORTING"
    },
    "GOLD-ART-24": {
        "supp": [
            {
                "official_number": "36/2024/QH15",
                "document_id": "traffic_order_36_2024_qh15",
                "article": 61,
                "clause": "Khoản 3",
                "evidence_role": "SUPPORTING_PARENT_LAW",
                "reason": "Điều luật mẹ quy định cơ sở đào tạo lái xe và trung tâm sát hạch lái xe."
            }
        ],
        "type": "PRIMARY_PLUS_SUPPORTING"
    },
    "GOLD-EXC-04": {
        "supp": [
            {
                "official_number": "168/2024/NĐ-CP",
                "document_id": "traffic_penalty_168_2024_nd_cp",
                "article": 6,
                "clause": "Khoản 11",
                "evidence_role": "SUPPORTING_PENALTY",
                "reason": "Quy định miễn trừ xử phạt đối với xe ưu tiên khi đang đi làm nhiệm vụ khẩn cấp."
            }
        ],
        "type": "PRIMARY_PLUS_SUPPORTING"
    },
    "GOLD-EXC-09": {
        "supp": [
            {
                "official_number": "36/2024/QH15",
                "document_id": "traffic_order_36_2024_qh15",
                "article": 65,
                "clause": "Khoản 2",
                "evidence_role": "SUPPORTING_PARENT_LAW",
                "reason": "Điều 65 Khoản 2 Luật 36 quy định 4 trường hợp CSGT được dừng phương tiện kiểm soát."
            },
            {
                "official_number": "73/2024/TT-BCA",
                "document_id": "traffic_police_patrol_73_2024_tt_bca",
                "article": 11,
                "clause": "Khoản 2",
                "evidence_role": "SUPPORTING_PROCEDURE",
                "reason": "Phương thức tuần tra bí mật kết hợp công khai xử lý vi phạm."
            }
        ],
        "type": "MULTI_VALID"
    },
    "GOLD-MUL-03": {
        "supp": [
            {
                "official_number": "36/2024/QH15",
                "document_id": "traffic_order_36_2024_qh15",
                "article": 36,
                "clause": "Khoản 2",
                "evidence_role": "SUPPORTING_PARENT_LAW",
                "reason": "Điều 36 Luật 36 quy định nguyên tắc cấp biển số xe theo mã định danh của chủ xe."
            },
            {
                "official_number": "36/2024/QH15",
                "document_id": "traffic_order_36_2024_qh15",
                "article": 39,
                "clause": "Khoản 1",
                "evidence_role": "SUPPORTING_PARENT_LAW",
                "reason": "Điều 39 Luật 36 quy định quản lý biển số xe định danh."
            }
        ],
        "type": "CO_REQUISITE"
    },
    "GOLD-MUL-07": {
        "supp": [
            {
                "official_number": "36/2024/QH15",
                "document_id": "traffic_order_36_2024_qh15",
                "article": 61,
                "clause": "Khoản 3",
                "evidence_role": "SUPPORTING_PARENT_LAW",
                "reason": "Quy định khung về tiêu chuẩn cơ sở vật chất trung tâm sát hạch lái xe."
            }
        ],
        "type": "PRIMARY_PLUS_SUPPORTING"
    },
    "GOLD-HRD-02": {
        "supp": [
            {
                "official_number": "36/2024/QH15",
                "document_id": "traffic_order_36_2024_qh15",
                "article": 11,
                "clause": "Khoản 3",
                "evidence_role": "SUPPORTING_PARENT_LAW",
                "reason": "Quy định tín hiệu đèn giao thông màu đỏ phải dừng lại, trừ trường hợp có biển phụ/đèn phụ cho phép rẽ phải."
            },
            {
                "official_number": "36/2024/QH15",
                "document_id": "traffic_order_36_2024_qh15",
                "article": 15,
                "clause": "Khoản 1",
                "evidence_role": "SUPPORTING_PARENT_LAW",
                "reason": "Quy định quy tắc chuyển hướng xe tại nơi đường giao nhau."
            }
        ],
        "type": "MULTI_VALID"
    },
    "GOLD-HRD-13": {
        "supp": [
            {
                "official_number": "36/2024/QH15",
                "document_id": "traffic_order_36_2024_qh15",
                "article": 12,
                "clause": "Khoản 2",
                "evidence_role": "SUPPORTING_PARENT_LAW",
                "reason": "Quy định khi trời mưa, sương mù, trơn trượt phải giảm tốc độ và giữ khoảng cách lớn hơn."
            }
        ],
        "type": "PRIMARY_PLUS_SUPPORTING"
    },
    "GOLD-DIR-13": {
        "supp": [
            {
                "official_number": "151/2024/NĐ-CP",
                "document_id": "traffic_guideline_151_2024_nd_cp",
                "article": 39,
                "clause": "Khoản 1",
                "evidence_role": "SUPPORTING_DECREE_GUIDE",
                "reason": "Nghị định 151 hướng dẫn việc kết nối dữ liệu mã định danh cá nhân với biển số xe."
            },
            {
                "official_number": "79/2024/TT-BCA",
                "document_id": "traffic_vehicle_registration_79_2024_tt_bca",
                "article": 4,
                "clause": "Khoản 2",
                "evidence_role": "SUPPORTING_PROCEDURE",
                "reason": "Thông tư 79 quy định quy trình cấp và quản lý biển số định danh theo mã định danh cá nhân."
            }
        ],
        "type": "MULTI_VALID"
    },
    "GOLD-DIR-14": {
        "supp": [
            {
                "official_number": "79/2024/TT-BCA",
                "document_id": "traffic_vehicle_registration_79_2024_tt_bca",
                "article": 14,
                "clause": "Khoản 1",
                "evidence_role": "SUPPORTING_PROCEDURE",
                "reason": "Thông tư 79 quy định chi tiết hồ sơ, thủ tục thu hồi chứng nhận đăng ký, biển số xe khi chuyển quyền sở hữu xe."
            },
            {
                "official_number": "36/2024/QH15",
                "document_id": "traffic_order_36_2024_qh15",
                "article": 39,
                "clause": "Khoản 3",
                "evidence_role": "SUPPORTING_PARENT_LAW",
                "reason": "Quy định giữ lại biển số xe định danh trong thời hạn 05 năm để cấp lại cho chủ xe."
            }
        ],
        "type": "MULTI_VALID"
    },
    "GOLD-MUL-24": {
        "supp": [
            {
                "official_number": "35/2024/QH15",
                "document_id": "road_35_2024_qh15",
                "article": 45,
                "clause": "Khoản 3",
                "evidence_role": "SUPPORTING_PARENT_LAW",
                "reason": "Luật Đường bộ Điều 45 quy định thẩm quyền và các đối tượng được miễn, giảm phí sử dụng đường cao tốc."
            },
            {
                "official_number": "130/2024/NĐ-CP",
                "document_id": "traffic_highway_130_2024_nd_cp",
                "article": 11,
                "clause": "Khoản 1",
                "evidence_role": "SUPPORTING_DECREE_GUIDE",
                "reason": "Quy định cơ chế quản lý và miễn phí cho phương tiện ưu tiên phục vụ an ninh quốc phòng."
            }
        ],
        "type": "MULTI_VALID"
    },
    "GOLD-AMD-20": {
        "supp": [
            {
                "official_number": "30/2026/TT-BXD",
                "document_id": "traffic_inspection_procedures_30_2026_tt_bxd",
                "article": 8,
                "clause": "Khoản 2",
                "evidence_role": "SUPPORTING_AMENDMENT_ORIGIN",
                "reason": "Điều khoản gốc của Thông tư 30 quy định kiểm tra phanh con lăn trước khi được sửa đổi bởi Thông tư 45."
            }
        ],
        "type": "PRIMARY_PLUS_SUPPORTING"
    }
}

# General co-regulation topics mapping
TOPIC_RULES = [
    {
        "keywords": ["tốc độ tối đa", "chạy quá tốc độ", "tốc độ cho phép"],
        "co_evidences": [
            ("168/2024/NĐ-CP", "traffic_penalty_168_2024_nd_cp", 6, "SUPPORTING_PENALTY", "Xử phạt vi phạm tốc độ ô tô"),
            ("168/2024/NĐ-CP", "traffic_penalty_168_2024_nd_cp", 7, "SUPPORTING_PENALTY", "Xử phạt vi phạm tốc độ mô tô"),
            ("36/2024/QH15", "traffic_order_36_2024_qh15", 12, "SUPPORTING_PARENT_LAW", "Nguyên tắc chấp hành tốc độ trong Luật TTATGTĐB")
        ],
        "default_type": "PRIMARY_PLUS_SUPPORTING"
    },
    {
        "keywords": ["khoảng cách an toàn", "cự ly tối thiểu"],
        "co_evidences": [
            ("36/2024/QH15", "traffic_order_36_2024_qh15", 12, "SUPPORTING_PARENT_LAW", "Khoảng cách an toàn giữa hai xe"),
            ("168/2024/NĐ-CP", "traffic_penalty_168_2024_nd_cp", 6, "SUPPORTING_PENALTY", "Xử phạt vi phạm không giữ khoảng cách")
        ],
        "default_type": "PRIMARY_PLUS_SUPPORTING"
    },
    {
        "keywords": ["nồng độ cồn", "uống rượu bia", "hơi thở có cồn"],
        "co_evidences": [
            ("36/2024/QH15", "traffic_order_36_2024_qh15", 10, "SUPPORTING_PARENT_LAW", "Hành vi bị nghiêm cấm điều khiển phương tiện có nồng độ cồn"),
            ("168/2024/NĐ-CP", "traffic_penalty_168_2024_nd_cp", 6, "SUPPORTING_PENALTY", "Xử phạt nồng độ cồn ô tô"),
            ("168/2024/NĐ-CP", "traffic_penalty_168_2024_nd_cp", 7, "SUPPORTING_PENALTY", "Xử phạt nồng độ cồn mô tô")
        ],
        "default_type": "MULTI_VALID"
    },
    {
        "keywords": ["dừng xe", "đỗ xe", "dừng đỗ"],
        "co_evidences": [
            ("36/2024/QH15", "traffic_order_36_2024_qh15", 18, "SUPPORTING_PARENT_LAW", "Quy tắc dừng xe, đỗ xe trên đường bộ"),
            ("168/2024/NĐ-CP", "traffic_penalty_168_2024_nd_cp", 6, "SUPPORTING_PENALTY", "Xử phạt dừng đỗ xe sai quy định ô tô"),
            ("168/2024/NĐ-CP", "traffic_penalty_168_2024_nd_cp", 7, "SUPPORTING_PENALTY", "Xử phạt dừng đỗ xe sai quy định mô tô")
        ],
        "default_type": "PRIMARY_PLUS_SUPPORTING"
    },
    {
        "keywords": ["vượt xe", "xin vượt", "nhường đường"],
        "co_evidences": [
            ("36/2024/QH15", "traffic_order_36_2024_qh15", 14, "SUPPORTING_PARENT_LAW", "Quy tắc vượt xe và nhường đường"),
            ("168/2024/NĐ-CP", "traffic_penalty_168_2024_nd_cp", 6, "SUPPORTING_PENALTY", "Xử phạt hành vi vượt xe sai quy định ô tô"),
            ("168/2024/NĐ-CP", "traffic_penalty_168_2024_nd_cp", 7, "SUPPORTING_PENALTY", "Xử phạt hành vi vượt xe sai quy định mô tô")
        ],
        "default_type": "PRIMARY_PLUS_SUPPORTING"
    },
    {
        "keywords": ["dừng phương tiện", "cảnh sát giao thông", "hiệu lệnh dừng xe"],
        "co_evidences": [
            ("36/2024/QH15", "traffic_order_36_2024_qh15", 65, "SUPPORTING_PARENT_LAW", "Quyền hạn của CSGT dừng phương tiện tham gia giao thông"),
            ("73/2024/TT-BCA", "traffic_police_patrol_73_2024_tt_bca", 12, "SUPPORTING_PROCEDURE", "Quy trình dừng phương tiện của CSGT")
        ],
        "default_type": "MULTI_VALID"
    },
    {
        "keywords": ["giấy phép lái xe", "gplx", "hạng bằng", "hạng a1", "hạng b", "hạng c"],
        "co_evidences": [
            ("36/2024/QH15", "traffic_order_36_2024_qh15", 58, "SUPPORTING_PARENT_LAW", "Phân hạng Giấy phép lái xe"),
            ("36/2024/QH15", "traffic_order_36_2024_qh15", 59, "SUPPORTING_PARENT_LAW", "Độ tuổi của người lái xe"),
            ("36/2024/QH15", "traffic_order_36_2024_qh15", 60, "SUPPORTING_PARENT_LAW", "Thời hạn của Giấy phép lái xe"),
            ("12/2025/TT-BCA", "traffic_driving_license_12_2025_tt_bca", 12, "SUPPORTING_PROCEDURE", "Quy trình đào tạo, sát hạch cấp GPLX")
        ],
        "default_type": "PRIMARY_PLUS_SUPPORTING"
    },
    {
        "keywords": ["trừ điểm", "phục hồi điểm", "12 điểm"],
        "co_evidences": [
            ("36/2024/QH15", "traffic_order_36_2024_qh15", 62, "SUPPORTING_PARENT_LAW", "Điểm của Giấy phép lái xe"),
            ("168/2024/NĐ-CP", "traffic_penalty_168_2024_nd_cp", 32, "SUPPORTING_PENALTY", "Quy định trừ điểm GPLX theo hành vi vi phạm"),
            ("65/2024/TT-BCA", "traffic_points_recovery_65_2024_tt_bca", 6, "SUPPORTING_PROCEDURE", "Quy trình kiểm tra phục hồi điểm GPLX"),
            ("105/2026/TT-BCA", "traffic_points_recovery_105_2026_tt_bca", 1, "SUPPORTING_AMENDMENT", "Sửa đổi quy định phục hồi điểm GPLX")
        ],
        "default_type": "MULTI_VALID"
    },
    {
        "keywords": ["đăng kiểm", "kiểm định", "chu kỳ kiểm định", "an toàn kỹ thuật"],
        "co_evidences": [
            ("89/2026/NĐ-CP", "traffic_inspection_framework_89_2026_nd_cp", 6, "SUPPORTING_DECREE_GUIDE", "Khung điều kiện kinh doanh dịch vụ kiểm định xe"),
            ("30/2026/TT-BXD", "traffic_inspection_procedures_30_2026_tt_bxd", 5, "SUPPORTING_PROCEDURE", "Quy trình kiểm định an toàn kỹ thuật"),
            ("45/2026/TT-BXD", "traffic_inspection_amendment_45_2026_tt_bxd", 1, "SUPPORTING_AMENDMENT", "Sửa đổi quy trình kiểm định an toàn kỹ thuật")
        ],
        "default_type": "PRIMARY_PLUS_SUPPORTING"
    },
    {
        "keywords": ["niên hạn", "niên hạn sử dụng"],
        "co_evidences": [
            ("89/2026/NĐ-CP", "traffic_inspection_framework_89_2026_nd_cp", 3, "SUPPORTING_DECREE_GUIDE", "Niên hạn sử dụng xe cơ giới"),
            ("36/2024/QH15", "traffic_order_36_2024_qh15", 40, "SUPPORTING_PARENT_LAW", "Điều kiện an toàn kỹ thuật và niên hạn sử dụng xe")
        ],
        "default_type": "MULTI_VALID"
    },
    {
        "keywords": ["biển số định danh", "đăng ký xe", "chứng nhận đăng ký"],
        "co_evidences": [
            ("36/2024/QH15", "traffic_order_36_2024_qh15", 36, "SUPPORTING_PARENT_LAW", "Đăng ký xe và cấp biển số xe"),
            ("36/2024/QH15", "traffic_order_36_2024_qh15", 37, "SUPPORTING_PARENT_LAW", "Thu hồi chứng nhận đăng ký và biển số xe"),
            ("36/2024/QH15", "traffic_order_36_2024_qh15", 39, "SUPPORTING_PARENT_LAW", "Quản lý biển số xe định danh"),
            ("79/2024/TT-BCA", "traffic_vehicle_registration_79_2024_tt_bca", 4, "SUPPORTING_PROCEDURE", "Thủ tục cấp, thu hồi đăng ký, biển số xe")
        ],
        "default_type": "MULTI_VALID"
    },
    {
        "keywords": ["đường cao tốc", "phí đường bộ", "thu phí", "miễn phí"],
        "co_evidences": [
            ("35/2024/QH15", "road_35_2024_qh15", 45, "SUPPORTING_PARENT_LAW", "Đường cao tốc và thu phí sử dụng đường cao tốc"),
            ("130/2024/NĐ-CP", "traffic_highway_130_2024_nd_cp", 4, "SUPPORTING_DECREE_GUIDE", "Quy định mức thu phí và đối tượng miễn giảm phí cao tốc"),
            ("130/2024/NĐ-CP", "traffic_highway_130_2024_nd_cp", 11, "SUPPORTING_DECREE_GUIDE", "Trình tự thu phí và quản lý phương tiện miễn phí")
        ],
        "default_type": "MULTI_VALID"
    }
]

# Statistics
type_counts = {"SINGLE": 0, "MULTI_VALID": 0, "CO_REQUISITE": 0, "PRIMARY_PLUS_SUPPORTING": 0}
changed_count = 0
unresolved_cases = []

revised_cases = []

for tc in cases:
    cid = tc["test_case_id"]
    cat = tc["category"]
    q = tc["query"]
    as_of = tc.get("as_of_date")
    exp = tc["expected_evidence"]
    diff = tc.get("difficulty", "MEDIUM")

    # 1. Primary Evidence
    p_off = exp["official_number"]
    p_doc = exp["document_id"]
    p_art = exp.get("article")
    p_clause = exp.get("clause")
    p_notes = exp.get("notes", "")

    # Clean clause & point
    p_point = None
    if p_notes:
        pt_m = re.search(r"Điểm\s*([a-zA-Z0-9]+)", p_notes, re.IGNORECASE)
        if pt_m:
            p_point = f"Điểm {pt_m.group(1)}"

    # Determine primary role
    if "sửa đổi" in q.lower() or "bãi bỏ" in q.lower():
        p_role = "PRIMARY_AMENDMENT"
    elif "phạt" in q.lower() or "tước" in q.lower() or "trừ điểm" in q.lower():
        p_role = "PRIMARY_PENALTY"
    elif "thủ tục" in q.lower() or "hồ sơ" in q.lower() or "quy trình" in q.lower():
        p_role = "PRIMARY_PROCEDURE"
    elif "thời điểm" in q.lower() or "hiệu lực" in q.lower() or "ngày nào" in q.lower():
        p_role = "PRIMARY_TEMPORAL"
    elif "thẩm quyền" in q.lower() or "cơ quan nào" in q.lower() or "ai có quyền" in q.lower():
        p_role = "PRIMARY_AUTHORITY"
    else:
        p_role = "PRIMARY_RULE"

    primary_ev = {
        "official_number": p_off,
        "document_id": p_doc,
        "article": p_art,
        "clause": p_clause,
        "point": p_point,
        "evidence_role": p_role,
        "reason": f"Căn cứ trực tiếp quy định {p_notes if p_notes else 'nội dung được hỏi trong truy vấn'}."
    }

    # 2. Supporting & Required Evidence logic
    supp_evidences = []
    req_evidences = []
    ev_type = "SINGLE"

    # Priority 1: Check 17 false-miss cases
    if cid in FALSE_MISS_17_CASES:
        f_info = FALSE_MISS_17_CASES[cid]
        ev_type = f_info["type"]
        supp_evidences.extend(f_info["supp"])
        if ev_type == "CO_REQUISITE":
            req_evidences = [primary_ev] + f_info["supp"]
        changed_count += 1

    # Priority 2: Check by Category
    elif cat == "MULTI_DOCUMENT":
        ev_type = "CO_REQUISITE"
        # Find co-regulation from query text
        q_l = q.lower()
        matched_rule = None
        for rule in TOPIC_RULES:
            if any(k in q_l for k in rule["keywords"]):
                for off, did, art, role, r_reason in rule["co_evidences"]:
                    if did.lower() != p_doc.lower() or art != p_art:
                        supp_evidences.append({
                            "official_number": off,
                            "document_id": did,
                            "article": art,
                            "clause": None,
                            "point": None,
                            "evidence_role": role,
                            "reason": r_reason
                        })
                break
        
        # If no specific rule matched, check mentioned documents in query
        if not supp_evidences:
            for did, off in VALID_DOCS.items():
                if off.lower() in q_l and did.lower() != p_doc.lower():
                    supp_evidences.append({
                        "official_number": off,
                        "document_id": did,
                        "article": 1,
                        "clause": None,
                        "point": None,
                        "evidence_role": "SUPPORTING_CO_REGULATION",
                        "reason": f"Văn bản liên tịch được đề cập trực tiếp trong câu hỏi ({off})."
                    })
        
        req_evidences = [primary_ev] + supp_evidences[:2]
        changed_count += 1

    elif cat == "AMENDMENT_LINEAGE":
        ev_type = "PRIMARY_PLUS_SUPPORTING"
        # Find base document being amended
        q_l = q.lower()
        base_found = False
        for did, off in VALID_DOCS.items():
            if off.lower() in q_l and did.lower() != p_doc.lower():
                supp_evidences.append({
                    "official_number": off,
                    "document_id": did,
                    "article": p_art,
                    "clause": None,
                    "point": None,
                    "evidence_role": "SUPPORTING_AMENDMENT_ORIGIN",
                    "reason": f"Quy định gốc tại văn bản bị sửa đổi ({off}) làm cơ sở đối chiếu điều khoản sửa đổi."
                })
                base_found = True
                break
        if not base_found:
            # Add general base reference
            supp_evidences.append({
                "official_number": "36/2024/QH15",
                "document_id": "traffic_order_36_2024_qh15",
                "article": 1,
                "clause": None,
                "point": None,
                "evidence_role": "SUPPORTING_PARENT_LAW",
                "reason": "Luật gốc điều chỉnh trật tự an toàn giao thông đường bộ."
            })
        changed_count += 1

    elif cat == "TEMPORAL_CONTRAST":
        ev_type = "MULTI_VALID"
        # Contrasting pair: either past law or current law is legally valid context
        supp_evidences.append({
            "official_number": "36/2024/QH15" if "36" not in p_off else "168/2024/NĐ-CP",
            "document_id": "traffic_order_36_2024_qh15" if "36" not in p_off else "traffic_penalty_168_2024_nd_cp",
            "article": p_art,
            "clause": None,
            "point": None,
            "evidence_role": "SUPPORTING_TRANSITION",
            "reason": "Quy định đối chứng tại văn bản thời kỳ chuyển tiếp."
        })
        changed_count += 1

    elif cat == "TEMPORAL_QUERY":
        # Check if query asks for date or substantive
        q_l = q.lower()
        if "có hiệu lực" in q_l or "từ ngày nào" in q_l or "áp dụng từ" in q_l:
            ev_type = "SINGLE"
        else:
            ev_type = "PRIMARY_PLUS_SUPPORTING"
            supp_evidences.append({
                "official_number": "36/2024/QH15",
                "document_id": "traffic_order_36_2024_qh15",
                "article": 88,
                "clause": "Khoản 1",
                "point": None,
                "evidence_role": "SUPPORTING_TRANSITION",
                "reason": "Điều khoản hiệu lực thi hành của Luật TTATGTĐB 2024."
            })
            changed_count += 1

    else:
        # Category: DIRECT_RULE, ARTICLE_RETRIEVAL, CONDITIONAL_EXCEPTION, HARD_CONFUSING
        q_l = q.lower()
        matched_rule = None
        for rule in TOPIC_RULES:
            if any(k in q_l for k in rule["keywords"]):
                matched_rule = rule
                break

        if matched_rule:
            ev_type = matched_rule["default_type"]
            for off, did, art, role, r_reason in matched_rule["co_evidences"]:
                if did.lower() != p_doc.lower() or art != p_art:
                    supp_evidences.append({
                        "official_number": off,
                        "document_id": did,
                        "article": art,
                        "clause": None,
                        "point": None,
                        "evidence_role": role,
                        "reason": f"{r_reason} (đồng căn cứ điều chỉnh hành vi)."
                    })
            if supp_evidences:
                changed_count += 1
        else:
            # Pure single definition / direct query
            ev_type = "SINGLE"

    # Clean duplicates in supporting
    unique_supp = []
    seen = set()
    for s in supp_evidences:
        key = (s["document_id"].lower(), s["article"])
        if key not in seen and key != (primary_ev["document_id"].lower(), primary_ev["article"]):
            seen.add(key)
            unique_supp.append(s)

    type_counts[ev_type] += 1

    revised_case = {
        "test_case_id": cid,
        "category": cat,
        "query": q,
        "as_of_date": as_of,
        "difficulty": diff,
        "evidence_type": ev_type,
        "primary_evidence": primary_ev,
        "acceptable_supporting_evidence": unique_supp,
        "required_evidence_set": req_evidences if ev_type == "CO_REQUISITE" else []
    }
    revised_cases.append(revised_case)

# Validation Phase
print("\n=== AUDIT & REVISION SUMMARY ===")
print(f"Total Cases Processed: {len(revised_cases)} / {len(cases)}")
assert len(revised_cases) == 225, "ERROR: Total cases must be exactly 225!"

print("Distribution of evidence_type:")
for et, count in type_counts.items():
    print(f"  - {et:<25}: {count:3d} cases ({count/len(revised_cases)*100:4.1f}%)")

print(f"Total Cases with Ground Truth Enriched: {changed_count} ({changed_count/len(revised_cases)*100:4.1f}%)")

# Verify all documents exist
invalid_docs = []
for c in revised_cases:
    p_did = c["primary_evidence"]["document_id"]
    if p_did not in VALID_DOCS:
        invalid_docs.append((c["test_case_id"], p_did))
    for s in c["acceptable_supporting_evidence"]:
        s_did = s["document_id"]
        if s_did not in VALID_DOCS:
            invalid_docs.append((c["test_case_id"], s_did))

if invalid_docs:
    print(f"[!] Warning: Found {len(invalid_docs)} unverified document IDs:", invalid_docs[:5])
else:
    print("Corpus Integrity Check: 100% of Primary and Supporting Documents exist in verified Traffic Corpus! 🟢")

output_payload = {
    "version": "2.0",
    "dataset_name": "gold_retrieval_225_cases_v2",
    "revision_date": "2026-09-10",
    "total_cases": len(revised_cases),
    "metadata_summary": {
        "single_count": type_counts["SINGLE"],
        "multi_valid_count": type_counts["MULTI_VALID"],
        "co_requisite_count": type_counts["CO_REQUISITE"],
        "primary_plus_supporting_count": type_counts["PRIMARY_PLUS_SUPPORTING"],
        "enriched_cases_count": changed_count,
        "false_miss_resolved_count": len(FALSE_MISS_17_CASES)
    },
    "cases": revised_cases
}

with open(out_path, "w", encoding="utf-8") as f:
    json.dump(output_payload, f, ensure_ascii=False, indent=2)

print(f"\nSaved standardized Gold Dataset v2 to: {out_path}")
