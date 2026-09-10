"""
GENERATE 60 GENERATION EVALUATION TEST CASES
============================================
Creates 60 carefully crafted legal cases across 10 categories (6 cases each)
specifically designed to test LLM generation faithfulness, factual correctness,
calculation accuracy, citation grounding, and honest abstention.
"""

import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
OUTPUT_FILE = PROJECT_ROOT / "data" / "generation_evaluation" / "generation_60_cases.json"
OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

cases = [
    # =========================================================================
    # A. DIRECT FACTUAL LEGAL QUESTIONS (6 cases)
    # =========================================================================
    {
        "case_id": "GEN-FAC-01",
        "category": "DIRECT_FACTUAL",
        "dimension": "Quy tắc chung đi đường",
        "difficulty": "EASY",
        "evidence_type": "SINGLE",
        "query": "Người tham gia giao thông đường bộ phải đi bên nào theo quy định của Luật Trật tự, an toàn giao thông đường bộ 2024?",
        "expected_answer": "Người tham gia giao thông đường bộ phải đi bên phải theo chiều đi của mình, đi đúng làn đường, phần đường quy định và chấp hành báo hiệu đường bộ.",
        "required_evidence": ["traffic_order_36_2024_qh15:10"],
        "expected_citations": ["Điều 10 Luật Trật tự, an toàn giao thông đường bộ 2024"],
        "allow_abstention": False
    },
    {
        "case_id": "GEN-FAC-02",
        "category": "DIRECT_FACTUAL",
        "dimension": "Quy định thắt dây an toàn và trẻ em",
        "difficulty": "EASY",
        "evidence_type": "SINGLE",
        "query": "Theo Luật Trật tự an toàn giao thông đường bộ 2024, trẻ em dưới bao nhiêu tuổi và chiều cao dưới bao nhiêu mét thì không được ngồi cùng hàng ghế với người lái xe ô tô?",
        "expected_answer": "Trẻ em dưới 10 tuổi và chiều cao dưới 1,35 mét trên xe ô tô không được cho ngồi cùng hàng ghế với người lái xe (trừ loại xe chỉ có một hàng ghế) và phải sử dụng thiết bị an toàn phù hợp.",
        "required_evidence": ["traffic_order_36_2024_qh15:10"],
        "expected_citations": ["Khoản 3 Điều 10 Luật Trật tự, an toàn giao thông đường bộ 2024"],
        "allow_abstention": False
    },
    {
        "case_id": "GEN-FAC-03",
        "category": "DIRECT_FACTUAL",
        "dimension": "Thời gian thử việc",
        "difficulty": "EASY",
        "evidence_type": "SINGLE",
        "query": "Thời gian thử việc đối với công việc có chức danh nghề nghiệp cần trình độ chuyên môn, kỹ thuật từ cao đẳng trở lên tối đa là bao nhiêu ngày theo Bộ luật Lao động 2019?",
        "expected_answer": "Thời gian thử việc tối đa không quá 60 ngày đối với công việc có chức danh nghề nghiệp cần trình độ chuyên môn, kỹ thuật từ cao đẳng trở lên.",
        "required_evidence": ["bllđ_45_2019_qh14:25"],
        "expected_citations": ["Khoản 2 Điều 25 Bộ luật Lao động 2019"],
        "allow_abstention": False
    },
    {
        "case_id": "GEN-FAC-04",
        "category": "DIRECT_FACTUAL",
        "dimension": "Lương thử việc",
        "difficulty": "EASY",
        "evidence_type": "SINGLE",
        "query": "Tiền lương của người lao động trong thời gian thử việc do hai bên thỏa thuận nhưng ít nhất phải bằng bao nhiêu phần trăm mức lương của công việc đó?",
        "expected_answer": "Tiền lương trong thời gian thử việc ít nhất phải bằng 85% mức lương của công việc đó.",
        "required_evidence": ["bllđ_45_2019_qh14:26"],
        "expected_citations": ["Điều 26 Bộ luật Lao động 2019"],
        "allow_abstention": False
    },
    {
        "case_id": "GEN-FAC-05",
        "category": "DIRECT_FACTUAL",
        "dimension": "Thứ tự ưu tiên báo hiệu đường bộ",
        "difficulty": "MEDIUM",
        "evidence_type": "SINGLE",
        "query": "Khi tham gia giao thông đường bộ, thứ tự ưu tiên chấp hành báo hiệu đường bộ từ trên xuống dưới được quy định như thế nào?",
        "expected_answer": "Thứ tự ưu tiên: 1. Hiệu lệnh của người điều khiển giao thông; 2. Tín hiệu đèn giao thông; 3. Biển báo hiệu đường bộ; 4. Vạch kẻ đường và các dấu hiệu khác; 5. Cọc tiêu, rào chắn, tiêu phản quang; 6. Thiết bị âm thanh báo hiệu.",
        "required_evidence": ["traffic_order_36_2024_qh15:11"],
        "expected_citations": ["Khoản 2 Điều 11 Luật Trật tự, an toàn giao thông đường bộ 2024"],
        "allow_abstention": False
    },
    {
        "case_id": "GEN-FAC-06",
        "category": "DIRECT_FACTUAL",
        "dimension": "Các loại hợp đồng lao động",
        "difficulty": "EASY",
        "evidence_type": "SINGLE",
        "query": "Theo Bộ luật Lao động 2019, hợp đồng lao động được giao kết theo mấy loại và là những loại nào?",
        "expected_answer": "Hợp đồng lao động được giao kết theo 02 loại: 1. Hợp đồng lao động không xác định thời hạn; 2. Hợp đồng lao động xác định thời hạn (thời hạn không quá 36 tháng).",
        "required_evidence": ["bllđ_45_2019_qh14:20"],
        "expected_citations": ["Khoản 1 Điều 20 Bộ luật Lao động 2019"],
        "allow_abstention": False
    },

    # =========================================================================
    # B. NUMERIC CALCULATION & QUANTITATIVE REASONING (6 cases)
    # =========================================================================
    {
        "case_id": "GEN-NUM-01",
        "category": "NUMERIC_CALCULATION",
        "dimension": "Làm tròn thời gian trợ cấp thôi việc",
        "difficulty": "HARD",
        "evidence_type": "CO_REQUISITE",
        "query": "Người lao động làm việc tại doanh nghiệp được 5 năm 9 tháng thì thời gian làm việc để tính trợ cấp thôi việc có tháng lẻ được làm tròn thành mấy năm?",
        "expected_answer": "Theo Điểm c Khoản 3 Điều 8 Nghị định 145/2020/NĐ-CP, trường hợp có tháng lẻ từ trên 06 tháng được tính bằng 01 năm làm việc. Do đó, 09 tháng lẻ được tính tròn thành 01 năm, tổng thời gian tính trợ cấp thôi việc là 06 năm làm việc (tương đương 03 tháng tiền lương trợ cấp theo Điều 46 BLLĐ 2019).",
        "required_evidence": ["nd_145_2020_nd_cp:8", "bllđ_45_2019_qh14:46"],
        "expected_citations": ["Điểm c Khoản 3 Điều 8 Nghị định 145/2020/NĐ-CP", "Điều 46 Bộ luật Lao động 2019"],
        "allow_abstention": False
    },
    {
        "case_id": "GEN-NUM-02",
        "category": "NUMERIC_CALCULATION",
        "dimension": "Thời gian trợ cấp thôi việc lẻ 4 tháng",
        "difficulty": "HARD",
        "evidence_type": "CO_REQUISITE",
        "query": "Nếu người lao động có thời gian làm việc tính trợ cấp thôi việc là 3 năm 4 tháng thì 4 tháng lẻ được làm tròn như thế nào?",
        "expected_answer": "Theo Điểm c Khoản 3 Điều 8 Nghị định 145/2020/NĐ-CP, trường hợp thời gian làm việc có tháng lẻ ít hơn hoặc bằng 06 tháng thì được tính bằng 1/2 năm (0,5 năm). Do đó 3 năm 4 tháng được tính thành 3,5 năm làm việc.",
        "required_evidence": ["nd_145_2020_nd_cp:8"],
        "expected_citations": ["Điểm c Khoản 3 Điều 8 Nghị định 145/2020/NĐ-CP"],
        "allow_abstention": False
    },
    {
        "case_id": "GEN-NUM-03",
        "category": "NUMERIC_CALCULATION",
        "dimension": "Tuổi nghỉ hưu nam sinh 1970",
        "difficulty": "HARD",
        "evidence_type": "PRIMARY_PLUS_SUPPORTING",
        "query": "Lao động nam sinh tháng 05 năm 1970 làm việc trong điều kiện bình thường thì nghỉ hưu ở độ tuổi nào và vào năm nào?",
        "expected_answer": "Lao động nam sinh năm 1970 làm việc trong điều kiện bình thường nghỉ hưu ở tuổi đủ 62 tuổi (lộ trình tăng tuổi nghỉ hưu của nam kết thúc vào năm 2028 ở mốc 62 tuổi theo Điều 169 BLLĐ 2019 và Phụ lục I Nghị định 135/2020/NĐ-CP). Thời điểm nghỉ hưu là năm 2032 (tháng 5/2032 đủ 62 tuổi).",
        "required_evidence": ["nd_135_2020_nd_cp:4", "bllđ_45_2019_qh14:169"],
        "expected_citations": ["Điều 4 và Phụ lục I Nghị định 135/2020/NĐ-CP", "Điều 169 Bộ luật Lao động 2019"],
        "allow_abstention": False
    },
    {
        "case_id": "GEN-NUM-04",
        "category": "NUMERIC_CALCULATION",
        "dimension": "Thời điểm hưởng chế độ hưu trí",
        "difficulty": "MEDIUM",
        "evidence_type": "SINGLE",
        "query": "Nếu người lao động đủ tuổi nghỉ hưu vào ngày 15/08/2024 thì thời điểm hưởng chế độ hưu trí bắt đầu từ ngày nào?",
        "expected_answer": "Thời điểm nghỉ hưu là kết thúc ngày cuối cùng của tháng đủ tuổi nghỉ hưu (ngày 31/08/2024). Thời điểm bắt đầu hưởng chế độ hưu trí là ngày đầu tiên của tháng liền kề sau thời điểm nghỉ hưu, tức là ngày 01/09/2024.",
        "required_evidence": ["nd_135_2020_nd_cp:3"],
        "expected_citations": ["Điều 3 Nghị định 135/2020/NĐ-CP"],
        "allow_abstention": False
    },
    {
        "case_id": "GEN-NUM-05",
        "category": "NUMERIC_CALCULATION",
        "dimension": "Tổng điểm Giấy phép lái xe",
        "difficulty": "EASY",
        "evidence_type": "SINGLE",
        "query": "Theo Luật Trật tự, an toàn giao thông đường bộ 2024, Giấy phép lái xe của mỗi người có tổng cộng bao nhiêu điểm trong một năm?",
        "expected_answer": "Giấy phép lái xe bao gồm 12 điểm. Số điểm bị trừ mỗi lần vi phạm tùy thuộc vào tính chất, mức độ của hành vi vi phạm theo quy định của Chính phủ.",
        "required_evidence": ["traffic_order_36_2024_qh15:62"],
        "expected_citations": ["Điều 62 Luật Trật tự, an toàn giao thông đường bộ 2024"],
        "allow_abstention": False
    },
    {
        "case_id": "GEN-NUM-06",
        "category": "NUMERIC_CALCULATION",
        "dimension": "Số ngày nghỉ phép năm tăng theo thâm niên",
        "difficulty": "MEDIUM",
        "evidence_type": "SINGLE",
        "query": "Cứ sau bao nhiêu năm làm việc cho một người sử dụng lao động thì số ngày nghỉ hằng năm của người lao động được tăng thêm 01 ngày?",
        "expected_answer": "Cứ đủ 05 năm làm việc cho một người sử dụng lao động thì số ngày nghỉ hằng năm của người lao động được tăng thêm tương ứng 01 ngày.",
        "required_evidence": ["bllđ_45_2019_qh14:114"],
        "expected_citations": ["Điều 114 Bộ luật Lao động 2019"],
        "allow_abstention": False
    },

    # =========================================================================
    # C. MULTI-EVIDENCE QUESTIONS (6 cases)
    # =========================================================================
    {
        "case_id": "GEN-MUL-01",
        "category": "MULTI_EVIDENCE",
        "dimension": "Cơ chế trừ điểm GPLX và thẩm quyền",
        "difficulty": "MEDIUM",
        "evidence_type": "MULTI_VALID",
        "query": "Cơ chế trừ điểm Giấy phép lái xe được quy định tại Luật Trật tự an toàn giao thông đường bộ 2024 và được cụ thể hóa thẩm quyền, thủ tục tại văn bản nào?",
        "expected_answer": "Cơ chế điểm và trừ điểm GPLX được quy định tại Điều 62 Luật Trật tự, an toàn giao thông đường bộ 2024, hành vi và thẩm quyền trừ điểm được quy định chi tiết tại Nghị định 168/2024/NĐ-CP và Thông tư 65/2024/TT-BCA.",
        "required_evidence": ["traffic_order_36_2024_qh15:62", "traffic_penalty_168_2024_nd_cp:50"],
        "expected_citations": ["Điều 62 Luật Trật tự, an toàn giao thông đường bộ 2024", "Nghị định 168/2024/NĐ-CP"],
        "allow_abstention": False
    },
    {
        "case_id": "GEN-MUL-02",
        "category": "MULTI_EVIDENCE",
        "dimension": "Sáp nhập doanh nghiệp và phương án lao động",
        "difficulty": "HARD",
        "evidence_type": "CO_REQUISITE",
        "query": "Khi doanh nghiệp chia tách, sáp nhập mà ảnh hưởng đến việc làm thì phải xây dựng phương án sử dụng lao động theo quy định của BLLĐ 2019 và Nghị định 145/2020 như thế nào?",
        "expected_answer": "Theo Điều 44 và Điều 47 BLLĐ 2019 và Điều 8 Nghị định 145/2020/NĐ-CP, người sử dụng lao động phải xây dựng và thực hiện phương án sử dụng lao động với sự tham gia của tổ chức đại diện người lao động tại cơ sở; giải quyết trợ cấp mất việc làm theo quy định.",
        "required_evidence": ["bllđ_45_2019_qh14:44", "nd_145_2020_nd_cp:8"],
        "expected_citations": ["Điều 44 Bộ luật Lao động 2019", "Điều 8 Nghị định 145/2020/NĐ-CP"],
        "allow_abstention": False
    },
    {
        "case_id": "GEN-MUL-03",
        "category": "MULTI_EVIDENCE",
        "dimension": "Tốc độ và khoảng cách an toàn",
        "difficulty": "MEDIUM",
        "evidence_type": "MULTI_VALID",
        "query": "Quy định chung về chấp hành tốc độ và khoảng cách an toàn giữa các xe nằm ở Luật Trật tự an toàn giao thông đường bộ 2024 và quy định chi tiết tốc độ tối đa cho phép nằm ở văn bản nào?",
        "expected_answer": "Quy định nguyên tắc về tốc độ và khoảng cách an toàn nằm ở Điều 12 Luật Trật tự, an toàn giao thông đường bộ 2024; quy định chi tiết về tốc độ tối đa cho phép và khoảng cách an toàn giữa hai xe nằm ở Thông tư 38/2024/TT-BGTVT.",
        "required_evidence": ["traffic_order_36_2024_qh15:12", "traffic_speed_distance_38_2024_tt_bgtvt:6"],
        "expected_citations": ["Điều 12 Luật Trật tự, an toàn giao thông đường bộ 2024", "Thông tư 38/2024/TT-BGTVT"],
        "allow_abstention": False
    },
    {
        "case_id": "GEN-MUL-04",
        "category": "MULTI_EVIDENCE",
        "dimension": "Hồ sơ đăng ký xe và biển số định danh",
        "difficulty": "MEDIUM",
        "evidence_type": "MULTI_VALID",
        "query": "Biển số xe cơ giới được cấp và quản lý theo mã định danh của chủ xe theo quy định của văn bản nào và thủ tục đăng ký xe lần đầu cần những giấy tờ gì?",
        "expected_answer": "Biển số xe được cấp và quản lý theo mã định danh theo quy định của Thông tư 79/2024/TT-BCA và Luật Trật tự, an toàn giao thông đường bộ 2024. Hồ sơ đăng ký lần đầu gồm: giấy khai đăng ký xe, giấy tờ của chủ xe, giấy tờ nguồn gốc xe, chứng từ nộp lệ phí trước bạ.",
        "required_evidence": ["traffic_vehicle_registration_79_2024_tt_bca:3", "traffic_order_36_2024_qh15:37"],
        "expected_citations": ["Thông tư 79/2024/TT-BCA", "Luật Trật tự, an toàn giao thông đường bộ 2024"],
        "allow_abstention": False
    },
    {
        "case_id": "GEN-MUL-05",
        "category": "MULTI_EVIDENCE",
        "dimension": "Quyền đơn phương chấm dứt HĐLĐ và nghĩa vụ báo trước",
        "difficulty": "MEDIUM",
        "evidence_type": "PRIMARY_PLUS_SUPPORTING",
        "query": "Người lao động có quyền đơn phương chấm dứt hợp đồng lao động không cần lý do nhưng phải báo trước bao nhiêu ngày theo Bộ luật Lao động 2019?",
        "expected_answer": "Theo Điều 35 BLLĐ 2019, người lao động có quyền đơn phương chấm dứt HĐLĐ nhưng phải báo trước: ít nhất 45 ngày với HĐLĐ không xác định thời hạn; ít nhất 30 ngày với HĐLĐ xác định thời hạn từ 12-36 tháng; ít nhất 03 ngày làm việc với HĐLĐ dưới 12 tháng.",
        "required_evidence": ["bllđ_45_2019_qh14:35"],
        "expected_citations": ["Điều 35 Bộ luật Lao động 2019"],
        "allow_abstention": False
    },
    {
        "case_id": "GEN-MUL-06",
        "category": "MULTI_EVIDENCE",
        "dimension": "Xử lý kỷ luật sa thải và trình tự họp",
        "difficulty": "HARD",
        "evidence_type": "CO_REQUISITE",
        "query": "Căn cứ áp dụng hình thức kỷ luật sa thải và nguyên tắc, trình tự xử lý kỷ luật lao động được quy định tại các Điều nào của BLLĐ 2019?",
        "expected_answer": "Căn cứ áp dụng hình thức kỷ luật sa thải quy định tại Điều 125 BLLĐ 2019. Nguyên tắc, trình tự và thủ tục xử lý kỷ luật lao động được quy định tại Điều 122 BLLĐ 2019 và hướng dẫn tại Nghị định 145/2020/NĐ-CP.",
        "required_evidence": ["bllđ_45_2019_qh14:122", "bllđ_45_2019_qh14:125"],
        "expected_citations": ["Điều 122 Bộ luật Lao động 2019", "Điều 125 Bộ luật Lao động 2019"],
        "allow_abstention": False
    },

    # =========================================================================
    # D. TEMPORAL & VERSION-AWARE QUESTIONS (6 cases)
    # =========================================================================
    {
        "case_id": "GEN-TEM-01",
        "category": "TEMPORAL_VERSION",
        "dimension": "Thời điểm có hiệu lực Luật 36/2024",
        "difficulty": "EASY",
        "evidence_type": "SINGLE",
        "query": "Luật Trật tự, an toàn giao thông đường bộ số 36/2024/QH15 có hiệu lực thi hành từ ngày tháng năm nào?",
        "expected_answer": "Luật Trật tự, an toàn giao thông đường bộ 2024 có hiệu lực thi hành từ ngày 01 tháng 01 năm 2025 (riêng quy định tại khoản 3 Điều 10 có hiệu lực từ ngày 01 tháng 01 năm 2026).",
        "required_evidence": ["traffic_order_36_2024_qh15:88"],
        "expected_citations": ["Điều 88 Luật Trật tự, an toàn giao thông đường bộ 2024"],
        "allow_abstention": False
    },
    {
        "case_id": "GEN-TEM-02",
        "category": "TEMPORAL_VERSION",
        "dimension": "Chuyển tiếp thi sát hạch lái xe",
        "difficulty": "HARD",
        "evidence_type": "PRIMARY_PLUS_SUPPORTING",
        "query": "Người học lái xe ô tô thi sát hạch vào ngày 15/05/2026 có phải thi nội dung sát hạch lái xe mô phỏng trên máy tính không?",
        "expected_answer": "Có. Đối với các khóa học và kỳ thi sát hạch diễn ra trước ngày 01/07/2026, thí sinh vẫn phải thi nội dung sát hạch mô phỏng các tình huống giao thông trên máy tính theo quy định chuyển tiếp của Thông tư 12/2025/TT-BCA và Thông tư 108/2026/TT-BCA.",
        "required_evidence": ["traffic_driving_license_12_2025_tt_bca:14"],
        "expected_citations": ["Thông tư 12/2025/TT-BCA"],
        "allow_abstention": False
    },
    {
        "case_id": "GEN-TEM-03",
        "category": "TEMPORAL_VERSION",
        "dimension": "Hiệu lực quy định thiết bị an toàn cho trẻ em",
        "difficulty": "MEDIUM",
        "evidence_type": "SINGLE",
        "query": "Quy định bắt buộc người lái xe ô tô phải có thiết bị an toàn phù hợp khi chở trẻ em dưới 10 tuổi và chiều cao dưới 1,35m có hiệu lực từ ngày nào?",
        "expected_answer": "Quy định tại Khoản 3 Điều 10 về thiết bị an toàn cho trẻ em có hiệu lực thi hành từ ngày 01 tháng 01 năm 2026 (theo Khoản 2 Điều 88 Luật Trật tự, an toàn giao thông đường bộ 2024).",
        "required_evidence": ["traffic_order_36_2024_qh15:88"],
        "expected_citations": ["Khoản 2 Điều 88 Luật Trật tự, an toàn giao thông đường bộ 2024"],
        "allow_abstention": False
    },
    {
        "case_id": "GEN-TEM-04",
        "category": "TEMPORAL_VERSION",
        "dimension": "Phạt vi phạm trẻ em từ 15/08/2026",
        "difficulty": "HARD",
        "evidence_type": "SINGLE",
        "query": "Từ ngày 15/08/2026, hành vi chở trẻ em ngồi ghế trước không có thiết bị an toàn bị xử phạt theo văn bản pháp luật nào?",
        "expected_answer": "Hành vi này bị xử phạt theo Nghị định 168/2024/NĐ-CP (và văn bản sửa đổi bổ sung có hiệu lực từ năm 2026) quy định xử phạt vi phạm hành chính trong lĩnh vực trật tự, an toàn giao thông đường bộ.",
        "required_evidence": ["traffic_penalty_168_2024_nd_cp:6"],
        "expected_citations": ["Nghị định 168/2024/NĐ-CP"],
        "allow_abstention": False
    },
    {
        "case_id": "GEN-TEM-05",
        "category": "TEMPORAL_VERSION",
        "dimension": "Hiệu lực Nghị định 168/2024/NĐ-CP",
        "difficulty": "MEDIUM",
        "evidence_type": "SINGLE",
        "query": "Nghị định số 168/2024/NĐ-CP về xử phạt vi phạm hành chính trật tự, an toàn giao thông đường bộ có hiệu lực từ ngày nào và thay thế văn bản nào?",
        "expected_answer": "Nghị định 168/2024/NĐ-CP có hiệu lực từ ngày 01 tháng 01 năm 2025 và thay thế Nghị định số 100/2019/NĐ-CP và Nghị định 123/2021/NĐ-CP.",
        "required_evidence": ["traffic_penalty_168_2024_nd_cp:52"],
        "expected_citations": ["Điều 52 Nghị định 168/2024/NĐ-CP"],
        "allow_abstention": False
    },
    {
        "case_id": "GEN-TEM-06",
        "category": "TEMPORAL_VERSION",
        "dimension": "Thời hạn sử dụng Giấy phép lái xe",
        "difficulty": "MEDIUM",
        "evidence_type": "SINGLE",
        "query": "Giấy phép lái xe các hạng được cấp trước ngày Luật 36/2024 có hiệu lực thì có tiếp tục được sử dụng không?",
        "expected_answer": "Giấy phép lái xe đã được cấp trước ngày Luật này có hiệu lực tiếp tục được sử dụng theo thời hạn ghi trên giấy phép lái xe (theo Điều khoản chuyển tiếp Điều 89 Luật 36/2024/QH15).",
        "required_evidence": ["traffic_order_36_2024_qh15:89"],
        "expected_citations": ["Điều 89 Luật Trật tự, an toàn giao thông đường bộ 2024"],
        "allow_abstention": False
    },

    # =========================================================================
    # E. AMENDMENT & LINEAGE QUESTIONS (6 cases)
    # =========================================================================
    {
        "case_id": "GEN-AMD-01",
        "category": "AMENDMENT_LINEAGE",
        "dimension": "Văn bản sửa đổi Thông tư 12/2025",
        "difficulty": "MEDIUM",
        "evidence_type": "SINGLE",
        "query": "Văn bản nào đã sửa đổi, bổ sung Thông tư 12/2025/TT-BCA về đào tạo, sát hạch, cấp giấy phép lái xe?",
        "expected_answer": "Thông tư số 108/2026/TT-BCA là văn bản sửa đổi, bổ sung một số điều của Thông tư số 12/2025/TT-BCA của Bộ Công an.",
        "required_evidence": ["traffic_driving_license_108_2026_tt_bca:1"],
        "expected_citations": ["Thông tư 108/2026/TT-BCA"],
        "allow_abstention": False
    },
    {
        "case_id": "GEN-AMD-02",
        "category": "AMENDMENT_LINEAGE",
        "dimension": "Bãi bỏ Nghị định 100/2019",
        "difficulty": "EASY",
        "evidence_type": "SINGLE",
        "query": "Nghị định 100/2019/NĐ-CP về xử phạt vi phạm giao thông đường bộ đã bị thay thế hoàn toàn bởi văn bản nào?",
        "expected_answer": "Nghị định 100/2019/NĐ-CP (và Nghị định 123/2021/NĐ-CP sửa đổi) đã được thay thế hoàn toàn bởi Nghị định số 168/2024/NĐ-CP kể từ ngày 01/01/2025.",
        "required_evidence": ["traffic_penalty_168_2024_nd_cp:52"],
        "expected_citations": ["Nghị định 168/2024/NĐ-CP"],
        "allow_abstention": False
    },
    {
        "case_id": "GEN-AMD-03",
        "category": "AMENDMENT_LINEAGE",
        "dimension": "Văn bản thay thế Luật Giao thông đường bộ 2008",
        "difficulty": "EASY",
        "evidence_type": "SINGLE",
        "query": "Luật Giao thông đường bộ 2008 đã được tách ra và thay thế bởi hai đạo luật nào có hiệu lực từ năm 2025?",
        "expected_answer": "Luật Giao thông đường bộ 2008 được tách ra và thay thế bởi: 1. Luật Trật tự, an toàn giao thông đường bộ số 36/2024/QH15; 2. Luật Đường bộ số 35/2024/QH15.",
        "required_evidence": ["traffic_order_36_2024_qh15:88", "road_35_2024_qh15:85"],
        "expected_citations": ["Luật Trật tự, an toàn giao thông đường bộ 2024", "Luật Đường bộ 2024"],
        "allow_abstention": False
    },
    {
        "case_id": "GEN-AMD-04",
        "category": "AMENDMENT_LINEAGE",
        "dimension": "Sửa đổi quy định xe hợp đồng đón trả khách",
        "difficulty": "HARD",
        "evidence_type": "SINGLE",
        "query": "Nghị định nào sửa đổi, bổ sung Nghị định số 158/2024/NĐ-CP về điều kiện kinh doanh vận tải hành khách bằng xe ô tô?",
        "expected_answer": "Nghị định sửa đổi liên quan đến vận tải đường bộ theo chuỗi phả hệ quản lý hoạt động kinh doanh vận tải đường bộ thay thế hoặc bổ sung Nghị định 158/2024/NĐ-CP.",
        "required_evidence": ["traffic_transport_158_2024_nd_cp:1"],
        "expected_citations": ["Nghị định 158/2024/NĐ-CP"],
        "allow_abstention": False
    },
    {
        "case_id": "GEN-AMD-05",
        "category": "AMENDMENT_LINEAGE",
        "dimension": "Sửa đổi Bộ luật Lao động 2012",
        "difficulty": "EASY",
        "evidence_type": "SINGLE",
        "query": "Bộ luật Lao động năm 2012 đã hết hiệu lực và được thay thế bởi văn bản nào từ ngày 01/01/2021?",
        "expected_answer": "Bộ luật Lao động số 10/2012/QH13 đã hết hiệu lực và được thay thế bởi Bộ luật Lao động số 45/2019/QH14 kể từ ngày 01 tháng 01 năm 2021.",
        "required_evidence": ["bllđ_45_2019_qh14:219"],
        "expected_citations": ["Điều 219 Bộ luật Lao động 2019"],
        "allow_abstention": False
    },
    {
        "case_id": "GEN-AMD-06",
        "category": "AMENDMENT_LINEAGE",
        "dimension": "Hiệu lực thay thế Thông tư 24/2023 đăng ký xe",
        "difficulty": "MEDIUM",
        "evidence_type": "SINGLE",
        "query": "Thông tư số 24/2023/TT-BCA về đăng ký xe được thay thế bởi Thông tư nào từ ngày 01/01/2025?",
        "expected_answer": "Thông tư số 79/2024/TT-BCA của Bộ Công an ban hành quy định về cấp, thu hồi đăng ký, biển số xe cơ giới thay thế Thông tư 24/2023/TT-BCA từ ngày 01/01/2025.",
        "required_evidence": ["traffic_vehicle_registration_79_2024_tt_bca:40"],
        "expected_citations": ["Thông tư 79/2024/TT-BCA"],
        "allow_abstention": False
    },

    # =========================================================================
    # F. EXCEPTION & CONDITIONAL QUESTIONS (6 cases)
    # =========================================================================
    {
        "case_id": "GEN-EXC-01",
        "category": "EXCEPTION_CONDITIONAL",
        "dimension": "Quyền ưu tiên của xe ưu tiên",
        "difficulty": "MEDIUM",
        "evidence_type": "SINGLE",
        "query": "Xe chữa cháy đi làm nhiệm vụ khẩn cấp có bị hạn chế tốc độ không và có được đi vào đường ngược chiều không?",
        "expected_answer": "Xe chữa cháy đi làm nhiệm vụ khẩn cấp không bị hạn chế tốc độ; được phép đi vào đường ngược chiều, các đường khác có thể đi được và được đi khi có tín hiệu đèn đỏ, chỉ phải tuân theo chỉ dẫn của người điều khiển giao thông.",
        "required_evidence": ["traffic_order_36_2024_qh15:26"],
        "expected_citations": ["Điều 26 Luật Trật tự, an toàn giao thông đường bộ 2024"],
        "allow_abstention": False
    },
    {
        "case_id": "GEN-EXC-02",
        "category": "EXCEPTION_CONDITIONAL",
        "dimension": "Trường hợp không bị xử phạt vượt tốc độ",
        "difficulty": "HARD",
        "evidence_type": "SINGLE",
        "query": "Trường hợp người điều khiển xe chạy quá tốc độ quy định dưới 05 km/h thì có bị xử phạt tiền theo Nghị định 168/2024/NĐ-CP không?",
        "expected_answer": "Không bị xử phạt tiền. Theo Nghị định 168/2024/NĐ-CP, chế tài phạt tiền đối với hành vi chạy quá tốc độ chỉ bắt đầu áp dụng khi xe chạy quá tốc độ quy định từ 05 km/h trở lên.",
        "required_evidence": ["traffic_penalty_168_2024_nd_cp:6"],
        "expected_citations": ["Điều 6 Nghị định 168/2024/NĐ-CP"],
        "allow_abstention": False
    },
    {
        "case_id": "GEN-EXC-03",
        "category": "EXCEPTION_CONDITIONAL",
        "dimension": "Lùi xe trên đường cao tốc",
        "difficulty": "EASY",
        "evidence_type": "SINGLE",
        "query": "Người điều khiển phương tiện có được phép lùi xe trên đường cao tốc không?",
        "expected_answer": "Tuyệt đối không được lùi xe trên đường cao tốc (trừ các xe ưu tiên đang đi làm nhiệm vụ khẩn cấp theo quy định). Hành vi này bị nghiêm cấm và xử phạt rất nặng.",
        "required_evidence": ["traffic_order_36_2024_qh15:16", "traffic_order_36_2024_qh15:25"],
        "expected_citations": ["Điều 16 và Điều 25 Luật Trật tự, an toàn giao thông đường bộ 2024"],
        "allow_abstention": False
    },
    {
        "case_id": "GEN-EXC-04",
        "category": "EXCEPTION_CONDITIONAL",
        "dimension": "Ngoại lệ đơn phương chấm dứt không cần báo trước",
        "difficulty": "HARD",
        "evidence_type": "SINGLE",
        "query": "Người lao động có quyền đơn phương chấm dứt hợp đồng lao động mà KHÔNG CẦN BÁO TRƯỚC trong những trường hợp nào?",
        "expected_answer": "Theo Khoản 2 Điều 35 BLLĐ 2019, người lao động không cần báo trước khi: không được bố trí đúng công việc, địa điểm; không được trả đủ lương đúng hạn; bị ngược đãi, đánh đập, quấy rối tình dục; phụ nữ mang thai phải nghỉ việc theo chỉ định của cơ sở y tế; hoặc NSDLĐ cung cấp thông tin không trung thực.",
        "required_evidence": ["bllđ_45_2019_qh14:35"],
        "expected_citations": ["Khoản 2 Điều 35 Bộ luật Lao động 2019"],
        "allow_abstention": False
    },
    {
        "case_id": "GEN-EXC-05",
        "category": "EXCEPTION_CONDITIONAL",
        "dimension": "Ngoại lệ chuyển nhượng nhà ở xã hội",
        "difficulty": "HARD",
        "evidence_type": "SINGLE",
        "query": "Người mua nhà ở xã hội có được bán lại trong thời hạn 05 năm kể từ ngày thanh toán hết tiền mua không?",
        "expected_answer": "Trong thời hạn 05 năm kể từ ngày thanh toán hết tiền mua, bên mua không được bán lại cho người khác mà chỉ được bán lại cho chủ đầu tư dự án nhà ở xã hội hoặc đối tượng thuộc diện được mua nhà ở xã hội với giá bán tối đa bằng giá mua trong hợp đồng.",
        "required_evidence": ["housing_27_2023_qh15:89"],
        "expected_citations": ["Điều 89 Luật Nhà ở 2023"],
        "allow_abstention": False
    },
    {
        "case_id": "GEN-EXC-06",
        "category": "EXCEPTION_CONDITIONAL",
        "dimension": "Vượt xe bên phải",
        "difficulty": "MEDIUM",
        "evidence_type": "SINGLE",
        "query": "Khi tham gia giao thông, người lái xe có được phép vượt xe khác về phía bên phải không và trong trường hợp nào?",
        "expected_answer": "Khi vượt, các xe phải vượt về bên trái, trừ trường hợp được vượt bên phải khi: 1. Xe phía trước có tín hiệu rẽ trái hoặc đang rẽ trái; 2. Xe điện đang chạy giữa đường; 3. Xe chuyên dùng đang làm việc trên đường mà không thể vượt bên trái.",
        "required_evidence": ["traffic_order_36_2024_qh15:14"],
        "expected_citations": ["Khoản 4 Điều 14 Luật Trật tự, an toàn giao thông đường bộ 2024"],
        "allow_abstention": False
    },

    # =========================================================================
    # G. EXPLICIT CITATION DEMAND QUESTIONS (6 cases)
    # =========================================================================
    {
        "case_id": "GEN-CIT-01",
        "category": "CITATION_DEMAND",
        "dimension": "Căn cứ điều khoản chuyển hướng xe",
        "difficulty": "EASY",
        "evidence_type": "SINGLE",
        "query": "Điều nào của Luật Trật tự, an toàn giao thông đường bộ 2024 quy định về việc chuyển hướng xe?",
        "expected_answer": "Điều 15 Luật Trật tự, an toàn giao thông đường bộ 2024 quy định về chuyển hướng xe.",
        "required_evidence": ["traffic_order_36_2024_qh15:15"],
        "expected_citations": ["Điều 15 Luật Trật tự, an toàn giao thông đường bộ 2024"],
        "allow_abstention": False
    },
    {
        "case_id": "GEN-CIT-02",
        "category": "CITATION_DEMAND",
        "dimension": "Căn cứ điều khoản dừng xe, đỗ xe",
        "difficulty": "EASY",
        "evidence_type": "SINGLE",
        "query": "Quy định về dừng xe, đỗ xe trên đường bộ nằm ở Điều bao nhiêu của Luật Trật tự, an toàn giao thông đường bộ 2024?",
        "expected_answer": "Quy định về dừng xe, đỗ xe nằm ở Điều 18 Luật Trật tự, an toàn giao thông đường bộ 2024.",
        "required_evidence": ["traffic_order_36_2024_qh15:18"],
        "expected_citations": ["Điều 18 Luật Trật tự, an toàn giao thông đường bộ 2024"],
        "allow_abstention": False
    },
    {
        "case_id": "GEN-CIT-03",
        "category": "CITATION_DEMAND",
        "dimension": "Căn cứ điều khoản tốc độ ngoài khu dân cư",
        "difficulty": "MEDIUM",
        "evidence_type": "SINGLE",
        "query": "Điều nào của Thông tư 38/2024/TT-BGTVT quy định về tốc độ tối đa cho phép xe cơ giới tham gia giao thông ngoài khu vực đông dân cư?",
        "expected_answer": "Điều 7 Thông tư 38/2024/TT-BGTVT quy định về tốc độ tối đa cho phép xe cơ giới tham gia giao thông ngoài khu vực đông dân cư.",
        "required_evidence": ["traffic_speed_distance_38_2024_tt_bgtvt:7"],
        "expected_citations": ["Điều 7 Thông tư 38/2024/TT-BGTVT"],
        "allow_abstention": False
    },
    {
        "case_id": "GEN-CIT-04",
        "category": "CITATION_DEMAND",
        "dimension": "Căn cứ điều khoản xử phạt trừ điểm GPLX",
        "difficulty": "MEDIUM",
        "evidence_type": "SINGLE",
        "query": "Căn cứ theo Điều nào của Nghị định 168/2024/NĐ-CP quy định về các hành vi vi phạm trật tự an toàn giao thông bị trừ điểm Giấy phép lái xe?",
        "expected_answer": "Điều 32 (hoặc Điều 50 về nguyên tắc trừ điểm) của Nghị định 168/2024/NĐ-CP quy định chi tiết về các hành vi bị trừ điểm Giấy phép lái xe.",
        "required_evidence": ["traffic_penalty_168_2024_nd_cp:32", "traffic_penalty_168_2024_nd_cp:50"],
        "expected_citations": ["Điều 32 hoặc Điều 50 Nghị định 168/2024/NĐ-CP"],
        "allow_abstention": False
    },
    {
        "case_id": "GEN-CIT-05",
        "category": "CITATION_DEMAND",
        "dimension": "Căn cứ điều khoản tiền lương làm thêm giờ",
        "difficulty": "EASY",
        "evidence_type": "SINGLE",
        "query": "Điều nào của Bộ luật Lao động 2019 quy định về tiền lương làm thêm giờ, làm việc vào ban đêm của người lao động?",
        "expected_answer": "Điều 98 Bộ luật Lao động 2019 quy định về tiền lương làm thêm giờ, làm việc vào ban đêm.",
        "required_evidence": ["bllđ_45_2019_qh14:98"],
        "expected_citations": ["Điều 98 Bộ luật Lao động 2019"],
        "allow_abstention": False
    },
    {
        "case_id": "GEN-CIT-06",
        "category": "CITATION_DEMAND",
        "dimension": "Căn cứ điều khoản trợ cấp mất việc làm",
        "difficulty": "EASY",
        "evidence_type": "SINGLE",
        "query": "Quy định về trợ cấp mất việc làm được quy định tại Điều bao nhiêu của Bộ luật Lao động 2019?",
        "expected_answer": "Trợ cấp mất việc làm được quy định tại Điều 47 Bộ luật Lao động 2019.",
        "required_evidence": ["bllđ_45_2019_qh14:47"],
        "expected_citations": ["Điều 47 Bộ luật Lao động 2019"],
        "allow_abstention": False
    },

    # =========================================================================
    # H. AMBIGUOUS & INSUFFICIENT EVIDENCE QUESTIONS (6 cases)
    # =========================================================================
    {
        "case_id": "GEN-AMB-01",
        "category": "AMBIGUOUS_INSUFFICIENT",
        "dimension": "Hỏi chung chung về mức phạt giao thông",
        "difficulty": "MEDIUM",
        "evidence_type": "SINGLE",
        "query": "Tôi vượt đèn đỏ thì bị phạt bao nhiêu tiền?",
        "expected_answer": "Mức phạt phụ thuộc vào loại phương tiện điều khiển: Nếu điều khiển xe ô tô thì phạt từ 4.000.000 đến 6.000.000 đồng (Điều 6 NĐ 168); nếu điều khiển xe mô tô, xe gắn máy thì phạt từ 800.000 đến 1.000.000 đồng (Điều 7 NĐ 168).",
        "required_evidence": ["traffic_penalty_168_2024_nd_cp:6", "traffic_penalty_168_2024_nd_cp:7"],
        "expected_citations": ["Điều 6 hoặc Điều 7 Nghị định 168/2024/NĐ-CP"],
        "allow_abstention": False
    },
    {
        "case_id": "GEN-AMB-02",
        "category": "AMBIGUOUS_INSUFFICIENT",
        "dimension": "Hỏi tuổi nghỉ hưu không rõ giới tính",
        "difficulty": "MEDIUM",
        "evidence_type": "PRIMARY_PLUS_SUPPORTING",
        "query": "Người sinh năm 1972 thì bao nhiêu tuổi được nghỉ hưu?",
        "expected_answer": "Pháp luật phân biệt rõ theo giới tính: Đối với lao động nam sinh năm 1972, tuổi nghỉ hưu trong điều kiện bình thường là đủ 62 tuổi (vào năm 2034); đối với lao động nữ sinh năm 1972, tuổi nghỉ hưu là 58 tuổi 8 tháng hoặc 59 tuổi tùy tháng sinh theo Phụ lục I Nghị định 135/2020/NĐ-CP.",
        "required_evidence": ["nd_135_2020_nd_cp:4", "bllđ_45_2019_qh14:169"],
        "expected_citations": ["Điều 4 và Phụ lục I Nghị định 135/2020/NĐ-CP"],
        "allow_abstention": False
    },
    {
        "case_id": "GEN-AMB-03",
        "category": "AMBIGUOUS_INSUFFICIENT",
        "dimension": "Tốc độ xe chạy trong khu đông dân cư không rõ loại đường",
        "difficulty": "MEDIUM",
        "evidence_type": "SINGLE",
        "query": "Xe máy chạy trong khu vực đông dân cư được chạy tối đa bao nhiêu km/h?",
        "expected_answer": "Tốc độ tối đa phụ thuộc vào loại đường: Trên đường đôi hoặc đường một chiều có từ hai làn xe cơ giới trở lên, tốc độ tối đa là 60 km/h; trên đường hai chiều hoặc đường một chiều có một làn xe cơ giới, tốc độ tối đa là 50 km/h (Điều 6 Thông tư 38/2024/TT-BGTVT).",
        "required_evidence": ["traffic_speed_distance_38_2024_tt_bgtvt:6"],
        "expected_citations": ["Điều 6 Thông tư 38/2024/TT-BGTVT"],
        "allow_abstention": False
    },
    {
        "case_id": "GEN-AMB-04",
        "category": "AMBIGUOUS_INSUFFICIENT",
        "dimension": "Trợ cấp khi thôi việc không rõ nguyên nhân nghỉ",
        "difficulty": "MEDIUM",
        "evidence_type": "MULTI_VALID",
        "query": "Tôi nghỉ việc ở công ty thì được nhận tiền trợ cấp gì?",
        "expected_answer": "Tùy thuộc vào nguyên nhân chấm dứt hợp đồng lao động: Nếu chấm dứt hợp đồng theo Điều 34 (hết hạn, hai bên thỏa thuận, đơn phương đúng luật) thì được trợ cấp thôi việc (Điều 46 BLLĐ 2019); nếu mất việc do thay đổi cơ cấu, công nghệ, sáp nhập thì được nhận trợ cấp mất việc làm (Điều 47 BLLĐ 2019). Ngoài ra còn chế độ bảo hiểm thất nghiệp theo Luật Việc làm.",
        "required_evidence": ["bllđ_45_2019_qh14:46", "bllđ_45_2019_qh14:47"],
        "expected_citations": ["Điều 46 hoặc Điều 47 Bộ luật Lao động 2019"],
        "allow_abstention": False
    },
    {
        "case_id": "GEN-AMB-05",
        "category": "AMBIGUOUS_INSUFFICIENT",
        "dimension": "Phạt vi phạm nồng độ cồn không rõ mức cồn",
        "difficulty": "MEDIUM",
        "evidence_type": "SINGLE",
        "query": "Uống rượu bia lái xe ô tô bị phạt bao nhiêu tiền?",
        "expected_answer": "Mức phạt tiền đối với người lái xe ô tô vi phạm nồng độ cồn được chia thành 3 mức tùy thuộc vào hàm lượng cồn trong máu hoặc hơi thở: 1. Chưa vượt quá 50 mg/100 ml máu (hoặc 0.25 mg/1 lít khí thở): phạt 6-8 triệu; 2. Vượt quá 50-80 mg/100 ml máu (hoặc 0.25-0.4 mg/lít khí thở): phạt 16-18 triệu; 3. Vượt quá 80 mg/100 ml máu (hoặc 0.4 mg/lít khí thở): phạt 30-40 triệu đồng.",
        "required_evidence": ["traffic_penalty_168_2024_nd_cp:6"],
        "expected_citations": ["Điều 6 Nghị định 168/2024/NĐ-CP"],
        "allow_abstention": False
    },
    {
        "case_id": "GEN-AMB-06",
        "category": "AMBIGUOUS_INSUFFICIENT",
        "dimension": "Hồ sơ đăng ký xe máy không rõ xe mới hay sang tên",
        "difficulty": "MEDIUM",
        "evidence_type": "SINGLE",
        "query": "Thủ tục làm giấy tờ xe máy cần những gì theo quy định mới?",
        "expected_answer": "Cần phân định rõ đăng ký xe mới lần đầu hay sang tên chuyển quyền sở hữu theo Thông tư 79/2024/TT-BCA. Với đăng ký lần đầu cần giấy khai đăng ký xe, giấy tờ chủ xe, hóa đơn nguồn gốc và lệ phí trước bạ; với sang tên cần thêm chứng nhận thu hồi đăng ký biển số cũ và chứng từ chuyển quyền sở hữu.",
        "required_evidence": ["traffic_vehicle_registration_79_2024_tt_bca:8"],
        "expected_citations": ["Thông tư 79/2024/TT-BCA"],
        "allow_abstention": False
    },

    # =========================================================================
    # I. HARD CONFUSING & CONTRASTIVE QUESTIONS (6 cases)
    # =========================================================================
    {
        "case_id": "GEN-HRD-01",
        "category": "HARD_CONFUSING",
        "dimension": "Trừ điểm GPLX vs Tước quyền sử dụng GPLX",
        "difficulty": "HARD",
        "evidence_type": "MULTI_VALID",
        "query": "Phân biệt trường hợp bị trừ điểm Giấy phép lái xe với trường hợp bị tước quyền sử dụng Giấy phép lái xe theo quy định mới?",
        "expected_answer": "Trừ điểm GPLX (Điều 62 Luật 36/2024) là biện pháp quản lý hành chính, GPLX có 12 điểm và người lái xe vẫn được điều khiển phương tiện nếu chưa bị trừ hết điểm. Tước quyền sử dụng GPLX là hình thức xử phạt bổ sung theo Luật Xử lý VPHC, trong thời gian bị tước, cá nhân không được phép điều khiển phương tiện ghi trong giấy phép.",
        "required_evidence": ["traffic_order_36_2024_qh15:62", "traffic_penalty_168_2024_nd_cp:50"],
        "expected_citations": ["Điều 62 Luật Trật tự, an toàn giao thông đường bộ 2024", "Nghị định 168/2024/NĐ-CP"],
        "allow_abstention": False
    },
    {
        "case_id": "GEN-HRD-02",
        "category": "HARD_CONFUSING",
        "dimension": "Trợ cấp thôi việc vs Trợ cấp mất việc làm",
        "difficulty": "HARD",
        "evidence_type": "CO_REQUISITE",
        "query": "Khoản tiền trợ cấp thôi việc khác với trợ cấp mất việc làm ở những điểm mấu chốt nào theo Bộ luật Lao động 2019?",
        "expected_answer": "Khác nhau ở căn cứ áp dụng và mức chi trả: Trợ cấp thôi việc (Điều 46) áp dụng khi chấm dứt HĐLĐ bình thường, mức chi trả 1/2 tháng lương/năm làm việc. Trợ cấp mất việc làm (Điều 47) áp dụng khi chấm dứt do thay đổi cơ cấu, sáp nhập, chia tách, mức chi trả 01 tháng lương/năm làm việc nhưng ít nhất bằng 02 tháng tiền lương.",
        "required_evidence": ["bllđ_45_2019_qh14:46", "bllđ_45_2019_qh14:47"],
        "expected_citations": ["Điều 46 Bộ luật Lao động 2019", "Điều 47 Bộ luật Lao động 2019"],
        "allow_abstention": False
    },
    {
        "case_id": "GEN-HRD-03",
        "category": "HARD_CONFUSING",
        "dimension": "Phạt nhiều hành vi vi phạm và trừ điểm",
        "difficulty": "HARD",
        "evidence_type": "SINGLE",
        "query": "Nếu người lái xe vi phạm cùng lúc 2 lỗi bị phạt tiền và cả 2 lỗi đều thuộc diện bị trừ điểm GPLX thì việc trừ điểm và phạt tiền được áp dụng như thế nào?",
        "expected_answer": "Về phạt tiền: cộng dồn tiền phạt của từng hành vi để tính tổng mức phạt tiền. Về trừ điểm GPLX: theo Điểm b Khoản 1 Điều 50 Nghị định 168/2024/NĐ-CP, nếu có từ 02 hành vi vi phạm trở lên bị trừ điểm thì CHỈ ÁP DỤNG TRỪ ĐIỂM ĐỐI VỚI HÀNH VI VI PHẠM BỊ TRỪ NHIỀU ĐIỂM NHẤT (không cộng dồn điểm trừ).",
        "required_evidence": ["traffic_penalty_168_2024_nd_cp:50"],
        "expected_citations": ["Điểm b Khoản 1 Điều 50 Nghị định 168/2024/NĐ-CP"],
        "allow_abstention": False
    },
    {
        "case_id": "GEN-HRD-04",
        "category": "HARD_CONFUSING",
        "dimension": "Dừng xe vs Đỗ xe",
        "difficulty": "MEDIUM",
        "evidence_type": "SINGLE",
        "query": "Quy định của pháp luật phân biệt 'dừng xe' và 'đỗ xe' như thế nào theo Luật Trật tự an toàn giao thông đường bộ 2024?",
        "expected_answer": "Dừng xe là trạng thái đứng yên tạm thời của phương tiện trong một khoảng thời gian cần thiết đủ để cho người lên, xuống, xếp dỡ hàng hóa hoặc kiểm tra xe (người lái xe không được rời vị trí lái). Đỗ xe là trạng thái đứng yên của phương tiện không giới hạn thời gian (người lái xe có thể rời vị trí lái).",
        "required_evidence": ["traffic_order_36_2024_qh15:18"],
        "expected_citations": ["Điều 18 Luật Trật tự, an toàn giao thông đường bộ 2024"],
        "allow_abstention": False
    },
    {
        "case_id": "GEN-HRD-05",
        "category": "HARD_CONFUSING",
        "dimension": "Đơn phương chấm dứt HĐLĐ trái luật vs đúng luật",
        "difficulty": "HARD",
        "evidence_type": "SINGLE",
        "query": "Hậu quả pháp lý khi người lao động đơn phương chấm dứt hợp đồng lao động trái pháp luật theo Bộ luật Lao động 2019?",
        "expected_answer": "Theo Điều 40 BLLĐ 2019, người lao động đơn phương chấm dứt HĐLĐ trái pháp luật thì: 1. Không được trợ cấp thôi việc; 2. Phải bồi thường cho NSDLĐ nửa tháng tiền lương theo HĐLĐ và một khoản tiền tương ứng với tiền lương trong những ngày không báo trước; 3. Phải hoàn trả chi phí đào tạo nghề (nếu có).",
        "required_evidence": ["bllđ_45_2019_qh14:40"],
        "expected_citations": ["Điều 40 Bộ luật Lao động 2019"],
        "allow_abstention": False
    },
    {
        "case_id": "GEN-HRD-06",
        "category": "HARD_CONFUSING",
        "dimension": "Quyền thu hồi GPLX và phục hồi điểm",
        "difficulty": "HARD",
        "evidence_type": "MULTI_VALID",
        "query": "Khi Giấy phép lái xe bị trừ hết 12 điểm thì người lái xe có bị thu hồi giấy phép lái xe ngay không và làm sao để được phục hồi điểm?",
        "expected_answer": "Khi bị trừ hết 12 điểm, người lái xe không được điều khiển phương tiện tham gia giao thông. Sau ít nhất 06 tháng kể từ ngày bị trừ hết điểm, người lái xe phải tham gia kiểm tra kiến thức pháp luật về trật tự an toàn giao thông do CSGT tổ chức, nếu đạt kết quả thì được phục hồi đủ 12 điểm theo quy định tại Thông tư 65/2024/TT-BCA và Luật 36/2024/QH15.",
        "required_evidence": ["traffic_order_36_2024_qh15:62", "traffic_points_recovery_65_2024_tt_bca:5"],
        "expected_citations": ["Điều 62 Luật Trật tự, an toàn giao thông đường bộ 2024", "Thông tư 65/2024/TT-BCA"],
        "allow_abstention": False
    },

    # =========================================================================
    # J. "NO SUFFICIENT LEGAL BASIS" ABSTENTION & REFUSAL (6 cases)
    # =========================================================================
    {
        "case_id": "GEN-NOB-01",
        "category": "ABSTENTION_OUT_OF_CORPUS",
        "dimension": "Luật Hàng hải quốc tế",
        "difficulty": "MEDIUM",
        "evidence_type": "OUT_OF_CORPUS",
        "query": "Quy tắc phòng ngừa đâm va tàu thuyền trên biển (COLREGs) áp dụng vùng biển quốc tế quy định quyền ưu tiên của tàu buồm như thế nào?",
        "expected_answer": "Hiện tại cơ sở dữ liệu chưa có quy định trực tiếp về vấn đề này. Câu hỏi thuộc phạm vi Công ước Hàng hải quốc tế / Bộ luật Hàng hải Việt Nam ngoài phạm vi dữ liệu hiện hành.",
        "required_evidence": [],
        "expected_citations": [],
        "allow_abstention": True
    },
    {
        "case_id": "GEN-NOB-02",
        "category": "ABSTENTION_OUT_OF_CORPUS",
        "dimension": "Luật Hàng không dân dụng",
        "difficulty": "MEDIUM",
        "evidence_type": "OUT_OF_CORPUS",
        "query": "Theo Luật Hàng không dân dụng Việt Nam, hành khách mang hành lý xách tay quá cước trên chuyến bay quốc tế bị xử lý thế nào?",
        "expected_answer": "Hiện tại cơ sở dữ liệu chưa có quy định trực tiếp về vấn đề này. Câu hỏi thuộc phạm vi pháp luật hàng không dân dụng ngoài phạm vi dữ liệu hiện hành.",
        "required_evidence": [],
        "expected_citations": [],
        "allow_abstention": True
    },
    {
        "case_id": "GEN-NOB-03",
        "category": "ABSTENTION_OUT_OF_CORPUS",
        "dimension": "Luật Không gian vũ trụ",
        "difficulty": "HARD",
        "evidence_type": "OUT_OF_CORPUS",
        "query": "Căn cứ pháp lý nào tại Việt Nam quy định về quyền sở hữu khoáng sản khai thác từ mặt trăng và các thiên thể vũ trụ?",
        "expected_answer": "Hiện tại cơ sở dữ liệu pháp luật chưa có quy định về khai thác khoáng sản vũ trụ hay thiên thể ngoài không gian. Hệ thống từ chối bịa đặt căn cứ pháp lý.",
        "required_evidence": [],
        "expected_citations": [],
        "allow_abstention": True
    },
    {
        "case_id": "GEN-NOB-04",
        "category": "ABSTENTION_OUT_OF_CORPUS",
        "dimension": "Thuế vũ khí quân sự đặc biệt",
        "difficulty": "HARD",
        "evidence_type": "OUT_OF_CORPUS",
        "query": "Mức thuế suất thuế giá trị gia tăng áp dụng cho việc cá nhân tự nhập khẩu xe tăng chiến đấu và tàu ngầm quân sự là bao nhiêu?",
        "expected_answer": "Hiện tại cơ sở dữ liệu không có quy định cho phép cá nhân nhập khẩu vũ khí quân dụng như xe tăng hay tàu ngầm; đây là hàng hóa thuộc diện quản lý đặc biệt của quốc phòng an ninh và bị cấm nhập khẩu thương mại tự do.",
        "required_evidence": [],
        "expected_citations": [],
        "allow_abstention": True
    },
    {
        "case_id": "GEN-NOB-05",
        "category": "ABSTENTION_OUT_OF_CORPUS",
        "dimension": "Pháp luật ngoại hành tinh",
        "difficulty": "MEDIUM",
        "evidence_type": "OUT_OF_CORPUS",
        "query": "Thủ tục xin cấp thẻ căn cước và quốc tịch Việt Nam cho sinh vật ngoài hành tinh (Alien) cư trú tại Trái Đất được quy định ở Thông tư nào?",
        "expected_answer": "Hiện tại cơ sở dữ liệu pháp luật Việt Nam chưa có quy định về sinh vật ngoài hành tinh. Luật Căn cước và Luật Quốc tịch chỉ áp dụng cho công dân và con người.",
        "required_evidence": [],
        "expected_citations": [],
        "allow_abstention": True
    },
    {
        "case_id": "GEN-NOB-06",
        "category": "ABSTENTION_OUT_OF_CORPUS",
        "dimension": "Hợp đồng quỹ đạo vệ tinh viễn thông",
        "difficulty": "HARD",
        "evidence_type": "OUT_OF_CORPUS",
        "query": "Quy trình giải quyết tranh chấp quyền chiếm giữ vị trí quỹ đạo địa tĩnh không gian giữa hai tập đoàn viễn thông quốc tế được xử lý theo Điều nào của Bộ luật Dân sự?",
        "expected_answer": "Hiện tại cơ sở dữ liệu chưa có quy định trực tiếp về vấn đề tranh chấp vị trí quỹ đạo địa tĩnh trong không gian. Vấn đề này thuộc phạm vi điều chỉnh của Liên minh Viễn thông Quốc tế (ITU) và các điều ước quốc tế chuyên ngành.",
        "required_evidence": [],
        "expected_citations": [],
        "allow_abstention": True
    }
]

payload = {
    "dataset_name": "VietLegal AI - 60 Generation Quality Evaluation Test Cases",
    "version": "1.0.0",
    "total_cases": len(cases),
    "category_counts": {
        "DIRECT_FACTUAL": 6,
        "NUMERIC_CALCULATION": 6,
        "MULTI_EVIDENCE": 6,
        "TEMPORAL_VERSION": 6,
        "AMENDMENT_LINEAGE": 6,
        "EXCEPTION_CONDITIONAL": 6,
        "CITATION_DEMAND": 6,
        "AMBIGUOUS_INSUFFICIENT": 6,
        "HARD_CONFUSING": 6,
        "ABSTENTION_OUT_OF_CORPUS": 6
    },
    "cases": cases
}

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(payload, f, ensure_ascii=False, indent=2)

print(f"[+] Successfully generated {len(cases)} cases into {OUTPUT_FILE}")
