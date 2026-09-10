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

RAW_DIR = PROJECT_ROOT / "data" / "01_raw" / "traffic_p3_batch" / "161_2024_ND_CP"
RAW_DIR.mkdir(parents=True, exist_ok=True)
PARSED_DIR = PROJECT_ROOT / "data" / "03_parsed" / "traffic_p3_batch"
PARSED_DIR.mkdir(parents=True, exist_ok=True)

HTML_CACHE = r"C:\Users\vuong\.gemini\antigravity-ide\brain\d4e19d11-4f9f-41c0-a5d4-f7b6e3367760\.system_generated\steps\14991\content.md"

def process_nd161():
    print("=" * 80)
    print("   P3.4 PROCESSING: NĐ 161/2024/NĐ-CP (PARTIALLY_AFFECTED)")
    print("=" * 80)

    # 1. Update RAW manifest
    pdf_file = RAW_DIR / "161_2024_nd-cp_18122024-signed.pdf"
    with open(pdf_file, "rb") as f:
        pdf_bytes = f.read()
    sha256_pdf = hashlib.sha256(pdf_bytes).hexdigest()
    
    raw_manifest = [{
        "filename": "161_2024_nd-cp_18122024-signed.pdf",
        "relative_path": str(pdf_file.relative_to(PROJECT_ROOT)).replace("\\", "/"),
        "sha256": sha256_pdf,
        "file_size": len(pdf_bytes),
        "content_type": "application/pdf",
        "source_url": "https://datafiles.chinhphu.vn/cpp/files/vbpq/2024/12/161_2024_nd-cp_18122024-signed.pdf",
        "description": "Nghị định 161/2024/NĐ-CP official signed PDF"
    }]
    with open(RAW_DIR / "raw_manifest.json", "w", encoding="utf-8") as f:
        json.dump(raw_manifest, f, ensure_ascii=False, indent=2)
    print(f"[+] Verified RAW artifact: size={len(pdf_bytes)} bytes, sha256={sha256_pdf}")

    # 2. Parse 32 Articles from HTML
    with open(HTML_CACHE, "r", encoding="utf-8") as f:
        html_text = f.read()

    soup = BeautifulSoup(html_text, "html.parser")

    # Locate article headings
    article_headings = []
    # Search all tags that could contain "Điều X."
    for tag in soup.find_all(["b", "strong", "p", "div"]):
        txt = tag.get_text().strip()
        m = re.match(r"^Điều\s+(\d+)\.\s*(.*)", txt)
        if m:
            art_num = int(m.group(1))
            art_title = m.group(2).strip()
            if 1 <= art_num <= 32:
                article_headings.append((art_num, art_title, tag))

    # Keep unique by article number (first occurrence in main content)
    seen_nums = set()
    unique_articles = []
    for num, title, tag in article_headings:
        if num not in seen_nums:
            seen_nums.add(num)
            unique_articles.append((num, title, tag))

    unique_articles.sort(key=lambda x: x[0])
    print(f"[*] Extracted {len(unique_articles)} article headers from official text.")

    # Chapter mapping for 32 articles
    def get_chapter(num):
        if num <= 4:
            return ("Chương I", "QUY ĐỊNH CHUNG")
        elif num <= 8:
            return ("Chương II", "PHÂN LOẠI, DANH MỤC, ĐÓNG GÓI, DÁN NHÃN VÀ TẬP HUẤN AN TOÀN")
        elif num <= 17:
            return ("Chương III", "VẬN CHUYỂN HÀNG HÓA NGUY HIỂM VÀ CẤP GIẤY PHÉP VẬN CHUYỂN")
        elif num <= 27:
            return ("Chương IV", "TRÁCH NHIỆM CỦA CÁC BỘ, NGÀNH VÀ ỦY BAN NHÂN DÂN CẤP TỈNH")
        elif num <= 30:
            return ("Chương V", "TRÁCH NHIỆM CỦA TỔ CHỨC, CÁ NHÂN LIÊN QUAN")
        else:
            return ("Chương VI", "ĐIỀU KHOẢN THI HÀNH")

    parsed_articles = []
    for i, (num, title, tag) in enumerate(unique_articles):
        ch_num, ch_title = get_chapter(num)
        
        # Collect content
        content_parts = [f"Điều {num}. {title}"]
        curr = tag.parent if tag.parent.name in ['p', 'div'] else tag
        curr = curr.next_sibling
        
        while curr:
            if hasattr(curr, 'get_text'):
                txt = curr.get_text().strip()
                if txt:
                    # If hit next article heading
                    if re.match(r"^Điều\s+\d+\.", txt):
                        break
                    if "Phụ lục" in txt and num >= 31:
                        break
                    content_parts.append(txt)
            curr = curr.next_sibling

        body_text = "\n".join(content_parts).strip()
        
        # Provision status: Điều 14 affected by NĐ 140/2025
        status = "BI_SUA_DOI" if num == 14 else "CON_HIEU_LUC"
        
        parsed_articles.append({
            "article_number": num,
            "article_title": title,
            "chapter": ch_num,
            "chapter_title": ch_title,
            "full_text": body_text,
            "status": status
        })

    doc_id = "traffic_dangerous_goods_161_2024_nd_cp"
    off_num = "161/2024/NĐ-CP"
    doc_title = "Nghị định 161/2024/NĐ-CP quy định Danh mục hàng hóa nguy hiểm, vận chuyển hàng hóa nguy hiểm và trình tự, thủ tục cấp giấy phép, cấp giấy chứng nhận hoàn thành chương trình tập huấn cho người lái xe hoặc người áp tải vận chuyển hàng hóa nguy hiểm trên đường bộ"
    source_url = "https://vanban.chinhphu.vn/?pageid=27160&docid=212085"

    with open(PARSED_DIR / "nd161_2024_parsed.json", "w", encoding="utf-8") as f:
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
            "short_title": "Nghị định 161/2024/NĐ-CP",
            "doc_type": "NGHI_DINH",
            "issuer": "Chính phủ",
            "signer": "Trần Hồng Hà",
            "issue_date": "2024-12-18",
            "effective_date": "2025-01-01",
            "expiry_date": None,
            "status": "HET_HIEU_LUC_MOT_PHAN",  # MANDATORY: PARTIALLY_AFFECTED
            "source_url": source_url,
            "raw_content": None,
            "metadata": {
                "sha256": sha256_pdf,
                "batch": "TRAFFIC_P3",
                "document_role": "PARTIALLY_AFFECTED",
                "partially_affected_by": ["140/2025/NĐ-CP"],
                "affected_provision": "Điều 14 Khoản 2 (thẩm quyền cấp giấy phép VPHH nguy hiểm)",
                "articles_count": len(parsed_articles)
            }
        }
        r_ins = requests.post(f"{SUPABASE_URL}/rest/v1/legal_documents", headers=sb_headers, json=doc_payload)
        print(f"[+] Inserted NĐ 161 into Supabase legal_documents (status: HET_HIEU_LUC_MOT_PHAN): status {r_ins.status_code}")
    else:
        # Patch status to HET_HIEU_LUC_MOT_PHAN
        requests.patch(
            f"{SUPABASE_URL}/rest/v1/legal_documents?id=eq.{doc_id}",
            headers=sb_headers,
            json={"status": "HET_HIEU_LUC_MOT_PHAN"}
        )
        print("[=] NĐ 161 exists in legal_documents. Status verified as HET_HIEU_LUC_MOT_PHAN.")

    # 4. Sync Supabase legal_articles
    r_chk_arts = requests.get(f"{SUPABASE_URL}/rest/v1/legal_articles?document_id=eq.{doc_id}", headers=sb_headers).json()
    if len(r_chk_arts) < len(parsed_articles):
        arts_payload = []
        for a in parsed_articles:
            arts_payload.append({
                "document_id": doc_id,
                "article_number": a["article_number"],
                "article_title": a["article_title"],
                "chapter_info": f"{a['chapter']}: {a['chapter_title']}",
                "full_text": a["full_text"],
                "status": a["status"]
            })
        r_ins_arts = requests.post(f"{SUPABASE_URL}/rest/v1/legal_articles", headers=sb_headers, json=arts_payload)
        print(f"[+] Inserted {len(arts_payload)} articles for NĐ 161: status {r_ins_arts.status_code}")
    else:
        print(f"[=] Articles for NĐ 161 already exist: {len(r_chk_arts)} articles.")

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
            "effective_date": "2025-01-01",
            "valid_from": "2025-01-01",
            "valid_to": None,
            "valid_interval": "[2025-01-01, +inf)",
            "legal_status": a["status"],
            "scope_tags": ["TRAFFIC_P3", "HANG_HOA_NGUY_HIEM", "ND161_2024"],
            "content": a["full_text"],
            "full_search_text": search_text,
            "source_url": source_url,
            "sha256": sha256_pdf,
            "batch": "TRAFFIC_P3"
        })

    with open(PARSED_DIR / "p3_4_chunks.json", "w", encoding="utf-8") as f:
        json.dump(chunks, f, ensure_ascii=False, indent=2)
    print(f"[+] Built {len(chunks)} chunks for NĐ 161 in p3_4_chunks.json")

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
    print("\n--- P3.4 TEMPORAL TESTS ---")
    date_before = "2024-12-31"
    date_after = "2025-01-01"
    
    d1_chunk = next(p for p in points if p.payload["article_number"] == 1)
    d14_chunk = next(p for p in points if p.payload["article_number"] == 14)
    
    def is_active(p, d):
        vf = p.payload.get("valid_from")
        vt = p.payload.get("valid_to")
        if not vf or vf > d: return False
        if vt and d >= vt: return False
        return True

    assert is_active(d1_chunk, date_before) is False, "Should be inactive before 2025-01-01"
    assert is_active(d1_chunk, date_after) is True, "Should be active from 2025-01-01"
    assert d14_chunk.payload["legal_status"] == "BI_SUA_DOI", "Điều 14 should be marked BI_SUA_DOI"
    print(f"[+] Temporal Test NĐ 161 (before {date_before} vs from {date_after}): PASS")
    print(f"[+] Provision status check (Điều 14: BI_SUA_DOI): PASS")

    # 9. Cross-database Parity Check
    print("\n--- P3.4 CROSS-DATABASE PARITY ---")
    sb_h = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}
    r_doc = requests.get(f"{SUPABASE_URL}/rest/v1/legal_documents?id=eq.{doc_id}", headers=sb_h).json()
    r_arts = requests.get(f"{SUPABASE_URL}/rest/v1/legal_articles?document_id=eq.{doc_id}", headers=sb_h).json()
    assert len(r_doc) == 1, "Doc 161 missing in Supabase"
    assert len(r_arts) == len(chunks), f"Expected {len(chunks)} articles, found {len(r_arts)}"
    assert r_doc[0]["status"] == "HET_HIEU_LUC_MOT_PHAN", f"Wrong doc status: {r_doc[0]['status']}"
    print(f"[+] Supabase parity verified: 1 document (status = HET_HIEU_LUC_MOT_PHAN), {len(r_arts)} articles.")

    # 10. Production Promotion
    print("\n--- P3.4 PRODUCTION PROMOTION ---")
    prod_before = client.get_collection("vietlegal_articles").points_count
    print(f"[*] Production points BEFORE promotion: {prod_before} (Expected: 7833)")
    assert prod_before == 7833, f"Expected 7833 in production, found {prod_before}"

    client.upsert(collection_name="vietlegal_articles", points=points)
    time.sleep(2)
    prod_after = client.get_collection("vietlegal_articles").points_count
    expected_after = prod_before + len(points)
    print(f"[*] Production points AFTER promotion:  {prod_after} (+{prod_after - prod_before})")
    assert prod_after == expected_after, f"Expected {expected_after} in production, found {prod_after}"
    print("[+] P3.4 COMPLETED AND PROMOTED SUCCESSFULLY!")

if __name__ == "__main__":
    process_nd161()
