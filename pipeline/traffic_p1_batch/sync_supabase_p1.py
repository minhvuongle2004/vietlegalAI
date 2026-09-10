import os
import sys
import json
import re
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

P1_PARSED_DIR = PROJECT_ROOT / "data" / "03_parsed" / "traffic_p1_batch"

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

def sync_traffic_p1():
    print("=" * 90)
    print("   TASK 2: SUPABASE RELATIONAL PARITY SYNC FOR TRAFFIC P1")
    print("=" * 90)

    docs_before, arts_before = get_table_counts()
    print(f"[*] Supabase BEFORE:")
    print(f"    - legal_documents: {docs_before}")
    print(f"    - legal_articles:  {arts_before}")

    headers = get_headers()
    doc_files = sorted([f for f in P1_PARSED_DIR.glob("traffic_*.json") if f.name != "all_traffic_p1_chunks.json"])

    inserted_docs = 0
    skipped_docs = 0
    inserted_articles = 0
    skipped_articles = 0

    sync_summary = []

    for fpath in doc_files:
        with open(fpath, "r", encoding="utf-8") as f:
            pdata = json.load(f)

        meta = pdata.get("metadata", {})
        hierarchy = pdata.get("hierarchy", {})
        articles = hierarchy.get("articles", [])

        doc_id = meta.get("source_document_id")
        off_num = meta.get("official_number")
        title = meta.get("title")
        issuer = meta.get("source_authority") or "Chính phủ"
        issue_date = meta.get("issue_date") or "2024-01-01"
        effective_date = meta.get("effective_date") or "2025-01-01"
        source_url = meta.get("source_url") or ""
        sha256 = meta.get("sha256") or ""
        doc_role = meta.get("document_role") or "PRIMARY"
        legal_status = meta.get("legal_status") or "CURRENT"
        norm_status = meta.get("normalized_status") or "CURRENT_CORE"

        # Định dạng doc_type
        if "NĐ" in off_num or "ND" in off_num:
            doc_type = "NGHI_DINH"
        elif "TT" in off_num:
            doc_type = "THONG_TU"
        elif "VBHN" in off_num:
            doc_type = "VAN_BAN_HOP_NHAT"
        else:
            doc_type = "VAN_BAN_QUY_PHAM"

        # Xác định short_title
        if "73/2024" in off_num:
            short_title = "Thông tư 73/2024/TT-BCA"
        elif "89/2026" in off_num:
            short_title = "Nghị định 89/2026/NĐ-CP"
        elif "30/2026" in off_num:
            short_title = "Thông tư 30/2026/TT-BXD"
        elif "65/2024" in off_num:
            short_title = "Thông tư 65/2024/TT-BCA"
        elif "12/2025" in off_num:
            short_title = "Thông tư 12/2025/TT-BXD"
        elif "19/2026" in off_num:
            short_title = "Thông tư 19/2026/TT-BXD"
        elif "28/2024" in off_num:
            short_title = "Thông tư 28/2024/TT-BCA"
        elif "26/VBHN" in off_num:
            short_title = "Văn bản hợp nhất 26/VBHN-BXD"
        else:
            short_title = off_num

        print(f"\n[*] Processing: {short_title} ({doc_id})")

        # 1. Kiểm tra document tồn tại
        r_chk_doc = requests.get(
            f"{SUPABASE_URL}/rest/v1/legal_documents?id=eq.{doc_id}&select=id",
            headers=headers
        )
        existing_doc = r_chk_doc.json() if r_chk_doc.status_code == 200 else []

        if not existing_doc:
            doc_payload = {
                "id": doc_id,
                "official_number": off_num,
                "title": title,
                "short_title": short_title,
                "doc_type": doc_type,
                "issuer": issuer,
                "signer": meta.get("signer"),
                "issue_date": issue_date,
                "effective_date": effective_date,
                "expiry_date": None,
                "status": "CON_HIEU_LUC" if legal_status != "HISTORICAL" else "HET_HIEU_LUC",
                "source_url": source_url,
                "raw_content": None,
                "metadata": {
                    "sha256": sha256,
                    "provenance": meta.get("source_status_authority") or "CSDL Quốc gia về VBPL / Cổng TTĐT Chính phủ",
                    "legal_status": legal_status,
                    "document_role": doc_role,
                    "normalized_status": norm_status,
                    "primary_current_core": False if off_num == "28/2024/TT-BCA" else (doc_role == "PRIMARY")
                }
            }
            r_ins_doc = requests.post(f"{SUPABASE_URL}/rest/v1/legal_documents", headers=headers, json=doc_payload)
            if r_ins_doc.status_code in [200, 201]:
                print(f"    [+] Inserted document into legal_documents: {doc_id}")
                inserted_docs += 1
            else:
                raise RuntimeError(f"Lỗi insert legal_documents: {r_ins_doc.status_code} {r_ins_doc.text}")
        else:
            print(f"    [=] Document already exists: {doc_id}")
            skipped_docs += 1

        # 2. Kiểm tra articles đã có trong Supabase
        r_chk_art = requests.get(
            f"{SUPABASE_URL}/rest/v1/legal_articles?document_id=eq.{doc_id}&select=article_number",
            headers=headers
        )
        existing_art_nums = set(a["article_number"] for a in r_chk_art.json()) if r_chk_art.status_code == 200 else set()

        # 3. Chuẩn bị legal_articles
        articles_to_insert = []
        for art in articles:
            a_idx = art.get("article_index")
            a_num = art.get("article_number", "")
            match = re.search(r"\d+", str(a_num))
            art_int = int(match.group()) if match else a_idx

            if art_int in existing_art_nums:
                skipped_articles += 1
                continue

            a_title = art.get("article_title", "")
            chap = art.get("chapter", "")
            clauses = art.get("clauses", [])

            # Tạo full_text chuẩn legal source
            body_parts = []
            for c in clauses:
                c_num = c.get("clause_number", "")
                c_txt = c.get("clause_text", "")
                pts = c.get("points", [])
                if c_num and c_txt:
                    clause_line = f"{c_num}: {c_txt}".strip() if not c_txt.startswith(c_num) else c_txt
                    body_parts.append(clause_line)
                elif c_txt:
                    body_parts.append(c_txt)

                for p in pts:
                    p_let = p.get("point_letter", "")
                    p_txt = p.get("point_text", "")
                    if p_let and p_txt:
                        point_line = f"{p_let}) {p_txt}".strip() if not p_txt.startswith(p_let) else p_txt
                        body_parts.append(f"  {point_line}")
                    elif p_txt:
                        body_parts.append(f"  {p_txt}")

            header_line = f"{a_num}. {a_title}".strip() if a_title else a_num
            full_text = f"{header_line}\n" + "\n".join(body_parts) if body_parts else header_line

            # Provision-level handling cho TT 28/2024/TT-BCA:
            # Điều 1 & Điều 2 bị bãi bỏ -> HET_HIEU_LUC
            # Điều 3 & Điều 4 còn hiệu lực -> CON_HIEU_LUC
            if off_num == "28/2024/TT-BCA":
                if art_int in [1, 2]:
                    art_status = "HET_HIEU_LUC"
                else:
                    art_status = "CON_HIEU_LUC"
            else:
                art_status = "CON_HIEU_LUC"

            articles_to_insert.append({
                "document_id": doc_id,
                "article_number": art_int,
                "article_title": a_title,
                "full_text": full_text.strip(),
                "chapter_info": chap,
                "status": art_status
            })

        if articles_to_insert:
            for i in range(0, len(articles_to_insert), 20):
                batch = articles_to_insert[i:i+20]
                r_ins_art = requests.post(f"{SUPABASE_URL}/rest/v1/legal_articles", headers=headers, json=batch)
                if r_ins_art.status_code in [200, 201]:
                    inserted_articles += len(batch)
                else:
                    raise RuntimeError(f"Lỗi insert legal_articles: {r_ins_art.status_code} {r_ins_art.text}")
            print(f"    [+] Inserted {len(articles_to_insert)} articles into legal_articles")
        else:
            print(f"    [=] All {len(articles)} articles already exist.")

        sync_summary.append({
            "document_id": doc_id,
            "official_number": off_num,
            "short_title": short_title,
            "articles_count": len(articles),
            "inserted_articles": len(articles_to_insert)
        })

    docs_after, arts_after = get_table_counts()
    print("\n" + "=" * 90)
    print(f"[*] Supabase AFTER SYNC:")
    print(f"    - legal_documents: {docs_after} (Delta: +{docs_after - docs_before})")
    print(f"    - legal_articles:  {arts_after} (Delta: +{arts_after - arts_before})")
    print("=" * 90)

    return {
        "docs_before": docs_before,
        "docs_after": docs_after,
        "arts_before": arts_before,
        "arts_after": arts_after,
        "inserted_docs": inserted_docs,
        "skipped_docs": skipped_docs,
        "inserted_articles": inserted_articles,
        "skipped_articles": skipped_articles,
        "summary": sync_summary
    }

if __name__ == "__main__":
    sync_traffic_p1()
