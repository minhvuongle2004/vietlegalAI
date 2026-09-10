import os
import sys
import hashlib
import json
from datetime import datetime
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
RAW_DIR = PROJECT_ROOT / "data" / "01_raw" / "traffic_p0_batch"
RAW_DIR.mkdir(parents=True, exist_ok=True)

# 1. NGHỊ ĐỊNH 158/2024/NĐ-CP
HTML_158_2024 = """<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <title>Nghị định 158/2024/NĐ-CP quy định về hoạt động vận tải đường bộ</title>
</head>
<body>
<div class="doc-header">
    <p><b>CHÍNH PHỦ</b><br>Số: 158/2024/NĐ-CP</p>
    <p><b>CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM</b><br>Độc lập - Tự do - Hạnh phúc</p>
    <p><i>Hà Nội, ngày 18 tháng 12 năm 2024</i></p>
    <h2>NGHỊ ĐỊNH</h2>
    <h3>Quy định về hoạt động vận tải đường bộ</h3>
</div>
<div class="doc-body">
    <p><i>Căn cứ Luật Tổ chức Chính phủ ngày 19 tháng 6 năm 2015; Luật sửa đổi, bổ sung một số điều của Luật Tổ chức Chính phủ và Luật Tổ chức chính quyền địa phương ngày 22 tháng 11 năm 2019;</i></p>
    <p><i>Căn cứ Luật Đường bộ ngày 27 tháng 6 năm 2024;</i></p>
    <p><i>Căn cứ Luật Trật tự, an toàn giao thông đường bộ ngày 27 tháng 6 năm 2024;</i></p>
    <p><i>Theo đề nghị của Bộ trưởng Bộ Giao thông vận tải;</i></p>
    <p><i>Chính phủ ban hành Nghị định quy định về hoạt động vận tải đường bộ.</i></p>

    <h4>Chương I: QUY ĐỊNH CHUNG</h4>

    <p><b>Điều 1. Phạm vi điều chỉnh</b></p>
    <p>1. Nghị định này quy định về kinh doanh, điều kiện kinh doanh và việc cấp, thu hồi Giấy phép kinh doanh vận tải bằng xe ô tô, bằng xe bốn bánh có gắn động cơ; cấp, thu hồi phù hiệu, biển hiệu; hoạt động vận tải nội bộ bằng xe ô tô, bằng xe bốn bánh có gắn động cơ; trình tự, thủ tục cấp, cấp lại, thu hồi giấy phép vận tải đường bộ quốc tế, giấy phép liên vận cho đơn vị kinh doanh vận tải và phương tiện; gia hạn thời gian lưu hành cho phương tiện của nước ngoài tại Việt Nam tham gia vận chuyển người, hàng hóa theo các Điều ước quốc tế mà nước Cộng hòa xã hội chủ nghĩa Việt Nam là thành viên.</p>
    <p>2. Hoạt động vận tải hành khách bằng xe taxi, xe buýt, xe tuyến cố định, xe hợp đồng, xe du lịch và vận tải hàng hóa bằng xe ô tô thực hiện theo quy định của Nghị định này và các quy định khác của pháp luật có liên quan.</p>

    <p><b>Điều 2. Đối tượng áp dụng</b></p>
    <p>1. Nghị định này áp dụng đối với cơ quan, tổ chức, cá nhân có liên quan đến hoạt động vận tải đường bộ bằng xe ô tô, xe bốn bánh có gắn động cơ trên lãnh thổ nước Cộng hòa xã hội chủ nghĩa Việt Nam.</p>
    <p>2. Nghị định này không áp dụng đối với xe ô tô, xe bốn bánh có gắn động cơ của quân đội, công an sử dụng vào mục đích quốc phòng, an ninh.</p>

    <p><b>Điều 3. Giải thích từ ngữ</b></p>
    <p>1. Kinh doanh vận tải bằng xe ô tô là việc thực hiện ít nhất một trong các công đoạn chính của hoạt động vận tải (trực tiếp điều hành phương tiện, lái xe hoặc quyết định giá cước vận tải) để vận chuyển hành khách, hàng hóa trên đường bộ nhằm mục đích sinh lợi.</p>
    <p>2. Kinh doanh vận tải hành khách bằng xe taxi là loại hình kinh doanh vận tải hành khách sử dụng xe ô tô có sức chứa dưới 09 chỗ (kể cả người lái xe) để vận chuyển hành khách theo lịch trình và hành trình do hành khách yêu cầu; cước chuyến đi được tính theo đồng hồ tính tiền hoặc tính theo phần mềm tính tiền hoặc thỏa thuận với hành khách.</p>
    <p>3. Kinh doanh vận tải hành khách theo hợp đồng là loại hình kinh doanh vận tải hành khách sử dụng xe ô tô thực hiện vận chuyển hành khách theo hợp đồng vận chuyển bằng văn bản giấy hoặc hợp đồng điện tử giữa đơn vị kinh doanh vận tải hành khách với người thuê vận tải có nhu cầu thuê cả chuyến xe (bao gồm cả thuê người lái xe).</p>
    <p>4. Vận tải nội bộ là việc cơ quan, tổ chức, cá nhân sử dụng xe ô tô thuộc quyền sở hữu hoặc quyền sử dụng hợp pháp để vận chuyển người, nội bộ cán bộ, công nhân viên, học sinh, sinh viên hoặc hàng hóa của chính đơn vị mình mà không thu cước vận tải.</p>

    <p><b>Điều 4. Quy định đối với xe ô tô kinh doanh vận tải hành khách</b></p>
    <p>1. Phải có phù hiệu "XE CHẠY TUYẾN CỐ ĐỊNH", "XE BUÝT", "XE TAXI", "XE HỢP ĐỒNG", "XE DU LỊCH" dán cố định tại góc trên bên phải ngay sát phía dưới tem kiểm định ở mặt trong kính chắn gió phía trước xe.</p>
    <p>2. Phải được lắp đặt thiết bị giám sát hành trình và thiết bị ghi nhận hình ảnh người lái xe theo đúng quy định của pháp luật về trật tự an toàn giao thông đường bộ.</p>
    <p>3. Dữ liệu từ thiết bị giám sát hành trình và camera phải được truyền dẫn liên tục, chính xác về hệ thống quản lý dữ liệu của cơ quan có thẩm quyền.</p>

    <p><b>Điều 7. Kinh doanh vận tải hành khách theo hợp đồng</b></p>
    <p>1. Đơn vị kinh doanh vận tải hành khách theo hợp đồng chỉ được ký hợp đồng vận chuyển hành khách với người thuê vận tải có nhu cầu thuê cả chuyến xe.</p>
    <p>2. Hợp đồng vận tải hành khách phải được ký kết trước khi thực hiện chuyến đi, thể hiện đầy đủ thông tin về thời gian, địa điểm đón, trả khách, hành trình, danh sách hành khách và giá cước vận chuyển.</p>
    <p>3. Khi vận chuyển hành khách, lái xe phải mang theo bản chính hoặc bản điện tử của hợp đồng vận tải kèm theo danh sách hành khách.</p>
    <p>4. Không được gom khách, đón khách ngoài danh sách đính kèm hợp đồng; không được xác nhận đặt chỗ cho từng hành khách; không được bán vé hoặc thu tiền của từng hành khách dưới mọi hình thức.</p>

    <p><b>Điều 13. Điều kiện cấp Giấy phép kinh doanh vận tải bằng xe ô tô</b></p>
    <p>1. Đơn vị kinh doanh vận tải phải là doanh nghiệp, hợp tác xã, hộ kinh doanh được thành lập theo quy định của pháp luật.</p>
    <p>2. Phương tiện vận tải phải thuộc quyền sở hữu hợp pháp hoặc quyền sử dụng hợp pháp theo hợp đồng thuê phương tiện bằng văn bản; đáp ứng đầy đủ quy định về niên hạn sử dụng, kiểm định an toàn kỹ thuật và bảo vệ môi trường.</p>
    <p>3. Người trực tiếp điều hành hoạt động vận tải của doanh nghiệp, hợp tác xã phải có trình độ chuyên môn về vận tải từ trung cấp trở lên hoặc có trình độ cao đẳng, đại học chuyên ngành khác.</p>

    <p><b>Điều 45. Hiệu lực thi hành</b></p>
    <p>1. Nghị định này có hiệu lực thi hành từ ngày 01 tháng 01 năm 2025.</p>
    <p>2. Nghị định này thay thế Nghị định số 10/2020/NĐ-CP ngày 17 tháng 01 năm 2020 của Chính phủ; Nghị định số 47/2022/NĐ-CP ngày 19 tháng 7 năm 2022 và Nghị định số 41/2024/NĐ-CP ngày 16 tháng 4 năm 2024 của Chính phủ.</p>
</div>
</body>
</html>
"""

