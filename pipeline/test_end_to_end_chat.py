import os
import sys
import json
import requests

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

url = "http://127.0.0.1:8000/api/v1/chat/completions"
payload = {
    "query": (
        "Tôi nghỉ việc sau 6 năm làm việc, trong đó có đóng BHXH và bảo hiểm thất nghiệp đầy đủ. "
        "Khi nghỉ việc, tôi có thể được hưởng những chế độ nào? "
        "Hãy phân biệt điều kiện hưởng BHXH một lần và trợ cấp thất nghiệp, đồng thời chỉ rõ căn cứ pháp lý của từng chế độ."
    ),
    "top_k": 5,
    "use_reranker": True
}

print(f"Gửi request tới {url}...")
res = requests.post(url, json=payload, stream=True, timeout=60)
print(f"HTTP Status: {res.status_code}")

full_text = ""
for line in res.iter_lines():
    if line:
        decoded = line.decode("utf-8")
        if decoded.startswith("data: "):
            data_str = decoded[6:]
            try:
                data = json.loads(data_str)
                if "citations" in data:
                    print("\n" + "=" * 60)
                    print("CÁC CĂN CỨ PHÁP LÝ ĐƯỢC HỆ THỐNG TRUY XUẤT:")
                    print("=" * 60)
                    for c in data["citations"]:
                        print(f"  • [{c['doc_title']}] Điều {c['article_number']}: {c['article_title']}")
                    print("=" * 60 + "\n")
                elif "token" in data:
                    full_text += data["token"]
            except Exception as e:
                pass

print("=== CÂU TRẢ LỜI CỦA VIETLEGAL AI ===")
print(full_text)
