import sys
import json
import time
import requests
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

API_URL = "http://127.0.0.1:8000/api/v1/chat/completions"

TAX_TEST_CASES = [
    {
        "id": "TC-41",
        "category": "tax_law",
        "title": "Biểu thuế luỹ tiến từng phần 5 bậc và tính thuế TNCN từ tiền lương (Điều 9)",
        "query": "Một cá nhân cư trú có thu nhập tính thuế từ tiền lương, tiền công trong tháng là 25 triệu đồng. Theo Biểu thuế luỹ tiến từng phần của Luật Thuế thu nhập cá nhân 2025 (Luật số 109/2025/QH15), số thuế TNCN phải nộp trong tháng được tính như thế nào và là bao nhiêu tiền?",
        "expected_articles": [
            {"doc_keyword": "tncn", "article_number": [9, 8]}
        ],
        "expected_keywords": [
            "luỹ tiến|lũy tiến",
            "bậc 1",
            "5%",
            "10%",
            "2|2 triệu|2.000.000"
        ],
        "forbidden_keywords": [
            "bậc 7",
            "80 triệu"
        ]
    },
    {
        "id": "TC-42",
        "category": "tax_law",
        "title": "Mức giảm trừ gia cảnh cho bản thân và người phụ thuộc (Điều 10)",
        "query": "Mức giảm trừ gia cảnh cho bản thân người nộp thuế và cho mỗi người phụ thuộc được quy định là bao nhiêu triệu đồng/tháng theo Điều 10 Luật Thuế thu nhập cá nhân 2025 (Luật số 109/2025/QH15)? Nguyên tắc tính giảm trừ đối với người phụ thuộc như thế nào?",
        "expected_articles": [
            {"doc_keyword": "tncn", "article_number": 10}
        ],
        "expected_keywords": [
            "15,5 triệu",
            "6,2 triệu",
            "người nộp thuế",
            "người phụ thuộc",
            "một lần"
        ],
        "forbidden_keywords": [
            "11 triệu đồng/tháng",
            "4,4 triệu đồng/tháng"
        ]
    },
    {
        "id": "TC-43",
        "category": "tax_law",
        "title": "Mức thuế suất thuế TNDN phổ thông 20% và mức ưu đãi theo doanh thu (Điều 10)",
        "query": "Theo Luật Thuế thu nhập doanh nghiệp 2025 (Luật số 67/2025/QH15), mức thuế suất thuế thu nhập doanh nghiệp phổ thông là bao nhiêu? Doanh nghiệp có doanh thu năm dưới 3 tỷ đồng và từ trên 3 đến 50 tỷ đồng được áp dụng các mức thuế suất ưu đãi nào?",
        "expected_articles": [
            {"doc_keyword": "tndn", "article_number": 10}
        ],
        "expected_keywords": [
            "20%",
            "15%",
            "17%",
            "3 tỷ",
            "50 tỷ"
        ],
        "forbidden_keywords": [
            "22%",
            "25% là phổ thông"
        ]
    },
    {
        "id": "TC-44",
        "category": "tax_law",
        "title": "Điều kiện các khoản chi được trừ khi tính thuế TNDN (Điều 9)",
        "query": "Doanh nghiệp được trừ các khoản chi khi xác định thu nhập chịu thuế TNDN nếu đáp ứng các điều kiện gì theo Điều 9 Luật Thuế thu nhập doanh nghiệp 2025? Khoản chi mua hàng hóa từng lần có giá trị từ 20 triệu đồng trở lên có bắt buộc phải có chứng từ thanh toán không dùng tiền mặt không?",
        "expected_articles": [
            {"doc_keyword": "tndn", "article_number": 9}
        ],
        "expected_keywords": [
            "sản xuất, kinh doanh",
            "hóa đơn",
            "chứng từ",
            "20 triệu",
            "không dùng tiền mặt"
        ],
        "forbidden_keywords": [
            "tiền mặt không giới hạn"
        ]
    },
    {
        "id": "TC-45",
        "category": "tax_law",
        "title": "Thời hạn nộp thuế và nộp hồ sơ khai thuế theo Luật Quản lý thuế 2025 (Điều 14)",
        "query": "Theo Điều 14 Luật Quản lý thuế 2025 (Luật số 108/2025/QH15), trong trường hợp người nộp thuế tự tính thuế thì thời hạn nộp thuế chậm nhất được xác định là ngày nào so với thời hạn nộp hồ sơ khai thuế?",
        "expected_articles": [
            {"doc_keyword": "qlt", "article_number": [14, 12]}
        ],
        "expected_keywords": [
            "ngày cuối cùng",
            "thời hạn nộp",
            "hồ sơ khai thuế",
            "tự tính thuế"
        ],
        "forbidden_keywords": [
            "sau 30 ngày kể từ ngày hết hạn khai"
        ]
    },
    {
        "id": "TC-46",
        "category": "tax_law",
        "title": "Mức tính tiền chậm nộp tiền thuế 0,03%/ngày (Điều 16)",
        "query": "Mức tính tiền chậm nộp tiền thuế được xác định là bao nhiêu phần trăm một ngày theo khoản 2 Điều 16 Luật Quản lý thuế 2025 (Luật số 108/2025/QH15)? Nếu một doanh nghiệp chậm nộp 100 triệu đồng tiền thuế trong thời gian 30 ngày thì số tiền chậm nộp phải trả là bao nhiêu?",
        "expected_articles": [
            {"doc_keyword": "qlt", "article_number": 16}
        ],
        "expected_keywords": [
            "0,03%",
            "chậm nộp",
            "tiền chậm nộp",
            "900.000",
            "ngày"
        ],
        "forbidden_keywords": [
            "0,05%/ngày",
            "0,07%/ngày"
        ]
    },
    {
        "id": "TC-47",
        "category": "tax_law",
        "title": "Cross-Document: Nghĩa vụ nộp thuế TNDN và Chế tài tính tiền chậm nộp thuế",
        "query": "Doanh nghiệp kê khai phát sinh 50 triệu đồng thuế TNDN phải nộp nhưng quá hạn 10 ngày vẫn chưa nộp vào ngân sách nhà nước. Căn cứ Luật Thuế thu nhập doanh nghiệp 2025 và Luật Quản lý thuế 2025, doanh nghiệp có trách nhiệm nộp số thuế TNDN và tiền chậm nộp được tính như thế nào?",
        "expected_articles": [
            {"doc_keyword": "tndn", "article_number": [10, 11, 2]},
            {"doc_keyword": "qlt", "article_number": [14, 16]}
        ],
        "expected_keywords": [
            "thuế thu nhập doanh nghiệp",
            "tiền chậm nộp",
            "0,03%",
            "ngày cuối cùng",
            "ngân sách"
        ],
        "forbidden_keywords": [
            "không phải chịu tiền chậm nộp"
        ]
    },
    {
        "id": "TC-48",
        "category": "tax_law",
        "title": "Temporal Version-Aware: Đổi mới Biểu thuế 5 bậc và Giảm trừ gia cảnh Luật Thuế TNCN 2025",
        "query": "Luật Thuế thu nhập cá nhân 2025 (số 109/2025/QH15) có hiệu lực từ ngày 01/07/2026 và áp dụng cho kỳ tính thuế năm 2026 có những điểm đổi mới căn bản nào về số lượng bậc trong Biểu thuế luỹ tiến từng phần và mức giảm trừ gia cảnh so với quy định cũ trước đây?",
        "expected_articles": [
            {"doc_keyword": "tncn", "article_number": [9, 10, 28, 29]}
        ],
        "expected_keywords": [
            "5 bậc",
            "15,5 triệu",
            "6,2 triệu",
            "109/2025/QH15",
            "2026"
        ],
        "forbidden_keywords": [
            "vẫn giữ nguyên 7 bậc thuế cũ"
        ]
    }
]


