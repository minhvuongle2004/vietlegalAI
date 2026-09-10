import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
import fitz
import os

doc = fitz.open("data/01_raw/traffic_p2_batch/165_2024_ND_CP/165-pl1.pdf")
print("Total pages in 165-pl1.pdf:", len(doc))

# Let's see if we can check text or if there is any OCR or embedded text
for i in range(min(5, len(doc))):
    page = doc[i]
    print(f"Page {i+1} rect:", page.rect)
