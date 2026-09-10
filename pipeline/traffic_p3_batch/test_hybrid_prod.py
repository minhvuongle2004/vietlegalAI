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

def test():
    store = QdrantVectorStore(collection_name="vietlegal_articles")
    embedder = get_embedding_service()
    retriever = HybridRetriever(vector_store=store, embedding_service=embedder)

    with open(PROJECT_ROOT / "data" / "03_parsed" / "traffic_p0_5_batch" / "benchmark_25_cases.json", encoding="utf-8") as f:
        cases = json.load(f)["cases"]

    for cid_target in ["TC-DOM-GPLX-01", "TC-DOM-CONTRAST-01A", "TC-DOM-CONTRAST-01B"]:
        tc = [c for c in cases if c["test_case_id"] == cid_target][0]
        q = tc["query"]
        as_of = tc["as_of_date"]
        hits = retriever.retrieve(query=q, as_of_date=as_of, top_k=5)
        print(f"\n{cid_target} (as_of={as_of}):")
        for r, h in enumerate(hits, 1):
            doc_id = h.get("doc_id")
            off = h.get("official_number")
            art = h.get("article_number")
            print(f"  Rank {r}: doc_id={doc_id} | off={off} | Điều {art}")

if __name__ == "__main__":
    test()
