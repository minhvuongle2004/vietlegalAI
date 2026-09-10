import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
import os
import hashlib
import json
import shutil
from pathlib import Path
from datetime import datetime, timezone

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
RAW_P3_DIR = PROJECT_ROOT / "data" / "01_raw" / "traffic_p3_batch"
RAW_P3_DIR.mkdir(parents=True, exist_ok=True)

# 1. Prepare raw artifacts for 168 and 238
dir_168 = RAW_P3_DIR / "168_2024_ND_CP"
dir_238 = RAW_P3_DIR / "238_2026_ND_CP"
dir_168.mkdir(parents=True, exist_ok=True)
dir_238.mkdir(parents=True, exist_ok=True)

src_168 = PROJECT_ROOT / "data" / "01_raw" / "html" / "168_2024_ND_CP.html"
dest_168 = dir_168 / "168_2024_ND_CP.html"
if src_168.exists() and not dest_168.exists():
    shutil.copy(src_168, dest_168)

src_238 = PROJECT_ROOT / "data" / "01_raw" / "traffic_p0_batch" / "238_2026_ND_CP.html"
dest_238 = dir_238 / "238_2026_ND_CP.html"
if src_238.exists() and not dest_238.exists():
    shutil.copy(src_238, dest_238)

def compute_meta(filepath, url, desc):
    with open(filepath, "rb") as f:
        content = f.read()
    sha256 = hashlib.sha256(content).hexdigest()
    return {
        "filename": filepath.name,
        "relative_path": str(filepath.relative_to(PROJECT_ROOT)).replace("\\", "/"),
        "sha256": sha256,
        "file_size": len(content),
        "content_type": "text/html",
        "source_url": url,
        "retrieved_at": datetime.now(timezone.utc).isoformat(),
        "description": desc
    }

meta_168 = compute_meta(dest_168, "https://vanban.chinhphu.vn/?pageid=27160&docid=212171", "Nghị định 168/2024/NĐ-CP xử phạt vi phạm hành chính TTATGT")
meta_238 = compute_meta(dest_238, "https://vanban.chinhphu.vn/?pageid=27160&docid=212450", "Nghị định 238/2026/NĐ-CP sửa đổi, bổ sung Nghị định 168/2024/NĐ-CP")

with open(dir_168 / "raw_manifest.json", "w", encoding="utf-8") as f:
    json.dump([meta_168], f, ensure_ascii=False, indent=2)

with open(dir_238 / "raw_manifest.json", "w", encoding="utf-8") as f:
    json.dump([meta_238], f, ensure_ascii=False, indent=2)

print(f"[+] Prepared RAW for NĐ 168: SHA256 = {meta_168['sha256']}, Size = {meta_168['file_size']}")
print(f"[+] Prepared RAW for NĐ 238: SHA256 = {meta_238['sha256']}, Size = {meta_238['file_size']}")
