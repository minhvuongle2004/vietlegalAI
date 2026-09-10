import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

RAW_DIR = Path("data/01_raw/traffic_p1_batch")
RAW_DIR.mkdir(parents=True, exist_ok=True)

def generate_12_2025():
    # Thông tư số 12/2025/TT-BXD: 4 Chương, 31 Điều
    articles = []

    # Chương I: Quy định chung (Điều 1 - Điều 4)
    articles.append("""
    <h3>CHƯƠNG I: QUY ĐỊNH CHUNG</h3>
    <p><b>Điều 1. Phạm vi điều chỉnh</b></p>
    <p>1. Thông tư này quy định về tải trọng, khổ giới hạn của đường bộ; công bố tải trọng và khổ giới hạn của đường bộ; điều kiện, trình tự, thủ tục cấp Giấy phép lưu hành cho xe quá tải trọng, xe quá khổ giới hạn, xe bánh xích trên đường bộ.</p>
    <p>2. Quy định về vận chuyển hàng siêu trường, siêu trọng trên mạng lưới đường bộ.</p>
    """)

    articles.append("""
    <p><b>Điều 2. Đối tượng áp dụng</b></p>
    <p>Thông tư này áp dụng đối với cơ quan, tổ chức, cá nhân liên quan đến việc quản lý, khai thác đường bộ và chủ phương tiện, người lái xe, người thuê vận tải, người xếp dỡ hàng hóa trên xe ô tô tham gia giao thông đường bộ.</p>
    """)

    articles.append("""
    <p><b>Điều 3. Giải thích từ ngữ</b></p>
    <p>1. <i>Tải trọng của đường bộ</i> bao gồm tải trọng trục xe và tổng trọng lượng của xe cơ giới được phép lưu hành trên đoạn tuyến đường bộ theo công bố của cơ quan có thẩm quyền.</p>
    <p>2. <i>Khổ giới hạn của đường bộ</i> là khoảng không gian giới hạn về chiều cao, chiều rộng của đường bộ bao gồm cầu, hầm, bến phà, đường bộ để các xe kể cả hàng hóa xếp trên xe đi qua được an toàn.</p>
    <p>3. <i>Xe quá tải trọng</i> là phương tiện giao thông cơ giới đường bộ có tổng trọng lượng hoặc có tải trọng trục xe vượt quá tải trọng khai thác cho phép của đường bộ.</p>
    <p>4. <i>Xe quá khổ giới hạn</i> là phương tiện giao thông cơ giới đường bộ có một trong các kích thước bao ngoài (kể cả hàng hóa xếp trên xe) vượt quá khổ giới hạn cho phép.</p>
    <p>5. <i>Hàng siêu trường</i> là hàng không thể tháo rời, khi xếp lên phương tiện vận chuyển có một trong các kích thước thực tế: chiều dài lớn hơn 20,0 m; chiều rộng lớn hơn 2,5 m; chiều cao tính từ mặt đường lớn hơn 4,2 m.</p>
    <p>6. <i>Hàng siêu trọng</i> là hàng không thể tháo rời, có trọng lượng thực tế lớn hơn 32 tấn.</p>
    """)

    articles.append("""
    <p><b>Điều 4. Nguyên tắc chung về lưu hành xe trên đường bộ</b></p>
    <p>1. Chỉ được phép cho xe lưu hành trên đường bộ khi tải trọng trục xe, tổng trọng lượng và kích thước bao của xe không vượt quá giới hạn quy định, trừ trường hợp có Giấy phép lưu hành xe do cơ quan có thẩm quyền cấp.</p>
    <p>2. Nghiêm cấm mọi hành vi tự ý cơi nới, thay đổi kích thước thùng xe, chở hàng vượt quá tải trọng, khổ giới hạn gây hư hỏng kết cấu hạ tầng giao thông.</p>
    """)

    # Chương II: Quy định về tải trọng và khổ giới hạn đường bộ (Điều 5 - Điều 12)
    articles.append("""
    <h3>CHƯƠNG II: TẢI TRỌNG VÀ KHỔ GIỚI HẠN CỦA ĐƯỜNG BỘ</h3>
    <p><b>Điều 5. Tải trọng trục xe cho phép</b></p>
    <p>Tải trọng trục xe không được vượt quá các giới hạn sau:</p>
    <p>1. Trục đơn: Tải trọng trục xe không quá 10,0 tấn/trục.</p>
    <p>2. Cụm trục kép (hai trục xe), phụ thuộc vào khoảng cách d giữa hai tâm trục:</p>
    <p>a) Trường hợp d dưới 1,0 m: Tải trọng cụm trục không quá 11,0 tấn;</p>
    <p>b) Trường hợp 1,0 m đến dưới 1,3 m: Tải trọng cụm trục không quá 16,0 tấn;</p>
    <p>c) Trường hợp d từ 1,3 m trở lên: Tải trọng cụm trục không quá 18,0 tấn.</p>
    <p>3. Cụm trục ba, phụ thuộc vào khoảng cách d giữa hai tâm trục liền kề:</p>
    <p>a) Trường hợp d dưới 1,3 m: Tải trọng cụm trục không quá 21,0 tấn;</p>
    <p>b) Trường hợp d từ 1,3 m trở lên: Tải trọng cụm trục không quá 24,0 tấn.</p>
    """)

    articles.append("""
    <p><b>Điều 6. Tổng trọng lượng cho phép của xe thân liền</b></p>
    <p>1. Xe có tổng số 02 trục: Tổng trọng lượng không quá 16,0 tấn.</p>
    <p>2. Xe có tổng số 03 trục: Tổng trọng lượng không quá 24,0 tấn.</p>
    <p>3. Xe có tổng số 04 trục: Tổng trọng lượng không quá 30,0 tấn.</p>
    <p>4. Xe có tổng số 05 trục trở lên: Tổng trọng lượng không quá 34,0 tấn.</p>
    """)

    articles.append("""
    <p><b>Điều 7. Tổng trọng lượng cho phép của tổ hợp xe đầu kéo kéo sơ mi rơ moóc</b></p>
    <p>1. Tổ hợp xe có tổng số 03 trục: Tổng trọng lượng không quá 26,0 tấn.</p>
    <p>2. Tổ hợp xe có tổng số 04 trục: Tổng trọng lượng không quá 34,0 tấn.</p>
    <p>3. Tổ hợp xe có tổng số 05 trục: Tổng trọng lượng không quá 40,0 tấn (trường hợp cụm trục sau của sơ mi rơ moóc là cụm trục ba thì không quá 44,0 tấn).</p>
    <p>4. Tổ hợp xe có tổng số 06 trục trở lên: Tổng trọng lượng không quá 48,0 tấn.</p>
    """)

    articles.append("""
    <p><b>Điều 8. Tổng trọng lượng cho phép của ô tô kéo rơ moóc</b></p>
    <p>Tổng trọng lượng của đoàn xe gồm ô tô kéo rơ moóc không được vượt quá tổng trọng lượng cho phép theo thiết kế kéo theo của ô tô kéo và không vượt quá 45,0 tấn.</p>
    """)

    articles.append("""
    <p><b>Điều 9. Chiều cao xếp hàng hóa cho phép của xe cơ giới</b></p>
    <p>1. Đối với xe tải thùng hở có mui phủ: Chiều cao xếp hàng hóa tối đa là chiều cao giới hạn của mui phủ theo thiết kế của nhà sản xuất hoặc thiết kế cải tạo đã được phê duyệt.</p>
    <p>2. Đối với xe tải thùng hở không mui: Hàng hóa xếp trên thùng xe không được vượt quá chiều cao sau tính từ điểm cao nhất của mặt đường xe chạy:</p>
    <p>a) Xe có khối lượng chở hàng từ 05 tấn trở lên: Chiều cao xếp hàng không quá 4,2 m;</p>
    <p>b) Xe có khối lượng chở hàng từ 2,5 tấn đến dưới 05 tấn: Chiều cao xếp hàng không quá 3,5 m;</p>
    <p>c) Xe có khối lượng chở hàng dưới 2,5 tấn: Chiều cao xếp hàng không quá 2,8 m.</p>
    <p>3. Đối với xe chuyên dùng và xe chở container: Chiều cao xếp hàng tính từ mặt đường không quá 4,35 m.</p>
    """)

    articles.append("""
    <p><b>Điều 10. Chiều rộng và chiều dài xếp hàng hóa</b></p>
    <p>1. Chiều rộng xếp hàng hóa cho phép trên xe cơ giới không được vượt quá chiều rộng của thùng xe theo thiết kế kỹ thuật.</p>
    <p>2. Chiều dài xếp hàng hóa cho phép không được lớn hơn 1,1 lần chiều dài toàn bộ của xe theo thiết kế và không quá 20,0 m.</p>
    """)

    articles.append("""
    <p><b>Điều 11. Khổ giới hạn của đường bộ</b></p>
    <p>1. Chiều cao tĩnh không giới hạn của đường bộ là 4,75 m đối với đường cao tốc, quốc lộ, đường tỉnh và tối thiểu 4,5 m đối với các cấp đường khác.</p>
    <p>2. Chiều rộng làn xe tiêu chuẩn từ 3,5 m đến 3,75 m đối với đường cao tốc và từ 3,0 m đến 3,5 m đối với các tuyến đường thông thường.</p>
    """)

    articles.append("""
    <p><b>Điều 12. Công bố tải trọng và khổ giới hạn của đường bộ</b></p>
    <p>Cơ quan quản lý đường bộ có trách nhiệm công bố định kỳ và cập nhật liên tục danh mục tải trọng cầu đường, khổ giới hạn hầm, cầu trên hệ thống cổng thông tin điện tử.</p>
    """)

    # Chương III: Cấp giấy phép lưu hành xe quá tải trọng, quá khổ giới hạn (Điều 13 - Điều 25)
    articles.append("""
    <h3>CHƯƠNG III: CẤP GIẤY PHÉP LƯU HÀNH XE QUÁ TẢI TRỌNG, QUÁ KHỔ GIỚI HẠN</h3>
    <p><b>Điều 13. Điều kiện cấp Giấy phép lưu hành xe</b></p>
    <p>1. Chỉ cấp Giấy phép lưu hành xe quá tải trọng, xe quá khổ giới hạn trong trường hợp vận chuyển hàng không thể tháo rời hoặc phục vụ an ninh, quốc phòng, công trình trọng điểm quốc gia.</p>
    <p>2. Tuyến đường lưu hành phải có kết cấu hạ tầng cầu đường đáp ứng được khả năng chịu tải hoặc đã được khảo sát, gia cường bảo đảm an toàn.</p>
    """)

    articles.append("""
    <p><b>Điều 14. Thẩm quyền cấp Giấy phép lưu hành xe</b></p>
    <p>1. Cục Đường bộ Việt Nam hoặc Khu Quản lý đường bộ cấp phép cho các hành trình lưu hành đi qua hai tỉnh, thành phố trực thuộc Trung ương trở lên.</p>
    <p>2. Sở Quản lý chuyên ngành cấp tỉnh cấp phép cho hành trình lưu hành trong phạm vi địa bàn tỉnh.</p>
    """)

    articles.append("""
    <p><b>Điều 15. Hồ sơ đề nghị cấp Giấy phép lưu hành xe</b></p>
    <p>1. Đơn đề nghị cấp Giấy phép lưu hành xe theo mẫu quy định.</p>
    <p>2. Bản sao Giấy đăng ký xe, Giấy chứng nhận kiểm định an toàn kỹ thuật của xe, rơ moóc.</p>
    <p>3. Phương án vận chuyển, sơ đồ vị trí xếp hàng hóa và phương án gia cường đường bộ (nếu thuộc trường hợp phải khảo sát cầu đường).</p>
    """)

    articles.append("""
    <p><b>Điều 16. Thời hạn giải quyết thủ tục cấp phép</b></p>
    <p>Trong thời hạn 02 ngày làm việc kể từ ngày nhận đủ hồ sơ hợp lệ. Trường hợp phải khảo sát cầu đường, thời hạn không quá 10 ngày làm việc.</p>
    """)

    articles.append("""
    <p><b>Điều 17. Hiệu lực của Giấy phép lưu hành xe</b></p>
    <p>Giấy phép lưu hành xe được cấp theo từng chuyến hoặc có thời hạn tối đa không quá 60 ngày đối với các phương tiện vận chuyển hàng trên tuyến đường cố định đáp ứng yêu cầu kỹ thuật.</p>
    """)

    articles.append("""
    <p><b>Điều 18. Trách nhiệm của chủ xe, lái xe khi lưu hành xe quá tải, quá khổ</b></p>
    <p>Phải mang theo Giấy phép lưu hành xe bản chính (hoặc bản điện tử có mã xác thực), tuân thủ đúng tuyến đường, thời gian lưu hành và các biện pháp bảo đảm an toàn ghi trong Giấy phép.</p>
    """)

    articles.append("""
    <p><b>Điều 19. Bố trí xe hỗ trợ dẫn đường, hộ tống</b></p>
    <p>Trường hợp xe có kích thước chiều rộng vượt quá 3,5 m hoặc chiều dài vượt quá 25 m, phải có xe hỗ trợ dẫn đường đi trước cảnh báo và bố trí đèn tín hiệu ưu tiên.</p>
    """)

    articles.append("""
    <p><b>Điều 20. Khảo sát, kiểm định và thử tải cầu đường</b></p>
    <p>Khi tổng trọng lượng của đoàn xe vượt quá khả năng chịu tải thiết kế của cầu, bắt buộc phải thuê đơn vị tư vấn độc lập thực hiện khảo sát, đánh giá và lập phương án gia cường.</p>
    """)

    articles.append("""
    <p><b>Điều 21. Quy định đối với xe bánh xích</b></p>
    <p>Xe bánh xích tự hành không được chạy trực tiếp trên mặt đường nhựa, đường bê tông xi măng. Khi di chuyển trên đường bộ phải chở trên rơ moóc chuyên dùng hoặc có biện pháp lót đường bảo vệ kết cấu mặt đường.</p>
    """)

    articles.append("""
    <p><b>Điều 22. Giám sát tải trọng tự động bằng cân thông minh</b></p>
    <p>Áp dụng hệ thống cân tải trọng tự động tốc độ cao (WIM) lắp đặt cố định trên các tuyến đường bộ để ghi nhận và phạt nguội các phương tiện vi phạm tải trọng.</p>
    """)

    articles.append("""
    <p><b>Điều 23. Đình chỉ lưu hành và xử lý vi phạm</b></p>
    <p>Xe lưu hành sai tuyến đường, sai thời gian hoặc chở quá tải trọng so với mức ghi trong Giấy phép lưu hành bị đình chỉ lưu hành ngay và xử phạt theo quy định.</p>
    """)

    articles.append("""
    <p><b>Điều 24. Thu hồi Giấy phép lưu hành xe</b></p>
    <p>Giấy phép lưu hành xe bị thu hồi khi phát hiện hồ sơ xin cấp phép có thông tin gian dối hoặc xe gây tai nạn, sập cầu đường do lỗi chở quá tải.</p>
    """)

    articles.append("""
    <p><b>Điều 25. Phí thẩm định và chi phí gia cường đường bộ</b></p>
    <p>Tổ chức, cá nhân xin cấp Giấy phép lưu hành chịu trách nhiệm chi trả phí thẩm định hồ sơ và toàn bộ chi phí khảo sát, gia cường công trình đường bộ (nếu có).</p>
    """)

    # Chương IV: Điều khoản thi hành (Điều 26 - Điều 31)
    articles.append("""
    <h3>CHƯƠNG IV: ĐIỀU KHOẢN THI HÀNH</h3>
    <p><b>Điều 26. Trách nhiệm của Cục Đường bộ Việt Nam</b></p>
    <p>Chỉ đạo, hướng dẫn nghiệp vụ cấp Giấy phép lưu hành xe, kiểm tra tải trọng xe và quản lý cơ sở dữ liệu cấp phép toàn quốc.</p>
    """)

    articles.append("""
    <p><b>Điều 27. Trách nhiệm của Sở Quản lý chuyên ngành cấp tỉnh</b></p>
    <p>Tổ chức tiếp nhận, giải quyết hồ sơ cấp Giấy phép lưu hành xe trên địa bàn; thanh tra, kiểm tra và bảo vệ kết cấu hạ tầng đường bộ địa phương.</p>
    """)

    articles.append("""
    <p><b>Điều 28. Trách nhiệm của lực lượng Thanh tra giao thông</b></p>
    <p>Phối hợp với Cảnh sát giao thông kiểm soát tải trọng phương tiện tại các trạm kiểm tra tải trọng xe cố định và lưu động.</p>
    """)

    articles.append("""
    <p><b>Điều 29. Ứng dụng dịch vụ công trực tuyến</b></p>
    <p>Toàn bộ thủ tục nộp hồ sơ, thẩm định và cấp Giấy phép lưu hành xe quá tải, quá khổ được thực hiện trên môi trường điện tử Cổng Dịch vụ công quốc gia.</p>
    """)

    articles.append("""
    <p><b>Điều 30. Điều khoản chuyển tiếp</b></p>
    <p>Giấy phép lưu hành xe đã được cấp trước ngày Thông tư này có hiệu lực tiếp tục có giá trị sử dụng cho đến hết thời hạn ghi trong Giấy phép.</p>
    """)

    articles.append("""
    <p><b>Điều 31. Hiệu lực thi hành</b></p>
    <p>Thông tư này có hiệu lực thi hành kể từ ngày 01 tháng 07 năm 2025.</p>
    """)

    html_content = f"""<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <title>Thông tư 12/2025/TT-BXD quy định về tải trọng, khổ giới hạn đường bộ</title>
</head>
<body>
<div class="doc-header">
    <p><b>BỘ XÂY DỰNG</b><br>Số: 12/2025/TT-BXD</p>
    <p><b>CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM</b><br>Độc lập - Tự do - Hạnh phúc</p>
    <p><i>Hà Nội, ngày 15 tháng 05 năm 2025</i></p>
    <h2>THÔNG TƯ</h2>
    <h3>Quy định về tải trọng, khổ giới hạn của đường bộ; lưu hành xe quá tải trọng, xe quá khổ giới hạn, xe bánh xích trên đường bộ</h3>
</div>
<div class="doc-body">
{''.join(articles)}
</div>
</body>
</html>"""
    out_file = RAW_DIR / "12_2025_TT_BXD.html"
    out_file.write_text(html_content, encoding="utf-8")
    print(f"Generated {out_file.name} with {len(articles)} articles ({len(html_content)} bytes)")


