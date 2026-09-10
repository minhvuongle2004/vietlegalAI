import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
import os
import json
import requests
from pathlib import Path
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
load_dotenv(PROJECT_ROOT / ".env")

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

def sync_p3_2():
    print("=" * 80)
    print("   P3.2 SUPABASE SYNC: NĐ 158/2024 + NĐ 218/2026")
    print("=" * 80)

    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }

    # 1. Insert / Update NĐ 158 into legal_documents
    doc_id_158 = "traffic_transport_158_2024_nd_cp"
    r_chk_158 = requests.get(f"{SUPABASE_URL}/rest/v1/legal_documents?id=eq.{doc_id_158}", headers=headers).json()
    if not r_chk_158:
        doc158_payload = {
            "id": doc_id_158,
            "official_number": "158/2024/NĐ-CP",
            "title": "Nghị định quy định về hoạt động vận tải đường bộ",
            "short_title": "Nghị định 158/2024/NĐ-CP",
            "doc_type": "NGHI_DINH",
            "issuer": "Chính phủ",
            "signer": "Trần Hồng Hà",
            "issue_date": "2024-12-18",
            "effective_date": "2025-01-01",
            "expiry_date": None,
            "status": "CON_HIEU_LUC",
            "source_url": "https://vanban.chinhphu.vn/?pageid=27160&docid=212082",
            "raw_content": None,
            "metadata": {
                "sha256": "2c9a9e4dbaebf415b33980370b3c184b50d1edc4b220b7f473674527a1c47fe5",
                "amended_by": ["218/2026/NĐ-CP"],
                "replaces": ["10/2020/NĐ-CP", "47/2022/NĐ-CP", "41/2024/NĐ-CP"],
                "document_role": "ORIGINAL",
                "batch": "TRAFFIC_P3"
            }
        }
        r_ins = requests.post(f"{SUPABASE_URL}/rest/v1/legal_documents", headers=headers, json=doc158_payload)
        print(f"[+] Inserted NĐ 158 into legal_documents: status {r_ins.status_code}")
    else:
        print("[=] NĐ 158 already exists in legal_documents.")

    # 2. Insert / Update NĐ 218 into legal_documents
    doc_id_218 = "traffic_amendment_218_2026_nd_cp"
    r_chk_218 = requests.get(f"{SUPABASE_URL}/rest/v1/legal_documents?id=eq.{doc_id_218}", headers=headers).json()
    if not r_chk_218:
        doc218_payload = {
            "id": doc_id_218,
            "official_number": "218/2026/NĐ-CP",
            "title": "Nghị định sửa đổi, bổ sung một số điều của Nghị định số 158/2024/NĐ-CP ngày 18 tháng 12 năm 2024 của Chính phủ quy định về hoạt động vận tải đường bộ",
            "short_title": "Nghị định 218/2026/NĐ-CP",
            "doc_type": "NGHI_DINH",
            "issuer": "Chính phủ",
            "signer": "Trần Hồng Hà",
            "issue_date": "2026-06-19",
            "effective_date": "2026-08-10",
            "expiry_date": None,
            "status": "CON_HIEU_LUC",
            "source_url": "https://vanban.chinhphu.vn/?pageid=27160&docid=212455",
            "raw_content": None,
            "metadata": {
                "sha256": "97df896cc2fbac93fbbd18e08117e8510f8560b112883657fc0e9f8bc918460b",
                "amends": ["158/2024/NĐ-CP"],
                "target_document_id": "traffic_transport_158_2024_nd_cp",
                "document_role": "AMENDMENT",
                "batch": "TRAFFIC_P3"
            }
        }
        r_ins = requests.post(f"{SUPABASE_URL}/rest/v1/legal_documents", headers=headers, json=doc218_payload)
        print(f"[+] Inserted NĐ 218 into legal_documents: status {r_ins.status_code}")
    else:
        print("[=] NĐ 218 already exists in legal_documents.")

    # 3. Check / Insert articles for NĐ 158
    r_chk_art158 = requests.get(f"{SUPABASE_URL}/rest/v1/legal_articles?document_id=eq.{doc_id_158}", headers=headers).json()
    if len(r_chk_art158) == 0:
        articles_158 = [
            {
                "document_id": doc_id_158,
                "article_number": 1,
                "article_title": "Phạm vi điều chỉnh",
                "full_text": """Điều 1. Phạm vi điều chỉnh
1. Nghị định này quy định về kinh doanh, điều kiện kinh doanh và việc cấp, thu hồi Giấy phép kinh doanh vận tải bằng xe ô tô, bằng xe bốn bánh có gắn động cơ; cấp, thu hồi phù hiệu, biển hiệu; hoạt động vận tải nội bộ bằng xe ô tô, bằng xe bốn bánh có gắn động cơ; trình tự, thủ tục cấp, cấp lại, thu hồi giấy phép vận tải đường bộ quốc tế, giấy phép liên vận cho đơn vị kinh doanh vận tải và phương tiện; gia hạn thời gian lưu hành cho phương tiện của nước ngoài tại Việt Nam tham gia vận chuyển người, hàng hóa theo các Điều ước quốc tế mà nước Cộng hòa xã hội chủ nghĩa Việt Nam là thành viên.
2. Hoạt động vận tải hành khách bằng xe taxi, xe buýt, xe tuyến cố định, xe hợp đồng, xe du lịch và vận tải hàng hóa bằng xe ô tô thực hiện theo quy định của Nghị định này và các quy định khác của pháp luật có liên quan.""",
                "chapter_info": "Chương I: QUY ĐỊNH CHUNG",
                "status": "CON_HIEU_LUC"
            },
            {
                "document_id": doc_id_158,
                "article_number": 2,
                "article_title": "Đối tượng áp dụng",
                "full_text": """Điều 2. Đối tượng áp dụng
1. Nghị định này áp dụng đối với cơ quan, tổ chức, cá nhân có liên quan đến hoạt động vận tải đường bộ bằng xe ô tô, xe bốn bánh có gắn động cơ trên lãnh thổ nước Cộng hòa xã hội chủ nghĩa Việt Nam.
2. Nghị định này không áp dụng đối với xe ô tô, xe bốn bánh có gắn động cơ của quân đội, công an sử dụng vào mục đích quốc phòng, an ninh.""",
                "chapter_info": "Chương I: QUY ĐỊNH CHUNG",
                "status": "CON_HIEU_LUC"
            },
            {
                "document_id": doc_id_158,
                "article_number": 3,
                "article_title": "Giải thích từ ngữ",
                "full_text": """Điều 3. Giải thích từ ngữ
1. Kinh doanh vận tải bằng xe ô tô là việc thực hiện ít nhất một trong các công đoạn chính của hoạt động vận tải (trực tiếp điều hành phương tiện, lái xe hoặc quyết định giá cước vận tải) để vận chuyển hành khách, hàng hóa trên đường bộ nhằm mục đích sinh lợi.
2. Kinh doanh vận tải hành khách bằng xe taxi là loại hình kinh doanh vận tải hành khách sử dụng xe ô tô có sức chứa dưới 09 chỗ (kể cả người lái xe) để vận chuyển hành khách theo lịch trình và hành trình do hành khách yêu cầu; cước chuyến đi được tính theo đồng hồ tính tiền hoặc tính theo phần mềm tính tiền hoặc thỏa thuận với hành khách.
3. Kinh doanh vận tải hành khách theo hợp đồng là loại hình kinh doanh vận tải hành khách sử dụng xe ô tô thực hiện vận chuyển hành khách theo hợp đồng vận chuyển bằng văn bản giấy hoặc hợp đồng điện tử giữa đơn vị kinh doanh vận tải hành khách với người thuê vận tải có nhu cầu thuê cả chuyến xe (bao gồm cả thuê người lái xe).
4. Vận tải nội bộ là việc cơ quan, tổ chức, cá nhân sử dụng xe ô tô thuộc quyền sở hữu hoặc quyền sử dụng hợp pháp để vận chuyển người, nội bộ cán bộ, công nhân viên, học sinh, sinh viên hoặc hàng hóa của chính đơn vị mình mà không thu cước vận tải.""",
                "chapter_info": "Chương I: QUY ĐỊNH CHUNG",
                "status": "CON_HIEU_LUC"
            },
            {
                "document_id": doc_id_158,
                "article_number": 4,
                "article_title": "Quy định đối với xe ô tô kinh doanh vận tải hành khách",
                "full_text": """Điều 4. Quy định đối với xe ô tô kinh doanh vận tải hành khách
1. Phải có phù hiệu "XE CHẠY TUYẾN CỐ ĐỊNH", "XE BUÝT", "XE TAXI", "XE HỢP ĐỒNG", "XE DU LỊCH" dán cố định tại góc trên bên phải ngay sát phía dưới tem kiểm định ở mặt trong kính chắn gió phía trước xe.
2. Phải được lắp đặt thiết bị giám sát hành trình và thiết bị ghi nhận hình ảnh người lái xe theo đúng quy định của pháp luật về trật tự an toàn giao thông đường bộ.
3. Dữ liệu từ thiết bị giám sát hành trình và camera phải được truyền dẫn liên tục, chính xác về hệ thống quản lý dữ liệu của cơ quan có thẩm quyền.""",
                "chapter_info": "Chương II: KINH DOANH VẬN TẢI BẰNG XE Ô TÔ",
                "status": "CON_HIEU_LUC"
            },
            {
                "document_id": doc_id_158,
                "article_number": 7,
                "article_title": "Kinh doanh vận tải hành khách theo hợp đồng",
                "full_text": """Điều 7. Kinh doanh vận tải hành khách theo hợp đồng
1. Đơn vị kinh doanh vận tải hành khách theo hợp đồng chỉ được ký hợp đồng vận chuyển hành khách với người thuê vận tải có nhu cầu thuê cả chuyến xe.
2. Hợp đồng vận tải hành khách phải được ký kết trước khi thực hiện chuyến đi, thể hiện đầy đủ thông tin về thời gian, địa điểm đón, trả khách, hành trình, danh sách hành khách và giá cước vận chuyển.
3. Khi vận chuyển hành khách, lái xe phải mang theo bản chính hoặc bản điện tử của hợp đồng vận tải kèm theo danh sách hành khách.
4. Không được gom khách, đón khách ngoài danh sách đính kèm hợp đồng; không được xác nhận đặt chỗ cho từng hành khách; không được bán vé hoặc thu tiền của từng hành khách dưới mọi hình thức.""",
                "chapter_info": "Chương II: KINH DOANH VẬN TẢI BẰNG XE Ô TÔ",
                "status": "BI_SUA_DOI"
            },
            {
                "document_id": doc_id_158,
                "article_number": 13,
                "article_title": "Điều kiện cấp Giấy phép kinh doanh vận tải bằng xe ô tô",
                "full_text": """Điều 13. Điều kiện cấp Giấy phép kinh doanh vận tải bằng xe ô tô
1. Đơn vị kinh doanh vận tải phải là doanh nghiệp, hợp tác xã, hộ kinh doanh được thành lập theo quy định của pháp luật.
2. Phương tiện vận tải phải thuộc quyền sở hữu hợp pháp hoặc quyền sử dụng hợp pháp theo hợp đồng thuê phương tiện bằng văn bản; đáp ứng đầy đủ quy định về niên hạn sử dụng, kiểm định an toàn kỹ thuật và bảo vệ môi trường.
3. Người trực tiếp điều hành hoạt động vận tải của doanh nghiệp, hợp tác xã phải có trình độ chuyên môn về vận tải từ trung cấp trở lên hoặc có trình độ cao đẳng, đại học chuyên ngành khác.""",
                "chapter_info": "Chương III: ĐIỀU KIỆN KINH DOANH VẬN TẢI",
                "status": "CON_HIEU_LUC"
            },
            {
                "document_id": doc_id_158,
                "article_number": 19,
                "article_title": "Cấp và thu hồi Giấy phép kinh doanh vận tải bằng xe ô tô",
                "full_text": """Điều 19. Cấp và thu hồi Giấy phép kinh doanh vận tải bằng xe ô tô
1. Giấy phép kinh doanh vận tải bằng xe ô tô do Sở Giao thông vận tải cấp cho đơn vị kinh doanh vận tải đáp ứng đủ điều kiện theo quy định.
2. Đơn vị kinh doanh vận tải bị thu hồi Giấy phép kinh doanh không thời hạn trong các trường hợp:
a) Cung cấp bản sao không đúng với bản chính hoặc thông tin sai lệch trong hồ sơ đề nghị cấp Giấy phép;
b) Chấm dứt hoạt động theo quy định của pháp luật hoặc theo đề nghị của đơn vị kinh doanh vận tải;
c) Không kinh doanh vận tải toàn bộ các loại hình ghi trên Giấy phép trong thời hạn 06 tháng kể từ ngày được cấp;
d) Sửa chữa hoặc làm sai lệch dữ liệu thiết bị giám sát hành trình, camera ghi nhận hình ảnh.""",
                "chapter_info": "Chương IV: CẤP, THU HỒI GIẤY PHÉP KINH DOANH",
                "status": "BI_SUA_DOI"
            },
            {
                "document_id": doc_id_158,
                "article_number": 45,
                "article_title": "Hiệu lực thi hành",
                "full_text": """Điều 45. Hiệu lực thi hành
1. Nghị định này có hiệu lực thi hành từ ngày 01 tháng 01 năm 2025.
2. Nghị định này thay thế Nghị định số 10/2020/NĐ-CP ngày 17 tháng 01 năm 2020 của Chính phủ; Nghị định số 47/2022/NĐ-CP ngày 19 tháng 7 năm 2022 và Nghị định số 41/2024/NĐ-CP ngày 16 tháng 4 năm 2024 của Chính phủ.""",
                "chapter_info": "Chương VI: ĐIỀU KHOẢN THI HÀNH",
                "status": "CON_HIEU_LUC"
            }
        ]
        r_ins_art = requests.post(f"{SUPABASE_URL}/rest/v1/legal_articles", headers=headers, json=articles_158)
        print(f"[+] Inserted {len(articles_158)} articles for NĐ 158: status {r_ins_art.status_code}")
    else:
        print(f"[=] Articles for NĐ 158 already exist: {len(r_chk_art158)} articles.")

    # 4. Check / Insert articles for NĐ 218 (Điều 1, Điều 2)
    r_chk_art218 = requests.get(f"{SUPABASE_URL}/rest/v1/legal_articles?document_id=eq.{doc_id_218}", headers=headers).json()
    if len(r_chk_art218) < 2:
        articles_218 = [
            {
                "document_id": doc_id_218,
                "article_number": 1,
                "article_title": "Sửa đổi, bổ sung một số điều của Nghị định số 158/2024/NĐ-CP",
                "full_text": """Điều 1. Sửa đổi, bổ sung một số điều của Nghị định số 158/2024/NĐ-CP
1. Sửa đổi, bổ sung khoản 4 và bổ sung khoản 5, khoản 6 vào Điều 7 như sau:
"4. Đơn vị kinh doanh vận tải hành khách theo hợp đồng và người lái xe không được đón, trả khách tại trụ sở chính, trụ sở chi nhánh, văn phòng đại diện hoặc địa điểm cố định khác do đơn vị kinh doanh vận tải thuê, hợp tác kinh doanh trên các tuyến đường phố; không được ấn định hành trình, lịch trình cố định để phục vụ cho nhiều hành khách hoặc nhiều người thuê vận tải khác nhau.
5. Nghiêm cấm việc xác nhận đặt chỗ cho từng hành khách, gom khách, bán vé hoặc thu tiền trực tiếp của từng hành khách dưới mọi hình thức đối với xe kinh doanh vận tải theo hợp đồng.
6. Từ ngày 01 tháng 01 năm 2028, đơn vị kinh doanh vận tải hành khách theo hợp đồng phải thực hiện kết nối, chia sẻ tự động dữ liệu về nội dung hợp đồng vận tải hành khách điện tử cho Cục Cảnh sát giao thông (Bộ Công an) và Cục Đường bộ Việt Nam trước khi thực hiện chuyến đi."
2. Bổ sung điểm đ vào khoản 2 Điều 19 về các trường hợp thu hồi Giấy phép kinh doanh vận tải như sau:
"đ) Đơn vị kinh doanh vận tải hành khách theo hợp đồng vi phạm quy định về việc đón, trả khách tại trụ sở chính, chi nhánh, văn phòng đại diện từ 03 lần trở lên trong thời gian 01 tháng hoặc tổ chức hoạt động gom khách, bán vé trá hình tuyến cố định.\"""",
                "chapter_info": "Chương I: QUY ĐỊNH CHUNG",
                "status": "CON_HIEU_LUC"
            },
            {
                "document_id": doc_id_218,
                "article_number": 2,
                "article_title": "Hiệu lực thi hành",
                "full_text": """Điều 2. Hiệu lực thi hành
1. Nghị định này có hiệu lực thi hành từ ngày 10 tháng 08 năm 2026.
2. Các Bộ trưởng, Thủ trưởng cơ quan ngang bộ, Thủ trưởng cơ quan thuộc Chính phủ, Chủ tịch Ủy ban nhân dân các tỉnh, thành phố trực thuộc trung ương chịu trách nhiệm thi hành Nghị định này.""",
                "chapter_info": "Chương I: QUY ĐỊNH CHUNG",
                "status": "CON_HIEU_LUC"
            }
        ]
        r_ins_art = requests.post(f"{SUPABASE_URL}/rest/v1/legal_articles", headers=headers, json=articles_218)
        print(f"[+] Inserted {len(articles_218)} articles for NĐ 218: status {r_ins_art.status_code}")
    else:
        print(f"[=] Articles for NĐ 218 already exist: {len(r_chk_art218)} articles.")

    # Verify counts
    h_cnt = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Prefer": "count=exact"}
    r_cnt_docs = requests.get(f"{SUPABASE_URL}/rest/v1/legal_documents?select=id", headers=h_cnt, params={"limit": 1})
    r_cnt_arts = requests.get(f"{SUPABASE_URL}/rest/v1/legal_articles?select=id", headers=h_cnt, params={"limit": 1})
    cnt_docs = r_cnt_docs.headers.get("Content-Range", "0/0").split("/")[-1]
    cnt_arts = r_cnt_arts.headers.get("Content-Range", "0/0").split("/")[-1]
    print(f"[*] Supabase status after P3.2: documents = {cnt_docs}, articles = {cnt_arts}")

if __name__ == "__main__":
    sync_p3_2()
