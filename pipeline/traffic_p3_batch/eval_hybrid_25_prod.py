import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
import os
import json
from pathlib import Path
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
load_dotenv(PROJECT_ROOT / ".env")

from backend.app.services.rag.embeddings import get_embedding_service
from backend.app.services.rag.vector_store import QdrantVectorStore
from backend.app.services.rag.retriever import HybridRetriever

def eval_all():
    store = QdrantVectorStore(collection_name="vietlegal_articles")
    embedder = get_embedding_service()
    retriever = HybridRetriever(vector_store=store, embedding_service=embedder)

    with open(PROJECT_ROOT / "data" / "03_parsed" / "traffic_p0_5_batch" / "benchmark_25_cases.json", encoding="utf-8") as f:
        cases = json.load(f)["cases"]

    hit1 = 0
    hit2 = 0
    hit3 = 0

    print("=" * 80)
    print("   25 BASELINE CASES EVALUATION VIA HYBRID RETRIEVER ON PRODUCTION")
    print("=" * 80)

    for idx, tc in enumerate(cases, 1):
        cid = tc["test_case_id"]
        q = tc["query"]
        as_of = tc.get("as_of_date")
        exp = [d.lower() for d in tc["expected_documents"]]

        hits = retriever.retrieve(query=q, as_of_date=as_of, top_k=5)
        rank = None
        for r, h in enumerate(hits, 1):
            doc_id = str(h.get("doc_id", "") or "").lower()
            off_num = str(h.get("official_number", "") or "").lower()
            title = str(h.get("doc_title", "") or "").lower()
            if any(e in doc_id or e in off_num or e in title for e in exp):
                rank = r
                break

        if rank == 1:
            hit1 += 1
            hit2 += 1
            hit3 += 1
            status = "PASS (Hit@1)"
        elif rank == 2:
            hit2 += 1
            hit3 += 1
            status = "PASS (Hit@2)"
        elif rank == 3:
            hit3 += 1
            status = "PASS (Hit@3)"
        else:
            status = f"MISS (Rank: {rank})"

        top1 = hits[0] if hits else {}
        top1_doc = top1.get("doc_id") or top1.get("official_number")
        print(f"[{idx:02d}/25] [{status:14}] {cid:20} | as_of={as_of} | Top 1: {top1_doc} Điều {top1.get('article_number')}")

    print("-" * 80)
    print(f"Total: 25 | Hit@1: {hit1}/25 ({hit1/25*100:.1f}%) | Hit@2: {hit2}/25 ({hit2/25*100:.1f}%) | Hit@3: {hit3}/25 ({hit3/25*100:.1f}%)")
    print("=" * 80)

if __name__ == "__main__":
    eval_all()
