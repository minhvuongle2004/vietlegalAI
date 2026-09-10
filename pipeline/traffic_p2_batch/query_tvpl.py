import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
import urllib.request
import re

url = "https://thuvienphapluat.vn/page/tim-van-ban.aspx?keyword=165/2024/N%C4%90-CP"
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
req = urllib.request.Request(url, headers=headers)
try:
    with urllib.request.urlopen(req) as resp:
        html = resp.read().decode("utf-8", errors="ignore")
        print("Length:", len(html))
        links = re.findall(r'href=["\'](https://thuvienphapluat\.vn/van-ban/[^"\']+)["\']', html)
        print("Links count:", len(links))
        for l in set(links):
            if "165-2024" in l:
                print("Found:", l)
except Exception as e:
    print("Error:", e)
