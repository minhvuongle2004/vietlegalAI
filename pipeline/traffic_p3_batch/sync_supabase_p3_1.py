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

def sync_p3_1():
    print("=" * 80)
    print("   P3.1 SUPABASE SYNC: NĐ 168/2024 + NĐ 238/2026")
    print("=" * 80)

    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }

    # 1. Update NĐ 168 metadata.amended_by
    r_chk_168 = requests.get(f"{SUPABASE_URL}/rest/v1/legal_documents?id=eq.traffic_penalty_168_2024_nd_cp", headers=headers).json()
    if r_chk_168:
        doc168 = r_chk_168[0]
        meta168 = doc168.get("metadata") or {}
        amended_list = meta168.get("amended_by") or []
        if "238/2026/NĐ-CP" not in amended_list:
            amended_list.append("238/2026/NĐ-CP")
        meta168["amended_by"] = amended_list
        meta168["batch"] = "TRAFFIC_P3"
        requests.patch(
            f"{SUPABASE_URL}/rest/v1/legal_documents?id=eq.traffic_penalty_168_2024_nd_cp",
            headers=headers,
            json={"metadata": meta168, "short_title": "Nghị định 168/2024/NĐ-CP"}
        )
        print("[+] Updated NĐ 168 amended_by: ['238/2026/NĐ-CP']")

    # 2. Check / Insert NĐ 238 into legal_documents
    doc_id_238 = "traffic_penalty_amendment_238_2026_nd_cp"
    r_chk_238 = requests.get(f"{SUPABASE_URL}/rest/v1/legal_documents?id=eq.{doc_id_238}", headers=headers).json()
    
    if not r_chk_238:
        doc238_payload = {
            "id": doc_id_238,
            "official_number": "238/2026/NĐ-CP",
            "title": "Nghị định sửa đổi, bổ sung một số điều của Nghị định số 168/2024/NĐ-CP ngày 26 tháng 12 năm 2024 của Chính phủ quy định xử phạt vi phạm hành chính về trật tự, an toàn giao thông trong lĩnh vực giao thông đường bộ; trừ điểm, phục hồi điểm giấy phép lái xe",
            "short_title": "Nghị định 238/2026/NĐ-CP",
            "doc_type": "NGHI_DINH",
            "issuer": "Chính phủ",
            "signer": "Trần Lưu Quang",
            "issue_date": "2026-06-26",
            "effective_date": "2026-08-15",
            "expiry_date": None,
            "status": "CON_HIEU_LUC",
            "source_url": "https://vanban.chinhphu.vn/?pageid=27160&docid=212450",
            "raw_content": None,
            "metadata": {
                "sha256": "36ca5dd9b7f482644edc35a79551d9a1b6017ebc400867f2d091c03c79ccb896",
                "amends": ["168/2024/NĐ-CP"],
                "target_document_id": "traffic_penalty_168_2024_nd_cp",
                "document_role": "AMENDMENT",
                "batch": "TRAFFIC_P3"
            }
        }
        r_ins = requests.post(f"{SUPABASE_URL}/rest/v1/legal_documents", headers=headers, json=doc238_payload)
        print(f"[+] Inserted NĐ 238 into legal_documents: status {r_ins.status_code}")
    else:
        print("[=] NĐ 238 already exists in legal_documents.")

    # 3. Check / Insert articles for NĐ 238 (Điều 1, Điều 2)
    r_chk_art238 = requests.get(f"{SUPABASE_URL}/rest/v1/legal_articles?document_id=eq.{doc_id_238}", headers=headers).json()
    if len(r_chk_art238) < 2:
        articles_238 = [
            {
                "document_id": doc_id_238,
                "article_number": 1,
                "article_title": "Sửa đổi, bổ sung một số điều của Nghị định số 168/2024/NĐ-CP",
                "full_text": """Điều 1. Sửa đổi, bổ sung một số điều của Nghị định số 168/2024/NĐ-CP
1. Bổ sung điểm q vào khoản 1 và điểm h vào khoản 3 Điều 5 (Xử phạt người điều khiển xe ô tô vi phạm quy tắc giao thông).
2. Sửa đổi, bổ sung khoản 8 Điều 13 (Xử phạt hành vi vi phạm quy định về biển số xe).
3. Bổ sung khoản 6a vào Điều 14 (Xử phạt vi phạm điều kiện vận tải).""",
                "chapter_info": "Chương I: QUY ĐỊNH CHUNG",
                "status": "CON_HIEU_LUC"
            },
            {
                "document_id": doc_id_238,
                "article_number": 2,
                "article_title": "Hiệu lực thi hành",
                "full_text": "Điều 2. Hiệu lực thi hành\nNghị định này có hiệu lực thi hành từ ngày 15 tháng 08 năm 2026.",
                "chapter_info": "Chương I: QUY ĐIH CHUNG",
                "status": "CON_HIEU_LUC"
            }
        ]
        r_ins_art = requests.post(f"{SUPABASE_URL}/rest/v1/legal_articles", headers=headers, json=articles_238)
        print(f"[+] Inserted {len(articles_238)} articles for NĐ 238: status {r_ins_art.status_code}")
    else:
        print(f"[=] Articles for NĐ 238 already exist: {len(r_chk_art238)} articles.")

    # Verify counts
    h_cnt = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Prefer": "count=exact"}
    r_cnt_docs = requests.get(f"{SUPABASE_URL}/rest/v1/legal_documents?select=id", headers=h_cnt, params={"limit": 1})
    r_cnt_arts = requests.get(f"{SUPABASE_URL}/rest/v1/legal_articles?select=id", headers=h_cnt, params={"limit": 1})
    cnt_docs = r_cnt_docs.headers.get("Content-Range", "0/0").split("/")[-1]
    cnt_arts = r_cnt_arts.headers.get("Content-Range", "0/0").split("/")[-1]
    print(f"[*] Supabase status after P3.1: documents = {cnt_docs}, articles = {cnt_arts}")

if __name__ == "__main__":
    sync_p3_1()
