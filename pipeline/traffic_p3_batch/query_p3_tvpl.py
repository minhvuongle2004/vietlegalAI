import urllib.request
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def find_links(keyword):
    encoded = urllib.parse.quote(keyword)
    url = f"https://thuvienphapluat.vn/page/tim-van-ban.aspx?keyword={encoded}"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            html = resp.read().decode("utf-8", errors="ignore")
            pattern = re.compile(r'href=["\'](https://thuvienphapluat\.vn/van-ban/[^"\']+)["\']')
            matches = pattern.findall(html)
            print(f"Keyword: {keyword} -> Found {len(matches)} links:")
            for m in list(dict.fromkeys(matches))[:5]:
                print("  ", m)
    except Exception as e:
        print(f"Error querying {keyword}: {e}")

if __name__ == "__main__":
    import urllib.parse
    find_links("158/2024/NĐ-CP")
    find_links("130/2024/NĐ-CP")
    find_links("161/2024/NĐ-CP")
