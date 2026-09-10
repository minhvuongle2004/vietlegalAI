import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
import re

path = r"C:\Users\vuong\.gemini\antigravity-ide\brain\d4e19d11-4f9f-41c0-a5d4-f7b6e3367760\.system_generated\steps\14368\content.md"
with open(path, "r", encoding="utf-8") as f:
    text = f.read()

# Match articles: "Điều X."
# Note: stop before Phụ lục
annex_start = text.find("Phụ lục I\nMẪU TỜ TRÌNH")
if annex_start == -1:
    annex_start = text.find("Phụ lục I\n")
body_text = text[:annex_start] if annex_start != -1 else text

# Let's find all chapters in body
chapters = re.findall(r'(Chương\s+[IVXLCDM]+\s*\n[^\n]+)', body_text)
print("=== Chapters ===")
for c in chapters:
    print(c.replace('\n', ' - '))

# Let's find all Articles
articles = re.findall(r'(Điều\s+(\d+)\.\s*([^\n]+))', body_text)
print(f"\nTotal Articles found: {len(articles)}")
seen_nums = set()
for a in articles:
    num = int(a[1])
    seen_nums.add(num)
    
min_a = min(seen_nums)
max_a = max(seen_nums)
missing = [i for i in range(min_a, max_a + 1) if i not in seen_nums]
print(f"Article range: {min_a} to {max_a}")
print(f"Missing articles: {missing}")

# Check first and last articles
print("First:", articles[0][0])
print("Last:", articles[-1][0])
