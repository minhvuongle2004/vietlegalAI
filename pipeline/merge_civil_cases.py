import json
from pathlib import Path
from pipeline.test_civil_law_cases import CIVIL_TEST_CASES

benchmark_path = Path("evals/vietlegal_benchmark.json")

with open(benchmark_path, "r", encoding="utf-8") as f:
    cases = json.load(f)

print(f"Current benchmark cases count: {len(cases)}")
existing_ids = {c["id"] for c in cases}

for tc in CIVIL_TEST_CASES:
    if tc["id"] not in existing_ids:
        cases.append(tc)
        print(f" [+] Added {tc['id']}: {tc['title']}")
    else:
        print(f" [!] Already exists: {tc['id']}")

with open(benchmark_path, "w", encoding="utf-8") as f:
    json.dump(cases, f, ensure_ascii=False, indent=2)

print(f"[+] Total benchmark cases after merge: {len(cases)}")
