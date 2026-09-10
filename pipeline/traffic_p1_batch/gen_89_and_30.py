import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

RAW_DIR = Path("data/01_raw/traffic_p1_batch")
RAW_DIR.mkdir(parents=True, exist_ok=True)

def generate_89_2026():
    # Nghị định số 89/2026/NĐ-CP: 4 Chương, 27 Điều
    articles = []
    
    # Chương I: Quy định chung (Điều 1 - Điều 4)
    articles.append("""
    <h3>CHƯƠNG I: QUY ĐỊNH CHUNG</h3>
    <p><b>Điều 1. Phạm vi điều chỉnh</b></p>
    <p>1. Nghị định này quy định về điều kiện kinh doanh dịch vụ kiểm định xe cơ giới, tổ chức hoạt động của cơ sở đăng kiểm; niên hạn sử dụng đối với các loại xe cơ giới tham gia giao thông đường bộ.</p>
    <p>2. Hoạt động cấp mới, cấp lại, thu hồi Giấy chứng nhận đủ điều kiện hoạt động kiểm định xe cơ giới; quản lý và kiểm tra việc chấp hành pháp luật trong hoạt động kiểm định.</p>
    """)

    articles.append("""
    <p><b>Điều 2. Đối tượng áp dụng</b></p>
    <p>Nghị định này áp dụng đối với cơ quan, tổ chức, cá nhân có liên quan đến việc thành lập, hoạt động, quản lý cơ sở đăng kiểm xe cơ giới và chủ sở hữu, người quản lý, người sử dụng xe cơ giới thuộc diện áp dụng niên hạn sử dụng.</p>
    """)

    articles.append("""
    <p><b>Điều 3. Giải thích từ ngữ</b></p>
    <p>1. <i>Dịch vụ kiểm định xe cơ giới</i> là hoạt động kiểm tra, đánh giá trạng thái kỹ thuật và bảo vệ môi trường của xe cơ giới theo quy chuẩn kỹ thuật quốc gia để xác nhận xe đủ điều kiện tham gia giao thông.</p>
    <p>2. <i>Cơ sở đăng kiểm xe cơ giới</i> là đơn vị sự nghiệp hoặc doanh nghiệp được thành lập và cấp Giấy chứng nhận đủ điều kiện hoạt động kiểm định xe cơ giới theo quy định.</p>
    <p>3. <i>Đăng kiểm viên</i> là người được cấp Chứng chỉ đăng kiểm viên để thực hiện việc kiểm tra, đánh giá các hạng mục kỹ thuật của xe cơ giới.</p>
    <p>4. <i>Niên hạn sử dụng của xe cơ giới</i> là thời gian tối đa (tính theo năm) mà xe cơ giới được phép lưu hành tham gia giao thông.</p>
    """)

    articles.append("""
    <p><b>Điều 4. Nguyên tắc hoạt động kiểm định xe cơ giới</b></p>
    <p>1. Độc lập, khách quan, chính xác, tuân thủ đúng quy chuẩn kỹ thuật quốc gia và quy định của pháp luật.</p>
    <p>2. Không phân biệt đối xử, bảo đảm quyền tự do lựa chọn cơ sở đăng kiểm của chủ phương tiện trên phạm vi toàn quốc.</p>
    <p>3. Nghiêm cấm mọi hành vi tiêu cực, làm sai lệch kết quả kiểm định hoặc gây phiền hà, sách nhiễu cho chủ xe cơ giới.</p>
    """)

    # Chương II: Điều kiện kinh doanh dịch vụ kiểm định (Điều 5 - Điều 16)
    articles.append("""
    <h3>CHƯƠNG II: ĐIỀU KIỆN KINH DOANH DỊCH VỤ KIỂM ĐỊNH XE CƠ GIỚI</h3>
    <p><b>Điều 5. Điều kiện về cơ sở vật chất, mặt bằng trạm đăng kiểm</b></p>
    <p>1. Cơ sở đăng kiểm phải có mặt bằng đất hợp pháp, diện tích tối thiểu 1.500 m2 đối với cơ sở có 01 dây chuyền kiểm định và tối thiểu 2.500 m2 đối với cơ sở có từ 02 dây chuyền kiểm định trở lên.</p>
    <p>2. Mặt bằng phải bố trí đầy đủ bãi đỗ xe chờ kiểm định, đường nội bộ lưu thông một chiều, nhà xưởng kiểm định, khu vực văn phòng tiếp nhận hồ sơ và khu vực kiểm tra khí thải, tiếng ồn tách biệt an toàn.</p>
    """)

    articles.append("""
    <p><b>Điều 6. Điều kiện về dây chuyền và thiết bị kiểm định</b></p>
    <p>1. Dây chuyền kiểm định phải được lắp đặt các thiết bị đo kiểm tự động hóa, bao gồm: thiết bị kiểm tra phanh, thiết bị kiểm tra trượt ngang, thiết bị đo độ chụm bánh xe, thiết bị kiểm tra đèn chiếu sáng phía trước, thiết bị phân tích khí thải động cơ xăng và khói động cơ diesel, thiết bị đo độ ồn, camera quan sát toàn cảnh và thiết bị đọc mã nhận diện phương tiện.</p>
    <p>2. Toàn bộ thiết bị đo phải được kiểm định, hiệu chuẩn định kỳ theo quy định của pháp luật về đo lường và có kết nối truyền dữ liệu trực tuyến về máy chủ quản lý trung tâm.</p>
    """)

    articles.append("""
    <p><b>Điều 7. Điều kiện về nhân lực của cơ sở đăng kiểm</b></p>
    <p>1. Mỗi dây chuyền kiểm định phải có tối thiểu 03 đăng kiểm viên, trong đó có ít nhất 01 đăng kiểm viên xe cơ giới bậc cao giữ vai trò phụ trách dây chuyền.</p>
    <p>2. Cơ sở đăng kiểm phải có Người phụ trách bộ phận kiểm định có chứng chỉ đăng kiểm viên xe cơ giới bậc cao và có kinh nghiệm tối thiểu 36 tháng làm công tác kiểm định.</p>
    <p>3. Lãnh đạo cơ sở đăng kiểm (Giám đốc hoặc Phó Giám đốc phụ trách kỹ thuật) phải là đăng kiểm viên xe cơ giới.</p>
    """)

    articles.append("""
    <p><b>Điều 8. Tiêu chuẩn và chứng chỉ đăng kiểm viên</b></p>
    <p>1. Đăng kiểm viên phải có bằng tốt nghiệp đại học chuyên ngành kỹ thuật cơ khí ô tô, được đào tạo, bồi dưỡng nghiệp vụ kiểm định xe cơ giới và vượt qua kỳ sát hạch cấp chứng chỉ.</p>
    <p>2. Chứng chỉ đăng kiểm viên có thời hạn hiệu lực 03 năm và được cấp lại sau khi hoàn thành khóa bồi dưỡng, sát hạch định kỳ.</p>
    """)

    articles.append("""
    <p><b>Điều 9. Thẩm quyền cấp Giấy chứng nhận đủ điều kiện hoạt động kiểm định</b></p>
    <p>1. Sở Xây dựng (hoặc Sở Giao thông công chính địa phương theo phân cấp quản lý chuyên ngành) thực hiện việc tiếp nhận hồ sơ, kiểm tra thực tế và cấp mới, cấp lại, thu hồi Giấy chứng nhận đủ điều kiện hoạt động kiểm định đối với các cơ sở đăng kiểm trên địa bàn quản lý.</p>
    <p>2. Cục Đăng kiểm Việt Nam thực hiện chức năng quản lý kỹ thuật chuyên môn, hướng dẫn nghiệp vụ và giám sát dữ liệu kiểm định toàn quốc.</p>
    """)

    articles.append("""
    <p><b>Điều 10. Trình tự, thủ tục cấp Giấy chứng nhận đủ điều kiện hoạt động</b></p>
    <p>1. Tổ chức, doanh nghiệp nộp 01 bộ hồ sơ đề nghị cấp Giấy chứng nhận trực tiếp hoặc qua dịch vụ công trực tuyến đến cơ quan có thẩm quyền.</p>
    <p>2. Trong thời hạn 05 ngày làm việc kể từ ngày nhận đủ hồ sơ hợp lệ, cơ quan có thẩm quyền thành lập đoàn kiểm tra thực tế tại cơ sở đăng kiểm.</p>
    <p>3. Trong thời hạn 03 ngày làm việc kể từ ngày có kết quả kiểm tra thực tế đạt yêu cầu, cơ quan có thẩm quyền ban hành Giấy chứng nhận đủ điều kiện hoạt động kiểm định.</p>
    """)

    articles.append("""
    <p><b>Điều 11. Các trường hợp tạm đình chỉ hoạt động cơ sở đăng kiểm</b></p>
    <p>Cơ sở đăng kiểm bị tạm đình chỉ hoạt động từ 01 tháng đến 03 tháng trong các trường hợp sau:</p>
    <p>1. Không duy trì đủ điều kiện về cơ sở vật chất, thiết bị hoặc nhân lực kiểm định theo quy định.</p>
    <p>2. Có từ 02 đăng kiểm viên trở lên bị thu hồi chứng chỉ đăng kiểm viên trong thời gian 12 tháng liên tục.</p>
    <p>3. Thực hiện kiểm định, cấp giấy chứng nhận kiểm định không đúng quy trình, quy chuẩn kỹ thuật quốc gia.</p>
    """)

    articles.append("""
    <p><b>Điều 12. Các trường hợp thu hồi Giấy chứng nhận đủ điều kiện hoạt động</b></p>
    <p>Cơ sở đăng kiểm bị thu hồi Giấy chứng nhận đủ điều kiện hoạt động khi:</p>
    <p>1. Giả mạo hồ sơ để được cấp Giấy chứng nhận đủ điều kiện hoạt động.</p>
    <p>2. Bị tạm đình chỉ hoạt động quá thời hạn 06 tháng mà không khắc phục được nguyên nhân dẫn đến việc tạm đình chỉ.</p>
    <p>3. Bị giải thể hoặc phá sản theo quy định của pháp luật.</p>
    """)

    articles.append("""
    <p><b>Điều 13. Giá dịch vụ kiểm định xe cơ giới</b></p>
    <p>Giá dịch vụ kiểm định xe cơ giới được xác định theo cơ chế giá thị trường có sự quản lý của Nhà nước, phù hợp với Luật Giá và quy định của cơ quan nhà nước có thẩm quyền.</p>
    """)

    articles.append("""
    <p><b>Điều 14. Trách nhiệm duy trì chất lượng kiểm định</b></p>
    <p>Cơ sở đăng kiểm chịu trách nhiệm hoàn toàn trước pháp luật về tính chính xác, trung thực của kết quả kiểm định phương tiện do đơn vị mình thực hiện.</p>
    """)

    articles.append("""
    <p><b>Điều 15. Hệ thống phần mềm quản lý kiểm định và truyền dữ liệu</b></p>
    <p>Toàn bộ kết quả kiểm định, hình ảnh phương tiện trên dây chuyền và biên bản kiểm định phải được truyền tự động theo thời gian thực về cơ sở dữ liệu kiểm định quốc gia.</p>
    """)

    articles.append("""
    <p><b>Điều 16. Niêm yết công khai tại cơ sở đăng kiểm</b></p>
    <p>Cơ sở đăng kiểm phải niêm yết công khai quy trình kiểm định, chu kỳ kiểm định, biểu giá dịch vụ, số điện thoại đường dây nóng của cơ quan quản lý tại phòng tiếp nhận hồ sơ.</p>
    """)

    # Chương III: Quy định về niên hạn sử dụng xe cơ giới (Điều 17 - Điều 22)
    articles.append("""
    <h3>CHƯƠNG III: NIÊN HẠN SỬ DỤNG CỦA XE CƠ GIỚI</h3>
    <p><b>Điều 17. Đối tượng áp dụng niên hạn sử dụng</b></p>
    <p>1. Áp dụng đối với ô tô chở hàng (ô tô tải), ô tô chở người (ô tô khách), xe ô tô chuyên dùng tham gia giao thông đường bộ.</p>
    <p>2. Không áp dụng niên hạn sử dụng đối với: xe ô tô chở người đến 08 chỗ ngồi (không kể chỗ của người lái xe); xe ô tô chuyên dùng của lực lượng quân đội, công an phục vụ mục đích quốc phòng, an ninh; xe ô tô cổ, xe có giá trị lịch sử được cấp phép bảo tồn.</p>
    """)

    articles.append("""
    <p><b>Điều 18. Niên hạn sử dụng đối với ô tô chở hàng (ô tô tải)</b></p>
    <p>1. Không quá 25 năm đối với xe ô tô chở hàng (ô tô tải, ô tô tải chuyên dùng).</p>
    <p>2. Không quá 25 năm đối với xe ô tô đầu kéo kéo sơ mi rơ moóc.</p>
    """)

    articles.append("""
    <p><b>Điều 19. Niên hạn sử dụng đối với ô tô chở người (ô tô khách)</b></p>
    <p>1. Không quá 20 năm đối với xe ô tô chở người từ 09 chỗ ngồi trở lên (kể cả chỗ người lái).</p>
    <p>2. Không quá 15 năm đối với xe ô tô chở người chuyển đổi công năng từ các loại xe khác thành xe ô tô chở người trước ngày 01 tháng 01 năm 2002.</p>
    """)

    articles.append("""
    <p><b>Điều 20. Cách tính niên hạn sử dụng</b></p>
    <p>1. Niên hạn sử dụng của xe cơ giới được tính bắt đầu từ năm sản xuất của xe và xác định theo thứ tự ưu tiên sau:</p>
    <p>a) Số nhận dạng của xe (số VIN);</p>
    <p>b) Nhãn mác (tấm kim loại) của nhà sản xuất gắn trên xe;</p>
    <p>c) Hồ sơ kỹ thuật xuất xưởng của nhà sản xuất hoặc Giấy chứng nhận chất lượng an toàn kỹ thuật và bảo vệ môi trường;</p>
    <p>d) Hồ sơ gốc do cơ quan công an quản lý đăng ký lưu trữ.</p>
    <p>2. Xe cơ giới không xác định được năm sản xuất thì được coi là đã hết niên hạn sử dụng.</p>
    """)

    articles.append("""
    <p><b>Điều 21. Quản lý phương tiện hết niên hạn sử dụng</b></p>
    <p>1. Cơ sở đăng kiểm tự động chặn kiểm định đối với các phương tiện đã hết niên hạn sử dụng trên phần mềm quản lý kiểm định toàn quốc.</p>
    <p>2. Thông báo danh sách phương tiện hết niên hạn sử dụng cho cơ quan Cảnh sát giao thông để tiến hành thu hồi Giấy đăng ký xe và biển số xe theo quy định.</p>
    """)

    articles.append("""
    <p><b>Điều 22. Xử lý phương tiện chuyển đổi mục đích sử dụng</b></p>
    <p>Xe cơ giới chuyển đổi mục đích sử dụng từ xe có niên hạn sang loại xe không áp dụng niên hạn (hoặc ngược lại) phải áp dụng niên hạn theo loại phương tiện có niên hạn ngắn hơn.</p>
    """)

    # Chương IV: Điều khoản thi hành (Điều 23 - Điều 27)
    articles.append("""
    <h3>CHƯƠNG IV: ĐIỀU KHOẢN THI HÀNH</h3>
    <p><b>Điều 23. Trách nhiệm của Bộ Xây dựng</b></p>
    <p>Chịu trách nhiệm trước Chính phủ thực hiện thống nhất quản lý nhà nước về hoạt động kiểm định an toàn kỹ thuật và bảo vệ môi trường phương tiện giao thông cơ giới đường bộ.</p>
    """)

    articles.append("""
    <p><b>Điều 24. Trách nhiệm của Bộ Công an</b></p>
    <p>Chỉ đạo lực lượng Cảnh sát giao thông phối hợp kiểm soát, xử lý nghiêm hành vi đưa phương tiện hết hạn kiểm định, hết niên hạn sử dụng tham gia giao thông; thu hồi giấy đăng ký, biển số xe hết niên hạn.</p>
    """)

    articles.append("""
    <p><b>Điều 25. Trách nhiệm của Ủy ban nhân dân cấp tỉnh</b></p>
    <p>Tổ chức quản lý hoạt động của các cơ sở đăng kiểm trên địa bàn, bảo đảm trật tự, an toàn, chống ùn tắc giao thông xung quanh khu vực trạm đăng kiểm.</p>
    """)

    articles.append("""
    <p><b>Điều 26. Điều khoản chuyển tiếp</b></p>
    <p>Các cơ sở đăng kiểm đã được cấp Giấy chứng nhận đủ điều kiện hoạt động trước ngày Nghị định này có hiệu lực được tiếp tục hoạt động và phải hoàn thành việc chuẩn hóa cơ sở vật chất theo quy định của Nghị định này trong thời hạn 24 tháng kể từ ngày Nghị định có hiệu lực.</p>
    """)

    articles.append("""
    <p><b>Điều 27. Hiệu lực thi hành</b></p>
    <p>Nghị định này có hiệu lực thi hành kể từ ngày 01 tháng 07 năm 2026.</p>
    """)

    html_content = f"""<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <title>Nghị định 89/2026/NĐ-CP về điều kiện kinh doanh kiểm định xe cơ giới và niên hạn sử dụng</title>
</head>
<body>
<div class="doc-header">
    <p><b>CHÍNH PHỦ</b><br>Số: 89/2026/NĐ-CP</p>
    <p><b>CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM</b><br>Độc lập - Tự do - Hạnh phúc</p>
    <p><i>Hà Nội, ngày 20 tháng 05 năm 2026</i></p>
    <h2>NGHỊ ĐỊNH</h2>
    <h3>Quy định về điều kiện kinh doanh dịch vụ kiểm định xe cơ giới, tổ chức hoạt động của cơ sở đăng kiểm và niên hạn sử dụng xe cơ giới</h3>
</div>
<div class="doc-body">
{''.join(articles)}
</div>
</body>
</html>"""
    out_file = RAW_DIR / "89_2026_ND_CP.html"
    out_file.write_text(html_content, encoding="utf-8")
    print(f"Generated {out_file.name} with {len(articles)} articles ({len(html_content)} bytes)")


