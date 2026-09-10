import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
import os
import re
import json
from pathlib import Path
from bs4 import BeautifulSoup

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
HTML_PATH = r"C:\Users\vuong\.gemini\antigravity-ide\brain\d4e19d11-4f9f-41c0-a5d4-f7b6e3367760\.system_generated\steps\14991\content.md"
OUT_DIR = PROJECT_ROOT / "data" / "03_parsed" / "traffic_p3_batch"
OUT_DIR.mkdir(parents=True, exist_ok=True)

def parse_nd161_33_articles():
    with open(HTML_PATH, "r", encoding="utf-8") as f:
        text = f.read()

    # In 14991/content.md, let's see how articles are split
    # Search for "Điều X."
    articles_positions = []
    for i in range(1, 34):
        # find Điều i.
        pattern = rf'Điều\s+{i}\.\s*([^\n<]+)'
        m = re.search(pattern, text)
        if m:
            articles_positions.append((i, m.group(1).strip(), m.start()))
        else:
            print(f"Warning: could not find Điều {i} with regex!")

    print(f"Found {len(articles_positions)} articles with positions.")

    parsed_articles = []
    for idx, (num, title, start_pos) in enumerate(articles_positions):
        end_pos = articles_positions[idx + 1][2] if idx + 1 < len(articles_positions) else len(text)
        raw_snippet = text[start_pos:end_pos]
        
        # If last article, clean up signature/tail
        if num == 33:
            for marker in ['Nơi nhận:', 'TM. CHÍNH PHỦ', '<!--VABWAFA']:
                pos = raw_snippet.find(marker)
                if pos != -1:
                    raw_snippet = raw_snippet[:pos]
                    break
        
        soup = BeautifulSoup(raw_snippet, "html.parser")
        clean_text = soup.get_text(separator="\n").strip()
        clean_text = re.sub(r'\n\s*\n', '\n', clean_text)
        
        # Clean title if it has HTML remnants
        clean_title = re.sub(r'<[^>]+>', '', title).strip()
        clean_title = re.sub(r'["\']', '', clean_title).strip()
        
        parsed_articles.append({
            "article_number": num,
            "article_title": clean_title,
            "full_text": clean_text
        })

    print(f"[+] Successfully extracted {len(parsed_articles)} articles for NĐ 161 (Expected: 33).")
    
    out_file = OUT_DIR / "nd161_2024_full_33_articles.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(parsed_articles, f, ensure_ascii=False, indent=2)
    print(f"[+] Saved parsed articles to {out_file}")

    return parsed_articles

if __name__ == "__main__":
    arts = parse_nd161_33_articles()
    for a in arts:
        print(f"  Điều {a['article_number']}: {a['article_title'][:50]} (len={len(a['full_text'])})")
