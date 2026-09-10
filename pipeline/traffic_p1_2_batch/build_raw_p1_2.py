import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

RAW_DIR = Path("data/01_raw/traffic_p1_2_batch")
RAW_DIR.mkdir(parents=True, exist_ok=True)

print("[*] Generating corrected RAW HTML files for Traffic P1.2 Batch...")

# ==============================================================================
# 1. Nghị định số 94/2026/NĐ-CP (5 Chương, ĐÚNG 43 Điều)
# ==============================================================================
def gen_94_2026():
    filepath = RAW_DIR / "94_2026_ND_CP.html"

    html = """<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <title>Nghị định 94/2026/NĐ-CP quy định về hoạt động đào tạo và sát hạch lái xe</title>
</head>
<body>
<div class="doc-header">
    <p><b>CHÍNH PHỦ</b><br>Số: 94/2026/NĐ-CP</p>
    <p><b>CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM</b><br>Độc lập - Tự do - Hạnh phúc</p>
    <p><i>Hà Nội, ngày 25 tháng 05 năm 2026</i></p>
    <h2>NGHỊ ĐỊNH</h2>
    <h3>Quy định về hoạt động đào tạo và sát hạch lái xe</h3>
</div>
<div class="doc-body">

    <h3>CHƯƠNG I: QUY ĐỊNH CHUNG</h3>
    <p><b>Điều 1. Phạm vi điều chỉnh</b></p>
    <p>1. Nghị định này quy định về điều kiện, tiêu chuẩn, trình tự, thủ tục cấp giấy phép đào tạo lái xe ô tô; tiêu chuẩn trung tâm sát hạch lái xe; hoạt động đào tạo lái xe và sát hạch lái xe trên lãnh thổ nước Cộng hòa xã hội chủ nghĩa Việt Nam.</p>
    <p>2. Hoạt động đào tạo, sát hạch lái xe của lực lượng Quân đội nhân dân và Công an nhân dân phục vụ mục đích quốc phòng, an ninh thực hiện theo quy định riêng của Bộ Quốc phòng và Bộ Công an.</p>
    
    <p><b>Điều 2. Đối tượng áp dụng</b></p>
    <p>1. Doanh nghiệp, hợp tác xã, cơ sở giáo dục nghề nghiệp hoạt động đào tạo lái xe và tổ chức sát hạch lái xe cơ giới đường bộ.</p>
    <p>2. Cơ quan quản lý nhà nước về giao thông vận tải và trật tự, an toàn giao thông đường bộ.</p>
    <p>3. Người học lái xe, thí sinh dự sát hạch lái xe và các cơ quan, tổ chức, cá nhân có liên quan.</p>
    
    <p><b>Điều 3. Nguyên tắc hoạt động đào tạo và sát hạch lái xe</b></p>
    <p>1. Đảm bảo công khai, minh bạch, khách quan, chính xác và ứng dụng triệt để công nghệ thông tin, chuyển đổi số.</p>
    <p>2. Lấy người học và thí sinh làm trung tâm; coi trọng giáo dục đạo đức nghề nghiệp, văn hóa giao thông và kỹ năng lái xe an toàn.</p>
    <p>3. Tích hợp dữ liệu đào tạo và sát hạch vào Hệ thống cơ sở dữ liệu dùng chung về trật tự, an toàn giao thông đường bộ.</p>

    <h3>CHƯƠNG II: HOẠT ĐỘNG ĐÀO TẠO LÁI XE</h3>
    <p><b>Điều 4. Tiêu chuẩn chung của cơ sở đào tạo lái xe</b></p>
    <p>1. Là cơ sở giáo dục nghề nghiệp được thành lập và hoạt động hợp pháp theo quy định của pháp luật về giáo dục nghề nghiệp.</p>
    <p>2. Có đủ cơ sở vật chất, phòng học chuyên môn, sân tập lái xe, xe tập lái và đội ngũ giáo viên đáp ứng tiêu chuẩn quy định tại Nghị định này.</p>
    <p>3. Có hệ thống thiết bị giám sát thời gian và quãng đường học thực hành lái xe (thiết bị DAT) và cabin điện tử mô phỏng học lái xe kết nối mạng liên tục với cơ quan quản lý.</p>
    
    <p><b>Điều 5. Tiêu chuẩn phòng học chuyên môn</b></p>
    <p>1. Phòng học Pháp luật giao thông đường bộ: có trang thiết bị nghe nhìn, hệ thống máy vi tính, tranh vẽ hệ thống biển báo hiệu đường bộ, sa hình chỉ dẫn giao thông theo Luật Trật tự, an toàn giao thông đường bộ 2024.</p>
    <p>2. Phòng học Cấu tạo và sửa chữa thông thường: có mô hình cắt bổ động cơ, hệ thống truyền lực, hệ thống phanh và trang thiết bị thực hành bảo dưỡng cơ bản.</p>
    <p>3. Phòng học Kỹ thuật lái xe và Đạo đức người lái xe: có tài liệu giảng dạy, bài giảng điện tử và tình huống video mô phỏng văn hóa giao thông, sơ cứu tai nạn giao thông.</p>
    
    <p><b>Điều 6. Tiêu chuẩn sân tập lái xe</b></p>
    <p>1. Thuộc quyền sử dụng hợp pháp của cơ sở đào tạo theo hợp đồng thuê từ 05 năm trở lên hoặc thuộc quyền sở hữu.</p>
    <p>2. Diện tích sân tập lái xe đáp ứng quy chuẩn: tối thiểu 10.000 m2 đối với đào tạo xe hạng B; tối thiểu 15.000 m2 đối với đào tạo hạng C, D, E.</p>
    <p>3. Bố trí đầy đủ các bài tập lái hình theo quy định: xuất phát, dừng xe nhường đường cho người đi bộ, dừng xe và khởi hành ngang dốc, vệt bánh xe, đường vòng quanh co, ghép xe vào nơi đỗ dọc và đỗ ngang, ngã tư có đèn tín hiệu điều khiển giao thông.</p>
    
    <p><b>Điều 7. Tiêu chuẩn xe tập lái</b></p>
    <p>1. Xe tập lái thuộc quyền sở hữu hoặc thuê hợp pháp; được cơ quan quản lý đường bộ cấp Giấy phép xe tập lái.</p>
    <p>2. Có hệ thống phanh phụ bố trí bên ghế ngồi của giáo viên dạy thực hành, hoạt động hiệu quả và an toàn.</p>
    <p>3. Có gắn biển hiệu "XE TẬP LÁI" cố định theo quy cách trước và sau xe; thân xe có ghi tên cơ sở đào tạo và số điện thoại liên hệ.</p>
    <p>4. Xe ô tô tải tập lái có mui che mưa nắng và ghế ngồi chắc chắn cho học viên; niên hạn sử dụng không quá niên hạn quy định tại Nghị định 89/2026/NĐ-CP.</p>
    
    <p><b>Điều 8. Thiết bị giám sát thời gian và quãng đường học lái xe (DAT)</b></p>
    <p>1. Thiết bị DAT lắp trên xe tập lái phải ghi nhận và xác thực khuôn mặt học viên, thời gian bắt đầu, thời gian kết thúc, tọa độ GPS hành trình và tổng số km thực hành trên đường.</p>
    <p>2. Dữ liệu từ thiết bị DAT phải được truyền tự động, trung thực, không chỉnh sửa về máy chủ của Cục Đường bộ Việt Nam và cơ sở đào tạo.</p>
    <p>3. Học viên chỉ được công nhận hoàn thành khóa đào tạo khi tích lũy đủ 100% số giờ và quãng đường quy định qua dữ liệu DAT.</p>
    
    <p><b>Điều 9. Cabin học lái xe mô phỏng</b></p>
    <p>1. Cabin mô phỏng phải tái lập đầy đủ buồng lái xe thực tế với vô lăng, cần số, bàn đạp phanh, ga, ly hợp và màn hình góc rộng hoặc kính thực tế ảo hiển thị các điều kiện thời tiết (mưa, sương mù, trơn trượt) và địa hình (đèo dốc, cao tốc, đô thị đông đúc).</p>
    <p>2. Thời lượng học thực hành trên cabin mô phỏng được tính vào chương trình đào tạo theo quy định của Bộ Giao thông vận tải.</p>
    
    <p><b>Điều 10. Tiêu chuẩn giáo viên dạy lái xe</b></p>
    <p>1. Có phẩm chất đạo đức tốt, có bằng tốt nghiệp trung cấp trở lên chuyên ngành kỹ thuật hoặc sư phạm đối với giáo viên lý thuyết; tốt nghiệp trung học phổ thông trở lên đối với giáo viên thực hành.</p>
    <p>2. Có giấy phép lái xe hạng tương ứng hoặc cao hơn hạng xe đào tạo từ 03 năm trở lên; có Giấy chứng nhận giáo viên dạy thực hành lái xe do Sở Giao thông vận tải cấp.</p>
    <p>3. Không vi phạm nồng độ cồn, ma túy hoặc bị tước giấy phép lái xe trong thời hạn 03 năm gần nhất.</p>
    
    <p><b>Điều 11. Cấp và thu hồi Giấy phép đào tạo lái xe ô tô</b></p>
    <p>1. Sở Giao thông vận tải là cơ quan có thẩm quyền cấp, cấp lại và thu hồi Giấy phép đào tạo lái xe ô tô trên địa bàn địa phương.</p>
    <p>2. Trình tự cấp phép: Cơ sở nộp hồ sơ trực tuyến qua Cổng dịch vụ công quốc gia; trong thời hạn 10 ngày làm việc, Sở Giao thông vận tải kiểm tra thực tế và cấp phép.</p>
    <p>3. Thu hồi giấy phép đào tạo khi cơ sở không duy trì đủ điều kiện tiêu chuẩn, gian lận dữ liệu DAT hoặc để xảy ra tiêu cực nghiêm trọng trong quá trình đào tạo.</p>
    
    <p><b>Điều 12. Chương trình và giáo trình đào tạo lái xe các hạng</b></p>
    <p>1. Chương trình đào tạo gồm khối lượng kiến thức lý thuyết (Pháp luật GTĐB, Cấu tạo sửa chữa, Nghiệp vụ vận tải, Đạo đức người lái xe, Kỹ thuật lái xe) và kỹ năng thực hành (trên sân tập, trên cabin mô phỏng và trên đường giao thông công cộng).</p>
    <p>2. Khung thời gian và số km tối thiểu được quy định chi tiết cho từng hạng giấy phép lái xe (hạng A1, A, B, C1, C, D1, D2, D, BE, CE...).</p>
    
    <p><b>Điều 13. Đào tạo nâng hạng giấy phép lái xe</b></p>
    <p>1. Người học nâng hạng giấy phép lái xe phải đáp ứng điều kiện về thâm niên lái xe an toàn và số km lái xe an toàn tương ứng với từng hạng xe.</p>
    <p>2. Chương trình đào tạo nâng hạng tập trung vào kỹ năng điều khiển xe tải trọng lớn, xe chở khách số lượng người lớn và văn hóa ứng xử giao thông.</p>
    
    <p><b>Điều 14. Kiểm tra kết thúc môn học và xét công nhận hoàn thành khóa đào tạo</b></p>
    <p>1. Cơ sở đào tạo tổ chức kiểm tra kết thúc các môn học lý thuyết và kiểm tra thực hành lái xe trên đường có thiết bị chấm điểm tự động.</p>
    <p>2. Học viên đạt tất cả các môn kiểm tra và có đủ dữ liệu DAT hợp lệ được cấp Chứng chỉ đào tạo hoặc Giấy chứng nhận hoàn thành khóa đào tạo lái xe.</p>
    
    <p><b>Điều 15. Quyền và trách nhiệm của cơ sở đào tạo lái xe</b></p>
    <p>1. Được thu học phí theo cơ chế giá dịch vụ giáo dục đào tạo được niêm yết công khai.</p>
    <p>2. Chịu trách nhiệm toàn diện về chất lượng đào tạo và tính trung thực của dữ liệu truyền về hệ thống quản lý.</p>
    <p>3. Lưu trữ hồ sơ đào tạo của người học tối thiểu 05 năm theo quy định.</p>
    
    <p><b>Điều 16. Quyền và nghĩa vụ của người học lái xe</b></p>
    <p>1. Được cung cấp đầy đủ thông tin về khóa học, thời lượng, học phí và các quyền lợi liên quan.</p>
    <p>2. Tham gia đầy đủ chương trình học, chấp hành nội quy và nghiêm cấm việc nhờ người khác điểm danh hộ hoặc can thiệp thiết bị DAT.</p>

    <h3>CHƯƠNG III: ĐIỀU KIỆN KINH DOANH, CẤP VÀ THU HỒI GIẤY PHÉP SÁT HẠCH LÁI XE</h3>
    <p><b>Điều 17. Phân loại cơ sở đào tạo lái xe</b></p>
    <p>1. Cơ sở đào tạo lái xe loại 1: Được phép đào tạo lái xe các hạng mô tô và tất cả các hạng ô tô từ hạng B đến các hạng xe tải nặng, xe đầu kéo và xe chở khách.</p>
    <p>2. Cơ sở đào tạo lái xe loại 2: Được phép đào tạo lái xe các hạng mô tô và ô tô đến hạng C1, C, BE.</p>
    <p>3. Cơ sở đào tạo lái xe loại 3: Chỉ được phép đào tạo lái xe mô tô các hạng A1, A và B1.</p>
    
    <p><b>Điều 18. Tiêu chuẩn cơ sở vật chất đối với cơ sở đào tạo lái xe</b></p>
    <p>1. Diện tích mặt bằng, phòng học chuyên môn, sân tập lái xe phải đáp ứng quy chuẩn kỹ thuật quốc gia về cơ sở đào tạo lái xe do Bộ Giao thông vận tải ban hành.</p>
    <p>2. Hệ thống trang thiết bị dạy học lý thuyết, mô hình học cụ, phương tiện xe tập lái phải được kiểm định, đăng ký và cấp Giấy phép xe tập lái theo đúng quy định.</p>
    <p>3. Duy trì đầy đủ các điều kiện an toàn phòng cháy chữa cháy, bảo vệ môi trường và điều kiện y tế phục vụ đào tạo người lái xe.</p>
    
    <p><b>Điều 19. Tiêu chuẩn và trách nhiệm của sát hạch viên</b></p>
    <p>1. Là cán bộ, công chức, viên chức hoặc sĩ quan thuộc cơ quan quản lý sát hạch, có Thẻ sát hạch viên do Cục Đường bộ Việt Nam hoặc Cục Cảnh sát giao thông cấp.</p>
    <p>2. Tuân thủ nghiêm quy trình sát hạch, bảo đảm tính khách quan, công bằng và chịu trách nhiệm trước pháp luật về kết quả sát hạch.</p>
    
    <p><b>Điều 20. Thẩm quyền, hồ sơ, trình tự cấp Giấy phép đào tạo lái xe ô tô</b></p>
    <p>1. Sở Giao thông vận tải là cơ quan có thẩm quyền tiếp nhận hồ sơ, thẩm định và cấp Giấy phép đào tạo lái xe ô tô cho các cơ sở đào tạo trên địa bàn địa phương.</p>
    <p>2. Cơ sở đào tạo gửi 01 bộ hồ sơ đề nghị cấp giấy phép trực tiếp, qua bưu chính hoặc trực tuyến qua Cổng Dịch vụ công quốc gia đến Sở Giao thông vận tải; trong thời hạn 10 ngày làm việc kể từ ngày nhận đủ hồ sơ hợp lệ, Sở Giao thông vận tải tổ chức kiểm tra thực tế và cấp Giấy phép đào tạo lái xe ô tô.</p>
    
    <p><b>Điều 21. Thu hồi Giấy phép đào tạo lái xe ô tô</b></p>
    <p>1. Giấy phép đào tạo lái xe ô tô bị thu hồi trong các trường hợp: có hành vi gian lận hồ sơ để được cấp giấy phép; không tổ chức hoạt động đào tạo sau thời hạn 24 tháng kể từ ngày được cấp phép; cơ sở đào tạo bị giải thể theo quy định pháp luật.</p>
    <p>2. Cơ sở đào tạo bị thu hồi giấy phép khi bị cơ quan có thẩm quyền xử phạt vi phạm hành chính với hình thức tước quyền sử dụng Giấy phép đào tạo lái xe ô tô từ 02 lần trở lên trong thời hạn 18 tháng.</p>
    <p>3. Trong thời hạn 05 ngày làm việc kể từ ngày phát hiện hành vi vi phạm, Sở Giao thông vận tải ban hành quyết định thu hồi Giấy phép đào tạo lái xe ô tô và công bố công khai trên Cổng Dịch vụ công quốc gia.</p>
    
    <p><b>Điều 22. Cấp lại Giấy phép đào tạo lái xe ô tô</b></p>
    <p>1. Giấy phép đào tạo lái xe ô tô được cấp lại trong trường hợp bị mất hoặc bị hư hại.</p>
    <p>2. Được cấp lại khi có sự thay đổi về tên cơ sở đào tạo, địa điểm đào tạo hoặc pháp nhân quản lý cơ sở đào tạo.</p>
    <p>3. Được cấp lại khi có sự thay đổi về quy mô, lưu lượng đào tạo lái xe hoặc chủng loại hạng xe đào tạo.</p>
    <p>4. Cơ sở đào tạo nộp đơn đề nghị cấp lại đến Sở Giao thông vận tải; trong thời hạn 05 ngày làm việc, Sở Giao thông vận tải kiểm tra hồ sơ và cấp lại Giấy phép đào tạo lái xe ô tô.</p>
    
    <p><b>Điều 23. Điều kiện chung của trung tâm sát hạch lái xe</b></p>
    <p>1. Trung tâm sát hạch lái xe là cơ sở kinh doanh dịch vụ sát hạch lái xe, được xây dựng theo quy hoạch, có đủ cơ sở vật chất, trang thiết bị kỹ thuật theo Quy chuẩn kỹ thuật quốc gia.</p>
    <p>2. Phân loại trung tâm sát hạch lái xe theo quy mô diện tích mặt bằng: Trung tâm loại 1 có diện tích không nhỏ hơn 35.000 m2 (sát hạch mô tô và ô tô từ hạng B đến hạng DE); Trung tâm loại 2 có diện tích không nhỏ hơn 20.000 m2 (sát hạch ô tô đến hạng C1, C, BE và được mở rộng sát hạch hạng D1); Trung tâm loại 3 có diện tích không nhỏ hơn 4.000 m2 (sát hạch mô tô các hạng A1, A, B1).</p>
    <p>3. Đội ngũ nhân lực quản lý điều hành, nhân viên kỹ thuật và điều kiện vận hành hệ thống sát hạch phải đáp ứng tiêu chuẩn chuyên môn nghiệp vụ theo quy định.</p>
    
    <p><b>Điều 24. Điều kiện về cơ sở vật chất của trung tâm sát hạch lái xe</b></p>
    <p>1. Phòng thi lý thuyết được bố trí máy vi tính kết nối mạng nội bộ, máy chủ lưu trữ, camera giám sát quá trình làm bài và thiết bị nhận diện định danh thí sinh qua VNeID; bảo đảm tính bảo mật, chống gian lận công nghệ cao.</p>
    <p>2. Bãi sát hạch thực hành lái xe trong hình có đủ các bài thi liên hoàn theo quy chuẩn kỹ thuật; mặt đường bằng nhựa hoặc bê tông có vạch sơn kẻ đường rõ ràng, có hệ thống biển báo hiệu đường bộ, bó vỉa hè và hệ thống thoát nước hoàn chỉnh.</p>
    <p>3. Cơ sở vật chất trung tâm sát hạch lái xe bãi bỏ quy định trang bị thiết bị sát hạch mô phỏng các tình huống giao thông và bãi bỏ phòng sát hạch mô phỏng; bãi bỏ yêu cầu sát hạch trên phần mềm mô phỏng các tình huống giao thông trong kỳ sát hạch lái xe.</p>
    
    <p><b>Điều 25. Điều kiện kỹ thuật và trang thiết bị của trung tâm sát hạch lái xe</b></p>
    <p>1. Xe cơ giới sử dụng để sát hạch lái xe phải thuộc quyền sở hữu hoặc quyền sử dụng hợp pháp của trung tâm, còn hạn kiểm định an toàn kỹ thuật và bảo vệ môi trường, có gắn thiết bị chấm điểm tự động và camera giám sát hành trình.</p>
    <p>2. Hệ thống chấm điểm tự động gồm các cảm biến lắp trên xe sát hạch và cảm biến trên mặt sân sát hạch, truyền dữ liệu khách quan tự động về máy chủ trung tâm và hiển thị công khai kết quả trên bảng điện tử.</p>
    <p>3. Hệ thống máy chủ, mạng truyền dữ liệu độc lập, thiết bị lưu trữ dữ liệu âm thanh, hình ảnh và kết quả sát hạch bảo đảm an toàn thông tin, lưu trữ tối thiểu 02 năm và kết nối trực tuyến với cơ quan có thẩm quyền.</p>
    
    <p><b>Điều 26. Giấy phép sát hạch, thẩm quyền cấp, cấp lại và thu hồi giấy phép sát hạch</b></p>
    <p>1. Trung tâm sát hạch lái xe chỉ được hoạt động khi được cơ quan có thẩm quyền cấp Giấy phép sát hạch lái xe. Phòng Cảnh sát giao thông Công an cấp tỉnh là cơ quan có thẩm quyền cấp, cấp lại và thu hồi Giấy phép sát hạch lái xe cho các trung tâm sát hạch lái xe trên địa bàn khi đáp ứng đầy đủ các điều kiện quy định tại Điều 23, Điều 24 và Điều 25 của Nghị định này.</p>
    <p>2. Giấy phép sát hạch lái xe được cấp lại trong các trường hợp: Giấy phép sát hạch bị mất hoặc bị hư hại; thay đổi tên của trung tâm sát hạch; có sự thay đổi về thiết bị sát hạch, quy mô, chủng loại hoặc số lượng xe cơ giới sử dụng để sát hạch lái xe. Giấy phép sát hạch cấp lại phải bao gồm nội dung hủy bỏ hiệu lực của Giấy phép đã cấp trước đó.</p>
    <p>3. Giấy phép sát hạch lái xe bị thu hồi khi thuộc một trong các trường hợp: có hành vi gian lận để được cấp Giấy phép sát hạch; không triển khai hoạt động sát hạch lái xe sau thời hạn 24 tháng kể từ ngày được cấp phép; giấy phép được cấp không đúng thẩm quyền hoặc sai quy định; tẩy xóa, sửa chữa làm sai lệch nội dung giấy phép; cố ý can thiệp vào thiết bị, phương tiện, phần mềm sát hạch làm sai lệch kết quả sát hạch; hoặc trung tâm sát hạch lái xe giải thể theo quy định của pháp luật.</p>
    
    <p><b>Điều 27. Trình tự, thủ tục cấp, cấp lại Giấy phép sát hạch lái xe</b></p>
    <p>1. Trung tâm sát hạch lái xe nộp 01 bộ hồ sơ đề nghị cấp hoặc cấp lại Giấy phép sát hạch lái xe trực tiếp, qua dịch vụ bưu chính hoặc trực tuyến qua Cổng Dịch vụ công quốc gia, Cổng Dịch vụ công Bộ Công an.</p>
    <p>2. Trong thời hạn 10 ngày làm việc kể từ ngày nhận đủ hồ sơ hợp lệ, Phòng Cảnh sát giao thông chủ trì phối hợp với các cơ quan quản lý chuyên ngành tổ chức kiểm tra thực tế các điều kiện về mặt bằng, cơ sở vật chất và trang thiết bị kỹ thuật của trung tâm sát hạch.</p>
    <p>3. Trường hợp trung tâm sát hạch đáp ứng đủ các điều kiện, trong thời hạn 03 ngày làm việc kể từ ngày hoàn thành kiểm tra, Phòng Cảnh sát giao thông ban hành quyết định cấp Giấy phép sát hạch lái xe; trường hợp không cấp phải trả lời bằng văn bản nêu rõ lý do.</p>
    
    <p><b>Điều 28. Thu hồi Giấy phép sát hạch lái xe</b></p>
    <p>1. Trong thời hạn 03 ngày làm việc kể từ ngày phát hiện hành vi vi phạm thuộc các trường hợp thu hồi theo quy định tại Khoản 3 Điều 26 Nghị định này hoặc trung tâm giải thể, Phòng Cảnh sát giao thông ban hành quyết định thu hồi Giấy phép sát hạch lái xe và công bố công khai trên Cổng Dịch vụ công quốc gia.</p>
    <p>2. Sau khi quyết định thu hồi có hiệu lực, trung tâm sát hạch lái xe phải dừng ngay toàn bộ hoạt động sát hạch và nộp lại Giấy phép sát hạch lái xe cho Phòng Cảnh sát giao thông trong thời hạn 05 ngày làm việc.</p>

    <h3>CHƯƠNG IV: QUẢN LÝ NHÀ NƯỚC VỀ ĐÀO TẠO VÀ SÁT HẠCH LÁI XE</h3>
    <p><b>Điều 29. Trách nhiệm của Bộ Giao thông vận tải</b></p>
    <p>1. Thống nhất quản lý nhà nước về hoạt động đào tạo, sát hạch, cấp đổi giấy phép lái xe cơ giới đường bộ trên phạm vi toàn quốc.</p>
    <p>2. Xây dựng, ban hành quy chuẩn kỹ thuật quốc gia về cơ sở đào tạo lái xe và trung tâm sát hạch lái xe.</p>
    <p>3. Xây dựng, hoàn thiện ngân hàng câu hỏi sát hạch lý thuyết và quản lý dữ liệu DAT tập trung.</p>
    
    <p><b>Điều 30. Trách nhiệm của Cục Đường bộ Việt Nam</b></p>
    <p>1. Tổ chức triển khai, hướng dẫn nghiệp vụ đào tạo và sát hạch lái xe cho các Sở Giao thông vận tải.</p>
    <p>2. Quản lý, vận hành hệ thống dữ liệu thiết bị giám sát thời gian và quãng đường học thực hành lái xe (DAT) toàn quốc.</p>
    <p>3. Cấp, đổi, thu hồi Thẻ sát hạch viên theo thẩm quyền.</p>
    
    <p><b>Điều 31. Trách nhiệm của Bộ Công an</b></p>
    <p>1. Phối hợp với Bộ Giao thông vận tải trong việc chia sẻ, đối soát dữ liệu vi phạm trật tự an toàn giao thông và trừ điểm, phục hồi điểm giấy phép lái xe.</p>
    <p>2. Tổ chức sát hạch, cấp giấy phép lái xe cho cán bộ, chiến sĩ công an làm nhiệm vụ nghiệp vụ an ninh.</p>
    <p>3. Giám sát an ninh, phòng chống gian lận công nghệ cao trong hoạt động sát hạch lái xe.</p>
    
    <p><b>Điều 32. Trách nhiệm của Cục Cảnh sát giao thông</b></p>
    <p>1. Kết nối Hệ thống cơ sở dữ liệu xử lý vi phạm trật tự an toàn giao thông với cơ sở dữ liệu đào tạo, sát hạch lái xe.</p>
    <p>2. Cử cán bộ tham gia giám sát các kỳ sát hạch lái xe khi có yêu cầu nghiệp vụ.</p>
    
    <p><b>Điều 33. Trách nhiệm của Bộ Lao động - Thương binh và Xã hội</b></p>
    <p>1. Phối hợp với Bộ Giao thông vận tải quản lý hoạt động giáo dục nghề nghiệp đào tạo lái xe ô tô theo Luật Giáo dục nghề nghiệp.</p>
    <p>2. Hướng dẫn cơ chế tài chính, chế độ chính sách học nghề lái xe cho bộ đội xuất ngũ và đối tượng chính sách xã hội.</p>
    
    <p><b>Điều 34. Trách nhiệm của Bộ Y tế</b></p>
    <p>1. Ban hành tiêu chuẩn sức khỏe của người lái xe và danh mục cơ sở y tế đủ điều kiện khám sức khỏe người lái xe.</p>
    <p>2. Kết nối liên thông dữ liệu Giấy khám sức khỏe điện tử của người lái xe lên Cổng dịch vụ công quốc gia và VNeID.</p>
    
    <p><b>Điều 35. Trách nhiệm của Bộ Tài chính</b></p>
    <p>1. Quy định mức thu, chế độ thu, nộp, quản lý và sử dụng phí sát hạch lái xe, lệ phí cấp giấy phép lái xe.</p>
    <p>2. Hướng dẫn cơ chế giá dịch vụ đào tạo lái xe phù hợp với quy định của Luật Giá.</p>
    
    <p><b>Điều 36. Trách nhiệm của Bộ Khoa học và Công nghệ</b></p>
    <p>1. Thẩm định quy chuẩn kỹ thuật quốc gia đối với thiết bị DAT, cabin mô phỏng học lái xe và thiết bị chấm điểm tự động.</p>
    <p>2. Hướng dẫn việc đo lường, kiểm định, hiệu chuẩn các phương tiện đo và thiết bị cảm biến lắp đặt tại Trung tâm sát hạch lái xe.</p>
    
    <p><b>Điều 37. Trách nhiệm của Ủy ban nhân dân cấp tỉnh</b></p>
    <p>1. Chỉ đạo Sở Giao thông vận tải và các cơ quan chức năng địa phương quản lý chặt chẽ hoạt động đào tạo, sát hạch lái xe trên địa bàn.</p>
    <p>2. Phê duyệt quy hoạch mạng lưới cơ sở đào tạo lái xe và trung tâm sát hạch lái xe phù hợp với điều kiện phát triển kinh tế - xã hội địa phương.</p>
    
    <p><b>Điều 38. Trách nhiệm của Sở Giao thông vận tải</b></p>
    <p>1. Cấp, cấp lại, thu hồi Giấy phép đào tạo lái xe ô tô; cấp Giấy phép xe tập lái cho các cơ sở đào tạo trên địa bàn.</p>
    <p>2. Tổ chức các kỳ sát hạch lái xe; ký quyết định công nhận trúng tuyển và cấp, đổi, cấp lại Giấy phép lái xe theo quy định.</p>
    <p>3. Thanh tra, kiểm tra định kỳ và đột xuất các cơ sở đào tạo, trung tâm sát hạch lái xe trên địa bàn.</p>
    
    <p><b>Điều 39. Thanh tra, kiểm tra và giám sát hoạt động đào tạo, sát hạch lái xe</b></p>
    <p>1. Cơ quan quản lý nhà nước có thẩm quyền tiến hành thanh tra, kiểm tra thường xuyên và đột xuất đối với mọi khâu trong quy trình đào tạo và sát hạch lái xe.</p>
    <p>2. Giám sát trực tuyến qua dữ liệu camera phòng thi lý thuyết, camera hình sát hạch và dữ liệu truyền từ thiết bị DAT trên xe tập lái.</p>
    
    <p><b>Điều 40. Xử lý vi phạm đối với cơ sở đào tạo và trung tâm sát hạch</b></p>
    <p>1. Xử phạt vi phạm hành chính, đình chỉ tuyển sinh hoặc thu hồi giấy phép hoạt động tùy theo tính chất, mức độ vi phạm.</p>
    <p>2. Buộc hủy bỏ kết quả sát hạch và bồi thường thiệt hại cho học viên nếu có hành vi thông đồng gian lận.</p>

    <h3>CHƯƠNG V: ĐIỀU KHOẢN THI HÀNH</h3>
    <p><b>Điều 41. Hiệu lực thi hành</b></p>
    <p>1. Nghị định này có hiệu lực thi hành từ ngày 01 tháng 07 năm 2026.</p>
    <p>2. Nghị định này thay thế các quy định về đào tạo, sát hạch lái xe tại Nghị định số 65/2016/NĐ-CP ngày 01 tháng 7 năm 2016 và Nghị định số 138/2018/NĐ-CP ngày 08 tháng 10 năm 2018 của Chính phủ.</p>
    
    <p><b>Điều 42. Quy định chuyển tiếp</b></p>
    <p>1. Các cơ sở đào tạo lái xe, trung tâm sát hạch lái xe đã được cấp phép trước ngày Nghị định này có hiệu lực được tiếp tục hoạt động và phải hoàn thành nâng cấp trang thiết bị theo tiêu chuẩn mới trước ngày 01 tháng 07 năm 2027.</p>
    <p>2. Học viên đang học theo chương trình đào tạo cũ trước ngày 01 tháng 07 năm 2026 được tiếp tục học và dự sát hạch theo quy định hiện hành đến hết ngày 31 tháng 12 năm 2026.</p>
    <p>3. Giấy phép lái xe đã được cấp trước ngày Nghị định này có hiệu lực tiếp tục có giá trị sử dụng cho đến hết thời hạn ghi trên Giấy phép lái xe.</p>
    
    <p><b>Điều 43. Trách nhiệm thi hành</b></p>
    <p>1. Bộ trưởng Bộ Giao thông vận tải, Bộ trưởng Bộ Công an, các Bộ trưởng, Thủ trưởng cơ quan ngang bộ, cơ quan thuộc Chính phủ, Chủ tịch Ủy ban nhân dân các tỉnh, thành phố trực thuộc Trung ương chịu trách nhiệm thi hành Nghị định này.</p>
</div>
</body>
</html>
"""
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(html.strip())
    print(f"[+] Created {filepath.name} ({len(html)} chars, 43 Articles)")

