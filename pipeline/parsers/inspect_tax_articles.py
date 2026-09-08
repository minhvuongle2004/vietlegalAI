import sys
sys.path.insert(0, ".")
from pipeline.parsers.test_tax_parser import parse_html_document

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

docs = [
    ("data/01_raw/html/109_2025_QH15.html", "tncn_109_2025_qh15", "Luật Thuế TNCN 109/2025/QH15", 29),
    ("data/01_raw/html/67_2025_QH15.html", "tndn_67_2025_qh15", "Luật Thuế TNDN 67/2025/QH15", 20),
    ("data/01_raw/html/108_2025_QH15.html", "qlt_108_2025_qh15", "Luật Quản lý thuế 108/2025/QH15", 53)
]

for path, doc_id, name, max_art in docs:
    arts = parse_html_document(path, doc_id)
    # filter to exact max_art
    arts = [a for a in arts if a["article_number"] <= max_art]
    # deduplicate by article_number keeping first
    seen = set()
    cleaned = []
    for a in arts:
        if a["article_number"] not in seen:
            seen.add(a["article_number"])
            cleaned.append(a)
    cleaned.sort(key=lambda x: x["article_number"])
    print(f"\n================ {name} ({len(cleaned)} articles) ================")
    for a in cleaned:
        content_preview = " ".join(a["lines"][:2])[:80]
        print(f"Điều {a['article_number']}: {a['title']} | {content_preview}...")