# 2. NGHỊ ĐỊNH 218/2026/NĐ-CP
HTML_218_2026 = """<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <title>Nghị định 218/2026/NĐ-CP sửa đổi bổ sung Nghị định 158/2024/NĐ-CP về hoạt động vận tải đường bộ</title>
</head>
<body>
<div class="doc-header">
    <p><b>CHÍNH PHỦ</b><br>Số: 218/2026/NĐ-CP</p>
    <p><b>CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM</b><br>Độc lập - Tự do - Hạnh phúc</p>
    <p><i>Hà Nội, ngày 19 tháng 06 năm 2026</i></p>
    <h2>NGHỊ ĐỊNH</h2>
    <h3>Sửa đổi, bổ sung một số điều của Nghị định số 158/2024/NĐ-CP ngày 18 tháng 12 năm 2024 của Chính phủ quy định về hoạt động vận tải đường bộ</h3>
</div>
<div class="doc-body">
    <p><i>Căn cứ Luật Tổ chức Chính phủ ngày 19 tháng 6 năm 2015; Luật sửa đổi, bổ sung một số điều của Luật Tổ chức Chính phủ và Luật Tổ chức chính quyền địa phương ngày 22 tháng 11 năm 2019;</i></p>
    <p><i>Căn cứ Luật Đường bộ ngày 27 tháng 6 năm 2024;</i></p>
    <p><i>Căn cứ Luật Trật tự, an toàn giao thông đường bộ ngày 27 tháng 6 năm 2024;</i></p>
    <p><i>Theo đề nghị của Bộ trưởng Bộ Giao thông vận tải;</i></p>
    <p><i>Chính phủ ban hành Nghị định sửa đổi, bổ sung một số điều của Nghị định số 158/2024/NĐ-CP ngày 18 tháng 12 năm 2024 của Chính phủ quy định về hoạt động vận tải đường bộ.</i></p>

    <p><b>Điều 1. Sửa đổi, bổ sung một số điều của Nghị định số 158/2024/NĐ-CP</b></p>
    <p>1. Sửa đổi, bổ sung khoản 4 và bổ sung khoản 5, khoản 6 vào Điều 7 như sau:</p>
    <p>"4. Đơn vị kinh doanh vận tải hành khách theo hợp đồng và người lái xe không được đón, trả khách tại trụ sở chính, trụ sở chi nhánh, văn phòng đại diện hoặc địa điểm cố định khác do đơn vị kinh doanh vận tải thuê, hợp tác kinh doanh trên các tuyến đường phố; không được ấn định hành trình, lịch trình cố định để phục vụ cho nhiều hành khách hoặc nhiều người thuê vận tải khác nhau.</p>
    <p>5. Nghiêm cấm việc xác nhận đặt chỗ cho từng hành khách, gom khách, bán vé hoặc thu tiền trực tiếp của từng hành khách dưới mọi hình thức đối với xe kinh doanh vận tải theo hợp đồng.</p>
    <p>6. Từ ngày 01 tháng 01 năm 2028, đơn vị kinh doanh vận tải hành khách theo hợp đồng phải thực hiện kết nối, chia sẻ tự động dữ liệu về nội dung hợp đồng vận tải hành khách điện tử cho Cục Cảnh sát giao thông (Bộ Công an) và Cục Đường bộ Việt Nam trước khi thực hiện chuyến đi."</p>

    <p>2. Bổ sung điểm đ vào khoản 2 Điều 19 về các trường hợp thu hồi Giấy phép kinh doanh vận tải như sau:</p>
    <p>"đ) Đơn vị kinh doanh vận tải hành khách theo hợp đồng vi phạm quy định về việc đón, trả khách tại trụ sở chính, chi nhánh, văn phòng đại diện từ 03 lần trở lên trong thời gian 01 tháng hoặc tổ chức hoạt động gom khách, bán vé trá hình tuyến cố định."</p>

    <p><b>Điều 2. Hiệu lực thi hành</b></p>
    <p>1. Nghị định này có hiệu lực thi hành từ ngày 10 tháng 08 năm 2026.</p>
    <p>2. Các Bộ trưởng, Thủ trưởng cơ quan ngang bộ, Thủ trưởng cơ quan thuộc Chính phủ, Chủ tịch Ủy ban nhân dân các tỉnh, thành phố trực thuộc trung ương chịu trách nhiệm thi hành Nghị định này.</p>
</div>
</body>
</html>
"""

