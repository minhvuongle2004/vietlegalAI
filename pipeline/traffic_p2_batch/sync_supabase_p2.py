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
PARSED_FILE = PROJECT_ROOT / "data" / "03_parsed" / "traffic_p2_batch" / "traffic_road_law_detail_165_2024_nd_cp.json"

def get_headers():
    return {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }

def get_table_counts():
    h = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Range-Unit": "items",
        "Prefer": "count=exact"
    }
    r_docs = requests.get(f"{SUPABASE_URL}/rest/v1/legal_documents?select=id", headers=h, params={"limit": 1})
    docs_range = r_docs.headers.get("Content-Range", "")
    docs_count = int(docs_range.split("/")[-1]) if "/" in docs_range else len(r_docs.json())

    r_arts = requests.get(f"{SUPABASE_URL}/rest/v1/legal_articles?select=id", headers=h, params={"limit": 1})
    arts_range = r_arts.headers.get("Content-Range", "")
    arts_count = int(arts_range.split("/")[-1]) if "/" in arts_range else len(r_arts.json())

    return docs_count, arts_count

def sync_supabase_p2():
    print("=" * 80)
    print("   SUPABASE SAFE SYNC FOR TRAFFIC P2 (NĐ 165/2024/NĐ-CP)")
    print("=" * 80)

    docs_before, arts_before = get_table_counts()
    print(f"[*] Supabase BEFORE sync:")
    print(f"    - legal_documents: {docs_before}")
    print(f"    - legal_articles:  {arts_before}")

    with open(PARSED_FILE, "r", encoding="utf-8") as f:
        doc_data = json.load(f)

    meta = doc_data["metadata"]
    doc_id = meta["document_id"]
    off_num = meta["official_number"]
    title = meta["title"]
    short_title = meta["short_title"]
    headers = get_headers()

    # 1. Check / Insert into legal_documents
    r_chk_doc = requests.get(
        f"{SUPABASE_URL}/rest/v1/legal_documents?id=eq.{doc_id}&select=id",
        headers=headers
    )
    existing_docs = r_chk_doc.json() if r_chk_doc.status_code == 200 else []

    inserted_docs = 0
    if not existing_docs:
        doc_payload = {
            "id": doc_id,
            "official_number": off_num,
            "title": title,
            "short_title": short_title,
            "doc_type": "NGHI_DINH",
            "issuer": meta["issuer"],
            "signer": meta["signer"],
            "issue_date": meta["issue_date"],
            "effective_date": meta["effective_date"],
            "expiry_date": None,
            "status": meta["legal_status"],
            "source_url": meta["source_url"],
            "raw_content": None,
            "metadata": {
                "sha256": meta["sha256"],
                "annex_sha256": meta["annex_sha256"],
                "amended_by": meta["amended_by"],
                "provenance": "Cổng TTĐT Chính phủ (vanban.chinhphu.vn)",
                "document_role": meta["document_role"],
                "normalized_status": meta["normalized_status"],
                "batch": "TRAFFIC_P2"
            }
        }
        r_ins = requests.post(f"{SUPABASE_URL}/rest/v1/legal_documents", headers=headers, json=doc_payload)
        if r_ins.status_code in [200, 201]:
            print(f"[+] Inserted document into legal_documents: {doc_id}")
            inserted_docs = 1
        else:
            raise RuntimeError(f"Error inserting document: {r_ins.status_code} {r_ins.text}")
    else:
        print(f"[=] Document already exists: {doc_id}")

    # 2. Check / Insert articles into legal_articles
    r_chk_art = requests.get(
        f"{SUPABASE_URL}/rest/v1/legal_articles?document_id=eq.{doc_id}&select=article_number",
        headers=headers
    )
    existing_art_nums = set(a["article_number"] for a in r_chk_art.json()) if r_chk_art.status_code == 200 else set()
    print(f"[*] Existing articles in Supabase for {doc_id}: {len(existing_art_nums)}")

    articles_to_insert = []
    for art in doc_data["articles"]:
        art_num = art["article_number"]
        if art_num in existing_art_nums:
            continue

        art_title = art["article_title"]
        chap = f"{art['chapter']}: {art['chapter_title']}"
        raw_body = art["raw_text"]
        full_text = f"Điều {art_num}. {art_title}\n{raw_body}".strip()

        articles_to_insert.append({
            "document_id": doc_id,
            "article_number": art_num,
            "article_title": art_title,
            "full_text": full_text,
            "chapter_info": chap,
            "status": "CON_HIEU_LUC"
        })

    inserted_articles = 0
    if articles_to_insert:
        print(f"[*] Inserting {len(articles_to_insert)} new articles in batches of 20...")
        for i in range(0, len(articles_to_insert), 20):
            batch = articles_to_insert[i:i+20]
            r_ins_batch = requests.post(f"{SUPABASE_URL}/rest/v1/legal_articles", headers=headers, json=batch)
            if r_ins_batch.status_code in [200, 201]:
                inserted_articles += len(batch)
            else:
                raise RuntimeError(f"Error inserting articles batch: {r_ins_batch.status_code} {r_ins_batch.text}")
        print(f"[+] Successfully inserted {inserted_articles} articles!")
    else:
        print(f"[=] All {len(doc_data['articles'])} articles already exist in legal_articles.")

    docs_after, arts_after = get_table_counts()
    print("\n" + "=" * 80)
    print(f"[*] Supabase AFTER sync:")
    print(f"    - legal_documents: {docs_before} -> {docs_after} (+{docs_after - docs_before})")
    print(f"    - legal_articles:  {arts_before} -> {arts_after} (+{arts_after - arts_before})")
    print("=" * 80)

    # Save report
    report = {
        "document_id": doc_id,
        "official_number": off_num,
        "docs_before": docs_before,
        "docs_after": docs_after,
        "arts_before": arts_before,
        "arts_after": arts_after,
        "inserted_docs": inserted_docs,
        "inserted_articles": inserted_articles,
        "total_doc_articles": len(doc_data["articles"]),
        "status": "PASS"
    }

    report_path = PROJECT_ROOT / "data" / "03_parsed" / "traffic_p2_batch" / "supabase_sync_report.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    return report

if __name__ == "__main__":
    sync_supabase_p2()
