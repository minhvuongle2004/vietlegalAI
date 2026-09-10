import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
import fitz

def analyze_pdf(pdf_path):
    print(f"=== Analyzing {pdf_path} ===")
    doc = fitz.open(pdf_path)
    print("Page count:", len(doc))
    total_chars = 0
    pages_with_text = 0
    pages_with_images = 0
    
    for i, page in enumerate(doc):
        text = page.get_text()
        total_chars += len(text.strip())
        if len(text.strip()) > 50:
            pages_with_text += 1
        imgs = page.get_images()
        if imgs:
            pages_with_images += 1
            
    print(f"Total chars: {total_chars}")
    print(f"Pages with >50 chars text: {pages_with_text}/{len(doc)}")
    print(f"Pages with images: {pages_with_images}/{len(doc)}")
    
    # Print sample from first page with text
    for i, page in enumerate(doc):
        t = page.get_text().strip()
        if t:
            print(f"--- Sample Page {i} (len {len(t)}) ---")
            print(t[:300])
            break

analyze_pdf("data/01_raw/traffic_p2_batch/165_2024_ND_CP/165_2024_nd-cp_26122024-signed.pdf")
analyze_pdf("data/01_raw/traffic_p2_batch/165_2024_ND_CP/165-pl1.pdf")
