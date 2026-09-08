import sys
import requests
from bs4 import BeautifulSoup
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

targets = [
    {
        "url": "https://thuvienphapluat.vn/van-ban/Thue-Phi-Le-Phi/Luat-Thue-thu-nhap-ca-nhan-2025-so-109-2025-QH15-665870.aspx",
        "output": "data/01_raw/html/109_2025_QH15.html",
        "name": "Luật Thuế TNCN 109/2025/QH15"
    },
    {
        "url": "https://thuvienphapluat.vn/van-ban/Doanh-nghiep/Luat-Thue-thu-nhap-doanh-nghiep-2025-so-67-2025-QH15-580594.aspx",
        "output": "data/01_raw/html/67_2025_QH15.html",
        "name": "Luật Thuế TNDN 67/2025/QH15"
    },
    {
        "url": "https://thuvienphapluat.vn/van-ban/Thue-Phi-Le-Phi/Luat-Quan-ly-thue-2025-so-108-2025-QH15-675268.aspx",
        "output": "data/01_raw/html/108_2025_QH15.html",
        "name": "Luật Quản lý thuế 108/2025/QH15"
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
    print(f"Fetching {target['name']}...")
    try:
        r = session.get(target["url"], headers=headers, timeout=25)
        print(f"  Status: {r.status_code}, Length: {len(r.text)}")
        soup = BeautifulSoup(r.text, "html.parser")
        content_div = (
            soup.find(id="toanvancontent")
            or soup.find(id="divContentDoc")
            or soup.find("div", class_="content1")
            or soup.find(id="content-box")
        )
        if content_div:
            out_file = Path(target["output"])
            out_file.parent.mkdir(parents=True, exist_ok=True)
            out_file.write_text(str(content_div), encoding="utf-8")
            print(f"  [+] Saved {len(str(content_div))} bytes to {target['output']}")
        else:
            print(f"  [-] Div not found. Title: {soup.title.text if soup.title else 'None'}")
            # If whole text was returned anyway:
            if len(r.text) > 10000:
                out_file = Path(target["output"])
                out_file.write_text(r.text, encoding="utf-8")
                print(f"  [+] Saved full page {len(r.text)} bytes to {target['output']}")
    except Exception as e:
        print(f"  [-] Error: {e}")
