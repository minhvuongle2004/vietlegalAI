import os
import sys
import json
import time
import asyncio
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)

import torch
print(f"[*] GPU Acceleration Status: CUDA available={torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"[*] Active GPU: {torch.cuda.get_device_name(0)}")

from evals.profile_traffic_latency import ProfiledHybridRetriever, ProfiledLegalAnswerGenerator
from evals.run_smoke_regression import evaluate_case_correctness, evaluate_retrieval

async def run_targeted_rerun():
    print("=" * 90)
    print("   TARGETED RERUN VERIFICATION: TG-10 & TC-19")
    print("   Xác nhận giải quyết Evaluator Bug (TC-19) & Model Reliability (TG-10)")
    print("=" * 90)

    # 1. Load 2 test cases
    with open(PROJECT_ROOT / "evals" / "traffic_benchmark_10.json", "r", encoding="utf-8") as f:
        traffic_data = json.load(f)
    tg10 = next(t for t in traffic_data if t["id"] == "TG-10")
    tg10["domain_group"] = "Traffic Law (Giao thông đường bộ)"

    with open(PROJECT_ROOT / "evals" / "benchmark_56_phase3.json", "r", encoding="utf-8") as f:
        bench_data = json.load(f)
    tc19 = next(t for t in bench_data.get("details", []) if t["id"] == "TC-19")
    tc19["domain_group"] = "Core Benchmark (arithmetic_calculation)"

    target_cases = [tg10, tc19]

    # 2. Khởi tạo Retriever & Generator với GPU CUDA FP16
    retriever = ProfiledHybridRetriever()
    generator = ProfiledLegalAnswerGenerator()

    rerun_results = []

    for tc in target_cases:
        tc_id = tc["id"]
        title = tc.get("title", "")
        query = tc["query"]
        as_of_date = tc.get("law_as_of_date") or tc.get("as_of_date") or "2026-09-01"

        print(f"\n[+] Đang chạy Targeted Rerun: {tc_id} — {title}")
        
        # Retrieval
        ret_chunks = retriever.retrieve_with_profile(
            query=query,
            top_k=5,
            use_reranker=True,
            as_of_date=as_of_date,
            use_clause_extraction=True
        )
        r_stats = retriever.stats.copy()

        # Generation
        answer_text = ""
        async for token in generator.generate_answer_stream_profiled(query=query, retrieved_chunks=ret_chunks):
            answer_text += token
        g_stats = generator.gen_stats.copy()

        pure_pipeline_s = (r_stats["total_retrieval_ms"] + g_stats["total_gen_wall_clock_ms"] - g_stats["backoff_sleep_ms"]) / 1000.0

        corr = evaluate_case_correctness(answer_text, tc)
        ret_eval = evaluate_retrieval(ret_chunks, tc)
        is_passed = corr["pass"] and ret_eval["retrieval_pass"]

        res_entry = {
            "id": tc_id,
            "title": title,
            "pure_pipeline_s": round(pure_pipeline_s, 2),
            "reranker_s": round(r_stats["reranker_ms"] / 1000, 2),
            "context_chars": g_stats["context_chars"],
            "input_tokens": g_stats["context_tokens_approx"],
            "retrieval_pass": ret_eval["retrieval_pass"],
            "correctness_pass": corr["pass"],
            "status": "PASSED" if is_passed else "FAILED",
            "matched_expected": corr["matched_expected"],
            "missing_expected": corr["missing_expected"],
            "answer_preview": answer_text[:300] + "..."
        }
        rerun_results.append(res_entry)

        status_tag = "✅ PASSED" if is_passed else "❌ FAILED"
        print(f"    --> Kết Quả: {status_tag} | Pure Pipeline={res_entry['pure_pipeline_s']}s (Reranker={res_entry['reranker_s']}s) | Context={res_entry['context_chars']:,} chars")
        print(f"    --> Retrieval: {'✅ PASS' if ret_eval['retrieval_pass'] else '❌ FAIL'} | Correctness: {'✅ PASS' if corr['pass'] else '❌ FAIL'}")
        if not is_passed:
            print(f"    --> Missing: {corr['missing_expected']}")

    print("\n" + "=" * 90)
    print("   TỔNG KẾT TARGETED RERUN")
    print("=" * 90)
    for r in rerun_results:
        print(f"   [{r['id']}] {r['title']}: {r['status']} (Pipeline={r['pure_pipeline_s']}s, Reranker={r['reranker_s']}s)")
    
    # Lưu file kết quả targeted rerun
    out_file = PROJECT_ROOT / "evals" / "targeted_rerun_results.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(rerun_results, f, ensure_ascii=False, indent=2)
    print(f"\n[+] Đã lưu kết quả tại: {out_file}")

if __name__ == "__main__":
    asyncio.run(run_targeted_rerun())
