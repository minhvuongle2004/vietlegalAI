import sys
import json
import time
import requests
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

API_URL = "http://127.0.0.1:8000/api/v1/chat/completions"

REAL_ESTATE_TEST_CASES = [
    {
        "id": "TC-49",
        "category": "real_estate_law",
        "title": "Mức đặt cọc tối đa khi mua bán nhà ở hình thành trong tương lai (Điều 23)",
        "query": "Chủ đầu tư dự án bất động sản được thu tiền đặt cọc tối đa bao nhiêu phần trăm giá bán nhà ở hình thành trong tương lai và khi nào mới được thu đặt cọc theo Luật Kinh doanh bất động sản 2023?",
        "expected_articles": [
            {"doc_keyword": "re_business", "article_number": 23}
        ],
        "expected_keywords": [
            "5%|năm phần trăm",
            "đặt cọc",
            "giá bán|giá cho thuê",
            "đủ điều kiện"
        ],
        "forbidden_keywords": [
            "không giới hạn",
            "30% đặt cọc",
            "50% đặt cọc"
        ]
    },
    {
        "id": "TC-50",
        "category": "real_estate_law",
        "title": "Điều kiện bán nhà ở hình thành trong tương lai và nghiệm thu móng (Điều 24)",
        "query": "Theo Luật Kinh doanh bất động sản 2023, để được đưa nhà ở hình thành trong tương lai vào kinh doanh, chủ đầu tư dự án chung cư phải hoàn thành những điều kiện gì về giấy tờ pháp lý và biên bản nghiệm thu công trình?",
        "expected_articles": [
            {"doc_keyword": "re_business", "article_number": 24}
        ],
        "expected_keywords": [
            "quyền sử dụng đất",
            "giấy phép xây dựng",
            "nghiệm thu|phần móng",
            "bảo lãnh"
        ],
        "forbidden_keywords": []
    },
    {
        "id": "TC-51",
        "category": "real_estate_law",
        "title": "Điều kiện thực hiện các quyền chuyển nhượng quyền sử dụng đất (Điều 45)",
        "query": "Người sử dụng đất muốn chuyển nhượng quyền sử dụng đất cho người khác thì cần phải đáp ứng các điều kiện chung nào theo quy định tại Điều 45 Luật Đất đai 2024?",
        "expected_articles": [
            {"doc_keyword": "land", "article_number": 45}
        ],
        "expected_keywords": [
            "Giấy chứng nhận",
            "không có tranh chấp|được giải quyết",
            "không bị kê biên",
            "thời hạn sử dụng đất"
        ],
        "forbidden_keywords": []
    },
    {
        "id": "TC-52",
        "category": "real_estate_law",
        "title": "Bỏ khung giá đất và nguyên tắc ban hành bảng giá đất hàng năm (Điều 158, 159)",
        "query": "Luật Đất đai 2024 quy định như thế nào về việc xây dựng, ban hành bảng giá đất và nguyên tắc định giá đất? Bảng giá đất được công bố và áp dụng định kỳ như thế nào?",
        "expected_articles": [
            {"doc_keyword": "land", "article_number": [158, 159]}
        ],
        "expected_keywords": [
            "bảng giá đất",
            "nguyên tắc thị trường",
            "Ủy ban nhân dân cấp tỉnh|UBND",
            "hằng năm|hàng năm|01 tháng 01"
        ],
        "forbidden_keywords": [
            "khung giá đất của Chính phủ"
        ]
    },
    {
        "id": "TC-53",
        "category": "real_estate_law",
        "title": "Đối tượng và điều kiện hưởng chính sách nhà ở xã hội (Điều 76, 78)",
        "query": "Những nhóm đối tượng nào được hưởng chính sách hỗ trợ về nhà ở xã hội và cần đáp ứng các điều kiện gì về nhà ở và thu nhập theo quy định của Luật Nhà ở 2023?",
        "expected_articles": [
            {"doc_keyword": "housing", "article_number": [76, 78]}
        ],
        "expected_keywords": [
            "nhà ở xã hội",
            "chưa có nhà ở|thuộc sở hữu",
            "thu nhập",
            "Điều 76|Điều 78"
        ],
        "forbidden_keywords": []
    },
    {
        "id": "TC-54",
        "category": "real_estate_law",
        "title": "Thời hạn tối thiểu 5 năm không được bán lại nhà ở xã hội (Điều 89)",
        "query": "Người mua nhà ở xã hội theo Luật Nhà ở 2023 có được phép bán lại nhà ở đó cho người khác ngay không? Thời hạn tối thiểu để được phép bán lại nhà ở xã hội theo cơ chế thị trường là bao lâu?",
        "expected_articles": [
            {"doc_keyword": "housing", "article_number": 89}
        ],
        "expected_keywords": [
            "05 năm|5 năm",
            "thanh toán hết",
            "chủ đầu tư",
            "tiền sử dụng đất"
        ],
        "forbidden_keywords": [
            "bán tự do ngay lập tức",
            "không cần thời hạn"
        ]
    },
    {
        "id": "TC-55",
        "category": "real_estate_law",
        "title": "Cross-Document: Đặt cọc mua bán căn hộ tương lai (Kinh doanh BĐS Đ23 vs BLDS Đ328)",
        "query": "Chủ đầu tư dự án bất động sản yêu cầu khách hàng đặt cọc 20% giá trị hợp đồng để giữ chỗ mua căn hộ chung cư khi chưa hoàn thành phần móng, với lý do Điều 328 Bộ luật Dân sự 2015 cho phép tự do thỏa thuận đặt cọc. Việc làm này của chủ đầu tư có đúng luật không theo Luật Kinh doanh bất động sản 2023 và Bộ luật Dân sự 2015?",
        "expected_articles": [
            {"doc_keyword": "re_business", "article_number": 23},
            {"doc_keyword": "blds", "article_number": 328}
        ],
        "expected_keywords": [
            "5%|không quá 5%",
            "trái pháp luật|không đúng|sai quy định|vi phạm",
            "chuyên ngành|ưu tiên",
            "đủ điều kiện|móng",
            "328"
        ],
        "forbidden_keywords": [
            "chủ đầu tư làm đúng",
            "hợp pháp vì tự do thỏa thuận 20%"
        ]
    },
    {
        "id": "TC-56",
        "category": "real_estate_law",
        "title": "Cross-Document: Chấp thuận chủ trương đầu tư và giao đất qua đấu giá/đấu thầu (Đầu tư Đ29, 32 vs Đất đai Đ125, 126)",
        "query": "Để thực hiện dự án nhà ở thương mại có sử dụng đất, thủ tục chấp thuận chủ trương đầu tư và các hình thức lựa chọn nhà đầu tư giao đất, cho thuê đất được quy định như thế nào theo Luật Đầu tư 2020 và Luật Đất đai 2024?",
        "expected_articles": [
            {"doc_keyword": "investment", "article_number": [29, 32]},
            {"doc_keyword": "land", "article_number": [125, 126]}
        ],
        "expected_keywords": [
            "chấp thuận chủ trương đầu tư",
            "đấu giá quyền sử dụng đất",
            "đấu thầu",
            "Điều 125|Điều 126",
            "Luật Đầu tư"
        ],
        "forbidden_keywords": []
    }
]


