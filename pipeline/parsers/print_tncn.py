import sys
sys.path.insert(0, ".")
from pipeline.parsers.test_tax_parser import parse_html_document

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

arts = parse_html_document("data/01_raw/html/109_2025_QH15.html", "tncn_109_2025_qh15")
print(f"Total parsed: {len(arts)}")
for a in arts[:29]:
    print(f"Điều {a['article_number']}: {a['title']}")
