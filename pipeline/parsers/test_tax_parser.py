import sys
import re
from bs4 import BeautifulSoup
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def parse_html_document(html_path: str, doc_prefix: str):
    path = Path(html_path)
    if not path.exists():
        print(f"File not found: {html_path}")
        return []
    
    html = path.read_text(encoding="utf-8", errors="ignore")
    soup = BeautifulSoup(html, "html.parser")
    
    # Extract text with line breaks preserved
    for br in soup.find_all("br"):
        br.replace_with("\n")
    for p in soup.find_all(["p", "div", "tr"]):
        p.append("\n")
        
    raw_text = soup.get_text()
    lines = [line.strip() for line in raw_text.splitlines() if line.strip()]
    
    # Identify Articles: "Điều X." hoặc "Điều X:"
    articles = []
    current_art = None
    
    article_pattern = re.compile(r"^Điều\s+(\d+)\.?\s*(.*)", re.IGNORECASE)
    chapter_pattern = re.compile(r"^Chương\s+([IVXLCDM\d]+)\.?\s*(.*)", re.IGNORECASE)
    
    current_chapter = ""
    
    for line in lines:
        ch_match = chapter_pattern.match(line)
        if ch_match:
            current_chapter = line
            continue
            
        art_match = article_pattern.match(line)
        if art_match:
            art_num = int(art_match.group(1))
            art_title = art_match.group(2).strip()
            if current_art:
                articles.append(current_art)
            current_art = {
                "article_number": art_num,
                "title": art_title,
                "chapter": current_chapter,
                "lines": [line],
                "doc_id": doc_prefix
            }
        else:
            if current_art:
                current_art["lines"].append(line)
                
    if current_art:
        articles.append(current_art)
        
    return articles

docs = [
    {"path": "data/01_raw/html/109_2025_QH15.html", "id": "tncn_109_2025_qh15", "name": "Luật Thuế TNCN 109/2025/QH15"},
    {"path": "data/01_raw/html/67_2025_QH15.html", "id": "tndn_67_2025_qh15", "name": "Luật Thuế TNDN 67/2025/QH15"},
    {"path": "data/01_raw/html/108_2025_QH15.html", "id": "qlt_108_2025_qh15", "name": "Luật Quản lý thuế 108/2025/QH15"}
]

for d in docs:
    arts = parse_html_document(d["path"], d["id"])
    print(f"\n[{d['name']}]")
    print(f"  Total articles parsed: {len(arts)}")
    if arts:
        print(f"  First: Điều {arts[0]['article_number']}: {arts[0]['title']}")
        print(f"  Last:  Điều {arts[-1]['article_number']}: {arts[-1]['title']}")
        # check missing numbers
        nums = [a["article_number"] for a in arts]
        missing = [x for x in range(1, max(nums) + 1) if x not in nums]
        if missing:
            print(f"  WARNING: Missing articles: {missing}")
        else:
            print(f"  -> SUCCESS: All {max(nums)} articles consecutively parsed!")
