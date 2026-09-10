import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
import os
import json
import time
from pathlib import Path
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
load_dotenv(PROJECT_ROOT / ".env")

from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels
from backend.app.services.rag.embeddings import get_embedding_service

CHUNKS_FILE = PROJECT_ROOT / "data" / "03_parsed" / "traffic_p2_batch" / "traffic_p2_chunks.json"

def ingest_staging():
    print("=" * 80)
    print("   INGESTING TRAFFIC P2 CHUNKS INTO QDRANT STAGING")
    print("=" * 80)

    # 1. Connect to Qdrant Cloud
    q_url = os.getenv("QDRANT_URL")
    q_key = os.getenv("QDRANT_API_KEY")
    client = QdrantClient(url=q_url, api_key=q_key)

    prod_coll = "vietlegal_articles"
    staging_coll = "vietlegal_articles_staging"

    prod_count_initial = client.get_collection(prod_coll).points_count
    staging_count_initial = client.get_collection(staging_coll).points_count
    print(f"[*] Initial Production '{prod_coll}' count: {prod_count_initial}")
    print(f"[*] Initial Staging '{staging_coll}' count: {staging_count_initial}")

    assert prod_count_initial == 7658, f"GATE FAIL: Production must be 7658, found {prod_count_initial}"

    # 2. Load chunks
    with open(CHUNKS_FILE, "r", encoding="utf-8") as f:
        chunks = json.load(f)
    print(f"[*] Loaded {len(chunks)} chunks to ingest.")

    # 3. Compute Embeddings with BAAI/bge-m3
    print("\n[*] Initializing BAAI/bge-m3 embedding service...")
    embedder = get_embedding_service()
    assert embedder.dimension == 1024, f"Expected 1024 dimensions, got {embedder.dimension}"

    texts_to_embed = [c["full_search_text"] for c in chunks]
    print(f"[*] Embedding {len(texts_to_embed)} chunks on GPU/CUDA...")
    t0 = time.time()
    vectors = embedder.embed_texts(texts_to_embed)
    embed_time = time.time() - t0
    print(f"[+] Computed {len(vectors)} vectors in {embed_time:.2f}s!")

    # 4. Prepare Qdrant Points
    points = []
    for c, vec in zip(chunks, vectors):
        point_id = c["chunk_id"]
        payload = {
            "chunk_id": c["chunk_id"],
            "document_id": c["document_id"],
            "doc_id": c["doc_id"],
            "official_number": c["official_number"],
            "doc_title": c["doc_title"],
            "canonical_provision_id": c["canonical_provision_id"],
            "version_id": c["version_id"],
            "unit_type": c["unit_type"],
            "article_number": c["article_number"],
            "clause_number": c["clause_number"],
            "point_number": c["point_number"],
            "annex_number": c["annex_number"],
            "chapter": c.get("chapter"),
            "chapter_title": c.get("chapter_title"),
            "article_title": c.get("article_title"),
            "effective_date": c["effective_date"],
            "valid_from": c["valid_from"],
            "valid_to": c["valid_to"],
            "valid_interval": c["valid_interval"],
            "legal_status": c["legal_status"],
            "scope_tags": c.get("scope_tags", []),
            "source_url": c["source_url"],
            "source_hash": c["source_hash"],
            "authority_delegation": c.get("authority_delegation"),
            "procedural_overlay": c.get("procedural_overlay"),
            "amendment_source": c.get("amendment_source"),
            "context_header": c["context_header"],
            "content": c["content"],
            "full_search_text": c["full_search_text"],
            "batch": "TRAFFIC_P2"
        }
        points.append(qmodels.PointStruct(id=point_id, vector=vec, payload=payload))

    # 5. Upsert into staging in batches
    batch_size = 50
    print(f"\n[*] Upserting {len(points)} points into '{staging_coll}' in batches of {batch_size}...")
    for i in range(0, len(points), batch_size):
        batch = points[i:i+batch_size]
        client.upsert(collection_name=staging_coll, points=batch)
        print(f"    [+] Uploaded batch {i//batch_size + 1} ({len(batch)} points)")

    time.sleep(1) # Allow indexing
    staging_count_final = client.get_collection(staging_coll).points_count
    prod_count_final = client.get_collection(prod_coll).points_count

    print("\n" + "=" * 80)
    print(f"[*] Staging count AFTER ingestion:    {staging_count_final} (+{staging_count_final - staging_count_initial})")
    print(f"[*] Production count (MUST BE 7658): {prod_count_final} (untouched: {prod_count_final == 7658})")
    print("=" * 80)

    assert prod_count_final == 7658, "CRITICAL: Production collection was mutated!"
    assert staging_count_final == staging_count_initial + len(points), f"Expected staging to have {staging_count_initial + len(points)}, got {staging_count_final}"

    report = {
        "production_collection": prod_coll,
        "staging_collection": staging_coll,
        "production_points_before": prod_count_initial,
        "production_points_after": prod_count_final,
        "staging_points_before": staging_count_initial,
        "staging_points_after": staging_count_final,
        "points_ingested": len(points),
        "production_untouched": True,
        "status": "PASS"
    }

    report_file = PROJECT_ROOT / "data" / "03_parsed" / "traffic_p2_batch" / "qdrant_staging_report.json"
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(f"[+] Saved staging report to {report_file}")
    return report

if __name__ == "__main__":
    ingest_staging()
