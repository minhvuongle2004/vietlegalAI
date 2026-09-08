import sys
import json
import requests

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

queries = [
    "Công ty giữ bản chính bằng đại học của người lao động bị phạt bao nhiêu tiền?",
    "Công ty không trả lương làm thêm giờ thì bị xử phạt như thế nào?",
    "Sa thải lao động nữ vì lý do mang thai thì người sử dụng lao động bị xử phạt thế nào?",
]

for q in queries:
    print("=" * 75)
    print("CÂU HỎI:", q)
    print("=" * 75)

    try:
        r = requests.post(
            "http://127.0.0.1:8000/api/v1/chat/completions",
            json={"query": q, "top_k": 3, "use_reranker": False},
            stream=True,
            timeout=30,
        )
        if r.status_code == 200:
            full_response = ""
            citations = []
            for line in r.iter_lines():
                if not line:
                    continue
                line_str = line.decode("utf-8")
                if line_str.startswith("data: "):
                    data_json = line_str[6:]
                    try:
                        data = json.loads(data_json)
                        if "citations" in data:
                            citations = data["citations"]
                        if "token" in data:
                            full_response += data["token"]
                    except Exception:
                        pass
            
            print("\nCĂN CỨ PHÁP LÝ (CITATIONS):")
            for c in citations:
                doc = c.get("doc_id", "")
                art = c.get("article_number", "")
                title = c.get("article_title", "")
                print(f"  * [{doc}] Điều {art}: {title}")

            print("\nTRẢ LỜI CỦA VIETLEGAL AI:")
            print(full_response.strip())
        else:
            print("Lỗi HTTP:", r.status_code, r.text)
    except Exception as e:
        print("Lỗi kết nối:", e)
    print("\n")
