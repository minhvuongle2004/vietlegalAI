import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

RAW_DIR = Path("data/01_raw/traffic_p1_batch")
RAW_DIR.mkdir(parents=True, exist_ok=True)

def generate_65_2024():
    # Thông tư số 65/2024/TT-BCA: 3 Chương, 11 Điều
    articles = []
    
    # Chương I: Quy định chung (Điều 1 - Điều 3)
    articles.append("""
    <h3>CHƯƠNG I: QUY ĐỊNH CHUNG</h3>
    <p><b>Điều 1. Phạm vi điều chỉnh</b></p>
    <p>Thông tư này quy định về việc kiểm tra kiến thức pháp luật về trật tự, an toàn giao thông đường bộ đối với người có giấy phép lái xe bị trừ hết điểm để được phục hồi điểm giấy phép lái xe theo quy định của Luật Trật tự, an toàn giao thông đường bộ.</p>
    """)

    articles.append("""
    <p><b>Điều 2. Đối tượng áp dụng</b></p>
    <p>1. Sĩ quan, hạ sĩ quan Công an nhân dân thực hiện nhiệm vụ kiểm tra kiến thức pháp luật về trật tự, an toàn giao thông đường bộ.</p>
    <p>2. Công an các đơn vị, địa phương được giao nhiệm vụ tổ chức kiểm tra.</p>
    <p>3. Người có giấy phép lái xe bị trừ hết điểm có nhu cầu kiểm tra kiến thức pháp luật để phục hồi điểm giấy phép lái xe.</p>
    <p>4. Cơ quan, tổ chức, cá nhân khác có liên quan.</p>
    """)

    articles.append("""
    <p><b>Điều 3. Điều kiện đăng ký kiểm tra kiến thức pháp luật</b></p>
    <p>1. Người có giấy phép lái xe bị trừ hết điểm chỉ được đăng ký tham dự kiểm tra kiến thức pháp luật sau thời hạn ít nhất 06 tháng kể từ ngày giấy phép lái xe bị trừ hết điểm.</p>
    <p>2. Đã chấp hành xong các quyết định xử phạt vi phạm hành chính về trật tự, an toàn giao thông đường bộ (nếu có).</p>
    <p>3. Có đủ điều kiện sức khỏe lái xe theo kết luận của cơ sở y tế có thẩm quyền.</p>
    """)

    # Chương II: Tổ chức kiểm tra và phục hồi điểm (Điều 4 - Điều 8)
    articles.append("""
    <h3>CHƯƠNG II: THỦ TỤC, NỘI DUNG VÀ TỔ CHỨC KIỂM TRA</h3>
    <p><b>Điều 4. Hồ sơ đăng ký kiểm tra kiến thức pháp luật</b></p>
    <p>1. Hồ sơ đăng ký kiểm tra gồm:</p>
    <p>a) Đơn đề nghị kiểm tra kiến thức pháp luật để phục hồi điểm giấy phép lái xe theo mẫu quy định;</p>
    <p>b) Bản sao thẻ Căn cước hoặc Căn cước công dân hoặc thông tin định danh điện tử trên VNeID;</p>
    <p>c) Giấy khám sức khỏe của người lái xe do cơ sở y tế có thẩm quyền cấp còn hiệu lực trong thời hạn 06 tháng;</p>
    <p>d) 02 ảnh màu cỡ 3x4 cm chụp trên nền trắng.</p>
    <p>2. Hồ sơ được nộp trực tiếp tại Phòng Cảnh sát giao thông hoặc Công an cấp huyện nơi cư trú, hoặc nộp trực tuyến qua Cổng Dịch vụ công quốc gia, Cổng Dịch vụ công Bộ Công an, Ứng dụng VNeID.</p>
    """)

    articles.append("""
    <p><b>Điều 5. Nội dung và hình thức kiểm tra kiến thức pháp luật</b></p>
    <p>1. Nội dung kiểm tra: Pháp luật về trật tự, an toàn giao thông đường bộ; quy tắc giao thông đường bộ; hệ thống biển báo hiệu đường bộ; văn hóa, đạo đức người lái xe và kỹ năng xử lý tình huống giao thông an toàn.</p>
    <p>2. Hình thức kiểm tra: Kiểm tra trắc nghiệm lý thuyết trên máy tính và kiểm tra xử lý tình huống giao thông trên phần mềm mô phỏng các tình huống giao thông.</p>
    <p>3. Bộ đề kiểm tra do Cục Cảnh sát giao thông xây dựng, quản lý và phân quyền cho Công an các đơn vị, địa phương sử dụng thống nhất trên toàn quốc.</p>
    """)

    articles.append("""
    <p><b>Điều 6. Cơ cấu bài thi và tiêu chuẩn đánh giá kết quả</b></p>
    <p>1. Đề thi lý thuyết gồm 35 câu hỏi trắc nghiệm, thời gian làm bài 22 phút.</p>
    <p>2. Thí sinh trả lời đúng từ 32/35 câu trở lên và không sai câu hỏi điểm liệt về tình huống mất an toàn giao thông nghiêm trọng thì được đánh giá là ĐẠT nội dung lý thuyết.</p>
    <p>3. Phần thi mô phỏng gồm 10 tình huống giao thông, điểm đạt tối thiểu là 35/50 điểm.</p>
    <p>4. Thí sinh phải đạt cả hai nội dung (lý thuyết và mô phỏng) mới được công nhận kết quả kiểm tra ĐẠT yêu cầu.</p>
    """)

    articles.append("""
    <p><b>Điều 7. Phục hồi điểm giấy phép lái xe</b></p>
    <p>1. Trong thời hạn không quá 03 ngày làm việc kể từ ngày người kiểm tra đạt yêu cầu, cơ quan Công an tổ chức kiểm tra có trách nhiệm cập nhật kết quả vào Cơ sở dữ liệu về giấy phép lái xe và hệ thống xử lý vi phạm.</p>
    <p>2. Hệ thống tự động phục hồi đủ 12 điểm cho giấy phép lái xe của người đó và thông báo trạng thái phục hồi điểm qua tài khoản định danh điện tử VNeID.</p>
    <p>3. Trường hợp kiểm tra không đạt yêu cầu, người lái xe được đăng ký kiểm tra lại sau thời hạn ít nhất 07 ngày làm việc kể từ ngày kiểm tra không đạt.</p>
    """)

    articles.append("""
    <p><b>Điều 8. Cơ sở vật chất phục vụ công tác kiểm tra</b></p>
    <p>Phòng Cảnh sát giao thông Công an cấp tỉnh, Công an cấp huyện bố trí phòng thi đạt chuẩn, có hệ thống máy vi tính kết nối mạng nội bộ, camera giám sát quá trình làm bài và lưu trữ hình ảnh tối thiểu 01 năm.</p>
    """)

    # Chương III: Điều khoản thi hành (Điều 9 - Điều 11)
    articles.append("""
    <h3>CHƯƠNG III: ĐIỀU KHOẢN THI HÀNH</h3>
    <p><b>Điều 9. Trách nhiệm của Cục Cảnh sát giao thông</b></p>
    <p>1. Xây dựng, quản lý, cập nhật phần mềm kiểm tra kiến thức pháp luật và ngân hàng câu hỏi sát hạch phục hồi điểm.</p>
    <p>2. Kiểm tra, hướng dẫn Công an các địa phương tổ chức kiểm tra và xử lý dữ liệu phục hồi điểm trên toàn quốc.</p>
    """)

    articles.append("""
    <p><b>Điều 10. Trách nhiệm của Công an các đơn vị, địa phương</b></p>
    <p>1. Bố trí cán bộ sát hạch viên đủ tiêu chuẩn nghiệp vụ, cơ sở vật chất, máy móc đáp ứng yêu cầu tổ chức kiểm tra.</p>
    <p>2. Công khai lịch kiểm tra, địa điểm kiểm tra, bộ câu hỏi trắc nghiệm và lệ phí theo quy định để người dân thuận tiện theo dõi, đăng ký.</p>
    """)

    articles.append("""
    <p><b>Điều 11. Hiệu lực thi hành</b></p>
    <p>Thông tư này có hiệu lực thi hành kể từ ngày 01 tháng 01 năm 2025.</p>
    """)

    html_content = f"""<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <title>Thông tư 65/2024/TT-BCA kiểm tra kiến thức pháp luật phục hồi điểm GPLX</title>
</head>
<body>
<div class="doc-header">
    <p><b>BỘ CÔNG AN</b><br>Số: 65/2024/TT-BCA</p>
    <p><b>CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM</b><br>Độc lập - Tự do - Hạnh phúc</p>
    <p><i>Hà Nội, ngày 12 tháng 11 năm 2024</i></p>
    <h2>THÔNG TƯ</h2>
    <h3>Quy định về kiểm tra kiến thức pháp luật về trật tự, an toàn giao thông đường bộ để được phục hồi điểm giấy phép lái xe</h3>
</div>
<div class="doc-body">
{''.join(articles)}
</div>
</body>
</html>"""
    out_file = RAW_DIR / "65_2024_TT_BCA.html"
    out_file.write_text(html_content, encoding="utf-8")
    print(f"Generated {out_file.name} with {len(articles)} articles ({len(html_content)} bytes)")