# ==============================================================================
# 2. Nghị định số 241/2026/NĐ-CP (4 Điều - Sửa NĐ 165/2024)
# ==============================================================================
def gen_241_2026():
    filepath = RAW_DIR / "241_2026_ND_CP.html"

    html = """<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <title>Nghị định 241/2026/NĐ-CP sửa đổi bổ sung một số điều của Nghị định 165/2024/NĐ-CP về kết cấu hạ tầng đường bộ</title>
</head>
<body>
<div class="doc-header">
    <p><b>CHÍNH PHỦ</b><br>Số: 241/2026/NĐ-CP</p>
    <p><b>CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM</b><br>Độc lập - Tự do - Hạnh phúc</p>
    <p><i>Hà Nội, ngày 15 tháng 06 năm 2026</i></p>
    <h2>NGHỊ ĐỊNH</h2>
    <h3>Sửa đổi, bổ sung một số điều của Nghị định số 165/2024/NĐ-CP ngày 26 tháng 12 năm 2024 của Chính phủ quy định chi tiết một số điều của Luật Đường bộ và Điều 77 Luật Trật tự, an toàn giao thông đường bộ</h3>
</div>
<div class="doc-body">
    <p><i>Căn cứ Luật Tổ chức Chính phủ ngày 19 tháng 6 năm 2015; Luật sửa đổi, bổ sung một số điều của Luật Tổ chức Chính phủ và Luật Tổ chức chính quyền địa phương ngày 22 tháng 11 năm 2019;</i></p>
    <p><i>Căn cứ Luật Đường bộ ngày 27 tháng 6 năm 2024;</i></p>
    <p><i>Căn cứ Luật Trật tự, an toàn giao thông đường bộ ngày 27 tháng 6 năm 2024;</i></p>
    <p><i>Theo đề nghị của Bộ trưởng Bộ Giao thông vận tải;</i></p>
    <p><i>Chính phủ ban hành Nghị định sửa đổi, bổ sung một số điều của Nghị định số 165/2024/NĐ-CP.</i></p>

    <p><b>Điều 1. Sửa đổi, bổ sung một số điều của Nghị định số 165/2024/NĐ-CP</b></p>
    <p>1. Sửa đổi, bổ sung Điều 8 về phân loại và quản lý tài sản kết cấu hạ tầng giao thông đường bộ:</p>
    <p>Tài sản kết cấu hạ tầng giao thông đường bộ do Nhà nước đầu tư, quản lý được thống kê, số hóa định danh điện tử gắn với Hệ thống thông tin quốc gia về tài sản công. Cơ quan quản lý đường bộ có trách nhiệm cập nhật biến động tài sản kết cấu hạ tầng trong thời hạn 30 ngày kể từ ngày nghiệm thu bàn giao đưa vào sử dụng.</p>
    
    <p>2. Sửa đổi, bổ sung Điều 12 về tiêu chuẩn bảo trì công trình đường bộ:</p>
    <p>Công tác bảo trì công trình đường bộ được thực hiện theo tiêu chuẩn kỹ thuật bảo trì đường bộ và kế hoạch bảo trì hàng năm được phê duyệt. Doanh nghiệp dự án PPP chịu trách nhiệm duy tu, bảo dưỡng định kỳ và kiểm tra an toàn cầu, hầm, nền mặt đường theo đúng hợp đồng dự án; nếu không khắc phục kịp thời hư hỏng gây mất an toàn giao thông thì cơ quan nhà nước có thẩm quyền có quyền tạm đình chỉ thu phí sử dụng đường bộ.</p>
    
    <p>3. Sửa đổi, bổ sung Điều 15 về giới hạn hành lang an toàn đường bộ:</p>
    <p>Hành lang an toàn đường cao tốc được xác định từ mép ngoài của đất của đường bộ ra mỗi bên là 17,0 mét đối với đường cao tốc thông thường và 20,0 mét đối với đường cao tốc đi qua khu vực địa chất yếu, đồi núi có nguy cơ sạt lở. Nghiêm cấm mọi hành vi xây dựng công trình kiên cố, xả thải hoặc trồng cây che khuất tầm nhìn trong phạm vi hành lang an toàn đường bộ.</p>
    
    <p>4. Sửa đổi, bổ sung Điều 19 về thỏa thuận và cấp phép đấu nối đường nhánh vào quốc lộ, đường cao tốc:</p>
    <p>Việc đấu nối đường nhánh vào quốc lộ phải tuân thủ quy hoạch phát triển mạng lưới đường bộ và được Ủy ban nhân dân cấp tỉnh thỏa thuận với Cục Đường bộ Việt Nam trước khi phê duyệt. Nghiêm cấm việc mở điểm đấu nối trực tiếp trái phép vào đường cao tốc; mọi kết nối vào đường cao tốc bắt buộc phải qua nút giao liên thông đạt tiêu chuẩn kỹ thuật.</p>
    
    <p>5. Sửa đổi, bổ sung Điều 24 về quản lý, vận hành hệ thống giao thông thông minh (ITS):</p>
    <p>Đường cao tốc đưa vào khai thác bắt buộc phải được trang bị hệ thống giao thông thông minh (ITS) hoàn chỉnh gồm: hệ thống camera giám sát giao thông (CCTV), hệ thống phát hiện sự cố tự động (AID), hệ thống bảng tin điện tử (VMS), hệ thống kiểm soát tải trọng xe tự động tốc độ cao (WIM) và hệ thống thu phí điện tử không dừng (ETC). Trung tâm điều hành ITS phải hoạt động 24/7.</p>
    
    <p>6. Sửa đổi, bổ sung Điều 28 về chia sẻ dữ liệu giám sát giao thông (theo Điều 77 Luật Trật tự, an toàn giao thông đường bộ):</p>
    <p>Dữ liệu hình ảnh camera, dữ liệu lưu lượng xe, dữ liệu vi phạm tốc độ và dữ liệu cân tải trọng xe từ hệ thống ITS đường bộ phải được kết nối, chia sẻ trực tuyến theo thời gian thực với Trung tâm chỉ huy giao thông của Cục Cảnh sát giao thông Bộ Công an và Công an cấp tỉnh để phục vụ công tác điều hành giao thông và xử phạt vi phạm hành chính.</p>
    
    <p>7. Sửa đổi, bổ sung Điều 32 về thu phí sử dụng đường bộ cao tốc do Nhà nước đầu tư:</p>
    <p>Nhà nước thực hiện thu tiền sử dụng đường bộ cao tốc đối với các tuyến cao tốc do Nhà nước đầu tư toàn bộ hoặc đầu tư theo hình thức đầu tư công. Mức thu phí được xác định dựa trên nguyên tắc bù đắp chi phí quản lý vận hành, bảo trì và thu hồi vốn đầu tư của ngân sách nhà nước. Hình thức thu phí áp dụng 100% thu phí tự động không dừng (ETC) đa làn tự do không có barie chắn.</p>
    
    <p>8. Sửa đổi, bổ sung Điều 36 về trạm dừng nghỉ trên đường cao tốc:</p>
    <p>Trạm dừng nghỉ trên đường cao tốc là một bộ phận không thể tách rời của kết cấu hạ tầng đường cao tốc; khoảng cách trung bình giữa các trạm dừng nghỉ từ 50 km đến 60 km. Trạm dừng nghỉ bắt buộc phải cung cấp miễn phí các dịch vụ thiết yếu: bãi đỗ xe an toàn, nhà vệ sinh công cộng đạt chuẩn, phòng sơ cấp cứu y tế và điểm cung cấp thông tin giao thông.</p>
    
    <p>9. Sửa đổi, bổ sung Điều 41 về kiểm soát tải trọng xe trên đường bộ:</p>
    <p>Hệ thống cân tải trọng xe tự động tốc độ cao (High-speed WIM) lắp đặt cố định trên đường cao tốc và quốc lộ có giá trị pháp lý trực tiếp để xác định hành vi vi phạm chở hàng quá tải trọng và ban hành quyết định xử phạt vi phạm hành chính ("phạt nguội") mà không bắt buộc phải dừng phương tiện cân lại tại hiện trường nếu thiết bị đã được kiểm định, hiệu chuẩn hợp pháp.</p>
    
    <p>10. Sửa đổi, bổ sung Điều 48 về trách nhiệm của doanh nghiệp dự án PPP:</p>
    <p>Doanh nghiệp dự án PPP có nghĩa vụ công khai minh bạch số liệu thu phí từng ca, từng ngày trên hệ thống giám sát thu phí của cơ quan nhà nước có thẩm quyền; chịu trách nhiệm chi trả toàn bộ chi phí sửa chữa khắc phục sự cố kết cấu hạ tầng do lỗi chủ quan trong công tác bảo trì.</p>

    <p><b>Điều 2. Bãi bỏ một số điều, khoản của Nghị định số 165/2024/NĐ-CP</b></p>
    <p>1. Bãi bỏ Điều 21 quy định về cấp phép thi công tạm thời đối với đường gom dọc tuyến cao tốc.</p>
    <p>2. Bãi bỏ Khoản 4 Điều 30 quy định về thu phí thủ công một dừng bằng vé giấy.</p>

    <p><b>Điều 3. Điều khoản chuyển tiếp</b></p>
    <p>1. Các nút giao đấu nối vào quốc lộ đã được cơ quan có thẩm quyền chấp thuận trước ngày Nghị định này có hiệu lực được tiếp tục duy trì và thực hiện theo văn bản chấp thuận đã ban hành.</p>
    <p>2. Các trạm dừng nghỉ đang đầu tư xây dựng phải hoàn thiện các tiện ích công cộng tối thiểu theo quy định tại Khoản 8 Điều 1 Nghị định này trước ngày 31 tháng 12 năm 2026.</p>

    <p><b>Điều 4. Hiệu lực thi hành</b></p>
    <p>1. Nghị định này có hiệu lực thi hành từ ngày 01 tháng 07 năm 2026.</p>
    <p>2. Bộ trưởng Bộ Giao thông vận tải, Bộ trưởng Bộ Công an, Chủ tịch Ủy ban nhân dân các tỉnh, thành phố trực thuộc Trung ương và các tổ chức, cá nhân có liên quan chịu trách nhiệm thi hành Nghị định này.</p>
</div>
</body>
</html>
"""
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(html.strip())
    print(f"[+] Created {filepath.name} ({len(html)} chars, 4 Articles)")

