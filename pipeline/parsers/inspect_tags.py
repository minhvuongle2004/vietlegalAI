import sys
from pathlib import Path
from bs4 import BeautifulSoup
import re

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

html = Path('data/01_raw/html/27_2023_QH15.html').read_text(encoding='utf-8', errors='ignore')
soup = BeautifulSoup(html, 'html.parser')

# Search for elements containing "Giải thích từ ngữ" (which is Điều 2 of Luật Nhà ở)
for el in soup.find_all(text=re.compile(r"Giải thích từ ngữ", re.IGNORECASE)):
    parent = el.parent
    print("Found 'Giải thích từ ngữ':")
    print("Parent tag:", parent.name, parent.attrs)
    print("Grandparent tag:", parent.parent.name if parent.parent else None)
    print("Surrounding HTML:")
    print(str(parent.parent)[:500] if parent.parent else str(parent)[:500])
    break

# Also search for Điều 3, Điều 4
for art in ["Điều 2", "Điều 3", "Điều 18"]:
    matches = soup.find_all(text=re.compile(rf"{art}\b"))
    print(f"\nOccurrences of '{art}': {len(matches)}")
    for m in matches[:3]:
        print("  ->", repr(m.strip()[:60]))
