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

TARGET = {
    "filename": "91_2015_QH13.html",
    "url": "https://thuvienphapluat.vn/van-ban/Quyen-dan-su/Bo-luat-dan-su-2015-296215.aspx",
    "title": "Bộ luật Dân sự 2015 (91/2015/QH13)",
}

def crawl_blds2015():
    print("=" * 60)
    print("   PLAYWRIGHT CRAWLER: TẢI BỘ LUẬT DÂN SỰ 2015 (91/2015/QH13)")
    print("=" * 60)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080},
        )
        page = context.new_page()

        out_file = OUT_DIR / TARGET["filename"]
        print(f"\n[*] Đang truy cập: {TARGET['title']}...")
        print(f"    URL: {TARGET['url']}")
        
        try:
            page.goto(TARGET["url"], wait_until="domcontentloaded", timeout=60000)
            page.wait_for_timeout(5000)

            # Tìm phần nội dung chính
            content_html = ""
            for selector in ["#content-box", ".content1", ".block-content", "div.news-content", "#divContentDoc"]:
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
            print(f" [!] Lỗi khi tải {TARGET['title']}: {e}")

        browser.close()
    print("\n[DONE] Hoàn tất quá trình crawl Bộ luật Dân sự 2015!")

if __name__ == "__main__":
    crawl_blds2015()
