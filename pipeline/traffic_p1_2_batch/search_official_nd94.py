import sys
from pathlib import Path
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
from playwright.sync_api import sync_playwright

def search_official():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        
        # 1. Search chinhphu.vn
        print("[*] Searching chinhphu.vn for 94/2026/ND-CP...")
        search_url = "https://chinhphu.vn/tim-kiem?keyword=94%2F2026%2FN%C4%90-CP"
        try:
            page.goto(search_url, timeout=30000, wait_until="domcontentloaded")
            page.wait_for_timeout(3000)
            links = page.locator("a").all()
            print(f"Total links on chinhphu search: {len(links)}")
            for l in links:
                try:
                    href = l.get_attribute("href") or ""
                    text = l.inner_text().strip()
                    if any(k in text.lower() for k in ["94", "sát hạch", "đào tạo", "lái xe", "nghị định"]):
                        print(f"  CP: {text[:60]} --> {href}")
                except:
                    pass
        except Exception as e:
            print(f"Chinhphu error: {e}")

        # 3. Search thuvienphapluat.vn
        print("\n[*] Searching thuvienphapluat.vn...")
        tvpl_url = "https://thuvienphapluat.vn/page/tim-van-ban.aspx?keyword=94%2F2026%2FN%C4%90-CP"
        try:
            page.goto(tvpl_url, timeout=30000, wait_until="domcontentloaded")
            page.wait_for_timeout(3000)
            links = page.locator("a").all()
            print(f"Total links on TVPL search: {len(links)}")
            for l in links:
                try:
                    href = l.get_attribute("href") or ""
                    text = l.inner_text().strip()
                    if "94" in text or "sát hạch" in text.lower() or "đào tạo" in text.lower():
                        print(f"  TVPL: {text[:70]} --> {href}")
                except:
                    pass
        except Exception as e:
            print(f"TVPL error: {e}")

        browser.close()

if __name__ == "__main__":
    search_official()
