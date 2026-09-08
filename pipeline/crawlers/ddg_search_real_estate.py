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
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

queries = [
    "site:thuvienphapluat.vn Luat Dat dai 31/2024/QH15",
    "site:thuvienphapluat.vn Luat Nha o 27/2023/QH15",
    "site:thuvienphapluat.vn Luat Kinh doanh bat dong san 29/2023/QH15",
    "site:thuvienphapluat.vn Luat Dau tu 61/2020/QH14"
]

for q in queries:
    url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(q)}"
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=15) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
            urls = re.findall(r'href="([^"]*thuvienphapluat\.vn/van-ban/[^"]+)"', html)
            print(f"\nQuery: {q}")
            for u in urls[:5]:
                actual = re.findall(r'uddg=([^&]+)', u)
                if actual:
                    actual_url = urllib.parse.unquote(actual[0])
                    print(f"  -> {actual_url}")
                else:
                    print(f"  -> {u}")
    except Exception as e:
        print(f"Error {q}: {e}")
