import json
import glob
import sys

sys.stdout.reconfigure(encoding='utf-8')

file_path = glob.glob('data/03_parsed/*.json')[0]
with open(file_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f"Tổng số chương: {len(data['chapters'])}")
total_articles = sum(len(c['articles']) for c in data['chapters'])
print(f"Tổng số điều: {total_articles}")

for c in data['chapters']:
    first_art = c['articles'][0]['article_number']
    last_art = c['articles'][-1]['article_number']
    count = len(c['articles'])
    name = c.get('title') or c.get('chapter_title') or c.get('name')
    print(f"- Chương {c.get('chapter_number')}: {name} (Điều {first_art} - {last_art}, {count} điều)")
