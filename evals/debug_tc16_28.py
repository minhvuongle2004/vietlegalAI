import json
import os
from pathlib import Path
from dotenv import load_dotenv
import requests

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

with open("evals/benchmark_report.json", encoding="utf-8") as f:
    report = json.load(f)
    cases = {c["id"]: c for c in report["details"]}

print("=" * 80)
print("  INSPECTING EXACT RETRIEVED CHUNKS AND CONTEXT SENT TO LLM")
print("=" * 80)

# 1. Gọi endpoint debug-retrieve cho TC-16 và TC-28
for tc_id in ["TC-16", "TC-28"]:
    c = cases[tc_id]
    q = c["query"]
    print(f"\n{'#'*80}\n  CASE {tc_id}: {c['title']}\n  Query: {q}\n{'#'*80}")
    
    # Gọi /api/v1/legal/debug-retrieve
    resp = requests.get("http://127.0.0.1:8000/api/v1/legal/debug-retrieve", params={"q": q}, timeout=60)
    data = resp.json()
    
    final_5 = data.get("final_top5", [])
    print(f"\n--- TOP-5 RETRIEVED CHUNKS FOR {tc_id} ---")
    for i, h in enumerate(final_5, 1):
        print(f"[{i}] {h['doc_id']} Đ{h['article_number']}: {h['title']} (rerank: {h['reranker_score']})")
    
    print("\n--- DETAILED FULL_TEXT OF RETRIEVED CHUNKS ---")
    # Lấy nội dung chi tiết từng điều từ Supabase
    url = os.getenv("SUPABASE_URL", "").rstrip("/")
    key = os.getenv("SUPABASE_KEY", "")
    headers = {"apikey": key, "Authorization": f"Bearer {key}"}
    for h in final_5:
        doc_id = h["doc_id"]
        art_num = h["article_number"]
        res = requests.get(f"{url}/rest/v1/legal_articles?document_id=eq.{doc_id}&article_number=eq.{art_num}&select=article_number,article_title,full_text", headers=headers)
        if res.status_code == 200 and res.json():
            art = res.json()[0]
            print(f"\n>>> [NỘI DUNG Đ{art['article_number']}: {art['article_title']}] <<<")
            txt = art['full_text']
            # Kiểm tra xem có Phụ lục I hay bảng biểu không
            print(f"Độ dài ký tự: {len(txt)}")
            print(txt[:800])
            if "Phụ lục" in txt or "phụ lục" in txt:
                print(">>> CÓ CHỨA TỪ 'Phụ lục' <<<")
            else:
                print(">>> KHÔNG CHỨA TỪ 'Phụ lục' <<<")
            if "1972" in txt or "1966" in txt:
                print(f">>> CÓ CHỨA NĂM SINH ĐANG TÌM KIẾM TRONG TEXT! <<<")
            else:
                print(f">>> KHÔNG CÓ NĂM SINH TRONG TEXT! <<<")

print("\n" + "=" * 80)
print("  KIỂM TRA TẤT CẢ ĐIỀU KHOẢN CỦA NĐ 135 TRONG SUPABASE")
print("=" * 80)
res = requests.get(f"{url}/rest/v1/legal_articles?document_id=ilike.*135*&select=document_id,article_number,article_title", headers=headers)
if res.status_code == 200:
    for row in sorted(res.json(), key=lambda x: x['article_number']):
        print(f"  Đ{row['article_number']}: {row['article_title']}")

