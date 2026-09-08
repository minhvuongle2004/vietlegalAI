import urllib.request
import json
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def test_chat(query: str):
    print(f"\n{'='*70}\n[TEST] CÂU HỎI: {query}\n{'='*70}")
    payload = {
        "query": query,
        "use_reranker": False,
        "top_k": 3
    }
    req = urllib.request.Request(
        "http://127.0.0.1:8000/api/v1/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=45) as resp:
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

    print("\n--- CĂN CỨ PHÁP LÝ TRÍCH DẪN ---")
    for c in citations:
        did = c.get('doc_id')
        dt = c.get('doc_title')
        anum = c.get('article_number')
        atitle = c.get('article_title')
        print(f" [+] [{did}] {dt} -> Điều {anum}: {atitle}")

    print("\n--- CÂU TRẢ LỜI CỦA VIETLEGAL AI ---")
    full_answer = "".join(tokens)
    print(full_answer)
    return citations, full_answer

if __name__ == "__main__":
    test_chat("Điều kiện hưởng trợ cấp thất nghiệp theo Luật Việc làm là gì và mức hưởng hàng tháng là bao nhiêu? Căn cứ vào điều nào?")
    test_chat("Người lao động được hưởng bảo hiểm xã hội một lần trong những trường hợp nào theo Luật Bảo hiểm xã hội 2014?")
