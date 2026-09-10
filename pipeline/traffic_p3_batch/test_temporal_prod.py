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

def test():
    store = QdrantVectorStore(collection_name="vietlegal_articles")
    embedder = get_embedding_service()

    with open(PROJECT_ROOT / "data" / "03_parsed" / "traffic_p0_5_batch" / "benchmark_25_cases.json", encoding="utf-8") as f:
        cases = json.load(f)["cases"]

    for idx, tc in enumerate(cases, 1):
        cid = tc["test_case_id"]
        if cid in ["TC-DOM-GPLX-01", "TC-DOM-CONTRAST-01A"]:
            q = tc["query"]
            as_of = tc["as_of_date"]
            vec = embedder.embed_texts([q])[0]
            hits = store.search_similar(query_vector=vec, limit=5, as_of_date=as_of)
            print(f"\n{cid} (as_of={as_of}):")
            for r, h in enumerate(hits, 1):
                sc = h.get("score")
                sc_str = f"{sc:.4f}" if sc is not None else "None"
                print(f"  Rank {r} (score={sc_str}): {h.get('doc_id')} {h.get('official_number')} Điều {h.get('article_number')}")

if __name__ == "__main__":
    test()
