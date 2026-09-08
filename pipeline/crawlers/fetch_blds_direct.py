import sys
import requests
from bs4 import BeautifulSoup
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

url = "https://thuvienphapluat.vn/van-ban/Quyen-dan-su/Bo-luat-dan-su-2015-296215.aspx"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7",
    "Referer": "https://www.google.com/",
}

session = requests.Session()
r = session.get(url, headers=headers, timeout=25)
print(f"Status: {r.status_code}, Length: {len(r.text)}")

soup = BeautifulSoup(r.text, "html.parser")
content_div = (
    soup.find(id="toanvancontent")
    or soup.find(id="divContentDoc")
    or soup.find("div", class_="content1")
    or soup.find(id="content-box")
)

if content_div:
    out_file = Path("data/01_raw/html/91_2015_QH13.html")
    out_file.parent.mkdir(parents=True, exist_ok=True)
    out_file.write_text(str(content_div), encoding="utf-8")
    print(f"[+] SUCCESSFULLY saved HTML! Size: {len(str(content_div))} bytes")
else:
    print(f"[-] Content div not found. Title: {soup.title.text if soup.title else 'None'}")
