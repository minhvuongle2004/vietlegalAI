import sys
sys.path.append(".")
from pipeline.parsers.test_real_estate_parser import parse_html_document
from collections import Counter

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

docs = [
    ("data/01_raw/html/31_2024_QH15.html", "land_31_2024_qh15", 260),
    ("data/01_raw/html/27_2023_QH15.html", "housing_27_2023_qh15", 198),
    ("data/01_raw/html/29_2023_QH15.html", "re_business_29_2023_qh15", 83),
    ("data/01_raw/html/61_2020_QH14.html", "investment_61_2020_qh14", 77),
]

for html_path, prefix, max_art in docs:
    arts = parse_html_document(html_path, prefix)
    counts = Counter([a["article_number"] for a in arts])
    dups = {k: v for k, v in counts.items() if v > 1}
    print(f"\n--- {prefix} (Max: {max_art}) ---")
    print(f"Total parsed: {len(arts)}, Duplicates: {len(dups)}")
    for num, count in list(dups.items())[:10]:
        matching = [a for a in arts if a["article_number"] == num]
        print(f"  Article {num} appeared {count} times:")
        for m in matching:
            print(f"    - Title: {repr(m['title'][:60])} | lines: {len(m['lines'])}")