def test_tax_cases():
    print("=" * 80)
    print("   KIỂM THỬ CÔ LẬP CỤM THUẾ 2025/2026 (DOMAIN EVALUATION: TC-41 -> TC-48)")
    print("=" * 80)

    total = len(TAX_TEST_CASES)
    passed_count = 0
    retrieval_passed_count = 0

    for idx, tc in enumerate(TAX_TEST_CASES, 1):
        print(f"\n[{idx:02d}/{total}] {tc['id']}: {tc['title']}")
        print(f"  > Query: {tc['query'][:80]}...")

        payload = {
            "query": tc["query"],
            "top_k": 5,
            "use_reranker": True,
            "as_of_date": tc.get("as_of_date"),
        }

        retrieved_citations = []
        answer_text = ""
        latency_ms = 0
        start_t = time.time()

        for attempt in range(2):
            try:
                retrieved_citations = []
                answer_text = ""
                res = requests.post(API_URL, json=payload, stream=True, timeout=60)
                if res.status_code == 200:
                    for line in res.iter_lines():
                        if line:
                            decoded = line.decode("utf-8")
                            if decoded.startswith("data: "):
                                data_str = decoded[6:]
                                try:
                                    data = json.loads(data_str)
                                    if "citations" in data:
                                        retrieved_citations = data["citations"]
                                    elif "token" in data:
                                        answer_text += data["token"]
                                    elif "latency_ms" in data:
                                        latency_ms = data["latency_ms"]
                                except:
                                    pass
                if answer_text:
                    break
                elif attempt == 0:
                    time.sleep(1.0)
            except Exception as e:
                if attempt == 0:
                    time.sleep(1.0)
                    continue
                print(f"  [!] Request Error: {e}")

        total_ms = int((time.time() - start_t) * 1000)

        # Evaluate Retrieval
        retrieval_ok = True
        matched_articles = []
        retrieved_keys = set()
        for c in retrieved_citations:
            doc_id = str(c.get("doc_id", "")).lower()
            art_num = c.get("article_number")
            retrieved_keys.add((doc_id, art_num))

        for exp in tc["expected_articles"]:
            exp_kw = exp.get("doc_keyword", "").lower()
            exp_num = exp.get("article_number")
            exp_nums = exp_num if isinstance(exp_num, list) else [exp_num]
            found = any(exp_kw in r_doc and r_num in exp_nums for (r_doc, r_num) in retrieved_keys)
            if found:
                matched_articles.append(f"Điều {exp_nums[0] if len(exp_nums)==1 else exp_nums}")
            else:
                retrieval_ok = False

        if retrieval_ok:
            retrieval_passed_count += 1

        # Evaluate Keywords
        ans_lower = answer_text.lower()
        matched_kw = []
        for kw_rule in tc["expected_keywords"]:
            synonyms = [s.strip() for s in kw_rule.split("|")]
            if any(syn.lower() in ans_lower for syn in synonyms):
                matched_kw.append(kw_rule)
        kw_ratio = len(matched_kw) / len(tc["expected_keywords"]) if tc["expected_keywords"] else 1.0

        # Forbidden check
        violates_forbidden = False
        for fkw in tc.get("forbidden_keywords", []):
            if fkw.lower() in ans_lower:
                violates_forbidden = True
                print(f"  [X] Vi phạm từ khóa cấm: '{fkw}'")
                break

        passed = retrieval_ok and (kw_ratio >= 0.6) and not violates_forbidden
        if passed:
            passed_count += 1

        status_str = "PASSED" if passed else "FAILED"
        print(f"  [+] KẾT QUẢ: {status_str} (Retrieval: {'OK' if retrieval_ok else 'FAIL'} | Keywords: {len(matched_kw)}/{len(tc['expected_keywords'])} | Latency: {total_ms}ms)")
        cit_list = [str(c.get('doc_id')) + ': D' + str(c.get('article_number')) for c in retrieved_citations[:4]]
        print(f"      - Trích dẫn: {cit_list}")
        print(f"      - Trả lời mẫu: {answer_text[:120].replace(chr(10), ' ')}...")

    print("\n" + "=" * 80)
    print(f" KẾT QUẢ KIỂM THỬ CỤM THUẾ (DOMAIN EVALUATION)")
    print(f"  - Test Case Pass Rate: {passed_count}/{total} ({passed_count/total*100:.1f}%)")
    print(f"  - Retrieval Recall:    {retrieval_passed_count}/{total} ({retrieval_passed_count/total*100:.1f}%)")
    print("=" * 80)

    return passed_count == total


if __name__ == "__main__":
    success = test_tax_cases()
    if not success:
        sys.exit(1)
