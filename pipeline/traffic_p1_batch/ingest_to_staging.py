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

CHUNKS_FILE = PROJECT_ROOT / "data" / "03_parsed" / "traffic_p1_batch" / "all_traffic_p1_chunks.json"

def main():
    print("=" * 80)
    print("   TRAFFIC P1: CONTROLLED INGESTION TO QDRANT STAGING COLLECTION")
    print("=" * 80)

    if not CHUNKS_FILE.exists():
        raise FileNotFoundError(f"Missing {CHUNKS_FILE}")

    with open(CHUNKS_FILE, "r", encoding="utf-8") as f:
        chunks: List[Dict[str, Any]] = json.load(f)

    print(f"[*] Loaded {len(chunks)} semantic chunks from {CHUNKS_FILE.name}")

    # 1. Connect to Qdrant Cloud
    client = QdrantClient(url=CLOUD_URL, api_key=CLOUD_API_KEY, timeout=15.0)
    print(f"[+] Connected to Qdrant Cloud: {CLOUD_URL}")

    # 2. Ensure Staging Collection exists and clean
    colls = [c.name for c in client.get_collections().collections]
    if STAGING_COLLECTION in colls:
        print(f"[*] Deleting existing staging collection '{STAGING_COLLECTION}' to ensure clean slate...")
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
            print(f"Index error for {field}: {e}")

    print(f"[+] Staging collection initialized with {len(indexed_fields)} payload indices.")

    # 4. Generate Embeddings using BGE-M3
    print("\n[*] Initializing Embedding Service (BGE-M3)...")
    embedder = get_embedding_service()
    texts_to_embed = [c["text"] for c in chunks]

    t0 = time.time()
    print(f"[*] Computing embeddings for {len(texts_to_embed)} chunks on GPU...")
    vectors = embedder.embed_texts(texts_to_embed, batch_size=16)
    t1 = time.time()
    print(f"[+] Successfully generated {len(vectors)} vectors in {t1 - t0:.2f}s! Vector dimension: {len(vectors[0])}")

    # 5. Build Points for Qdrant
    points = []
    for c, vec in zip(chunks, vectors):
        point_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, c["chunk_id"]))
        
        # Determine standard status
        is_active = c["effective_from"] <= "2026-09-10"
        status_value = "CON_HIEU_LUC" if is_active else "CHUA_HIEU_LUC"
        if c.get("effective_until") and c["effective_until"] <= "2026-09-10":
            status_value = "HET_HIEU_LUC"
            
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
            "ingestion_batch": "traffic_p1_batch"
        }
        
        points.append(qmodels.PointStruct(
            id=point_id,
            vector=vec,
            payload=payload
        ))

    # 6. Upload to Staging in batches
    print(f"\n[*] Uploading {len(points)} points to Staging collection in batches of 50...")
    batch_size = 50
    total_uploaded = 0
    t_upload_0 = time.time()
    
    for i in range(0, len(points), batch_size):
        batch = points[i : i + batch_size]
        client.upsert(collection_name=STAGING_COLLECTION, points=batch)
        total_uploaded += len(batch)
        print(f" [+] Uploaded {total_uploaded}/{len(points)} points...")
        
    t_upload_1 = time.time()
    print(f"[+] Ingestion to Staging completed in {t_upload_1 - t_upload_0:.2f}s!")

    # 7. Verification on Staging
    info = client.get_collection(STAGING_COLLECTION)
    print("\n" + "=" * 80)
    print("   STAGING COLLECTION INGESTION VERIFICATION")
    print("=" * 80)
    print(f"Collection Name:     {STAGING_COLLECTION}")
    print(f"Points Count:        {info.points_count} (Expected: {len(chunks)})")
    print(f"Vector Dimensions:   {info.config.params.vectors.size}")
    print(f"Distance Metric:     {info.config.params.vectors.distance}")
    
    if info.points_count == len(chunks):
        print("🟢 100% POINTS INGESTED & VERIFIED ON STAGING COLLECTION!")
    else:
        print(f"🔴 MISMATCH: Expected {len(chunks)}, found {info.points_count}")

    # Verify Production Collection is untouched
    prod_info = client.get_collection("vietlegal_articles")
    print("\n" + "-" * 80)
    print(f"PRODUCTION COLLECTION INTEGRITY CHECK:")
    print(f"Collection Name:     vietlegal_articles")
    print(f"Points Count:        {prod_info.points_count} (Must be EXACTLY 7170)")
    if prod_info.points_count == 7170:
        print("🟢 PRODUCTION BASELINE FROZEN AT 7,170 POINTS (ZERO MUTATION)!")
    else:
        print(f"🔴 WARNING: Production collection mutated! Current: {prod_info.points_count}")

if __name__ == "__main__":
    main()