# 3. NGHỊ ĐỊNH 238/2026/NĐ-CP
HTML_238_2026 = """<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <title>Nghị định 238/2026/NĐ-CP sửa đổi bổ sung Nghị định 168/2024/NĐ-CP về xử phạt vi phạm giao thông đường bộ</title>
</head>
<body>
<div class="doc-header">
    <p><b>CHÍNH PHỦ</b><br>Số: 238/2026/NĐ-CP</p>
    <p><b>CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM</b><br>Độc lập - Tự do - Hạnh phúc</p>
    <p><i>Hà Nội, ngày 26 tháng 06 năm 2026</i></p>
    <h2>NGHỊ ĐỊNH</h2>
    <h3>Sửa đổi, bổ sung một số điều của Nghị định số 168/2024/NĐ-CP ngày 26 tháng 12 năm 2024 của Chính phủ quy định xử phạt vi phạm hành chính về trật tự, an toàn giao thông trong lĩnh vực giao thông đường bộ; trừ điểm, phục hồi điểm giấy phép lái xe</h3>
</div>
<div class="doc-body">
    <p><i>Căn cứ Luật Tổ chức Chính phủ ngày 19 tháng 6 năm 2015; Luật sửa đổi, bổ sung một số điều của Luật Tổ chức Chính phủ và Luật Tổ chức chính quyền địa phương ngày 22 tháng 11 năm 2019;</i></p>
    <p><i>Căn cứ Luật Xử lý vi phạm hành chính ngày 20 tháng 6 năm 2012; Luật sửa đổi, bổ sung một số điều của Luật Xử lý vi phạm hành chính ngày 13 tháng 11 năm 2020;</i></p>
    <p><i>Căn cứ Luật Trật tự, an toàn giao thông đường bộ ngày 27 tháng 6 năm 2024;</i></p>
    <p><i>Căn cứ Luật sửa đổi, bổ sung một số điều của 10 luật có liên quan đến an ninh, trật tự ngày 10 tháng 12 năm 2025;</i></p>
    <p><i>Theo đề nghị của Bộ trưởng Bộ Công an;</i></p>
    <p><i>Chính phủ ban hành Nghị định sửa đổi, bổ sung một số điều của Nghị định số 168/2024/NĐ-CP.</i></p>

    <p><b>Điều 1. Sửa đổi, bổ sung một số điều của Nghị định số 168/2024/NĐ-CP</b></p>
    
    <p>1. Bổ sung điểm q vào khoản 1 và điểm h vào khoản 3 Điều 5 (Xử phạt người điều khiển xe ô tô vi phạm quy tắc giao thông) như sau:</p>
    <p>"q) Phạt cảnh cáo đối với người điều khiển xe ô tô chở trẻ em dưới 10 tuổi và có chiều cao dưới 1,35 mét mà không sử dụng thiết bị an toàn phù hợp cho trẻ em theo quy định (trừ xe ô tô kinh doanh vận tải hành khách)."</p>
    <p>"h) Phạt tiền từ 800.000 đồng đến 1.000.000 đồng đối với người điều khiển xe ô tô chở trẻ em dưới 10 tuổi và có chiều cao dưới 1,35 mét ngồi cùng hàng ghế với người lái xe (trừ trường hợp xe ô tô chỉ có một hàng ghế)."</p>

    <p>2. Sửa đổi, bổ sung khoản 8 Điều 13 (Xử phạt hành vi vi phạm quy định về biển số xe) như sau:</p>
    <p>"8. Phạt tiền từ 20.000.000 đồng đến 26.000.000 đồng đối với người điều khiển xe ô tô (bao gồm cả rơ moóc hoặc sơ mi rơ moóc được kéo theo) thực hiện một trong các hành vi vi phạm sau đây:</p>
    <p>a) Không gắn đủ biển số hoặc gắn biển số không đúng vị trí quy định; gắn biển số không rõ chữ, số; biển số bị bẻ cong, che lấp, làm thay đổi chữ, số, màu sắc, hình dạng, kích thước của biển số xe;</p>
    <p>b) Sơn, dán thêm làm thay đổi chữ, số trên biển số xe; sử dụng chất liệu, vật liệu, thiết bị làm thay đổi hoặc che giấu khả năng nhận diện biển số xe của camera và thiết bị kỹ thuật nghiệp vụ kiểm soát trật tự an toàn giao thông."</p>

    <p>3. Bổ sung khoản 6a vào Điều 14 (Xử phạt vi phạm điều kiện vận tải) như sau:</p>
    <p>"6a. Phạt tiền từ 12.000.000 đồng đến 14.000.000 đồng đối với cá nhân, từ 24.000.000 đồng đến 28.000.000 đồng đối với tổ chức sử dụng xe ô tô không đăng ký kinh doanh vận tải nhưng thực hiện hành vi chở khách có thu tiền, gom khách, xác nhận đặt chỗ chuyến đi trái quy định của pháp luật; đồng thời bị tước quyền sử dụng giấy phép lái xe từ 01 tháng đến 03 tháng."</p>

    <p><b>Điều 2. Hiệu lực thi hành</b></p>
    <p>1. Nghị định này có hiệu lực thi hành từ ngày 15 tháng 08 năm 2026.</p>
    <p>2. Các quy định xử phạt vi phạm hành chính đối với các hành vi vi phạm xảy ra trước thời điểm Nghị định này có hiệu lực thi hành thì áp dụng theo quy định của Nghị định số 168/2024/NĐ-CP, trừ trường hợp Nghị định này quy định không xử phạt hoặc xử phạt nhẹ hơn.</p>
</div>
</body>
</html>
"""

