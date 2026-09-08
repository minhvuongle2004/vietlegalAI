import sys
from pathlib import Path
from bs4 import BeautifulSoup
import re

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

html = Path('data/01_raw/html/27_2023_QH15.html').read_text(encoding='utf-8', errors='ignore')
soup = BeautifulSoup(html, 'html.parser')

for br in soup.find_all("br"):
    br.replace_with("\n")
for p in soup.find_all(["p", "div", "tr"]):
    p.append("\n")
    
raw_text = soup.get_text()
lines = [line.strip() for line in raw_text.splitlines() if line.strip()]

print(f"Total lines: {len(lines)}")
dieu_lines = [l for l in lines if l.startswith("Điều ") or "Điều " in l[:10]]
print(f"Total lines starting with Dieu: {len(dieu_lines)}")
for l in dieu_lines[:25]:
    print("  ->", l[:80])