def generate_19_2026():
    # Thông tư số 19/2026/TT-BXD: 3 Điều (Amendment Source)
    articles = []

    articles.append("""
    <p><b>Điều 1. Sửa đổi, bổ sung một số điều của Thông tư số 12/2025/TT-BXD ngày 15 tháng 05 năm 2025 của Bộ trưởng Bộ Xây dựng quy định về tải trọng, khổ giới hạn của đường bộ; lưu hành xe quá tải trọng, xe quá khổ giới hạn, xe bánh xích trên đường bộ</b></p>
    <p>1. Sửa đổi, bổ sung Khoản 2 Điều 5 về tải trọng cụm trục kép:</p>
    <p>Đối với cụm trục kép có khoảng cách giữa hai tâm trục từ 1,3 m trở lên và được trang bị hệ thống treo khí nén (bóng hơi) đạt chuẩn chất lượng an toàn kỹ thuật, tải trọng cụm trục cho phép tối đa được áp dụng mức 19,0 tấn (tăng 1,0 tấn so với mức tiêu chuẩn 18,0 tấn của hệ thống treo nhíp thông thường).</p>
    <p>2. Sửa đổi, bổ sung Khoản 3 Điều 7 về tổng trọng lượng tổ hợp xe đầu kéo kéo sơ mi rơ moóc:</p>
    <p>Tổ hợp xe có tổng số 05 trục trở lên, trong đó cụm trục sau của sơ mi rơ moóc là cụm trục ba và toàn bộ các trục đều sử dụng hệ thống treo khí nén, tổng trọng lượng cho phép tối đa khi lưu hành trên mạng lưới đường cao tốc đạt chuẩn được nâng lên không quá 45,0 tấn.</p>
    <p>3. Sửa đổi, bổ sung Điều 16 về thủ tục cấp Giấy phép lưu hành điện tử:</p>
    <p>Thời hạn giải quyết thủ tục cấp Giấy phép lưu hành xe quá tải, quá khổ trực tuyến toàn trình được rút ngắn xuống không quá 24 giờ làm việc kể từ thời điểm tiếp nhận hồ sơ điện tử hợp lệ đối với các tuyến đường đã có sẵn dữ liệu tải trọng số hóa.</p>
    """)

    articles.append("""
    <p><b>Điều 2. Trách nhiệm thi hành</b></p>
    <p>Cục trưởng Cục Đường bộ Việt Nam, Thủ trưởng các cơ quan, đơn vị thuộc Bộ Xây dựng, Giám đốc Sở chuyên ngành các tỉnh, thành phố trực thuộc Trung ương chịu trách nhiệm tổ chức thực hiện Thông tư này.</p>
    """)

    articles.append("""
    <p><b>Điều 3. Hiệu lực thi hành</b></p>
    <p>Thông tư này có hiệu lực thi hành kể từ ngày 01 tháng 07 năm 2026.</p>
    """)

    html_content = f"""<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <title>Thông tư 19/2026/TT-BXD sửa đổi bổ sung Thông tư 12/2025/TT-BXD về tải trọng đường bộ</title>
</head>
<body>
<div class="doc-header">
    <p><b>BỘ XÂY DỰNG</b><br>Số: 19/2026/TT-BXD</p>
    <p><b>CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM</b><br>Độc lập - Tự do - Hạnh phúc</p>
    <p><i>Hà Nội, ngày 08 tháng 05 năm 2026</i></p>
    <h2>THÔNG TƯ</h2>
    <h3>Sửa đổi, bổ sung một số điều của Thông tư số 12/2025/TT-BXD về tải trọng, khổ giới hạn đường bộ</h3>
</div>
<div class="doc-body">
{''.join(articles)}
</div>
</body>
</html>"""
    out_file = RAW_DIR / "19_2026_TT_BXD.html"
    out_file.write_text(html_content, encoding="utf-8")
    print(f"Generated {out_file.name} with {len(articles)} articles ({len(html_content)} bytes)")


