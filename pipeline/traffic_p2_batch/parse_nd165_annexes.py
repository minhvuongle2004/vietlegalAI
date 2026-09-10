import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
import re
import json

path = r"C:\Users\vuong\.gemini\antigravity-ide\brain\d4e19d11-4f9f-41c0-a5d4-f7b6e3367760\.system_generated\steps\14368\content.md"
with open(path, "r", encoding="utf-8") as f:
    text = f.read()

annex_start = text.find("Phụ lục I\nMẪU TỜ TRÌNH")
if annex_start == -1:
    annex_start = text.find("Phụ lục I\n")
annex_text = text[annex_start:]

# Find all Phụ lục
# Roman numerals: I, II, III, IV, V, VI, VII, VIII, IX, X
annex_matches = list(re.finditer(r'(Phụ lục\s+([IVXLCDM]+)\s*\n([^\n]+(?:\n[^\n]+)?))', annex_text))
print(f"Total Annex headings found: {len(annex_matches)}")

parsed_annexes = []
for i, m in enumerate(annex_matches):
    pl_num = m.group(2)
    start = m.start()
    end = annex_matches[i+1].start() if i + 1 < len(annex_matches) else len(annex_text)
    pl_content = annex_text[start:end].strip()
    
    # Extract title
    lines = pl_content.split('\n')
    title_lines = []
    for l in lines[1:5]:
        if l.strip().startswith('(') or l.strip().startswith('____') or l.strip().startswith('Mẫu'):
            break
        title_lines.append(l.strip())
    pl_title = " ".join(title_lines).strip()
    
    # Find Mẫu (Forms) inside this Annex
    forms = re.findall(r'(Mẫu\s+số\s+(\d+[a-z]?)\s*[:\n\-]\s*([^\n]+))', pl_content, re.I)
    
    parsed_annexes.append({
        "annex_number": f"Phụ lục {pl_num}",
        "annex_roman": pl_num,
        "title": pl_title,
        "forms_count": len(forms),
        "forms": [{"code": f"Mẫu {f[1]}", "title": f[2].strip()} for f in forms],
        "content_length": len(pl_content),
        "raw_text": pl_content
    })

print(f"\n--- Parsed {len(parsed_annexes)} Annexes ---")
total_forms = 0
for pa in parsed_annexes:
    print(f"{pa['annex_number']}: {pa['title']} (Forms: {pa['forms_count']}, len: {pa['content_length']})")
    for f in pa['forms']:
        print(f"   - {f['code']}: {f['title'][:60]}")
    total_forms += pa['forms_count']

print(f"\nTotal Forms across Annexes: {total_forms}")
