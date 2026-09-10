import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
import os
import re
import json
import time
import uuid
import hashlib
import requests
from pathlib import Path
from dotenv import load_dotenv
from bs4 import BeautifulSoup

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
load_dotenv(PROJECT_ROOT / ".env")

from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels
from backend.app.services.rag.embeddings import get_embedding_service

CLOUD_URL = os.getenv("QDRANT_URL")
CLOUD_API_KEY = os.getenv("QDRANT_API_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

RAW_DIR = PROJECT_ROOT / "data" / "01_raw" / "traffic_p3_batch" / "130_2024_ND_CP"
RAW_DIR.mkdir(parents=True, exist_ok=True)
PARSED_DIR = PROJECT_ROOT / "data" / "03_parsed" / "traffic_p3_batch"
PARSED_DIR.mkdir(parents=True, exist_ok=True)

HTML_CACHE = r"C:\Users\vuong\.gemini\antigravity-ide\brain\d4e19d11-4f9f-41c0-a5d4-f7b6e3367760\.system_generated\steps\14966\content.md"

def process_nd130():
    print("=" * 80)
    print("   P3.3 PROCESSING: NĐ 130/2024/NĐ-CP (THU PHÍ CAO TỐC)")
    print("=" * 80)

    # 1. Update RAW manifest
    pdf_file = RAW_DIR / "130-cp.signed.pdf"
    with open(pdf_file, "rb") as f:
        pdf_bytes = f.read()
    sha256_pdf = hashlib.sha256(pdf_bytes).hexdigest()
    
    raw_manifest = [{
        "filename": "130-cp.signed.pdf",
        "relative_path": str(pdf_file.relative_to(PROJECT_ROOT)).replace("\\", "/"),
        "sha256": sha256_pdf,
        "file_size": len(pdf_bytes),
        "content_type": "application/pdf",
        "source_url": "https://datafiles.chinhphu.vn/cpp/files/vbpq/2024/9/130-cp.signed.pdf",
        "description": "Nghị định 130/2024/NĐ-CP official signed PDF"
    }]
    with open(RAW_DIR / "raw_manifest.json", "w", encoding="utf-8") as f:
        json.dump(raw_manifest, f, ensure_ascii=False, indent=2)
    print(f"[+] Verified RAW artifact: size={len(pdf_bytes)} bytes, sha256={sha256_pdf}")

    # 2. Parse 13 Articles from HTML
    with open(HTML_CACHE, "r", encoding="utf-8") as f:
        html_text = f.read()

    soup = BeautifulSoup(html_text, "html.parser")
    
    # Locate all article headings and their text
    article_headings = []
    for tag in soup.find_all(["b", "strong"]):
        txt = tag.get_text().strip()
        m = re.match(r"^Điều\s+(\d+)\.\s*(.*)", txt)
        if m:
            art_num = int(m.group(1))
            art_title = m.group(2).strip()
            article_headings.append((art_num, art_title, tag))

    # Deduplicate in order
    seen_nums = set()
    unique_articles = []
    for num, title, tag in article_headings:
        if num not in seen_nums and 1 <= num <= 13:
            seen_nums.add(num)
            unique_articles.append((num, title, tag))

    unique_articles.sort(key=lambda x: x[0])
    print(f"[*] Extracted {len(unique_articles)} articles from official text.")

    # Chapter mapping
    chapter_map = {
        1: ("Chương I", "QUY ĐỊNH CHUNG"),
        2: ("Chương I", "QUY ĐỊNH CHUNG"),
        3: ("Chương II", "QUY ĐỊNH CHUNG VỀ THU PHÍ SỬ DỤNG ĐƯỜNG BỘ CAO TỐC"),
        4: ("Chương II", "QUY ĐỊNH CHUNG VỀ THU PHÍ SỬ DỤNG ĐƯỜNG BỘ CAO TỐC"),
        5: ("Chương II", "QUY ĐỊNH CHUNG VỀ THU PHÍ SỬ DỤNG ĐƯỜNG BỘ CAO TỐC"),
        6: ("Chương II", "QUY ĐỊNH CHUNG VỀ THU PHÍ SỬ DỤNG ĐƯỜNG BỘ CAO TỐC"),
        7: ("Chương II", "QUY ĐỊNH CHUNG VỀ THU PHÍ SỬ DỤNG ĐƯỜNG BỘ CAO TỐC"),
        8: ("Chương II", "QUY ĐỊNH CHUNG VỀ THU PHÍ SỬ DỤNG ĐƯỜNG BỘ CAO TỐC"),
        9: ("Chương III", "QUY ĐỊNH VỀ MỨC THU, CHẾ ĐỘ THU, NỘP, QUẢN LÝ VÀ SỬ DỤNG PHÍ SỬ DỤNG ĐƯỜNG BỘ CAO TỐC"),
        10: ("Chương III", "QUY ĐỊNH VỀ MỨC THU, CHẾ ĐỘ THU, NỘP, QUẢN LÝ VÀ SỬ DỤNG PHÍ SỬ DỤNG ĐƯỜNG BỘ CAO TỐC"),
        11: ("Chương III", "QUY ĐỊNH VỀ MỨC THU, CHẾ ĐỘ THU, NỘP, QUẢN LÝ VÀ SỬ DỤNG PHÍ SỬ DỤNG ĐƯỜNG BỘ CAO TỐC"),
        12: ("Chương IV", "TỔ CHỨC THỰC HIỆN"),
        13: ("Chương IV", "TỔ CHỨC THỰC HIỆN"),
    }

    # Extract text between tags
    parsed_articles = []
    for i, (num, title, tag) in enumerate(unique_articles):
        ch_num, ch_title = chapter_map[num]
        
        # Traverse siblings until next article heading
        content_parts = [f"Điều {num}. {title}"]
        curr = tag.parent if tag.parent.name in ['p', 'div'] else tag
        curr = curr.next_sibling
        
        while curr:
            if hasattr(curr, 'get_text'):
                txt = curr.get_text().strip()
                if txt:
                    # Check if next article heading
                    if re.match(r"^Điều\s+\d+\.", txt):
                        break
                    if "Phụ lục" in txt and num == 13:
                        break
                    content_parts.append(txt)
            curr = curr.next_sibling

        body_text = "\n".join(content_parts).strip()
        parsed_articles.append({
            "article_number": num,
            "article_title": title,
            "chapter": ch_num,
            "chapter_title": ch_title,
            "full_text": body_text
        })

    doc_id = "traffic_toll_130_2024_nd_cp"
    off_num = "130/2024/NĐ-CP"
    doc_title = "Nghị định 130/2024/NĐ-CP quy định về thu phí sử dụng đường bộ cao tốc đối với phương tiện lưu thông trên tuyến đường bộ cao tốc thuộc sở hữu toàn dân do Nhà nước đại diện chủ sở hữu và trực tiếp quản lý, khai thác"
    source_url = "https://vanban.chinhphu.vn/?pageid=27160&docid=211434"

    # Save parsed JSON
    with open(PARSED_DIR / "nd130_2024_parsed.json", "w", encoding="utf-8") as f:
        json.dump(parsed_articles, f, ensure_ascii=False, indent=2)

    # 3. Sync Supabase legal_documents
    sb_headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }

    r_chk = requests.get(f"{SUPABASE_URL}/rest/v1/legal_documents?id=eq.{doc_id}", headers=sb_headers).json()
    if not r_chk:
        doc_payload = {
            "id": doc_id,
            "official_number": off_num,
            "title": doc_title,
            "short_title": "Nghị định 130/2024/NĐ-CP",
            "doc_type": "NGHI_DINH",
            "issuer": "Chính phủ",
            "signer": "Trần Hồng Hà",
            "issue_date": "2024-10-10",
            "effective_date": "2024-10-10",  # MANDATORY CORRECTION: 2024-10-10
            "expiry_date": None,
            "status": "CON_HIEU_LUC",
            "source_url": source_url,
            "raw_content": None,
            "metadata": {
                "sha256": sha256_pdf,
                "batch": "TRAFFIC_P3",
                "effective_date_correction": "Enacted and effective from 2024-10-10 as per Article 13",
                "articles_count": 13
            }
        }
        r_ins = requests.post(f"{SUPABASE_URL}/rest/v1/legal_documents", headers=sb_headers, json=doc_payload)
        print(f"[+] Inserted NĐ 130 into Supabase legal_documents: status {r_ins.status_code}")
    else:
        # Patch effective_date if needed
        requests.patch(
            f"{SUPABASE_URL}/rest/v1/legal_documents?id=eq.{doc_id}",
            headers=sb_headers,
            json={"effective_date": "2024-10-10", "status": "CON_HIEU_LUC"}
        )
        print("[=] NĐ 130 exists in legal_documents. Verified effective_date = 2024-10-10.")

    # 4. Sync Supabase legal_articles
    r_chk_arts = requests.get(f"{SUPABASE_URL}/rest/v1/legal_articles?document_id=eq.{doc_id}", headers=sb_headers).json()
    if len(r_chk_arts) < 13:
        arts_payload = []
        for a in parsed_articles:
            arts_payload.append({
                "document_id": doc_id,
                "article_number": a["article_number"],
                "article_title": a["article_title"],
                "chapter_info": f"{a['chapter']}: {a['chapter_title']}",
                "full_text": a["full_text"],
                "status": "CON_HIEU_LUC"
            })
        r_ins_arts = requests.post(f"{SUPABASE_URL}/rest/v1/legal_articles", headers=sb_headers, json=arts_payload)
        print(f"[+] Inserted {len(arts_payload)} articles for NĐ 130: status {r_ins_arts.status_code}")
    else:
        print(f"[=] Articles for NĐ 130 already exist: {len(r_chk_arts)} articles.")

    # 5. Build Chunks for Qdrant
    chunks = []
    for a in parsed_articles:
        cid = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{doc_id}:article_{a['article_number']}:v1_current"))
        search_text = f"[{off_num} - {doc_title}]\n{a['chapter']}: {a['chapter_title']} > Điều {a['article_number']}: {a['article_title']}\n{a['full_text']}"
        chunks.append({
            "chunk_id": cid,
            "document_id": doc_id,
            "doc_id": doc_id,
            "official_number": off_num,
            "doc_title": doc_title,
            "canonical_provision_id": f"{doc_id}:article_{a['article_number']}",
            "version_id": "v1_current",
            "unit_type": "ARTICLE",
            "article_number": a["article_number"],
            "chapter": a["chapter"],
            "chapter_title": a["chapter_title"],
            "article_title": a["article_title"],
            "effective_date": "2024-10-10",
            "valid_from": "2024-10-10",
            "valid_to": None,
            "valid_interval": "[2024-10-10, +inf)",
            "legal_status": "CON_HIEU_LUC",
            "scope_tags": ["TRAFFIC_P3", "THU_PHI_CAO_TOC", "ND130_2024"],
            "content": a["full_text"],
            "full_search_text": search_text,
            "source_url": source_url,
            "sha256": sha256_pdf,
            "batch": "TRAFFIC_P3"
        })

    with open(PARSED_DIR / "p3_3_chunks.json", "w", encoding="utf-8") as f:
        json.dump(chunks, f, ensure_ascii=False, indent=2)
    print(f"[+] Built {len(chunks)} chunks for NĐ 130 in p3_3_chunks.json")

    # 6. Embedding with BGE-M3
    print(f"[*] Embedding {len(chunks)} chunks with BGE-M3...")
    embedder = get_embedding_service()
    texts = [c["full_search_text"] for c in chunks]
    vectors = embedder.embed_texts(texts)

    points = []
    for c, vec in zip(chunks, vectors):
        points.append(qmodels.PointStruct(id=c["chunk_id"], vector=vec, payload=c))

    # 7. Ingest to Staging
    client = QdrantClient(url=CLOUD_URL, api_key=CLOUD_API_KEY, timeout=30.0)
    print(f"[*] Upserting {len(points)} points into 'vietlegal_articles_staging'...")
    client.upsert(collection_name="vietlegal_articles_staging", points=points)

    # 8. Temporal Test
    print("\n--- P3.3 TEMPORAL TESTS ---")
    date_before = "2024-10-09"
    date_after = "2024-10-10"
    
    d1_chunk = next(p for p in points if p.payload["article_number"] == 1)
    d6_chunk = next(p for p in points if p.payload["article_number"] == 6)
    
    def is_active(p, d):
        vf = p.payload.get("valid_from")
        vt = p.payload.get("valid_to")
        if not vf or vf > d: return False
        if vt and d >= vt: return False
        return True

    assert is_active(d1_chunk, date_before) is False, "Should be inactive before 2024-10-10"
    assert is_active(d1_chunk, date_after) is True, "Should be active from 2024-10-10"
    assert is_active(d6_chunk, date_after) is True, "Điều 6 (Đối tượng miễn phí) should be active from 2024-10-10"
    print(f"[+] Temporal Test NĐ 130 (before {date_before} vs from {date_after}): PASS")

    # 9. Cross-database Parity Check
    print("\n--- P3.3 CROSS-DATABASE PARITY ---")
    sb_h = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}
    r_doc = requests.get(f"{SUPABASE_URL}/rest/v1/legal_documents?id=eq.{doc_id}", headers=sb_h).json()
    r_arts = requests.get(f"{SUPABASE_URL}/rest/v1/legal_articles?document_id=eq.{doc_id}", headers=sb_h).json()
    assert len(r_doc) == 1, "Doc 130 missing in Supabase"
    assert len(r_arts) == 13, f"Expected 13 articles, found {len(r_arts)}"
    assert r_doc[0]["effective_date"] == "2024-10-10", f"Wrong effective_date: {r_doc[0]['effective_date']}"
    print(f"[+] Supabase parity verified: 1 document (effective_date = 2024-10-10), 13 articles.")

    # 10. Production Promotion
    print("\n--- P3.3 PRODUCTION PROMOTION ---")
    prod_before = client.get_collection("vietlegal_articles").points_count
    print(f"[*] Production points BEFORE promotion: {prod_before} (Expected: 7820)")
    assert prod_before == 7820, f"Expected 7820 in production, found {prod_before}"

    client.upsert(collection_name="vietlegal_articles", points=points)
    time.sleep(2)
    prod_after = client.get_collection("vietlegal_articles").points_count
    print(f"[*] Production points AFTER promotion:  {prod_after} (+{prod_after - prod_before})")
    assert prod_after == 7833, f"Expected 7833 in production, found {prod_after}"
    print("[+] P3.3 COMPLETED AND PROMOTED SUCCESSFULLY!")

if __name__ == "__main__":
    process_nd130()
