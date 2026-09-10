import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
import urllib.request
import re

url = "https://vanban.chinhphu.vn/?pageid=27160&docid=212168&classid=1"
req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
with urllib.request.urlopen(req) as resp:
    html = resp.read().decode("utf-8", errors="ignore")
    # Find all table rows or blocks mentioning attachments / file names
    matches = re.findall(r'(<tr[^>]*>.*?</tr>)', html, re.DOTALL)
    for row in matches:
        if "pdf" in row.lower() or "tệp" in row.lower() or "dính kèm" in row.lower() or "pl" in row.lower():
            # strip tags
            text = re.sub(r'<[^>]+>', ' ', row)
            text = re.sub(r'\s+', ' ', text).strip()
            print("Row:", text)
            
    # Find all links ending with pdf/doc
    links = re.findall(r'href=["\']([^"\']+)["\']', html)
    for l in set(links):
        if any(l.lower().endswith(x) for x in ['.pdf', '.doc', '.docx', '.zip', '.rar']):
            print("File link:", l)
