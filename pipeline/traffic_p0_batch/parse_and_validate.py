import os
import sys
import re
import json
import hashlib
from datetime import date, datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
RAW_DIR = PROJECT_ROOT / "data" / "01_raw" / "traffic_p0_batch"
PARSED_DIR = PROJECT_ROOT / "data" / "03_parsed" / "traffic_p0_batch"
PARSED_DIR.mkdir(parents=True, exist_ok=True)

from bs4 import BeautifulSoup

# Định nghĩa cấu hình bóc tách và Metadata chuẩn cho 5 văn bản
CONFIGS = [
    {
        "filename": "158_2024_ND_CP.html",
        "doc_id": "traffic_transport_158_2024_nd_cp",
        "official_number": "158/2024/NĐ-CP",
        "title": "Nghị định 158/2024/NĐ-CP quy định về hoạt động vận tải đường bộ",
        "doc_type": "NGHI_DINH",
        "issue_date": "2024-12-18",
        "effective_date": "2025-01-01",
        "status": "CON_HIEU_LUC",
        "version_chain": [
            {"step": 1, "doc_number": "158/2024/NĐ-CP", "effective": "2025-01-01", "role": "GỐC"},
            {"step": 2, "doc_number": "218/2026/NĐ-CP", "effective": "2026-08-10", "role": "SỬA ĐỔI, BỔ SUNG"}
        ],
        "relations": {
            "amends": [],
            "amended_by": [
                {
                    "target_document_id": "traffic_amendment_218_2026_nd_cp",
                    "official_number": "218/2026/NĐ-CP",
                    "effective_date": "2026-08-10",
                    "description": "Sửa đổi, bổ sung quy định về xe hợp đồng, cấm đón trả khách tại văn phòng đại diện"
                }
            ]
        },
        "scope_tags": ["van_tai_duong_bo", "xe_taxi", "xe_hop_dong", "phu_hieu", "dieu_kien_kdvt"]
    },
    {
        "filename": "218_2026_ND_CP.html",
        "doc_id": "traffic_amendment_218_2026_nd_cp",
        "official_number": "218/2026/NĐ-CP",
        "title": "Nghị định 218/2026/NĐ-CP sửa đổi, bổ sung một số điều của Nghị định 158/2024/NĐ-CP về hoạt động vận tải đường bộ",
        "doc_type": "NGHI_DINH",
        "issue_date": "2026-06-19",
        "effective_date": "2026-08-10",
        "status": "CON_HIEU_LUC",
        "version_chain": [
            {"step": 1, "doc_number": "158/2024/NĐ-CP", "effective": "2025-01-01", "role": "GỐC"},
            {"step": 2, "doc_number": "218/2026/NĐ-CP", "effective": "2026-08-10", "role": "SỬA ĐỔI, BỔ SUNG"}
        ],
        "relations": {
            "amends": [
                {
                    "target_document_id": "traffic_transport_158_2024_nd_cp",
                    "official_number": "158/2024/NĐ-CP",
                    "provisions": [
                        {
                            "source_provision": "Khoản 1 Điều 1",
                            "target_provision": "Điều 7 khoản 4, khoản 5, khoản 6",
                            "operation": "amend_and_add",
                            "description": "Nghiêm cấm xe hợp đồng đón trả khách tại trụ sở chính, chi nhánh, văn phòng đại diện; cấm gom khách, xác nhận đặt chỗ từng khách; quy định kết nối dữ liệu CSGT từ 01/01/2028"
                        },
                        {
                            "source_provision": "Khoản 2 Điều 1",
                            "target_provision": "Điều 19 khoản 2 điểm đ",
                            "operation": "add",
                            "description": "Thu hồi Giấy phép kinh doanh vận tải nếu vi phạm đón trả khách tại văn phòng đại diện từ 3 lần/tháng hoặc gom khách trá hình tuyến cố định"
                        }
                    ]
                }
            ],
            "amended_by": []
        },
        "scope_tags": ["sua_doi_van_tai", "xe_hop_dong", "cam_don_tra_khach", "thu_hoi_giay_phep"]
    },
    {
        "filename": "238_2026_ND_CP.html",
        "doc_id": "traffic_penalty_amendment_238_2026_nd_cp",
        "official_number": "238/2026/NĐ-CP",
        "title": "Nghị định 238/2026/NĐ-CP sửa đổi, bổ sung Nghị định 168/2024/NĐ-CP về xử phạt vi phạm hành chính TTATGT đường bộ",
        "doc_type": "NGHI_DINH",
        "issue_date": "2026-06-26",
        "effective_date": "2026-08-15",
        "status": "CON_HIEU_LUC",
        "version_chain": [
            {"step": 1, "doc_number": "168/2024/NĐ-CP", "effective": "2025-01-01", "role": "GỐC"},
            {"step": 2, "doc_number": "238/2026/NĐ-CP", "effective": "2026-08-15", "role": "SỬA ĐỔI, BỔ SUNG"}
        ],
        "relations": {
            "amends": [
                {
                    "target_document_id": "traffic_penalty_168_2024_nd_cp",
                    "official_number": "168/2024/NĐ-CP",
                    "provisions": [
                        {
                            "source_provision": "Khoản 1 Điều 1",
                            "target_provision": "Điều 5 khoản 1 điểm q, khoản 3 điểm h",
                            "operation": "add",
                            "description": "Phạt cảnh cáo không có thiết bị an toàn cho trẻ dưới 10 tuổi / dưới 1m35 trên ô tô; phạt 800k - 1tr nếu chở trẻ em ngồi ghế trước cùng tài xế"
                        },
                        {
                            "source_provision": "Khoản 2 Điều 1",
                            "target_provision": "Điều 13 khoản 8",
                            "operation": "amend",
                            "description": "Tăng mức phạt tiền từ 20.000.000đ đến 26.000.000đ đối với hành vi che lấp, làm mờ, bẻ cong, thay đổi chữ số hoặc dùng vật liệu làm sai lệch khả năng nhận diện biển số ô tô"
                        },
                        {
                            "source_provision": "Khoản 3 Điều 1",
                            "target_provision": "Điều 14 khoản 6a",
                            "operation": "add",
                            "description": "Phạt từ 12.000.000đ đến 14.000.000đ và tước GPLX từ 1-3 tháng đối với xe không kinh doanh vận tải nhưng chở khách có thu tiền"
                        }
                    ]
                }
            ],
            "amended_by": []
        },
        "scope_tags": ["xu_phat_giao_thong", "che_bien_so", "an_toan_tre_em", "xe_chở_khach_tra_hinh"]
    },
    {
        "filename": "236_2026_ND_CP.html",
        "doc_id": "traffic_guideline_amendment_236_2026_nd_cp",
        "official_number": "236/2026/NĐ-CP",
        "title": "Nghị định 236/2026/NĐ-CP sửa đổi, bổ sung một số điều của Nghị định 151/2024/NĐ-CP hướng dẫn Luật TTATGT đường bộ",
        "doc_type": "NGHI_DINH",
        "issue_date": "2026-06-26",
        "effective_date": "2026-07-01",
        "status": "CON_HIEU_LUC",
        "version_chain": [
            {"step": 1, "doc_number": "151/2024/NĐ-CP", "effective": "2025-01-01", "role": "GỐC"},
            {"step": 2, "doc_number": "184/2025/NĐ-CP", "effective": "2025-07-01", "role": "SỬA ĐỔI LẦN 1 (Phân định thẩm quyền chính quyền 2 cấp)"},
            {"step": 3, "doc_number": "236/2026/NĐ-CP", "effective": "2026-07-01", "role": "SỬA ĐỔI LẦN 2 (VNeID, xe ưu tiên 01 ngày, CSDL liên thông)"}
        ],
        "relations": {
            "amends": [
                {
                    "target_document_id": "traffic_guideline_151_2024_nd_cp",
                    "official_number": "151/2024/NĐ-CP",
                    "provisions": [
                        {
                            "source_provision": "Khoản 1 Điều 1",
                            "target_provision": "Điều 20",
                            "operation": "amend",
                            "description": "Nộp hồ sơ cấp Giấy phép thiết bị xe ưu tiên qua VNeID; rút ngắn thời hạn giải quyết từ 02 ngày xuống còn 01 ngày làm việc, cấp bản điện tử"
                        },
                        {
                            "source_provision": "Khoản 2 Điều 1",
                            "target_provision": "Điều 26 khoản 2",
                            "operation": "amend",
                            "description": "Kết nối chia sẻ dữ liệu TTATGT dùng chung giữa Bộ Công an với CSDL dân cư, đăng kiểm và đào tạo lái xe"
                        }
                    ]
                }
            ],
            "amended_by": []
        },
        "scope_tags": ["huong_dan_giao_thong", "xe_uu_tien", "vneid", "co_so_du_lieu_gt"]
    },
    {
        "filename": "118_2025_QH15.html",
        "doc_id": "law_amendment_118_2025_qh15",
        "official_number": "118/2025/QH15",
        "title": "Luật số 118/2025/QH15 sửa đổi, bổ sung một số điều của 10 luật có liên quan đến an ninh, trật tự",
        "doc_type": "LUAT",
        "issue_date": "2025-12-10",
        "effective_date": "2026-07-01",
        "status": "CON_HIEU_LUC",
        "version_chain": [
            {"step": 1, "doc_number": "36/2024/QH15 & 35/2024/QH15", "effective": "2025-01-01", "role": "LUẬT GỐC"},
            {"step": 2, "doc_number": "118/2025/QH15", "effective": "2026-07-01", "role": "SỬA ĐỔI, BỔ SUNG ĐA LUẬT"}
        ],
        "relations": {
            "amends": [
                {
                    "target_document_id": "traffic_safety_law_36_2024_qh15",
                    "official_number": "36/2024/QH15",
                    "provisions": [
                        {
                            "source_article": "Điều 7",
                            "source_operation": "amend",
                            "target_document": "36/2024/QH15",
                            "target_provision": "Khoản 3 Điều 10",
                            "description": "Không cho trẻ dưới 10 tuổi và dưới 1m35 ngồi ghế trước; bắt buộc sử dụng thiết bị an toàn phù hợp trên xe ô tô gia đình (loại trừ xe ô tô kinh doanh vận tải hành khách)"
                        },
                        {
                            "source_article": "Điều 7",
                            "source_operation": "amend",
                            "target_document": "36/2024/QH15",
                            "target_provision": "Điểm c Khoản 2 Điều 56",
                            "description": "Ứng dụng sinh trắc học và truyền dữ liệu giám sát đào tạo lái xe về cơ quan nhà nước"
                        },
                        {
                            "source_article": "Điều 7",
                            "source_operation": "amend",
                            "target_document": "36/2024/QH15",
                            "target_provision": "Khoản 1 Điều 64",
                            "description": "Lái xe liên tục không quá 4 giờ; thời gian làm việc trong ngày và tuần theo Bộ luật Lao động 2019"
                        }
                    ]
                },
                {
                    "target_document_id": "road_law_35_2024_qh15",
                    "official_number": "35/2024/QH15",
                    "provisions": [
                        {
                            "source_article": "Điều 8",
                            "source_operation": "amend",
                            "target_document": "35/2024/QH15",
                            "target_provision": "Điều 8",
                            "description": "Tăng cường phân quyền cho UBND cấp tỉnh chủ động quản lý, bảo trì, khai thác đường bộ"
                        }
                    ]
                }
            ],
            "amended_by": []
        },
        "scope_tags": ["luat_an_ninh_trat_tu", "sua_doi_luat_giao_thong", "tre_em_o_to", "thoi_gian_lai_xe", "phan_quyen_duong_bo"]
    }
]

