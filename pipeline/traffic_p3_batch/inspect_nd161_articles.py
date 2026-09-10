import json
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

with open("data/03_parsed/traffic_p3_batch/nd161_2024_full_33_articles.json", "r", encoding="utf-8") as f:
    arts = json.load(f)

for num in [14, 19, 23, 27]:
    a = next(x for x in arts if x["article_number"] == num)
    print(f"=== ĐIỀU {num}: {a['article_title']} ===")
    print(a["full_text"])
    print("\n" + "="*50 + "\n")
