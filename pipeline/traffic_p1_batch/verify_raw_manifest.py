import sys
import json
import hashlib
import re
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

RAW_DIR = Path("data/01_raw/traffic_p1_batch")
manifest_path = RAW_DIR / "manifest.json"

with open(manifest_path, "r", encoding="utf-8") as f:
    manifest = json.load(f)

print(f"Verifying Manifest: {manifest['batch_name']}")
print(f"Total documents: {manifest['total_documents']}")
print(f"Reported Core Articles: {manifest['total_core_articles_count']}\n")

all_passed = True
total_verified_core_articles = 0

for doc in manifest["documents"]:
    file_path = RAW_DIR / doc["filename"]
    raw_bytes = file_path.read_bytes()
    computed_sha = hashlib.sha256(raw_bytes).hexdigest()
    
    sha_match = computed_sha == doc["sha256"]
    
    # Count articles in HTML
    html_text = raw_bytes.decode("utf-8")
    articles = re.findall(r'<p><b>Điều\s+\d+[\.:]', html_text)
    article_count = len(articles)
    
    count_match = article_count == doc["source_articles_count"]
    
    status_str = "PASS" if (sha_match and count_match) else "FAIL"
    if not (sha_match and count_match):
        all_passed = False
        
    print(f"[{status_str}] {doc['filename']}:")
    print(f"       SHA-256 match: {sha_match} ({computed_sha[:16]}...)")
    print(f"       Articles: {article_count} (Expected: {doc['source_articles_count']})")
    print(f"       Dimensions: Legal={doc['legal_status']} | Ingestion={doc['ingestion_status']} | Role={doc['document_role']}")
    
    if doc["ingestion_status"] == "CORE" and doc["legal_status"] == "CURRENT":
        total_verified_core_articles += article_count

print("\n" + "="*60)
print(f"Overall Verification Result: {'100% PASSED' if all_passed else 'FAILED'}")
print(f"Total Current Core Articles Verified: {total_verified_core_articles} / 137")
print("="*60)
