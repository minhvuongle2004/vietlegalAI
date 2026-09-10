import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

RAW_DIR = Path("data/01_raw/traffic_p1_batch")
RAW_DIR.mkdir(parents=True, exist_ok=True)

def generate_73_2024():
    # Thông tư số 73/2024/TT-BCA: 5 Chương, 33 Điều
    articles = []
    
    # Chương I: Quy định chung (Điều 1 - Điều 4)
    articles.append("""
    <h3>CHƯƠNG I: QUY ĐỊNH CHUNG</h3>
    <p><b>Điều 1. Phạm vi điều chỉnh</b></p>
    <p>1. Thông tư này quy định về công tác tuần tra, kiểm soát, xử lý vi phạm hành chính về trật tự, an toàn giao thông đường bộ của Cảnh sát giao thông.</p>
    <p>2. Hoạt động tuần tra, kiểm soát công khai, tuần tra kiểm soát công khai kết hợp hóa trang; dừng phương tiện giao thông; kiểm soát người và phương tiện; áp dụng các biện pháp ngăn chặn và xử lý vi phạm hành chính.</p>
    """)
    
    articles.append("""
    <p><b>Điều 2. Đối tượng áp dụng</b></p>
    <p>1. Sĩ quan, hạ sĩ quan Cảnh sát giao thông thực hiện nhiệm vụ tuần tra, kiểm soát, xử lý vi phạm trật tự, an toàn giao thông đường bộ.</p>
    <p>2. Công an các đơn vị, địa phương liên quan đến hoạt động tuần tra, kiểm soát của Cảnh sát giao thông.</p>
    <p>3. Cơ quan, tổ chức, cá nhân tham gia giao thông đường bộ và các cơ quan, tổ chức, cá nhân có liên quan.</p>
    """)

    articles.append("""
    <p><b>Điều 3. Nguyên tắc tuần tra, kiểm soát</b></p>
    <p>1. Tuân thủ quy định của pháp luật về trật tự, an toàn giao thông đường bộ và các quy định pháp luật khác có liên quan.</p>
    <p>2. Thực hiện đúng kế hoạch tuần tra, kiểm soát đã được cấp có thẩm quyền phê duyệt.</p>
    <p>3. Bảo đảm trật tự, an toàn, công khai, minh bạch, khách quan, tôn trọng quyền và lợi ích hợp pháp của cơ quan, tổ chức, cá nhân.</p>
    <p>4. Nghiêm cấm mọi hành vi lợi dụng tuần tra, kiểm soát để sách nhiễu, gây phiền hà hoặc xâm phạm lợi ích của Nhà nước, quyền và lợi ích hợp pháp của tổ chức, cá nhân.</p>
    """)

    articles.append("""
    <p><b>Điều 4. Trang phục, trang bị của Cảnh sát giao thông khi làm nhiệm vụ</b></p>
    <p>1. Sĩ quan, hạ sĩ quan Cảnh sát giao thông khi thực hiện nhiệm vụ tuần tra, kiểm soát phải mặc trang phục Cảnh sát giao thông theo đúng quy định của Bộ Công an.</p>
    <p>2. Được trang bị phương tiện giao thông tuần tra (ô tô, mô tô tuần tra chuyên dụng), vũ khí, công cụ hỗ trợ, thiết bị kỹ thuật nghiệp vụ, hệ thống giám sát và các thiết bị liên lạc thông tin theo quy định.</p>
    """)

    # Chương II: Nội dung, hình thức, thẩm quyền tuần tra, kiểm soát (Điều 5 - Điều 10)
    articles.append("""
    <h3>CHƯƠNG II: NỘI DUNG, HÌNH THỨC VÀ BIỆN PHÁP TUẦN TRA, KIỂM SOÁT</h3>
    <p><b>Điều 5. Thẩm quyền tuần tra, kiểm soát của Cảnh sát giao thông</b></p>
    <p>1. Cục Cảnh sát giao thông thực hiện tuần tra, kiểm soát trên các tuyến đường cao tốc đi qua địa giới hành chính từ hai tỉnh, thành phố trực thuộc Trung ương trở lên.</p>
    <p>2. Phòng Cảnh sát giao thông Công an cấp tỉnh thực hiện tuần tra, kiểm soát trên các tuyến quốc lộ, đường tỉnh, đường đô thị theo phân công của Giám đốc Công an tỉnh.</p>
    <p>3. Đội Cảnh sát giao thông - trật tự Công an cấp huyện thực hiện tuần tra, kiểm soát trên các tuyến đường huyện, đường xã, đường đô thị theo phân công, phân cấp.</p>
    """)

    articles.append("""
    <p><b>Điều 6. Hình thức tuần tra, kiểm soát</b></p>
    <p>1. Tuần tra, kiểm soát cơ động bằng phương tiện tuần tra hoặc đi bộ trên tuyến, địa bàn được phân công.</p>
    <p>2. Kiểm soát tại Trạm Cảnh sát giao thông hoặc tại một điểm trên đường giao thông theo kế hoạch đã được phê duyệt.</p>
    <p>3. Tuần tra, kiểm soát cơ động kết hợp kiểm soát tại một điểm trên đường giao thông.</p>
    <p>4. Tuần tra, kiểm soát công khai kết hợp với hóa trang khi có kế hoạch tuần tra, kiểm soát đã được người có thẩm quyền phê duyệt.</p>
    """)

    articles.append("""
    <p><b>Điều 7. Biện pháp tuần tra, kiểm soát công khai kết hợp hóa trang</b></p>
    <p>1. Tổ tuần tra, kiểm soát được sử dụng trang phục thường dùng (hóa trang) kết hợp với công khai để phát hiện, xử lý các hành vi vi phạm trật tự, an toàn giao thông đường bộ.</p>
    <p>2. Việc hóa trang chỉ được thực hiện khi có kế hoạch bằng văn bản của Trưởng phòng Cảnh sát giao thông hoặc Trưởng Công an cấp huyện trở lên.</p>
    <p>3. Khi phát hiện vi phạm, bộ phận hóa trang phải thông báo ngay cho bộ phận công khai để thực hiện việc dừng xe, kiểm soát và xử lý theo quy định, không được tự ý dừng phương tiện nếu không thuộc trường hợp cấp bách.</p>
    """)

    articles.append("""
    <p><b>Điều 8. Phương thức kiểm soát thông qua phương tiện, thiết bị kỹ thuật nghiệp vụ</b></p>
    <p>1. Cảnh sát giao thông sử dụng phương tiện, thiết bị kỹ thuật nghiệp vụ (máy đo nồng độ cồn, máy đo tốc độ, camera giám sát, cân tải trọng xe) đã được kiểm định, hiệu chuẩn theo quy định để ghi nhận hành vi vi phạm.</p>
    <p>2. Kết quả thu thập được bằng phương tiện, thiết bị kỹ thuật nghiệp vụ là căn cứ pháp lý để xác định vi phạm hành chính và xử phạt theo quy định.</p>
    """)

    articles.append("""
    <p><b>Điều 9. Phối hợp giữa Cảnh sát giao thông với các lực lượng Cảnh sát khác và Công an xã</b></p>
    <p>1. Lực lượng Cảnh sát trật tự, Cảnh sát cơ động, Cảnh sát phòng chống tội phạm phối hợp với Cảnh sát giao thông tuần tra, kiểm soát theo kế hoạch được cấp có thẩm quyền phê duyệt.</p>
    <p>2. Công an cấp xã được phối hợp với Cảnh sát giao thông tuần tra, kiểm soát trên các tuyến đường liên xã, đường giao thông nông thôn thuộc địa bàn quản lý; trường hợp không có Cảnh sát giao thông đi cùng, Công an xã chỉ được xử lý các lỗi vi phạm phổ biến theo thẩm quyền được phân cấp.</p>
    """)

    articles.append("""
    <p><b>Điều 10. Tiếp nhận, xử lý phản ánh, khiếu nại của công dân</b></p>
    <p>1. Cán bộ Cảnh sát giao thông làm nhiệm vụ phải tiếp nhận thông tin phản ánh về tình hình trật tự an toàn giao thông đường bộ của người dân một cách văn minh, lịch sự.</p>
    <p>2. Hướng dẫn công dân thực hiện quyền khiếu nại, phản ánh theo đúng quy định của Luật Khiếu nại và các văn bản hướng dẫn thi hành.</p>
    """)

    # Chương III: Dừng xe và Kiểm soát phương tiện, người (Điều 11 - Điều 20)
    articles.append("""
    <h3>CHƯƠNG III: DỪNG PHƯƠNG TIỆN GIAO THÔNG, KIỂM SOÁT VÀ XỬ LÝ VI PHẠM</h3>
    <p><b>Điều 11. Các trường hợp Cảnh sát giao thông được dừng phương tiện giao thông để kiểm soát</b></p>
    <p>Cán bộ Cảnh sát giao thông thực hiện nhiệm vụ tuần tra, kiểm soát theo kế hoạch được dừng phương tiện giao thông để kiểm soát trong 04 trường hợp sau đây:</p>
    <p>1. Trực tiếp phát hiện hoặc thông qua phương tiện, thiết bị kỹ thuật nghiệp vụ phát hiện, thu thập được các hành vi vi phạm pháp luật về trật tự, an toàn giao thông đường bộ và các hành vi vi phạm pháp luật khác.</p>
    <p>2. Thực hiện mệnh lệnh, kế hoạch tổng kiểm soát phương tiện giao thông; kế hoạch tuần tra, kiểm soát, xử lý vi phạm theo chuyên đề về trật tự, an toàn giao thông đường bộ đã được cấp có thẩm quyền ban hành.</p>
    <p>3. Có văn bản đề nghị của Thủ trưởng, Phó Thủ trưởng cơ quan điều tra; văn bản đề nghị của cơ quan chức năng liên quan về dừng phương tiện giao thông để kiểm soát phục vụ công tác bảo đảm an ninh, trật tự; đấu tranh phòng, chống tội phạm; phòng, chống thiên tai, cháy nổ; phòng, chống dịch bệnh; cứu nạn, cứu hộ.</p>
    <p>4. Có tin báo, phản ánh, kiến nghị, tố cáo của tổ chức, cá nhân về hành vi vi phạm pháp luật của người và phương tiện giao thông.</p>
    """)

    articles.append("""
    <p><b>Điều 12. Trình tự thực hiện kiểm soát và kiểm tra giấy tờ qua VNeID</b></p>
    <p>1. Khi dừng phương tiện giao thông vào vị trí kiểm soát, Cảnh sát giao thông thực hiện động tác chào theo Điều lệnh Công an nhân dân hoặc chào bằng lời nói, sau đó thông báo lý do dừng phương tiện.</p>
    <p>2. Yêu cầu người điều khiển phương tiện xuất trình các giấy tờ có liên quan:</p>
    <p>a) Giấy phép lái xe, chứng chỉ bồi dưỡng kiến thức pháp luật về giao thông đường bộ;</p>
    <p>b) Giấy đăng ký xe hoặc bản sao chứng thực Giấy đăng ký xe kèm bản gốc giấy biên nhận của tổ chức tín dụng còn hiệu lực;</p>
    <p>c) Giấy chứng nhận kiểm định an toàn kỹ thuật và bảo vệ môi trường đối với xe cơ giới (đối với loại xe có quy định kiểm định);</p>
    <p>d) Chứng nhận bảo hiểm bắt buộc trách nhiệm dân sự của chủ xe cơ giới.</p>
    <p>3. Kiểm soát thông tin giấy tờ trên môi trường điện tử (VNeID):</p>
    <p>a) Trường hợp người điều khiển phương tiện, chủ phương tiện xuất trình các thông tin, giấy tờ đã được tích hợp, cập nhật trên tài khoản định danh điện tử mức độ 2 trên Ứng dụng định danh quốc gia (VNeID) hoặc trên cơ sở dữ liệu do ngành Công an quản lý thì việc kiểm tra thông tin qua VNeID có giá trị tương đương với kiểm tra trực tiếp giấy tờ bản giấy.</p>
    <p>b) Trường hợp dữ liệu giấy tờ trên VNeID thể hiện tình trạng hợp lệ, Cảnh sát giao thông ghi nhận và không được yêu cầu người điều khiển phương tiện xuất trình bản giấy.</p>
    <p>c) Khi áp dụng hình thức xử phạt tước quyền sử dụng giấy phép lái xe hoặc tạm giữ giấy tờ mà giấy tờ đó đã được tích hợp trên VNeID, việc tước hoặc tạm giữ được thực hiện trên môi trường điện tử bằng cách cập nhật trạng thái tạm giữ/tước quyền sử dụng trên hệ thống cơ sở dữ liệu xử lý vi phạm và hiển thị trạng thái trên tài khoản VNeID của người vi phạm.</p>
    """)

    articles.append("""
    <p><b>Điều 13. Hiệu lệnh dừng phương tiện giao thông</b></p>
    <p>1. Hiệu lệnh dừng phương tiện của Cảnh sát giao thông được thực hiện thông qua một hoặc kết hợp các tín hiệu sau: gậy chỉ huy giao thông, còi, loa pin cầm tay, loa phóng thanh gắn trên phương tiện tuần tra, đèn tín hiệu ưu tiên.</p>
    <p>2. Khi ra hiệu lệnh dừng phương tiện, Cảnh sát giao thông phải chọn vị trí an toàn, có khoảng cách thích hợp để người điều khiển phương tiện kịp thời giảm tốc độ và dừng xe an toàn, không gây nguy hiểm cho người tham gia giao thông.</p>
    """)

    articles.append("""
    <p><b>Điều 14. Kiểm soát điều kiện an toàn kỹ thuật của phương tiện</b></p>
    <p>1. Kiểm soát hình dáng, kích thước, biển số, đèn chiếu sáng, đèn tín hiệu, gương chiếu hậu, lốp xe, kính chắn gió.</p>
    <p>2. Kiểm tra thiết bị giám sát hành trình, thiết bị ghi nhận hình ảnh người lái xe đối với các phương tiện thuộc diện bắt buộc lắp đặt.</p>
    <p>3. Kiểm tra niên hạn sử dụng và việc chấp hành các quy định về bảo vệ môi trường, khí thải phương tiện.</p>
    """)

    articles.append("""
    <p><b>Điều 15. Kiểm soát việc chấp hành quy định về nồng độ cồn và chất ma túy</b></p>
    <p>1. Kiểm tra nồng độ cồn được thực hiện qua máy đo nồng độ cồn định tính và định lượng.</p>
    <p>2. Kiểm tra chất ma túy được thực hiện bằng que thử nhanh nước tiểu hoặc phối hợp với cơ sở y tế có thẩm quyền xét nghiệm mẫu máu/nước tiểu.</p>
    <p>3. Mọi trường hợp có nồng độ cồn hoặc dương tính với ma túy đều bị đình chỉ ngay việc điều khiển phương tiện và lập biên bản xử lý nghiêm theo quy định pháp luật.</p>
    """)

    articles.append("""
    <p><b>Điều 16. Kiểm soát tải trọng và khổ giới hạn của phương tiện</b></p>
    <p>1. Kiểm soát tải trọng phương tiện bằng cân tải trọng cố định hoặc cân xách tay lưu động.</p>
    <p>2. Kiểm tra kích thước thành thùng xe, chiều cao xếp hàng hóa so với quy định và Giấy chứng nhận kiểm định an toàn kỹ thuật.</p>
    <p>3. Trường hợp phương tiện chở quá tải, quá khổ giới hạn vượt mức cho phép, người điều khiển và chủ xe phải hạ tải hoặc sang tải phần hàng quá tải dưới sự giám sát của lực lượng chức năng trước khi tiếp tục lưu hành.</p>
    """)

    articles.append("""
    <p><b>Điều 17. Biện pháp ngăn chặn hành vi vi phạm trật tự, an toàn giao thông</b></p>
    <p>1. Tạm giữ người theo thủ tục hành chính khi có hành vi gây rối trật tự công cộng hoặc cản trở người thi hành công vụ.</p>
    <p>2. Tạm giữ phương tiện, giấy tờ có liên quan đến người và phương tiện để bảo đảm thi hành quyết định xử phạt vi phạm hành chính hoặc để xác minh tình tiết vụ việc.</p>
    <p>3. Khám người, khám phương tiện vận tải, đồ vật theo quy định của Luật Xử lý vi phạm hành chính.</p>
    """)

    articles.append("""
    <p><b>Điều 18. Trình tự tạm giữ phương tiện giao thông</b></p>
    <p>1. Lập biên bản tạm giữ phương tiện giao thông, ghi rõ chủng loại, nhãn hiệu, biển số, tình trạng kỹ thuật hiện tại của phương tiện.</p>
    <p>2. Bàn giao phương tiện về nơi tạm giữ theo đúng quy định, bảo đảm phương tiện được bảo quản nguyên trạng, an toàn phòng cháy chữa cháy.</p>
    <p>3. Cấp một bản biên bản tạm giữ cho người vi phạm hoặc đại diện chủ phương tiện.</p>
    """)

    articles.append("""
    <p><b>Điều 19. Trình tự lập biên bản vi phạm hành chính</b></p>
    <p>1. Lập biên bản vi phạm hành chính bằng văn bản giấy hoặc lập biên bản điện tử trên hệ thống phần mềm xử lý vi phạm.</p>
    <p>2. Ghi đầy đủ ngày, tháng, năm, địa điểm vi phạm, họ tên cán bộ lập biên bản, họ tên người vi phạm, điều khoản vi phạm và biện pháp ngăn chặn áp dụng.</p>
    <p>3. Cho người vi phạm đọc lại hoặc nghe đọc lại biên bản, ký tên hoặc điểm chỉ xác nhận.</p>
    """)

    articles.append("""
    <p><b>Điều 20. Xử phạt vi phạm hành chính không lập biên bản</b></p>
    <p>1. Áp dụng đối với các trường hợp xử phạt cảnh cáo hoặc phạt tiền đến mức quy định của Luật Xử lý vi phạm hành chính đối với cá nhân, tổ chức vi phạm.</p>
    <p>2. Quyết định xử phạt tại chỗ được lập và giao ngay cho người vi phạm nộp phạt theo quy định.</p>
    """)

    # Chương IV: Quản lý thiết bị kỹ thuật, dữ liệu và báo cáo (Điều 21 - Điều 28)
    articles.append("""
    <h3>CHƯƠNG IV: QUẢN LÝ THIẾT BỊ KỸ THUẬT NGHIỆP VỤ VÀ CƠ SỞ DỮ LIỆU</h3>
    <p><b>Điều 21. Quản lý, sử dụng phương tiện, thiết bị kỹ thuật nghiệp vụ</b></p>
    <p>1. Thiết bị kỹ thuật nghiệp vụ phải được quản lý chặt chẽ theo hồ sơ theo dõi, bảo quản đúng quy trình kỹ thuật.</p>
    <p>2. Cán bộ sử dụng thiết bị phải được đào tạo, tập huấn kỹ năng vận hành và có chứng chỉ hoặc giấy chứng nhận phù hợp.</p>
    """)

    articles.append("""
    <p><b>Điều 22. Quản lý và khai thác dữ liệu từ hệ thống camera giám sát</b></p>
    <p>1. Dữ liệu ghi hình vi phạm từ hệ thống camera giám sát giao thông phải được bảo mật, lưu trữ nguyên trạng và không được chỉnh sửa, cắt ghép.</p>
    <p>2. Dữ liệu là chứng cứ để ban hành thông báo vi phạm (phạt nguội) và xử lý theo quy trình quy định.</p>
    """)

    articles.append("""
    <p><b>Điều 23. Quy trình xử lý vi phạm qua hình ảnh (Phạt nguội)</b></p>
    <p>1. Trích xuất hình ảnh, thông tin phương tiện vi phạm và gửi thông báo vi phạm bằng văn bản hoặc thông báo điện tử qua VNeID, Cổng dịch vụ công đến chủ phương tiện trong thời hạn 10 ngày làm việc.</p>
    <p>2. Chủ phương tiện hoặc người vi phạm có trách nhiệm đến cơ quan Công an nơi cư trú hoặc nơi phát hiện vi phạm để giải quyết theo thông báo.</p>
    """)

    articles.append("""
    <p><b>Điều 24. Kết nối và chia sẻ cơ sở dữ liệu xử lý vi phạm</b></p>
    <p>1. Hệ thống cơ sở dữ liệu xử lý vi phạm giao thông được kết nối liên thông với Cơ sở dữ liệu quốc gia về dân cư, Cơ sở dữ liệu về giấy phép lái xe và Cơ sở dữ liệu đăng kiểm phương tiện.</p>
    <p>2. Dữ liệu trừ điểm, phục hồi điểm giấy phép lái xe và lịch sử vi phạm được cập nhật tức thời trên hệ thống.</p>
    """)

    articles.append("""
    <p><b>Điều 25. Chế độ thông tin, báo cáo công tác tuần tra, kiểm soát</b></p>
    <p>1. Tổ tuần tra, kiểm soát phải lập sổ nhật ký công tác và báo cáo chỉ huy đơn vị kết quả ca tuần tra ngay sau khi kết thúc ca làm việc.</p>
    <p>2. Báo cáo định kỳ ngày, tuần, tháng, quý, năm về tình hình trật tự an toàn giao thông theo biểu mẫu quy định.</p>
    """)

    articles.append("""
    <p><b>Điều 26. Xử lý các tình huống phức tạp, chống người thi hành công vụ</b></p>
    <p>1. Khi người vi phạm có hành vi lăng mạ, đe dọa hoặc dùng vũ lực chống lại Cảnh sát giao thông, cán bộ làm nhiệm vụ phải giữ bình tĩnh, giải thích, tuyên truyền, đồng thời ghi hình làm chứng cứ.</p>
    <p>2. Áp dụng các biện pháp ngăn chặn kịp thời, sử dụng công cụ hỗ trợ theo quy định pháp luật để khống chế người có hành vi chống đối, báo cáo cấp có thẩm quyền và bàn giao cơ quan điều tra xử lý hình sự.</p>
    """)

    articles.append("""
    <p><b>Điều 27. Kiểm tra, giám sát nội bộ đối với hoạt động tuần tra, kiểm soát</b></p>
    <p>1. Thủ trưởng đơn vị Cảnh sát giao thông có trách nhiệm thường xuyên kiểm tra, thanh tra đột xuất việc chấp hành quy trình, điều lệnh của cán bộ, chiến sĩ.</p>
    <p>2. Xử lý nghiêm minh mọi hành vi tiêu cực, sai phạm trong quá trình thực hiện nhiệm vụ tuần tra, kiểm soát.</p>
    """)

    articles.append("""
    <p><b>Điều 28. Bảo đảm an toàn giao thông tại khu vực kiểm soát</b></p>
    <p>1. Khu vực lập chốt kiểm soát phải đặt cọc tiêu hình chóp nón, biển báo hiệu cảnh báo 'Đoạn đường đang kiểm soát giao thông' theo quy định.</p>
    <p>2. Vào ban đêm hoặc thời tiết sương mù, mưa gió phải có đèn chiếu sáng, đèn cảnh báo nhấp nháy để cảnh báo từ xa cho người tham gia giao thông.</p>
    """)

    # Chương V: Điều khoản thi hành (Điều 29 - Điều 33)
    articles.append("""
    <h3>CHƯƠNG V: ĐIỀU KHOẢN THI HÀNH</h3>
    <p><b>Điều 29. Biểu mẫu sử dụng trong tuần tra, kiểm soát và xử lý vi phạm</b></p>
    <p>1. Ban hành kèm theo Thông tư này 06 biểu mẫu nghiệp vụ phục vụ công tác tuần tra, kiểm soát và xử lý vi phạm hành chính của Cảnh sát giao thông.</p>
    <p>2. Các biểu mẫu phải được in, quản lý, cấp phát và sử dụng đúng quy định của Bộ Công an.</p>
    """)

    articles.append("""
    <p><b>Điều 30. Bảo đảm kinh phí, cơ sở vật chất kỹ thuật</b></p>
    <p>Kinh phí bảo đảm cho công tác tuần tra, kiểm soát, trang bị phương tiện, thiết bị kỹ thuật nghiệp vụ do ngân sách nhà nước bảo đảm theo quy định của pháp luật.</p>
    """)

    articles.append("""
    <p><b>Điều 31. Áp dụng công nghệ thông tin và chuyển đổi số</b></p>
    <p>Đẩy mạnh ứng dụng công nghệ thông tin, trí tuệ nhân tạo và chuyển đổi số toàn diện trong công tác tuần tra, kiểm soát, xử lý vi phạm và lưu trữ hồ sơ điện tử.</p>
    """)

    articles.append("""
    <p><b>Điều 32. Hiệu lực thi hành</b></p>
    <p>1. Thông tư này có hiệu lực thi hành kể từ ngày 01 tháng 01 năm 2025.</p>
    <p>2. Thông tư này bãi bỏ:</p>
    <p>a) Thông tư số 32/2023/TT-BCA ngày 01 tháng 08 năm 2023 của Bộ trưởng Bộ Công an quy định nhiệm vụ, quyền hạn, hình thức, nội dung và quy trình tuần tra, kiểm soát, xử lý vi phạm hành chính về giao thông đường bộ của Cảnh sát giao thông;</p>
    <p>b) Bãi bỏ Điều 1 Thông tư số 28/2024/TT-BCA ngày 29 tháng 06 năm 2024 của Bộ trưởng Bộ Công an sửa đổi, bổ sung một số điều của Thông tư số 32/2023/TT-BCA và Thông tư số 24/2023/TT-BCA.</p>
    """)

    articles.append("""
    <p><b>Điều 33. Trách nhiệm thi hành</b></p>
    <p>1. Cục trưởng Cục Cảnh sát giao thông có trách nhiệm chỉ đạo, hướng dẫn, kiểm tra, đôn đốc việc thực hiện Thông tư này.</p>
    <p>2. Giám đốc Công an tỉnh, thành phố trực thuộc Trung ương có trách nhiệm tổ chức triển khai thực hiện Thông tư này tại địa phương.</p>
    <p>3. Thủ trưởng các đơn vị trực thuộc Bộ Công an, Giám đốc Công an các địa phương chịu trách nhiệm thi hành Thông tư này.</p>
    """)

    html_content = f"""<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <title>Thông tư 73/2024/TT-BCA quy định công tác tuần tra, kiểm soát, xử lý vi phạm của CSGT</title>
</head>
<body>
<div class="doc-header">
    <p><b>BỘ CÔNG AN</b><br>Số: 73/2024/TT-BCA</p>
    <p><b>CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM</b><br>Độc lập - Tự do - Hạnh phúc</p>
    <p><i>Hà Nội, ngày 15 tháng 11 năm 2024</i></p>
    <h2>THÔNG TƯ</h2>
    <h3>Quy định về công tác tuần tra, kiểm soát, xử lý vi phạm hành chính về trật tự, an toàn giao thông đường bộ của Cảnh sát giao thông</h3>
</div>
<div class="doc-body">
{''.join(articles)}
</div>
</body>
</html>"""
    out_file = RAW_DIR / "73_2024_TT_BCA.html"
    out_file.write_text(html_content, encoding="utf-8")
    print(f"Generated {out_file.name} with {len(articles)} articles ({len(html_content)} bytes)")

generate_73_2024()