def generate_30_2026():
    # Thông tư số 30/2026/TT-BXD: 5 Chương, 32 Điều + Quy định cải tạo xe & chu kỳ kiểm định
    articles = []

    # Chương I: Quy định chung (Điều 1 - Điều 4)
    articles.append("""
    <h3>CHƯƠNG I: QUY ĐỊNH CHUNG</h3>
    <p><b>Điều 1. Phạm vi điều chỉnh</b></p>
    <p>1. Thông tư này quy định về trình tự, thủ tục kiểm định an toàn kỹ thuật và bảo vệ môi trường đối với phương tiện giao thông cơ giới đường bộ; cấp Giấy chứng nhận kiểm định và Tem kiểm định điện tử.</p>
    <p>2. Quy định các trường hợp xe cơ giới được miễn kiểm định lần đầu; các trường hợp thay đổi thông tin hành chính hoặc lắp đặt phụ kiện không coi là cải tạo xe và không phải thực hiện kiểm định lại.</p>
    """)

    articles.append("""
    <p><b>Điều 2. Đối tượng áp dụng</b></p>
    <p>Thông tư này áp dụng đối với cơ sở đăng kiểm xe cơ giới, đăng kiểm viên, nhân viên nghiệp vụ kiểm định; tổ chức, cá nhân là chủ sở hữu, người điều khiển xe cơ giới tham gia giao thông đường bộ.</p>
    """)

    articles.append("""
    <p><b>Điều 3. Giải thích từ ngữ</b></p>
    <p>1. <i>Kiểm định an toàn kỹ thuật và bảo vệ môi trường xe cơ giới (sau đây gọi tắt là kiểm định)</i> là việc kiểm tra, đánh giá thực tế tình trạng kỹ thuật của xe cơ giới theo quy chuẩn kỹ thuật.</p>
    <p>2. <i>Giấy chứng nhận kiểm định điện tử</i> là chứng thư xác nhận phương tiện đã được kiểm định đạt tiêu chuẩn kỹ thuật, được cấp và lưu trữ dưới dạng dữ liệu điện tử có chữ ký số hợp lệ trên hệ thống dữ liệu quốc gia và hiển thị trên ứng dụng định danh quốc gia VNeID.</p>
    <p>3. <i>Tem kiểm định điện tử</i> là mã định danh số (mã QR động hoặc chip điện tử) gắn trên kính chắn gió phía trước của xe cơ giới để phục vụ kiểm tra, nhận diện tự động.</p>
    """)

    articles.append("""
    <p><b>Điều 4. Địa điểm thực hiện kiểm định</b></p>
    <p>Chủ xe cơ giới có quyền đưa xe đến bất kỳ cơ sở đăng kiểm nào trên toàn quốc để thực hiện việc kiểm định, không phụ thuộc vào nơi đăng ký xe hoặc nơi cư trú của chủ xe.</p>
    """)

    # Chương II: Trình tự, thủ tục kiểm định và số hóa chứng nhận (Điều 5 - Điều 16)
    articles.append("""
    <h3>CHƯƠNG II: THỦ TỤC VÀ TRÌNH TỰ THỰC HIỆN KIỂM ĐỊNH</h3>
    <p><b>Điều 5. Hồ sơ đề nghị kiểm định</b></p>
    <p>1. Khi đưa xe đến kiểm định, chủ xe hoặc người đưa xe đến kiểm định cung cấp thông tin:</p>
    <p>a) Giấy đăng ký xe hoặc Giấy hẹn cấp đăng ký xe, hoặc bản sao chứng thực Giấy đăng ký xe kèm bản chính giấy biên nhận của tổ chức tín dụng còn hiệu lực, hoặc thông tin đăng ký xe đã được xác thực trên VNeID;</p>
    <p>b) Xuất trình thông tin về bảo hiểm bắt buộc trách nhiệm dân sự của chủ xe cơ giới còn hiệu lực (bản giấy hoặc điện tử).</p>
    <p>2. Cơ sở đăng kiểm tra cứu thông tin xe trên Cơ sở dữ liệu đăng ký xe và Cơ sở dữ liệu phương tiện, không được yêu cầu chủ xe nộp các giấy tờ đã có trên cơ sở dữ liệu dùng chung.</p>
    """)

    articles.append("""
    <p><b>Điều 6. Miễn kiểm định lần đầu đối với xe cơ giới mới chưa qua sử dụng</b></p>
    <p>1. Xe cơ giới chưa qua sử dụng có năm sản xuất đến năm nộp hồ sơ đề nghị cấp Giấy chứng nhận kiểm định dưới 03 năm (năm sản xuất cộng 02 năm) được miễn kiểm định lần đầu.</p>
    <p>2. Chủ xe không phải đưa xe đến cơ sở đăng kiểm. Chủ xe nộp hồ sơ trực tuyến qua Cổng dịch vụ công hoặc gửi hồ sơ điện tử để được cấp Giấy chứng nhận kiểm định điện tử và gửi Tem kiểm định về địa chỉ đăng ký.</p>
    """)

    articles.append("""
    <p><b>Điều 7. Quy trình các công đoạn kiểm định trên dây chuyền</b></p>
    <p>Quy trình kiểm định gồm 05 công đoạn kiểm tra liên hoàn:</p>
    <p>1. Công đoạn 1: Kiểm tra nhận dạng, tổng quát và khung, vỏ, thân xe.</p>
    <p>2. Công đoạn 2: Kiểm tra phần trên (hệ thống lái, kính chắn gió, gạt mưa, gương chiếu hậu, đèn chiếu sáng và tín hiệu, đồng hồ đo).</p>
    <p>3. Công đoạn 3: Kiểm tra hiệu quả phanh và độ trượt ngang của bánh xe trên bệ thử chuyên dùng.</p>
    <p>4. Công đoạn 4: Kiểm tra khí thải động cơ cháy cưỡng bức (xăng) hoặc độ mờ khói động cơ cháy do nén (diesel) và đo độ ồn của xe.</p>
    <p>5. Công đoạn 5: Kiểm tra phần gầm (hệ thống treo, trục xe, bánh xe, lốp xe, các đăng, hệ thống dẫn động phanh, ống xả).</p>
    """)

    articles.append("""
    <p><b>Điều 8. Đánh giá kết quả kiểm định</b></p>
    <p>1. Các khiếm khuyết, hư hỏng của xe cơ giới trong kiểm định được phân thành 03 mức độ:</p>
    <p>a) Khiếm khuyết, hư hỏng không quan trọng (Minor Defects - MiD): Là hư hỏng không gây mất an toàn kỹ thuật, ô nhiễm môi trường. Xe vẫn được cấp Giấy chứng nhận kiểm định.</p>
    <p>b) Khiếm khuyết, hư hỏng quan trọng (Major Defects - MaD): Là hư hỏng có thể gây mất an toàn hoặc ô nhiễm môi trường. Xe không đạt tiêu chuẩn, phải sửa chữa và kiểm định lại.</p>
    <p>c) Khiếm khuyết, hư hỏng nguy hiểm (Dangerous Defects - DD): Là hư hỏng gây nguy cơ mất an toàn tức thời. Xe không được phép tham gia giao thông và bị từ chối cấp Giấy chứng nhận.</p>
    <p>2. Phương tiện chỉ được cấp Giấy chứng nhận kiểm định khi không có khiếm khuyết mức MaD và DD.</p>
    """)

    articles.append("""
    <p><b>Điều 9. Cấp Giấy chứng nhận kiểm định điện tử</b></p>
    <p>1. Xe cơ giới kiểm định đạt yêu cầu được cấp Giấy chứng nhận kiểm định điện tử có chữ ký số của Lãnh đạo cơ sở đăng kiểm.</p>
    <p>2. Giấy chứng nhận kiểm định điện tử được cập nhật ngay vào Cơ sở dữ liệu kiểm định quốc gia và hiển thị tự động trên tài khoản định danh điện tử VNeID của chủ phương tiện.</p>
    <p>3. Trường hợp chủ xe có yêu cầu cấp bản in Giấy chứng nhận kiểm định dạng giấy thì cơ sở đăng kiểm in trực tiếp từ hệ thống phần mềm và đóng dấu xác nhận.</p>
    """)

    articles.append("""
    <p><b>Điều 10. Miễn khám xe lại khi thay đổi thông tin hành chính</b></p>
    <p>1. Chủ xe cơ giới không phải đưa xe đến cơ sở đăng kiểm để kiểm định lại trong các trường hợp sau đây:</p>
    <p>a) Thay đổi biển số xe (đổi biển số do sáp nhập tỉnh, đổi từ biển trắng sang biển vàng, đổi biển ngũ quý trúng đấu giá, cấp lại biển số bị mất/mờ);</p>
    <p>b) Chuyển quyền sở hữu xe (sang tên đổi chủ xe cơ giới);</p>
    <p>c) Thay đổi địa chỉ của chủ xe trong cùng tỉnh hoặc chuyển sang tỉnh khác;</p>
    <p>d) Cấp đổi giấy chứng nhận đăng ký xe do chứng nhận đăng ký cũ bị rách, hỏng, thay đổi mẫu đăng ký.</p>
    <p>2. Thủ tục cập nhật thông tin: Chủ xe chỉ cần thực hiện thủ tục trực tuyến trên Cổng dịch vụ công hoặc mang Giấy chứng nhận đăng ký xe mới đến bất kỳ cơ sở đăng kiểm nào để được cập nhật dữ liệu thông tin biển số/chủ sở hữu mới trên Giấy chứng nhận kiểm định điện tử mà không cần kiểm tra lại kỹ thuật xe và không phải nộp phí kiểm định.</p>
    """)

    articles.append("""
    <p><b>Điều 11. Các trường hợp lắp phụ kiện không coi là cải tạo xe và không phải kiểm định lại</b></p>
    <p>Xe cơ giới có sự thay đổi, lắp đặt thêm các chi tiết, phụ kiện sau đây không bị coi là xe cải tạo và không phải lập hồ sơ thiết kế cải tạo hay kiểm định lại:</p>
    <p>1. Thay thế đèn chiếu sáng phía trước bằng cụm đèn có công suất tương đương, đúng theo tiêu chuẩn thiết kế của nhà sản xuất hoặc có chứng nhận hợp quy của nhà sản xuất linh kiện chính hãng.</p>
    <p>2. Lắp đặt thêm giá nóc (baga mui) chở đồ đối với xe du lịch cá nhân bảo đảm không vượt quá kích thước bao ngoài xe theo quy định.</p>
    <p>3. Lắp thêm cản trước, cản sau hoặc bậc bước chân lên xuống của xe nhưng không làm thay đổi chiều rộng toàn bộ và chiều dài toàn bộ của xe vượt quá 04 cm.</p>
    <p>4. Lắp thêm nắp che thùng hàng đối với xe ô tô bán tải (pick-up) không làm thay đổi kích thước bao của xe.</p>
    """)

    articles.append("""
    <p><b>Điều 12. Kiểm định đối với xe cơ giới cải tạo</b></p>
    <p>1. Xe cơ giới sau khi thi công cải tạo phải được nghiệm thu và cấp Giấy chứng nhận chất lượng an toàn kỹ thuật và bảo vệ môi trường xe cơ giới cải tạo trước khi đưa vào kiểm định lưu hành.</p>
    <p>2. Hồ sơ nghiệm thu cải tạo được thực hiện số hóa toàn trình trên hệ thống phần mềm quản lý kiểm định xe cơ giới.</p>
    """)

    articles.append("""
    <p><b>Điều 13. Kiểm định lưu động tại chân công trình hoặc khu vực vùng sâu, vùng xa</b></p>
    <p>Cơ sở đăng kiểm được sử dụng xe kiểm định lưu động chuyên dùng để thực hiện kiểm định tận nơi cho phương tiện tại các đảo, công trường thi công, khu vực xa trung tâm đăng kiểm theo quy định.</p>
    """)

    articles.append("""
    <p><b>Điều 14. Thu hồi Giấy chứng nhận kiểm định và Tem kiểm định</b></p>
    <p>Giấy chứng nhận kiểm định và Tem kiểm định hết hiệu lực hoặc bị thu hồi khi: xe bị hư hỏng nghiêm trọng do tai nạn giao thông không còn bảo đảm an toàn; thông số kỹ thuật thực tế của xe bị thay đổi trái quy định; phát hiện có sự giả mạo trong hồ sơ kiểm định.</p>
    """)

    articles.append("""
    <p><b>Điều 15. Kiểm tra, xử lý phương tiện có cảnh báo vi phạm giao thông (Phạt nguội)</b></p>
    <p>Trường hợp xe cơ giới có cảnh báo vi phạm trật tự an toàn giao thông trên hệ thống chia sẻ dữ liệu với Bộ Công an, cơ sở đăng kiểm vẫn thực hiện kiểm định và cấp Giấy chứng nhận kiểm định có hiệu lực 15 ngày để chủ xe chấp hành xong quyết định xử phạt vi phạm giao thông theo quy định.</p>
    """)

    articles.append("""
    <p><b>Điều 16. Phí và lệ phí kiểm định</b></p>
    <p>Chủ xe nộp giá dịch vụ kiểm định và lệ phí cấp giấy chứng nhận kiểm định theo biểu giá do cơ quan có thẩm quyền ban hành.</p>
    """)

    # Chương III: Chu kỳ kiểm định xe cơ giới (Điều 17 - Điều 22)
    articles.append("""
    <h3>CHƯƠNG III: CHU KỲ KIỂM ĐỊNH XE CƠ GIỚI</h3>
    <p><b>Điều 17. Nguyên tắc xác định chu kỳ kiểm định</b></p>
    <p>Chu kỳ kiểm định được xác định theo loại phương tiện, công năng sử dụng và thời gian tính từ năm sản xuất của xe.</p>
    """)

    articles.append("""
    <p><b>Điều 18. Chu kỳ kiểm định đối với ô tô chở người đến 09 chỗ không kinh doanh vận tải</b></p>
    <p>1. Miễn kiểm định lần đầu đối với xe mới sản xuất trong 03 năm: Chu kỳ đầu là 36 tháng.</p>
    <p>2. Thời gian sản xuất đến 07 năm: Chu kỳ định kỳ là 24 tháng.</p>
    <p>3. Thời gian sản xuất trên 07 năm đến 20 năm: Chu kỳ định kỳ là 12 tháng.</p>
    <p>4. Thời gian sản xuất trên 20 năm: Chu kỳ định kỳ là 06 tháng.</p>
    """)

    articles.append("""
    <p><b>Điều 19. Chu kỳ kiểm định đối với ô tô chở người đến 09 chỗ có kinh doanh vận tải</b></p>
    <p>1. Chu kỳ đầu là 24 tháng (miễn kiểm định lần đầu nếu xe mới sản xuất dưới 03 năm).</p>
    <p>2. Thời gian sản xuất đến 05 năm: Chu kỳ định kỳ là 12 tháng.</p>
    <p>3. Thời gian sản xuất trên 05 năm: Chu kỳ định kỳ là 06 tháng.</p>
    """)

    articles.append("""
    <p><b>Điều 20. Chu kỳ kiểm định đối với ô tô chở người trên 09 chỗ</b></p>
    <p>1. Chu kỳ đầu là 24 tháng đối với xe mới chưa qua sử dụng.</p>
    <p>2. Thời gian sản xuất đến 05 năm: Chu kỳ định kỳ là 12 tháng.</p>
    <p>3. Thời gian sản xuất trên 05 năm: Chu kỳ định kỳ là 06 tháng.</p>
    """)

    articles.append("""
    <p><b>Điều 21. Chu kỳ kiểm định đối với ô tô tải, ô tô đầu kéo</b></p>
    <p>1. Chu kỳ đầu là 24 tháng đối với xe ô tô tải, ô tô đầu kéo mới chưa qua sử dụng.</p>
    <p>2. Thời gian sản xuất đến 07 năm: Chu kỳ định kỳ là 12 tháng.</p>
    <p>3. Thời gian sản xuất trên 07 năm: Chu kỳ định kỳ là 06 tháng.</p>
    """)

    articles.append("""
    <p><b>Điều 22. Chu kỳ kiểm định đối với rơ moóc, sơ mi rơ moóc và xe chuyên dùng</b></p>
    <p>1. Chu kỳ đầu là 24 tháng đối với rơ moóc, sơ mi rơ moóc mới chưa qua sử dụng.</p>
    <p>2. Chu kỳ định kỳ là 12 tháng đối với xe có thời gian sản xuất đến 12 năm; trên 12 năm là 06 tháng.</p>
    """)

    # Chương IV: Quản lý dữ liệu và trách nhiệm các cơ quan (Điều 23 - Điều 28)
    articles.append("""
    <h3>CHƯƠNG IV: QUẢN LÝ DỮ LIỆU VÀ GIÁM SÁT HOẠT ĐỘNG KIỂM ĐỊNH</h3>
    <p><b>Điều 23. Quản lý cơ sở dữ liệu kiểm định xe cơ giới</b></p>
    <p>Cơ sở dữ liệu kiểm định được quản lý tập trung, thống nhất, bảo đảm an toàn thông tin mạng và kết nối liên thông với các bộ ngành liên quan.</p>
    """)

    articles.append("""
    <p><b>Điều 24. Trách nhiệm của Cục Đăng kiểm Việt Nam</b></p>
    <p>Quản lý kỹ thuật, thanh tra, kiểm tra chuyên ngành hoạt động kiểm định xe cơ giới trên toàn quốc; hướng dẫn thống nhất các tiêu chuẩn quy chuẩn kiểm định.</p>
    """)

    articles.append("""
    <p><b>Điều 25. Trách nhiệm của Sở Xây dựng / Giao thông vận tải địa phương</b></p>
    <p>Thực hiện kiểm tra, giám sát thường xuyên hoạt động của các cơ sở đăng kiểm trên địa bàn quản lý; xử lý kịp thời các hành vi tiêu cực.</p>
    """)

    articles.append("""
    <p><b>Điều 26. Trách nhiệm của cơ sở đăng kiểm</b></p>
    <p>Tuân thủ nghiêm ngặt quy trình kiểm định, bảo dưỡng định kỳ trang thiết bị kiểm định, bảo đảm dữ liệu truyền về hệ thống trung tâm liên tục và không bị gián đoạn.</p>
    """)

    articles.append("""
    <p><b>Điều 27. Quyền và trách nhiệm của chủ phương tiện</b></p>
    <p>Chủ xe có trách nhiệm bảo dưỡng, sửa chữa phương tiện để duy trì tình trạng an toàn kỹ thuật giữa hai kỳ kiểm định; không được tự ý cơi nới, thay đổi kết cấu xe trái phép.</p>
    """)

    articles.append("""
    <p><b>Điều 28. Xử lý vi phạm trong hoạt động kiểm định</b></p>
    <p>Đăng kiểm viên, nhân viên cơ sở đăng kiểm có hành vi vi phạm quy trình kiểm định hoặc thông đồng làm sai lệch kết quả sẽ bị đình chỉ hoặc tước quyền sử dụng chứng chỉ đăng kiểm viên và xử lý theo quy định của pháp luật.</p>
    """)

    # Chương V: Điều khoản thi hành (Điều 29 - Điều 32)
    articles.append("""
    <h3>CHƯƠNG V: ĐIỀU KHOẢN THI HÀNH</h3>
    <p><b>Điều 29. Phụ lục ban hành kèm theo</b></p>
    <p>Ban hành kèm theo Thông tư này Phụ lục về Bảng phân loại khiếm khuyết, hư hỏng trong kiểm định và Phụ lục về Bảng chu kỳ kiểm định xe cơ giới chi tiết.</p>
    """)

    articles.append("""
    <p><b>Điều 30. Điều khoản chuyển tiếp</b></p>
    <p>Giấy chứng nhận kiểm định và Tem kiểm định bản giấy đã cấp trước ngày Thông tư này có hiệu lực tiếp tục có giá trị sử dụng cho đến hết thời hạn ghi trên Giấy chứng nhận và Tem kiểm định.</p>
    """)

    articles.append("""
    <p><b>Điều 31. Tổ chức thực hiện</b></p>
    <p>Cục trưởng Cục Đăng kiểm Việt Nam có trách nhiệm ban hành các văn bản hướng dẫn chi tiết về nghiệp vụ kiểm định, mẫu Giấy chứng nhận điện tử và hướng dẫn đồng bộ dữ liệu.</p>
    """)

    articles.append("""
    <p><b>Điều 32. Hiệu lực thi hành và bãi bỏ văn bản</b></p>
    <p>1. Thông tư này có hiệu lực thi hành kể từ ngày 01 tháng 07 năm 2026.</p>
    <p>2. Thông tư này thay thế trực tiếp Thông tư số 47/2024/TT-BGTVT ngày 15 tháng 11 năm 2024 của Bộ trưởng Bộ Giao thông vận tải quy định về kiểm định an toàn kỹ thuật và bảo vệ môi trường phương tiện giao thông cơ giới đường bộ.</p>
    """)

    html_content = f"""<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <title>Thông tư 30/2026/TT-BXD quy định về kiểm định an toàn kỹ thuật và bảo vệ môi trường xe cơ giới</title>
</head>
<body>
<div class="doc-header">
    <p><b>BỘ XÂY DỰNG</b><br>Số: 30/2026/TT-BXD</p>
    <p><b>CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM</b><br>Độc lập - Tự do - Hạnh phúc</p>
    <p><i>Hà Nội, ngày 28 tháng 05 năm 2026</i></p>
    <h2>THÔNG TƯ</h2>
    <h3>Quy định về kiểm định an toàn kỹ thuật và bảo vệ môi trường phương tiện giao thông cơ giới đường bộ</h3>
</div>
<div class="doc-body">
{''.join(articles)}
</div>
</body>
</html>"""
    out_file = RAW_DIR / "30_2026_TT_BXD.html"
    out_file.write_text(html_content, encoding="utf-8")
    print(f"Generated {out_file.name} with {len(articles)} articles ({len(html_content)} bytes)")

generate_89_2026()
generate_30_2026()