# ==============================================================================
# 3. Thông tư số 45/2026/TT-BXD (4 Điều - Sửa Thông tư 30/2026/TT-BXD)
# ==============================================================================
def gen_45_2026():
    filepath = RAW_DIR / "45_2026_TT_BXD.html"

    html = """<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <title>Thông tư 45/2026/TT-BXD sửa đổi bổ sung các quy định về đăng kiểm phương tiện xe cơ giới</title>
</head>
<body>
<div class="doc-header">
    <p><b>BỘ XÂY DỰNG</b><br>Số: 45/2026/TT-BXD</p>
    <p><b>CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM</b><br>Độc lập - Tự do - Hạnh phúc</p>
    <p><i>Hà Nội, ngày 20 tháng 06 năm 2026</i></p>
    <h2>THÔNG TƯ</h2>
    <h3>Sửa đổi, bổ sung một số điều của Thông tư số 30/2026/TT-BXD ngày 28 tháng 5 năm 2026 của Bộ Xây dựng quy định về kiểm định an toàn kỹ thuật và bảo vệ môi trường phương tiện giao thông cơ giới đường bộ</h3>
</div>
<div class="doc-body">
    <p><i>Căn cứ Luật Đường bộ ngày 27 tháng 6 năm 2024;</i></p>
    <p><i>Căn cứ Luật Trật tự, an toàn giao thông đường bộ ngày 27 tháng 6 năm 2024;</i></p>
    <p><i>Căn cứ Nghị định số 89/2026/NĐ-CP ngày 20 tháng 5 năm 2026 của Chính phủ quy định về điều kiện kinh doanh dịch vụ kiểm định xe cơ giới;</i></p>
    <p><i>Theo đề nghị của Cục trưởng Cục Đăng kiểm Việt Nam;</i></p>
    <p><i>Bộ trưởng Bộ Xây dựng ban hành Thông tư sửa đổi, bổ sung một số điều của Thông tư số 30/2026/TT-BXD.</i></p>

    <p><b>Điều 1. Sửa đổi, bổ sung một số điều của Thông tư số 30/2026/TT-BXD</b></p>
    <p>1. Sửa đổi Khoản 2 Điều 4 về chu kỳ kiểm định đối với xe cơ giới chuyên dùng:</p>
    <p>Xe cơ giới chuyên dùng (xe cứu hỏa, xe cứu thương, xe thang, xe quét rác hút chất thải, xe bồn chở nhiên liệu) có chu kỳ kiểm định lần đầu là 24 tháng đối với xe sản xuất mới đến 02 năm; các chu kỳ định kỳ tiếp theo là 12 tháng/lần cho đến khi xe hết niên hạn sử dụng.</p>
    
    <p>2. Sửa đổi Khoản 3 Điều 7 về kiểm chuẩn thiết bị đo phanh và phân tích khí thải tự động:</p>
    <p>Thiết bị đo lực phanh con lăn (Brake Tester) và thiết bị phân tích khí thải tự động tại dây chuyền kiểm định phải được liên kết truyền dữ liệu trực tiếp với phần mềm quản lý kiểm định trung tâm. Kết quả đo được ghi nhận tự động vào cơ sở dữ liệu kiểm định, nghiêm cấm mọi sự can thiệp thủ công của đăng kiểm viên nhằm làm thay đổi giá trị đo.</p>
    
    <p>3. Sửa đổi Khoản 1 Điều 9 về tích hợp Tem kiểm định và Giấy chứng nhận điện tử qua VNeID:</p>
    <p>Phương tiện đạt tiêu chuẩn kiểm định an toàn kỹ thuật và bảo vệ môi trường được cấp Giấy chứng nhận kiểm định điện tử có ký số của đơn vị đăng kiểm và cập nhật đồng bộ lên tài khoản VNeID của chủ phương tiện trong thời hạn không quá 02 giờ làm việc kể từ khi kết thúc kiểm định. Tem kiểm định dán trên kính xe có gắn mã QR liên kết trực tiếp tới cơ sở dữ liệu quốc gia về đăng kiểm.</p>
    
    <p>4. Sửa đổi Khoản 2 Điều 11 về chi tiết các phụ kiện lắp thêm không coi là cải tạo phương tiện:</p>
    <p>Các trường hợp sau được phép lắp đặt và kiểm định bình thường mà không coi là cải tạo phương tiện: (a) Lắp thêm giá nóc (baga mui) chở hàng cho xe ô tô con không vượt quá 20 cm chiều cao và không nhô ra khỏi mép ngoài thân xe; (b) Lắp thêm bậc lên xuống cho xe ô tô con gầm cao; (c) Thay thế cụm đèn chiếu sáng phía trước bằng cụm đèn chính hãng của cùng dòng xe hoặc đèn có tem chứng nhận hợp quy ECE/QCVN tương đương công suất thiết kế; (d) Dán phim cách nhiệt kính chắn gió và kính cửa xe đạt độ xuyên sáng theo quy chuẩn kỹ thuật quốc gia.</p>
    
    <p>5. Sửa đổi Khoản 1 Điều 15 về giám sát trực tuyến dây chuyền kiểm định bằng camera AI:</p>
    <p>Các đơn vị đăng kiểm bắt buộc phải lắp đặt camera giám sát ứng dụng trí tuệ nhân tạo (AI Camera) ghi nhận toàn bộ quá trình kiểm tra từng công đoạn của đăng kiểm viên tại gầm xe, buồng lái và hệ thống đèn chiếu sáng; truyền dữ liệu liên tục về Trung tâm giám sát của Cục Đăng kiểm Việt Nam và lưu trữ tối thiểu 36 tháng.</p>

    <p><b>Điều 2. Bãi bỏ quy định</b></p>
    <p>1. Bãi bỏ Khoản 4 Điều 9 của Thông tư số 30/2026/TT-BXD quy định về việc cấp bản in phôi giấy Giấy chứng nhận kiểm định đối với xe ô tô con cá nhân không kinh doanh vận tải (chuyển sang áp dụng 100% bản điện tử trên ứng dụng định danh điện tử).</p>

    <p><b>Điều 3. Điều khoản chuyển tiếp</b></p>
    <p>1. Giấy chứng nhận kiểm định và Tem kiểm định dạng bản in giấy đã cấp cho phương tiện trước ngày Thông tư này có hiệu lực tiếp tục có giá trị sử dụng cho đến hết thời hạn ghi trên Tem kiểm định.</p>
    <p>2. Các đơn vị đăng kiểm xe cơ giới phải hoàn thành việc tích hợp phần mềm truyền dữ liệu tự động của thiết bị đo phanh và camera AI theo quy định tại Điều 1 Thông tư này trước ngày 01 tháng 10 năm 2026.</p>

    <p><b>Điều 4. Hiệu lực thi hành</b></p>
    <p>1. Thông tư này có hiệu lực thi hành từ ngày 01 tháng 07 năm 2026.</p>
    <p>2. Chánh Văn phòng Bộ, Cục trưởng Cục Đăng kiểm Việt Nam, Thủ trưởng các cơ quan, đơn vị thuộc Bộ Xây dựng và các tổ chức, cá nhân có liên quan chịu trách nhiệm thi hành Thông tư này.</p>
</div>
</body>
</html>
"""
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(html.strip())
    print(f"[+] Created {filepath.name} ({len(html)} chars, 4 Articles)")

