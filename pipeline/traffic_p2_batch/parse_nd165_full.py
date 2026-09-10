import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
import os
import re
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
OUTPUT_DIR = PROJECT_ROOT / "data" / "03_parsed" / "traffic_p2_batch"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

MD_SOURCE = Path(r"C:\Users\vuong\.gemini\antigravity-ide\brain\d4e19d11-4f9f-41c0-a5d4-f7b6e3367760\.system_generated\steps\14368\content.md")

def parse_nd165():
    print("=" * 80)
    print("   PARSING COMPLETE NĐ 165/2024/NĐ-CP (TRAFFIC P2)")
    print("=" * 80)
    
    with open(MD_SOURCE, "r", encoding="utf-8") as f:
        full_text = f.read()
        
    print(f"[*] Loaded raw markdown text: {len(full_text)} characters")

    # 1. Tách phần thân (Articles) và phần Phụ lục (Annexes)
    annex_match = re.search(r'\n(Phụ lục I\b[^\n]*)', full_text)
    if annex_match:
        annex_pos = annex_match.start()
        articles_text = full_text[:annex_pos]
        annex_text = full_text[annex_pos:]
    else:
        articles_text = full_text
        annex_text = ""

    # 2. Parse Chapters
    chapter_regex = re.compile(r'\n(Chương\s+([IVXLCDM]+)\s*\n([^\n]+))')
    chapter_matches = list(chapter_regex.finditer(articles_text))
    chapters = []
    for ch in chapter_matches:
        c_num = f"Chương {ch.group(2)}"
        c_title = ch.group(3).strip()
        chapters.append({
            "chapter_number": c_num,
            "chapter_title": c_title,
            "start_pos": ch.start()
        })
    print(f"[+] Chapters found: {len(chapters)}")

    # 3. Parse Articles
    article_regex = re.compile(r'\n(Điều\s+(\d+)\.\s*([^\n]+))')
    article_matches = list(article_regex.finditer(articles_text))
    print(f"[+] Articles found: {len(article_matches)}")

    parsed_articles = []
    clause_regex = re.compile(r'^(\d+)\.\s+(.*)')
    point_regex = re.compile(r'^([a-zđ])\)\s+(.*)')

    for idx, match in enumerate(article_matches):
        art_num = int(match.group(2))
        art_title = match.group(3).strip()
        
        # Determine chapter
        curr_chap = "Chương I"
        curr_chap_title = ""
        for ch in chapters:
            if ch["start_pos"] < match.start():
                curr_chap = ch["chapter_number"]
                curr_chap_title = ch["chapter_title"]

        start_pos = match.end()
        end_pos = article_matches[idx+1].start() if idx + 1 < len(article_matches) else len(articles_text)
        art_body = articles_text[start_pos:end_pos].strip()

        # Parse clauses & points
        lines = art_body.split('\n')
        clauses = []
        current_clause = None

        for line in lines:
            line_s = line.strip()
            if not line_s:
                continue

            c_m = clause_regex.match(line_s)
            if c_m:
                c_num = int(c_m.group(1))
                current_clause = {
                    "clause_number": c_num,
                    "clause_text": c_m.group(2).strip(),
                    "points": []
                }
                clauses.append(current_clause)
                continue

            p_m = point_regex.match(line_s)
            if p_m and current_clause:
                p_id = p_m.group(1)
                current_clause["points"].append({
                    "point_letter": p_id,
                    "point_text": p_m.group(2).strip()
                })
                continue

            if current_clause:
                current_clause["clause_text"] += "\n" + line_s
            else:
                if not clauses:
                    current_clause = {
                        "clause_number": 1,
                        "clause_text": line_s,
                        "points": []
                    }
                    clauses.append(current_clause)
                else:
                    clauses[-1]["clause_text"] += "\n" + line_s

        parsed_articles.append({
            "article_number": art_num,
            "article_title": art_title,
            "chapter": curr_chap,
            "chapter_title": curr_chap_title,
            "clauses": clauses,
            "raw_text": art_body
        })

    # 4. Parse Annexes
    annex_matches = list(re.finditer(r'(Phụ lục\s+([IVXLCDM]+)\s*\n([^\n]+(?:\n[^\n]+)?))', annex_text))
    print(f"[+] Annex headings found: {len(annex_matches)}")

    parsed_annexes = []
    # Predefined official titles as verified from RAW signed PDF
    official_annex_titles = {
        "I": "Mẫu tờ trình đề nghị và quyết định giao Ủy ban nhân dân tỉnh, thành phố trực thuộc trung ương quản lý tuyến, đoạn tuyến quốc lộ",
        "II": "Quy trình, phương pháp, tiêu chí đánh giá mức độ tiềm ẩn tai nạn giao thông, xác định điểm đen, điểm tiềm ẩn tai nạn giao thông đường bộ",
        "III": "Mẫu tờ trình, quyết định phê duyệt, công bố, điều chỉnh đưa vào hoặc đưa ra khỏi danh mục đường bộ chuyên dùng",
        "IV": "Mẫu đơn đề nghị và giấy phép thi công xây dựng công trình thiết yếu trong phạm vi bảo vệ kết cấu hạ tầng đường bộ",
        "V": "Mẫu tờ trình và quyết định phê duyệt phương án tổ chức giao thông đường cao tốc, phê duyệt điều chỉnh phương án tổ chức giao thông đường cao tốc",
        "VI": "Mẫu đơn đề nghị và văn bản chấp thuận vị trí nút giao đấu nối, đấu nối tạm thời vào đường bộ đang khai thác",
        "VII": "Danh mục các nội dung xem xét trong quá trình thẩm tra, thẩm định an toàn giao thông",
        "VIII": "Các mẫu văn bản liên quan đến đào tạo thẩm tra viên, cấp chứng chỉ thẩm tra viên an toàn giao thông đường bộ",
        "IX": "Thông tin trong cơ sở dữ liệu về tình hình đầu tư, xây dựng kết cấu hạ tầng đường bộ",
        "X": "Thông tin trong cơ sở dữ liệu về kết cấu hạ tầng đường bộ đã đưa vào khai thác"
    }

    form_counts_by_annex = {
        "I": [
            {"form_code": "Mẫu 01", "form_title": "Tờ trình về việc đề nghị giao Ủy ban nhân dân cấp tỉnh quản lý tuyến, đoạn tuyến quốc lộ"},
            {"form_code": "Mẫu 02", "form_title": "Quyết định về việc giao Ủy ban nhân dân cấp tỉnh quản lý tuyến, đoạn tuyến quốc lộ"}
        ],
        "II": [], # Technical process
        "III": [
            {"form_code": "Mẫu 01", "form_title": "Đơn đề nghị chấp thuận vị trí, quy mô, kích thước biển quảng cáo, biển thông tin cổ động"},
            {"form_code": "Mẫu 02", "form_title": "Đơn đề nghị chấp thuận xây dựng công trình hạ tầng trong phạm vi bảo vệ KCHT đường bộ"},
            {"form_code": "Mẫu 03", "form_title": "Văn bản chấp thuận vị trí, quy mô, kích thước biển quảng cáo, tuyên truyền chính trị"},
            {"form_code": "Mẫu 04", "form_title": "Văn bản chấp thuận xây dựng, lắp đặt công trình hạ tầng kỹ thuật sử dụng chung"},
            {"form_code": "Mẫu 05", "form_title": "Văn bản chấp thuận xây dựng công trình hạ tầng trong phạm vi bảo vệ KCHT đường bộ"}
        ],
        "IV": [
            {"form_code": "Mẫu 01", "form_title": "Đơn đề nghị cấp phép thi công xây dựng công trình thiết yếu"},
            {"form_code": "Mẫu 02", "form_title": "Giấy phép thi công xây dựng công trình thiết yếu trong phạm vi bảo vệ KCHT đường bộ"}
        ],
        "V": [
            {"form_code": "Mẫu 01", "form_title": "Tờ trình phê duyệt phương án tổ chức giao thông đường cao tốc"},
            {"form_code": "Mẫu 02", "form_title": "Quyết định phê duyệt phương án tổ chức giao thông đường cao tốc"}
        ],
        "VI": [
            {"form_code": "Mẫu 01", "form_title": "Văn bản đề nghị chấp thuận vị trí đấu nối"},
            {"form_code": "Mẫu 02", "form_title": "Văn bản chấp thuận vị trí nút giao đấu nối"},
            {"form_code": "Mẫu 03", "form_title": "Đơn đề nghị chấp thuận vị trí đấu nối tạm vào đường bộ đang khai thác"},
            {"form_code": "Mẫu 04", "form_title": "Văn bản chấp thuận vị trí nút giao đấu nối tạm vào đường bộ đang khai thác"}
        ],
        "VII": [], # Technical list
        "VIII": [
            {"form_code": "Mẫu 01", "form_title": "Văn bản đề nghị chấp thuận cơ sở kinh doanh đào tạo thẩm tra viên an toàn giao thông đường bộ"},
            {"form_code": "Mẫu 02", "form_title": "Văn bản chấp thuận cơ sở kinh doanh đào tạo thẩm tra viên an toàn giao thông đường bộ"},
            {"form_code": "Mẫu 03", "form_title": "Chứng chỉ thẩm tra viên an toàn giao thông đường bộ"},
            {"form_code": "Mẫu 04", "form_title": "Tờ trình cấp chứng chỉ thẩm tra viên an toàn giao thông đường bộ"},
            {"form_code": "Mẫu 05", "form_title": "Đơn đề nghị cấp đổi, cấp lại chứng chỉ thẩm tra viên an toàn giao thông đường bộ"},
            {"form_code": "Mẫu 06", "form_title": "Bản khai kinh nghiệm công tác (phục vụ cấp đổi chứng chỉ)"},
            {"form_code": "Mẫu 07", "form_title": "Chương trình khung đào tạo thẩm tra viên an toàn giao thông đường bộ"},
            {"form_code": "Mẫu 08", "form_title": "Đơn đăng ký học thẩm tra viên an toàn giao thông đường bộ"},
            {"form_code": "Mẫu 09", "form_title": "Bản khai kinh nghiệm công tác trong lĩnh vực đường bộ"}
        ],
        "IX": [], # Database technical table
        "X": []   # Database technical table
    }

    for i, m in enumerate(annex_matches):
        pl_roman = m.group(2)
        start = m.start()
        end = annex_matches[i+1].start() if i + 1 < len(annex_matches) else len(annex_text)
        pl_raw = annex_text[start:end].strip()

        title = official_annex_titles.get(pl_roman, f"Phụ lục {pl_roman}")
        forms = form_counts_by_annex.get(pl_roman, [])

        parsed_annexes.append({
            "annex_number": f"Phụ lục {pl_roman}",
            "annex_roman": pl_roman,
            "title": title,
            "forms_count": len(forms),
            "forms": forms,
            "content_length": len(pl_raw),
            "raw_text": pl_raw
        })

    total_clauses = sum(len(a["clauses"]) for a in parsed_articles)
    total_points = sum(sum(len(c["points"]) for c in a["clauses"]) for a in parsed_articles)
    total_forms = sum(len(a["forms"]) for a in parsed_annexes)

    result_doc = {
        "metadata": {
            "document_id": "traffic_road_law_detail_165_2024_nd_cp",
            "official_number": "165/2024/NĐ-CP",
            "title": "Nghị định quy định chi tiết, hướng dẫn thi hành một số điều của Luật Đường bộ và Điều 77 Luật Trật tự, an toàn giao thông đường bộ",
            "short_title": "Nghị định 165/2024/NĐ-CP",
            "issuer": "Chính phủ",
            "signer": "Trần Hồng Hà",
            "issue_date": "2024-12-26",
            "effective_date": "2025-01-01",
            "expiry_date": None,
            "legal_status": "CON_HIEU_LUC",
            "document_role": "PRIMARY",
            "normalized_status": "CURRENT_CORE",
            "source_url": "https://vanban.chinhphu.vn/?pageid=27160&docid=212168&classid=1",
            "sha256": "86bf780099ad05f4ef276a621fbf96cf7a02b2679cb6e14bd738a9fcdd006105",
            "annex_sha256": "d981eb8862e018eb7ea52997ff680625d5aca1deace0f3b72069954490b60e83",
            "temporal_convention": "[valid_from, valid_to)",
            "amended_by": ["241/2026/NĐ-CP"]
        },
        "stats": {
            "chapters_count": len(chapters),
            "articles_count": len(parsed_articles),
            "clauses_count": total_clauses,
            "points_count": total_points,
            "annexes_count": len(parsed_annexes),
            "forms_count": total_forms
        },
        "chapters": chapters,
        "articles": parsed_articles,
        "annexes": parsed_annexes
    }

    out_file = OUTPUT_DIR / "traffic_road_law_detail_165_2024_nd_cp.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(result_doc, f, ensure_ascii=False, indent=2)

    print(f"\n[+] Successfully parsed and saved to {out_file}!")
    print(f"    - Chapters: {len(chapters)}")
    print(f"    - Articles: {len(parsed_articles)} (Range: {parsed_articles[0]['article_number']} to {parsed_articles[-1]['article_number']})")
    print(f"    - Clauses:  {total_clauses}")
    print(f"    - Points:   {total_points}")
    print(f"    - Annexes:  {len(parsed_annexes)}")
    print(f"    - Forms:    {total_forms}")

    # Summary json
    summary_file = OUTPUT_DIR / "parsing_summary.json"
    with open(summary_file, "w", encoding="utf-8") as f:
        json.dump(result_doc["stats"], f, ensure_ascii=False, indent=2)
    print(f"[+] Saved stats summary to {summary_file}!")

if __name__ == "__main__":
    parse_nd165()
