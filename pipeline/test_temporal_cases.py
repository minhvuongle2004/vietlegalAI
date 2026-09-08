import sys
import json
import requests

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

cases = [
    {
        "id": "TC-31",
        "as_of_date": "2024-12-31",
        "query": "Tại thời điểm tháng 12/2024, người lao động sau 1 năm nghỉ việc không tiếp tục đóng BHXH và chưa đủ 20 năm đóng BHXH có được rút BHXH một lần không theo quy định Luật BHXH?",
    },
    {
        "id": "TC-32",
        "as_of_date": "2025-08-01",
        "query": "Từ ngày 01/07/2025 khi Luật BHXH 2024 có hiệu lực thi hành, điều kiện rút BHXH một lần đối với người lao động sau 12 tháng không thuộc diện tham gia BHXH bắt buộc được quy định tại điều nào?",
    },
    {
        "id": "TC-33",
        "as_of_date": "2025-08-01",
        "query": "Theo Luật Bảo hiểm xã hội 2024 có hiệu lực từ ngày 01/07/2025, người lao động đủ tuổi nghỉ hưu cần đóng BHXH tối thiểu bao nhiêu năm để được hưởng lương hưu hàng tháng theo Điều 64?",
    },
    {
        "id": "TC-34",
        "as_of_date": "2025-08-01",
        "query": "Luật sửa đổi, bổ sung một số điều của Luật Bảo hiểm y tế số 51/2024/QH15 có hiệu lực từ ngày 01/07/2025 sửa đổi quy định gì về mức hưởng và đăng ký khám bệnh, chữa bệnh bảo hiểm y tế?",
    },
]

for c in cases:
    print(f"Testing {c['id']} with as_of_date={c['as_of_date']}...")
    res = requests.post(
        "http://127.0.0.1:8000/api/v1/chat/completions",
        json={
            "query": c["query"],
            "top_k": 5,
            "use_reranker": True,
            "as_of_date": c["as_of_date"],
        },
        stream=True,
        timeout=60,
    )
    citations = []
    text = ""
    for line in res.iter_lines():
        if line:
            decoded = line.decode("utf-8")
            if decoded.startswith("data: "):
                try:
                    d = json.loads(decoded[6:])
                    if "citations" in d:
                        citations = d["citations"]
                    elif "token" in d:
                        text += d["token"]
                except:
                    pass
    cits = [f"{x.get('doc_id')}_D{x.get('article_number')}" for x in citations]
    print(f"  -> Citations: {cits}")
    print(f"  -> Answer snippet: {text[:150]}...\n")