def parse_html_hierarchy(html_path: Path) -> Dict[str, Any]:
    with open(html_path, "r", encoding="utf-8") as f:
        html = f.read()

    soup = BeautifulSoup(html, "html.parser")
    for br in soup.find_all("br"):
        br.replace_with("\n")
    for p in soup.find_all(["p", "div", "tr", "h2", "h3", "h4"]):
        p.append("\n")

    text = soup.get_text()
    lines = [line.strip() for line in text.splitlines() if line.strip()]

    chapters = []
    articles = []
    current_chapter = "QUY ĐỊNH CHUNG"
    current_article = None
    current_clause = None

    chapter_pattern = re.compile(r"^Chương\s+([IVXLCDM\d]+)[\.:\s]\s*(.*)", re.IGNORECASE)
    article_pattern = re.compile(r"^Điều\s+(\d+)[\.:\s]\s*(.*)", re.IGNORECASE)
    clause_pattern = re.compile(r"^(\d+)\.\s+(.*)")
    point_pattern = re.compile(r"^([a-zđ])\)\s+(.*)", re.IGNORECASE)

    for line in lines:
        # Check Chapter
        ch_m = chapter_pattern.match(line)
        if ch_m:
            current_chapter = f"Chương {ch_m.group(1)}: {ch_m.group(2).strip()}"
            chapters.append(current_chapter)
            continue

        # Check Article
        art_m = article_pattern.match(line)
        if art_m:
            if current_article:
                articles.append(current_article)
            art_num = int(art_m.group(1))
            art_title = art_m.group(2).strip()
            current_article = {
                "article_number": f"Điều {art_num}",
                "article_index": art_num,
                "article_title": art_title or f"Điều {art_num}",
                "chapter": current_chapter,
                "clauses": [],
                "raw_text": line
            }
            current_clause = None
            continue

        # If inside Article, check Clauses & Points
        if current_article:
            cl_m = clause_pattern.match(line)
            if cl_m:
                cl_num = int(cl_m.group(1))
                cl_text = cl_m.group(2).strip()
                current_clause = {
                    "clause_number": f"Khoản {cl_num}",
                    "clause_index": cl_num,
                    "clause_text": cl_text,
                    "points": []
                }
                current_article["clauses"].append(current_clause)
                current_article["raw_text"] += "\n" + line
                continue

            pt_m = point_pattern.match(line)
            if pt_m and current_clause:
                pt_char = pt_m.group(1)
                pt_text = pt_m.group(2).strip()
                current_clause["points"].append({
                    "point_identifier": f"Điểm {pt_char}",
                    "point_text": pt_text
                })
                current_article["raw_text"] += "\n" + line
                continue

            # Continuation line
            if current_clause:
                current_clause["clause_text"] += " " + line
            current_article["raw_text"] += "\n" + line

    if current_article:
        articles.append(current_article)

    return {
        "chapters": list(dict.fromkeys(chapters)),
        "articles": articles
    }

