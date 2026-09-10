import hashlib
from pathlib import Path

cur_text = Path("data/01_raw/traffic_p1_2_batch/94_2026_ND_CP.html").read_text(encoding="utf-8")

# Let's see if we can find the exact text of the corrupted version
# The corrupted Điều 26:
corrupted_d26 = """    <p><b>Điều 26. Nội dung sát hạch mô phỏng các tình huống giao thông</b></p>
    <p>1. Thí sinh dự sát hạch lái xe ô tô các hạng phải thực hiện bài sát hạch mô phỏng các tình huống giao thông trên máy tính gồm 10 câu hỏi tình huống mô phỏng.</p>
    <p>2. Điểm tối đa của bài sát hạch mô phỏng là 50 điểm, mỗi câu hỏi có điểm từ 0 đến 5 điểm tùy thuộc vào thời điểm thí sinh phát hiện và xử lý tình huống.</p>
    <p>3. Thí sinh đạt từ 35/50 điểm trở lên được công nhận đạt nội dung sát hạch mô phỏng.</p>"""

# Let's check if replacing the current Điều 26 gives e972ddd7 or what it gives
cur_d26 = """    <p><b>Điều 26. Giấy phép sát hạch, thẩm quyền cấp, cấp lại và thu hồi giấy phép sát hạch</b></p>
    <p>1. Trung tâm sát hạch lái xe chỉ được hoạt động khi được cơ quan có thẩm quyền cấp Giấy phép sát hạch lái xe. Phòng Cảnh sát giao thông Công an cấp tỉnh là cơ quan có thẩm quyền cấp, cấp lại và thu hồi Giấy phép sát hạch lái xe cho các trung tâm sát hạch lái xe trên địa bàn khi đáp ứng đầy đủ các điều kiện quy định tại Điều 23, Điều 24 và Điều 25 của Nghị định này.</p>
    <p>2. Giấy phép sát hạch lái xe được cấp lại trong các trường hợp: Giấy phép sát hạch bị mất hoặc bị hư hại; thay đổi tên của trung tâm sát hạch; có sự thay đổi về thiết bị sát hạch, quy mô, chủng loại hoặc số lượng xe cơ giới sử dụng để sát hạch lái xe. Giấy phép sát hạch cấp lại phải bao gồm nội dung hủy bỏ hiệu lực của Giấy phép đã cấp trước đó.</p>
    <p>3. Giấy phép sát hạch lái xe bị thu hồi khi thuộc một trong các trường hợp: có hành vi gian lận để được cấp Giấy phép sát hạch; không triển khai hoạt động sát hạch lái xe sau thời hạn 24 tháng kể từ ngày được cấp phép; giấy phép được cấp không đúng thẩm quyền hoặc sai quy định; tẩy xóa, sửa chữa làm sai lệch nội dung giấy phép; cố ý can thiệp vào thiết bị, phương tiện, phần mềm sát hạch làm sai lệch kết quả sát hạch; hoặc trung tâm sát hạch lái xe giải thể theo quy định của pháp luật.</p>"""

target_hash = "e972ddd7b61ff5f186e3cd500425620456b782948fde899e61fea76e1c0db744"

# Let's test
if cur_d26 in cur_text:
    test_text = cur_text.replace(cur_d26, corrupted_d26)
    h = hashlib.sha256(test_text.encode("utf-8")).hexdigest()
    print("Test hash with corrupted d26:", h)
    if h == target_hash:
        print("MATCHED TARGET HASH EXACTLY!")
        Path("data/05_quarantine/94_2026_ND_CP_corrupted.html").write_text(test_text, encoding="utf-8")
    else:
        print("Target was:", target_hash)
else:
    print("cur_d26 not found in cur_text")