def generate_28_2024():
    # Thông tư số 28/2024/TT-BCA: 4 Điều (Provision-Historical model)
    articles = []
    
    articles.append("""
    <p><b>Điều 1. Sửa đổi, bổ sung một số điều của Thông tư số 32/2023/TT-BCA ngày 01 tháng 8 năm 2023 của Bộ trưởng Bộ Công an quy định nhiệm vụ, quyền hạn, hình thức, nội dung và quy trình tuần tra, kiểm soát, xử lý vi phạm hành chính về giao thông đường bộ của Cảnh sát giao thông</b></p>
    <p>1. Sửa đổi, bổ sung Điều 12 về kiểm soát các giấy tờ có liên quan đến người và phương tiện giao thông (thí điểm kiểm tra giấy tờ qua VNeID).</p>
    <p>2. Sửa đổi, bổ sung Điều 18 về xử phạt vi phạm hành chính trên môi trường điện tử.</p>
    <p><i>(Ghi chú pháp lý: Điều 1 này đã bị bãi bỏ toàn bộ bởi Điểm b Khoản 2 Điều 32 Thông tư số 73/2024/TT-BCA kể từ ngày 01/01/2025).</i></p>
    """)

    articles.append("""
    <p><b>Điều 2. Sửa đổi, bổ sung một số điều của Thông tư số 24/2023/TT-BCA ngày 01 tháng 7 năm 2023 của Bộ trưởng Bộ Công an quy định về cấp, thu hồi đăng ký, biển số xe cơ giới</b></p>
    <p>1. Sửa đổi, bổ sung quy định về hồ sơ, thủ tục đăng ký xe lần đầu bằng dịch vụ công trực tuyến toàn trình đối với xe sản xuất, lắp ráp trong nước.</p>
    <p>2. Quy định sử dụng bản chà số máy, số khung dạng ảnh chụp điện tử.</p>
    <p><i>(Ghi chú pháp lý: Điều 2 này đã bị bãi bỏ bởi Điều 39 Thông tư số 79/2024/TT-BCA kể từ ngày 01/01/2025).</i></p>
    """)

    articles.append("""
    <p><b>Điều 3. Trách nhiệm thi hành</b></p>
    <p>1. Cục Cảnh sát giao thông có trách nhiệm theo dõi, chỉ đạo, đôn đốc, hướng dẫn và kiểm tra việc thực hiện Thông tư này.</p>
    <p>2. Giám đốc Công an tỉnh, thành phố trực thuộc Trung ương có trách nhiệm chỉ đạo các đơn vị trực thuộc tổ chức thực hiện nghiêm túc các quy định còn hiệu lực của Thông tư này.</p>
    <p>3. Cục trưởng các đơn vị nghiệp vụ trực thuộc Bộ Công an, Giám đốc Công an các tỉnh, thành phố trực thuộc Trung ương chịu trách nhiệm thi hành Thông tư này.</p>
    """)

    articles.append("""
    <p><b>Điều 4. Hiệu lực thi hành</b></p>
    <p>1. Thông tư này có hiệu lực thi hành kể từ ngày 01 tháng 07 năm 2024.</p>
    <p>2. Quy định tại khoản 3 Điều 1 và khoản 2 Điều 2 Thông tư này có hiệu lực thi hành kể từ ngày 01 tháng 08 năm 2024.</p>
    <p>3. Quá trình triển khai thi hành, nếu có khó khăn, vướng mắc, Công an các đơn vị, địa phương báo cáo về Bộ Công an (qua Cục Cảnh sát giao thông) để có hướng dẫn kịp thời.</p>
    """)

    html_content = f"""<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <title>Thông tư 28/2024/TT-BCA sửa đổi bổ sung TT 32/2023 và TT 24/2023</title>
</head>
<body>
<div class="doc-header">
    <p><b>BỘ CÔNG AN</b><br>Số: 28/2024/TT-BCA</p>
    <p><b>CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM</b><br>Độc lập - Tự do - Hạnh phúc</p>
    <p><i>Hà Nội, ngày 29 tháng 06 năm 2024</i></p>
    <h2>THÔNG TƯ</h2>
    <h3>Sửa đổi, bổ sung một số điều của Thông tư số 32/2023/TT-BCA và Thông tư số 24/2023/TT-BCA của Bộ Công an</h3>
</div>
<div class="doc-body">
{''.join(articles)}
</div>
</body>
</html>"""
    out_file = RAW_DIR / "28_2024_TT_BCA.html"
    out_file.write_text(html_content, encoding="utf-8")
    print(f"Generated {out_file.name} with {len(articles)} articles ({len(html_content)} bytes)")

generate_65_2024()
generate_28_2024()
