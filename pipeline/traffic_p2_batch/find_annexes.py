import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
import re

path = r"C:\Users\vuong\.gemini\antigravity-ide\brain\d4e19d11-4f9f-41c0-a5d4-f7b6e3367760\.system_generated\steps\14368\content.md"
with open(path, "r", encoding="utf-8") as f:
    text = f.read()

# Look for Annex headings
pattern = r'(#+\s*PHỤ LỤC\s+[IVXLCDM0-9]+[^\n]*|\bPHỤ LỤC\s+[IVXLCDM0-9]+\b[^\n]*)'
matches = re.finditer(pattern, text, re.I)
for m in matches:
    start = max(0, m.start() - 50)
    end = min(len(text), m.end() + 200)
    print("--- MATCH at pos", m.start(), "---")
    print(text[m.start():end])