def generate_26_vbhn():
    # Văn bản hợp nhất số 26/VBHN-BXD (Consolidated Reference)
    # Hợp nhất Thông tư 12/2025 và Thông tư 19/2026: 31 Điều
    articles = []

    articles.append("""
    <h3>CHƯƠNG I: QUY ĐỊNH CHUNG</h3>
    <p><b>Điều 1. Phạm vi điều chỉnh</b></p>
    <p>1. Văn bản này hợp nhất quy định về tải trọng, khổ giới hạn của đường bộ; công bố tải trọng và khổ giới hạn của đường bộ; điều kiện, trình tự, thủ tục cấp Giấy phép lưu hành cho xe quá tải trọng, xe quá khổ giới hạn, xe bánh xích trên đường bộ.</p>
    <p>2. Quy định về vận chuyển hàng siêu trường, siêu trọng trên mạng lưới đường bộ.</p>
    """)

    articles.append("""
    <p><b>Điều 2. Đối tượng áp dụng</b></p>
    <p>Áp dụng đối với cơ quan, tổ chức, cá nhân liên quan đến quản lý, khai thác đường bộ và chủ phương tiện, người lái xe, người thuê vận tải, người xếp dỡ hàng hóa trên xe ô tô tham gia giao thông đường bộ.</p>
    """)

    articles.append("""
    <p><b>Điều 3. Giải thích từ ngữ</b></p>
    <p>Quy định chi tiết các khái niệm tải trọng đường bộ, khổ giới hạn đường bộ, xe quá tải trọng, xe quá khổ giới hạn, hàng siêu trường, hàng siêu trọng.</p>
    """)

    articles.append("""
    <p><b>Điều 4. Nguyên tắc chung về lưu hành xe trên đường bộ</b></p>
    <p>Chỉ được lưu hành khi đáp ứng quy định về tải trọng, kích thước bao ngoài, trừ trường hợp có Giấy phép lưu hành do cơ quan có thẩm quyền cấp.</p>
    """)

    articles.append("""
    <h3>CHƯƠNG II: TẢI TRỌNG VÀ KHỔ GIỚI HẠN CỦA ĐƯỜNG BỘ</h3>
    <p><b>Điều 5. Tải trọng trục xe cho phép</b></p>
    <p>1. Trục đơn: Tải trọng trục xe không quá 10,0 tấn/trục.</p>
    <p>2. Cụm trục kép (hai trục xe):</p>
    <p>a) Khoảng cách d dưới 1,0 m: Không quá 11,0 tấn;</p>
    <p>b) Khoảng cách 1,0 m đến dưới 1,3 m: Không quá 16,0 tấn;</p>
    <p>c) Khoảng cách d từ 1,3 m trở lên: Không quá 18,0 tấn đối với hệ thống treo nhíp thông thường; áp dụng mức tối đa 19,0 tấn đối với xe được trang bị hệ thống treo khí nén (bóng hơi) đạt chuẩn an toàn kỹ thuật <i>(quy định sửa đổi theo Thông tư 19/2026/TT-BXD)</i>.</p>
    <p>3. Cụm trục ba: Khoảng cách d dưới 1,3 m không quá 21,0 tấn; từ 1,3 m trở lên không quá 24,0 tấn.</p>
    """)

    articles.append("""
    <p><b>Điều 6. Tổng trọng lượng cho phép của xe thân liền</b></p>
    <p>Xe 02 trục không quá 16,0 tấn; xe 03 trục không quá 24,0 tấn; xe 04 trục không quá 30,0 tấn; xe 05 trục trở lên không quá 34,0 tấn.</p>
    """)

    articles.append("""
    <p><b>Điều 7. Tổng trọng lượng cho phép của tổ hợp xe đầu kéo kéo sơ mi rơ moóc</b></p>
    <p>1. Tổ hợp xe 03 trục: Không quá 26,0 tấn.</p>
    <p>2. Tổ hợp xe 04 trục: Không quá 34,0 tấn.</p>
    <p>3. Tổ hợp xe 05 trục: Không quá 40,0 tấn (trường hợp cụm trục sau của sơ mi rơ moóc là cụm trục ba không quá 44,0 tấn; nâng lên mức không quá 45,0 tấn khi toàn bộ các trục dùng hệ thống treo khí nén lưu hành trên cao tốc - <i>sửa đổi bởi TT 19/2026/TT-BXD</i>).</p>
    <p>4. Tổ hợp xe 06 trục trở lên: Không quá 48,0 tấn.</p>
    """)

    for idx in range(8, 32):
        if idx == 16:
            articles.append(f"""
    <p><b>Điều {idx}. Thời hạn giải quyết thủ tục cấp phép</b></p>
    <p>Thời hạn giải quyết thủ tục cấp Giấy phép lưu hành xe quá tải, quá khổ trực tuyến toàn trình không quá 24 giờ làm việc đối với các tuyến đường đã có sẵn dữ liệu tải trọng số hóa <i>(sửa đổi bởi TT 19/2026/TT-BXD)</i>; không quá 02 ngày làm việc đối với các trường hợp thông thường và không quá 10 ngày làm việc nếu phải khảo sát cầu đường.</p>
    """)
        elif idx == 31:
            articles.append(f"""
    <p><b>Điều {idx}. Hiệu lực thi hành</b></p>
    <p>Thông tư số 12/2025/TT-BXD có hiệu lực thi hành từ ngày 01/07/2025; các nội dung sửa đổi bổ sung của Thông tư 19/2026/TT-BXD có hiệu lực từ ngày 01/07/2026.</p>
    """)
        else:
            articles.append(f"""
    <p><b>Điều {idx}. Quy định hợp nhất về quản lý tải trọng và lưu hành xe</b></p>
    <p>Nội dung hợp nhất tương ứng theo quy định tại Thông tư số 12/2025/TT-BXD và Thông tư số 19/2026/TT-BXD của Bộ Xây dựng.</p>
    """)

    html_content = f"""<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <title>Văn bản hợp nhất 26/VBHN-BXD về tải trọng, khổ giới hạn đường bộ</title>
</head>
<body>
<div class="doc-header">
    <p><b>BỘ XÂY DỰNG</b><br>Số: 26/VBHN-BXD</p>
    <p><b>CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM</b><br>Độc lập - Tự do - Hạnh phúc</p>
    <p><i>Hà Nội, ngày 02 tháng 06 năm 2026</i></p>
    <h2>VĂN BẢN HỢP NHẤT</h2>
    <h3>Thông tư quy định về tải trọng, khổ giới hạn của đường bộ; lưu hành xe quá tải trọng, xe quá khổ giới hạn, xe bánh xích trên đường bộ</h3>
</div>
<div class="doc-body">
{''.join(articles)}
</div>
</body>
</html>"""
    out_file = RAW_DIR / "26_2026_VBHN_BXD.html"
    out_file.write_text(html_content, encoding="utf-8")
    print(f"Generated {out_file.name} with {len(articles)} articles ({len(html_content)} bytes)")

generate_12_2025()
generate_19_2026()
generate_26_vbhn()
