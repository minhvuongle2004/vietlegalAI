import sys
import time
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from playwright.sync_api import sync_playwright

OUT_DIR = PROJECT_ROOT / "data" / "01_raw" / "html"
OUT_DIR.mkdir(parents=True, exist_ok=True)

TARGETS = [
    {
        "filename": "58_2014_QH13.html",
        "url": "https://thuvienphapluat.vn/van-ban/Bao-hiem/Luat-Bao-hiem-xa-hoi-2014-259700.aspx",
        "title": "Luật Bảo hiểm xã hội 2014",
    },
    {
        "filename": "38_2013_QH13.html",
        "url": "https://thuvienphapluat.vn/van-ban/Lao-dong-Tien-luong/Luat-viec-lam-nam-2013-215628.aspx",
        "title": "Luật Việc làm 2013",
    },
]

def crawl_laws():
    print("=" * 60)
    print("   PLAYWRIGHT CRAWLER: TẢI TOÀN VĂN LUẬT CỤM 3")
    print("=" * 60)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080},
        )
        page = context.new_page()

        for item in TARGETS:
            out_file = OUT_DIR / item["filename"]
            print(f"\n[*] Đang truy cập: {item['title']}...")
            print(f"    URL: {item['url']}")
            
            try:
                page.goto(item["url"], wait_until="domcontentloaded", timeout=45000)
                page.wait_for_timeout(3000)

                # Tìm phần nội dung chính
                content_html = ""
                for selector in ["#content-box", ".content1", ".block-content", "div.news-content"]:
                    if page.locator(selector).count() > 0:
                        content_html = page.locator(selector).first.inner_html()
                        print(f" [+] Tìm thấy nội dung với selector: {selector}")
                        break

                if not content_html:
                    content_html = page.content()
                    print(" [!] Dùng page.content() đầy đủ.")

                out_file.write_text(content_html, encoding="utf-8")
                size_kb = out_file.stat().st_size / 1024
                print(f" [+] ĐÃ LƯU THÀNH CÔNG: {out_file.name} ({size_kb:.1f} KB)")
            except Exception as e:
                print(f" [!] Lỗi khi tải {item['title']}: {e}")

        browser.close()
    print("\n[DONE] Hoàn tất quá trình crawl dữ liệu Cụm 3!")

if __name__ == "__main__":
    crawl_laws()
