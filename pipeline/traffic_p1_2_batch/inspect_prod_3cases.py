import json
import sys

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

with open('data/03_parsed/traffic_p1_2_batch/production_reference_results.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

for res in data.get('detailed_results', []):
    cid = res.get('test_case_id')
    if cid in ['TC-DOM-GPLX-01', 'TC-DOM-CONTRAST-01A', 'TC-DOM-GPLX-02']:
        print("="*60)
        print(f"CASE: {cid}")
        print(f"Query: {res.get('query')}")
        print(f"Rank in Production: {res.get('rank')}")
        print(f"Matched: {res.get('matched_doc')}")
        print("Top 5 candidates in Production:")
        for cand in res.get('top5_candidates', []):
            print(f"   Rank {cand.get('rank')} (score={cand.get('score')}): {cand.get('official_number')} {cand.get('article')} {cand.get('clause')} - {cand.get('text_preview')[:80]}")
