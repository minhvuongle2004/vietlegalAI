import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
import urllib.request
import re

url = "https://chinhphu.vn/tim-kiem?keyword=241%2F2026%2FN%C4%90-CP"
req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
try:
    with urllib.request.urlopen(req) as resp:
        html = resp.read().decode("utf-8", errors="ignore")
        print("HTML length:", len(html))
        # Tìm các link văn bản hoặc pdf
        links = re.findall(r'href="([^"]+)"', html)
        print("All hrefs count:", len(links))
        for l in links[:20]:
            print("Link:", l)
except Exception as e:
    print("Error:", e)
