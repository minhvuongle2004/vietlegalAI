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
        "filename": "36_2024_QH15.html",
        "url": "https://thuvienphapluat.vn/van-ban/Giao-thong-Van-tai/Luat-trat-tu-an-toan-giao-thong-duong-bo-2024-so-36-2024-QH15-444251.aspx",
        "title": "Luật Trật tự, an toàn giao thông đường bộ 2024 (36/2024/QH15)",
    },
    {
        "filename": "35_2024_QH15.html",
        "url": "https://thuvienphapluat.vn/van-ban/Giao-thong-Van-tai/Luat-Duong-bo-2024-588811.aspx",
        "title": "Luật Đường bộ 2024 (35/2024/QH15)",
    },
    {
        "filename": "168_2024_ND_CP.html",
        "url": "https://thuvienphapluat.vn/van-ban/Giao-thong-Van-tai/Nghi-dinh-168-2024-ND-CP-xu-phat-vi-pham-hanh-chinh-an-toan-giao-thong-duong-bo-619502.aspx",
        "title": "Nghị định 168/2024/NĐ-CP (Xử phạt vi phạm hành chính TTATGT)",
    },
    {
        "filename": "151_2024_ND_CP.html",
        "url": "https://thuvienphapluat.vn/van-ban/Giao-thong-Van-tai/Nghi-dinh-151-2024-ND-CP-huong-dan-Luat-Trat-tu-an-toan-giao-thong-duong-bo-619564.aspx",
        "title": "Nghị định 151/2024/NĐ-CP (Hướng dẫn Luật TTATGTĐB)",
    },
]


def crawl_traffic_laws():
    print("=" * 70)
    print("   PLAYWRIGHT CRAWLER: TẢI 4 VĂN BẢN CORE CỤM GIAO THÔNG")
    print("=" * 70)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080},
        )
        page = context.new_page()

        for target in TARGETS:
            out_file = OUT_DIR / target["filename"]
            print(f"\n[*] Đang truy cập: {target['title']}...")
            print(f"    URL: {target['url']}")

            try:
                page.goto(target["url"], wait_until="domcontentloaded", timeout=60000)
                page.wait_for_timeout(4000)

                # Tìm phần nội dung chính
                content_html = ""
                for selector in ["#divContentDoc", ".content1", "#content-box", ".block-content"]:
                    if page.locator(selector).count() > 0:
                        content_html = page.locator(selector).first.inner_html()
                        print(f" [+] Tìm thấy nội dung với selector: {selector}")
                        break

                if not content_html:
                    content_html = page.content()
                    print(" [!] Dùng page.content() dự phòng.")

                out_file.write_text(content_html, encoding="utf-8")
                size_kb = out_file.stat().st_size / 1024
                print(f" [+] ĐÃ LƯU THÀNH CÔNG: {out_file.name} ({size_kb:.1f} KB)")
            except Exception as e:
                print(f" [!] Lỗi khi tải {target['title']}: {e}")

        browser.close()
    print("\n[DONE] Hoàn tất quá trình tải 4 văn bản Cụm Giao thông!")


if __name__ == "__main__":
    crawl_traffic_laws()
