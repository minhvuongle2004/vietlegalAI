import os
import sys
import json
import time
import re
import asyncio
from pathlib import Path
from typing import List, Dict, Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from backend.app.services.rag.retriever import HybridRetriever
from backend.app.services.rag.generator import LegalAnswerGenerator

BENCHMARK_FILE = PROJECT_ROOT / "evals" / "traffic_benchmark_10.json"
OUTPUT_REPORT = PROJECT_ROOT / "evals" / "traffic_tg09_report.json"


async def run_tg09_eval():
    if not BENCHMARK_FILE.exists():
        print(f"[!] Không tìm thấy {BENCHMARK_FILE}")
        return

    with open(BENCHMARK_FILE, "r", encoding="utf-8") as f:
        all_cases = json.load(f)

    tg09 = next((c for c in all_cases if c["id"] == "TG-09"), None)
    if not tg09:
        print("[!] Không tìm thấy case TG-09 trong benchmark!")
        return

    print("=" * 95)
    print("   VIETLEGAL AI — KIỂM THỬ CÔ LẬP CASE TG-09 (TITLE MAPPING & TEMPORAL REASONING)")
    print(f"   Test Case: TG-09 — {tg09.get('title', '')}")
    print("=" * 95)

    retriever = HybridRetriever()
    generator = LegalAnswerGenerator()

    query = tg09["query"]
    as_of_date = tg09.get("law_as_of_date", "2026-03-01")
    expected_articles = tg09.get("expected_articles", [])
    expected_keywords = tg09.get("expected_keywords", [])
    forbidden_keywords = tg09.get("forbidden_keywords", [])

    print(f"\n> Query: {query}")
    print(f"> As-of Date: {as_of_date}")

    t_start = time.time()

    # 1. Retrieval
    t_ret_start = time.time()
    retrieved_chunks = retriever.retrieve(
        query=query,
        top_k=5,
        use_reranker=True,
        as_of_date=as_of_date,
    )
    ret_time_ms = int((time.time() - t_ret_start) * 1000)

    # Đo Context Length
    context_str = generator._build_context_str(retrieved_chunks)
    context_len = len(context_str)

    print(f"\n[+] Retrieval Hoàn tất ({ret_time_ms}ms): {len(retrieved_chunks)} items.")
    print("-" * 50)
    for idx, c in enumerate(retrieved_chunks, 1):
        print(f"  Item #{idx}: Doc={c.get('doc_id')} | Title={c.get('doc_title')} | Điều={c.get('article_number')}: {c.get('article_title')}")
    print("-" * 50)
    print(f"[+] Context Length: {context_len:,} ký tự (~{context_len // 4:,} tokens)")

    # 2. Generation & đo TTFT + Total Latency
    t_gen_start = time.time()
    ttft_ms = None
    answer_text = ""

    try:
        async for token in generator.generate_answer_stream(query=query, retrieved_chunks=retrieved_chunks):
            if ttft_ms is None:
                ttft_ms = int((time.time() - t_gen_start) * 1000)
            answer_text += token
    except Exception as e:
        print(f"[!] Lỗi generator: {e}")
        answer_text = f"[LỖI GENERATOR]: {e}"

    gen_time_ms = int((time.time() - t_gen_start) * 1000)
    total_time_ms = int((time.time() - t_start) * 1000)

    # 3. Đánh giá 3 lớp kiểm tra
    # A. Retrieval Match
    retrieved_docs_arts = [
        (c.get("doc_id", "").lower(), str(c.get("article_number", "")))
        for c in retrieved_chunks
    ]
    matched_expected = 0
    total_expected = 0
    for exp in expected_articles:
        exp_kw = exp.get("doc_keyword", "").lower()
        arts = exp.get("article_number", [])
        if isinstance(arts, (int, str)):
            arts = [arts]
        for a in arts:
            total_expected += 1
            if any(exp_kw in d and str(a) == art_str for d, art_str in retrieved_docs_arts):
                matched_expected += 1

    retrieval_pass = matched_expected >= 2  # Cần ít nhất 2 điều quan trọng (Điều 53 và Điều 54 NĐ 168)

    # B. Document Title Recognition (Không bị từ chối)
    rejection_phrases = [
        "không có trong các căn cứ",
        "chưa có quy định trực tiếp",
        "không được cung cấp",
        "không tìm thấy thông tin",
    ]
    is_rejected = any(rp in answer_text.lower() for rp in rejection_phrases)
    title_recognized = not is_rejected and "168/2024" in answer_text

    # C. Reasoning & Expected Keywords
    matched_kws = []
    missing_kws = []
    ans_lower = answer_text.lower()

    for kw in expected_keywords:
        parts = [p.strip().lower() for p in kw.split("|")]
        if any(p in ans_lower for p in parts):
            matched_kws.append(kw)
        else:
            missing_kws.append(kw)

    hit_forbidden = [f for f in forbidden_keywords if f.lower() in ans_lower]

    keyword_ratio = len(matched_kws) / len(expected_keywords) if expected_keywords else 1.0
    reasoning_pass = keyword_ratio >= 0.70 and len(hit_forbidden) == 0

    # D. Tổng kết trạng thái
    final_pass = retrieval_pass and title_recognized and reasoning_pass

    print("\n" + "=" * 95)
    print("                    KẾT QUẢ ĐÁNH GIÁ TG-09")
    print("=" * 95)
    print(f"Trạng thái: {'[PASSED]' if final_pass else '[FAILED]'}")
    print(f"1. Retrieval: {matched_expected}/{total_expected} expected articles -> {'PASS' if retrieval_pass else 'FAIL'}")
    print(f"2. Tên văn bản được nhận diện: {'PASS (Được công nhận)' if title_recognized else 'FAIL (Bị từ chối hoặc thiếu)'}")
    print(f"3. Reasoning Keywords: {len(matched_kws)}/{len(expected_keywords)} ({keyword_ratio*100:.1f}%) -> {'PASS' if reasoning_pass else 'FAIL'}")
    print(f"   - Matched: {matched_kws}")
    print(f"   - Missing: {missing_kws}")
    print(f"4. Hiệu năng: TTFT={ttft_ms}ms | Total Gen={gen_time_ms}ms | Total Latency={total_time_ms}ms")
    print("\n--- NỘI DUNG CÂU TRẢ LỜI CỦA MÔ HÌNH ---")
    print(answer_text)
    print("=" * 95)

    result_data = {
        "id": "TG-09",
        "passed": final_pass,
        "retrieval_pass": retrieval_pass,
        "title_recognized": title_recognized,
        "reasoning_pass": reasoning_pass,
        "retrieval_score": f"{matched_expected}/{total_expected}",
        "context_length_chars": context_len,
        "ttft_ms": ttft_ms,
        "gen_time_ms": gen_time_ms,
        "total_time_ms": total_time_ms,
        "matched_keywords": matched_kws,
        "missing_keywords": missing_kws,
        "answer": answer_text,
    }

    with open(OUTPUT_REPORT, "w", encoding="utf-8") as f:
        json.dump(result_data, f, ensure_ascii=False, indent=2)

    retriever.close()


if __name__ == "__main__":
    asyncio.run(run_tg09_eval())
