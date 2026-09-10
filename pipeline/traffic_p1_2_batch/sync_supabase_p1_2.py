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

P1_2_FILES = [
    {
        "file": "traffic_driver_training_94_2026_nd_cp.json",
        "doc_id": "traffic_driver_training_94_2026_nd_cp",
        "official_number": "94/2026/NĐ-CP",
        "short_title": "Nghị định 94/2026/NĐ-CP",
        "doc_type": "NGHI_DINH",
        "expected_articles": 43
    },
    {
        "file": "traffic_road_infra_amendment_241_2026_nd_cp.json",
        "doc_id": "traffic_road_infra_amendment_241_2026_nd_cp",
        "official_number": "241/2026/NĐ-CP",
        "short_title": "Nghị định 241/2026/NĐ-CP",
        "doc_type": "NGHI_DINH",
        "expected_articles": 4
    },
    {
        "file": "traffic_inspection_amendment_45_2026_tt_bxd.json",
        "doc_id": "traffic_inspection_amendment_45_2026_tt_bxd",
        "official_number": "45/2026/TT-BXD",
        "short_title": "Thông tư 45/2026/TT-BXD",
        "doc_type": "THONG_TU",
        "expected_articles": 4
    },
    {
        "file": "traffic_road_signs_qcvn41_51_2024_tt_bgtvt.json",
        "doc_id": "traffic_road_signs_qcvn41_51_2024_tt_bgtvt",
        "official_number": "51/2024/TT-BGTVT",
        "short_title": "Thông tư 51/2024/TT-BGTVT",
        "doc_type": "THONG_TU",
        "expected_articles": 2
    }
]

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

