import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
import os
import hashlib
import json
import urllib.request
from datetime import datetime, timezone

RAW_DIR = "data/01_raw/traffic_p2_batch/165_2024_ND_CP"
os.makedirs(RAW_DIR, exist_ok=True)

artifacts = [
    {
        "filename": "165_2024_nd-cp_26122024-signed.pdf",
        "url": "https://datafiles.chinhphu.vn/cpp/files/vbpq/2025/01/165_2024_nd-cp_26122024-signed.pdf",
        "description": "Nghị định 165/2024/NĐ-CP official signed PDF"
    },
    {
        "filename": "165-pl1.pdf",
        "url": "https://datafiles.chinhphu.vn/cpp/files/vbpq/2025/01/165-pl1.pdf",
        "description": "Nghị định 165/2024/NĐ-CP official annex artifact (Phụ lục)"
    }
]

manifest = []

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

for item in artifacts:
    filepath = os.path.join(RAW_DIR, item["filename"])
    print(f"Downloading {item['filename']} from {item['url']}...")
    req = urllib.request.Request(item["url"], headers=headers)
    with urllib.request.urlopen(req, timeout=60) as resp:
        content = resp.read()
        content_type = resp.headers.get("Content-Type", "application/pdf")
    
    with open(filepath, "wb") as f:
        f.write(content)
        
    sha256 = hashlib.sha256(content).hexdigest()
    file_size = len(content)
    now_iso = datetime.now(timezone.utc).isoformat()
    
    print(f"Downloaded {item['filename']}: size={file_size} bytes, sha256={sha256}")
    manifest.append({
        "filename": item["filename"],
        "relative_path": filepath.replace("\\", "/"),
        "source_url": item["url"],
        "sha256": sha256,
        "file_size": file_size,
        "content_type": content_type,
        "retrieved_at": now_iso,
        "description": item["description"]
    })

manifest_path = os.path.join(RAW_DIR, "raw_manifest.json")
with open(manifest_path, "w", encoding="utf-8") as f:
    json.dump(manifest, f, ensure_ascii=False, indent=2)

print(f"Saved raw manifest to {manifest_path}")
