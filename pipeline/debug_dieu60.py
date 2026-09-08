import urllib.request
import json
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

payload = {
    "query": "Tôi đã tham gia BHXH được 8 năm và hiện đã nghỉ việc. Theo Luật Bảo hiểm xã hội 2014 trong cơ sở dữ liệu của hệ thống, tôi có thể hưởng BHXH một lần trong những trường hợp nào? Hãy nêu rõ căn cứ Điều 60 và các điều kiện liên quan.",
    "use_reranker": False,
    "top_k": 10
}

req = urllib.request.Request(
    "http://127.0.0.1:8000/api/v1/chat/completions",
    data=json.dumps(payload).encode("utf-8"),
    headers={"Content-Type": "application/json"}
)

with urllib.request.urlopen(req, timeout=40) as resp:
    tokens = []
    citations = []
    for raw_line in resp:
        line = raw_line.decode("utf-8").strip()
        if line.startswith("data:"):
            data_str = line[5:].strip()
            try:
                msg = json.loads(data_str)
                if "token" in msg:
                    tokens.append(msg["token"])
                if "citations" in msg:
                    citations = msg["citations"]
            except:
                pass

print("=== CITATIONS RETRIEVED ===")
for c in citations:
    print(f"- [{c.get('doc_id')}] Điều {c.get('article_number')}: {c.get('article_title')}")
    print("  Clause:", c.get("clause_number"))
    print("  Context header:", c.get("context_header"))
    print("  Excerpt:\n", repr(c.get("excerpt")))
    print("-" * 50)

print("\n=== BOT RESPONSE ===")
print("".join(tokens))