def check_retrieval(citations, expected_list):
    if not citations:
        return False, []
    
    cit_signatures = []
    for c in citations:
        doc_id = c.get("doc_id", "").lower()
        art_num = c.get("article_number")
        cit_signatures.append((doc_id, art_num))
        
    found_matches = []
    for exp in expected_list:
        kw = exp["doc_keyword"].lower()
        exp_arts = exp["article_number"]
        if isinstance(exp_arts, int):
            exp_arts = [exp_arts]
            
        matched = False
        for doc_id, art_num in cit_signatures:
            if kw in doc_id and art_num in exp_arts:
                matched = True
                break
        found_matches.append(matched)
        
    all_matched = all(found_matches)
    return all_matched, found_matches


def check_keywords(text, expected_patterns):
    import re
    matched = []
    missing = []
    t_lower = text.lower()
    for pat in expected_patterns:
        options = [p.strip().lower() for p in pat.split("|")]
        if any(re.search(re.escape(opt), t_lower) for opt in options):
            matched.append(pat)
        else:
            missing.append(pat)
    return matched, missing


def check_forbidden(text, forbidden_list):
    import re
    found = []
    t_lower = text.lower()
    for f in forbidden_list:
        if re.search(re.escape(f.lower()), t_lower):
            found.append(f)
    return found


