import sys
from pathlib import Path
from bs4 import BeautifulSoup
import re

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

html = Path('data/01_raw/html/27_2023_QH15.html').read_text(encoding='utf-8', errors='ignore')
soup = BeautifulSoup(html, "html.parser")

for br in soup.find_all("br"):
    br.replace_with("\n")
for p in soup.find_all(["p", "div", "tr"]):
    p.append("\n")
    
raw_text = soup.get_text()

# Normalize cases where "Điều" is followed by newlines and a number
normalized_text = re.sub(r'Điều\s*\n+\s*(\d+)[\.:\s]', r'Điều \1. ', raw_text)

lines = [line.strip() for line in normalized_text.splitlines() if line.strip()]

article_pattern = re.compile(r"^Điều\s+(\d+)[\.:\s]\s*(.*)", re.IGNORECASE)

articles = []
for line in lines:
    m = article_pattern.match(line)
    if m:
        articles.append((int(m.group(1)), m.group(2)[:40]))

nums = [a[0] for a in articles]
unique_nums = sorted(list(set(nums)))
print(f"Total article matches: {len(articles)}")
print(f"Unique article numbers: {len(unique_nums)} (Min: {min(unique_nums)}, Max: {max(unique_nums)})")
missing = set(range(1, max(unique_nums) + 1)) - set(unique_nums)
print(f"Missing: {sorted(list(missing))}")