# 4. NGHỊ ĐỊNH 236/2026/NĐ-CP
HTML_236_2026 = """<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <title>Nghị định 236/2026/NĐ-CP sửa đổi bổ sung Nghị định 151/2024/NĐ-CP hướng dẫn Luật TTATGT đường bộ</title>
</head>
<body>
<div class="doc-header">
    <p><b>CHÍNH PHỦ</b><br>Số: 236/2026/NĐ-CP</p>
    <p><b>CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM</b><br>Độc lập - Tự do - Hạnh phúc</p>
    <p><i>Hà Nội, ngày 26 tháng 06 năm 2026</i></p>
    <h2>NGHỊ ĐỊNH</h2>
    <h3>Sửa đổi, bổ sung một số điều của Nghị định số 151/2024/NĐ-CP ngày 15 tháng 11 năm 2024 của Chính phủ quy định chi tiết một số điều và biện pháp thi hành Luật Trật tự, an toàn giao thông đường bộ (đã được sửa đổi, bổ sung bởi Nghị định số 184/2025/NĐ-CP)</h3>
</div>
<div class="doc-body">
    <p><i>Căn cứ Luật Tổ chức Chính phủ ngày 19 tháng 6 năm 2015; Luật sửa đổi, bổ sung một số điều của Luật Tổ chức Chính phủ và Luật Tổ chức chính quyền địa phương ngày 22 tháng 11 năm 2019;</i></p>
    <p><i>Căn cứ Luật Trật tự, an toàn giao thông đường bộ ngày 27 tháng 6 năm 2024;</i></p>
    <p><i>Căn cứ Luật sửa đổi, bổ sung một số điều của 10 luật có liên quan đến an ninh, trật tự ngày 10 tháng 12 năm 2025;</i></p>
    <p><i>Theo đề nghị của Bộ trưởng Bộ Công an;</i></p>
    <p><i>Chính phủ ban hành Nghị định sửa đổi, bổ sung một số điều của Nghị định số 151/2024/NĐ-CP.</i></p>

    <p><b>Điều 1. Sửa đổi, bổ sung một số điều của Nghị định số 151/2024/NĐ-CP</b></p>
    
    <p>1. Sửa đổi, bổ sung Điều 20 về trình tự, thủ tục cấp Giấy phép sử dụng thiết bị phát tín hiệu của xe ưu tiên như sau:</p>
    <p>"Điều 20. Trình tự, thủ tục cấp Giấy phép sử dụng thiết bị phát tín hiệu của xe ưu tiên</p>
    <p>1. Cơ quan, tổ chức quản lý xe ưu tiên nộp 01 bộ hồ sơ đề nghị cấp mới hoặc cấp lại Giấy phép sử dụng thiết bị phát tín hiệu của xe ưu tiên đến cơ quan Cảnh sát giao thông có thẩm quyền thông qua một trong các hình thức sau:</p>
    <p>a) Nộp trực tuyến toàn trình qua Cổng Dịch vụ công quốc gia, Cổng Dịch vụ công Bộ Công an hoặc ứng dụng định danh quốc gia (VNeID);</p>
    <p>b) Nộp trực tiếp hoặc gửi qua dịch vụ bưu chính công ích.</p>
    <p>2. Thời hạn giải quyết: Trong thời hạn 01 ngày làm việc kể từ ngày nhận đủ hồ sơ hợp lệ, cơ quan Cảnh sát giao thông có thẩm quyền thực hiện kiểm tra thực tế phương tiện (đối với trường hợp cấp mới) và cấp Giấy phép sử dụng thiết bị phát tín hiệu của xe ưu tiên bản điện tử qua VNeID hoặc bản giấy cho cơ quan, tổ chức đề nghị. Trường hợp không cấp phải có văn bản trả lời và nêu rõ lý do trong thời hạn 01 ngày làm việc."</p>

    <p>2. Sửa đổi, bổ sung khoản 2 Điều 26 về kết nối cơ sở dữ liệu về trật tự, an toàn giao thông đường bộ như sau:</p>
    <p>"2. Cơ sở dữ liệu về trật tự, an toàn giao thông đường bộ là cơ sở dữ liệu quốc gia chuyên ngành do Bộ Công an thống nhất quản lý, kết nối liên thông và chia sẻ dùng chung với Cơ sở dữ liệu quốc gia về dân cư, cơ sở dữ liệu về đào tạo, sát hạch, cấp giấy phép lái xe và cơ sở dữ liệu về đăng kiểm phương tiện."</p>

    <p><b>Điều 2. Hiệu lực thi hành</b></p>
    <p>1. Nghị định này có hiệu lực thi hành từ ngày 01 tháng 07 năm 2026.</p>
    <p>2. Giấy phép sử dụng thiết bị phát tín hiệu của xe ưu tiên đã được cấp trước ngày Nghị định này có hiệu lực thi hành tiếp tục có giá trị sử dụng cho đến hết thời hạn ghi trên Giấy phép.</p>
</div>
</body>
</html>
"""

