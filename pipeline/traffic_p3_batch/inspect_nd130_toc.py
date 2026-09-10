import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

path = r"C:\Users\vuong\.gemini\antigravity-ide\brain\d4e19d11-4f9f-41c0-a5d4-f7b6e3367760\.system_generated\steps\14942\content.md"
with open(path, "r", encoding="utf-8") as f:
    text = f.read()

matches = re.findall(r'title="([^"]+)"', text)
seen = set()
for m in matches:
    if ("Điều " in m or "CHƯƠNG " in m or "Phụ lục" in m) and m not in seen:
        seen.add(m)
        print(" ", m)
