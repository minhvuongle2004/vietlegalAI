import sys
sys.path.insert(0, ".")
from backend.app.services.rag.retriever import HybridRetriever

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

retriever = HybridRetriever()

queries = [
    ("TC-41", "Một cá nhân cư trú có thu nhập tính thuế từ tiền lương, tiền công trong tháng là 25 triệu đồng. Theo Biểu thuế luỹ tiến từng phần của Luật Thuế thu nhập cá nhân 2025 (Luật số 109/2025/QH15), số thuế TNCN phải nộp trong tháng được tính như thế nào và là bao nhiêu tiền?"),
    ("TC-47", "Doanh nghiệp kê khai phát sinh 50 triệu đồng thuế TNDN phải nộp nhưng quá hạn 10 ngày vẫn chưa nộp vào ngân sách nhà nước. Căn cứ Luật Thuế thu nhập doanh nghiệp 2025 và Luật Quản lý thuế 2025, doanh nghiệp có trách nhiệm nộp số thuế TNDN và tiền chậm nộp được tính như thế nào?")
]

for name, q in queries:
    print(f"\n================ {name} ================")
    sub_q = retriever.decompose_query(q)
    print(f"Sub-queries ({len(sub_q)}):")
    for sq in sub_q:
        print(f"  [{sq['category']} | {sq['doc_keyword']}]: {sq['sub_query'][:70]}...")
    results = retriever.retrieve(q, top_k=5, use_reranker=True)
    print("Retrieved top 5:")
    for r in results:
        print(f"  - {r.get('doc_id')}: Điều {r.get('article_number')} ({r.get('article_title')}) [RRF: {r.get('rrf_score', 0):.4f}]")