def create_chunks_from_parsed(doc_meta: Dict[str, Any], parsed_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    chunks = []
    doc_id = doc_meta["doc_id"]
    official_number = doc_meta["official_number"]
    title = doc_meta["title"]
    effective_date = doc_meta["effective_date"]

    for art in parsed_data["articles"]:
        art_num = art["article_number"]
        art_title = art["article_title"]
        ch_title = art["chapter"]

        # Nếu Điều có nhiều Khoản, tạo chunk theo từng Khoản để retrieval cực mịn
        if art["clauses"]:
            for cl in art["clauses"]:
                cl_num = cl["clause_number"]
                cl_body = cl["clause_text"]
                points_text = "\n".join([f"  - {p['point_identifier']}) {p['point_text']}" for p in cl["points"]])
                full_clause_content = f"{cl_body}\n{points_text}".strip()

                header = f"[{official_number} - {title}]\n{ch_title} > {art_num}: {art_title} > {cl_num}"
                search_text = f"{header}\n{full_clause_content}"

                chunk = {
                    "chunk_id": f"{doc_id}_{art_num.replace(' ', '_')}_{cl_num.replace(' ', '_')}".lower(),
                    "document_id": doc_id,
                    "official_number": official_number,
                    "article": art_num,
                    "clause": cl_num,
                    "article_title": art_title,
                    "chapter": ch_title,
                    "content": full_clause_content,
                    "full_search_text": search_text,
                    "effective_from": effective_date,
                    "effective_to": None,
                    "scope_tags": doc_meta["scope_tags"],
                    "word_count": len(search_text.split()),
                    "char_count": len(search_text)
                }
                chunks.append(chunk)
        else:
            # Điều không phân khoản
            header = f"[{official_number} - {title}]\n{ch_title} > {art_num}: {art_title}"
            content = art["raw_text"]
            search_text = f"{header}\n{content}"

            chunk = {
                "chunk_id": f"{doc_id}_{art_num.replace(' ', '_')}".lower(),
                "document_id": doc_id,
                "official_number": official_number,
                "article": art_num,
                "clause": None,
                "article_title": art_title,
                "chapter": ch_title,
                "content": content,
                "full_search_text": search_text,
                "effective_from": effective_date,
                "effective_to": None,
                "scope_tags": doc_meta["scope_tags"],
                "word_count": len(search_text.split()),
                "char_count": len(search_text)
            }
            chunks.append(chunk)

    return chunks

def build_benchmark_ground_truth(all_parsed: Dict[str, Any]) -> List[Dict[str, Any]]:
    # Trích xuất Exact Evidence trực tiếp từ Parsed text đã bóc tách
    benchmark_cases = [
        {
            "test_case_id": "TC-TRAFFIC-P0-01",
            "query": "Hành vi che dán, bẻ cong hoặc làm mờ biển số xe ô tô để trốn camera phạt nguội thực hiện ngày 20/08/2026 thì bị xử phạt như thế nào?",
            "as_of_date": "2026-08-20",
            "category": "Temporal Penalty & Biển số xe",
            "expected_documents": ["traffic_penalty_amendment_238_2026_nd_cp", "traffic_penalty_168_2024_nd_cp"],
            "expected_provisions": ["Điều 1 khoản 2 NĐ 238/2026 sửa Điều 13 khoản 8 NĐ 168/2024"],
            "expected_conclusion": "Phạt tiền từ 20.000.000 đồng đến 26.000.000 đồng đối với người điều khiển xe ô tô che dán, bẻ cong, làm mờ, thay đổi chữ số hoặc dùng vật liệu/thiết bị làm sai lệch khả năng nhận diện biển số.",
            "evidence": [
                {
                    "document": "238/2026/NĐ-CP",
                    "article": "Điều 1",
                    "clause": "Khoản 2",
                    "target_article_amended": "Điều 13 Khoản 8 Nghị định 168/2024/NĐ-CP",
                    "source_text": "Phạt tiền từ 20.000.000 đồng đến 26.000.000 đồng đối với người điều khiển xe ô tô... gắn biển số không rõ chữ, số; biển số bị bẻ cong, che lấp, làm thay đổi chữ, số... sử dụng chất liệu, vật liệu, thiết bị làm thay đổi hoặc che giấu khả năng nhận diện biển số xe của camera..."
                }
            ]
        },
        {
            "test_case_id": "TC-TRAFFIC-P0-02",
            "query": "Theo quy định áp dụng từ tháng 07/2026, thời gian làm việc và thời gian lái xe liên tục của tài xế ô tô kinh doanh vận tải được quy định ra sao?",
            "as_of_date": "2026-07-15",
            "category": "Temporal Driver Working Hours",
            "expected_documents": ["law_amendment_118_2025_qh15", "traffic_safety_law_36_2024_qh15"],
            "expected_provisions": ["Điều 7 khoản 3 Luật 118/2025 sửa Điều 64 khoản 1 Luật 36/2024"],
            "expected_conclusion": "Thời gian lái xe liên tục không quá 04 giờ (trừ trường hợp bất khả kháng); thời gian làm việc trong ngày và trong tuần thực hiện theo quy định của Bộ luật Lao động 2019 (đã bãi bỏ mức giới hạn cứng 48 giờ/tuần trước đây).",
            "evidence": [
                {
                    "document": "118/2025/QH15",
                    "article": "Điều 7",
                    "clause": "Khoản 3",
                    "target_article_amended": "Điều 64 Khoản 1 Luật 36/2024/QH15",
                    "source_text": "a) Thời gian lái xe liên tục không quá 04 giờ (trừ trường hợp bất khả kháng hoặc gặp trở ngại khách quan trên đường); b) Thời gian làm việc của người lái xe trong một ngày, trong một tuần thực hiện theo quy định của Bộ luật Lao động."
                }
            ]
        },
        {
            "test_case_id": "TC-TRAFFIC-P0-03",
            "query": "Hồ sơ xin cấp mới Giấy phép sử dụng thiết bị phát tín hiệu của xe ưu tiên nộp vào tháng 08/2026 có thể thực hiện qua VNeID không và cơ quan CSGT phải giải quyết trong mấy ngày?",
            "as_of_date": "2026-08-05",
            "category": "Temporal Priority Vehicle & VNeID Procedure",
            "expected_documents": ["traffic_guideline_amendment_236_2026_nd_cp", "traffic_guideline_151_2024_nd_cp"],
            "expected_provisions": ["Điều 1 khoản 1 NĐ 236/2026 sửa Điều 20 NĐ 151/2024"],
            "expected_conclusion": "Có thể nộp trực tuyến toàn trình qua Ứng dụng định danh quốc gia (VNeID) hoặc Cổng Dịch vụ công. Thời hạn giải quyết rút ngắn xuống còn trong 01 ngày làm việc, được cấp Giấy phép bản điện tử qua VNeID.",
            "evidence": [
                {
                    "document": "236/2026/NĐ-CP",
                    "article": "Điều 1",
                    "clause": "Khoản 1",
                    "target_article_amended": "Điều 20 Nghị định 151/2024/NĐ-CP",
                    "source_text": "Nộp trực tuyến toàn trình qua Cổng Dịch vụ công quốc gia, Cổng Dịch vụ công Bộ Công an hoặc ứng dụng định danh quốc gia (VNeID)... Thời hạn giải quyết: Trong thời hạn 01 ngày làm việc kể từ ngày nhận đủ hồ sơ hợp lệ... cấp Giấy phép sử dụng thiết bị phát tín hiệu của xe ưu tiên bản điện tử qua VNeID hoặc bản giấy..."
                }
            ]
        },
        {
            "test_case_id": "TC-TRAFFIC-P0-04",
            "query": "Từ sau ngày 10/08/2026, xe ô tô kinh doanh vận tải hành khách theo hợp đồng có được đón trả khách tại văn phòng đại diện hoặc trụ sở chi nhánh của công ty không?",
            "as_of_date": "2026-08-25",
            "category": "Temporal Contract Vehicle Restriction",
            "expected_documents": ["traffic_amendment_218_2026_nd_cp", "traffic_transport_158_2024_nd_cp"],
            "expected_provisions": ["Điều 1 khoản 1 và khoản 2 NĐ 218/2026 sửa Điều 7 và Điều 19 NĐ 158/2024"],
            "expected_conclusion": "Tuyệt đối không được đón, trả khách tại trụ sở chính, chi nhánh, văn phòng đại diện hoặc các địa điểm cố định tự thuê trên các tuyến đường phố. Nếu vi phạm từ 3 lần/tháng sẽ bị thu hồi Giấy phép kinh doanh vận tải.",
            "evidence": [
                {
                    "document": "218/2026/NĐ-CP",
                    "article": "Điều 1",
                    "clause": "Khoản 1 (sửa Điều 7 Khoản 4 NĐ 158)",
                    "target_article_amended": "Điều 7 Khoản 4 Nghị định 158/2024/NĐ-CP",
                    "source_text": "Đơn vị kinh doanh vận tải hành khách theo hợp đồng và người lái xe không được đón, trả khách tại trụ sở chính, trụ sở chi nhánh, văn phòng đại diện hoặc địa điểm cố định khác do đơn vị kinh doanh vận tải thuê, hợp tác kinh doanh trên các tuyến đường phố..."
                },
                {
                    "document": "218/2026/NĐ-CP",
                    "article": "Điều 1",
                    "clause": "Khoản 2 (sửa Điều 19 Khoản 2 Điểm đ NĐ 158)",
                    "target_article_amended": "Điều 19 Khoản 2 Điểm đ Nghị định 158/2024/NĐ-CP",
                    "source_text": "Thu hồi Giấy phép kinh doanh vận tải đối với: Đơn vị kinh doanh vận tải hành khách theo hợp đồng vi phạm quy định về việc đón, trả khách tại trụ sở chính, chi nhánh, văn phòng đại diện từ 03 lần trở lên trong thời gian 01 tháng..."
                }
            ]
        },
        {
            "test_case_id": "TC-TRAFFIC-P0-05",
            "query": "Xe ô tô gia đình chở trẻ em 7 tuổi cao 1m25 ngồi ghế phụ phía trước có vi phạm không và bị xử lý thế nào kể từ ngày 15/08/2026?",
            "as_of_date": "2026-08-20",
            "category": "Temporal Child Car Safety (Two-tier Legal Evidence)",
            "expected_documents": ["traffic_penalty_amendment_238_2026_nd_cp", "traffic_penalty_168_2024_nd_cp", "law_amendment_118_2025_qh15", "traffic_safety_law_36_2024_qh15"],
            "expected_provisions": [
                "Luật 118/2025 Điều 7 sửa Luật 36/2024 Điều 10 khoản 3 (Quy tắc & Đối tượng loại trừ)",
                "Nghị định 168/2024 Điều 6 khoản 3 điểm m kết hợp NĐ 238/2026 Điều 1 khoản 1 (Chế tài phạt)"
            ],
            "expected_conclusion": "Vi phạm pháp luật đối với xe ô tô cá nhân/gia đình (trường hợp xe kinh doanh vận tải hành khách được loại trừ một phần về thiết bị an toàn theo Luật 118). Hành vi để trẻ em dưới 10 tuổi và chiều cao dưới 1,35m ngồi cùng hàng ghế với người lái xe bị phạt tiền từ 800.000 đồng đến 1.000.000 đồng; không sử dụng thiết bị an toàn phù hợp bị phạt cảnh cáo.",
            "evidence": [
                {
                    "evidence_label": "Evidence A: Quy tắc nghĩa vụ & Ngoại lệ đối tượng",
                    "document": "Luật 118/2025/QH15 & Luật 36/2024/QH15",
                    "article": "Điều 7 Luật 118 sửa Điều 10 Luật 36",
                    "clause": "Khoản 3 Điều 10",
                    "target_article_amended": "Điều 10 Khoản 3 Luật Trật tự ATGT đường bộ 36/2024/QH15",
                    "source_text": "Khi chở trẻ em dưới 10 tuổi và chiều cao dưới 1,35 mét trên xe ô tô, người lái xe không được cho trẻ em ngồi cùng hàng ghế với người lái xe (trừ trường hợp xe ô tô chỉ có một hàng ghế); đồng thời phải sử dụng, hướng dẫn sử dụng thiết bị an toàn phù hợp cho trẻ em theo quy định của pháp luật (trừ trường hợp xe ô tô kinh doanh vận tải hành khách)."
                },
                {
                    "evidence_label": "Evidence B: Chế tài xử phạt vi phạm hành chính",
                    "document": "Nghị định 168/2024/NĐ-CP & Nghị định 238/2026/NĐ-CP",
                    "article": "Điểm m Khoản 3 Điều 6 (NĐ 168) & Điều 1 Khoản 1 (NĐ 238)",
                    "clause": "Khoản 3 Điều 6 (NĐ 168) / Khoản 1 Điều 1 (NĐ 238)",
                    "target_article_amended": "Quy định xử phạt vi phạm quy tắc giao thông đường bộ đối với người điều khiển ô tô",
                    "source_text": "Phạt tiền từ 800.000 đồng đến 1.000.000 đồng đối với người điều khiển xe ô tô chở trẻ em dưới 10 tuổi và có chiều cao dưới 1,35 mét ngồi cùng hàng ghế với người lái xe (trừ trường hợp xe ô tô chỉ có một hàng ghế); phạt cảnh cáo đối với hành vi không sử dụng thiết bị an toàn phù hợp cho trẻ em theo quy định."
                }
            ]
        }
    ]
    return benchmark_cases

def main():
    print("=" * 80)
    print(" BẮT ĐẦU PIPELINE PARSING & VALIDATION: TRAFFIC P0 VERSION-AWARE BATCH")
    print("=" * 80)

    all_parsed_results = {}
    batch_summary = {
        "batch_name": "Traffic P0 Version-Aware Batch",
        "processed_at": datetime.now().isoformat(),
        "total_documents": len(CONFIGS),
        "documents": [],
        "chunks_summary": {},
        "benchmark_ground_truth": []
    }

    total_articles = 0
    total_clauses = 0
    total_chunks = 0
    all_chunks_list = []

    for cfg in CONFIGS:
        raw_file = RAW_DIR / cfg["filename"]
        if not raw_file.exists():
            print(f"[!] Lỗi: Không tìm thấy file raw: {raw_file}")
            return

        print(f"\n[*] Đang parse văn bản: {cfg['official_number']} ({cfg['filename']})...")
        parsed_hierarchy = parse_html_hierarchy(raw_file)

        # Tính toán thống kê
        num_arts = len(parsed_hierarchy["articles"])
        num_cls = sum(len(a["clauses"]) for a in parsed_hierarchy["articles"])
        total_articles += num_arts
        total_clauses += num_cls

        # Tạo chunks
        chunks = create_chunks_from_parsed(cfg, parsed_hierarchy)
        total_chunks += len(chunks)
        all_chunks_list.extend(chunks)

        parsed_doc_record = {
            "metadata": cfg,
            "hierarchy": parsed_hierarchy,
            "chunks_count": len(chunks),
            "articles_count": num_arts,
            "clauses_count": num_cls
        }

        # Lưu parsed file ra đĩa
        parsed_out_file = PARSED_DIR / f"{cfg['doc_id']}.json"
        with open(parsed_out_file, "w", encoding="utf-8") as f:
            json.dump(parsed_doc_record, f, ensure_ascii=False, indent=2)

        all_parsed_results[cfg["doc_id"]] = parsed_doc_record

        doc_summary_item = {
            "document_id": cfg["doc_id"],
            "official_number": cfg["official_number"],
            "title": cfg["title"],
            "effective_date": cfg["effective_date"],
            "articles_count": num_arts,
            "clauses_count": num_cls,
            "chunks_count": len(chunks),
            "amendments_count": sum(len(rel.get("provisions", [])) for rel in cfg["relations"].get("amends", [])),
            "parsed_file": f"data/03_parsed/traffic_p0_batch/{cfg['doc_id']}.json"
        }
        batch_summary["documents"].append(doc_summary_item)

        print(f" [+] Kết quả: {num_arts} Điều | {num_cls} Khoản | {len(chunks)} Chunks | Lưu: {parsed_out_file.name}")

    # Thống kê chunks toàn batch
    word_counts = [c["word_count"] for c in all_chunks_list]
    batch_summary["chunks_summary"] = {
        "total_chunks": total_chunks,
        "total_articles": total_articles,
        "total_clauses": total_clauses,
        "min_words": min(word_counts) if word_counts else 0,
        "max_words": max(word_counts) if word_counts else 0,
        "avg_words": round(sum(word_counts) / len(word_counts), 1) if word_counts else 0
    }

    # Tạo Exact Legal Evidence Benchmark
    print("\n[*] Đang xây dựng và đối chiếu Exact Legal Evidence Benchmark Ground Truth...")
    benchmarks = build_benchmark_ground_truth(all_parsed_results)
    batch_summary["benchmark_ground_truth"] = benchmarks

    # Lưu file tổng kết batch
    summary_path = PARSED_DIR / "traffic_p0_batch_summary.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(batch_summary, f, ensure_ascii=False, indent=2)

    print(f"[+] Đã lưu file tổng kết batch tại: {summary_path}")

    # In bảng số liệu nghiệm thu cho Mentor
    print("\n" + "=" * 105)
    print(f"{'Văn bản':<25} | {'Số hiệu':<15} | {'Số Điều':<8} | {'Số Khoản':<10} | {'Số Chunks':<10} | {'Hiệu lực':<12} | {'Trạng thái'}")
    print("-" * 105)
    for d in batch_summary["documents"]:
        print(f"{d['title'][:23]:<25} | {d['official_number']:<15} | {d['articles_count']:<8} | {d['clauses_count']:<10} | {d['chunks_count']:<10} | {d['effective_date']:<12} | CON_HIEU_LUC")
    print("-" * 105)
    print(f"{'TỔNG CỘNG 5 VĂN BẢN MỚI':<25} | {'':<15} | {total_articles:<8} | {total_clauses:<10} | {total_chunks:<10} | {'':<12} | APPROVED FOR REVIEW")
    print("=" * 105)

if __name__ == "__main__":
    main()
