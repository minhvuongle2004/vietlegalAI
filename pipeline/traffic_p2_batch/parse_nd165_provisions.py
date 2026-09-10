import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
import re
import json

path = r"C:\Users\vuong\.gemini\antigravity-ide\brain\d4e19d11-4f9f-41c0-a5d4-f7b6e3367760\.system_generated\steps\14368\content.md"
with open(path, "r", encoding="utf-8") as f:
    text = f.read()

# Separate preamble, articles, and annexes
# Find start of Annexes
annex_match = re.search(r'\n(Phụ lục I\b[^\n]*)', text)
if annex_match:
    annex_pos = annex_match.start()
    articles_text = text[:annex_pos]
    annex_text = text[annex_pos:]
else:
    articles_text = text
    annex_text = ""

# Split chapters
chapter_matches = list(re.finditer(r'(Chương\s+([IVXLCDM]+)\s*\n([^\n]+))', articles_text))
print(f"Total chapters: {len(chapter_matches)}")

# Split articles: "Điều {num}. {title}"
article_regex = re.compile(r'\n(Điều\s+(\d+)\.\s*([^\n]+))')
article_matches = list(article_regex.finditer(articles_text))
print(f"Total articles: {len(article_matches)}")

parsed_articles = []

for idx, match in enumerate(article_matches):
    art_header = match.group(1).strip()
    art_num = int(match.group(2))
    art_title = match.group(3).strip()
    
    # Determine chapter
    curr_chapter = "Chương I"
    curr_chapter_title = ""
    for ch in chapter_matches:
        if ch.start() < match.start():
            curr_chapter = f"Chương {ch.group(2)}"
            curr_chapter_title = ch.group(3).strip()
            
    # Text slice for this article
    start_pos = match.end()
    end_pos = article_matches[idx+1].start() if idx + 1 < len(article_matches) else len(articles_text)
    art_content = articles_text[start_pos:end_pos].strip()
    
    # Let's clean up annotation notes if any (e.g. "[Được sửa đổi bởi ...]") but keep track of text
    # Parse clauses: "1. ", "2. ", etc.
    # Clause pattern: \n(\d+)\.\s+ or starting at 0 if begins with "1. "
    lines = art_content.split('\n')
    clauses = []
    current_clause = None
    
    clause_regex = re.compile(r'^(\d+)\.\s+(.*)')
    point_regex = re.compile(r'^([a-zđ])\)\s+(.*)')
    
    for line in lines:
        line_s = line.strip()
        if not line_s:
            continue
            
        c_m = clause_regex.match(line_s)
        if c_m:
            c_num = int(c_m.group(1))
            current_clause = {
                "clause_number": c_num,
                "text": c_m.group(2),
                "points": []
            }
            clauses.append(current_clause)
            continue
            
        p_m = point_regex.match(line_s)
        if p_m and current_clause:
            p_id = p_m.group(1)
            current_clause["points"].append({
                "point_id": p_id,
                "text": p_m.group(2)
            })
            continue
            
        # Additional text attached to current clause or unnumbered clause
        if current_clause:
            current_clause["text"] += "\n" + line_s
        else:
            # Unnumbered single clause
            if not clauses:
                current_clause = {
                    "clause_number": 1,
                    "text": line_s,
                    "points": []
                }
                clauses.append(current_clause)
            else:
                clauses[-1]["text"] += "\n" + line_s
                
    parsed_articles.append({
        "article_number": art_num,
        "title": art_title,
        "chapter": curr_chapter,
        "chapter_title": curr_chapter_title,
        "raw_text": art_content,
        "clauses": clauses
    })

total_clauses = sum(len(a["clauses"]) for a in parsed_articles)
total_points = sum(sum(len(c["points"]) for c in a["clauses"]) for a in parsed_articles)

print(f"Parsed Articles: {len(parsed_articles)}")
print(f"Parsed Clauses: {total_clauses}")
print(f"Parsed Points: {total_points}")

# Check sample article: Điều 17, Điều 21, Điều 30
for a in parsed_articles:
    if a["article_number"] in [17, 21, 30, 32]:
        print(f"\n--- Điều {a['article_number']}: {a['title']} ---")
        print(f"Clauses count: {len(a['clauses'])}")
        for c in a["clauses"]:
            print(f"  Khoản {c['clause_number']}: points={len(c['points'])}, text preview: {c['text'][:60]}...")
            for p in c["points"]:
                print(f"    Điểm {p['point_id']}) {p['text'][:40]}...")
