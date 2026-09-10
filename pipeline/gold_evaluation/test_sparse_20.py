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

from backend.app.services.rag.retriever import HybridRetriever
from backend.app.services.rag.vector_store import QdrantVectorStore
from backend.app.services.rag.embeddings import get_embedding_service

retriever = HybridRetriever()

GOLD_DATASET_FILE = PROJECT_ROOT / "data" / "gold_evaluation" / "gold_retrieval_225_cases.json"
with open(GOLD_DATASET_FILE, "r", encoding="utf-8") as f:
    gold_data = json.load(f)
cases = gold_data["cases"]

# 20 representative cases:
# - 5 direct questions
# - 5 article retrieval
# - 5 temporal/amendment
# - 5 speed/lane/GPLX

direct_cases = [c for c in cases if c["category"] == "DIRECT_RULE"][:5]
article_cases = [c for c in cases if c["category"] == "ARTICLE_RETRIEVAL"][:5]
temporal_cases = [c for c in cases if c["category"] in ["TEMPORAL_QUERY", "AMENDMENT_LINEAGE"]][:5]
speed_lane_gplx_cases = [c for c in cases if any(k in c["query"].lower() for k in ["tốc độ", "làn", "gplx", "giấy phép lái xe"])][:5]

test_20 = direct_cases + article_cases + temporal_cases + speed_lane_gplx_cases
print(f"Total representative cases selected: {len(test_20)}")

for i, tc in enumerate(test_20, 1):
    q = tc["query"]
    cid = tc["test_case_id"]
    exp = tc["expected_evidence"]
    as_of = tc.get("as_of_date")
    
    sparse_results = retriever._sparse_search_bm25(q, limit=5, as_of_date=as_of)
    print(f"\n--- [{i}/20] {cid}: {q[:60]}... ---")
    print(f"  Expected: {exp.get('official_number')} | {exp.get('document_id')} | Điều {exp.get('article')}")
    print(f"  Sparse returned count: {len(sparse_results)}")
    for r_idx, res in enumerate(sparse_results[:5], 1):
        print(f"    Top {r_idx}: doc_id='{res.get('doc_id')}', official='{res.get('official_number')}', art={res.get('article_number')}, title='{res.get('article_title')[:30]}'")
