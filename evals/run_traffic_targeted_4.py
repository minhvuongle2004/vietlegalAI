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
OUTPUT_REPORT = PROJECT_ROOT / "evals" / "traffic_targeted_4_report.json"

TARGET_CASES = ["TG-01", "TG-02", "TG-05", "TG-10"]


async def run_targeted_eval():
    if not BENCHMARK_FILE.exists():
        print(f"[!] Không tìm thấy {BENCHMARK_FILE}")
        return

    with open(BENCHMARK_FILE, "r", encoding="utf-8") as f:
        all_cases = json.load(f)

    cases = [c for c in all_cases if c["id"] in TARGET_CASES]

    print("=" * 95)
    print("   VIETLEGAL AI — KIỂM THỬ CÔ LẬP TARGET ARTICLE HYDRATION")
    print(f"   Các test cases cô lập: {TARGET_CASES}")
    print(f"   Đo lường: Context Length, TTFT, Total Time, Reasoning Accuracy")
    print("=" * 95)

    retriever = HybridRetriever()
    generator = LegalAnswerGenerator()

    results = []

    for idx, tc in enumerate(cases, 1):
        tc_id = tc["id"]
        title = tc.get("title", "")
        query = tc["query"]
        as_of_date = tc.get("law_as_of_date", "2026-09-01")
        expected_articles = tc.get("expected_articles", [])
        expected_keywords = tc.get("expected_keywords", [])
        forbidden_keywords = tc.get("forbidden_keywords", [])

        print(f"\n[{idx}/{len(cases)}] {tc_id}: {title}")
        print(f"  > Query: {query}")

        t_start = time.time()

        # 1. Retrieval có Target Article Hydration
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
        hydrated_articles = [
            f"{c.get('doc_id')}:Đ{c.get('article_number')}"
            for c in retrieved_chunks
            if c.get("is_hydrated")
        ]

        print(f"  > Retrieval ({ret_time_ms}ms): {len(retrieved_chunks)} items. Hydrated: {hydrated_articles}")
        print(f"  > Context Length: {context_len:,} ký tự (~{context_len // 4:,} tokens)")

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
            print(f"  [!] Lỗi generator: {e}")
            answer_text = f"[LỖI GENERATOR]: {e}"

        gen_time_ms = int((time.time() - t_gen_start) * 1000)
        total_time_ms = int((time.time() - t_start) * 1000)

        # 3. Đánh giá kết quả
        # Lớp 1: Retrieval
        retrieved_keys = set()
        for c in retrieved_chunks:
            doc_id = str(c.get("doc_id", "")).lower()
            art_num = c.get("article_number")
            retrieved_keys.add((doc_id, art_num))

        matched_articles = []
        missing_articles = []
        for exp in expected_articles:
            exp_kw = (exp.get("doc_id") or exp.get("doc_keyword", "")).lower()
            exp_num = exp.get("article_number")
            exp_nums = exp_num if isinstance(exp_num, list) else [exp_num]
            found = False
            for (r_doc, r_num) in retrieved_keys:
                if exp_kw in r_doc and r_num in exp_nums:
                    found = True
                    break
            if found:
                matched_articles.append(f"{exp_kw}:Đ{exp_nums[0] if len(exp_nums)==1 else exp_nums}")
            else:
                missing_articles.append(f"{exp_kw}:Đ{exp_nums[0] if len(exp_nums)==1 else exp_nums}")

        retrieval_ok = len(missing_articles) == 0

        # Lớp 2: Keywords & Reasoning
        matched_kw = []
        for kw_rule in expected_keywords:
            synonyms = [s.strip() for s in kw_rule.split("|")]
            matched = False
            for syn in synonyms:
                try:
                    if re.search(syn, answer_text, re.IGNORECASE | re.DOTALL):
                        matched = True
                        break
                except re.error:
                    if syn.lower() in answer_text.lower():
                        matched = True
                        break
            if matched:
                matched_kw.append(kw_rule)

        kw_ratio = len(matched_kw) / len(expected_keywords) if expected_keywords else 1.0

        hit_forbidden = []
        for kw in forbidden_keywords:
            try:
                if re.search(kw, answer_text, re.IGNORECASE | re.DOTALL):
                    hit_forbidden.append(kw)
            except re.error:
                if kw.lower() in answer_text.lower():
                    hit_forbidden.append(kw)

        reasoning_ok = (kw_ratio >= 0.6) and (len(hit_forbidden) == 0)

        # Lớp 3: Legal Version
        ans_lower = answer_text.lower()
        version_ok = len(hit_forbidden) == 0 and ("100/2019" not in ans_lower)

        # Special check cho TG-10
        special_notes = []
        if tc_id == "TG-10":
            has_total_money = any(t in ans_lower for t in ["48.000.000", "48 triệu", "60.000.000", "60 triệu", "48 - 60", "48-60"])
            has_points_rule = any(t in ans_lower for t in ["10 điểm", "trừ 10 điểm", "nhiều nhất", "nhiều điểm nhất"])
            special_notes.append(f"TG-10 Tổng tiền: {'✅ ĐẠT (48-60 triệu)' if has_total_money else '❌ THIẾU'}")
            special_notes.append(f"TG-10 Nguyên tắc trừ điểm: {'✅ ĐẠT (10 điểm - cao nhất)' if has_points_rule else '❌ THIẾU'}")
            if not (has_total_money and has_points_rule):
                reasoning_ok = False

        final_passed = retrieval_ok and reasoning_ok and version_ok
        status_str = "PASSED" if final_passed else "FAILED"

        print(f"  > Latency: TTFT = {ttft_ms}ms | Gen = {gen_time_ms}ms | Total = {total_time_ms}ms")
        print(f"  > Keywords: {len(matched_kw)}/{len(expected_keywords)} ({kw_ratio*100:.1f}%)")
        if special_notes:
            for sn in special_notes:
                print(f"  > {sn}")
        print(f"  => KẾT QUẢ: [{status_str}]")

        print("-" * 50)
        print(f"CÂU TRẢ LỜI CỦA MODEL:\n{answer_text.strip()}\n")
        print("-" * 50)

        results.append({
            "id": tc_id,
            "title": title,
            "status": status_str,
            "passed": final_passed,
            "retrieval_ok": retrieval_ok,
            "reasoning_ok": reasoning_ok,
            "version_ok": version_ok,
            "context_length_chars": context_len,
            "hydrated_articles": hydrated_articles,
            "retrieval_time_ms": ret_time_ms,
            "ttft_ms": ttft_ms,
            "gen_time_ms": gen_time_ms,
            "total_time_ms": total_time_ms,
            "matched_keywords": matched_kw,
            "missing_keywords": [kw for kw in expected_keywords if kw not in matched_kw],
            "hit_forbidden": hit_forbidden,
            "answer_preview": answer_text[:400] + "...",
        })
        await asyncio.sleep(2.0)

    with open(OUTPUT_REPORT, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print("\n" + "=" * 95)
    print("   TỔNG KẾT 4 TEST CASES CÔ LẬP:")
    passed_count = sum(1 for r in results if r["passed"])
    print(f"   Kết quả: {passed_count}/{len(results)} PASS ({passed_count/len(results)*100:.1f}%)")
    for r in results:
        print(f"   - {r['id']}: {r['status']} | Ctx: {r['context_length_chars']:,} chars | TTFT: {r['ttft_ms']}ms | Total: {r['total_time_ms']}ms")
    print("=" * 95)

    retriever.close()


if __name__ == "__main__":
    asyncio.run(run_targeted_eval())