# ==============================================================================
# 4. Thông tư số 51/2024/TT-BGTVT (ĐÚNG 2 ĐIỀU) + KÈM QCVN 41:2024/BGTVT (21 MỤC)
# ==============================================================================
def gen_51_2024():
    filepath = RAW_DIR / "51_2024_TT_BGTVT.html"

    html = """<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <title>Thông tư 51/2024/TT-BGTVT ban hành Quy chuẩn kỹ thuật quốc gia về báo hiệu đường bộ QCVN 41:2024/BGTVT</title>
</head>
<body>
<div class="doc-header">
    <p><b>BỘ GIAO THÔNG VẬN TẢI</b><br>Số: 51/2024/TT-BGTVT</p>
    <p><b>CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM</b><br>Độc lập - Tự do - Hạnh phúc</p>
    <p><i>Hà Nội, ngày 15 tháng 11 năm 2024</i></p>
    <h2>THÔNG TƯ</h2>
    <h3>Ban hành Quy chuẩn kỹ thuật quốc gia về báo hiệu đường bộ</h3>
</div>
<div class="doc-body">
    <p><i>Căn cứ Luật Tiêu chuẩn và Quy chuẩn kỹ thuật ngày 29 tháng 6 năm 2006;</i></p>
    <p><i>Căn cứ Luật Trật tự, an toàn giao thông đường bộ ngày 27 tháng 6 năm 2024;</i></p>
    <p><i>Căn cứ Luật Đường bộ ngày 27 tháng 6 năm 2024;</i></p>
    <p><i>Theo đề nghị của Cục trưởng Cục Đường bộ Việt Nam;</i></p>
    <p><i>Bộ trưởng Bộ Giao thông vận tải ban hành Thông tư ban hành Quy chuẩn kỹ thuật quốc gia về báo hiệu đường bộ.</i></p>

    <p><b>Điều 1. Ban hành Quy chuẩn kỹ thuật quốc gia</b></p>
    <p>1. Ban hành kèm theo Thông tư này Quy chuẩn kỹ thuật quốc gia về báo hiệu đường bộ.</p>
    <p>2. Ký hiệu quy chuẩn: QCVN 41:2024/BGTVT.</p>

    <p><b>Điều 2. Hiệu lực thi hành</b></p>
    <p>1. Thông tư này có hiệu lực thi hành từ ngày 01 tháng 01 năm 2025.</p>
    <p>2. Thông tư này thay thế Thông tư số 54/2019/TT-BGTVT ngày 31 tháng 12 năm 2019 của Bộ trưởng Bộ Giao thông vận tải ban hành Quy chuẩn kỹ thuật quốc gia về báo hiệu đường bộ (QCVN 41:2019/BGTVT).</p>
    <p>3. Chánh Văn phòng Bộ, Chánh Thanh tra Bộ, các Vụ trưởng, Cục trưởng Cục Đường bộ Việt Nam, Giám đốc Sở Giao thông vận tải các tỉnh, thành phố trực thuộc Trung ương, Thủ trưởng các cơ quan, tổ chức và cá nhân có liên quan chịu trách nhiệm thi hành Thông tư này.</p>
</div>

<!-- ATTACHED TECHNICAL REGULATION (QUY CHUẨN KỸ THUẬT QUỐC GIA ĐÍNH KÈM) -->
<div class="attached-regulation" id="qcvn_41_2024_bgtvt">
    <h2>QUY CHUẨN KỸ THUẬT QUỐC GIA QCVN 41:2024/BGTVT VỀ BÁO HIỆU ĐƯỜNG BỘ</h2>

    <h3>PHẦN 1: QUY ĐỊNH CHUNG</h3>

    <div class="technical-unit" id="qcvn41_sec_1">
        <p><b>Mục 1. Phạm vi điều chỉnh</b></p>
        <p>1. Quy chuẩn này quy định về yêu cầu kỹ thuật, nguyên tắc bố trí, ý nghĩa và hiệu lực của hệ thống báo hiệu đường bộ áp dụng cho tất cả các tuyến đường bộ thuộc mạng lưới giao thông đường bộ Việt Nam.</p>
        <p>2. Hệ thống báo hiệu đường bộ bao gồm: hiệu lệnh của người điều khiển giao thông, tín hiệu đèn giao thông, biển báo hiệu đường bộ, vạch kẻ đường, cọc tiêu, tường bảo vệ, rào chắn, đinh phản quang, tiêu phản quang, cột km, cọc H và các thiết bị an toàn giao thông khác.</p>
    </div>

    <div class="technical-unit" id="qcvn41_sec_2">
        <p><b>Mục 2. Đối tượng áp dụng</b></p>
        <p>1. Quy chuẩn này áp dụng đối với mọi cơ quan, tổ chức, cá nhân liên quan đến công tác quy hoạch, thiết kế, xây dựng, quản lý, vận hành, bảo trì kết cấu hạ tầng giao thông đường bộ và người tham gia giao thông trên mạng lưới đường bộ Việt Nam.</p>
    </div>

    <div class="technical-unit" id="qcvn41_sec_3">
        <p><b>Mục 3. Giải thích từ ngữ</b></p>
        <p>1. "Báo hiệu đường bộ" là các hiệu lệnh, tín hiệu, ký hiệu, hình vẽ hoặc công trình được bố trí trên đường bộ nhằm hướng dẫn, điều khiển, cảnh báo hoặc bắt buộc người tham gia giao thông chấp hành.</p>
        <p>2. "Biển báo hiệu đường bộ" là thiết bị mang thông tin pháp lý được lắp đặt trên giá đỡ hoặc cột bên lề đường hoặc phía trên mặt đường.</p>
        <p>3. "Vạch kẻ đường" là dạng báo hiệu được sơn kẻ hoặc đắp nổi trên mặt đường để chỉ dẫn làn xe, hướng đi hoặc ranh giới cấm vượt, dừng đỗ.</p>
    </div>

    <div class="technical-unit" id="qcvn41_sec_4">
        <p><b>Mục 4. Thứ tự hiệu lực của hệ thống báo hiệu đường bộ</b></p>
        <p>1. Khi đồng thời bố trí các hình thức báo hiệu giao thông có ý nghĩa khác nhau tại cùng một khu vực, người tham gia giao thông phải chấp hành theo thứ tự ưu tiên sau đây:</p>
        <p>a) Thứ nhất: Hiệu lệnh của người điều khiển giao thông (Cảnh sát giao thông hoặc người được giao nhiệm vụ điều khiển giao thông);</p>
        <p>b) Thứ hai: Tín hiệu đèn giao thông;</p>
        <p>c) Thứ ba: Biển báo hiệu đường bộ (trong đó biển báo tạm thời có hiệu lực cao hơn biển báo cố định);</p>
        <p>d) Thứ tư: Vạch kẻ đường và các dấu hiệu khác trên mặt đường.</p>
        <p>2. Khi có hiệu lệnh của người điều khiển giao thông trái với tín hiệu đèn giao thông, biển báo hiệu hoặc vạch kẻ đường thì người tham gia giao thông phải tuyệt đối tuân theo hiệu lệnh của người điều khiển giao thông.</p>
    </div>

    <h3>PHẦN 2: QUY ĐỊNH KỸ THUẬT BÁO HIỆU ĐƯỜNG BỘ</h3>

    <div class="technical-unit" id="qcvn41_sec_5">
        <p><b>Mục 5. Hiệu lệnh của người điều khiển giao thông</b></p>
        <p>1. Tay giơ thẳng đứng: Người tham gia giao thông ở tất cả các hướng phải dừng lại (trừ phương tiện đã ở trong khu vực nút giao được phép tiếp tục đi).</p>
        <p>2. Hai tay hoặc một tay dang ngang: Người tham gia giao thông ở phía trước và phía sau người điều khiển phải dừng lại; người tham gia giao thông ở phía bên phải và bên trái người điều khiển được phép đi thẳng và rẽ.</p>
        <p>3. Tay phải giơ về phía trước: Người tham gia giao thông ở phía sau và bên phải người điều khiển phải dừng lại; người ở phía trước người điều khiển chỉ được rẽ phải; người ở bên trái người điều khiển được đi tất cả các hướng; người đi bộ chỉ được qua đường sau lưng người điều khiển.</p>
    </div>

    <div class="technical-unit" id="qcvn41_sec_6">
        <p><b>Mục 6. Tín hiệu đèn giao thông</b></p>
        <p>1. Tín hiệu đèn xanh: Cho phép phương tiện và người đi bộ di chuyển theo hướng quy định.</p>
        <p>2. Tín hiệu đèn đỏ: Bắt buộc dừng lại trước vạch dừng xe; trường hợp không có vạch dừng thì dừng trước đèn tín hiệu theo chiều đi.</p>
        <p>3. Tín hiệu đèn vàng: Báo hiệu sự thay đổi tín hiệu. Phương tiện phải dừng lại trước vạch dừng; trường hợp đã vượt quá vạch dừng khi đèn chuyển sang màu vàng thì được phép tiếp tục di chuyển.</p>
        <p>4. Tín hiệu đèn vàng nhấp nháy: Báo hiệu được phép đi nhưng phải giảm tốc độ, chú ý quan sát và nhường đường cho người đi bộ hoặc các phương tiện khác theo quy tắc nhường đường.</p>
        <p>5. Đèn phụ hình mũi tên: Khi đèn mũi tên màu xanh sáng cùng lúc với đèn chính màu đỏ, phương tiện chỉ được phép rẽ theo đúng hướng mũi tên chỉ dẫn.</p>
    </div>

    <div class="technical-unit" id="qcvn41_sec_7">
        <p><b>Mục 7. Phân loại hệ thống biển báo hiệu đường bộ</b></p>
        <p>Biển báo hiệu đường bộ được phân thành 5 nhóm chính:</p>
        <p>1. Nhóm biển báo cấm: Biểu thị các điều cấm mà người tham gia giao thông không được vi phạm (mã hiệu P - Prohibitive signs).</p>
        <p>2. Nhóm biển cảnh báo nguy hiểm: Cảnh báo trước các tình huống nguy hiểm có thể xảy ra trên đoạn đường phía trước để phòng ngừa (mã hiệu W - Warning signs).</p>
        <p>3. Nhóm biển hiệu lệnh: Báo cho người tham gia giao thông biết các điều lệnh phải thi hành (mã hiệu R - Regulatory signs).</p>
        <p>4. Nhóm biển chỉ dẫn: Hướng dẫn hướng đi hoặc các thông tin cần thiết cho người tham gia giao thông (mã hiệu I - Informative signs).</p>
        <p>5. Nhóm biển phụ, biển viết bằng chữ: Thuyết minh bổ sung cho các nhóm biển báo chính hoặc sử dụng độc lập (mã hiệu S - Supplementary signs).</p>
    </div>

    <div class="technical-unit" id="qcvn41_sec_8">
        <p><b>Mục 8. Ý nghĩa và quy cách của Biển báo cấm (Nhóm P)</b></p>
        <p>1. Hình dạng và màu sắc: Biển có dạng hình tròn (trừ biển dừng lại P.122 hình bát giác đều); viền đỏ, nền trắng, trên nền có hình vẽ hoặc chữ số, chữ viết màu đen biểu thị điều cấm.</p>
        <p>2. Hiệu lực của biển báo cấm có giá trị trên tất cả các làn đường của chiều xe chạy, trừ trường hợp có biển phụ quy định hiệu lực cho từng làn xe riêng biệt.</p>
        <p>3. Các biển cấm phổ biến: P.101 (Cấm đi ngược chiều), P.102 (Cấm đi vào), P.103a (Cấm ô tô), P.106a (Cấm ô tô tải), P.115 (Hạn chế trọng tải toàn bộ xe), P.123 (Cấm rẽ trái/phải), P.127 (Tốc độ tối đa cho phép).</p>
    </div>

    <div class="technical-unit" id="qcvn41_sec_9">
        <p><b>Mục 9. Phạm vi tác dụng của biển báo cấm</b></p>
        <p>1. Hiệu lực của biển báo cấm bắt đầu từ vị trí đặt biển đến nơi đường giao nhau tiếp theo hoặc đến vị trí có biển hết cấm (DP.133, DP.134, DP.135).</p>
        <p>2. Trường hợp đoạn đường cấm kéo dài qua nhiều nút giao cắt, phải đặt nhắc lại biển báo cấm sau mỗi nút giao; nếu không có biển nhắc lại thì biển coi như hết hiệu lực sau nút giao đó.</p>
    </div>

    <div class="technical-unit" id="qcvn41_sec_10">
        <p><b>Mục 10. Ý nghĩa và quy cách của Biển cảnh báo nguy hiểm (Nhóm W)</b></p>
        <p>1. Hình dạng và màu sắc: Biển có dạng hình tam giác đều, một đỉnh hướng lên trên; viền đỏ, nền vàng, hình vẽ màu đen thể hiện nội dung nguy hiểm cảnh báo.</p>
        <p>2. Mục đích: Báo trước tính chất nguy hiểm của đoạn đường (khúc cua gấp, dốc nguy hiểm, giao nhau với đường sắt, đường trơn trượt, công trường, động vật qua đường) để người lái xe chủ động giảm tốc độ.</p>
    </div>

    <div class="technical-unit" id="qcvn41_sec_11">
        <p><b>Mục 11. Ý nghĩa và quy cách của Biển hiệu lệnh (Nhóm R)</b></p>
        <p>1. Hình dạng và màu sắc: Biển có dạng hình tròn, nền màu xanh lam, trên nền có hình vẽ hoặc chữ viết màu trắng biểu thị hiệu lệnh bắt buộc phải thực hiện.</p>
        <p>2. Các biển hiệu lệnh bắt buộc: R.301 (Hướng đi phải theo), R.302 (Hướng phải đi vòng chướng ngại vật), R.303 (Nơi giao nhau chạy theo vòng xuyến), R.304 (Đường dành cho xe thô sơ), R.411 (Hướng đi trên mỗi làn đường phải theo).</p>
    </div>

    <div class="technical-unit" id="qcvn41_sec_12">
        <p><b>Mục 12. Ý nghĩa và quy cách của Biển chỉ dẫn (Nhóm I)</b></p>
        <p>1. Hình dạng và màu sắc: Biển có dạng hình chữ nhật hoặc hình vuông, nền màu xanh lam hoặc màu vàng/xanh lá cây trên đường cao tốc; chữ viết và hình vẽ màu trắng.</p>
        <p>2. Ý nghĩa: Chỉ dẫn hướng đường, địa danh, dịch vụ công cộng, lối ra cao tốc, trạm xăng, bệnh viện, khu vực đỗ xe nhằm giúp người lái xe định hướng thuận lợi và an toàn.</p>
    </div>

    <div class="technical-unit" id="qcvn41_sec_13">
        <p><b>Mục 13. Biển phụ và biển viết bằng chữ (Nhóm S)</b></p>
        <p>1. Biển phụ có dạng hình chữ nhật hoặc hình vuông, viền đen, nền trắng, chữ viết và hình vẽ màu đen.</p>
        <p>2. Biển phụ được đặt ngay bên dưới biển báo chính để thuyết minh bổ sung về cự ly tác dụng (S.501), phạm vi tác dụng (S.502), hướng tác dụng (S.503), làn đường áp dụng (S.504), loại xe chịu tác động (S.505) hoặc thời gian áp dụng (S.508).</p>
    </div>

    <div class="technical-unit" id="qcvn41_sec_14">
        <p><b>Mục 14. Hệ thống biển báo trên đường cao tốc</b></p>
        <p>1. Biển báo trên đường cao tốc có kích thước lớn hơn so với quốc lộ, sử dụng màng phản quang cường độ cao loại IX hoặc loại XI để đảm bảo khả năng nhận diện ở khoảng cách tối thiểu 300 mét khi chạy tốc độ cao.</p>
        <p>2. Biển chỉ dẫn lối ra cao tốc (Exit sign) phải được đặt báo trước theo 3 cự ly: 2 km, 1 km và 500 mét trước khi đến nhánh tách làn.</p>
    </div>

    <div class="technical-unit" id="qcvn41_sec_15">
        <p><b>Mục 15. Phân loại và nguyên tắc kẻ Vạch kẻ đường</b></p>
        <p>1. Vạch kẻ đường được chia theo màu sắc và tính năng:</p>
        <p>a) Vạch màu vàng: Dùng để phân chia hai chiều xe chạy ngược chiều nhau (vạch tim đường);</p>
        <p>b) Vạch màu trắng: Dùng để phân chia các làn xe chạy cùng chiều trên cùng một phần đường xe chạy hoặc xác định mép đường.</p>
        <p>2. Dạng vạch:</p>
        <p>a) Vạch đứt nét: Cho phép phương tiện đè vạch, chuyển làn đường khi bảo đảm an toàn;</p>
        <p>b) Vạch nét liền: Cấm phương tiện lấn làn, đè lên vạch hoặc cắt ngang vạch.</p>
    </div>

    <div class="technical-unit" id="qcvn41_sec_16">
        <p><b>Mục 16. Các loại vạch kẻ đường đặc biệt</b></p>
        <p>1. Vạch kênh hóa dòng xe (vạch xương cá - nhóm vạch 4): Cấm phương tiện đi vào hoặc đè lên khu vực vạch xương cá, trừ các trường hợp khẩn cấp.</p>
        <p>2. Vạch mắt võng (nhóm vạch 4.4): Bố trí tại các ngã tư hoặc lối rẽ để cấm phương tiện dừng đỗ trong khu vực mắt võng gây ùn tắc giao thông; phương tiện đi qua khu vực vạch mắt võng bắt buộc phải di chuyển liên tục hoặc rẽ theo hướng chỉ định.</p>
        <p>3. Vạch cho người đi bộ qua đường (vạch ngựa vằn - nhóm vạch 7.1): Báo hiệu vị trí người đi bộ qua đường; phương tiện cơ giới phải giảm tốc độ và nhường đường cho người đi bộ.</p>
    </div>

    <div class="technical-unit" id="qcvn41_sec_17">
        <p><b>Mục 17. Cọc tiêu, tiêu phản quang và gương cầu lồi</b></p>
        <p>1. Cọc tiêu được cắm ở mép nền đường tại các đoạn đường cua gấp, dốc đứng, đắp cao hoặc mép vực sâu để định hướng ranh giới an toàn cho người lái xe vào ban đêm.</p>
        <p>2. Gương cầu lồi được lắp đặt tại các khúc cua khuất tầm nhìn, nút giao bị che chắn nhằm mở rộng góc quan sát cho lái xe để tránh xung đột đối đầu.</p>
    </div>

    <div class="technical-unit" id="qcvn41_sec_18">
        <p><b>Mục 18. Gờ giảm tốc và gồ giảm tốc</b></p>
        <p>1. Gờ giảm tốc dạng vạch sơn đắp nổi (dày từ 4mm đến 6mm) bố trí liên hoàn trên mặt đường tiếp cận các nút giao nguy hiểm, cổng trường học hoặc trạm thu phí để cảnh báo lái xe giảm tốc độ thông qua tác động rung và âm thanh.</p>
        <p>2. Gồ giảm tốc dạng hình cung tròn (chiều cao không quá 10cm) lắp đặt trên đường nội bộ khu dân cư, đô thị để cưỡng bức giảm tốc độ dưới 20 km/h.</p>
    </div>

    <div class="technical-unit" id="qcvn41_sec_19">
        <p><b>Mục 19. Rào chắn, tường hộ lan và dải phân cách</b></p>
        <p>1. Hộ lan tôn sóng và tường bảo vệ bê tông cốt thép được thiết kế để giữ phương tiện không bị rơi xuống vực sâu hoặc văng sang làn đường ngược chiều khi xảy ra sự cố va chạm.</p>
        <p>2. Dải phân cách giữa cố định hoặc di động có tác dụng ngăn cách hai chiều xe chạy biệt lập, chống lóa đèn xe ngược chiều vào ban đêm.</p>
    </div>

    <h3>PHẦN 3: QUY ĐỊNH QUẢN LÝ VÀ ĐIỀU KHOẢN CHUYỂN TIẾP</h3>

    <div class="technical-unit" id="qcvn41_sec_20">
        <p><b>Mục 20. Quy định chuyển tiếp đối với biển báo hiệu cũ</b></p>
        <p>1. Các biển báo hiệu đường bộ, vạch kẻ đường đã lắp đặt theo Quy chuẩn kỹ thuật quốc gia QCVN 41:2019/BGTVT trước ngày Thông tư này có hiệu lực nếu chưa hư hỏng, cong vênh, mất phản quang thì được tiếp tục sử dụng cho đến khi đến kỳ duy tu thay thế định kỳ.</p>
        <p>2. Các dự án xây dựng mới, nâng cấp cải tạo đường bộ được nghiệm thu đưa vào khai thác từ ngày 01 tháng 01 năm 2025 bắt buộc phải áp dụng 100% hệ thống báo hiệu theo QCVN 41:2024/BGTVT.</p>
    </div>

    <div class="technical-unit" id="qcvn41_sec_21">
        <p><b>Mục 21. Trách nhiệm rà soát và cắm biển báo hiệu đường bộ</b></p>
        <p>1. Cục Đường bộ Việt Nam, Sở Giao thông vận tải các tỉnh có trách nhiệm định kỳ hàng quý rà soát, dỡ bỏ ngay các biển báo bất hợp lý, biển báo bị che khuất hoặc mâu thuẫn giữa biển báo và vạch kẻ đường.</p>
        <p>2. Nghiêm cấm mọi tổ chức, cá nhân tự ý dựng, tháo dỡ, di dời, làm biến dạng hoặc vẽ bậy lên hệ thống biển báo hiệu đường bộ.</p>
    </div>
</div>
</body>
</html>
"""
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(html.strip())
    print(f"[+] Created {filepath.name} ({len(html)} chars, 2 Articles + QCVN 41 with 21 Technical Units)")

def main():
    gen_94_2026()
    gen_241_2026()
    gen_45_2026()
    gen_51_2024()
    print("[*] Corrected RAW documents generated successfully!")

if __name__ == "__main__":
    main()
