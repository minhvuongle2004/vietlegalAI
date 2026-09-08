import sys
sys.path.insert(0, ".")
from pipeline.parsers.test_tax_parser import parse_html_document

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

arts = parse_html_document("data/01_raw/html/108_2025_QH15.html", "qlt_108_2025_qh15")
for a in arts:
    if a["article_number"] in [12, 13, 14, 16]:
        print(f"\n================ Điều {a['article_number']}: {a['title']} ================")
        print("\n".join(a["lines"][:25]))
