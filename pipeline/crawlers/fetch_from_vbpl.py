import requests
from pathlib import Path
import re

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
OUT_DIR = PROJECT_ROOT / "data" / "01_raw" / "html"
OUT_DIR.mkdir(parents=True, exist_ok=True)

session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
})

def search_vbpl(keyword):
    url = f"https://vbpl.vn/TW/Pages/vbpq-timkiem.aspx?k={keyword}"
    try:
        resp = session.get(url, timeout=20, allow_redirects=True)
        print(f"Final URL: {resp.url}, Status: {resp.status_code}")
        items = re.findall(r'/TW/Pages/vbpq-toanvan\.aspx\?ItemID=(\d+)', resp.text)
        return list(dict.fromkeys(items))
    except Exception as e:
        print(f"Error searching {keyword}: {e}")
        return []

def download_vbpl_doc(item_id, save_name):
    url = f"https://vbpl.vn/TW/Pages/vbpq-toanvan.aspx?ItemID={item_id}"
    print(f"Fetching {url} -> {save_name}...")
    resp = session.get(url, timeout=30, allow_redirects=True)
    out_file = OUT_DIR / save_name
    out_file.write_text(resp.text, encoding="utf-8")
    print(f"Saved {save_name} ({len(resp.text)/1024:.1f} KB)")


if __name__ == "__main__":
    import urllib.parse
    print("Searching VBPL for 58/2014/QH13...")
    res1 = search_vbpl("58/2014/QH13")
    print("Results 58/2014/QH13:", res1)
    if res1:
        download_vbpl_doc(res1[0], "58_2014_QH13.html")

    print("Searching VBPL for 38/2013/QH13...")
    res2 = search_vbpl("38/2013/QH13")
    print("Results 38/2013/QH13:", res2)
    if res2:
        download_vbpl_doc(res2[0], "38_2013_QH13.html")
