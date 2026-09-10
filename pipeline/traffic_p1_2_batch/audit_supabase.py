import os
import sys
import json
from pathlib import Path
import requests

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from dotenv import load_dotenv
load_dotenv(PROJECT_ROOT / ".env")

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")

P1_2_DOCS = [
    {
        "doc_id": "traffic_driver_training_94_2026_nd_cp",
        "official_number": "94/2026/NĐ-CP",
        "name": "NĐ 94/2026/NĐ-CP",
        "expected_articles": 43
    },
    {
        "doc_id": "traffic_road_infra_amendment_241_2026_nd_cp",
        "official_number": "241/2026/NĐ-CP",
        "name": "NĐ 241/2026/NĐ-CP",
        "expected_articles": 4
    },
    {
        "doc_id": "traffic_inspection_amendment_45_2026_tt_bxd",
        "official_number": "45/2026/TT-BXD",
        "name": "TT 45/2026/TT-BXD",
        "expected_articles": 4
    },
    {
        "doc_id": "traffic_road_signs_qcvn41_51_2024_tt_bgtvt",
        "official_number": "51/2024/TT-BGTVT",
        "name": "TT 51/2024/TT-BGTVT",
        "expected_articles": 2
    }
]

def run_audit():
    print("=" * 80)
    print("   TASK 1: AUDIT SUPABASE (POSTGRESQL / REST API)")
    print("=" * 80)
    print(f"[*] Supabase URL: {SUPABASE_URL}")

    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
    }

    # 1. Tổng số legal_documents
    try:
        r_docs = requests.get(
            f"{SUPABASE_URL}/rest/v1/legal_documents?select=id,official_number,title,created_at",
            headers=headers,
            timeout=10
        )
        if r_docs.status_code == 200:
            all_docs = r_docs.json()
            print(f"[+] Total legal_documents in Supabase: {len(all_docs)}")
            doc_id_map = {d["id"]: d for d in all_docs}
            doc_num_map = {d["official_number"]: d for d in all_docs}
        else:
            print(f"[!] Error fetching legal_documents: {r_docs.status_code} {r_docs.text}")
            all_docs = []
            doc_id_map = {}
            doc_num_map = {}
    except Exception as e:
        print(f"[!] Exception fetching legal_documents: {e}")
        all_docs = []
        doc_id_map = {}
        doc_num_map = {}

    # 2. Tổng số legal_articles
    try:
        # Dùng HEAD hoặc count header
        r_arts_count = requests.get(
            f"{SUPABASE_URL}/rest/v1/legal_articles?select=id",
            headers={**headers, "Range-Unit": "items", "Prefer": "count=exact"},
            params={"limit": 1},
            timeout=10
        )
        content_range = r_arts_count.headers.get("Content-Range", "")
        print(f"[+] Total legal_articles count header: {content_range}")
    except Exception as e:
        print(f"[!] Exception fetching count: {e}")

    # 3. Kiểm tra cụ thể từng document trong P1.2
    print("\n[*] --- AUDIT P1.2 DOCUMENTS IN SUPABASE ---")
    audit_results = []
    for target in P1_2_DOCS:
        t_id = target["doc_id"]
        t_num = target["official_number"]
        found_doc = doc_id_map.get(t_id) or doc_num_map.get(t_num)

        # Check articles for this doc
        doc_key_to_query = found_doc["id"] if found_doc else t_id
        r_art = requests.get(
            f"{SUPABASE_URL}/rest/v1/legal_articles?document_id=eq.{doc_key_to_query}&select=id,article_number,article_title,created_at",
            headers=headers,
            timeout=10
        )
        articles = r_art.json() if r_art.status_code == 200 else []

        print(f"\nDocument: {target['name']}")
        print(f"  Expected ID: {t_id} | Number: {t_num}")
        if found_doc:
            print(f"  [FOUND] in legal_documents: ID='{found_doc.get('id')}', Number='{found_doc.get('official_number')}', CreatedAt='{found_doc.get('created_at')}'")
        else:
            print(f"  [MISSING] from legal_documents")

        print(f"  Articles in legal_articles: {len(articles)} / {target['expected_articles']} expected")
        if articles:
            sample_arts = [a["article_number"] for a in articles[:5]]
            print(f"  Sample article numbers: {sample_arts} ...")

        audit_results.append({
            "target": target,
            "document_found": bool(found_doc),
            "doc_info": found_doc,
            "articles_count": len(articles),
            "articles_expected": target["expected_articles"]
        })

    # Lưu report JSON
    out_path = PROJECT_ROOT / "data" / "03_parsed" / "traffic_p1_2_batch" / "supabase_audit_report.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(audit_results, f, ensure_ascii=False, indent=2)
    print(f"\n[+] Đã ghi báo cáo audit: {out_path}")

if __name__ == "__main__":
    run_audit()
