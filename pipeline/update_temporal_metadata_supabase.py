import os
import sys
import requests
import dotenv

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

dotenv.load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL", "").rstrip("/")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

def update_metadata():
    print("=" * 60)
    print("   CẬP NHẬT TEMPORAL METADATA TRÊN SUPABASE")
    print("=" * 60)

    # 1. Cập nhật Luật BHXH 2014 (Hết hiệu lực từ 01/07/2025 -> expiry_date: 2025-06-30)
    bhxh_doc_url = f"{SUPABASE_URL}/rest/v1/legal_documents?id=eq.bhxh_58_2014_qh13"
    bhxh_payload = {
        "effective_date": "2016-01-01",
        "expiry_date": "2025-06-30",
        "status": "HET_HIEU_LUC"
    }
    r = requests.patch(bhxh_doc_url, headers=headers, json=bhxh_payload)
    print(f"[*] Cập nhật legal_documents cho bhxh_58_2014_qh13: status {r.status_code}")

    # Cập nhật status trong legal_articles cho bhxh_58_2014_qh13
    bhxh_art_url = f"{SUPABASE_URL}/rest/v1/legal_articles?document_id=eq.bhxh_58_2014_qh13"
    r_art = requests.patch(bhxh_art_url, headers=headers, json={"status": "HET_HIEU_LUC"})
    print(f"[*] Cập nhật legal_articles cho bhxh_58_2014_qh13: status {r_art.status_code}")

    # 2. Đảm bảo các văn bản còn lại có status CON_HIEU_LUC và expiry_date is null
    other_docs = [
        ("bllđ_45_2019_qh14", "2021-01-01"),
        ("nd_145_2020_nd_cp", "2021-02-01"),
        ("nd_12_2022_nd_cp", "2022-01-17"),
        ("nd_74_2024_nd_cp", "2024-07-01"),
        ("ldn_59_2020_qh14", "2021-01-01"),
        ("nd_01_2021_nd_cp", "2021-01-04"),
        ("nd_122_2021_nd_cp", "2022-01-01"),
        ("nd_135_2020_nd_cp", "2021-01-01"),
        ("vieclam_38_2013_qh13", "2015-01-01"),
    ]

    for doc_id, eff_date in other_docs:
        doc_url = f"{SUPABASE_URL}/rest/v1/legal_documents?id=eq.{doc_id}"
        payload = {
            "effective_date": eff_date,
            "expiry_date": None,
            "status": "CON_HIEU_LUC"
        }
        res = requests.patch(doc_url, headers=headers, json=payload)
        print(f"[+] Document {doc_id}: {res.status_code}")

    print("\n[DONE] Hoàn tất cập nhật Temporal Metadata trong Supabase!")

if __name__ == "__main__":
    update_metadata()
