import json
import sys

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

with open('data/03_parsed/traffic_p1_2_batch/traffic_driver_training_94_2026_nd_cp.json', 'r', encoding='utf-8') as f:
    doc = json.load(f)

print('Doc:', doc.get('official_number'))
print('Total articles:', len(doc.get('articles', [])))
total_clauses = 0
for a in doc.get('articles', []):
    num_clauses = len(a.get('clauses', []))
    total_clauses += num_clauses
    print(f"{a.get('article_number')}: {num_clauses} clauses - {a.get('title')}")
print('Total clauses in ND 94:', total_clauses)
