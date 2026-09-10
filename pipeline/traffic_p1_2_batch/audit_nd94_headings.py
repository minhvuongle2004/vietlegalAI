import re
import sys

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

with open('data/01_raw/traffic_p1_2_batch/94_2026_ND_CP.html', 'r', encoding='utf-8') as f:
    text = f.read()

pattern = re.compile(r'<b>(Điều \d+\.[^<]+)</b>')
matches = pattern.findall(text)
print(f"Total articles in 94_2026_ND_CP.html: {len(matches)}")
for i, m in enumerate(matches, 1):
    print(f"{i:2d}. {m}")
