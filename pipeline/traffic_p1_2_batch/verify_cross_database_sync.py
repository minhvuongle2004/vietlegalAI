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

def verify_sync():
    print("=" * 80)
    print("   POST-SYNC VERIFICATION: AUDIT SUPABASE & HYDRATION CHECK")
    print("=" * 80)

    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
    }

    # 1. Kiểm tra 4 documents
    p1_2_doc_ids = [
        "traffic_driver_training_94_2026_nd_cp",
        "traffic_road_infra_amendment_241_2026_nd_cp",
        "traffic_inspection_amendment_45_2026_tt_bxd",
        "traffic_road_signs_qcvn41_51_2024_tt_bgtvt"
    ]

    r_docs = requests.get(
        f"{SUPABASE_URL}/rest/v1/legal_documents?id=in.({','.join(p1_2_doc_ids)})&select=id,official_number,title,effective_date,status,metadata",
        headers=headers
    )
    docs = r_docs.json() if r_docs.status_code == 200 else []
    print(f"[+] Verified P1.2 Documents in Supabase: {len(docs)} / 4")
    for d in docs:
        sha = d.get("metadata", {}).get("sha256", "")[:12]
        print(f"    - {d['id']:45} | {d['official_number']:18} | eff: {d['effective_date']} | sha256: {sha}...")

    # 2. Kiểm tra 53 legal articles
    r_arts = requests.get(
        f"{SUPABASE_URL}/rest/v1/legal_articles?document_id=in.({','.join(p1_2_doc_ids)})&select=document_id,article_number,article_title,full_text,chapter_info,status",
        headers=headers
    )
    arts = r_arts.json() if r_arts.status_code == 200 else []
    print(f"\n[+] Verified P1.2 Legal Articles in Supabase: {len(arts)} / 53")

    doc_counts = {}
    empty_content = 0
    short_content = 0
    for a in arts:
        did = a["document_id"]
        doc_counts[did] = doc_counts.get(did, 0) + 1
        ft = a.get("full_text", "")
        if not ft:
            empty_content += 1
        elif len(ft) < 20:
            short_content += 1

    for did, count in doc_counts.items():
        print(f"    - {did:45}: {count} articles")

    print(f"    - Empty content: {empty_content}")
    print(f"    - Suspiciously short content (<20 chars): {short_content}")

    # 3. Sample check NĐ 94 Điều 24 (bãi bỏ mô phỏng) & Điều 26 (thẩm quyền cấp giấy phép sát hạch)
    r_sample = requests.get(
        f"{SUPABASE_URL}/rest/v1/legal_articles?document_id=eq.traffic_driver_training_94_2026_nd_cp&article_number=in.(24,26)&select=article_number,article_title,full_text",
        headers=headers
    )
    samples = r_sample.json() if r_sample.status_code == 200 else []
    print("\n[*] Sample Verification on NĐ 94/2026 in Supabase:")
    for s in samples:
        print(f"    [Điều {s['article_number']}: {s['article_title']}]")
        lines = s["full_text"].split("\n")
        print(f"      Header: {lines[0]}")
        print(f"      Paragraphs: {len(lines) - 1} paragraphs | Total chars: {len(s['full_text'])}")
        print(f"      Snippet: {s['full_text'][:160]}...\n")

    # 4. Kiểm tra Hydration qua HybridRetriever
    print("[*] Testing Article Hydration via HybridRetriever:")
    from backend.app.services.rag.retriever import HybridRetriever
    from backend.app.services.rag.vector_store import QdrantVectorStore
    from backend.app.services.rag.embeddings import get_embedding_service

    store = QdrantVectorStore(collection_name="vietlegal_articles")
    retriever = HybridRetriever(vector_store=store, embedding_service=get_embedding_service())

    full_art_26 = retriever._get_full_article_from_supabase("traffic_driver_training_94_2026_nd_cp", 26)
    if full_art_26 and "Phòng Cảnh sát giao thông" in full_art_26.get("full_text", ""):
        print(f"    [+] Hydration Test NĐ 94 Điều 26: SUCCESS 🟢 (Length: {len(full_art_26.get('full_text', ''))} chars loaded from Supabase)")
    else:
        print("    [!] Hydration Test NĐ 94 Điều 26: FAILED 🔴")

if __name__ == "__main__":
    verify_sync()
