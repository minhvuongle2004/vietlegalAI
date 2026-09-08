import os
import json
import requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

query = "Lao động nữ sinh vào tháng 7 năm 1972 làm việc trong điều kiện lao động bình thường. Căn cứ Phụ lục I Nghị định 135/2020/NĐ-CP, người này sẽ nghỉ hưu ở độ tuổi nào và thời điểm hưởng lương hưu là khi nào?"

print("=" * 80)
print("  DUMP 5 CHUNKS TRUYỀN VÀO LLM CỦA TC-16")
print("=" * 80)

# 1. Gọi debug-retrieve để lấy danh sách 5 chunks được chọn
resp = requests.get("http://127.0.0.1:8000/api/v1/legal/debug-retrieve", params={"q": query}, timeout=60)
data = resp.json()
final_5 = data.get("final_top5", [])

url = os.getenv("SUPABASE_URL", "").rstrip("/")
key = os.getenv("SUPABASE_KEY", "")
headers = {"apikey": key, "Authorization": f"Bearer {key}"}

output_lines = []
output_lines.append("=" * 80)
output_lines.append(f"QUERY: {query}\n")
output_lines.append(f"TỔNG SỐ CHUNKS ĐƯỢC CHỌN: {len(final_5)}")
output_lines.append("=" * 80)

for idx, h in enumerate(final_5, 1):
    doc_id = h["doc_id"]
    art_num = h["article_number"]
    rerank_score = h["reranker_score"]
    
    # Lấy full_text từ Supabase (chính là nội dung doc_store lưu)
    res = requests.get(
        f"{url}/rest/v1/legal_articles?document_id=eq.{doc_id}&article_number=eq.{art_num}&select=article_number,article_title,chapter_info,full_text",
        headers=headers
    )
    full_text = ""
    title = h["title"]
    chapter = ""
    if res.status_code == 200 and res.json():
        art = res.json()[0]
        title = art.get("article_title", title)
        chapter = art.get("chapter_info", "")
        full_text = art.get("full_text", "")
    
    header = f"Nghị định 135/2020/NĐ-CP. {chapter}. Điều {art_num}: {title}"
    
    output_lines.append(f"\n{'#'*80}")
    output_lines.append(f"--- CĂN CỨ PHÁP LÝ #{idx} ---")
    output_lines.append(f"Văn bản: {doc_id} | Điều {art_num}: {title}")
    output_lines.append(f"Điểm Reranker: {rerank_score}")
    output_lines.append(f"Độ dài ký tự: {len(full_text)}")
    output_lines.append(f"Ngữ cảnh: {header}")
    output_lines.append(f"{'#'*80}")
    output_lines.append("NỘI DUNG QUY ĐỊNH (NGUYÊN VĂN):")
    output_lines.append(full_text)
    output_lines.append("\n")

dump_content = "\n".join(output_lines)
with open("evals/tc16_full_context_dump.txt", "w", encoding="utf-8") as f:
    f.write(dump_content)

print(f"[+] Đã ghi toàn bộ 5 chunks nguyên văn vào: evals/tc16_full_context_dump.txt (Kích thước: {len(dump_content)} bytes)")

# In tóm tắt 5 chunks
for idx, h in enumerate(final_5, 1):
    print(f"  Chunk #{idx}: {h['doc_id']} - Điều {h['article_number']} (Rerank: {h['reranker_score']}) - {h['title'][:60]}")
