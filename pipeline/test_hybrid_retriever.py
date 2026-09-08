import sys
import io
import asyncio
from pathlib import Path

# Đảm bảo UTF-8 cho Windows console
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.services.rag.retriever import HybridRetriever
from backend.app.services.rag.generator import LegalAnswerGenerator


async def main():
    print("=" * 70)
    print("   VIETLEGAL AI - TEST TRUY VẤN KẾT HỢP (HYBRID SEARCH & RAG)")
    print("=" * 70)

    retriever = HybridRetriever()
    generator = LegalAnswerGenerator()

    test_questions = [
        "Người lao động thử việc tối đa bao nhiêu ngày?",
        "Bị sa thải hoặc đuổi việc vô lý thì công ty phải đền tiền thế nào?",
    ]

    for question in test_questions:
        print("\n" + "-" * 70)
        print(f"❓ CÂU HỎI: \"{question}\"")
        print("-" * 70)

        # 1. Truy xuất thông tin (Hybrid Search: Qdrant + Supabase)
        print("[*] Đang tìm kiếm kết hợp (Dense Vector Qdrant + Sparse BM25 Supabase)...")
        results = retriever.retrieve(query=question, top_k=3)

        print(f"[+] Tìm thấy {len(results)} căn cứ pháp lý liên quan nhất:")
        for rank, r in enumerate(results, start=1):
            print(f"  [{rank}] Điều {r['article_number']}: {r['article_title']} (Điểm RRF: {r['rrf_score']:.4f})")
            print(f"      Ngữ cảnh: {r['context_header']}")

        # 2. Sinh câu trả lời (LLM Answer Generation)
        print("\n🤖 TRỢ LÝ VIETLEGAL AI TRẢ LỜI:")
        print("--------------------------------------------------")
        async for token in generator.generate_answer_stream(query=question, retrieved_chunks=results):
            print(token, end="", flush=True)
        print("\n--------------------------------------------------\n")

    retriever.close()


if __name__ == "__main__":
    asyncio.run(main())
