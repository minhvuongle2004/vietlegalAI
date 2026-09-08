import requests
import re
import urllib.parse
from bs4 import BeautifulSoup
from pathlib import Path

SAVE_DIR = Path("data/01_raw/html")
SAVE_DIR.mkdir(parents=True, exist_ok=True)

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def search_vbpl(keyword):
    search_url = f"https://vbpl.vn/TW/Pages/vbpq-timkiem.aspx?KeySearch={urllib.parse.quote(keyword)}"
    r = requests.get(search_url, headers=headers, timeout=10)
    links = re.findall(r'href=["\'](/TW/Pages/vbpq-toanvan\.aspx\?ItemID=(\d+))', r.text)
    print(f"Keyword '{keyword}' found: {links}")
    return links

def download_vbpl(item_id, filename):
    url = f"https://vbpl.vn/TW/Pages/vbpq-toanvan.aspx?ItemID={item_id}"
    r = requests.get(url, headers=headers, timeout=15)
    soup = BeautifulSoup(r.text, 'html.parser')
    # find content div
    content_div = soup.find('div', class_='fulltext') or soup.find('div', id='toanvancontent') or soup.body
    text = str(content_div)
    out_path = SAVE_DIR / filename
    out_path.write_text(text, encoding='utf-8')
    print(f"[+] Saved {len(text)} chars to {out_path}")

if __name__ == '__main__':
    search_vbpl("41/2024/QH15")
    search_vbpl("51/2024/QH15")
