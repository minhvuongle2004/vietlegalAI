import sys
import hashlib
import json
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
RAW_DIR = PROJECT_ROOT / "data" / "01_raw" / "traffic_p1_2_batch"
MANIFEST_FILE = RAW_DIR / "manifest.json"

def calculate_sha256(filepath: Path) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()

def verify_manifest():
    if not MANIFEST_FILE.exists():
        print(f"[ERROR] Manifest file not found: {MANIFEST_FILE}")
        sys.exit(1)

    with open(MANIFEST_FILE, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    print("=" * 80)
    print(f"Verifying Manifest: {manifest.get('batch_name')}")
    print(f"Total documents: {manifest.get('total_documents')}")
    print(f"Reported Legal Articles: {manifest.get('total_legal_articles_count')}")
    print(f"Reported QCVN Technical Units: {manifest.get('total_qcvn_technical_units_count')}")
    print("=" * 80)

    all_passed = True
    verified_articles = 0
    verified_qcvn = 0

    for doc in manifest["documents"]:
        filename = doc["filename"]
        expected_hash = doc["sha256"]
        expected_size = doc["size_bytes"]
        filepath = RAW_DIR / filename

        if not filepath.exists():
            print(f"[FAIL] Missing file: {filename}")
            all_passed = False
            continue

        actual_hash = calculate_sha256(filepath)
        actual_size = filepath.stat().st_size

        hash_ok = (actual_hash == expected_hash)
        size_ok = (actual_size == expected_size)

        if hash_ok and size_ok:
            verified_articles += doc["source_articles_count"]
            verified_qcvn += doc.get("attached_units_count", 0)
            print(f"[PASS] {filename:22} | SHA-256 match: True | Articles: {doc['source_articles_count']:2} | QCVN Units: {doc.get('attached_units_count', 0):2} | Size: {actual_size:5} B")
        else:
            print(f"[FAIL] {filename:22} | Hash match: {hash_ok} | Size match: {size_ok}")
            all_passed = False

    print("=" * 80)
    if all_passed:
        print("Overall Verification Result: 100% PASSED")
        print(f"Total Legal Articles Verified: {verified_articles} / {manifest.get('total_legal_articles_count')}")
        print(f"Total QCVN Technical Units Verified: {verified_qcvn} / {manifest.get('total_qcvn_technical_units_count')}")
    else:
        print("Overall Verification Result: FAILED")
        sys.exit(1)
    print("=" * 80)

if __name__ == "__main__":
    verify_manifest()
