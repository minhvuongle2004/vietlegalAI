import urllib.request
import urllib.parse
import ssl
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
}

laws_to_find = [
    {"code": "31/2024/QH15", "name": "Luật Đất đai 2024"},
    {"code": "27/2023/QH15", "name": "Luật Nhà ở 2023"},
    {"code": "29/2023/QH15", "name": "Luật Kinh doanh bất động sản 2023"},
    {"code": "61/2020/QH14", "name": "Luật Đầu tư 2020"}
]

for law in laws_to_find:
    query = urllib.parse.quote(f"{law['code']}")
    url = f"https://thuvienphapluat.vn/tim-van-ban.aspx?keyword={query}"
    print(f"\nSearching for {law['name']} ({law['code']}) on TVPL...")
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, context=ctx, timeout=15) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
            links = re.findall(r'href="(https://thuvienphapluat\.vn/van-ban/[^"]+)"', html)
            if not links:
                raw_links = re.findall(r'href="(/van-ban/[^"]+)"', html)
                links = ["https://thuvienphapluat.vn" + l for l in raw_links]
            unique_links = []
            for l in links:
                if l not in unique_links and ".aspx" in l:
                    unique_links.append(l)
            print(f"Found {len(unique_links)} links:")
            for l in unique_links[:5]:
                print(f"  - {l}")
    except Exception as e:
        print(f"Error searching TVPL: {e}")
