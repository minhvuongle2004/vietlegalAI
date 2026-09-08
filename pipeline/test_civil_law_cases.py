import sys
import json
import re
import requests
import time

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

CIVIL_TEST_CASES = [
    {
        "id": "TC-35",
        "category": "civil_law",
        "title": "Đặt cọc và Xử lý tài sản đặt cọc khi vi phạm hợp đồng (Điều 328)",
        "as_of_date": "2024-12-31",
        "query": "Bên A đặt cọc cho bên B số tiền 100 triệu đồng để mua đất nhưng sau đó bên B đổi ý không chịu bán nữa. Theo Điều 328 Bộ luật Dân sự 2015, việc xử lý tiền đặt cọc được quy định thế nào và bên B phải trả cho bên A bao nhiêu tiền?",
        "expected_articles": [{"doc_keyword": "blds", "article_number": 328}],
        "expected_keywords": ["Điều 328", "Bộ luật Dân sự", "trả lại", "phạt cọc|tương đương|khoản tiền tương đương"],
        "forbidden_keywords": ["chỉ trả lại 100 triệu mà không bị phạt", "không phải trả lại tiền cọc"],
    },
    {
        "id": "TC-36",
        "category": "civil_law",
        "title": "Mức trần lãi suất vay tài sản tối đa 20%/năm (Điều 468)",
        "as_of_date": "2024-12-31",
        "query": "Các bên thỏa thuận hợp đồng vay tiền cá nhân với mức lãi suất 2,5%/tháng (tức 30%/năm). Mức lãi suất này có phù hợp với quy định của Bộ luật Dân sự 2015 không và theo Điều 468 thì mức lãi suất tối đa được phép thỏa thuận là bao nhiêu?",
        "expected_articles": [{"doc_keyword": "blds", "article_number": 468}],
        "expected_keywords": ["Điều 468", "Bộ luật Dân sự", "20%/năm|20% một năm|20% / năm", "không vượt quá|vượt quá", "không có hiệu lực|vô hiệu"],
        "forbidden_keywords": ["phù hợp, được phép thỏa thuận 30%"],
    },
    {
        "id": "TC-37",
        "category": "civil_law",
        "title": "Thời hiệu khởi kiện yêu cầu bồi thường thiệt hại ngoài hợp đồng (Điều 588)",
        "as_of_date": "2024-12-31",
        "query": "Thời hiệu khởi kiện yêu cầu bồi thường thiệt hại ngoài hợp đồng được xác định là bao nhiêu năm và tính từ thời điểm nào theo Điều 588 Bộ luật Dân sự 2015?",
        "expected_articles": [{"doc_keyword": "blds", "article_number": 588}],
        "expected_keywords": ["Điều 588", "Bộ luật Dân sự", "03 năm|3 năm", "thời điểm", "quyền, lợi ích hợp pháp bị xâm phạm"],
        "forbidden_keywords": ["01 năm", "02 năm", "5 năm"],
    },
    {
        "id": "TC-38",
        "category": "civil_law",
        "title": "Người thừa kế không phụ thuộc vào nội dung của di chúc (Điều 644)",
        "as_of_date": "2024-12-31",
        "query": "Người để lại di chúc truất toàn bộ quyền thừa kế của con chưa thành niên và vợ hợp pháp. Theo Điều 644 Bộ luật Dân sự 2015, những người này có được hưởng di sản không và mức hưởng bằng bao nhiêu phần của một suất thừa kế theo pháp luật?",
        "expected_articles": [{"doc_keyword": "blds", "article_number": 644}],
        "expected_keywords": ["Điều 644", "Bộ luật Dân sự", "vẫn được hưởng", "hai phần ba|2/3", "suất thừa kế theo pháp luật"],
        "forbidden_keywords": ["không được hưởng đồng nào", "bị truất hoàn toàn"],
    },
    {
        "id": "TC-39",
        "category": "civil_law",
        "title": "Điều kiện có hiệu lực của giao dịch dân sự & Hậu quả vô hiệu (Điều 117, 131)",
        "as_of_date": "2024-12-31",
        "query": "Giao dịch dân sự cần đáp ứng những điều kiện nào để có hiệu lực theo Điều 117 Bộ luật Dân sự 2015 và khi bị tuyên vô hiệu thì quyền, nghĩa vụ các bên được giải quyết ra sao theo Điều 131?",
        "expected_articles": [{"doc_keyword": "blds", "article_number": [117, 131]}],
        "expected_keywords": ["Điều 117", "Điều 131", "Bộ luật Dân sự", "tự nguyện", "khôi phục lại tình trạng ban đầu", "hoàn trả"],
        "forbidden_keywords": [],
    },
    {
        "id": "TC-40",
        "category": "civil_law",
        "title": "Thời điểm mở thừa kế và thời hiệu chia di sản bất động sản 30 năm (Điều 611, 623)",
        "as_of_date": "2024-12-31",
        "query": "Thời điểm mở thừa kế được xác định khi nào theo Điều 611 và thời hiệu để người thừa kế yêu cầu chia di sản thừa kế đối với bất động sản là bao nhiêu năm theo Điều 623 Bộ luật Dân sự 2015?",
        "expected_articles": [{"doc_keyword": "blds", "article_number": [611, 623]}],
        "expected_keywords": ["Điều 611", "Điều 623", "người có tài sản chết", "30 năm", "bất động sản"],
        "forbidden_keywords": ["10 năm đối với bất động sản"],
    },
]

