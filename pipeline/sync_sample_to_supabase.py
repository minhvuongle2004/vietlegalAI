import sys
import io
from pathlib import Path
from datetime import date

# Đảm bảo project root trong sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

from pipeline.models import LegalDocumentMetadata, DocumentType, DocumentStatus
from pipeline.parsers.legal_hierarchical_parser import LegalHierarchicalParser
from pipeline.loaders.supabase_loader import SupabaseLegalLoader
from pipeline.run_demo_parse import SAMPLE_LABOR_LAW_TEXT


def main():
    print("[1/3] Bóc tách dữ liệu mẫu (Bộ luật Lao động 2019)...")
    metadata = LegalDocumentMetadata(
        doc_id="bllđ_45_2019_qh14",
        official_number="45/2019/QH14",
        title="Bộ luật Lao động năm 2019",
        short_title="Bộ luật Lao động 2019",
        doc_type=DocumentType.BO_LUAT,
        issuer="Quốc hội",
        issue_date=date(2019, 11, 20),
        effective_date=date(2021, 1, 1),
        status=DocumentStatus.CON_HIEU_LUC,
        source_url="https://vbpl.vn/TW/Pages/vbpq-toanvan.aspx?ItemID=140306",
    )

    parser = LegalHierarchicalParser()
    parsed_doc = parser.parse(SAMPLE_LABOR_LAW_TEXT, metadata)
    print(f" -> Đã trích xuất {len(parsed_doc.raw_articles)} điều luật.")

    print("\n[2/3] Đang kết nối và đồng bộ lên Supabase Cloud...")
    loader = SupabaseLegalLoader()
    res = loader.sync_parsed_document(parsed_doc)

    print("\n[3/3] Kết quả đồng bộ:")
    print(f" -> Mã văn bản: {res['doc_id']}")
    print(f" -> Văn bản đã nạp vào 'legal_documents': {res['document_synced']}")
    print(f" -> Số điều luật đã nạp vào 'legal_articles': {res['articles_count']}")

    if res["document_synced"] and res["articles_count"] > 0:
        print("\n🎉 THÀNH CÔNG! Bạn có thể mở Supabase Table Editor để kiểm tra dữ liệu vừa nạp!")


if __name__ == "__main__":
    main()