def run_tests():
    print("=" * 80)
    print("   VIETLEGAL AI — CHẠY BENCHMARK CÔ LẬP CỤM BẤT ĐỘNG SẢN & ĐẦU TƯ (TC-49 ĐẾN TC-56)")
    print("=" * 80)
    
    results = []
    total = len(REAL_ESTATE_TEST_CASES)
    passed = 0
    retrieval_hits = 0
    
    for idx, tc in enumerate(REAL_ESTATE_TEST_CASES, 1):
        print(f"\n[{idx}/{total}] Đang kiểm thử {tc['id']}: {tc['title']}...")
        payload = {
            "query": tc["query"],
            "top_k": 5,
            "use_reranker": True,
            "as_of_date": "2026-09-01"
        }
        
        t0 = time.time()
        try:
            citations = []
            answer = ""
            resp = requests.post(API_URL, json=payload, stream=True, timeout=90)
            elapsed = time.time() - t0
            if resp.status_code != 200:
                print(f"  [-] Lỗi HTTP {resp.status_code}: {resp.text[:200]}")
                results.append({"id": tc["id"], "passed": False, "error": f"HTTP {resp.status_code}"})
                continue

            for line in resp.iter_lines():
                if line:
                    decoded = line.decode("utf-8")
                    if decoded.startswith("data: "):
                        data_str = decoded[6:]
                        try:
                            data = json.loads(data_str)
                            if "citations" in data:
                                citations = data["citations"]
                            elif "token" in data:
                                answer += data["token"]
                        except Exception:
                            pass

            elapsed = time.time() - t0

            # Check retrieval
            ret_ok, ret_details = check_retrieval(citations, tc["expected_articles"])
            if ret_ok:
                retrieval_hits += 1
                ret_status = "✅ 100%"
            else:
                ret_status = f"❌ (Chi tiết: {ret_details})"
                
            # Check keywords
            kw_matched, kw_missing = check_keywords(answer, tc["expected_keywords"])
            kw_ratio = len(kw_matched) / len(tc["expected_keywords"]) if tc["expected_keywords"] else 1.0
            
            # Check forbidden
            forb_found = check_forbidden(answer, tc.get("forbidden_keywords", []))
            
            # Overall decision
            is_pass = ret_ok and (kw_ratio >= 0.70) and (len(forb_found) == 0)
            if is_pass:
                passed += 1
                verdict = "PASSED ✅"
            else:
                verdict = "FAILED ❌"
                
            print(f"  -> Kết quả: {verdict}")
            print(f"  -> Retrieval: {ret_status} | Citations: {[(c.get('doc_id'), c.get('article_number')) for c in citations]}")
            print(f"  -> Keyword Match: {int(kw_ratio*100)}% ({len(kw_matched)}/{len(tc['expected_keywords'])}) | Thiếu: {kw_missing}")
            if forb_found:
                print(f"  -> [!] Phát hiện từ cấm: {forb_found}")
            print(f"  -> Thời gian xử lý: {elapsed:.2f}s")
            
            results.append({
                "id": tc["id"],
                "title": tc["title"],
                "passed": is_pass,
                "retrieval_ok": ret_ok,
                "kw_ratio": kw_ratio,
                "citations": citations,
                "elapsed": elapsed
            })
        except Exception as e:
            print(f"  [-] Exception: {e}")
            results.append({"id": tc["id"], "passed": False, "error": str(e)})
            
    print("\n" + "=" * 80)
    print("   TỔNG KẾT BENCHMARK CỤM BẤT ĐỘNG SẢN & ĐẦU TƯ (PHASE 3)")
    print("=" * 80)
    print(f" - Retrieval Recall: {retrieval_hits}/{total} ({retrieval_hits/total*100:.1f}%)")
    print(f" - Test Case Pass Rate: {passed}/{total} ({passed/total*100:.1f}%)")
    print("=" * 80)
    return results


if __name__ == "__main__":
    run_tests()
