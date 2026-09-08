import sys
from bs4 import BeautifulSoup
from pathlib import Path
import re

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def parse_html_document_refined(html_path: str, doc_prefix: str, expected_total: int):
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
    
    # Matches: "Điều 1.", "Điều 1:", "Điều 1 "
    article_pattern = re.compile(r"^Điều\s+(\d+)[\.:\s]\s*(.*)", re.IGNORECASE)
    chapter_pattern = re.compile(r"^Chương\s+([IVXLCDM\d]+)[\.:\s]\s*(.*)", re.IGNORECASE)
    
    current_chapter = ""
    expected_art = 1
    
    for line in lines:
        ch_match = chapter_pattern.match(line)
        if ch_match:
            current_chapter = line
            continue
            
        art_match = article_pattern.match(line)
        is_real_article = False
        if art_match:
            art_num = int(art_match.group(1))
            art_title = art_match.group(2).strip()
            
            # Check false positive reference
            invalid_title_patterns = [
                r"^của\s+Luật",
                r"^của\s+Bộ\s+luật",
                r"^của\s+Nghị\s+định",
                r"^và\s+Điều",
                r"^hoặc\s+Điều",
                r"của\s+Luật\s+này",
                r"theo\s+quy\s+định"
            ]
            is_ref = any(re.search(pat, art_title, re.IGNORECASE) for pat in invalid_title_patterns)
            
            # Real articles must be the next expected article (or within +1/+2 if skipping, but not backward jumping)
            if not is_ref and (art_num == expected_art or (expected_art <= art_num <= expected_art + 2)):
                is_real_article = True
                expected_art = art_num + 1
        
        if is_real_article:
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
    ("data/01_raw/html/31_2024_QH15.html", "land_31_2024_qh15", 260, "Luật Đất đai 2024 (260 điều)"),
    ("data/01_raw/html/27_2023_QH15.html", "housing_27_2023_qh15", 198, "Luật Nhà ở 2023 (198 điều)"),
    ("data/01_raw/html/29_2023_QH15.html", "re_business_29_2023_qh15", 83, "Luật Kinh doanh BĐS 2023 (83 điều)"),
    ("data/01_raw/html/61_2020_QH14.html", "investment_61_2020_qh14", 77, "Luật Đầu tư 2020 (77 điều)"),
]

for html_path, prefix, expected, desc in docs:
    arts = parse_html_document_refined(html_path, prefix, expected)
    nums = [a["article_number"] for a in arts]
    print(f"\n--- {desc} ---")
    print(f"Parsed {len(arts)} articles (Expected: {expected}). Min: {min(nums) if nums else 0}, Max: {max(nums) if nums else 0}")
    if len(arts) == expected:
        print(f"  [SUCCESS] EXACT MATCH: {len(arts)}/{expected} articles!")
    else:
        missing = set(range(1, expected + 1)) - set(nums)
        print(f"  [DIFF] Missing: {sorted(list(missing))}")
