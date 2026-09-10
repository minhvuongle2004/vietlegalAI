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

from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels
from backend.app.services.rag.embeddings import get_embedding_service

POINT_ID = "5234572f-a76e-504c-9348-5f33c2763293"
STAGING_COLLECTION = "vietlegal_articles_staging"
BENCHMARK_FILE = PROJECT_ROOT / "data" / "03_parsed" / "traffic_p0_5_batch" / "benchmark_25_cases.json"

def run_test():
    client = QdrantClient(url=os.getenv("QDRANT_URL"), api_key=os.getenv("QDRANT_API_KEY"))
    embedder = get_embedding_service()

    # 1. Retrieve current point from staging
    pts = client.retrieve(collection_name=STAGING_COLLECTION, ids=[POINT_ID], with_payload=True)
    if not pts:
        print(f"ERROR: Point {POINT_ID} not found in staging!")
        return
    orig_point = pts[0]
    orig_payload = orig_point.payload.copy()

    # 2. Prepare enhanced representation (Candidate K1)
    enhanced_text = (
        "[12/2025/TT-BCA - Điều 14: Nội dung sát hạch lái xe ô tô] "
        "Thí sinh dự sát hạch lái xe ô tô theo Thông tư 12 có bài thi mô phỏng, bắt buộc trải qua 4 nội dung: "
        "(1) Sát hạch lý thuyết; "
        "(2) Sát hạch lái xe mô phỏng tình huống giao thông; "
        "(3) Sát hạch thực hành trong hình; "
        "(4) Sát hạch thực hành trên đường."
    )
    new_vec = embedder.embed_texts([enhanced_text])[0]
    updated_payload = orig_payload.copy()
    updated_payload["content"] = (
        "Thí sinh dự sát hạch lái xe ô tô theo Thông tư 12 có bài thi mô phỏng, bắt buộc trải qua 4 nội dung: "
        "(1) Sát hạch lý thuyết; "
        "(2) Sát hạch lái xe mô phỏng tình huống giao thông; "
        "(3) Sát hạch thực hành trong hình; "
        "(4) Sát hạch thực hành trên đường."
    )
    updated_payload["full_search_text"] = enhanced_text

    # 3. Upsert into staging
    client.upsert(
        collection_name=STAGING_COLLECTION,
        points=[
            qmodels.PointStruct(
                id=POINT_ID,
                vector=new_vec,
                payload=updated_payload
            )
        ]
    )
    print(f"[+] Successfully updated point {POINT_ID} in {STAGING_COLLECTION}")

    # 4. Run all 25 baseline cases on staging
    with open(BENCHMARK_FILE, "r", encoding="utf-8") as f:
        cases = json.load(f)["cases"]

    hit1 = 0
    hit2 = 0
    hit3 = 0

    print("\n" + "=" * 90)
    print("   EVALUATION RESULTS ON STAGING ACROSS ALL 25 BASELINE CASES")
    print("=" * 90)

    for idx, tc in enumerate(cases, 1):
        cid = tc["test_case_id"]
        q = tc["query"]
        expected_docs = [d.lower() for d in tc["expected_documents"]]

        q_vec = embedder.embed_query(q)
        res = client.query_points(
            collection_name=STAGING_COLLECTION,
            query=q_vec,
            limit=5,
            with_payload=True
        )
        hits = res.points

        hit_rank = None
        for r, pt in enumerate(hits, 1):
            pld = pt.payload
            doc_id = str(pld.get("doc_id", "") or "").lower()
            off_num = str(pld.get("official_number", "") or "").lower()
            title = str(pld.get("doc_title", "") or "").lower()

            if any(exp in doc_id or exp in off_num or exp in title for exp in expected_docs):
                if hit_rank is None:
                    hit_rank = r

        if hit_rank == 1:
            hit1 += 1
            hit2 += 1
            hit3 += 1
            status_str = "🟢 HIT@1"
        elif hit_rank == 2:
            hit2 += 1
            hit3 += 1
            status_str = "🟡 HIT@2"
        elif hit_rank == 3:
            hit3 += 1
            status_str = "🟡 HIT@3"
        else:
            status_str = f"🔴 MISS (Rank {hit_rank})"

        top1_pld = hits[0].payload if hits else {}
        top1_str = f"{top1_pld.get('official_number')} {top1_pld.get('article_number')}"
        score1 = hits[0].score if hits else 0.0

        print(f"[{idx:02d}/25] {status_str:14} {cid:22} | Rank: {str(hit_rank):4} | Top 1: {top1_str:25} (score={score1:.4f})")
        if hit_rank != 1:
            for r, h in enumerate(hits[:3], 1):
                p = h.payload
                print(f"       Candidate #{r} (score={h.score:.4f}): {p.get('official_number')} {p.get('article_number')}")

    total = len(cases)
    print("-" * 90)
    print(f"SUMMARY ON STAGING:")
    print(f"  Hit@1: {hit1}/{total} ({hit1/total*100:.1f}%) [Target: >=92.0%]")
    print(f"  Hit@2: {hit2}/{total} ({hit2/total*100:.1f}%) [Target: 100.0%]")
    print(f"  Hit@3: {hit3}/{total} ({hit3/total*100:.1f}%) [Target: 100.0%]")
    print("=" * 90)

if __name__ == "__main__":
    run_test()