def sync_p1_2():
    print("=" * 80)
    print("   COMPLETE RELATIONAL + VECTOR DATA SYNCHRONIZATION (SUPABASE P1.2)")
    print("=" * 80)

    # 1. Đo lường hiện trạng trước khi sync
    docs_before, arts_before = get_table_counts()
    print(f"[*] Supabase BEFORE:")
    print(f"    - legal_documents: {docs_before}")
    print(f"    - legal_articles:  {arts_before}")

    headers = get_headers()
    parsed_dir = PROJECT_ROOT / "data" / "03_parsed" / "traffic_p1_2_batch"

    inserted_docs = 0
    inserted_articles = 0
    skipped_docs = 0
    skipped_articles = 0
    document_summaries = []

    for cfg in P1_2_FILES:
        fpath = parsed_dir / cfg["file"]
        with open(fpath, "r", encoding="utf-8") as f:
            data = json.load(f)

        doc_id = data["document_id"]
        off_num = data["official_number"]
        title = data["title"]
        issuer = data.get("authority", "Chính phủ")
        issue_date = data.get("issue_date") or "2026-01-01"
        effective_date = data.get("effective_date") or "2026-07-01"
        source_url = data.get("source_url", "")
        sha256 = data.get("sha256", "")

        print(f"\n[*] Processing document: {cfg['short_title']} ({doc_id})")

        # 1. Kiểm tra document đã có trong Supabase chưa
        r_check_doc = requests.get(
            f"{SUPABASE_URL}/rest/v1/legal_documents?id=eq.{doc_id}&select=id,official_number",
            headers=headers
        )
        existing_doc = r_check_doc.json() if r_check_doc.status_code == 200 else []

        if not existing_doc:
            doc_payload = {
                "id": doc_id,
                "official_number": off_num,
                "title": title,
                "short_title": cfg["short_title"],
                "doc_type": cfg["doc_type"],
                "issuer": issuer,
                "signer": data.get("signer"),
                "issue_date": issue_date,
                "effective_date": effective_date,
                "expiry_date": None,
                "status": "CON_HIEU_LUC",
                "source_url": source_url,
                "raw_content": None,
                "metadata": {
                    "sha256": sha256,
                    "provenance": data.get("source_status_authority", "Cổng TTĐT Chính phủ / CSDL Quốc gia về VBPL"),
                    "legal_status": data.get("legal_status", "CURRENT"),
                    "attached_regulation": data.get("attached_regulation")
                }
            }
            r_ins_doc = requests.post(
                f"{SUPABASE_URL}/rest/v1/legal_documents",
                headers=headers,
                json=doc_payload
            )
            if r_ins_doc.status_code in [200, 201]:
                print(f"    [+] Inserted document into legal_documents: {doc_id}")
                inserted_docs += 1
            else:
                raise RuntimeError(f"Lỗi insert legal_documents: {r_ins_doc.status_code} {r_ins_doc.text}")
        else:
            print(f"    [=] Document already exists in legal_documents: {doc_id}")
            skipped_docs += 1

        # 2. Kiểm tra các articles hiện có
        r_check_arts = requests.get(
            f"{SUPABASE_URL}/rest/v1/legal_articles?document_id=eq.{doc_id}&select=article_number",
            headers=headers
        )
        existing_art_nums = set()
        if r_check_arts.status_code == 200:
            existing_art_nums = set(a["article_number"] for a in r_check_arts.json())

        # 3. Chuẩn bị legal articles từ parsed JSON
        articles_to_insert = []
        raw_articles = data.get("articles", [])

        for art in raw_articles:
            raw_art_num = art.get("article_number", "")
            # Trích xuất số nguyên
            match_num = re.search(r"\d+", str(raw_art_num))
            art_int = int(match_num.group()) if match_num else art.get("article_index")

            if art_int in existing_art_nums:
                skipped_articles += 1
                continue

            art_title = art.get("article_title", "")
            chapter = art.get("chapter", "")

            # Xây dựng full_text chuẩn legal source
            paragraphs = art.get("raw_text_paragraphs", [])
            if not paragraphs and art.get("clauses"):
                paragraphs = [f"{c.get('clause_number')}: {c.get('clause_text')}".strip() for c in art.get("clauses", [])]

            header_line = f"{raw_art_num}. {art_title}".strip() if art_title else raw_art_num
            body_text = "\n".join(paragraphs).strip()
            full_text = f"{header_line}\n{body_text}".strip()

            articles_to_insert.append({
                "document_id": doc_id,
                "article_number": art_int,
                "article_title": art_title,
                "full_text": full_text,
                "chapter_info": chapter,
                "status": "CON_HIEU_LUC"
            })

        if articles_to_insert:
            # Insert theo batch 20 records
            for i in range(0, len(articles_to_insert), 20):
                batch = articles_to_insert[i:i+20]
                r_ins_art = requests.post(
                    f"{SUPABASE_URL}/rest/v1/legal_articles",
                    headers=headers,
                    json=batch
                )
                if r_ins_art.status_code in [200, 201]:
                    inserted_articles += len(batch)
                else:
                    raise RuntimeError(f"Lỗi insert legal_articles: {r_ins_art.status_code} {r_ins_art.text}")
            print(f"    [+] Inserted {len(articles_to_insert)} legal articles for {doc_id}")
        else:
            print(f"    [=] All {len(raw_articles)} articles already exist in legal_articles.")

        document_summaries.append({
            "doc_id": doc_id,
            "official_number": off_num,
            "expected_articles": cfg["expected_articles"],
            "actual_articles": len(raw_articles),
            "attached_qcvn_units": data.get("attached_regulation", {}).get("total_technical_units", 0) if data.get("attached_regulation") else 0
        })

    # 4. Đo lường hiện trạng sau khi sync
    docs_after, arts_after = get_table_counts()
    print("\n" + "=" * 80)
    print(f"[*] Supabase AFTER:")
    print(f"    - legal_documents: {docs_after} (Delta: +{docs_after - docs_before})")
    print(f"    - legal_articles:  {arts_after} (Delta: +{arts_after - arts_before})")
    print("=" * 80)

    # 5. Cross-Database Audit: Qdrant Production <-> Supabase
    print("\n[*] --- TASK 4: AUDIT QDRANT PRODUCTION <-> SUPABASE RELATIONAL ---")
    chunks_path = parsed_dir / "all_traffic_p1_2_chunks.json"
    with open(chunks_path, "r", encoding="utf-8") as f:
        all_chunks = json.load(f)

    # Fetch all P1.2 articles from Supabase to verify resolution
    r_all_p1_2_arts = requests.get(
        f"{SUPABASE_URL}/rest/v1/legal_articles?document_id=in.({','.join([c['doc_id'] for c in P1_2_FILES])})&select=document_id,article_number,article_title,full_text",
        headers=headers
    )
    supa_arts = r_all_p1_2_arts.json() if r_all_p1_2_arts.status_code == 200 else []
    supa_art_keys = set(f"{a['document_id']}_{a['article_number']}" for a in supa_arts)

    resolved_legal_chunks = 0
    resolved_qcvn_chunks = 0
    orphan_chunks = []

    for c in all_chunks:
        doc_id = c["document_id"]
        art_str = c.get("article", "")
        unit_type = c.get("unit_type")

        if unit_type == "QCVN_TECHNICAL_REGULATION" or "QCVN" in art_str:
            # QCVN technical units belong to attached_regulation of TT 51/2024
            if doc_id == "traffic_road_signs_qcvn41_51_2024_tt_bgtvt":
                resolved_qcvn_chunks += 1
            else:
                orphan_chunks.append(c["chunk_id"])
        else:
            # Legal articles
            match_num = re.search(r"\d+", art_str)
            art_int = int(match_num.group()) if match_num else None
            key = f"{doc_id}_{art_int}"
            if key in supa_art_keys:
                resolved_legal_chunks += 1
            else:
                orphan_chunks.append(c["chunk_id"])

    total_chunks = len(all_chunks)
    print(f"[+] Total Qdrant P1.2 Points: {total_chunks}")
    print(f"    - Legal Article Chunks Resolved to Supabase: {resolved_legal_chunks} / 142")
    print(f"    - QCVN Technical Regulation Chunks (Attached): {resolved_qcvn_chunks} / 21")
    print(f"    - Orphan Chunks: {len(orphan_chunks)}")

    report = {
        "supabase_before": {
            "legal_documents": docs_before,
            "legal_articles": arts_before
        },
        "supabase_after": {
            "legal_documents": docs_after,
            "legal_articles": arts_after
        },
        "sync_stats": {
            "inserted_docs": inserted_docs,
            "skipped_docs": skipped_docs,
            "inserted_articles": inserted_articles,
            "skipped_articles": skipped_articles
        },
        "documents": document_summaries,
        "qdrant_cross_mapping": {
            "total_p1_2_qdrant_points": total_chunks,
            "resolved_legal_chunks": resolved_legal_chunks,
            "resolved_qcvn_chunks": resolved_qcvn_chunks,
            "orphan_chunks_count": len(orphan_chunks),
            "orphan_chunks": orphan_chunks
        },
        "verdict": "SYNCED" if len(orphan_chunks) == 0 and docs_after == docs_before + 4 and arts_after == arts_before + 53 else "NEEDS FIX"
    }

    out_file = parsed_dir / "sync_supabase_p1_2_report.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"\n[+] Báo cáo kết quả đồng bộ đã lưu tại: {out_file}")
    print(f"[*] FINAL VERDICT: {report['verdict']} 🟢" if report['verdict'] == 'SYNCED' else f"[!] FINAL VERDICT: {report['verdict']} 🔴")

if __name__ == "__main__":
    sync_p1_2()
