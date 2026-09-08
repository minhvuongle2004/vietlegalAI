import sys
import requests
from bs4 import BeautifulSoup
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

targets = [
    {
        "url": "https://thuvienphapluat.vn/van-ban/Bat-dong-san/Luat-Dat-dai-2024-31-2024-QH15-523642.aspx",
        "output": "data/01_raw/html/31_2024_QH15.html",
        "name": "Luật Đất đai 31/2024/QH15"
    },
    {
        "url": "https://thuvienphapluat.vn/van-ban/Bat-dong-san/Luat-Nha-o-27-2023-QH15-528669.aspx",
        "output": "data/01_raw/html/27_2023_QH15.html",
        "name": "Luật Nhà ở 27/2023/QH15"
    },
    {
        "url": "https://thuvienphapluat.vn/van-ban/Bat-dong-san/Luat-Kinh-doanh-bat-dong-san-29-2023-QH15-530116.aspx",
        "output": "data/01_raw/html/29_2023_QH15.html",
        "name": "Luật Kinh doanh BĐS 29/2023/QH15"
    },
    {
        "url": "https://thuvienphapluat.vn/van-ban/Doanh-nghiep/Luat-Dau-tu-so-61-2020-QH14-321051.aspx",
        "output": "data/01_raw/html/61_2020_QH14.html",
        "name": "Luật Đầu tư 61/2020/QH14"
    }
]

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7",
    "Referer": "https://www.google.com/",
}

session = requests.Session()

for target in targets:
    print(f"\nFetching {target['name']}...")
    try:
        r = session.get(target["url"], headers=headers, timeout=30)
        print(f"  Status: {r.status_code}, Length: {len(r.text)}")
        soup = BeautifulSoup(r.text, "html.parser")
        content_div = (
            soup.find(id="toanvancontent")
            or soup.find(id="divContentDoc")
            or soup.find("div", class_="content1")
            or soup.find(id="content-box")
        )
        out_file = Path(target["output"])
        out_file.parent.mkdir(parents=True, exist_ok=True)
        if content_div:
            out_file.write_text(str(content_div), encoding="utf-8")
            print(f"  [+] Saved content_div ({len(str(content_div))} bytes) to {target['output']}")
        else:
            print(f"  [-] Div not found. Title: {soup.title.text if soup.title else 'None'}")
            if len(r.text) > 10000:
                out_file.write_text(r.text, encoding="utf-8")
                print(f"  [+] Saved full page ({len(r.text)} bytes) to {target['output']}")
    except Exception as e:
        print(f"  [-] Error: {e}")
