import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
import re

path = r"C:\Users\vuong\.gemini\antigravity-ide\brain\d4e19d11-4f9f-41c0-a5d4-f7b6e3367760\.system_generated\steps\14368\content.md"
with open(path, "r", encoding="utf-8") as f:
    text = f.read()

print("File size:", len(text))

# Find Chapters
chapters = re.findall(r'(Chương\s+[IVXLCDM]+[^\n]*)', text)
print("Chapters found:", len(chapters))
for c in chapters[:15]:
    print(" ", c)

# Find Articles
articles = re.findall(r'(Điều\s+(\d+[a-z]?)\.\s*([^\n]*))', text)
print("Articles found:", len(articles))
print("First 5 articles:")
for a in articles[:5]:
    print(" ", a[0][:80])
print("Last 5 articles:")
for a in articles[-5:]:
    print(" ", a[0][:80])

# Find Annexes
annexes = re.findall(r'(Phụ lục\s+[IVXLCDM0-9]+[^\n]*)', text, re.I)
print("Annexes mentioned:", len(annexes))
for an in set(annexes):
    print(" ", an)
