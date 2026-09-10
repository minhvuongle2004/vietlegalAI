import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def find_tvpl():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        for kw in ['158/2024/NĐ-CP', '130/2024/NĐ-CP', '161/2024/NĐ-CP']:
            url = f'https://thuvienphapluat.vn/page/tim-van-ban.aspx?keyword={kw}'
            print(f"\n[*] Searching for: {kw}...")
            page.goto(url, wait_until='domcontentloaded', timeout=30000)
            page.wait_for_timeout(3000)
            
            # Extract links
            links = page.eval_on_selector_all(
                'a',
                """elements => elements
                    .map(e => ({ href: e.href, text: e.innerText }))
                    .filter(e => e.href && e.href.includes('/van-ban/'))"""
            )
            
            num = kw.split('/')[0]
            matches = [l for l in links if num in l['text'] or num in l['href']]
            print(f"  Found {len(matches)} matching links:")
            seen = set()
            for m in matches:
                h = m['href']
                if h not in seen and h.endswith('.aspx'):
                    seen.add(h)
                    print(f"    {m['text'][:70]} -> {h}")
                    if len(seen) >= 3:
                        break
        browser.close()

if __name__ == '__main__':
    find_tvpl()
