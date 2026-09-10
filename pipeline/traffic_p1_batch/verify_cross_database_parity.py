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

def verify_cross_db():
    print("=" * 100)
    print("   TASKS 3, 4, 5: CROSS-DATABASE PARITY & PROVISION-HISTORICAL VERIFICATION")
    print("=" * 100)

    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
    }

    # 1. Tải 325 chunks P1
    chunks_file = P1_PARSED_DIR / "all_traffic_p1_chunks.json"
    with open(chunks_file, "r", encoding="utf-8") as f:
        chunks = json.load(f)
    print(f"[+] Loaded {len(chunks)} P1 chunks from {chunks_file.name}")

    # 2. Tải toàn bộ 8 documents P1 từ Supabase
    p1_doc_ids = [
        "traffic_police_patrol_73_2024_tt_bca",
        "traffic_inspection_framework_89_2026_nd_cp",
        "traffic_inspection_procedures_30_2026_tt_bxd",
        "traffic_points_recovery_65_2024_tt_bca",
        "traffic_weight_limits_12_2025_tt_bxd",
        "traffic_weight_amendment_19_2026_tt_bxd",
        "traffic_police_amendment_28_2024_tt_bca",
        "traffic_weight_consolidated_26_2026_vbhn_bxd"
    ]

    r_docs = requests.get(
        f"{SUPABASE_URL}/rest/v1/legal_documents?id=in.({','.join(p1_doc_ids)})&select=id,official_number,title,effective_date,status,metadata",
        headers=headers
    )
    supa_docs = {d["id"]: d for d in r_docs.json()}
    print(f"[+] Loaded {len(supa_docs)} / 8 P1 documents from Supabase legal_documents")

    # 3. Tải toàn bộ 172 articles P1 từ Supabase
    r_arts = requests.get(
        f"{SUPABASE_URL}/rest/v1/legal_articles?document_id=in.({','.join(p1_doc_ids)})&select=id,document_id,article_number,article_title,full_text,chapter_info,status",
        headers=headers,
        params={"limit": 500}
    )
    supa_arts = r_arts.json()
    supa_art_map = {(a["document_id"], a["article_number"]): a for a in supa_arts}
    print(f"[+] Loaded {len(supa_arts)} / 172 P1 legal articles from Supabase legal_articles")

    # 4. Kiểm tra từng point trong số 325 points
    print("\n[*] Auditing 325/325 P1 points mapping to Supabase...")
    resolved_points = 0
    orphan_points = []
    wrong_doc_points = []
    content_discrepancies = []

    for c in chunks:
        cid = c["chunk_id"]
        doc_id = c.get("document_id") or c.get("doc_id")
        art_str = c.get("article", "")
        match = re.search(r"\d+", str(art_str))
        art_num = int(match.group()) if match else None

        # A. Resolve Document
        if doc_id not in supa_docs:
            orphan_points.append({"chunk_id": cid, "reason": f"Missing doc_id {doc_id}"})
            continue

        doc_rec = supa_docs[doc_id]

        # B. Resolve Article
        art_key = (doc_id, art_num)
        if art_key not in supa_art_map:
            orphan_points.append({"chunk_id": cid, "reason": f"Missing article {art_key}"})
            continue

        art_rec = supa_art_map[art_key]

        # C. Verify Relationship & Content
        if art_rec["document_id"] != doc_id:
            wrong_doc_points.append({"chunk_id": cid, "doc_id": doc_id, "found_doc_id": art_rec["document_id"]})
            continue

        # Content inclusion: text của chunk phải là tập con (hoặc tương đương) của full_text trong Supabase
        c_text = c.get("text", "")
        full_text = art_rec.get("full_text", "")

        # Trích xuất 1 đoạn ngắn của chunk text để kiểm tra nó có nằm trong full_text không
        # Bỏ qua header chunk [73/2024/TT-BCA - Điều 1...]
        clean_c_text = re.sub(r"^\[.*?\]\s*", "", c_text).strip()
        first_sentence = clean_c_text.split("\n")[0][:40]

        if first_sentence and first_sentence not in full_text:
            content_discrepancies.append({
                "chunk_id": cid,
                "first_sentence": first_sentence,
                "full_text_len": len(full_text)
            })

        resolved_points += 1

    print(f"[+] 325 Points Audit Results:")
    print(f"    - Resolved Points:        {resolved_points} / 325 ({(resolved_points/325)*100:.1f}%)")
    print(f"    - Orphan Points:          {len(orphan_points)}")
    print(f"    - Wrong Document Points:  {len(wrong_doc_points)}")
    print(f"    - Content Discrepancies:  {len(content_discrepancies)}")

    # 5. Kiểm tra PROVISION-HISTORICAL TT 28/2024/TT-BCA
    print("\n[*] --- TASK 5: PROVISION-HISTORICAL VALIDATION FOR TT 28/2024/TT-BCA ---")
    tt28_doc = supa_docs.get("traffic_police_amendment_28_2024_tt_bca", {})
    tt28_meta = tt28_doc.get("metadata", {})
    print(f"    Document ID:             {tt28_doc.get('id')}")
    print(f"    Legal Status:            {tt28_meta.get('legal_status')}")
    print(f"    Normalized Status:       {tt28_meta.get('normalized_status')}")
    print(f"    Primary Current Core:    {tt28_meta.get('primary_current_core')}")

    tt28_arts = [a for a in supa_arts if a["document_id"] == "traffic_police_amendment_28_2024_tt_bca"]
    tt28_art_status = {a["article_number"]: a["status"] for a in tt28_arts}
    print(f"    Articles Status Map:     {tt28_art_status}")

    pass_tt28_d1 = tt28_art_status.get(1) == "HET_HIEU_LUC"
    pass_tt28_d2 = tt28_art_status.get(2) == "HET_HIEU_LUC"
    pass_tt28_d3 = tt28_art_status.get(3) == "CON_HIEU_LUC"
    pass_tt28_d4 = tt28_art_status.get(4) == "CON_HIEU_LUC"
    pass_tt28_core = tt28_meta.get("primary_current_core") is False

    all_tt28_pass = pass_tt28_d1 and pass_tt28_d2 and pass_tt28_d3 and pass_tt28_d4 and pass_tt28_core
    print(f"    - Điều 1 is HET_HIEU_LUC: {pass_tt28_d1}")
    print(f"    - Điều 2 is HET_HIEU_LUC: {pass_tt28_d2}")
    print(f"    - Điều 3 is CON_HIEU_LUC: {pass_tt28_d3}")
    print(f"    - Điều 4 is CON_HIEU_LUC: {pass_tt28_d4}")
    print(f"    - primary_current_core is False: {pass_tt28_core}")
    print(f"    Status TT 28/2024:       {'PASS 🟢' if all_tt28_pass else 'FAIL 🔴'}")

    # 6. Test Hydration via HybridRetriever
    print("\n[*] --- TASK 3: HYDRATION VERIFICATION VIA HYBRID RETRIEVER ---")
    from backend.app.services.rag.retriever import HybridRetriever
    from backend.app.services.rag.vector_store import QdrantVectorStore
    from backend.app.services.rag.embeddings import get_embedding_service

    store = QdrantVectorStore(collection_name="vietlegal_articles")
    retriever = HybridRetriever(vector_store=store, embedding_service=get_embedding_service())

    # Hydrate TT 73 Điều 11 (Các trường hợp Cảnh sát giao thông được dừng phương tiện để kiểm soát)
    art_73_11 = retriever._get_full_article_from_supabase("traffic_police_patrol_73_2024_tt_bca", 11)
    pass_hyd_73 = bool(art_73_11 and "dừng phương tiện giao thông để kiểm soát" in art_73_11.get("full_text", ""))
    print(f"    - Hydrate TT 73 Điều 11 (Các trường hợp dừng xe): {'PASS 🟢' if pass_hyd_73 else 'FAIL 🔴'} ({len(art_73_11.get('full_text', '')) if art_73_11 else 0} chars)")

    # Hydrate NĐ 89 Điều 7 (Điều kiện trung tâm đăng kiểm)
    art_89_7 = retriever._get_full_article_from_supabase("traffic_inspection_framework_89_2026_nd_cp", 7)
    pass_hyd_89 = bool(art_89_7 and len(art_89_7.get("full_text", "")) > 100)
    print(f"    - Hydrate NĐ 89 Điều 7 (Cơ sở đăng kiểm):        {'PASS 🟢' if pass_hyd_89 else 'FAIL 🔴'} ({len(art_89_7.get('full_text', '')) if art_89_7 else 0} chars)")

    # Hydrate TT 30 Điều 6 (Miễn kiểm định lần đầu)
    art_30_6 = retriever._get_full_article_from_supabase("traffic_inspection_procedures_30_2026_tt_bxd", 6)
    pass_hyd_30 = bool(art_30_6 and len(art_30_6.get("full_text", "")) > 100)
    print(f"    - Hydrate TT 30 Điều 6 (Miễn kiểm định lần đầu): {'PASS 🟢' if pass_hyd_30 else 'FAIL 🔴'} ({len(art_30_6.get('full_text', '')) if art_30_6 else 0} chars)")

    all_pass = (resolved_points == 325 and len(orphan_points) == 0 and len(wrong_doc_points) == 0 
                and all_tt28_pass and pass_hyd_73 and pass_hyd_89 and pass_hyd_30)

    print("\n" + "=" * 100)
    print(f" CROSS-DATABASE PARITY VERIFICATION VERDICT: {'PASS 🟢' if all_pass else 'FAIL 🔴'}")
    print("=" * 100)

    # Lưu báo cáo
    out_file = P1_PARSED_DIR / "p1_cross_database_parity_report.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump({
            "total_p1_points": len(chunks),
            "resolved_points": resolved_points,
            "orphan_count": len(orphan_points),
            "wrong_document_count": len(wrong_doc_points),
            "content_discrepancies_count": len(content_discrepancies),
            "tt28_validation": {
                "dieu_1_status": tt28_art_status.get(1),
                "dieu_2_status": tt28_art_status.get(2),
                "dieu_3_status": tt28_art_status.get(3),
                "dieu_4_status": tt28_art_status.get(4),
                "primary_current_core": tt28_meta.get("primary_current_core"),
                "passed": all_tt28_pass
            },
            "hydration_tests": {
                "tt73_dieu11": pass_hyd_73,
                "nd89_dieu7": pass_hyd_89,
                "tt30_dieu6": pass_hyd_30
            },
            "verdict": "PASS" if all_pass else "FAIL"
        }, f, ensure_ascii=False, indent=2)

    print(f"[+] Báo cáo đối soát đã được lưu tại: {out_file}")

if __name__ == "__main__":
    verify_cross_db()
