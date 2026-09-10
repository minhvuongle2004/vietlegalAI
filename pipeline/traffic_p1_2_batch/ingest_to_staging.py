import sys
import os
import json
import time
import uuid
from pathlib import Path
from typing import List, Dict, Any

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels
from backend.app.services.rag.embeddings import get_embedding_service

CLOUD_URL = "https://69f07c1e-2e88-452f-aded-6dd577ddbd9b.us-west-2-0.aws.cloud.qdrant.io"
CLOUD_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIiwic3ViamVjdCI6ImFwaS1rZXk6OTAxNjk0MzUtYjMwMS00YjAzLWFmMGYtYmYyZjc0MWE4MjYxIn0.bJ2YtMtnmDJXN4k3FKdduN_TsLARSOAvGjBRKW3p028"

STAGING_COLLECTION = "vietlegal_articles_staging"
PROD_COLLECTION = "vietlegal_articles"

CHUNKS_FILE = PROJECT_ROOT / "data" / "03_parsed" / "traffic_p1_2_batch" / "all_traffic_p1_2_chunks.json"

def main():
    print("=" * 80)
    print("   TRAFFIC P1.2: INGESTION TO QDRANT STAGING COLLECTION")
    print("=" * 80)

    if not CHUNKS_FILE.exists():
        raise FileNotFoundError(f"Missing {CHUNKS_FILE}")

    with open(CHUNKS_FILE, "r", encoding="utf-8") as f:
        chunks: List[Dict[str, Any]] = json.load(f)

    print(f"[*] Loaded {len(chunks)} semantic chunks from {CHUNKS_FILE.name}")

    # 1. Connect to Qdrant Cloud
    client = QdrantClient(url=CLOUD_URL, api_key=CLOUD_API_KEY, timeout=15.0)
    print(f"[+] Connected to Qdrant Cloud: {CLOUD_URL}")

    # Verify Production point count before touching staging
    prod_points_before = client.get_collection(PROD_COLLECTION).points_count
    print(f"[SAFETY CHECK] Production Collection '{PROD_COLLECTION}' Points: {prod_points_before}")
    if prod_points_before != 7495:
        print(f"[WARNING] Production points count is {prod_points_before} (expected 7495)!")

    # 2. Check Staging Collection
    colls = [c.name for c in client.get_collections().collections]
    existing_staging_count = 0
    if STAGING_COLLECTION in colls:
        existing_staging_count = client.get_collection(STAGING_COLLECTION).points_count
        print(f"[*] Found existing staging collection '{STAGING_COLLECTION}' with {existing_staging_count} points.")

    if existing_staging_count != prod_points_before:
        if STAGING_COLLECTION in colls:
            print(f"[*] Deleting existing staging collection '{STAGING_COLLECTION}' to reset clone...")
            client.delete_collection(STAGING_COLLECTION)

        print(f"[*] Creating Staging collection '{STAGING_COLLECTION}' (size=1024, distance=Cosine)...")
        client.create_collection(
            collection_name=STAGING_COLLECTION,
            vectors_config=qmodels.VectorParams(
                size=1024,
                distance=qmodels.Distance.COSINE
            )
        )

        # 3. Create Payload Indexes on Staging
        indexed_fields = [
            "doc_id", "article_number", "status", "official_number",
            "legal_status", "ingestion_status", "document_role",
            "current_retrieval_eligible", "primary_current_core"
        ]
        for field in indexed_fields:
            try:
                client.create_payload_index(
                    collection_name=STAGING_COLLECTION,
                    field_name=field,
                    field_schema=qmodels.PayloadSchemaType.KEYWORD
                )
            except Exception as e:
                print(f"Index notice for {field}: {e}")

        print(f"[+] Staging collection initialized with {len(indexed_fields)} payload indices.")

        # 4. Clone ALL 7,495 Production points into Staging
        print("\n" + "=" * 80, flush=True)
        print(f"[*] STEP 1: CLONING {prod_points_before} PRODUCTION POINTS INTO COMBINED STAGING...", flush=True)
        print("=" * 80, flush=True)
        
        scroll_offset = None
        copied_prod_points = 0
        clone_batch_size = 250
        t_clone_0 = time.time()
        batch_num = 0

        while True:
            batch_num += 1
            records, next_offset = client.scroll(
                collection_name=PROD_COLLECTION,
                limit=clone_batch_size,
                offset=scroll_offset,
                with_payload=True,
                with_vectors=True
            )
            if not records:
                break

            # Convert records to PointStruct
            staging_batch = [
                qmodels.PointStruct(
                    id=r.id,
                    vector=r.vector,
                    payload=r.payload
                )
                for r in records
            ]
            client.upsert(collection_name=STAGING_COLLECTION, points=staging_batch)
            copied_prod_points += len(staging_batch)
            print(f" [Batch {batch_num:2d}] Cloned {copied_prod_points}/{prod_points_before} points (offset: {str(next_offset)[:8]}...)", flush=True)

            if next_offset is None:
                break
            scroll_offset = next_offset

        t_clone_1 = time.time()
        print(f"[+] Successfully cloned {copied_prod_points} production points into staging in {t_clone_1 - t_clone_0:.2f}s!", flush=True)
    else:
        print(f"[+] Staging already contains exactly {existing_staging_count} production points. Skipping clone step!", flush=True)

    # 5. Generate Embeddings for P1.2 Chunks using BGE-M3
    print("\n" + "=" * 80, flush=True)
    print(f"[*] STEP 2: EMBEDDING & UPSERTING {len(chunks)} P1.2 POINTS...", flush=True)
    print("=" * 80, flush=True)
    print("[*] Initializing Embedding Service (BGE-M3)...", flush=True)
    embedder = get_embedding_service()
    texts_to_embed = [c["text"] for c in chunks]

    t0 = time.time()
    print(f"[*] Computing embeddings for {len(texts_to_embed)} chunks on GPU...", flush=True)
    vectors = embedder.embed_texts(texts_to_embed, batch_size=16)
    t1 = time.time()
    print(f"[+] Successfully generated {len(vectors)} vectors in {t1 - t0:.2f}s! Vector dimension: {len(vectors[0])}", flush=True)

    # 6. Build P1.2 Points for Qdrant
    p1_2_points = []
    for c, vec in zip(chunks, vectors):
        point_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, c["chunk_id"]))

        is_active = c["effective_from"] <= "2026-09-10"
        status_value = "CON_HIEU_LUC" if is_active else "CHUA_HIEU_LUC"

        payload = {
            "chunk_id": c["chunk_id"],
            "doc_id": c["document_id"],
            "doc_title": c["title"],
            "official_number": c["official_number"],
            "chapter": c["chapter"],
            "section": c.get("section"),
            "article_number": c["article"],
            "article_title": c["article_title"],
            "clause_number": c["clause"],
            "point_letter": c.get("point"),
            "status": status_value,
            "legal_status": c["legal_status"],
            "ingestion_status": c["ingestion_status"],
            "document_role": c["document_role"],
            "source_status": c["source_status"],
            "normalized_status": c["normalized_status"],
            "current_retrieval_eligible": c["current_retrieval_eligible"],
            "primary_current_core": c["primary_current_core"],
            "effective_date": c["effective_from"],
            "expiry_date": c.get("effective_until"),
            "context_header": f"[{c['official_number']} - {c['chapter']} - {c['article']}: {c['article_title']} - {c['clause']}]",
            "content": c["text"],
            "full_search_text": c["text"],
            "scope_tags": [c["document_id"], c["official_number"].replace("/", "_").lower()],
            "relations": c.get("relations", {}),
            "word_count": c["word_count"],
            "source_url": c["source_url"],
            "source_hash": c["source_hash"],
            "ingestion_batch": "traffic_p1_2_batch"
        }

        p1_2_points.append(qmodels.PointStruct(
            id=point_id,
            vector=vec,
            payload=payload
        ))

    # 7. Upload P1.2 Points to Staging in batches
    print(f"\n[*] Uploading {len(p1_2_points)} P1.2 points to Staging collection...", flush=True)
    batch_size = 50
    total_p1_2_uploaded = 0
    t_upload_0 = time.time()

    for i in range(0, len(p1_2_points), batch_size):
        batch = p1_2_points[i : i + batch_size]
        client.upsert(collection_name=STAGING_COLLECTION, points=batch)
        total_p1_2_uploaded += len(batch)
        print(f" [+] Uploaded {total_p1_2_uploaded}/{len(p1_2_points)} P1.2 points...", flush=True)

    t_upload_1 = time.time()
    print(f"[+] Upload of P1.2 points completed in {t_upload_1 - t_upload_0:.2f}s!", flush=True)

    # 8. Verify Combined Staging and Production point counts
    staging_count = client.get_collection(STAGING_COLLECTION).points_count
    prod_count_after = client.get_collection(PROD_COLLECTION).points_count
    expected_combined_count = prod_points_before + len(chunks)

    print("\n" + "=" * 80, flush=True)
    print("   COMBINED STAGING INGESTION VERIFICATION", flush=True)
    print("=" * 80, flush=True)
    print(f"Production Points (Original):     {prod_points_before}", flush=True)
    print(f"P1.2 Batch Points:                {len(chunks)}", flush=True)
    print(f"Combined Staging Expected Total:  {expected_combined_count}", flush=True)
    print(f"Combined Staging Actual Total:    {staging_count}", flush=True)
    print(f"Production Points (After Run):    {prod_count_after} (Unchanged: {prod_count_after == prod_points_before})", flush=True)
    print("=" * 80, flush=True)

    if staging_count != expected_combined_count:
        raise ValueError(f"Combined Staging count mismatch! Expected {expected_combined_count}, got {staging_count}")
    if prod_count_after != prod_points_before:
        raise ValueError("FATAL: Production points count was altered during staging ingestion!")

    print("[SUCCESS] Combined Staging created successfully with 7,658 points! Production remains intact (7,495 points).")

if __name__ == "__main__":
    main()