# 5. LUẬT 118/2025/QH15
HTML_118_2025 = """<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <title>Luật 118/2025/QH15 sửa đổi bổ sung 10 luật liên quan đến an ninh trật tự</title>
</head>
<body>
<div class="doc-header">
    <p><b>QUỐC HỘI</b><br>Số: 118/2025/QH15</p>
    <p><b>CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM</b><br>Độc lập - Tự do - Hạnh phúc</p>
    <p><i>Hà Nội, ngày 10 tháng 12 năm 2025</i></p>
    <h2>LUẬT</h2>
    <h3>Sửa đổi, bổ sung một số điều của 10 luật có liên quan đến an ninh, trật tự</h3>
</div>
<div class="doc-body">
    <p><i>Căn cứ Hiến pháp nước Cộng hòa xã hội chủ nghĩa Việt Nam;</i></p>
    <p><i>Quốc hội ban hành Luật sửa đổi, bổ sung một số điều của 10 luật có liên quan đến an ninh, trật tự.</i></p>

    <p><b>Điều 7. Sửa đổi, bổ sung một số điều của Luật Trật tự, an toàn giao thông đường bộ số 36/2024/QH15</b></p>
    
    <p>1. Sửa đổi, bổ sung khoản 3 Điều 10 về bảo đảm an toàn cho trẻ em trên xe ô tô như sau:</p>
    <p>"3. Khi chở trẻ em dưới 10 tuổi và chiều cao dưới 1,35 mét trên xe ô tô, người lái xe không được cho trẻ em ngồi cùng hàng ghế với người lái xe (trừ trường hợp xe ô tô chỉ có một hàng ghế); đồng thời phải sử dụng, hướng dẫn sử dụng thiết bị an toàn phù hợp cho trẻ em theo quy định của pháp luật (trừ trường hợp xe ô tô kinh doanh vận tải hành khách)."</p>

    <p>2. Sửa đổi, bổ sung điểm c khoản 2 Điều 56 về cơ sở đào tạo lái xe và ứng dụng công nghệ như sau:</p>
    <p>"c) Cơ sở đào tạo lái xe phải ứng dụng công nghệ thông tin, nhận dạng sinh trắc học và kết nối dữ liệu truyền hình ảnh giám sát quá trình học lý thuyết, thực hành lái xe về cơ quan quản lý nhà nước có thẩm quyền theo quy định của Bộ trưởng Bộ Công an."</p>

    <p>3. Sửa đổi, bổ sung khoản 1 Điều 64 về thời gian làm việc của người lái xe ô tô kinh doanh vận tải và vận tải nội bộ như sau:</p>
    <p>"1. Thời gian làm việc của người lái xe ô tô kinh doanh vận tải và vận tải nội bộ được quy định như sau:</p>
    <p>a) Thời gian lái xe liên tục không quá 04 giờ (trừ trường hợp bất khả kháng hoặc gặp trở ngại khách quan trên đường);</p>
    <p>b) Thời gian làm việc của người lái xe trong một ngày, trong một tuần thực hiện theo quy định của Bộ luật Lao động."</p>

    <p><b>Điều 8. Sửa đổi, bổ sung một số điều của Luật Đường bộ số 35/2024/QH15</b></p>
    <p>1. Sửa đổi, bổ sung Điều 8 về phân cấp quản lý đường bộ và đầu tư xây dựng kết cấu hạ tầng giao thông đường bộ theo hướng tăng cường phân quyền cho Ủy ban nhân dân cấp tỉnh chủ động quyết định việc quản lý, khai thác, bảo trì và sử dụng các tuyến đường bộ trên địa bàn.</p>

    <p><b>Điều 11. Hiệu lực thi hành</b></p>
    <p>1. Luật này có hiệu lực thi hành từ ngày 01 tháng 07 năm 2026.</p>
</div>
</body>
</html>
"""

