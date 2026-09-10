import sys
from pathlib import Path
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
from duckduckgo_search import DDGS

ddgs = DDGS()
print("[*] Searching for official URL of ND 94/2026/ND-CP...")
queries = [
    "94/2026/NĐ-CP site:chinhphu.vn",
    "94/2026/NĐ-CP site:congbao.chinhphu.vn",
    "94/2026/NĐ-CP site:thuvienphapluat.vn",
    "94/2026/NĐ-CP dao tao sat hach lai xe"
]

for q in queries:
    print(f"\nQuery: {q}")
    try:
        results = list(ddgs.text(q, max_results=3))
        for r in results:
            print(f"  {r.get('title')} --> {r.get('href')}")
    except Exception as e:
        print(f"  Error: {e}")
