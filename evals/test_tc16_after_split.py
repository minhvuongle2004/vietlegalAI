import json
import time
import requests

query = "Lao động nữ sinh vào tháng 7 năm 1972 làm việc trong điều kiện lao động bình thường. Căn cứ Phụ lục I Nghị định 135/2020/NĐ-CP, người này sẽ nghỉ hưu ở độ tuổi nào và thời điểm hưởng lương hưu là khi nào?"

print("=" * 80)
print("  KIỂM TRA TC-16 SAU KHI TÁCH PHỤ LỤC I THÀNH BẢNG NAM VÀ BẢNG NỮ")
print("=" * 80)
print("Query:", query)

# 1. Kiểm tra Debug-Retrieve
print("\n--- 1. KIỂM TRA TẦNG RETRIEVAL ---")
resp = requests.get("http://127.0.0.1:8000/api/v1/legal/debug-retrieve", params={"q": query}, timeout=60)
data = resp.json()

print("\nDense Sub-queries:")
for cat, hits in data.get("dense_sub_queries", {}).items():
    print(f"  Category '{cat}':")
    for h in hits[:10]:
        marker = " ◄◄◄ BẢNG NỮ (Đ13)" if h["article_number"] == 13 else (" ◄ BẢNG NAM (Đ10)" if h["article_number"] == 10 else "")
        print(f"    [{h['rank']:>2}] {h['doc_id']} Đ{str(h['article_number']):<4} score={h['score']:.6f} {h['title'][:55]}{marker}")

print("\nFinal Top-5 Chunks (Sau RRF + Reranker + Balanced Allocation):")
found_nu_pl1 = False
for h in data.get("final_top5", []):
    rank = h["rank"]
    doc_id = h["doc_id"]
    art = h["article_number"]
    r_score = h["reranker_score"]
    title = h["title"][:55]
    marker = ""
    if art == 13 and "135" in doc_id:
        marker = " ◄◄◄ BẢNG NỮ PHỤ LỤC I (ĐÍCH CẦN TÌM!)"
        found_nu_pl1 = True
    elif art == 10 and "135" in doc_id:
        marker = " ◄ BẢNG NAM PHỤ LỤC I"
    elif art == 4 and "135" in doc_id:
        marker = " ◄ ĐIỀU 4 (Năm nghỉ hưu)"
    print(f"  [{rank}] {doc_id} Đ{str(art):<4} (rerank: {r_score:.6f}) - {title}{marker}")

if found_nu_pl1:
    print("\n  >>> THÀNH CÔNG: Bảng Nữ Phụ lục I (Đ13) ĐÃ LỌT VÀO TOP-5 CUỐI CÙNG! <<<")
else:
    print("\n  >>> CHƯA LỌT: Bảng Nữ Phụ lục I chưa có trong Top-5 <<<")

# 2. Kiểm tra LLM Generation
print("\n--- 2. KIỂM TRA CÂU TRẢ LỜI CỦA LLM ---")
api_url = "http://127.0.0.1:8000/api/v1/chat/completions"
payload = {
    "query": query,
    "top_k": 5,
    "use_reranker": True,
}

t0 = time.time()
res = requests.post(api_url, json=payload, stream=True, timeout=60)
answer_text = ""
if res.status_code == 200:
    for line in res.iter_lines():
        if line:
            decoded = line.decode("utf-8")
            if decoded.startswith("data: "):
                try:
                    d = json.loads(decoded[6:])
                    if "token" in d:
                        answer_text += d["token"]
                except:
                    pass

elapsed = time.time() - t0
print(f"Thời gian sinh: {elapsed:.2f}s")
print("\n" + "=" * 80)
print("ANSWER NGUYÊN VĂN TỪ LLM:")
print("=" * 80)
print(answer_text)
print("=" * 80)

# 3. Đánh giá nhanh
print("\n--- 3. ĐÁNH GIÁ CHUẨN XÁC ---")
if "58 tuổi 4 tháng" in answer_text:
    print("  [+] KẾT QUẢ ĐẠT: Đã trả lời đúng mốc '58 tuổi 4 tháng'!")
else:
    print("  [-] KẾT QUẢ: Chưa xuất hiện '58 tuổi 4 tháng'")

if "51 tuổi" in answer_text:
    print("  [-] CẢNH BÁO: Vẫn còn ảo giác '51 tuổi'!")
else:
    print("  [+] KHẮC PHỤC TRIỆT ĐỂ: Hoàn toàn không còn ảo giác '51 tuổi'!")
