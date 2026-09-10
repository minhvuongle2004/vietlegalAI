import json
import sys
import re
from pathlib import Path
from bs4 import BeautifulSoup

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

raw_path = Path("data/01_raw/traffic_p1_2_batch/94_2026_ND_CP.html")
parsed_chunks_path = Path("data/03_parsed/traffic_p1_2_batch/all_traffic_p1_2_chunks.json")

# 1. Read RAW
raw_html = raw_path.read_text(encoding="utf-8")
soup = BeautifulSoup(raw_html, "html.parser")
doc_body = soup.find("div", class_="doc-body")

raw_articles = {}
for p in doc_body.find_all("p"):
    b_tag = p.find("b")
    if b_tag:
        text = b_tag.get_text(strip=True)
        m = re.match(r"^Điều\s+(\d+)\.\s*(.*)", text)
        if m:
            art_num = f"Điều {m.group(1)}"
            art_title = m.group(2).strip()
            raw_articles[art_num] = {
                "title": art_title,
                "raw_heading": text,
                "full_p": p.get_text(strip=True)
            }

print(f"Total raw articles parsed from HTML: {len(raw_articles)}")

# 2. Read parsed chunks
with open(parsed_chunks_path, "r", encoding="utf-8") as f:
    chunks = json.load(f)

nd94_chunks = [c for c in chunks if c.get("official_number") == "94/2026/NĐ-CP"]
print(f"Total ND 94 chunks: {len(nd94_chunks)}")

audit_results = []
contamination_found = []
shifted_numbering = []
wrong_provenance = []
heading_mismatch = []

for idx, c in enumerate(nd94_chunks, 1):
    art_num = c.get("article")
    art_title = c.get("article_title")
    content = c.get("text", "")
    source_url = c.get("source_url")
    doc_id = c.get("document_id")
    clause_num = c.get("clause")
    
    # Check 1: Document mapping & Provenance
    if doc_id != "traffic_driver_training_94_2026_nd_cp":
        wrong_provenance.append((c.get("chunk_id"), f"Wrong doc_id: {doc_id}"))
        
    if source_url != "https://chinhphu.vn/van-ban-chinh-phu-94-2026-ND-CP":
        wrong_provenance.append((c.get("chunk_id"), f"Wrong source_url: {source_url}"))

    # Check 2: Article exists in raw
    if art_num not in raw_articles:
        shifted_numbering.append((c.get("chunk_id"), f"Article {art_num} not in raw HTML"))
        continue

    # Check 3: Heading match
    raw_info = raw_articles[art_num]
    if raw_info["title"] != art_title:
        heading_mismatch.append((c.get("chunk_id"), f"Parsed: '{art_title}' vs Raw: '{raw_info['title']}'"))

    # Check 4: Contamination check (specifically simulation exam in ND 94)
    forbidden_terms = ["10 tình huống", "35/50", "5 điểm/tình huống", "đạt 35/50"]
    for term in forbidden_terms:
        if term in content:
            contamination_found.append((c.get("chunk_id"), art_num, term))

    # Specific check for Article 26:
    if art_num == "Điều 26":
        expected_title = "Giấy phép sát hạch, thẩm quyền cấp, cấp lại và thu hồi giấy phép sát hạch"
        if art_title != expected_title:
            heading_mismatch.append((c.get("chunk_id"), f"Dieu 26 title mismatch: '{art_title}' vs expected '{expected_title}'"))
        if "10 tình huống" in content or "mô phỏng" in content:
            contamination_found.append((c.get("chunk_id"), art_num, "simulation text in Điều 26"))

    audit_results.append({
        "chunk_id": c.get("chunk_id"),
        "article_number": art_num,
        "article_title": art_title,
        "clause_number": clause_num,
        "raw_heading": raw_info["raw_heading"],
        "status": "PASS"
    })

print("="*70)
print("TASK 4 — AUTOMATED SOURCE ALIGNMENT AUDIT RESULT:")
print(f"Total chunks audited: {len(nd94_chunks)}")
print(f"Map đúng Article: {len(audit_results)}/{len(nd94_chunks)}")
print(f"Map đúng Source Document: {len(nd94_chunks) - len(wrong_provenance)}/{len(nd94_chunks)}")
print(f"Heading Mismatches: {len(heading_mismatch)}")
print(f"Contamination Found: {len(contamination_found)}")
print(f"Shifted Article Numbering: {len(shifted_numbering)}")
print(f"Wrong Provenance: {len(wrong_provenance)}")

if contamination_found:
    print("\n[!] CONTAMINATION DETAILS:")
    for item in contamination_found:
        print(f"   {item}")

if heading_mismatch:
    print("\n[!] HEADING MISMATCH DETAILS:")
    for item in heading_mismatch:
        print(f"   {item}")

# Dump report
report = {
    "batch": "traffic_p1_2_batch",
    "document": "94/2026/NĐ-CP",
    "total_chunks": len(nd94_chunks),
    "valid_mapped_chunks": len(audit_results),
    "heading_mismatches_count": len(heading_mismatch),
    "contamination_count": len(contamination_found),
    "shifted_numbering_count": len(shifted_numbering),
    "wrong_provenance_count": len(wrong_provenance),
    "audit_verdict": "PASS" if len(audit_results) == 111 and len(contamination_found) == 0 and len(shifted_numbering) == 0 and len(wrong_provenance) == 0 and len(heading_mismatch) == 0 else "FAIL",
    "article_26_chunks": [c for c in nd94_chunks if c.get("article") == "Điều 26"]
}

with open("data/03_parsed/traffic_p1_2_batch/nd94_source_alignment_audit_report.json", "w", encoding="utf-8") as f:
    json.dump(report, f, ensure_ascii=False, indent=2)

print(f"\nAudit Report saved to: data/03_parsed/traffic_p1_2_batch/nd94_source_alignment_audit_report.json")
print(f"VERDICT: {report['audit_verdict']}")
print("="*70)
