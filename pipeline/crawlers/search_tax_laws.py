import urllib.request
import urllib.parse
import json
import ssl
import re

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

laws_to_find = [
    {"code": "109/2025/QH15", "name": "Thuế thu nhập cá nhân"},
    {"code": "67/2025/QH15", "name": "Thuế thu nhập doanh nghiệp"},
    {"code": "108/2025/QH15", "name": "Quản lý thuế"}
]

for law in laws_to_find:
    query = urllib.parse.quote(f"{law['code']} {law['name']}")
    url = f"https://thuvienphapluat.vn/tim-van-ban.aspx?keyword={query}"
    print(f"\nSearching for {law['code']} on TVPL...")
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, context=ctx, timeout=10) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
            links = re.findall(r'href="(https://thuvienphapluat\.vn/van-ban/[^"]+)"', html)
            if not links:
                links = re.findall(r'href="(/van-ban/[^"]+)"', html)
                links = ["https://thuvienphapluat.vn" + l for l in links]
            print(f"Found {len(links)} links:")
            for l in set(links[:10]):
                print(f"  - {l}")
    except Exception as e:
        print(f"Error searching TVPL: {e}")
