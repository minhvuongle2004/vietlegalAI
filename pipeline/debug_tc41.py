import requests
import json

payload = {
    "query": "Một cá nhân cư trú có thu nhập tính thuế từ tiền lương, tiền công trong tháng là 25 triệu đồng. Theo Biểu thuế luỹ tiến từng phần của Luật Thuế thu nhập cá nhân 2025 (Luật số 109/2025/QH15), số thuế TNCN phải nộp trong tháng được tính như thế nào và là bao nhiêu tiền?",
    "top_k": 8,
    "use_reranker": True
}

res = requests.post("http://127.0.0.1:8000/api/v1/chat/completions", json=payload, stream=True)
citations = []
text = ""
for line in res.iter_lines():
    if line:
        decoded = line.decode("utf-8")
        if decoded.startswith("data: "):
            d = json.loads(decoded[6:])
            if "citations" in d:
                citations = d["citations"]
            elif "token" in d:
                text += d["token"]

print("Citations retrieved:")
for c in citations:
    print(f"  - {c.get('doc_id')}: Điều {c.get('article_number')} ({c.get('article_title')})")
print("\nResponse preview:")
print(text[:300])
