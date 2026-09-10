import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
import json

with open("data/gold_evaluation/retrieval_failure_diagnosis.json", "r", encoding="utf-8") as f:
    diag = json.load(f)

cases = diag["cases"]

print(f"Total diagnosis cases: {len(cases)}")

# Find cases where root_cause is option 6
strict_cases = [c for c in cases if "quá chặt" in c.get("root_cause", "")]
print(f"Count of strict label cases: {len(strict_cases)}")

for sc in strict_cases:
    print(f"[{sc['test_case_id']}] Q: {sc['query'][:70]}...")
    print(f"   Expected: {sc['expected_evidence']['official_number']} Đ{sc['expected_evidence']['article']}")
    print(f"   Dense Rank: {sc.get('dense_rank')} | Dense Top1: {sc.get('dense_top3', [''])[0]}")
    print(f"   Diagnosis: {sc.get('diagnosis_notes')}")
    print()
