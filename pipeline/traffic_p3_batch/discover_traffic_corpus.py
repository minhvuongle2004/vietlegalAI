import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
import os
import json
import requests
from pathlib import Path
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
load_dotenv(PROJECT_ROOT / ".env")

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

def discover():
    print("=" * 90)
    print("   TRAFFIC P3 COVERAGE DISCOVERY — INGESTION GAP ANALYSIS")
    print("=" * 90)

    # 1. Fetch current documents in Supabase
    h = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}
    r = requests.get(f"{SUPABASE_URL}/rest/v1/legal_documents?select=id,official_number,short_title,doc_type,effective_date,status", headers=h)
    existing_docs = r.json()
    print(f"[*] Total legal_documents in Supabase: {len(existing_docs)}")

    print("\n--- ALL EXISTING LEGAL DOCUMENTS IN SUPABASE (37 DOCUMENTS) ---")
    traffic_keywords = ["giao thông", "đường bộ", "xe", "lái xe", "bca", "bxd", "bgtvt", "công an", "tuần tra", "sát hạch"]
    traffic_docs = []
    other_docs = []

    for d in sorted(existing_docs, key=lambda x: str(x.get("official_number", ""))):
        st = d.get("short_title") or d.get("title") or "N/A"
        off = d.get("official_number") or d.get("id")
        stat = d.get("status", "N/A")
        
        # Check if traffic
        is_traffic = any(k in st.lower() or k in off.lower() for k in traffic_keywords)
        if is_traffic or "165/2024" in off or "241/2026" in off or "89/2026" in off:
            traffic_docs.append((off, st, stat))
        else:
            other_docs.append((off, st, stat))

    print(f"\n[+] Identified {len(traffic_docs)} Traffic domain documents:")
    for off, st, stat in traffic_docs:
        print(f"    - {off:22} | {st[:45]:45} | {stat}")

    print(f"\n[+] Other domain documents ({len(other_docs)}):")
    for off, st, stat in other_docs:
        print(f"    - {off:22} | {st[:45]:45} | {stat}")

    return existing_numbers

if __name__ == "__main__":
    discover()
