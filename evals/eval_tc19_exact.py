import os
import sys
import json
import time
import requests

sys.stdout.reconfigure(encoding='utf-8')

API_URL = "http://127.0.0.1:8000/api/v1/chat/completions"

with open("evals/vietlegal_benchmark.json", "r", encoding="utf-8") as f:
    benchmark = json.load(f)

tc19 = next(item for item in benchmark if item["id"] == "TC-19")
query = tc19["query"]
expected_articles = tc19["expected_articles"]
expected_keywords = tc19["expected_keywords"]
forbidden_keywords = tc19["forbidden_keywords"]

print("="*80)
print(f"RUNNING BENCHMARK EXACTLY FOR TC-19")
print(f"Query: {query}")
print("="*80)

payload = {
    "query": query,
    "top_k": 5,
    "use_reranker": True
}

print("Đang chờ backend sẵn sàng...")
for attempt in range(30):
    try:
        r = requests.get("http://127.0.0.1:8000/api/v1/health", timeout=2)
        if r.status_code == 200:
            print("Backend đã sẵn sàng!")
            break
    except Exception:
        time.sleep(2)

start_time = time.time()
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

total_time = int((time.time() - start_time) * 1000)

# 1. Retrieval Recall
retrieval_ok = True
matched_articles = []
missing_articles = []

retrieved_keys = set()
for c in retrieved_citations:
    doc_id = str(c.get("doc_id", "")).lower()
    art_num = c.get("article_number")
    retrieved_keys.add((doc_id, art_num))

for exp in expected_articles:
    exp_kw = exp.get("doc_keyword", "").lower()
    exp_num = exp.get("article_number")
    exp_nums = exp_num if isinstance(exp_num, list) else [exp_num]
    found = False
    for (r_doc, r_num) in retrieved_keys:
        if exp_kw in r_doc and r_num in exp_nums:
            found = True
            break
    if found:
        matched_articles.append(f"Điều {exp_nums[0] if len(exp_nums)==1 else exp_nums} ({exp_kw})")
    else:
        missing_articles.append(f"Điều {exp_nums[0] if len(exp_nums)==1 else exp_nums} ({exp_kw})")
        retrieval_ok = False

# 2. Keywords Match
matched_kw = []
for kw_rule in expected_keywords:
    synonyms = [s.strip().lower() for s in kw_rule.split("|")]
    if any(s in answer_text.lower() for s in synonyms):
        matched_kw.append(kw_rule)

kw_ratio = len(matched_kw) / len(expected_keywords) if expected_keywords else 1.0
hit_forbidden = [kw for kw in forbidden_keywords if kw.lower() in answer_text.lower()]

# 3. Status
reasoning_ok = (kw_ratio >= 0.5) and (len(hit_forbidden) == 0)
final_passed = retrieval_ok and reasoning_ok

if final_passed:
    status_str = "PASSED"
else:
    status_str = "FAILED" if not retrieval_ok and not reasoning_ok else "PARTIAL"

report = {
    "tc_id": "TC-19",
    "retrieval": retrieval_ok,
    "matched_articles": matched_articles,
    "missing_articles": missing_articles,
    "kw_ratio": round(kw_ratio, 2),
    "matched_keywords": matched_kw,
    "missing_keywords": [k for k in expected_keywords if k not in matched_kw],
    "hit_forbidden": hit_forbidden,
    "status": status_str,
    "latency_ms": total_time,
    "answer_text": answer_text
}

with open("evals/tc19_benchmark_eval.json", "w", encoding="utf-8") as f:
    json.dump(report, f, ensure_ascii=False, indent=2)

print("\n" + "="*80)
print(f"Retrieval = {retrieval_ok}")
print(f"KW Ratio = {round(kw_ratio, 2)} ({len(matched_kw)}/{len(expected_keywords)})")
print(f"Matched Keywords: {matched_kw}")
print(f"Missing Keywords: {[k for k in expected_keywords if k not in matched_kw]}")
print(f"Hit Forbidden = {hit_forbidden}")
print(f"Status = {status_str}")
print("="*80)
