import os
import sys
import json
import time
import requests

sys.stdout.reconfigure(encoding='utf-8')

API_URL = "http://127.0.0.1:8000/api/v1/chat/completions"

tc19_query = "Người lao động làm việc từ ngày 01/01/2018 đến 30/09/2023 thì chấm dứt HĐLĐ hợp pháp. Trong suốt thời gian này người lao động không thuộc diện tham gia BHTN. Hỏi thời gian tính trợ cấp thôi việc là bao nhiêu năm?"

payload = {
    "query": tc19_query,
    "top_k": 5,
    "use_reranker": True
}

retrieved_citations = []
answer_text = ""

res = requests.post(API_URL, json=payload, stream=True, timeout=60)

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
            except:
                pass

expected_articles = [
    {"doc_keyword": "bllđ", "article_number": 46},
    {"doc_keyword": "145", "article_number": 8}
]

retrieved_keys = set()
for c in retrieved_citations:
    doc_id = str(c.get("doc_id", "")).lower()
    art_num = c.get("article_number")
    retrieved_keys.add((doc_id, art_num))

matched = []
missing = []
for exp in expected_articles:
    kw = exp["doc_keyword"].lower()
    num = exp["article_number"]
    found = any(kw in r_doc and r_num == num for (r_doc, r_num) in retrieved_keys)
    if found:
        matched.append(f"Điều {num} ({kw})")
    else:
        missing.append(f"Điều {num} ({kw})")

retrieval_ok = (len(missing) == 0)

result_data = {
    "retrieval_ok": retrieval_ok,
    "matched": matched,
    "missing": missing,
    "top_5": [
        {
            "rank": idx,
            "doc_id": c.get("doc_id"),
            "doc_title": c.get("doc_title"),
            "article_number": c.get("article_number"),
            "article_title": c.get("article_title")
        }
        for idx, c in enumerate(retrieved_citations, 1)
    ],
    "answer_text": answer_text
}

with open("evals/tc19_result.json", "w", encoding="utf-8") as f:
    json.dump(result_data, f, ensure_ascii=False, indent=2)

print("SUCCESS: Result saved to evals/tc19_result.json")
