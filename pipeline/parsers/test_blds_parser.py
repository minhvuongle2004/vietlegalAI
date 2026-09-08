import re
from bs4 import BeautifulSoup
from pathlib import Path

html_path = Path("data/01_raw/html/91_2015_QH13.html")
with open(html_path, "r", encoding="utf-8") as f:
    html = f.read()

soup = BeautifulSoup(html, "html.parser")
elements = soup.find_all(["p", "div"])

articles = {}
current_art_num = None
current_art_title = ""
current_art_lines = []
current_chapter = ""

for el in elements:
    text = re.sub(r"\s+", " ", el.get_text()).strip()
    if not text:
        continue

    # Check chapter
    chap_m = re.match(r"^(?:Chương|CHƯƠNG)\s+([IVXLCDM\d]+)[\.:\s]*(.*)", text)
    if chap_m:
        current_chapter = f"Chương {chap_m.group(1)}: {chap_m.group(2).strip()}"
        continue

    # Check article heading
    art_m = re.match(r"^Điều\s+(\d+)[\.:\s]*(.*)", text)
    if art_m:
        num = int(art_m.group(1))
        if current_art_num is None or num == current_art_num + 1 or num not in articles:
            if current_art_num is not None and current_art_num not in articles:
                articles[current_art_num] = {
                    "number": current_art_num,
                    "title": current_art_title,
                    "chapter": current_chapter,
                    "content": "\n".join(current_art_lines).strip(),
                }
            current_art_num = num
            current_art_title = art_m.group(2).strip()
            current_art_lines = [text]
            continue

    if current_art_num is not None:
        if not current_art_lines or text != current_art_lines[-1]:
            current_art_lines.append(text)

if current_art_num is not None and current_art_num not in articles:
    articles[current_art_num] = {
        "number": current_art_num,
        "title": current_art_title,
        "chapter": current_chapter,
        "content": "\n".join(current_art_lines).strip(),
    }

print(f"Total articles successfully extracted: {len(articles)} / 689")
empty_arts = [num for num, a in articles.items() if len(a["content"]) < 20]
print(f"Articles with < 20 chars content: {len(empty_arts)}")

for test_num in [1, 117, 328, 468, 584, 588, 611, 623, 644, 689]:
    if test_num in articles:
        a = articles[test_num]
        print(f"=== Điều {a['number']}: {a['title']} ===")
        print(f"   Chapter: {a['chapter']}")
        print(f"   Content len: {len(a['content'])} chars")
        print(f"   Snippet: {a['content'][:120]}...\n")
