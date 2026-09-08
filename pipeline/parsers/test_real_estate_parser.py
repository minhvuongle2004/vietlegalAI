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
    
    for br in soup.find_all("br"):
        br.replace_with("\n")
    for p in soup.find_all(["p", "div", "tr"]):
        p.append("\n")
        
    raw_text = soup.get_text()
    
    # Normalize cases where "Điều" is followed by newlines and a number
    normalized_text = re.sub(r'Điều\s*\n+\s*(\d+)[\.:\s]', r'Điều \1. ', raw_text)
    lines = [line.strip() for line in normalized_text.splitlines() if line.strip()]
    
    articles = []
    current_art = None
    
    article_pattern = re.compile(r"^Điều\s+(\d+)[\.:\s]\s*(.*)", re.IGNORECASE)
    chapter_pattern = re.compile(r"^Chương\s+([IVXLCDM\d]+)[\.:\s]\s*(.*)", re.IGNORECASE)
    
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
    ("data/01_raw/html/31_2024_QH15.html", "land_31_2024_qh15", "Luật Đất đai 2024 (chuẩn: 260 điều)"),
    ("data/01_raw/html/27_2023_QH15.html", "housing_27_2023_qh15", "Luật Nhà ở 2023 (chuẩn: 198 điều)"),
    ("data/01_raw/html/29_2023_QH15.html", "re_business_29_2023_qh15", "Luật Kinh doanh BĐS 2023 (chuẩn: 83 điều)"),
    ("data/01_raw/html/61_2020_QH14.html", "investment_61_2020_qh14", "Luật Đầu tư 2020 (chuẩn: 77 điều)"),
]

for html_path, prefix, desc in docs:
    arts = parse_html_document(html_path, prefix)
    nums = [a["article_number"] for a in arts]
    print(f"\n--- {desc} ---")
    print(f"Parsed {len(arts)} articles. Min: {min(nums) if nums else 0}, Max: {max(nums) if nums else 0}")
    if arts:
        print(f"First article: Điều {arts[0]['article_number']}: {arts[0]['title']} ({len(arts[0]['lines'])} lines)")
        print(f"Last article:  Điều {arts[-1]['article_number']}: {arts[-1]['title']} ({len(arts[-1]['lines'])} lines)")
        # Check missing numbers
        missing = set(range(1, max(nums) + 1)) - set(nums)
        if missing:
            print(f"Warning: missing article numbers: {sorted(list(missing))[:15]}")
        else:
            print("All sequential articles present from 1 to max! Perfect!")
