import os
import sys
import time
import json
import asyncio
from pathlib import Path
from datetime import datetime

# Windows encoding fix
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from dotenv import load_dotenv
load_dotenv(PROJECT_ROOT / ".env")

from backend.app.services.rag.retriever import HybridRetriever
from backend.app.services.rag.reranker import get_reranker_service
from backend.app.services.rag.generator import LegalAnswerGenerator

CASES_PATH = PROJECT_ROOT / "data" / "qa" / "realworld_qa_cases.json"
RESULTS_PATH = PROJECT_ROOT / "data" / "qa" / "realworld_qa_results.json"

print("=" * 80)
print("STEP 3.1 — REAL-WORLD QA EXECUTION & VALIDATION")
print("=" * 80)

# Initialize singletons
print("[*] Initializing HybridRetriever and Reranker (CUDA FP16)...")
retriever = HybridRetriever()
reranker = get_reranker_service()
reranker._ensure_loaded()
generator = LegalAnswerGenerator()
print("[+] Services loaded successfully.")

with open(CASES_PATH, "r", encoding="utf-8") as f:
    cases = json.load(f)
print(f"Loaded {len(cases)} real-world QA cases.")

async def run_single_case(tc, idx, total):
    cid = tc["id"]
    qtype = tc["type"]
    query = tc["query"]
    print(f"\n[{idx:02d}/{total}] {cid} ({qtype})")
    print(f"  Q: {query}")

    t0_ret = time.perf_counter()
    # 1. Clean Hybrid Retrieval (Dense 1.0 + Sparse 0.10, top 10 candidates)
    candidates = retriever.retrieve(query=query, top_k=10, use_reranker=False)
    t1_ret = time.perf_counter()
    ret_ms = (t1_ret - t0_ret) * 1000

    t0_rr = time.perf_counter()
    # 2. Cross-Encoder Reranker
    reranked = reranker.rerank(query=query, candidates=candidates, top_k=5)
    t1_rr = time.perf_counter()
    rr_ms = (t1_rr - t0_rr) * 1000

    # 3. LLM Generation
    t0_gen = time.perf_counter()
    tokens = []
    error_msg = None
    retries = 3
    for attempt in range(retries):
        try:
            tokens = []
            async for tok in generator.generate_answer_stream(query=query, retrieved_chunks=reranked):
                tokens.append(tok)
            break
        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg or "quota" in error_msg.lower():
                wait_sec = 5.0 * (attempt + 1)
                print(f"  [!] Rate limit hit (429), backoff {wait_sec}s...")
                await asyncio.sleep(wait_sec)
            else:
                await asyncio.sleep(2.0)
    t1_gen = time.perf_counter()
    gen_ms = (t1_gen - t0_gen) * 1000
    total_ms = ret_ms + rr_ms + gen_ms

    full_answer = "".join(tokens).strip()
    if not full_answer:
        full_answer = f"[ERROR: {error_msg}]"

    # Extract citations
    import re
    citations = set()
    art_matches = re.findall(r"Điều\s+\d+[\w\s]*(?:Luật|Bộ luật|Nghị định|Thông tư)\s+[^\n.,;()]+", full_answer, re.IGNORECASE)
    for am in art_matches:
        citations.add(am.strip())
    doc_matches = re.findall(r"(?:Luật|Nghị định|Thông tư|Bộ luật)\s+(?:số\s+)?[\d/]+(?:/[A-ZĐ-]+)?", full_answer, re.IGNORECASE)
    for dm in doc_matches:
        citations.add(dm.strip())

    refusal_signals = [
        "chưa có quy định", "không có quy định", "không có trong ngữ cảnh",
        "không chứa thông tin", "chưa chứa thông tin", "không đủ thông tin",
        "chưa đủ thông tin", "chưa có đủ cơ sở pháp lý", "ngoài phạm vi",
        "cơ sở dữ liệu chưa có", "không có trong cơ sở dữ liệu", "chưa có thông tin",
        "chưa có văn bản quy phạm"
    ]
    is_refusal = any(sig in full_answer.lower() for sig in refusal_signals)

    print(f"  Done in {total_ms/1000:.2f}s (Ret: {ret_ms:.0f}ms | Rerank: {rr_ms:.0f}ms | Gen: {gen_ms/1000:.2f}s)")
    print(f"  Citations: {len(citations)} | Refusal: {is_refusal}")
    print(f"  Preview: {full_answer[:120].replace(chr(10), ' ')}...")

    return {
        "id": cid,
        "type": qtype,
        "query": query,
        "notes": tc.get("notes", ""),
        "retrieved_context": [
            {
                "doc_title": c.get("doc_title", ""),
                "article_number": c.get("article_number", ""),
                "article_title": c.get("article_title", ""),
                "score": round(float(c.get("rerank_score", c.get("score", 0.0))), 4)
            }
            for c in reranked
        ],
        "final_answer": full_answer,
        "citations": sorted(list(citations)),
        "is_refusal": is_refusal,
        "latency": {
            "retrieval_ms": round(ret_ms, 2),
            "reranker_ms": round(rr_ms, 2),
            "generation_ms": round(gen_ms, 2),
            "total_ms": round(total_ms, 2)
        }
    }

async def main():
    results = []
    total = len(cases)
    for i, tc in enumerate(cases):
        res = await run_single_case(tc, i + 1, total)
        results.append(res)
        await asyncio.sleep(2.0)  # quota safety

    RESULTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(RESULTS_PATH, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\n[+] Saved all {len(results)} results to: {RESULTS_PATH}")

if __name__ == "__main__":
    asyncio.run(main())
