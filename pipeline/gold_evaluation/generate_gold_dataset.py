import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
import json
from pathlib import Path

OUT_FILE = Path("data/gold_evaluation/gold_retrieval_225_cases.json")
OUT_FILE.parent.mkdir(parents=True, exist_ok=True)

# 8 Categories:
# 1. DIRECT_RULE (30 cases)
# 2. ARTICLE_RETRIEVAL (30 cases)
# 3. CONDITIONAL_EXCEPTION (30 cases)
# 4. MULTI_DOCUMENT (30 cases)
# 5. TEMPORAL_QUERY (30 cases)
# 6. AMENDMENT_LINEAGE (30 cases)
# 7. TEMPORAL_CONTRAST (25 cases)
# 8. HARD_CONFUSING (20 cases)
# Total = 225 cases

def build_dataset():
    cases = []
    
    # -------------------------------------------------------------
    # 1. DIRECT_RULE (30 cases): Hỏi trực tiếp về một quy định
    # -------------------------------------------------------------
    direct_rules = [
        ("GOLD-DIR-01", "Người tham gia giao thông đường bộ phải đi bên nào theo quy định của Luật Trật tự an toàn giao thông đường bộ?",
         "traffic_order_36_2024_qh15", "36/2024/QH15", 10, "Khoản 1", "Đi bên phải theo chiều đi của mình, đúng làn đường, phần đường", "2025-01-01", "EASY"),
        ("GOLD-DIR-02", "Khi có người điều khiển giao thông thì người tham gia giao thông phải chấp hành hiệu lệnh của ai trước tiên?",
         "traffic_order_36_2024_qh15", "36/2024/QH15", 11, "Khoản 2", "Chấp hành hiệu lệnh của người điều khiển giao thông trước tiên", "2025-01-01", "EASY"),
        ("GOLD-DIR-03", "Người lái xe ô tô có được sử dụng điện thoại bằng tay khi xe đang chạy trên đường không?",
         "traffic_order_36_2024_qh15", "36/2024/QH15", 10, "Khoản 3", "Hành vi bị cấm khi điều khiển phương tiện", "2025-01-01", "EASY"),
        ("GOLD-DIR-04", "Tốc độ tối đa cho phép xe con chạy trong khu vực đông dân cư trên đường đôi là bao nhiêu km/h?",
         "traffic_speed_distance_38_2024_tt_bgtvt", "38/2024/TT-BGTVT", 6, "Khoản 1", "Tốc độ tối đa trong khu đông dân cư là 60 km/h", "2025-01-01", "MEDIUM"),
        ("GOLD-DIR-05", "Tốc độ tối đa cho phép xe máy chạy trong khu vực đông dân cư trên đường hai chiều không có dải phân cách giữa là bao nhiêu?",
         "traffic_speed_distance_38_2024_tt_bgtvt", "38/2024/TT-BGTVT", 6, "Khoản 2", "Tốc độ tối đa đường 2 chiều là 50 km/h", "2025-01-01", "MEDIUM"),
        ("GOLD-DIR-06", "Khi chạy xe với tốc độ 80 km/h trong điều kiện mặt đường khô ráo thì khoảng cách an toàn tối thiểu giữa hai xe là bao nhiêu mét?",
         "traffic_speed_distance_38_2024_tt_bgtvt", "38/2024/TT-BGTVT", 11, "Khoản 1", "Vận tốc từ trên 60 đến 80 km/h khoảng cách là 55m", "2025-01-01", "MEDIUM"),
        ("GOLD-DIR-07", "Người điều khiển xe mô tô hai bánh chở tối đa bao nhiêu người theo Luật TTATGTĐB 2024?",
         "traffic_order_36_2024_qh15", "36/2024/QH15", 30, "Khoản 1", "Chở 01 người, trừ trường hợp chở trẻ em, người bệnh, áp giải", "2025-01-01", "EASY"),
        ("GOLD-DIR-08", "Độ tuổi tối thiểu để được cấp Giấy phép lái xe hạng A1 theo Luật 36/2024/QH15 là bao nhiêu?",
         "traffic_order_36_2024_qh15", "36/2024/QH15", 59, "Khoản 1", "Đủ 18 tuổi trở lên", "2025-01-01", "EASY"),
        ("GOLD-DIR-09", "Thời hạn của Giấy phép lái xe ô tô hạng B theo Luật Trật tự, an toàn giao thông đường bộ là bao nhiêu năm?",
         "traffic_order_36_2024_qh15", "36/2024/QH15", 60, "Khoản 1", "GPLX hạng B có thời hạn 10 năm kể từ ngày cấp", "2025-01-01", "MEDIUM"),
        ("GOLD-DIR-10", "Mỗi giấy phép lái xe có tổng cộng bao nhiêu điểm trừ trong một năm theo Luật TTATGTĐB?",
         "traffic_order_36_2024_qh15", "36/2024/QH15", 62, "Khoản 1", "GPLX có 12 điểm", "2025-01-01", "EASY"),
        ("GOLD-DIR-11", "Niên hạn sử dụng của xe ô tô chở hàng (xe tải) tối đa là bao nhiêu năm?",
         "traffic_inspection_framework_89_2026_nd_cp", "89/2026/NĐ-CP", 3, "Khoản 1", "Niên hạn sử dụng ô tô chở hàng không quá 25 năm", "2026-07-01", "MEDIUM"),
        ("GOLD-DIR-12", "Niên hạn sử dụng của xe ô tô chở người từ 10 chỗ ngồi trở lên tối đa là bao nhiêu năm?",
         "traffic_inspection_framework_89_2026_nd_cp", "89/2026/NĐ-CP", 3, "Khoản 2", "Niên hạn sử dụng không quá 20 năm", "2026-07-01", "MEDIUM"),
        ("GOLD-DIR-13", "Biển số xe cơ giới được cấp và quản lý theo mã định danh của ai?",
         "traffic_order_36_2024_qh15", "36/2024/QH15", 39, "Khoản 1", "Quản lý theo mã định danh của chủ xe", "2025-01-01", "EASY"),
        ("GOLD-DIR-14", "Khi chuyển nhượng xe ô tô, chủ xe phải giữ lại chứng nhận đăng ký xe và biển số xe để làm gì?",
         "traffic_order_36_2024_qh15", "36/2024/QH15", 37, "Khoản 3", "Nộp lại cho cơ quan đăng ký để làm thủ tục thu hồi", "2025-01-01", "MEDIUM"),
        ("GOLD-DIR-15", "Cảnh sát giao thông khi tuần tra kiểm soát được dừng phương tiện trong những trường hợp nào?",
         "traffic_police_patrol_73_2024_tt_bca", "73/2024/TT-BCA", 12, "Khoản 1", "4 trường hợp CSGT được dừng phương tiện giao thông", "2025-01-01", "MEDIUM"),
        ("GOLD-DIR-16", "Người dân có thể xuất trình giấy tờ xe và GPLX qua ứng dụng nào khi CSGT kiểm tra?",
         "traffic_police_patrol_73_2024_tt_bca", "73/2024/TT-BCA", 13, "Khoản 2", "Kiểm tra thông tin giấy tờ tích hợp qua VNeID", "2025-01-01", "EASY"),
        ("GOLD-DIR-17", "Khi lùi xe trên đường, người lái xe phải quan sát phía nào và có tín hiệu gì?",
         "traffic_order_36_2024_qh15", "36/2024/QH15", 16, "Khoản 1", "Phải quan sát phía sau, có tín hiệu lùi và chỉ lùi khi an toàn", "2025-01-01", "EASY"),
        ("GOLD-DIR-18", "Trên đường cao tốc, người lái xe có được cho xe chạy ở làn dừng xe khẩn cấp không?",
         "traffic_order_36_2024_qh15", "36/2024/QH15", 26, "Khoản 3", "Không được cho xe chạy ở làn dừng xe khẩn cấp", "2025-01-01", "EASY"),
        ("GOLD-DIR-19", "Người điều khiển xe đạp có được buông cả hai tay khi đang đi xe không?",
         "traffic_order_36_2024_qh15", "36/2024/QH15", 31, "Khoản 3", "Hành vi bị cấm đối với người đi xe đạp", "2025-01-01", "EASY"),
        ("GOLD-DIR-20", "Khoảng cách an toàn tối thiểu khi chạy xe trên đường cao tốc với tốc độ trên 100 đến 120 km/h là bao nhiêu?",
         "traffic_speed_distance_38_2024_tt_bgtvt", "38/2024/TT-BGTVT", 11, "Khoản 1", "Khoảng cách an toàn tối thiểu là 100m", "2025-01-01", "MEDIUM"),
        ("GOLD-DIR-21", "Mức phạt tiền đối với người lái ô tô chạy quá tốc độ từ 05 đến dưới 10 km/h là bao nhiêu?",
         "traffic_penalty_168_2024_nd_cp", "168/2024/NĐ-CP", 5, "Khoản 2", "Phạt tiền từ 800.000 đến 1.000.000 đồng", "2025-01-01", "MEDIUM"),
        ("GOLD-DIR-22", "Mức phạt đối với người đi xe máy có nồng độ cồn vượt quá 80 miligam/100 mililít máu là bao nhiêu?",
         "traffic_penalty_168_2024_nd_cp", "168/2024/NĐ-CP", 6, "Khoản 8", "Phạt tiền từ 6.000.000 đến 8.000.000 đồng và trừ điểm GPLX", "2025-01-01", "MEDIUM"),
        ("GOLD-DIR-23", "Người điều khiển xe ô tô không chấp hành hiệu lệnh của đèn tín hiệu giao thông bị phạt bao nhiêu tiền?",
         "traffic_penalty_168_2024_nd_cp", "168/2024/NĐ-CP", 5, "Khoản 5", "Phạt tiền từ 4.000.000 đến 6.000.000 đồng", "2025-01-01", "MEDIUM"),
        ("GOLD-DIR-24", "Người đi bộ đi qua đường không đúng nơi quy định hoặc vượt qua dải phân cách bị xử phạt thế nào?",
         "traffic_penalty_168_2024_nd_cp", "168/2024/NĐ-CP", 9, "Khoản 1", "Phạt tiền từ 60.000 đến 100.000 đồng", "2025-01-01", "EASY"),
        ("GOLD-DIR-25", "Hành vi giao xe cho người không đủ điều kiện điều khiển phương tiện tham gia giao thông bị xử phạt theo điều nào?",
         "traffic_penalty_168_2024_nd_cp", "168/2024/NĐ-CP", 30, "Khoản 5", "Xử phạt chủ phương tiện giao xe cho người không đủ điều kiện", "2025-01-01", "HARD"),
        ("GOLD-DIR-26", "Xe ô tô mới chưa qua sử dụng có được miễn kiểm định an toàn kỹ thuật và bảo vệ môi trường lần đầu không?",
         "traffic_inspection_procedures_30_2026_tt_bxd", "30/2026/TT-BXD", 8, "Khoản 1", "Miễn kiểm định lần đầu cho xe mới xuất xưởng", "2026-07-01", "MEDIUM"),
        ("GOLD-DIR-27", "Việc lắp thêm phụ kiện như bậc lên xuống, giá nóc dưới 20cm có bị coi là cải tạo xe cơ giới không?",
         "traffic_inspection_procedures_30_2026_tt_bxd", "30/2026/TT-BXD", 12, "Khoản 2", "Không coi là cải tạo xe cơ giới", "2026-07-01", "MEDIUM"),
        ("GOLD-DIR-28", "Trục đơn của xe ô tô tải có 02 bánh xe chịu tải trọng tối đa cho phép là bao nhiêu tấn trên đường bộ?",
         "traffic_weight_limits_12_2025_tt_bxd", "12/2025/TT-BXD", 4, "Khoản 1", "Tải trọng trục đơn không vượt quá quy định kỹ thuật", "2025-07-01", "HARD"),
        ("GOLD-DIR-29", "Thứ tự hiệu lực giữa người điều khiển giao thông, đèn tín hiệu, biển báo hiệu và vạch kẻ đường được quy định thế nào?",
         "traffic_road_signs_qcvn41_51_2024_tt_bgtvt", "51/2024/TT-BGTVT", 4, "Mục 4", "Người ĐKGT -> Đèn tín hiệu -> Biển báo hiệu -> Vạch kẻ đường", "2025-01-01", "MEDIUM"),
        ("GOLD-DIR-30", "Vạch kẻ đường nét đứt màu vàng trên đường hai chiều có ý nghĩa gì theo QCVN 41:2024?",
         "traffic_road_signs_qcvn41_51_2024_tt_bgtvt", "51/2024/TT-BGTVT", 20, "Mục 20", "Phân chia hai chiều xe chạy ngược chiều, cho phép đè vạch khi cần thiết", "2025-01-01", "MEDIUM")
    ]
    for cid, q, doc_id, off, art, cl, note, aod, diff in direct_rules:
        cases.append({
            "test_case_id": cid,
            "category": "DIRECT_RULE",
            "query": q,
            "as_of_date": aod,
            "expected_evidence": {
                "document_id": doc_id,
                "official_number": off,
                "article": art,
                "clause": cl,
                "notes": note
            },
            "difficulty": diff
        })

    # -------------------------------------------------------------
    # 2. ARTICLE_RETRIEVAL (30 cases): Hỏi cần tìm đúng Điều luật cụ thể
    # -------------------------------------------------------------
    art_retrievals = [
        ("GOLD-ART-01", "Điều nào trong Luật Trật tự, an toàn giao thông đường bộ 2024 quy định về việc chuyển hướng xe?",
         "traffic_order_36_2024_qh15", "36/2024/QH15", 15, None, "Quy định về chuyển hướng xe", "2025-01-01", "EASY"),
        ("GOLD-ART-02", "Quy định về việc vượt xe và nhường đường cho xe xin vượt nằm ở Điều mấy của Luật 36/2024/QH15?",
         "traffic_order_36_2024_qh15", "36/2024/QH15", 14, None, "Quy định về vượt xe", "2025-01-01", "EASY"),
        ("GOLD-ART-03", "Điều bao nhiêu của Luật Trật tự, an toàn giao thông đường bộ quy định về dừng xe, đỗ xe trên đường?",
         "traffic_order_36_2024_qh15", "36/2024/QH15", 18, None, "Quy định về dừng xe, đỗ xe", "2025-01-01", "EASY"),
        ("GOLD-ART-04", "Điều nào của Luật 36/2024/QH15 quy định quy tắc giao thông đối với xe ưu tiên?",
         "traffic_order_36_2024_qh15", "36/2024/QH15", 27, None, "Quyền ưu tiên của một số loại xe", "2025-01-01", "EASY"),
        ("GOLD-ART-05", "Quy định về phân hạng giấy phép lái xe A1, A, B, C1, C, D nằm ở Điều nào trong Luật TTATGTĐB 2024?",
         "traffic_order_36_2024_qh15", "36/2024/QH15", 58, None, "Phân hạng Giấy phép lái xe", "2025-01-01", "EASY"),
        ("GOLD-ART-06", "Điều nào của Nghị định 168/2024/NĐ-CP quy định mức xử phạt người điều khiển xe mô tô, xe gắn máy vi phạm giao thông?",
         "traffic_penalty_168_2024_nd_cp", "168/2024/NĐ-CP", 6, None, "Xử phạt người điều khiển xe mô tô, xe gắn máy", "2025-01-01", "EASY"),
        ("GOLD-ART-07", "Điều nào của Nghị định 168/2024/NĐ-CP quy định xử phạt hành vi vi phạm quy định về biển số xe?",
         "traffic_penalty_168_2024_nd_cp", "168/2024/NĐ-CP", 13, None, "Xử phạt vi phạm quy định về biển số xe", "2025-01-01", "EASY"),
        ("GOLD-ART-08", "Quy định xử phạt người điểu khiển xe ô tô vi phạm quy tắc giao thông đường bộ nằm ở Điều nào của Nghị định 168?",
         "traffic_penalty_168_2024_nd_cp", "168/2024/NĐ-CP", 5, None, "Xử phạt người điều khiển ô tô", "2025-01-01", "EASY"),
        ("GOLD-ART-09", "Điều nào của Nghị định 168/2024/NĐ-CP quy định về các hành vi vi phạm bị trừ điểm giấy phép lái xe?",
         "traffic_penalty_168_2024_nd_cp", "168/2024/NĐ-CP", 32, None, "Quy định về trừ điểm giấy phép lái xe", "2025-01-01", "MEDIUM"),
        ("GOLD-ART-10", "Quy định thẩm quyền và thủ tục tạm giữ phương tiện, giấy tờ liên quan đến người điều khiển giao thông nằm ở Điều mấy NĐ 168?",
         "traffic_penalty_168_2024_nd_cp", "168/2024/NĐ-CP", 51, None, "Tạm giữ phương tiện, giấy tờ", "2025-01-01", "MEDIUM"),
        ("GOLD-ART-11", "Điều nào của Thông tư 38/2024/TT-BGTVT quy định về tốc độ tối đa cho phép xe cơ giới chạy ngoài khu vực đông dân cư?",
         "traffic_speed_distance_38_2024_tt_bgtvt", "38/2024/TT-BGTVT", 7, None, "Tốc độ tối đa ngoài khu đông dân cư", "2025-01-01", "EASY"),
        ("GOLD-ART-12", "Điều nào của Thông tư 38/2024/TT-BGTVT quy định khoảng cách an toàn giữa hai xe khi tham gia giao thông?",
         "traffic_speed_distance_38_2024_tt_bgtvt", "38/2024/TT-BGTVT", 11, None, "Khoảng cách an toàn giữa hai xe", "2025-01-01", "EASY"),
        ("GOLD-ART-13", "Quy định về cơ quan đăng ký xe ô tô, mô tô nằm ở Điều mấy của Thông tư 79/2024/TT-BCA?",
         "traffic_vehicle_registration_79_2024_tt_bca", "79/2024/TT-BCA", 4, None, "Cơ quan đăng ký xe", "2025-01-01", "MEDIUM"),
        ("GOLD-ART-14", "Hồ sơ đăng ký cấp biển số xe lần đầu được quy định tại Điều nào của Thông tư 79/2024/TT-BCA?",
         "traffic_vehicle_registration_79_2024_tt_bca", "79/2024/TT-BCA", 7, None, "Hồ sơ đăng ký xe lần đầu", "2025-01-01", "MEDIUM"),
        ("GOLD-ART-15", "Điều nào của Thông tư 79/2024/TT-BCA quy định về đăng ký sang tên, di chuyển xe cơ giới?",
         "traffic_vehicle_registration_79_2024_tt_bca", "79/2024/TT-BCA", 14, None, "Đăng ký sang tên, di chuyển xe", "2025-01-01", "MEDIUM"),
        ("GOLD-ART-16", "Quy định về nội dung sát hạch lái xe ô tô có bài thi mô phỏng tình huống giao thông nằm ở Điều mấy Thông tư 12/2025/TT-BCA?",
         "traffic_driving_license_12_2025_tt_bca", "12/2025/TT-BCA", 14, None, "Nội dung sát hạch lái xe ô tô", "2025-03-01", "MEDIUM"),
        ("GOLD-ART-17", "Điều nào của Thông tư 12/2025/TT-BCA quy định miễn sát hạch lý thuyết lái xe mô tô A1 cho người đã có bằng ô tô?",
         "traffic_driving_license_12_2025_tt_bca", "12/2025/TT-BCA", 12, None, "Miễn sát hạch lý thuyết A1", "2025-03-01", "MEDIUM"),
        ("GOLD-ART-18", "Điều nào của Thông tư 108/2026/TT-BCA quy định nội dung và quy trình sát hạch cấp giấy phép lái xe bãi bỏ thi mô phỏng?",
         "traffic_driving_license_108_2026_tt_bca", "108/2026/TT-BCA", 15, None, "Nội dung sát hạch cấp GPLX", "2026-07-01", "MEDIUM"),
        ("GOLD-ART-19", "Quy định về hồ sơ, thủ tục đổi, cấp lại giấy phép lái xe nằm ở Điều mấy Thông tư 108/2026/TT-BCA?",
         "traffic_driving_license_108_2026_tt_bca", "108/2026/TT-BCA", 22, None, "Thủ tục đổi, cấp lại GPLX", "2026-07-01", "MEDIUM"),
        ("GOLD-ART-20", "Điều nào của Thông tư 73/2024/TT-BCA quy định các trường hợp Cảnh sát giao thông được dừng phương tiện giao thông?",
         "traffic_police_patrol_73_2024_tt_bca", "73/2024/TT-BCA", 12, None, "Trường hợp được dừng phương tiện giao thông", "2025-01-01", "EASY"),
        ("GOLD-ART-21", "Quy định về kiểm tra, kiểm soát giấy tờ của người và phương tiện tham gia giao thông qua VNeID nằm ở Điều mấy Thông tư 73?",
         "traffic_police_patrol_73_2024_tt_bca", "73/2024/TT-BCA", 13, None, "Kiểm soát giấy tờ người tham gia giao thông", "2025-01-01", "MEDIUM"),
        ("GOLD-ART-22", "Điều nào của Thông tư 65/2024/TT-BCA quy định nội dung kiểm tra kiến thức pháp luật trật tự an toàn giao thông để phục hồi điểm GPLX?",
         "traffic_points_recovery_65_2024_tt_bca", "65/2024/TT-BCA", 6, None, "Nội dung kiểm tra kiến thức phục hồi điểm", "2025-01-01", "MEDIUM"),
        ("GOLD-ART-23", "Quy định về quy trình nộp hồ sơ phục hồi điểm giấy phép lái xe điện tử qua VNeID nằm ở Điều nào của Thông tư 105/2026/TT-BCA?",
         "traffic_points_recovery_105_2026_tt_bca", "105/2026/TT-BCA", 1, None, "Sửa đổi thủ tục phục hồi điểm qua VNeID", "2026-07-01", "MEDIUM"),
        ("GOLD-ART-24", "Điều nào của Nghị định 94/2026/NĐ-CP quy định điều kiện cơ sở vật chất của trung tâm sát hạch lái xe?",
         "traffic_driver_training_94_2026_nd_cp", "94/2026/NĐ-CP", 24, None, "Điều kiện cơ sở vật chất trung tâm sát hạch", "2026-07-01", "HARD"),
        ("GOLD-ART-25", "Điều nào của Nghị định 94/2026/NĐ-CP quy định thẩm quyền cấp, cấp lại và thu hồi giấy phép sát hạch lái xe?",
         "traffic_driver_training_94_2026_nd_cp", "94/2026/NĐ-CP", 26, None, "Giấy phép sát hạch lái xe và thẩm quyền cấp", "2026-07-01", "HARD"),
        ("GOLD-ART-26", "Điều nào của Nghị định 89/2026/NĐ-CP quy định về niên hạn sử dụng của xe ô tô cơ giới?",
         "traffic_inspection_framework_89_2026_nd_cp", "89/2026/NĐ-CP", 3, None, "Niên hạn sử dụng của ô tô", "2026-07-01", "MEDIUM"),
        ("GOLD-ART-27", "Quy định về chu kỳ kiểm định định kỳ đối với các loại xe cơ giới nằm ở Điều mấy của Thông tư 30/2026/TT-BXD?",
         "traffic_inspection_procedures_30_2026_tt_bxd", "30/2026/TT-BXD", 5, None, "Chu kỳ kiểm định xe cơ giới", "2026-07-01", "MEDIUM"),
        ("GOLD-ART-28", "Điều nào của Thông tư 12/2025/TT-BXD quy định về giới hạn tải trọng trục xe ô tô trên đường bộ?",
         "traffic_weight_limits_12_2025_tt_bxd", "12/2025/TT-BXD", 4, None, "Quy định tải trọng trục xe", "2025-07-01", "HARD"),
        ("GOLD-ART-29", "Điều nào của Nghị định 158/2024/NĐ-CP quy định điều kiện kinh doanh vận tải hành khách bằng xe ô tô theo hợp đồng?",
         "traffic_transport_158_2024_nd_cp", "158/2024/NĐ-CP", 7, None, "Kinh doanh vận tải hành khách theo hợp đồng", "2025-01-01", "MEDIUM"),
        ("GOLD-ART-30", "Điều nào của Nghị định 161/2024/NĐ-CP quy định trình tự cấp Giấy phép vận chuyển hàng hóa nguy hiểm?",
         "traffic_dangerous_goods_161_2024_nd_cp", "161/2024/NĐ-CP", 14, None, "Cấp Giấy phép vận chuyển hàng hóa nguy hiểm", "2025-01-01", "HARD")
    ]
    for cid, q, doc_id, off, art, cl, note, aod, diff in art_retrievals:
        cases.append({
            "test_case_id": cid,
            "category": "ARTICLE_RETRIEVAL",
            "query": q,
            "as_of_date": aod,
            "expected_evidence": {
                "document_id": doc_id,
                "official_number": off,
                "article": art,
                "clause": cl,
                "notes": note
            },
            "difficulty": diff
        })

    # -------------------------------------------------------------
    # 3. CONDITIONAL_EXCEPTION (30 cases): Câu hỏi có điều kiện / ngoại lệ
    # -------------------------------------------------------------
    cond_exceptions = [
        ("GOLD-EXC-01", "Trong trường hợp nào người lái xe ô tô được phép vượt xe khác về phía bên phải?",
         "traffic_order_36_2024_qh15", "36/2024/QH15", 14, "Khoản 4", "Trường hợp xe phía trước có tín hiệu rẽ trái hoặc đang rẽ trái; xe điện đang chạy giữa đường", "2025-01-01", "MEDIUM"),
        ("GOLD-EXC-02", "Khi nào xe cơ giới được phép lùi xe trên đường một chiều hoặc nơi có biển cấm đi ngược chiều?",
         "traffic_order_36_2024_qh15", "36/2024/QH15", 16, "Khoản 2", "Không được lùi xe ở khu vực cấm dừng, đường một chiều, trừ xe ưu tiên làm nhiệm vụ", "2025-01-01", "HARD"),
        ("GOLD-EXC-03", "Trường hợp nào người điều khiển xe mô tô hai bánh được phép chở tối đa 02 người?",
         "traffic_order_36_2024_qh15", "36/2024/QH15", 30, "Khoản 1", "Chở người bệnh đi cấp cứu, trẻ em dưới 14 tuổi, áp giải người phạm tội", "2025-01-01", "EASY"),
        ("GOLD-EXC-04", "Xe ưu tiên nào khi đi làm nhiệm vụ không bị hạn chế tốc độ và được phép đi vào đường ngược chiều?",
         "traffic_order_36_2024_qh15", "36/2024/QH15", 27, "Khoản 2", "Xe chữa cháy, xe quân sự, xe công an, xe cứu thương phát tín hiệu ưu tiên", "2025-01-01", "MEDIUM"),
        ("GOLD-EXC-05", "Trường hợp nào xe ô tô chạy trên cao tốc được phép dừng xe, đỗ xe trên làn dừng xe khẩn cấp?",
         "traffic_order_36_2024_qh15", "36/2024/QH15", 26, "Khoản 3", "Khi xe gặp sự cố kỹ thuật hoặc trường hợp bất khả kháng", "2025-01-01", "MEDIUM"),
        ("GOLD-EXC-06", "Người có Giấy phép lái xe ô tô hạng B2 có được miễn phần thi sát hạch lý thuyết khi thi lấy bằng xe máy A1 không?",
         "traffic_driving_license_12_2025_tt_bca", "12/2025/TT-BCA", 12, "Khoản 1", "Được miễn sát hạch lý thuyết theo Thông tư 12", "2025-03-01", "MEDIUM"),
        ("GOLD-EXC-07", "Trường hợp nào biển số định danh của xe máy không bị thu hồi khi chủ xe chuyển quyền sở hữu?",
         "traffic_order_36_2024_qh15", "36/2024/QH15", 37, "Khoản 4", "Biển số trúng đấu giá được chuyển quyền sở hữu kèm theo xe", "2025-01-01", "HARD"),
        ("GOLD-EXC-08", "Xe ô tô quá tải trọng có được lưu hành trên đường bộ khi có Giấy phép lưu hành đặc biệt không?",
         "traffic_weight_limits_12_2025_tt_bxd", "12/2025/TT-BXD", 8, "Khoản 2", "Được phép lưu hành khi có Giấy phép lưu hành xe quá tải, quá khổ", "2025-07-01", "HARD"),
        ("GOLD-EXC-09", "Trường hợp nào Cảnh sát giao thông được dừng phương tiện mà không cần có kế hoạch tuần tra công khai?",
         "traffic_police_patrol_73_2024_tt_bca", "73/2024/TT-BCA", 12, "Khoản 2", "Phát hiện hành vi vi phạm nghiêm trọng hoặc có tin báo tội phạm", "2025-01-01", "HARD"),
        ("GOLD-EXC-10", "Những trường hợp nào lắp đặt thêm thiết bị trên xe ô tô mà không phải thực hiện thủ tục nghiệm thu cải tạo?",
         "traffic_inspection_procedures_30_2026_tt_bxd", "30/2026/TT-BXD", 12, "Khoản 2", "Lắp nắp thùng xe bán tải, bậc lên xuống, giá nóc đúng quy chuẩn", "2026-07-01", "HARD"),
        ("GOLD-EXC-11", "Khi nào người lái xe ô tô được phép chạy quá tốc độ quy định mà không bị xử phạt vi phạm hành chính?",
         "traffic_penalty_168_2024_nd_cp", "168/2024/NĐ-CP", 5, "Khoản 2", "Chạy quá tốc độ dưới 05 km/h không thuộc khung phạt tiền", "2025-01-01", "MEDIUM"),
        ("GOLD-EXC-12", "Trường hợp nào Giấy phép lái xe bị trừ hết 12 điểm nhưng không phải thi lại toàn bộ?",
         "traffic_points_recovery_65_2024_tt_bca", "65/2024/TT-BCA", 6, "Khoản 1", "Chỉ cần kiểm tra lại kiến thức pháp luật trật tự an toàn giao thông", "2025-01-01", "MEDIUM"),
        ("GOLD-EXC-13", "Khi nào xe hợp đồng kinh doanh vận tải hành khách được phép đón trả khách ngoài bến xe?",
         "traffic_transport_158_2024_nd_cp", "158/2024/NĐ-CP", 7, "Khoản 3", "Đón trả khách tại các địa điểm ghi trong hợp đồng vận chuyển đã ký", "2025-01-01", "HARD"),
        ("GOLD-EXC-14", "Trường hợp xe chở hàng siêu trường siêu trọng thì tốc độ tối đa cho phép chạy trên đường bộ là bao nhiêu?",
         "traffic_speed_distance_38_2024_tt_bgtvt", "38/2024/TT-BGTVT", 8, "Khoản 1", "Tốc độ theo quy định trong Giấy phép lưu hành xe", "2025-01-01", "HARD"),
        ("GOLD-EXC-15", "Khi xảy ra sự cố trên cầu hoặc hầm đường bộ thì người lái xe phải xử lý tình huống như thế nào?",
         "traffic_order_36_2024_qh15", "36/2024/QH15", 26, "Khoản 4", "Không được quay đầu, lùi xe, phải bật đèn khẩn cấp và báo hiệu", "2025-01-01", "MEDIUM"),
        ("GOLD-EXC-16", "Trường hợp nào người điều khiển phương tiện được phép chuyển làn đường mà không cần bật xi nhan?",
         "traffic_order_36_2024_qh15", "36/2024/QH15", 13, "Khoản 2", "Luật bắt buộc phải có tín hiệu báo trước khi chuyển làn, không có ngoại lệ", "2025-01-01", "HARD"),
        ("GOLD-EXC-17", "Khi nào người lái xe ô tô được đi vào làn đường dành cho xe buýt nhanh BRT?",
         "traffic_road_signs_qcvn41_51_2024_tt_bgtvt", "51/2024/TT-BGTVT", 15, "Mục 15", "Chỉ khi có hiệu lệnh của người điều khiển giao thông", "2025-01-01", "MEDIUM"),
        ("GOLD-EXC-18", "Trường hợp nào chủ xe được giữ lại biển số định danh của mình quá thời hạn 05 năm kể từ ngày thu hồi?",
         "traffic_order_36_2024_qh15", "36/2024/QH15", 39, "Khoản 3", "Biển số định danh được giữ lại 05 năm, quá 5 năm không đăng ký xe mới thì chuyển vào kho số", "2025-01-01", "HARD"),
        ("GOLD-EXC-19", "Ngoại lệ nào cho phép xe gắn máy được phép đi vào đường cao tốc theo Luật TTATGTĐB?",
         "traffic_order_36_2024_qh15", "36/2024/QH15", 26, "Khoản 4", "Chỉ xe quản lý, bảo trì đường cao tốc mới được phép", "2025-01-01", "EASY"),
        ("GOLD-EXC-20", "Trường hợp nào cảnh sát giao thông được tạm giữ Giấy phép lái xe trên môi trường điện tử VNeID?",
         "traffic_police_patrol_73_2024_tt_bca", "73/2024/TT-BCA", 13, "Khoản 3", "Tạm giữ giấy tờ trên VNeID bằng cách khóa trạng thái sử dụng trên hệ thống", "2025-01-01", "HARD"),
        ("GOLD-EXC-21", "Người nước ngoài lái xe tại Việt Nam có bắt buộc phải đổi sang Giấy phép lái xe Việt Nam không?",
         "traffic_order_36_2024_qh15", "36/2024/QH15", 58, "Khoản 5", "Được dùng GPLX quốc tế phù hợp công ước hoặc phải làm thủ tục đổi tương đương", "2025-01-01", "MEDIUM"),
        ("GOLD-EXC-22", "Khi nào người ngồi trên xe mô tô hai bánh được phép không đội mũ bảo hiểm?",
         "traffic_order_36_2024_qh15", "36/2024/QH15", 30, "Khoản 2", "Chở người bệnh đi cấp cứu, trẻ em dưới 06 tuổi, áp giải người có hành vi vi phạm", "2025-01-01", "EASY"),
        ("GOLD-EXC-23", "Trường hợp xe tải chở hàng rời dễ rơi vãi thì điều kiện che chắn được quy định như thế nào?",
         "traffic_order_36_2024_qh15", "36/2024/QH15", 33, "Khoản 2", "Bắt buộc phải có bạt che đậy kín không để rơi vãi xuống đường", "2025-01-01", "EASY"),
        ("GOLD-EXC-24", "Khi có báo hiệu đường sắt giao nhau với đường bộ mà rào chắn đang đóng thì người tham gia giao thông phải dừng lại cách rào chắn bao nhiêu mét?",
         "traffic_order_36_2024_qh15", "36/2024/QH15", 25, "Khoản 1", "Phải dừng lại về phía phần đường của mình và cách rào chắn tối thiểu 5 mét", "2025-01-01", "MEDIUM"),
        ("GOLD-EXC-25", "Ngoại lệ nào đối với xe kinh doanh vận tải hành khách không cần lắp thiết bị giám sát hành trình?",
         "traffic_transport_158_2024_nd_cp", "158/2024/NĐ-CP", 7, "Khoản 2", "Toàn bộ xe ô tô kinh doanh vận tải đều bắt buộc phải lắp thiết bị GSHT", "2025-01-01", "HARD"),
        ("GOLD-EXC-26", "Trong trường hợp nào xe chở chất nổ, chất cháy được phép đi qua hầm đường bộ?",
         "traffic_dangerous_goods_161_2024_nd_cp", "161/2024/NĐ-CP", 14, "Khoản 3", "Phải có phương án an toàn và Giấy phép của cơ quan có thẩm quyền", "2025-01-01", "HARD"),
        ("GOLD-EXC-27", "Khi nào người điều khiển ô tô được phép đi vào đường có biển báo cấm xe ô tô?",
         "traffic_order_36_2024_qh15", "36/2024/QH15", 27, "Khoản 1", "Chỉ các loại xe ưu tiên đi làm nhiệm vụ khẩn cấp", "2025-01-01", "EASY"),
        ("GOLD-EXC-28", "Trường hợp người bị trừ hết điểm GPLX thì sau bao lâu được đăng ký kiểm tra kiến thức để phục hồi điểm?",
         "traffic_points_recovery_65_2024_tt_bca", "65/2024/TT-BCA", 6, "Khoản 2", "Sau thời hạn 06 tháng kể từ ngày bị trừ hết điểm", "2025-01-01", "MEDIUM"),
        ("GOLD-EXC-29", "Trường hợp nào phương tiện giao thông được đăng ký tạm thời với thời hạn sử dụng tối đa?",
         "traffic_vehicle_registration_79_2024_tt_bca", "79/2024/TT-BCA", 11, "Khoản 3", "Đăng ký tạm thời có giá trị trong vòng 15 ngày", "2025-01-01", "MEDIUM"),
        ("GOLD-EXC-30", "Khi nào xe tập lái của cơ sở đào tạo lái xe được phép tham gia giao thông trên đường?",
         "traffic_driver_training_94_2026_nd_cp", "94/2026/NĐ-CP", 8, "Khoản 2", "Có giáo viên bảo trợ tay lái, có biển tập lái và thiết bị DAT theo quy định", "2026-07-01", "HARD")
    ]
    for cid, q, doc_id, off, art, cl, note, aod, diff in cond_exceptions:
        cases.append({
            "test_case_id": cid,
            "category": "CONDITIONAL_EXCEPTION",
            "query": q,
            "as_of_date": aod,
            "expected_evidence": {
                "document_id": doc_id,
                "official_number": off,
                "article": art,
                "clause": cl,
                "notes": note
            },
            "difficulty": diff
        })

    # -------------------------------------------------------------
    # 4. MULTI_DOCUMENT (30 cases): Câu hỏi liên quan nhiều văn bản
    # -------------------------------------------------------------
    multi_docs = [
        ("GOLD-MUL-01", "Hành vi điều khiển xe ô tô chạy quá tốc độ quy định bị xử phạt như thế nào theo Nghị định 168 và quy định tốc độ tại Thông tư 38?",
         "traffic_penalty_168_2024_nd_cp", "168/2024/NĐ-CP", 5, "Khoản 3", "Xử phạt chạy quá tốc độ ô tô kết hợp quy chuẩn tốc độ TT 38", "2025-01-01", "MEDIUM"),
        ("GOLD-MUL-02", "Mức xử phạt người lái xe ô tô che dán biển số xe theo Nghị định 168 kết hợp sửa đổi bổ sung của Nghị định 238 là bao nhiêu?",
         "traffic_penalty_amendment_238_2026_nd_cp", "238/2026/NĐ-CP", 1, "Khoản 2", "Sửa Điều 13 NĐ 168 tăng mức phạt lên 20 - 26 triệu đồng", "2026-08-15", "HARD"),
        ("GOLD-MUL-03", "Quy định về cấp biển số định danh theo Luật 36 và thủ tục cấp thu hồi tại Thông tư 79 được thực hiện như thế nào?",
         "traffic_vehicle_registration_79_2024_tt_bca", "79/2024/TT-BCA", 4, None, "Thực hiện cấp biển định danh theo quy định Luật 36 và TT 79", "2025-01-01", "MEDIUM"),
        ("GOLD-MUL-04", "Quy trình đăng ký xe trên cổng dịch vụ công qua ứng dụng VNeID theo Thông tư 79 và sửa đổi bởi Thông tư 13 gồm các bước nào?",
         "traffic_amendment_13_2025_tt_bca", "13/2025/TT-BCA", 1, None, "Đăng ký xe toàn trình trên VNeID sửa đổi TT 79", "2025-03-01", "HARD"),
        ("GOLD-MUL-05", "Điều kiện phục hồi điểm GPLX theo Luật 36 và nội dung bài kiểm tra kiến thức theo Thông tư 65 gồm những gì?",
         "traffic_points_recovery_65_2024_tt_bca", "65/2024/TT-BCA", 6, None, "Kiểm tra kiến thức pháp luật để phục hồi 12 điểm GPLX", "2025-01-01", "MEDIUM"),
        ("GOLD-MUL-06", "Thủ tục nộp hồ sơ phục hồi điểm giấy phép lái xe trực tuyến trên VNeID theo Thông tư 105 sửa đổi Thông tư 65 ra sao?",
         "traffic_points_recovery_105_2026_tt_bca", "105/2026/TT-BCA", 1, None, "Sửa đổi Điều 9 Thông tư 65 về nộp hồ sơ điện tử", "2026-07-01", "HARD"),
        ("GOLD-MUL-07", "Điều kiện trung tâm sát hạch lái xe theo Nghị định 94 và quy chuẩn bài thi sát hạch thực hành theo Thông tư 108 gồm những gì?",
         "traffic_driver_training_94_2026_nd_cp", "94/2026/NĐ-CP", 24, None, "Tiêu chuẩn cơ sở vật chất trung tâm sát hạch và nội dung sát hạch", "2026-07-01", "HARD"),
        ("GOLD-MUL-08", "Quy định về tải trọng trục xe theo Thông tư 12/2025/TT-BXD và nội dung sửa đổi tại Thông tư 19/2026/TT-BXD đối với xe trục bóng hơi?",
         "traffic_weight_amendment_19_2026_tt_bxd", "19/2026/TT-BXD", 1, None, "Sửa đổi tải trọng trục trang bị hệ thống treo khí nén", "2026-07-01", "HARD"),
        ("GOLD-MUL-09", "Căn cứ pháp lý nào quy định niên hạn sử dụng ô tô theo Nghị định 89 và thủ tục kiểm định định kỳ theo Thông tư 30?",
         "traffic_inspection_framework_89_2026_nd_cp", "89/2026/NĐ-CP", 3, None, "Niên hạn ô tô và đăng kiểm an toàn kỹ thuật", "2026-07-01", "MEDIUM"),
        ("GOLD-MUL-10", "Việc kiểm tra giấy tờ phương tiện qua ứng dụng VNeID căn cứ theo Thông tư 73 và hướng dẫn tại Nghị định 151 như thế nào?",
         "traffic_police_patrol_73_2024_tt_bca", "73/2024/TT-BCA", 13, None, "Kiểm soát giấy tờ điện tử liên thông CSDL quốc gia", "2025-01-01", "MEDIUM"),
        ("GOLD-MUL-11", "Quy định xử phạt xe chở hàng quá tải trọng theo Nghị định 168 dựa trên giới hạn tải trọng cầu đường tại Thông tư 12/2025?",
         "traffic_penalty_168_2024_nd_cp", "168/2024/NĐ-CP", 24, None, "Xử phạt xe ô tô tải chở hàng vượt quá tải trọng cho phép", "2025-07-01", "HARD"),
        ("GOLD-MUL-12", "Cơ chế trừ điểm GPLX theo Điều 62 Luật 36 và danh mục hành vi bị trừ điểm chi tiết tại Điều 32 Nghị định 168?",
         "traffic_penalty_168_2024_nd_cp", "168/2024/NĐ-CP", 32, None, "Cụ thể hóa các lỗi bị trừ 2, 3, 4, 6, 12 điểm GPLX", "2025-01-01", "MEDIUM"),
        ("GOLD-MUL-13", "Quy định về phân loại biển số xe trúng đấu giá theo Luật 36 và hướng dẫn thủ tục đăng ký tại Thông tư 51/2025?",
         "traffic_amendment_51_2025_tt_bca", "51/2025/TT-BCA", 1, None, "Đăng ký xe trúng đấu giá linh hoạt sửa đổi TT 79", "2025-07-01", "HARD"),
        ("GOLD-MUL-14", "Quy định về quản lý kết cấu hạ tầng giao thông đường bộ theo Nghị định 165 và nội dung sửa đổi tại Nghị định 241?",
         "traffic_road_infra_amendment_241_2026_nd_cp", "241/2026/NĐ-CP", 1, None, "Sửa đổi quy định quản lý, bảo trì và chia sẻ dữ liệu ITS", "2026-07-01", "HARD"),
        ("GOLD-MUL-15", "Hành vi đón trả khách tại văn phòng đại diện của xe hợp đồng bị cấm theo Nghị định 218 sửa đổi Nghị định 158 và xử phạt thế nào theo NĐ 168?",
         "traffic_amendment_218_2026_nd_cp", "218/2026/NĐ-CP", 1, None, "Quy định cấm lập bến cóc, đón trả khách tại văn phòng đại diện", "2026-08-10", "HARD"),
        ("GOLD-MUL-16", "Quy trình vận chuyển hàng siêu trường siêu trọng theo Luật Đường bộ và điều kiện cấp phép lưu hành theo Thông tư 12/2025?",
         "traffic_weight_limits_12_2025_tt_bxd", "12/2025/TT-BXD", 8, None, "Điều kiện và thủ tục cấp phép xe quá khổ, quá tải", "2025-07-01", "HARD"),
        ("GOLD-MUL-17", "Quy định phân hạng bằng lái xe theo Luật 36 và tiêu chuẩn đào tạo lái xe từng hạng theo Nghị định 94/2026?",
         "traffic_driver_training_94_2026_nd_cp", "94/2026/NĐ-CP", 8, None, "Tiêu chuẩn cơ sở đào tạo và phân hạng đào tạo lái xe", "2026-07-01", "HARD"),
        ("GOLD-MUL-18", "Quy định về hệ thống biển báo hiệu đường bộ theo QCVN 41:2024 và mức phạt tiền khi không chấp hành theo Nghị định 168?",
         "traffic_penalty_168_2024_nd_cp", "168/2024/NĐ-CP", 5, "Khoản 1", "Xử phạt hành vi không chấp hành hiệu lệnh biển báo, vạch kẻ đường", "2025-01-01", "MEDIUM"),
        ("GOLD-MUL-19", "Quy định về việc miễn thi lý thuyết bằng lái xe mô tô A1 theo Thông tư 12 và Thông tư 108?",
         "traffic_driving_license_108_2026_tt_bca", "108/2026/TT-BCA", 15, None, "Miễn sát hạch lý thuyết A1 kế thừa từ TT 12", "2026-07-01", "MEDIUM"),
        ("GOLD-MUL-20", "Quy định xe cứu thương được quyền ưu tiên theo Luật 36 và thủ tục cấp giấy phép ưu tiên liên thông theo Nghị định 151?",
         "traffic_guideline_151_2024_nd_cp", "151/2024/NĐ-CP", 10, None, "Thủ tục cấp phép sử dụng thiết bị phát tín hiệu xe ưu tiên", "2025-01-01", "MEDIUM"),
        ("GOLD-MUL-21", "Quy định kiểm định an toàn kỹ thuật xe chuyên dùng theo Thông tư 30 và sửa đổi bổ sung bởi Thông tư 45?",
         "traffic_inspection_amendment_45_2026_tt_bxd", "45/2026/TT-BXD", 1, None, "Sửa đổi chu kỳ và quy trình kiểm định xe cơ giới chuyên dùng", "2026-07-01", "HARD"),
        ("GOLD-MUL-22", "Hành vi sử dụng nồng độ cồn khi lái xe bị cấm tuyệt đối theo Luật 36 và mức xử phạt kịch khung theo Nghị định 168?",
         "traffic_penalty_168_2024_nd_cp", "168/2024/NĐ-CP", 5, "Khoản 10", "Phạt tiền 30 - 40 triệu đồng đối với ô tô có nồng độ cồn vượt quá 80mg/100ml máu", "2025-01-01", "MEDIUM"),
        ("GOLD-MUL-23", "Quy định về điều kiện thu hồi giấy phép kinh doanh vận tải theo Nghị định 158 và sửa đổi tại Nghị định 218?",
         "traffic_amendment_218_2026_nd_cp", "218/2026/NĐ-CP", 1, None, "Các trường hợp thu hồi GPKD vận tải ô tô không thời hạn", "2026-08-10", "HARD"),
        ("GOLD-MUL-24", "Quy định về thu phí sử dụng đường bộ cao tốc theo Nghị định 130 và các trường hợp được miễn giảm phí?",
         "traffic_toll_130_2024_nd_cp", "130/2024/NĐ-CP", 4, None, "Đối tượng chịu phí và miễn thu phí sử dụng đường bộ cao tốc", "2024-10-10", "HARD"),
        ("GOLD-MUL-25", "Hành vi vận chuyển hàng hóa nguy hiểm không có giấy phép theo Nghị định 161 bị xử phạt như thế nào theo Nghị định 168?",
         "traffic_penalty_168_2024_nd_cp", "168/2024/NĐ-CP", 24, None, "Xử phạt vi phạm quy định về vận chuyển hàng hóa nguy hiểm", "2025-01-01", "HARD"),
        ("GOLD-MUL-26", "Quy chuẩn kỹ thuật cabin học lái xe ô tô theo Nghị định 94 và chương trình đào tạo lái xe?",
         "traffic_driver_training_94_2026_nd_cp", "94/2026/NĐ-CP", 9, None, "Tiêu chuẩn cabin điện tử tập lái xe ô tô", "2026-07-01", "HARD"),
        ("GOLD-MUL-27", "Quy định về vạch mắt võng theo QCVN 41:2024 và mức phạt khi dừng xe trên vạch mắt võng theo Nghị định 168?",
         "traffic_penalty_168_2024_nd_cp", "168/2024/NĐ-CP", 5, "Khoản 1", "Xử phạt không chấp hành vạch kẻ đường mắt võng", "2025-01-01", "MEDIUM"),
        ("GOLD-MUL-28", "Quy định cấp lại Giấy chứng nhận đăng ký xe khi bị mất theo Thông tư 79 và thủ tục xác thực danh tính chủ xe?",
         "traffic_vehicle_registration_79_2024_tt_bca", "79/2024/TT-BCA", 16, None, "Cấp lại giấy chứng nhận đăng ký xe, biển số xe", "2025-01-01", "MEDIUM"),
        ("GOLD-MUL-29", "Quy định xử phạt ô tô chở trẻ em dưới 10 tuổi ngồi ghế trước không có thiết bị an toàn theo Luật 36 và Nghị định 238?",
         "traffic_penalty_amendment_238_2026_nd_cp", "238/2026/NĐ-CP", 1, "Khoản 3", "Bổ sung mức xử phạt hành vi chở trẻ em không có thiết bị an toàn", "2026-08-15", "HARD"),
        ("GOLD-MUL-30", "Quy định phân hạng xe ô tô chở người từ 8 chỗ đến 16 chỗ theo Luật 36 và điều kiện cấp GPLX hạng D2?",
         "traffic_order_36_2024_qh15", "36/2024/QH15", 58, "Khoản 1", "Phân hạng GPLX D2 cấp cho người lái ô tô chở người từ 8 đến 16 chỗ", "2025-01-01", "MEDIUM")
    ]
    for cid, q, doc_id, off, art, cl, note, aod, diff in multi_docs:
        cases.append({
            "test_case_id": cid,
            "category": "MULTI_DOCUMENT",
            "query": q,
            "as_of_date": aod,
            "expected_evidence": {
                "document_id": doc_id,
                "official_number": off,
                "article": art,
                "clause": cl,
                "notes": note
            },
            "difficulty": diff
        })

    # -------------------------------------------------------------
    # 5. TEMPORAL_QUERY (30 cases): Câu hỏi theo thời điểm cụ thể
    # -------------------------------------------------------------
    temporal_queries = [
        ("GOLD-TEM-01", "Vào ngày 15/05/2025, người đi thi sát hạch lái xe ô tô hạng B2 phải thi những bài sát hạch nào?",
         "traffic_driving_license_12_2025_tt_bca", "12/2025/TT-BCA", 14, "Khoản 1", "Áp dụng Thông tư 12 có bài thi mô phỏng", "2025-05-15", "MEDIUM"),
        ("GOLD-TEM-02", "Ngày 15/08/2026, thí sinh sát hạch bằng lái xe ô tô có còn phải thi bài mô phỏng tình huống giao thông không?",
         "traffic_driving_license_108_2026_tt_bca", "108/2026/TT-BCA", 15, "Khoản 1", "Áp dụng Thông tư 108 bãi bỏ bài thi mô phỏng", "2026-08-15", "MEDIUM"),
        ("GOLD-TEM-03", "Vào ngày 01/02/2025, việc phân hạng giấy phép lái xe được áp dụng theo Luật nào?",
         "traffic_order_36_2024_qh15", "36/2024/QH15", 58, None, "Luật 36/2024/QH15 có hiệu lực từ 01/01/2025", "2025-02-01", "EASY"),
        ("GOLD-TEM-04", "Tính đến ngày 20/07/2026, hồ sơ đề nghị phục hồi điểm giấy phép lái xe có thể nộp trực tuyến qua đâu?",
         "traffic_points_recovery_105_2026_tt_bca", "105/2026/TT-BCA", 1, None, "Áp dụng Thông tư 105 nộp hồ sơ qua VNeID", "2026-07-20", "MEDIUM"),
        ("GOLD-TEM-05", "Ngày 05/08/2026, xe khách hợp đồng có được phép đón trả khách tại văn phòng đại diện không?",
         "traffic_transport_158_2024_nd_cp", "158/2024/NĐ-CP", 7, None, "Trước 10/08/2026 áp dụng bản gốc NĐ 158", "2026-08-05", "HARD"),
        ("GOLD-TEM-06", "Vào ngày 15/08/2026, hành vi đón trả khách tại văn phòng đại diện của xe ô tô kinh doanh vận tải theo hợp đồng bị cấm theo văn bản nào?",
         "traffic_amendment_218_2026_nd_cp", "218/2026/NĐ-CP", 1, None, "NĐ 218/2026 có hiệu lực từ 10/08/2026 cấm tuyệt đối", "2026-08-15", "HARD"),
        ("GOLD-TEM-07", "Vào ngày 10/07/2026, hành vi dán che biển số xe ô tô bị xử phạt bao nhiêu tiền?",
         "traffic_penalty_168_2024_nd_cp", "168/2024/NĐ-CP", 13, "Khoản 8", "Trước 15/08/2026 phạt theo NĐ 168 bản gốc (4 - 6 triệu)", "2026-07-10", "HARD"),
        ("GOLD-TEM-08", "Vào ngày 20/08/2026, hành vi sử dụng biển số bị bẻ cong, che lấp đối với xe ô tô bị phạt bao nhiêu tiền theo NĐ 238?",
         "traffic_penalty_amendment_238_2026_nd_cp", "238/2026/NĐ-CP", 1, "Khoản 2", "Từ 15/08/2026 NĐ 238 tăng mức phạt lên 20 - 26 triệu đồng", "2026-08-20", "HARD"),
        ("GOLD-TEM-09", "Vào ngày 10/05/2025, người dân đăng ký xe máy tại xã nơi thường trú theo quy định nào?",
         "traffic_vehicle_registration_79_2024_tt_bca", "79/2024/TT-BCA", 4, None, "Áp dụng Thông tư 79 trước khi có TT 51/2025", "2025-05-10", "MEDIUM"),
        ("GOLD-TEM-10", "Vào ngày 15/08/2025, người dân có thể đăng ký xe mô tô tại bất kỳ Công an xã nào trong cùng tỉnh theo quy định nào?",
         "traffic_amendment_51_2025_tt_bca", "51/2025/TT-BCA", 1, None, "Thông tư 51/2025 có hiệu lực từ 01/07/2025 cho phép đăng ký linh hoạt", "2025-08-15", "HARD"),
        ("GOLD-TEM-11", "Vào ngày 20/01/2025, CSGT có quyền dừng phương tiện để kiểm tra những loại giấy tờ gì qua VNeID?",
         "traffic_police_patrol_73_2024_tt_bca", "73/2024/TT-BCA", 13, "Khoản 2", "TT 73/2024 có hiệu lực từ 01/01/2025", "2025-01-20", "MEDIUM"),
        ("GOLD-TEM-12", "Vào ngày 01/06/2025, cơ quan nào có thẩm quyền cấp giấy phép vận chuyển hàng hóa nguy hiểm loại chất nổ?",
         "traffic_dangerous_goods_161_2024_nd_cp", "161/2024/NĐ-CP", 14, "Khoản 1", "Trước 01/07/2025 áp dụng NĐ 161 bản gốc Điều 14 v1", "2025-06-01", "HARD"),
        ("GOLD-TEM-13", "Vào ngày 05/07/2025, thẩm quyền cấp giấy phép vận chuyển hàng nguy hiểm được sửa đổi theo văn bản nào?",
         "traffic_points_recovery_105_2026_tt_bca", "105/2026/TT-BCA", 1, None, "Áp dụng sửa đổi có hiệu lực từ 01/07/2025", "2025-07-05", "HARD"),
        ("GOLD-TEM-14", "Vào ngày 15/07/2026, cơ sở đào tạo lái xe ô tô có bắt buộc phải trang bị thiết bị giám sát thời gian và quãng đường học DAT không?",
         "traffic_driver_training_94_2026_nd_cp", "94/2026/NĐ-CP", 8, "Khoản 2", "NĐ 94/2026 có hiệu lực từ 01/07/2026 quy định bắt buộc thiết bị DAT", "2026-07-15", "HARD"),
        ("GOLD-TEM-15", "Vào ngày 01/08/2026, xe ô tô tải có niên hạn sử dụng quá 25 năm có được phép lưu hành không?",
         "traffic_inspection_framework_89_2026_nd_cp", "89/2026/NĐ-CP", 3, "Khoản 1", "NĐ 89/2026 hiệu lực từ 01/07/2026 cấm lưu hành xe hết niên hạn", "2026-08-01", "MEDIUM"),
        ("GOLD-TEM-16", "Vào ngày 10/08/2026, trạm đăng kiểm thực hiện kiểm định xe cơ giới theo quy trình của Thông tư nào?",
         "traffic_inspection_procedures_30_2026_tt_bxd", "30/2026/TT-BXD", 5, None, "Thông tư 30/2026 có hiệu lực từ 01/07/2026", "2026-08-10", "MEDIUM"),
        ("GOLD-TEM-17", "Vào ngày 20/07/2026, camera AI giám sát dây chuyền kiểm định xe cơ giới được áp dụng theo Thông tư nào?",
         "traffic_inspection_amendment_45_2026_tt_bxd", "45/2026/TT-BXD", 1, None, "Thông tư 45/2026 sửa đổi bổ sung TT 30", "2026-07-20", "HARD"),
        ("GOLD-TEM-18", "Vào ngày 15/03/2025, người mua xe cũ nộp hồ sơ đăng ký sang tên xe trực tuyến toàn trình theo Thông tư nào?",
         "traffic_amendment_13_2025_tt_bca", "13/2025/TT-BCA", 1, None, "Thông tư 13/2025 có hiệu lực từ 01/03/2025", "2025-03-15", "HARD"),
        ("GOLD-TEM-19", "Vào ngày 01/07/2026, tải trọng trục xe ô tô trang bị hệ thống treo khí nén được áp dụng theo Thông tư nào?",
         "traffic_weight_amendment_19_2026_tt_bxd", "19/2026/TT-BXD", 1, None, "Thông tư 19/2026 có hiệu lực từ 01/07/2026", "2026-07-01", "HARD"),
        ("GOLD-TEM-20", "Vào ngày 15/01/2025, thứ tự hiệu lực của hệ thống báo hiệu đường bộ được áp dụng theo quy chuẩn nào?",
         "traffic_road_signs_qcvn41_51_2024_tt_bgtvt", "51/2024/TT-BGTVT", 4, None, "QCVN 41:2024 ban hành kèm TT 51/2024 có hiệu lực từ 01/01/2025", "2025-01-15", "MEDIUM"),
        ("GOLD-TEM-21", "Vào ngày 05/08/2026, quy định kết nối dữ liệu camera giám sát hạ tầng ITS cao tốc với Cảnh sát giao thông căn cứ vào đâu?",
         "traffic_road_infra_amendment_241_2026_nd_cp", "241/2026/NĐ-CP", 1, None, "Nghị định 241/2026 có hiệu lực từ 01/07/2026", "2026-08-05", "HARD"),
        ("GOLD-TEM-22", "Vào ngày 10/02/2025, hành vi lạng lách đánh võng đối với xe máy bị xử phạt theo Nghị định nào?",
         "traffic_penalty_168_2024_nd_cp", "168/2024/NĐ-CP", 6, "Khoản 9", "Nghị định 168/2024 có hiệu lực từ 01/01/2025", "2025-02-10", "MEDIUM"),
        ("GOLD-TEM-23", "Vào ngày 20/09/2026, người có bằng lái xe ô tô bị mất muốn xin cấp lại thì nộp hồ sơ theo quy định của văn bản nào?",
         "traffic_driving_license_108_2026_tt_bca", "108/2026/TT-BCA", 22, None, "Áp dụng Thông tư 108/2026", "2026-09-20", "MEDIUM"),
        ("GOLD-TEM-24", "Vào ngày 15/06/2025, quy định về tốc độ tối đa của ô tô trên đường cao tốc áp dụng theo văn bản nào?",
         "traffic_speed_distance_38_2024_tt_bgtvt", "38/2024/TT-BGTVT", 9, None, "Thông tư 38/2024/TT-BGTVT", "2025-06-15", "MEDIUM"),
        ("GOLD-TEM-25", "Vào ngày 25/08/2026, hành vi không nhường đường cho xe xin vượt khi có đủ điều kiện an toàn bị xử phạt theo văn bản nào?",
         "traffic_penalty_amendment_238_2026_nd_cp", "238/2026/NĐ-CP", 1, "Khoản 1", "Nghị định 238 sửa Điều 5 NĐ 168", "2026-08-25", "HARD"),
        ("GOLD-TEM-26", "Vào ngày 15/04/2025, người bị tạm giữ xe vi phạm giao thông có thể nộp tiền phạt trực tuyến để nhận lại xe qua cổng nào?",
         "traffic_penalty_168_2024_nd_cp", "168/2024/NĐ-CP", 51, None, "Nghị định 168/2024/NĐ-CP", "2025-04-15", "MEDIUM"),
        ("GOLD-TEM-27", "Vào ngày 01/07/2025, Thông tư 12/2025/TT-BXD về tải trọng trục xe bắt đầu có hiệu lực và thay thế văn bản nào?",
         "traffic_weight_limits_12_2025_tt_bxd", "12/2025/TT-BXD", 1, None, "Thông tư 12/2025/TT-BXD có hiệu lực từ 01/07/2025", "2025-07-01", "HARD"),
        ("GOLD-TEM-28", "Vào ngày 12/08/2026, trung tâm đào tạo lái xe phải lưu trữ dữ liệu DAT của học viên trong thời hạn bao lâu?",
         "traffic_driver_training_94_2026_nd_cp", "94/2026/NĐ-CP", 8, "Khoản 3", "Nghị định 94/2026/NĐ-CP", "2026-08-12", "HARD"),
        ("GOLD-TEM-29", "Vào ngày 01/01/2025, Luật Trật tự, an toàn giao thông đường bộ bắt đầu có hiệu lực thay thế Luật nào?",
         "traffic_order_36_2024_qh15", "36/2024/QH15", 1, None, "Luật 36/2024 thay thế Luật Giao thông đường bộ 2008", "2025-01-01", "EASY"),
        ("GOLD-TEM-30", "Vào ngày 30/08/2026, cơ quan nào có thẩm quyền thu hồi Giấy phép sát hạch lái xe của trung tâm sát hạch?",
         "traffic_driver_training_94_2026_nd_cp", "94/2026/NĐ-CP", 26, "Khoản 4", "Nghị định 94/2026 phân quyền thẩm quyền thu hồi giấy phép", "2026-08-30", "HARD")
    ]
    for cid, q, doc_id, off, art, cl, note, aod, diff in temporal_queries:
        cases.append({
            "test_case_id": cid,
            "category": "TEMPORAL_QUERY",
            "query": q,
            "as_of_date": aod,
            "expected_evidence": {
                "document_id": doc_id,
                "official_number": off,
                "article": art,
                "clause": cl,
                "notes": note
            },
            "difficulty": diff
        })

    # -------------------------------------------------------------
    # 6. AMENDMENT_LINEAGE (30 cases): Câu hỏi về quan hệ sửa đổi
    # -------------------------------------------------------------
    amendment_lineages = [
        ("GOLD-AMD-01", "Nghị định 238/2026/NĐ-CP sửa đổi, bổ sung những điều khoản nào của Nghị định số 168/2024/NĐ-CP?",
         "traffic_penalty_amendment_238_2026_nd_cp", "238/2026/NĐ-CP", 1, None, "Sửa đổi Điều 5, Điều 13, Điều 32 của Nghị định 168", "2026-08-15", "MEDIUM"),
        ("GOLD-AMD-02", "Nghị định 218/2026/NĐ-CP sửa đổi nội dung gì của Nghị định số 158/2024/NĐ-CP về kinh doanh vận tải ô tô?",
         "traffic_amendment_218_2026_nd_cp", "218/2026/NĐ-CP", 1, None, "Sửa đổi Điều 7 về xe hợp đồng và thu hồi GPKD vận tải", "2026-08-10", "MEDIUM"),
        ("GOLD-AMD-03", "Nghị định 241/2026/NĐ-CP sửa đổi, bổ sung các quy định nào của Nghị định số 165/2024/NĐ-CP?",
         "traffic_road_infra_amendment_241_2026_nd_cp", "241/2026/NĐ-CP", 1, None, "Sửa đổi quy định quản lý kết cấu hạ tầng đường bộ ITS", "2026-07-01", "HARD"),
        ("GOLD-AMD-04", "Thông tư 108/2026/TT-BCA thay thế cho Thông tư nào trong lĩnh vực sát hạch, cấp giấy phép lái xe?",
         "traffic_driving_license_108_2026_tt_bca", "108/2026/TT-BCA", 35, None, "Thay thế Thông tư số 12/2025/TT-BCA", "2026-07-01", "EASY"),
        ("GOLD-AMD-05", "Thông tư 105/2026/TT-BCA sửa đổi, bổ sung quy định nào của Thông tư số 65/2024/TT-BCA về kiểm tra phục hồi điểm GPLX?",
         "traffic_points_recovery_105_2026_tt_bca", "105/2026/TT-BCA", 1, None, "Sửa đổi Điều 9 về quy trình nộp hồ sơ phục hồi điểm qua VNeID", "2026-07-01", "MEDIUM"),
        ("GOLD-AMD-06", "Thông tư 13/2025/TT-BCA sửa đổi, bổ sung những điểm mới nào về đăng ký xe so với Thông tư 79/2024/TT-BCA?",
         "traffic_amendment_13_2025_tt_bca", "13/2025/TT-BCA", 1, None, "Sửa đổi đăng ký xe toàn trình trên cổng dịch vụ công", "2025-03-01", "MEDIUM"),
        ("GOLD-AMD-07", "Thông tư 51/2025/TT-BCA sửa đổi quy định gì về thẩm quyền đăng ký xe mô tô của Công an cấp xã?",
         "traffic_amendment_51_2025_tt_bca", "51/2025/TT-BCA", 1, None, "Cho phép đăng ký xe máy tại bất kỳ xã nào trong tỉnh", "2025-07-01", "HARD"),
        ("GOLD-AMD-08", "Thông tư 19/2026/TT-BXD sửa đổi quy định tải trọng trục xe của Thông tư 12/2025/TT-BXD như thế nào?",
         "traffic_weight_amendment_19_2026_tt_bxd", "19/2026/TT-BXD", 1, None, "Sửa đổi quy định tải trọng trục xe có hệ thống bóng hơi", "2026-07-01", "HARD"),
        ("GOLD-AMD-09", "Văn bản hợp nhất số 26/VBHN-BXD năm 2026 hợp nhất các văn bản nào về tải trọng đường bộ?",
         "traffic_weight_consolidated_26_2026_vbhn_bxd", "26/VBHN-BXD", 1, None, "Hợp nhất Thông tư 12/2025 và Thông tư 19/2026", "2026-07-01", "MEDIUM"),
        ("GOLD-AMD-10", "Thông tư 45/2026/TT-BXD sửa đổi bổ sung Thông tư số 30/2026/TT-BXD về kiểm định xe cơ giới ở nội dung nào?",
         "traffic_inspection_amendment_45_2026_tt_bxd", "45/2026/TT-BXD", 1, None, "Sửa đổi kiểm định xe chuyên dùng và camera AI kiểm chuẩn", "2026-07-01", "HARD"),
        ("GOLD-AMD-11", "Thông tư 73/2024/TT-BCA bãi bỏ những văn bản quy phạm pháp luật nào về công tác tuần tra kiểm soát của CSGT?",
         "traffic_police_patrol_73_2024_tt_bca", "73/2024/TT-BCA", 32, None, "Bãi bỏ toàn bộ Thông tư 32/2023 và Điều 1 Thông tư 28/2024", "2025-01-01", "HARD"),
        ("GOLD-AMD-12", "Thông tư 79/2024/TT-BCA khi ban hành đã bãi bỏ quy định nào của Thông tư số 28/2024/TT-BCA?",
         "traffic_vehicle_registration_79_2024_tt_bca", "79/2024/TT-BCA", 39, None, "Bãi bỏ Điều 2 Thông tư 28/2024/TT-BCA", "2025-01-01", "HARD"),
        ("GOLD-AMD-13", "Quy chuẩn kỹ thuật quốc gia QCVN 41:2024/BGTVT thay thế cho Quy chuẩn kỹ thuật nào trước đây?",
         "traffic_road_signs_qcvn41_51_2024_tt_bgtvt", "51/2024/TT-BGTVT", 2, None, "Thay thế QCVN 41:2019/BGTVT", "2025-01-01", "EASY"),
        ("GOLD-AMD-14", "Nghị định 94/2026/NĐ-CP thay thế các nghị định nào về điều kiện kinh doanh đào tạo và sát hạch lái xe?",
         "traffic_driver_training_94_2026_nd_cp", "94/2026/NĐ-CP", 41, None, "Thay thế Nghị định 65/2016/NĐ-CP và Nghị định 138/2018/NĐ-CP", "2026-07-01", "HARD"),
        ("GOLD-AMD-15", "Điều 19 của Nghị định 161/2024/NĐ-CP về vận chuyển hàng hóa nguy hiểm bị bãi bỏ bởi văn bản nào?",
         "traffic_points_recovery_105_2026_tt_bca", "105/2026/TT-BCA", 1, None, "Bãi bỏ Điều 19 từ 01/07/2025", "2025-07-01", "HARD"),
        ("GOLD-AMD-16", "Mức phạt che biển số ô tô được sửa đổi từ mức phạt cũ tại Nghị định 168 lên mức bao nhiêu theo Nghị định 238?",
         "traffic_penalty_amendment_238_2026_nd_cp", "238/2026/NĐ-CP", 1, "Khoản 2", "Tăng từ 4 - 6 triệu đồng lên 20 - 26 triệu đồng", "2026-08-15", "MEDIUM"),
        ("GOLD-AMD-17", "Quy định bổ sung điểm q vào Khoản 1 Điều 5 Nghị định 168 được ban hành bởi Nghị định nào?",
         "traffic_penalty_amendment_238_2026_nd_cp", "238/2026/NĐ-CP", 1, "Khoản 1", "Nghị định 238/2026/NĐ-CP", "2026-08-15", "HARD"),
        ("GOLD-AMD-18", "Quy định cấm nhà xe hợp đồng gom khách, bán vé như tuyến cố định được siết chặt bởi Nghị định sửa đổi nào?",
         "traffic_amendment_218_2026_nd_cp", "218/2026/NĐ-CP", 1, None, "Nghị định 218/2026 sửa Nghị định 158/2024", "2026-08-10", "MEDIUM"),
        ("GOLD-AMD-19", "Quy định bãi bỏ thi mô phỏng tình huống giao thông trong sát hạch lái xe được ban hành tại văn bản nào?",
         "traffic_driving_license_108_2026_tt_bca", "108/2026/TT-BCA", 15, None, "Thông tư 108/2026/TT-BCA", "2026-07-01", "EASY"),
        ("GOLD-AMD-20", "Văn bản nào sửa đổi quy định kiểm tra phanh con lăn và phân tích khí thải tự động trong đăng kiểm xe?",
         "traffic_inspection_amendment_45_2026_tt_bxd", "45/2026/TT-BXD", 1, None, "Thông tư 45/2026 sửa Thông tư 30/2026", "2026-07-01", "HARD"),
        ("GOLD-AMD-21", "Nghị định nào hướng dẫn Điều 77 Luật Trật tự, an toàn giao thông đường bộ về chia sẻ dữ liệu kết cấu hạ tầng với CSGT?",
         "traffic_road_infra_amendment_241_2026_nd_cp", "241/2026/NĐ-CP", 1, None, "Nghị định 241/2026/NĐ-CP", "2026-07-01", "HARD"),
        ("GOLD-AMD-22", "Thông tư nào đã bãi bỏ Thông tư 47/2024/TT-BGTVT về kiểm định an toàn kỹ thuật và bảo vệ môi trường xe cơ giới?",
         "traffic_inspection_procedures_30_2026_tt_bxd", "30/2026/TT-BXD", 32, None, "Thông tư 30/2026/TT-BXD bãi bỏ Thông tư 47", "2026-07-01", "HARD"),
        ("GOLD-AMD-23", "Quy định sửa đổi thủ tục cấp biển số tạm thời được cập nhật trong Thông tư nào của Bộ Công an?",
         "traffic_amendment_13_2025_tt_bca", "13/2025/TT-BCA", 1, None, "Thông tư 13/2025 sửa đổi TT 79", "2025-03-01", "MEDIUM"),
        ("GOLD-AMD-24", "Văn bản nào bãi bỏ quy định trang bị mô hình buồng lái mô phỏng trong trung tâm sát hạch lái xe?",
         "traffic_driver_training_94_2026_nd_cp", "94/2026/NĐ-CP", 24, "Khoản 3", "Nghị định 94/2026 bãi bỏ bắt buộc mô phỏng trong trung tâm sát hạch", "2026-07-01", "HARD"),
        ("GOLD-AMD-25", "Văn bản nào quy định việc tự động phục hồi đủ 12 điểm GPLX nếu sau 12 tháng không bị trừ điểm tiếp?",
         "traffic_points_recovery_105_2026_tt_bca", "105/2026/TT-BCA", 1, None, "Thông tư 105/2026/TT-BCA", "2026-07-01", "MEDIUM"),
        ("GOLD-AMD-26", "Nghị định 151/2024/NĐ-CP được sửa đổi bổ sung bởi văn bản nào vào năm 2026?",
         "traffic_guideline_151_2024_nd_cp", "151/2024/NĐ-CP", 1, None, "Được sửa đổi bởi Nghị định 236/2026/NĐ-CP", "2026-07-01", "HARD"),
        ("GOLD-AMD-27", "Văn bản nào sửa đổi quy định phân cấp thẩm quyền đăng kiểm xe cơ giới cho Bộ Xây dựng?",
         "traffic_inspection_procedures_30_2026_tt_bxd", "30/2026/TT-BXD", 1, None, "Thông tư 30/2026/TT-BXD", "2026-07-01", "HARD"),
        ("GOLD-AMD-28", "Quy định về thời hạn chuyển tiếp sử dụng phôi Giấy phép lái xe cũ được nêu tại điều nào của Thông tư 12/2025?",
         "traffic_driving_license_12_2025_tt_bca", "12/2025/TT-BCA", 18, None, "Điều khoản chuyển tiếp phôi bằng lái xe đến 2027", "2025-03-01", "HARD"),
        ("GOLD-AMD-29", "Luật số 118/2025/QH15 đã sửa đổi điều nào của Luật Trật tự, an toàn giao thông đường bộ 2024?",
         "traffic_order_36_2024_qh15", "36/2024/QH15", 10, None, "Sửa đổi Điều 10 về bảo đảm an toàn cho trẻ em trên xe", "2026-07-01", "HARD"),
        ("GOLD-AMD-30", "Văn bản nào sửa đổi quy định xử phạt vi phạm nồng độ cồn và cơ chế trừ điểm đối với xe máy chuyên dùng?",
         "traffic_penalty_168_2024_nd_cp", "168/2024/NĐ-CP", 7, None, "Nghị định 168/2024/NĐ-CP", "2025-01-01", "MEDIUM")
    ]
    for cid, q, doc_id, off, art, cl, note, aod, diff in amendment_lineages:
        cases.append({
            "test_case_id": cid,
            "category": "AMENDMENT_LINEAGE",
            "query": q,
            "as_of_date": aod,
            "expected_evidence": {
                "document_id": doc_id,
                "official_number": off,
                "article": art,
                "clause": cl,
                "notes": note
            },
            "difficulty": diff
        })

    # -------------------------------------------------------------
    # 7. TEMPORAL_CONTRAST (25 cases): Phân biệt trước / sau ngày cụ thể
    # -------------------------------------------------------------
    temporal_contrasts = [
        ("GOLD-CTR-01A", "Thí sinh thi sát hạch lái xe ô tô vào ngày 30/06/2026 có phải thực hiện bài thi mô phỏng tình huống giao thông không?",
         "traffic_driving_license_12_2025_tt_bca", "12/2025/TT-BCA", 14, "Khoản 1", "Trước 01/07/2026 áp dụng TT 12 bắt buộc thi mô phỏng", "2026-06-30", "MEDIUM"),
        ("GOLD-CTR-01B", "Thí sinh thi sát hạch lái xe ô tô vào ngày 01/07/2026 có phải thực hiện bài thi mô phỏng tình huống giao thông không?",
         "traffic_driving_license_108_2026_tt_bca", "108/2026/TT-BCA", 15, "Khoản 1", "Từ 01/07/2026 áp dụng TT 108 bãi bỏ thi mô phỏng", "2026-07-01", "MEDIUM"),
        ("GOLD-CTR-02A", "Xe hợp đồng vận chuyển khách có được đón trả khách tại văn phòng đại diện vào ngày 09/08/2026 không?",
         "traffic_transport_158_2024_nd_cp", "158/2024/NĐ-CP", 7, None, "Trước 10/08/2026 áp dụng NĐ 158", "2026-08-09", "HARD"),
        ("GOLD-CTR-02B", "Xe hợp đồng vận chuyển khách có được đón trả khách tại văn phòng đại diện vào ngày 10/08/2026 không?",
         "traffic_amendment_218_2026_nd_cp", "218/2026/NĐ-CP", 1, None, "Từ 10/08/2026 NĐ 218 cấm tuyệt đối đón khách tại VP đại diện", "2026-08-10", "HARD"),
        ("GOLD-CTR-03A", "Mức phạt tiền đối với hành vi che dán biển số xe ô tô vào ngày 14/08/2026 là bao nhiêu?",
         "traffic_penalty_168_2024_nd_cp", "168/2024/NĐ-CP", 13, "Khoản 8", "Trước 15/08/2026 áp dụng mức phạt NĐ 168 (4 - 6 triệu)", "2026-08-14", "HARD"),
        ("GOLD-CTR-03B", "Mức phạt tiền đối với hành vi che dán biển số xe ô tô vào ngày 15/08/2026 là bao nhiêu?",
         "traffic_penalty_amendment_238_2026_nd_cp", "238/2026/NĐ-CP", 1, "Khoản 2", "Từ 15/08/2026 áp dụng mức phạt NĐ 238 (20 - 26 triệu)", "2026-08-15", "HARD"),
        ("GOLD-CTR-04A", "Trước ngày 01/07/2025, thẩm quyền cấp phép vận chuyển hàng nguy hiểm loại 1 thực hiện theo quy định nào của Nghị định 161?",
         "traffic_dangerous_goods_161_2024_nd_cp", "161/2024/NĐ-CP", 14, "Khoản 1", "Áp dụng Điều 14 v1 của NĐ 161", "2025-06-30", "HARD"),
        ("GOLD-CTR-04B", "Từ ngày 01/07/2025, thẩm quyền cấp phép vận chuyển hàng nguy hiểm loại 1 thực hiện theo quy định nào?",
         "traffic_points_recovery_105_2026_tt_bca", "105/2026/TT-BCA", 1, None, "Áp dụng sửa đổi có hiệu lực từ 01/07/2025", "2025-07-01", "HARD"),
        ("GOLD-CTR-05A", "Trước ngày 01/07/2026, quy định quản lý bảo trì kết cấu hạ tầng đường bộ áp dụng theo Nghị định nào?",
         "traffic_road_law_detail_165_2024_nd_cp", "165/2024/NĐ-CP", 21, None, "Áp dụng Điều 21 v1 của NĐ 165", "2026-06-30", "HARD"),
        ("GOLD-CTR-05B", "Từ ngày 01/07/2026, quy định kết nối dữ liệu ITS và kiểm soát tải trọng tự động áp dụng theo Nghị định nào?",
         "traffic_road_infra_amendment_241_2026_nd_cp", "241/2026/NĐ-CP", 1, None, "Áp dụng Nghị định 241 sửa NĐ 165", "2026-07-01", "HARD"),
        ("GOLD-CTR-06A", "Vào ngày 30/06/2026, việc nộp hồ sơ phục hồi điểm giấy phép lái xe có nộp qua VNeID được không?",
         "traffic_points_recovery_65_2024_tt_bca", "65/2024/TT-BCA", 9, None, "Trước 01/07/2026 nộp hồ sơ trực tiếp theo Thông tư 65", "2026-06-30", "MEDIUM"),
        ("GOLD-CTR-06B", "Vào ngày 01/07/2026, người dân có thể nộp hồ sơ phục hồi điểm GPLX trực tuyến qua VNeID theo Thông tư nào?",
         "traffic_points_recovery_105_2026_tt_bca", "105/2026/TT-BCA", 1, None, "Từ 01/07/2026 TT 105 cho phép nộp trực tuyến", "2026-07-01", "MEDIUM"),
        ("GOLD-CTR-07A", "Trước ngày 01/03/2025, hồ sơ đăng ký xe máy bắt buộc phải nộp bản giấy hay nộp trực tuyến toàn trình?",
         "traffic_vehicle_registration_79_2024_tt_bca", "79/2024/TT-BCA", 7, None, "Áp dụng Thông tư 79 bản gốc", "2025-02-28", "MEDIUM"),
        ("GOLD-CTR-07B", "Từ ngày 01/03/2025, thủ tục đăng ký xe lần đầu được thực hiện trực tuyến toàn trình theo Thông tư nào?",
         "traffic_amendment_13_2025_tt_bca", "13/2025/TT-BCA", 1, None, "Áp dụng Thông tư 13/2025 sửa đổi", "2025-03-01", "MEDIUM"),
        ("GOLD-CTR-08A", "Trước ngày 01/07/2025, người mua xe máy có được đăng ký xe tại xã khác nơi thường trú trong cùng tỉnh không?",
         "traffic_vehicle_registration_79_2024_tt_bca", "79/2024/TT-BCA", 4, None, "Trước 01/07/2025 chỉ đăng ký tại nơi thường trú theo TT 79", "2025-06-30", "HARD"),
        ("GOLD-CTR-08B", "Từ ngày 01/07/2025, người dân được quyền đăng ký xe máy tại bất kỳ Công an xã nào trong tỉnh theo Thông tư nào?",
         "traffic_amendment_51_2025_tt_bca", "51/2025/TT-BCA", 1, None, "Áp dụng Thông tư 51/2025 sửa đổi", "2025-07-01", "HARD"),
        ("GOLD-CTR-09A", "Trước ngày 01/07/2026, tải trọng trục xe có hệ thống treo bóng hơi tính theo quy định nào của Thông tư 12?",
         "traffic_weight_limits_12_2025_tt_bxd", "12/2025/TT-BXD", 4, None, "Áp dụng quy định cũ tại Thông tư 12/2025", "2026-06-30", "HARD"),
        ("GOLD-CTR-09B", "Từ ngày 01/07/2026, tải trọng trục xe ô tô trang bị hệ thống treo khí nén được tính theo Thông tư nào?",
         "traffic_weight_amendment_19_2026_tt_bxd", "19/2026/TT-BXD", 1, None, "Áp dụng Thông tư 19/2026 sửa đổi", "2026-07-01", "HARD"),
        ("GOLD-CTR-10A", "Trước ngày 01/07/2026, niên hạn sử dụng xe ô tô được quản lý theo Nghị định nào?",
         "traffic_inspection_framework_89_2026_nd_cp", "89/2026/NĐ-CP", 3, None, "Trước 01/07/2026 áp dụng quy định hiện hành", "2026-06-30", "MEDIUM"),
        ("GOLD-CTR-10B", "Từ ngày 01/07/2026, niên hạn xe ô tô chở người không quá 20 năm áp dụng chính thức theo Nghị định nào?",
         "traffic_inspection_framework_89_2026_nd_cp", "89/2026/NĐ-CP", 3, None, "Áp dụng Nghị định 89/2026 có hiệu lực từ 01/07/2026", "2026-07-01", "MEDIUM"),
        ("GOLD-CTR-11A", "Vào ngày 30/06/2026, trung tâm đăng kiểm thực hiện thủ tục kiểm định xe cơ giới theo Thông tư nào?",
         "traffic_inspection_procedures_30_2026_tt_bxd", "30/2026/TT-BXD", 1, None, "Trước 01/07/2026 áp dụng các thông tư kiểm định trước", "2026-06-30", "HARD"),
        ("GOLD-CTR-11B", "Từ ngày 01/07/2026, thủ tục kiểm định số hóa và cấp chứng nhận kiểm định điện tử áp dụng theo Thông tư nào?",
         "traffic_inspection_procedures_30_2026_tt_bxd", "30/2026/TT-BXD", 5, None, "Áp dụng Thông tư 30/2026 của Bộ Xây dựng", "2026-07-01", "MEDIUM"),
        ("GOLD-CTR-12A", "Trước ngày 15/08/2026, hành vi chở trẻ em ngồi ghế trước không có thiết bị an toàn có bị phạt theo Nghị định 168 không?",
         "traffic_penalty_168_2024_nd_cp", "168/2024/NĐ-CP", 5, None, "Bản gốc NĐ 168 chưa có điều khoản phạt riêng", "2026-08-14", "HARD"),
        ("GOLD-CTR-12B", "Từ ngày 15/08/2026, hành vi chở trẻ em ngồi ghế trước không có thiết bị an toàn bị xử phạt theo văn bản nào?",
         "traffic_penalty_amendment_238_2026_nd_cp", "238/2026/NĐ-CP", 1, "Khoản 3", "Nghị định 238/2026 bổ sung mức xử phạt", "2026-08-15", "HARD"),
        ("GOLD-CTR-13A", "Vào ngày 31/12/2024, các hành vi vi phạm trật tự an toàn giao thông đường bộ được xử phạt theo Nghị định nào?",
         "traffic_penalty_168_2024_nd_cp", "168/2024/NĐ-CP", 1, None, "Nghị định 168 bắt đầu hiệu lực từ 01/01/2025", "2024-12-31", "EASY")
    ]
    for cid, q, doc_id, off, art, cl, note, aod, diff in temporal_contrasts:
        cases.append({
            "test_case_id": cid,
            "category": "TEMPORAL_CONTRAST",
            "query": q,
            "as_of_date": aod,
            "expected_evidence": {
                "document_id": doc_id,
                "official_number": off,
                "article": art,
                "clause": cl,
                "notes": note
            },
            "difficulty": diff
        })

    # -------------------------------------------------------------
    # 8. HARD_CONFUSING (20 cases): Câu hỏi khó, dễ gây nhầm lẫn
    # -------------------------------------------------------------
    hard_confusings = [
        ("GOLD-HRD-01", "Phân biệt trường hợp bị trừ điểm Giấy phép lái xe với trường hợp bị tước quyền sử dụng Giấy phép lái xe theo Nghị định 168?",
         "traffic_penalty_168_2024_nd_cp", "168/2024/NĐ-CP", 32, None, "Trừ điểm là biện pháp quản lý hành chính, tước GPLX là hình thức xử phạt bổ sung", "2025-01-01", "HARD"),
        ("GOLD-HRD-02", "Khi điều khiển xe ô tô rẽ phải tại ngã tư có đèn đỏ, người lái xe chỉ được rẽ phải trong điều kiện nào?",
         "traffic_road_signs_qcvn41_51_2024_tt_bgtvt", "51/2024/TT-BGTVT", 10, "Mục 10", "Chỉ được rẽ khi có biển phụ cho phép rẽ phải hoặc đèn xanh rẽ phải", "2025-01-01", "HARD"),
        ("GOLD-HRD-03", "Trường hợp người lái xe có nồng độ cồn chưa vượt quá 50 miligam/100 mililít máu thì bị xử phạt và trừ bao nhiêu điểm GPLX?",
         "traffic_penalty_168_2024_nd_cp", "168/2024/NĐ-CP", 5, "Khoản 6", "Khung phạt thấp nhất của nồng độ cồn ô tô", "2025-01-01", "HARD"),
        ("GOLD-HRD-04", "Biển báo gộp làn đường theo phương tiện và biển báo hiệu tốc độ tối đa cho phép trên từng làn đường khác nhau như thế nào theo QCVN 41:2024?",
         "traffic_road_signs_qcvn41_51_2024_tt_bgtvt", "51/2024/TT-BGTVT", 15, "Mục 15", "Phân biệt biển R.412 và biển R.415 gộp làn", "2025-01-01", "HARD"),
        ("GOLD-HRD-05", "Trường hợp xe ô tô bị phạt nguội nhưng chủ xe không phải là người điều khiển xe vi phạm thì ai phải chịu trách nhiệm nộp phạt?",
         "traffic_penalty_168_2024_nd_cp", "168/2024/NĐ-CP", 30, "Khoản 8", "Chủ phương tiện phải chứng minh người điều khiển hoặc chịu trách nhiệm nộp phạt", "2025-01-01", "HARD"),
        ("GOLD-HRD-06", "Hành vi sử dụng Giấy phép lái xe giả khác gì về chế tài so với hành vi không có Giấy phép lái xe theo Nghị định 168?",
         "traffic_penalty_168_2024_nd_cp", "168/2024/NĐ-CP", 5, "Khoản 9", "Dùng bằng giả bị tịch thu và phạt tiền kịch khung; có thể bị xử lý hình sự", "2025-01-01", "HARD"),
        ("GOLD-HRD-07", "Thế nào là hành vi cản trở xe ưu tiên và mức xử phạt đối với người điều khiển xe ô tô không nhường đường cho xe cứu thương?",
         "traffic_penalty_168_2024_nd_cp", "168/2024/NĐ-CP", 5, "Khoản 5", "Phạt tiền từ 6.000.000 đến 8.000.000 đồng và trừ 03 điểm GPLX", "2025-01-01", "HARD"),
        ("GOLD-HRD-08", "Phân biệt quy tắc nhường đường tại nơi đường giao nhau có vòng xuyến và không có vòng xuyến theo Luật TTATGTĐB?",
         "traffic_order_36_2024_qh15", "36/2024/QH15", 24, None, "Có vòng xuyến nhường bên trái; không có vòng xuyến nhường bên phải", "2025-01-01", "MEDIUM"),
        ("GOLD-HRD-09", "Trường hợp nào người điều khiển xe mô tô được phép đi vào đường cao tốc mà không bị xử phạt?",
         "traffic_order_36_2024_qh15", "36/2024/QH15", 26, "Khoản 4", "Chỉ xe mô tô tuần tra của lực lượng cảnh sát làm nhiệm vụ", "2025-01-01", "MEDIUM"),
        ("GOLD-HRD-10", "Điểm khác biệt căn bản giữa tạm giữ phương tiện để ngăn chặn vi phạm và tịch thu phương tiện theo Nghị định 168 là gì?",
         "traffic_penalty_168_2024_nd_cp", "168/2024/NĐ-CP", 51, None, "Tạm giữ có thời hạn tối đa 7 ngày; tịch thu là xác lập quyền sở hữu nhà nước", "2025-01-01", "HARD"),
        ("GOLD-HRD-11", "Khi đèn tín hiệu giao thông nhấp nháy vàng thì người tham gia giao thông được đi như thế nào?",
         "traffic_road_signs_qcvn41_51_2024_tt_bgtvt", "51/2024/TT-BGTVT", 10, "Mục 10", "Được đi nhưng phải giảm tốc độ, chú ý quan sát và nhường đường cho người đi bộ", "2025-01-01", "MEDIUM"),
        ("GOLD-HRD-12", "Hành vi bấm còi trong đô thị từ 22h đêm đến 5h sáng hôm sau bị xử phạt như thế nào?",
         "traffic_penalty_168_2024_nd_cp", "168/2024/NĐ-CP", 5, "Khoản 1", "Phạt tiền từ 300.000 đến 500.000 đồng", "2025-01-01", "EASY"),
        ("GOLD-HRD-13", "Quy định về khoảng cách an toàn khi chạy xe trong điều kiện trời mưa, sương mù, mặt đường trơn trượt được tính như thế nào?",
         "traffic_speed_distance_38_2024_tt_bgtvt", "38/2024/TT-BGTVT", 11, "Khoản 3", "Người lái xe phải chủ động giữ khoảng cách lớn hơn khoảng cách tối thiểu", "2025-01-01", "HARD"),
        ("GOLD-HRD-14", "Trường hợp xe ô tô chở hành khách quá số người quy định thì mức phạt tính trên mỗi hành khách vượt quá là bao nhiêu?",
         "traffic_penalty_168_2024_nd_cp", "168/2024/NĐ-CP", 23, "Khoản 2", "Phạt tiền từ 400.000 đến 600.000 đồng trên mỗi người chở quá", "2025-01-01", "HARD"),
        ("GOLD-HRD-15", "Hành vi đi ngược chiều trên đường cao tốc bị xử phạt bao nhiêu tiền và trừ bao nhiêu điểm GPLX?",
         "traffic_penalty_168_2024_nd_cp", "168/2024/NĐ-CP", 5, "Khoản 11", "Phạt tiền từ 30 - 40 triệu đồng và trừ 12 điểm GPLX", "2025-01-01", "MEDIUM"),
        ("GOLD-HRD-16", "Người lái xe ô tô kinh doanh vận tải hành khách liên tục quá 4 giờ hoặc quá 10 giờ trong một ngày bị phạt theo điều nào?",
         "traffic_penalty_168_2024_nd_cp", "168/2024/NĐ-CP", 23, "Khoản 6", "Xử phạt người lái xe vi phạm thời gian làm việc trong ngày", "2025-01-01", "HARD"),
        ("GOLD-HRD-17", "Quy định về việc chuyển quyền sở hữu xe trúng đấu giá có được chuyển nhượng biển số đi kèm không?",
         "traffic_order_36_2024_qh15", "36/2024/QH15", 37, "Khoản 4", "Chỉ được chuyển nhượng biển số trúng đấu giá kèm theo xe chuyển nhượng", "2025-01-01", "HARD"),
        ("GOLD-HRD-18", "Trường hợp xe hết niên hạn sử dụng vẫn tham gia giao thông thì người lái xe và chủ xe bị xử lý như thế nào?",
         "traffic_penalty_168_2024_nd_cp", "168/2024/NĐ-CP", 5, "Khoản 7", "Phạt tiền, tịch thu phương tiện và tước quyền sử dụng GPLX", "2026-07-01", "HARD"),
        ("GOLD-HRD-19", "Quy định trừ điểm giấy phép lái xe có áp dụng đối với người đi xe đạp hoặc xe máy điện không?",
         "traffic_order_36_2024_qh15", "36/2024/QH15", 62, "Khoản 1", "Chỉ áp dụng với người điều khiển phương tiện có Giấy phép lái xe", "2025-01-01", "EASY"),
        ("GOLD-HRD-20", "Thế nào là hành vi 'dừng xe' khác biệt với 'đỗ xe' theo định nghĩa pháp lý của Luật TTATGTĐB 2024?",
         "traffic_order_36_2024_qh15", "36/2024/QH15", 18, "Khoản 1", "Dừng xe là đứng yên tạm thời; đỗ xe là đứng yên không giới hạn thời gian", "2025-01-01", "MEDIUM")
    ]
    for cid, q, doc_id, off, art, cl, note, aod, diff in hard_confusings:
        cases.append({
            "test_case_id": cid,
            "category": "HARD_CONFUSING",
            "query": q,
            "as_of_date": aod,
            "expected_evidence": {
                "document_id": doc_id,
                "official_number": off,
                "article": art,
                "clause": cl,
                "notes": note
            },
            "difficulty": diff
        })

    with open(OUT_FILE, "w", encoding="utf-8") as f:
        json.dump({"total_cases": len(cases), "cases": cases}, f, ensure_ascii=False, indent=2)

    print(f"[+] Successfully generated Gold Evaluation Dataset: {len(cases)} cases -> {OUT_FILE}")
    category_counts = {}
    for c in cases:
        cat = c["category"]
        category_counts[cat] = category_counts.get(cat, 0) + 1
    for cat, cnt in category_counts.items():
        print(f"    - {cat:25}: {cnt} cases")

if __name__ == "__main__":
    build_dataset()
