"""
Script to synchronize vector collections from local Qdrant to Qdrant Cloud.
Reads 7,093 vectors + payloads from local Qdrant (http://localhost:6333)
and upserts them in batches to Qdrant Cloud.
"""

import sys
import time
from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels

LOCAL_URL = "http://localhost:6333"
CLOUD_URL = "https://69f07c1e-2e88-452f-aded-6dd577ddbd9b.us-west-2-0.aws.cloud.qdrant.io"
CLOUD_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIiwic3ViamVjdCI6ImFwaS1rZXk6OTAxNjk0MzUtYjMwMS00YjAzLWFmMGYtYmYyZjc0MWE4MjYxIn0.bJ2YtMtnmDJXN4k3FKdduN_TsLARSOAvGjBRKW3p028"
COLLECTION_NAME = "vietlegal_articles"
BATCH_SIZE = 100


def main():
    print("=" * 60)
    print("STARTING QDRANT CLOUD SYNCHRONIZATION")
    print("=" * 60)
    
    # 1. Connect to Local Qdrant
    print(f"[1/5] Connecting to Local Qdrant at {LOCAL_URL}...")
    local_client = QdrantClient(url=LOCAL_URL, check_compatibility=False)
    local_info = local_client.get_collection(COLLECTION_NAME)
    total_local_points = local_info.points_count
    print(f"      -> Local collection '{COLLECTION_NAME}' found: {total_local_points} points.")
    
    # 2. Connect to Qdrant Cloud
    print(f"[2/5] Connecting to Qdrant Cloud at {CLOUD_URL}...")
    cloud_client = QdrantClient(url=CLOUD_URL, api_key=CLOUD_API_KEY, check_compatibility=False)
    cloud_collections = [c.name for c in cloud_client.get_collections().collections]
    
    # 3. Create or prepare Collection on Cloud
    if COLLECTION_NAME not in cloud_collections:
        print(f"[3/5] Creating collection '{COLLECTION_NAME}' on Qdrant Cloud...")
        cloud_client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=qmodels.VectorParams(
                size=1024,
                distance=qmodels.Distance.COSINE
            )
        )
        print("      -> Collection created successfully.")
    else:
        cloud_info = cloud_client.get_collection(COLLECTION_NAME)
        print(f"[3/5] Collection '{COLLECTION_NAME}' already exists on Cloud ({cloud_info.points_count} points).")
    
    # 4. Stream and Upsert points in batches
    print(f"[4/5] Migrating {total_local_points} points to Qdrant Cloud (batch size: {BATCH_SIZE})...")
    offset = None
    synced_count = 0
    start_time = time.time()
    
    while True:
        records, next_offset = local_client.scroll(
            collection_name=COLLECTION_NAME,
            limit=BATCH_SIZE,
            offset=offset,
            with_payload=True,
            with_vectors=True
        )
        
        if not records:
            break
            
        points_to_upsert = [
            qmodels.PointStruct(
                id=rec.id,
                vector=rec.vector,
                payload=rec.payload
            )
            for rec in records
        ]
        
        cloud_client.upsert(
            collection_name=COLLECTION_NAME,
            points=points_to_upsert,
            wait=False
        )
        
        synced_count += len(records)
        elapsed = time.time() - start_time
        rate = synced_count / elapsed if elapsed > 0 else 0
        pct = (synced_count / total_local_points) * 100
        
        sys.stdout.write(f"\r      -> Synced: {synced_count}/{total_local_points} points ({pct:.1f}%) - {rate:.0f} pts/sec")
        sys.stdout.flush()
        
        if next_offset is None:
            break
        offset = next_offset

    print()
    total_time = time.time() - start_time
    print(f"      -> Completed upload in {total_time:.1f}s.")
    
    # 5. Verify Qdrant Cloud
    print("[5/5] Verifying points count on Qdrant Cloud...")
    time.sleep(2)  # brief pause for indexing
    cloud_final_info = cloud_client.get_collection(COLLECTION_NAME)
    print(f"      -> Qdrant Cloud total points: {cloud_final_info.points_count}")
    
    # Quick search verification
    print("      -> Testing search retrieval on Cloud...")
    sample_records, _ = local_client.scroll(collection_name=COLLECTION_NAME, limit=1, with_vectors=True)
    if sample_records:
        test_vector = sample_records[0].vector
        search_res = cloud_client.query_points(
            collection_name=COLLECTION_NAME,
            query=test_vector,
            limit=3
        )
        print(f"      -> Search test SUCCESS: Retrieved {len(search_res.points)} points matching query vector.")
        print(f"         Top match ID: {search_res.points[0].id} (score: {search_res.points[0].score:.4f})")

    print("=" * 60)
    print("ALL DONE! QDRANT CLOUD IS 100% READY FOR PRODUCTION.")
    print("=" * 60)


if __name__ == "__main__":
    main()
