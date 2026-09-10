import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
import os
import re
import json
from pathlib import Path
from bs4 import BeautifulSoup

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
HTML_PATH = r"C:\Users\vuong\.gemini\antigravity-ide\brain\d4e19d11-4f9f-41c0-a5d4-f7b6e3367760\.system_generated\steps\15031\content.md"
OUT_DIR = PROJECT_ROOT / "data" / "03_parsed" / "traffic_p3_batch"
OUT_DIR.mkdir(parents=True, exist_ok=True)

def parse_nd158_78_articles():
    with open(HTML_PATH, "r", encoding="utf-8") as f:
        text = f.read()

    # Split by <a name="dieu_(\d+)">
    parts = re.split(r'<a\s+name="dieu_(\d+)">', text)
    print(f"Total split sections: {len(parts)}")

    parsed_articles = []
    for i in range(1, len(parts), 2):
        num = int(parts[i])
        raw_content = parts[i+1]
        
        # Truncate after article 78 signature
        if num == 78:
            for marker in ['<!--VABWAFAATABfADIAMAAyADQAMQAyADIAOAA=-->', 'Nơi nhận:', 'TM. CHÍNH PHỦ']:
                pos = raw_content.find(marker)
                if pos != -1:
                    raw_content = raw_content[:pos]
                    break
        
        soup = BeautifulSoup(raw_content, "html.parser")
        clean_text = soup.get_text(separator="\n").strip()
        clean_text = re.sub(r'\n\s*\n', '\n', clean_text)
        
        # First line is title
        lines = [l.strip() for l in clean_text.split("\n") if l.strip()]
        header = lines[0] if lines else f"Điều {num}."
        
        # Extract title after "Điều X."
        m = re.match(r"^Điều\s+\d+\.\s*(.*)", header)
        art_title = m.group(1).strip() if m else header

        parsed_articles.append({
            "article_number": num,
            "article_title": art_title,
            "full_text": "\n".join(lines)
        })

    print(f"[+] Successfully extracted {len(parsed_articles)} articles (Expected: 78).")
    
    # Save parsed JSON
    out_file = OUT_DIR / "nd158_2024_full_78_articles.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(parsed_articles, f, ensure_ascii=False, indent=2)
    print(f"[+] Saved parsed articles to {out_file}")

    return parsed_articles

if __name__ == "__main__":
    arts = parse_nd158_78_articles()
    print(f"Article 1: {arts[0]['article_title']} (len={len(arts[0]['full_text'])})")
    print(f"Article 78: {arts[-1]['article_title']} (len={len(arts[-1]['full_text'])})")
