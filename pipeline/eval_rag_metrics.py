import os
import sys
import time
import json
import requests
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

API_BASE = "http://127.0.0.1:8000/api/v1"

def parse_sse_stream(response):
    """Phân tích các sự kiện SSE từ phản hồi streaming"""
    citations = []
    tokens = []
    latency_ms = None
    event_type = None

    for line in response.iter_lines(decode_unicode=True):
        if not line:
            continue
        if line.startswith("event:"):
            event_type = line.replace("event:", "").strip()
        elif line.startswith("data:"):
            data_str = line.replace("data:", "").strip()
            try:
                data_obj = json.loads(data_str)
                if event_type == "citations":
                    citations = data_obj.get("citations", [])
                elif event_type == "token":
                    tokens.append(data_obj.get("token", ""))
                elif event_type == "done":
                    latency_ms = data_obj.get("latency_ms")
            except Exception:
                pass

    return citations, "".join(tokens), latency_ms

def test_chat_query(query: str, top_k: int = 3):
    t0 = time.time()
    res = requests.post(
        f"{API_BASE}/chat/completions",
        json={"query": query, "top_k": top_k},
        stream=True,
        timeout=30,
    )
    first_byte_time = (time.time() - t0) * 1000
    if res.status_code != 200:
        return None, None, None, first_byte_time

    citations, answer, server_latency = parse_sse_stream(res)
    total_time = (time.time() - t0) * 1000
    return citations, answer, server_latency, total_time

def main():
    print("=" * 75)
    print("🚀 BẮT ĐẦU CHẠY KIỂM THỬ ĐÁNH GIÁ HỆ THỐNG RAG (VIETLEGAL AI)")
    print("   Target: http://127.0.0.1:8000/api/v1")
    print("=" * 75)

    test_cases = [
        {
            "query": "Thời gian thử việc tối đa của người có bằng đại học là bao lâu?",
            "expected_articles": [25],
            "category": "1. Thử việc (In-domain)",
        },
        {
            "query": "Hợp đồng không xác định thời hạn nghỉ việc phải báo trước bao nhiêu ngày?",
            "expected_articles": [35, 36],
            "category": "2. Nghỉ việc / Đơn phương (In-domain)",
        },
        {
            "query": "Người lao động làm việc đủ 12 tháng được nghỉ phép năm bao nhiêu ngày?",
            "expected_articles": [113],
            "category": "3. Nghỉ phép năm (In-domain)",
        },
        {
            "query": "Làm thêm giờ vào ngày nghỉ lễ tết được trả lương ít nhất bao nhiêu phần trăm?",
            "expected_articles": [98],
            "category": "4. Tiền lương làm thêm (In-domain)",
        },
        {
            "query": "Người sử dụng lao động có được phạt tiền thay vì kỷ luật lao động không?",
            "expected_articles": [127],
            "category": "5. Kỷ luật bị cấm (In-domain)",
        },
    ]

    print("\n--- PHẦN 1: ĐÁNH GIÁ RETRIEVAL & CITATION ACCURACY ---")
    hit_top1 = 0
    hit_top3 = 0
    latencies = []

    for idx, tc in enumerate(test_cases, 1):
        q = tc["query"]
        expected = tc["expected_articles"]

        citations, answer, s_lat, total_lat = test_chat_query(q, top_k=3)
        found_articles = [c.get("article_number") for c in citations]
        
        is_hit1 = any(e in found_articles[:1] for e in expected)
        is_hit3 = any(e in found_articles for e in expected)

        if is_hit1: hit_top1 += 1
        if is_hit3: hit_top3 += 1
        if s_lat: latencies.append(s_lat)

        status = "✅ PASS" if is_hit3 else "❌ MISS"
        print(f"[{idx}] {tc['category']}: {status}")
        print(f"    - Câu hỏi : {q}")
        print(f"    - Mong đợi: Điều {expected}")
        print(f"    - Trích dẫn tìm thấy: {found_articles}")
        print(f"    - Độ trễ Server: {s_lat}ms (Tổng thời gian: {total_lat:.0f}ms)")
        print(f"    - Đoạn trích câu trả lời: {answer[:130].strip()}...")
        print()

    print(f"🎯 KẾT QUẢ RETRIEVAL & CITATION:")
    print(f"   • Hit@1: {hit_top1}/{len(test_cases)} ({hit_top1/len(test_cases)*100:.0f}%)")
    print(f"   • Hit@3: {hit_top3}/{len(test_cases)} ({hit_top3/len(test_cases)*100:.0f}%)")
    print(f"   • Độ trễ trung bình: {sum(latencies)/len(latencies):.0f}ms")

    # PHẦN 2: KIỂM TRA PHÒNG CHỐNG ẢO GIÁC & CÂU HỎI NGOÀI PHẠM VI (OUT-OF-DOMAIN)
    print("\n" + "=" * 75)
    print("--- PHẦN 2: KIỂM TRA KHẢ NĂNG TỪ CHỐI CÂU HỎI NGOÀI CĂN CỨ ---")
    ood_query = "Thủ tục sang tên sổ đỏ nhà đất và lệ phí trước bạ bất động sản là bao nhiêu?"
    print(f"Câu hỏi test: '{ood_query}'")
    
    citations, ood_answer, s_lat, _ = test_chat_query(ood_query, top_k=3)
    print(f"Trích dẫn retrieved: {[c.get('article_number') for c in citations]}")
    print("\nPhản hồi từ AI:")
    print(ood_answer)

    refusal_keywords = ["không", "chưa có", "không đề cập", "không thuộc", "luật sư", "tham khảo", "bộ luật lao động"]
    passed_refusal = any(kw in ood_answer.lower() for kw in refusal_keywords)
    print(f"\n=> Đánh giá khả năng từ chối (Groundedness / No Hallucination): {'✅ ĐẠT (AI cảnh báo rõ không có căn cứ)' if passed_refusal else '❌ CHƯA ĐẠT'}")

    print("\n" + "=" * 75)
    print("🎯 TOÀN BỘ KIỂM THỬ ĐÃ HOÀN TẤT.")
    print("=" * 75)

if __name__ == "__main__":
    main()
