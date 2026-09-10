import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
import os
import json
import uuid
from pathlib import Path
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
load_dotenv(PROJECT_ROOT / ".env")

OUT_DIR = PROJECT_ROOT / "data" / "03_parsed" / "traffic_p3_batch"
OUT_DIR.mkdir(parents=True, exist_ok=True)
CHUNKS_FILE = OUT_DIR / "p3_2_chunks.json"

def build_p3_2_chunks():
    print("=" * 80)
    print("   BUILDING CHUNKS FOR P3.2: NĐ 158/2024 + NĐ 218/2026")
    print("=" * 80)

    doc_id_158 = "traffic_transport_158_2024_nd_cp"
    off_158 = "158/2024/NĐ-CP"
    title_158 = "Nghị định 158/2024/NĐ-CP quy định về hoạt động vận tải đường bộ"
    url_158 = "https://vanban.chinhphu.vn/?pageid=27160&docid=212082"
    sha_158 = "2c9a9e4dbaebf415b33980370b3c184b50d1edc4b220b7f473674527a1c47fe5"

    doc_id_218 = "traffic_amendment_218_2026_nd_cp"
    off_218 = "218/2026/NĐ-CP"
    title_218 = "Nghị định 218/2026/NĐ-CP sửa đổi, bổ sung một số điều của Nghị định 158/2024/NĐ-CP về hoạt động vận tải đường bộ"
    url_218 = "https://vanban.chinhphu.vn/?pageid=27160&docid=212455"
    sha_218 = "97df896cc2fbac93fbbd18e08117e8510f8560b112883657fc0e9f8bc918460b"

    chunks = []

    # 1. Điều 1 NĐ 158
    c1_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{doc_id_158}:article_1:v1_current"))
    c1_text = """Điều 1. Phạm vi điều chỉnh
1. Nghị định này quy định về kinh doanh, điều kiện kinh doanh và việc cấp, thu hồi Giấy phép kinh doanh vận tải bằng xe ô tô, bằng xe bốn bánh có gắn động cơ; cấp, thu hồi phù hiệu, biển hiệu; hoạt động vận tải nội bộ bằng xe ô tô, bằng xe bốn bánh có gắn động cơ; trình tự, thủ tục cấp, cấp lại, thu hồi giấy phép vận tải đường bộ quốc tế, giấy phép liên vận cho đơn vị kinh doanh vận tải và phương tiện; gia hạn thời gian lưu hành cho phương tiện của nước ngoài tại Việt Nam tham gia vận chuyển người, hàng hóa theo các Điều ước quốc tế mà nước Cộng hòa xã hội chủ nghĩa Việt Nam là thành viên.
2. Hoạt động vận tải hành khách bằng xe taxi, xe buýt, xe tuyến cố định, xe hợp đồng, xe du lịch và vận tải hàng hóa bằng xe ô tô thực hiện theo quy định của Nghị định này và các quy định khác của pháp luật có liên quan."""
    chunks.append({
        "chunk_id": c1_id,
        "document_id": doc_id_158,
        "doc_id": doc_id_158,
        "official_number": off_158,
        "doc_title": title_158,
        "canonical_provision_id": f"{doc_id_158}:article_1",
        "version_id": "v1_current",
        "unit_type": "ARTICLE",
        "article_number": 1,
        "chapter": "Chương I",
        "chapter_title": "QUY ĐỊNH CHUNG",
        "article_title": "Phạm vi điều chỉnh",
        "effective_date": "2025-01-01",
        "valid_from": "2025-01-01",
        "valid_to": None,
        "valid_interval": "[2025-01-01, +inf)",
        "legal_status": "CON_HIEU_LUC",
        "scope_tags": ["TRAFFIC_P3", "VAN_TAI_DUONG_BO", "ND158_ORIGINAL"],
        "amended_by": [],
        "content": c1_text,
        "full_search_text": f"[{off_158} - {title_158}]\nChương I: QUY ĐỊNH CHUNG > Điều 1: Phạm vi điều chỉnh\n{c1_text}",
        "source_url": url_158,
        "sha256": sha_158,
        "batch": "TRAFFIC_P3"
    })

    # 2. Điều 2 NĐ 158
    c2_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{doc_id_158}:article_2:v1_current"))
    c2_text = """Điều 2. Đối tượng áp dụng
1. Nghị định này áp dụng đối với cơ quan, tổ chức, cá nhân có liên quan đến hoạt động vận tải đường bộ bằng xe ô tô, xe bốn bánh có gắn động cơ trên lãnh thổ nước Cộng hòa xã hội chủ nghĩa Việt Nam.
2. Nghị định này không áp dụng đối với xe ô tô, xe bốn bánh có gắn động cơ của quân đội, công an sử dụng vào mục đích quốc phòng, an ninh."""
    chunks.append({
        "chunk_id": c2_id,
        "document_id": doc_id_158,
        "doc_id": doc_id_158,
        "official_number": off_158,
        "doc_title": title_158,
        "canonical_provision_id": f"{doc_id_158}:article_2",
        "version_id": "v1_current",
        "unit_type": "ARTICLE",
        "article_number": 2,
        "chapter": "Chương I",
        "chapter_title": "QUY ĐỊNH CHUNG",
        "article_title": "Đối tượng áp dụng",
        "effective_date": "2025-01-01",
        "valid_from": "2025-01-01",
        "valid_to": None,
        "valid_interval": "[2025-01-01, +inf)",
        "legal_status": "CON_HIEU_LUC",
        "scope_tags": ["TRAFFIC_P3", "VAN_TAI_DUONG_BO", "ND158_ORIGINAL"],
        "amended_by": [],
        "content": c2_text,
        "full_search_text": f"[{off_158} - {title_158}]\nChương I: QUY ĐỊNH CHUNG > Điều 2: Đối tượng áp dụng\n{c2_text}",
        "source_url": url_158,
        "sha256": sha_158,
        "batch": "TRAFFIC_P3"
    })

    # 3. Điều 3 NĐ 158
    c3_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{doc_id_158}:article_3:v1_current"))
    c3_text = """Điều 3. Giải thích từ ngữ
1. Kinh doanh vận tải bằng xe ô tô là việc thực hiện ít nhất một trong các công đoạn chính của hoạt động vận tải (trực tiếp điều hành phương tiện, lái xe hoặc quyết định giá cước vận tải) để vận chuyển hành khách, hàng hóa trên đường bộ nhằm mục đích sinh lợi.
2. Kinh doanh vận tải hành khách bằng xe taxi là loại hình kinh doanh vận tải hành khách sử dụng xe ô tô có sức chứa dưới 09 chỗ (kể cả người lái xe) để vận chuyển hành khách theo lịch trình và hành trình do hành khách yêu cầu; cước chuyến đi được tính theo đồng hồ tính tiền hoặc tính theo phần mềm tính tiền hoặc thỏa thuận với hành khách.
3. Kinh doanh vận tải hành khách theo hợp đồng là loại hình kinh doanh vận tải hành khách sử dụng xe ô tô thực hiện vận chuyển hành khách theo hợp đồng vận chuyển bằng văn bản giấy hoặc hợp đồng điện tử giữa đơn vị kinh doanh vận tải hành khách với người thuê vận tải có nhu cầu thuê cả chuyến xe (bao gồm cả thuê người lái xe).
4. Vận tải nội bộ là việc cơ quan, tổ chức, cá nhân sử dụng xe ô tô thuộc quyền sở hữu hoặc quyền sử dụng hợp pháp để vận chuyển người, nội bộ cán bộ, công nhân viên, học sinh, sinh viên hoặc hàng hóa của chính đơn vị mình mà không thu cước vận tải."""
    chunks.append({
        "chunk_id": c3_id,
        "document_id": doc_id_158,
        "doc_id": doc_id_158,
        "official_number": off_158,
        "doc_title": title_158,
        "canonical_provision_id": f"{doc_id_158}:article_3",
        "version_id": "v1_current",
        "unit_type": "ARTICLE",
        "article_number": 3,
        "chapter": "Chương I",
        "chapter_title": "QUY ĐỊNH CHUNG",
        "article_title": "Giải thích từ ngữ",
        "effective_date": "2025-01-01",
        "valid_from": "2025-01-01",
        "valid_to": None,
        "valid_interval": "[2025-01-01, +inf)",
        "legal_status": "CON_HIEU_LUC",
        "scope_tags": ["TRAFFIC_P3", "VAN_TAI_DUONG_BO", "ND158_ORIGINAL"],
        "amended_by": [],
        "content": c3_text,
        "full_search_text": f"[{off_158} - {title_158}]\nChương I: QUY ĐỊNH CHUNG > Điều 3: Giải thích từ ngữ\n{c3_text}",
        "source_url": url_158,
        "sha256": sha_158,
        "batch": "TRAFFIC_P3"
    })

    # 4. Điều 4 NĐ 158
    c4_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{doc_id_158}:article_4:v1_current"))
    c4_text = """Điều 4. Quy định đối với xe ô tô kinh doanh vận tải hành khách
1. Phải có phù hiệu "XE CHẠY TUYẾN CỐ ĐỊNH", "XE BUÝT", "XE TAXI", "XE HỢP ĐỒNG", "XE DU LỊCH" dán cố định tại góc trên bên phải ngay sát phía dưới tem kiểm định ở mặt trong kính chắn gió phía trước xe.
2. Phải được lắp đặt thiết bị giám sát hành trình và thiết bị ghi nhận hình ảnh người lái xe theo đúng quy định của pháp luật về trật tự an toàn giao thông đường bộ.
3. Dữ liệu từ thiết bị giám sát hành trình và camera phải được truyền dẫn liên tục, chính xác về hệ thống quản lý dữ liệu của cơ quan có thẩm quyền."""
    chunks.append({
        "chunk_id": c4_id,
        "document_id": doc_id_158,
        "doc_id": doc_id_158,
        "official_number": off_158,
        "doc_title": title_158,
        "canonical_provision_id": f"{doc_id_158}:article_4",
        "version_id": "v1_current",
        "unit_type": "ARTICLE",
        "article_number": 4,
        "chapter": "Chương II",
        "chapter_title": "KINH DOANH VẬN TẢI BẰNG XE Ô TÔ",
        "article_title": "Quy định đối với xe ô tô kinh doanh vận tải hành khách",
        "effective_date": "2025-01-01",
        "valid_from": "2025-01-01",
        "valid_to": None,
        "valid_interval": "[2025-01-01, +inf)",
        "legal_status": "CON_HIEU_LUC",
        "scope_tags": ["TRAFFIC_P3", "XE_HOP_DONG", "PHU_HIEU"],
        "amended_by": [],
        "content": c4_text,
        "full_search_text": f"[{off_158} - {title_158}]\nChương II: KINH DOANH VẬN TẢI BẰNG XE Ô TÔ > Điều 4: Quy định đối với xe ô tô kinh doanh vận tải hành khách\n{c4_text}",
        "source_url": url_158,
        "sha256": sha_158,
        "batch": "TRAFFIC_P3"
    })

    # 5. Điều 7 NĐ 158: v1_original [2025-01-01, 2026-08-10)
    c7_v1_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{doc_id_158}:article_7:v1_original"))
    c7_v1_text = """Điều 7. Kinh doanh vận tải hành khách theo hợp đồng
1. Đơn vị kinh doanh vận tải hành khách theo hợp đồng chỉ được ký hợp đồng vận chuyển hành khách với người thuê vận tải có nhu cầu thuê cả chuyến xe.
2. Hợp đồng vận tải hành khách phải được ký kết trước khi thực hiện chuyến đi, thể hiện đầy đủ thông tin về thời gian, địa điểm đón, trả khách, hành trình, danh sách hành khách và giá cước vận chuyển.
3. Khi vận chuyển hành khách, lái xe phải mang theo bản chính hoặc bản điện tử của hợp đồng vận tải kèm theo danh sách hành khách.
4. Không được gom khách, đón khách ngoài danh sách đính kèm hợp đồng; không được xác nhận đặt chỗ cho từng hành khách; không được bán vé hoặc thu tiền của từng hành khách dưới mọi hình thức."""
    chunks.append({
        "chunk_id": c7_v1_id,
        "document_id": doc_id_158,
        "doc_id": doc_id_158,
        "official_number": off_158,
        "doc_title": title_158,
        "canonical_provision_id": f"{doc_id_158}:article_7",
        "version_id": "v1_original",
        "unit_type": "ARTICLE",
        "article_number": 7,
        "chapter": "Chương II",
        "chapter_title": "KINH DOANH VẬN TẢI BẰNG XE Ô TÔ",
        "article_title": "Kinh doanh vận tải hành khách theo hợp đồng",
        "effective_date": "2025-01-01",
        "valid_from": "2025-01-01",
        "valid_to": "2026-08-10",
        "valid_interval": "[2025-01-01, 2026-08-10)",
        "legal_status": "BI_SUA_DOI",
        "scope_tags": ["TRAFFIC_P3", "XE_HOP_DONG", "ND158_ORIGINAL"],
        "amended_by": ["218/2026/NĐ-CP"],
        "content": c7_v1_text,
        "full_search_text": f"[{off_158} - {title_158}]\nChương II: KINH DOANH VẬN TẢI BẰNG XE Ô TÔ > Điều 7: Kinh doanh vận tải hành khách theo hợp đồng (Nguyên bản)\n{c7_v1_text}",
        "source_url": url_158,
        "sha256": sha_158,
        "batch": "TRAFFIC_P3"
    })

    # 6. Điều 7 NĐ 158: v2_amended [2026-08-10, +inf)
    c7_v2_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{doc_id_158}:article_7:v2_amended"))
    c7_v2_text = """Điều 7. Kinh doanh vận tải hành khách theo hợp đồng (Được sửa đổi, bổ sung bởi Điều 1 Khoản 1 Nghị định 218/2026/NĐ-CP từ ngày 10/08/2026)
1. Đơn vị kinh doanh vận tải hành khách theo hợp đồng chỉ được ký hợp đồng vận chuyển hành khách với người thuê vận tải có nhu cầu thuê cả chuyến xe.
2. Hợp đồng vận tải hành khách phải được ký kết trước khi thực hiện chuyến đi, thể hiện đầy đủ thông tin về thời gian, địa điểm đón, trả khách, hành trình, danh sách hành khách và giá cước vận chuyển.
3. Khi vận chuyển hành khách, lái xe phải mang theo bản chính hoặc bản điện tử của hợp đồng vận tải kèm theo danh sách hành khách.
4. Đơn vị kinh doanh vận tải hành khách theo hợp đồng và người lái xe không được đón, trả khách tại trụ sở chính, trụ sở chi nhánh, văn phòng đại diện hoặc địa điểm cố định khác do đơn vị kinh doanh vận tải thuê, hợp tác kinh doanh trên các tuyến đường phố; không được ấn định hành trình, lịch trình cố định để phục vụ cho nhiều hành khách hoặc nhiều người thuê vận tải khác nhau.
5. Nghiêm cấm việc xác nhận đặt chỗ cho từng hành khách, gom khách, bán vé hoặc thu tiền trực tiếp của từng hành khách dưới mọi hình thức đối với xe kinh doanh vận tải theo hợp đồng.
6. Từ ngày 01 tháng 01 năm 2028, đơn vị kinh doanh vận tải hành khách theo hợp đồng phải thực hiện kết nối, chia sẻ tự động dữ liệu về nội dung hợp đồng vận tải hành khách điện tử cho Cục Cảnh sát giao thông (Bộ Công an) và Cục Đường bộ Việt Nam trước khi thực hiện chuyến đi."""
    chunks.append({
        "chunk_id": c7_v2_id,
        "document_id": doc_id_158,
        "doc_id": doc_id_158,
        "official_number": off_158,
        "doc_title": title_158,
        "canonical_provision_id": f"{doc_id_158}:article_7",
        "version_id": "v2_amended",
        "unit_type": "ARTICLE",
        "article_number": 7,
        "chapter": "Chương II",
        "chapter_title": "KINH DOANH VẬN TẢI BẰNG XE Ô TÔ",
        "article_title": "Kinh doanh vận tải hành khách theo hợp đồng (Sửa đổi bởi NĐ 218/2026)",
        "effective_date": "2026-08-10",
        "valid_from": "2026-08-10",
        "valid_to": None,
        "valid_interval": "[2026-08-10, +inf)",
        "legal_status": "CON_HIEU_LUC",
        "scope_tags": ["TRAFFIC_P3", "XE_HOP_DONG", "CAM_DON_TRA_KHACH_VAN_PHONG", "ND218_AMENDED"],
        "amended_by": ["218/2026/NĐ-CP"],
        "content": c7_v2_text,
        "full_search_text": f"[{off_158} - {title_158}]\nChương II: KINH DOANH VẬN TẢI BẰNG XE Ô TÔ > Điều 7: Kinh doanh vận tải hành khách theo hợp đồng (Sửa đổi bổ sung bởi NĐ 218/2026/NĐ-CP)\n{c7_v2_text}",
        "source_url": url_218,
        "sha256": sha_218,
        "batch": "TRAFFIC_P3"
    })

    # 7. Điều 13 NĐ 158
    c13_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{doc_id_158}:article_13:v1_current"))
    c13_text = """Điều 13. Điều kiện cấp Giấy phép kinh doanh vận tải bằng xe ô tô
1. Đơn vị kinh doanh vận tải phải là doanh nghiệp, hợp tác xã, hộ kinh doanh được thành lập theo quy định của pháp luật.
2. Phương tiện vận tải phải thuộc quyền sở hữu hợp pháp hoặc quyền sử dụng hợp pháp theo hợp đồng thuê phương tiện bằng văn bản; đáp ứng đầy đủ quy định về niên hạn sử dụng, kiểm định an toàn kỹ thuật và bảo vệ môi trường.
3. Người trực tiếp điều hành hoạt động vận tải của doanh nghiệp, hợp tác xã phải có trình độ chuyên môn về vận tải từ trung cấp trở lên hoặc có trình độ cao đẳng, đại học chuyên ngành khác."""
    chunks.append({
        "chunk_id": c13_id,
        "document_id": doc_id_158,
        "doc_id": doc_id_158,
        "official_number": off_158,
        "doc_title": title_158,
        "canonical_provision_id": f"{doc_id_158}:article_13",
        "version_id": "v1_current",
        "unit_type": "ARTICLE",
        "article_number": 13,
        "chapter": "Chương III",
        "chapter_title": "ĐIỀU KIỆN KINH DOANH VẬN TẢI",
        "article_title": "Điều kiện cấp Giấy phép kinh doanh vận tải bằng xe ô tô",
        "effective_date": "2025-01-01",
        "valid_from": "2025-01-01",
        "valid_to": None,
        "valid_interval": "[2025-01-01, +inf)",
        "legal_status": "CON_HIEU_LUC",
        "scope_tags": ["TRAFFIC_P3", "DIEU_KIEN_KDVT"],
        "amended_by": [],
        "content": c13_text,
        "full_search_text": f"[{off_158} - {title_158}]\nChương III: ĐIỀU KIỆN KINH DOANH VẬN TẢI > Điều 13: Điều kiện cấp Giấy phép kinh doanh vận tải bằng xe ô tô\n{c13_text}",
        "source_url": url_158,
        "sha256": sha_158,
        "batch": "TRAFFIC_P3"
    })

    # 8. Điều 19 NĐ 158: v1_original [2025-01-01, 2026-08-10)
    c19_v1_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{doc_id_158}:article_19:v1_original"))
    c19_v1_text = """Điều 19. Cấp và thu hồi Giấy phép kinh doanh vận tải bằng xe ô tô
1. Giấy phép kinh doanh vận tải bằng xe ô tô do Sở Giao thông vận tải cấp cho đơn vị kinh doanh vận tải đáp ứng đủ điều kiện theo quy định.
2. Đơn vị kinh doanh vận tải bị thu hồi Giấy phép kinh doanh không thời hạn trong các trường hợp:
a) Cung cấp bản sao không đúng với bản chính hoặc thông tin sai lệch trong hồ sơ đề nghị cấp Giấy phép;
b) Chấm dứt hoạt động theo quy định của pháp luật hoặc theo đề nghị của đơn vị kinh doanh vận tải;
c) Không kinh doanh vận tải toàn bộ các loại hình ghi trên Giấy phép trong thời hạn 06 tháng kể từ ngày được cấp;
d) Sửa chữa hoặc làm sai lệch dữ liệu thiết bị giám sát hành trình, camera ghi nhận hình ảnh."""
    chunks.append({
        "chunk_id": c19_v1_id,
        "document_id": doc_id_158,
        "doc_id": doc_id_158,
        "official_number": off_158,
        "doc_title": title_158,
        "canonical_provision_id": f"{doc_id_158}:article_19",
        "version_id": "v1_original",
        "unit_type": "ARTICLE",
        "article_number": 19,
        "chapter": "Chương IV",
        "chapter_title": "CẤP, THU HỒI GIẤY PHÉP KINH DOANH",
        "article_title": "Cấp và thu hồi Giấy phép kinh doanh vận tải",
        "effective_date": "2025-01-01",
        "valid_from": "2025-01-01",
        "valid_to": "2026-08-10",
        "valid_interval": "[2025-01-01, 2026-08-10)",
        "legal_status": "BI_SUA_DOI",
        "scope_tags": ["TRAFFIC_P3", "THU_HOI_GIAY_PHEP", "ND158_ORIGINAL"],
        "amended_by": ["218/2026/NĐ-CP"],
        "content": c19_v1_text,
        "full_search_text": f"[{off_158} - {title_158}]\nChương IV: CẤP, THU HỒI GIẤY PHÉP KINH DOANH > Điều 19: Cấp và thu hồi Giấy phép kinh doanh vận tải (Nguyên bản)\n{c19_v1_text}",
        "source_url": url_158,
        "sha256": sha_158,
        "batch": "TRAFFIC_P3"
    })

    # 9. Điều 19 NĐ 158: v2_amended [2026-08-10, +inf)
    c19_v2_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{doc_id_158}:article_19:v2_amended"))
    c19_v2_text = """Điều 19. Cấp và thu hồi Giấy phép kinh doanh vận tải bằng xe ô tô (Được bổ sung bởi Điều 1 Khoản 2 Nghị định 218/2026/NĐ-CP từ ngày 10/08/2026)
1. Giấy phép kinh doanh vận tải bằng xe ô tô do Sở Giao thông vận tải cấp cho đơn vị kinh doanh vận tải đáp ứng đủ điều kiện theo quy định.
2. Đơn vị kinh doanh vận tải bị thu hồi Giấy phép kinh doanh không thời hạn trong các trường hợp:
a) Cung cấp bản sao không đúng với bản chính hoặc thông tin sai lệch trong hồ sơ đề nghị cấp Giấy phép;
b) Chấm dứt hoạt động theo quy định của pháp luật hoặc theo đề nghị của đơn vị kinh doanh vận tải;
c) Không kinh doanh vận tải toàn bộ các loại hình ghi trên Giấy phép trong thời hạn 06 tháng kể từ ngày được cấp;
d) Sửa chữa hoặc làm sai lệch dữ liệu thiết bị giám sát hành trình, camera ghi nhận hình ảnh;
đ) Đơn vị kinh doanh vận tải hành khách theo hợp đồng vi phạm quy định về việc đón, trả khách tại trụ sở chính, chi nhánh, văn phòng đại diện từ 03 lần trở lên trong thời gian 01 tháng hoặc tổ chức hoạt động gom khách, bán vé trá hình tuyến cố định."""
    chunks.append({
        "chunk_id": c19_v2_id,
        "document_id": doc_id_158,
        "doc_id": doc_id_158,
        "official_number": off_158,
        "doc_title": title_158,
        "canonical_provision_id": f"{doc_id_158}:article_19",
        "version_id": "v2_amended",
        "unit_type": "ARTICLE",
        "article_number": 19,
        "chapter": "Chương IV",
        "chapter_title": "CẤP, THU HỒI GIẤY PHÉP KINH DOANH",
        "article_title": "Cấp và thu hồi Giấy phép kinh doanh vận tải (Bổ sung bởi NĐ 218/2026)",
        "effective_date": "2026-08-10",
        "valid_from": "2026-08-10",
        "valid_to": None,
        "valid_interval": "[2026-08-10, +inf)",
        "legal_status": "CON_HIEU_LUC",
        "scope_tags": ["TRAFFIC_P3", "THU_HOI_GIAY_PHEP", "VI_PHAM_DON_TRA_KHACH", "ND218_AMENDED"],
        "amended_by": ["218/2026/NĐ-CP"],
        "content": c19_v2_text,
        "full_search_text": f"[{off_158} - {title_158}]\nChương IV: CẤP, THU HỒI GIẤY PHÉP KINH DOANH > Điều 19: Cấp và thu hồi Giấy phép kinh doanh vận tải (Bổ sung điểm đ bởi NĐ 218/2026/NĐ-CP)\n{c19_v2_text}",
        "source_url": url_218,
        "sha256": sha_218,
        "batch": "TRAFFIC_P3"
    })

    # 10. Điều 45 NĐ 158
    c45_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{doc_id_158}:article_45:v1_current"))
    c45_text = """Điều 45. Hiệu lực thi hành
1. Nghị định này có hiệu lực thi hành từ ngày 01 tháng 01 năm 2025.
2. Nghị định này thay thế Nghị định số 10/2020/NĐ-CP ngày 17 tháng 01 năm 2020 của Chính phủ; Nghị định số 47/2022/NĐ-CP ngày 19 tháng 7 năm 2022 và Nghị định số 41/2024/NĐ-CP ngày 16 tháng 4 năm 2024 của Chính phủ."""
    chunks.append({
        "chunk_id": c45_id,
        "document_id": doc_id_158,
        "doc_id": doc_id_158,
        "official_number": off_158,
        "doc_title": title_158,
        "canonical_provision_id": f"{doc_id_158}:article_45",
        "version_id": "v1_current",
        "unit_type": "ARTICLE",
        "article_number": 45,
        "chapter": "Chương VI",
        "chapter_title": "ĐIỀU KHOẢN THI HÀNH",
        "article_title": "Hiệu lực thi hành",
        "effective_date": "2025-01-01",
        "valid_from": "2025-01-01",
        "valid_to": None,
        "valid_interval": "[2025-01-01, +inf)",
        "legal_status": "CON_HIEU_LUC",
        "scope_tags": ["TRAFFIC_P3", "HIEU_LUC_THI_HANH"],
        "amended_by": [],
        "content": c45_text,
        "full_search_text": f"[{off_158} - {title_158}]\nChương VI: ĐIỀU KHOẢN THI HÀNH > Điều 45: Hiệu lực thi hành\n{c45_text}",
        "source_url": url_158,
        "sha256": sha_158,
        "batch": "TRAFFIC_P3"
    })

    # 11. NĐ 218 Điều 1
    c218_1_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{doc_id_218}:article_1:v1_current"))
    c218_1_text = """Điều 1. Sửa đổi, bổ sung một số điều của Nghị định số 158/2024/NĐ-CP
1. Sửa đổi, bổ sung khoản 4 và bổ sung khoản 5, khoản 6 vào Điều 7 (Nghiêm cấm xe hợp đồng đón trả khách tại trụ sở chính, văn phòng đại diện, chi nhánh trên đường phố; nghiêm cấm gom khách, xác nhận đặt chỗ từng khách; quy định kết nối dữ liệu CSGT từ 01/01/2028).
2. Bổ sung điểm đ vào khoản 2 Điều 19 về các trường hợp thu hồi Giấy phép kinh doanh vận tải (Thu hồi Giấy phép đối với đơn vị kinh doanh vận tải hành khách theo hợp đồng đón trả khách tại văn phòng đại diện từ 03 lần trở lên trong 01 tháng hoặc gom khách trá hình)."""
    chunks.append({
        "chunk_id": c218_1_id,
        "document_id": doc_id_218,
        "doc_id": doc_id_218,
        "official_number": off_218,
        "doc_title": title_218,
        "canonical_provision_id": f"{doc_id_218}:article_1",
        "version_id": "v1_current",
        "unit_type": "ARTICLE",
        "article_number": 1,
        "chapter": "Chương I",
        "chapter_title": "QUY ĐỊNH CHUNG",
        "article_title": "Sửa đổi, bổ sung một số điều của Nghị định số 158/2024/NĐ-CP",
        "effective_date": "2026-08-10",
        "valid_from": "2026-08-10",
        "valid_to": None,
        "valid_interval": "[2026-08-10, +inf)",
        "legal_status": "CON_HIEU_LUC",
        "scope_tags": ["TRAFFIC_P3", "ND218_AMENDMENT"],
        "amends": ["158/2024/NĐ-CP"],
        "content": c218_1_text,
        "full_search_text": f"[{off_218} - {title_218}]\nĐiều 1: Sửa đổi, bổ sung một số điều của Nghị định số 158/2024/NĐ-CP\n{c218_1_text}",
        "source_url": url_218,
        "sha256": sha_218,
        "batch": "TRAFFIC_P3"
    })

    # 12. NĐ 218 Điều 2
    c218_2_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{doc_id_218}:article_2:v1_current"))
    c218_2_text = """Điều 2. Hiệu lực thi hành
1. Nghị định này có hiệu lực thi hành từ ngày 10 tháng 08 năm 2026.
2. Các Bộ trưởng, Thủ trưởng cơ quan ngang bộ, Thủ trưởng cơ quan thuộc Chính phủ, Chủ tịch Ủy ban nhân dân các tỉnh, thành phố trực thuộc trung ương chịu trách nhiệm thi hành Nghị định này."""
    chunks.append({
        "chunk_id": c218_2_id,
        "document_id": doc_id_218,
        "doc_id": doc_id_218,
        "official_number": off_218,
        "doc_title": title_218,
        "canonical_provision_id": f"{doc_id_218}:article_2",
        "version_id": "v1_current",
        "unit_type": "ARTICLE",
        "article_number": 2,
        "chapter": "Chương I",
        "chapter_title": "QUY ĐỊNH CHUNG",
        "article_title": "Hiệu lực thi hành",
        "effective_date": "2026-08-10",
        "valid_from": "2026-08-10",
        "valid_to": None,
        "valid_interval": "[2026-08-10, +inf)",
        "legal_status": "CON_HIEU_LUC",
        "scope_tags": ["TRAFFIC_P3", "ND218_AMENDMENT"],
        "amends": ["158/2024/NĐ-CP"],
        "content": c218_2_text,
        "full_search_text": f"[{off_218} - {title_218}]\nĐiều 2: Hiệu lực thi hành\n{c218_2_text}",
        "source_url": url_218,
        "sha256": sha_218,
        "batch": "TRAFFIC_P3"
    })

    with open(CHUNKS_FILE, "w", encoding="utf-8") as f:
        json.dump(chunks, f, ensure_ascii=False, indent=2)

    print(f"[+] Successfully built {len(chunks)} chunks for P3.2 in {CHUNKS_FILE}")
    for c in chunks:
        print(f"  - {c['doc_id']} {c.get('article_number')} {c.get('version_id')} -> {c['valid_interval']}")

if __name__ == "__main__":
    build_p3_2_chunks()