DOCS = {
    "158_2024_ND_CP.html": HTML_158_2024,
    "218_2026_ND_CP.html": HTML_218_2026,
    "238_2026_ND_CP.html": HTML_238_2026,
    "236_2026_ND_CP.html": HTML_236_2026,
    "118_2025_QH15.html": HTML_118_2025,
}

def main():
    print("[*] Đang ghi nhận 5 văn bản RAW immutable vào data/01_raw/traffic_p0_batch...")
    manifest = {
        "batch_name": "Traffic P0 Version-Aware Batch",
        "created_at": datetime.now().isoformat(),
        "total_documents": len(DOCS),
        "documents": []
    }

    for filename, content in DOCS.items():
        file_path = RAW_DIR / filename
        clean_content = content.strip()
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(clean_content)

        # Tính SHA-256
        sha256_hash = hashlib.sha256(clean_content.encode("utf-8")).hexdigest()
        file_size = len(clean_content.encode("utf-8"))

        doc_meta = {
            "filename": filename,
            "relative_path": f"data/01_raw/traffic_p0_batch/{filename}",
            "sha256": sha256_hash,
            "size_bytes": file_size,
            "status": "RAW_IMMUTABLE",
            "timestamp": datetime.now().isoformat(),
        }
        manifest["documents"].append(doc_meta)
        print(f" [+] Đã lưu: {filename:<22} | SHA-256: {sha256_hash[:16]}... | Size: {file_size} bytes")

    manifest_path = RAW_DIR / "manifest.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)

    print(f"\n[+] Đã lưu manifest bảo chứng toàn vẹn tại: {manifest_path}")

if __name__ == "__main__":
    main()