API_URL = "http://127.0.0.1:8000/api/v1/chat/completions"

def run_civil_tests():
    print("=" * 80)
    print("   DOMAIN-SPECIFIC EVALUATION: BỘ LUẬT DÂN SỰ 2015 (6 CASES)")
    print("=" * 80)

    passed_count = 0
    retrieval_passed_count = 0

    for idx, tc in enumerate(CIVIL_TEST_CASES, 1):
        print(f"\n[{idx}/6] {tc['id']}: {tc['title']}")
        print(f"  > Query: {tc['query']}")

        payload = {
            "query": tc["query"],
            "top_k": 5,
            "use_reranker": True,
            "as_of_date": tc.get("as_of_date"),
        }

        retrieved_citations = []
        answer_text = ""
        req_start = time.time()

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
                                    d = json.loads(data_str)
                                    if "citations" in d:
                                        retrieved_citations = d["citations"]
                                    elif "token" in d:
                                        answer_text += d["token"]
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

        total_time = int((time.time() - req_start) * 1000)

        # 1. Evaluate Retrieval
        retrieval_ok = True
        matched_articles = []
        missing_articles = []

        retrieved_keys = set()
        for c in retrieved_citations:
            doc_id = str(c.get("doc_id", "")).lower()
            art_num = c.get("article_number")
            retrieved_keys.add((doc_id, art_num))

        for exp in tc["expected_articles"]:
            exp_kw = exp.get("doc_keyword", "").lower()
            exp_num = exp.get("article_number")
            exp_nums = exp_num if isinstance(exp_num, list) else [exp_num]
            found = False
            for (r_doc, r_num) in retrieved_keys:
                if exp_kw in r_doc and r_num in exp_nums:
                    found = True
                    break
            if found:
                matched_articles.append(f"Điều {exp_nums}")
            else:
                missing_articles.append(f"Điều {exp_nums} ({exp_kw})")
                retrieval_ok = False

        if retrieval_ok:
            retrieval_passed_count += 1

        # 2. Evaluate Keywords & Anti-hallucination
        matched_kw = []
        for kw_rule in tc["expected_keywords"]:
            synonyms = [s.strip() for s in kw_rule.split("|")]
            matched = False
            for syn in synonyms:
                try:
                    if re.search(syn, answer_text, re.IGNORECASE | re.DOTALL):
                        matched = True
                        break
                except re.error:
                    if syn.lower() in answer_text.lower():
                        matched = True
                        break
            if matched:
                matched_kw.append(kw_rule)

        kw_ratio = len(matched_kw) / len(tc["expected_keywords"]) if tc["expected_keywords"] else 1.0

        hit_forbidden = []
        for kw in tc["forbidden_keywords"]:
            try:
                if re.search(kw, answer_text, re.IGNORECASE | re.DOTALL):
                    hit_forbidden.append(kw)
            except re.error:
                if kw.lower() in answer_text.lower():
                    hit_forbidden.append(kw)

        # 3. Decision
        reasoning_ok = (kw_ratio >= 0.5) and (len(hit_forbidden) == 0)
        final_passed = retrieval_ok and reasoning_ok

        if final_passed:
            passed_count += 1
            print(f"  [+] KẾT QUẢ: PASSED (Retrieval: OK | Citations: {[c.get('doc_id')+'_D'+str(c.get('article_number')) for c in retrieved_citations]} | Keywords: {len(matched_kw)}/{len(tc['expected_keywords'])} | Latency: {total_time}ms)")
        else:
            print(f"  [-] KẾT QUẢ: FAILED (Retrieval: {'OK' if retrieval_ok else 'FAILED'} | Citations: {[c.get('doc_id')+'_D'+str(c.get('article_number')) for c in retrieved_citations]})")
            if not retrieval_ok:
                print(f"      Missing: {missing_articles}")
            if hit_forbidden:
                print(f"      Hit forbidden: {hit_forbidden}")
            if kw_ratio < 0.5:
                print(f"      Missing keywords: {[k for k in tc['expected_keywords'] if k not in matched_kw]}")

    print("\n" + "=" * 80)
    print(f"   KẾT QUẢ EVALUATION DOMAIN DÂN SỰ: {passed_count}/6 PASSED ({passed_count/6*100:.1f}%)")
    print(f"   RETRIEVAL RECALL RATE: {retrieval_passed_count}/6 ({retrieval_passed_count/6*100:.1f}%)")
    print("=" * 80)

if __name__ == "__main__":
    run_civil_tests()
