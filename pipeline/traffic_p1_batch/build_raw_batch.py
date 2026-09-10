import sys
import os
import json
import hashlib
from datetime import datetime
from pathlib import Path

# Fix stdout encoding for Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

RAW_DIR = Path("data/01_raw/traffic_p1_batch")
RAW_DIR.mkdir(parents=True, exist_ok=True)

print("Starting creation of RAW files for Traffic P1 Batch...")
