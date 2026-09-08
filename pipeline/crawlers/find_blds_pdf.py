import requests
import re
from bs4 import BeautifulSoup

url = 'https://vanban.chinhphu.vn/default.aspx?pageid=27160&docid=183188'
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

r = requests.get(url, headers=headers, timeout=20)
print('Status:', r.status_code)
soup = BeautifulSoup(r.text, 'html.parser')
for a in soup.find_all('a', href=True):
    href = a['href']
    if any(ext in href.lower() for ext in ['.pdf', '.doc', '.docx', 'download', 'toanvan']):
        print(f"Link: {a.text.strip()} -> {href}")
