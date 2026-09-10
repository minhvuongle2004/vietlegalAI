import json
import sys

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

with open('data/03_parsed/traffic_p1_2_batch/staging_frozen_baseline_protocol_results.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

for res in data.get('detailed_results', []):
    cid = res.get('test_case_id')
    if cid in ['TC-DOM-GPLX-01', 'TC-DOM-CONTRAST-01A', 'TC-DOM-GPLX-02']:
        print("="*70)
        print(f"CASE: {cid}")
        print(f"Query: {res.get('query')}")
        print(f"As of date: {res.get('as_of_date')}")
        print(f"Expected docs: {res.get('expected_documents')}")
        print(f"Expected primary evidence: {res.get('expected_primary_evidence')}")
        print(f"Rank achieved: {res.get('rank')}")
        print("Top 5 candidates:")
        for cand in res.get('top5_candidates', []):
            print(f"  Rank {cand.get('rank')} (score={cand.get('score')}):")
            print(f"       doc: {cand.get('official_number')}")
            print(f"       article: {cand.get('article')}")
            print(f"       clause: {cand.get('clause')}")
            print(f"       preview: {cand.get('text_preview')}")
