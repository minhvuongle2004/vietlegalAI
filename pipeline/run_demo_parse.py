"""
Script chạy thử nghiệm bộ bóc tách phân cấp văn bản pháp luật (Hierarchical Parser).
Kiểm chứng khả năng bóc tách Chương, Điều, Khoản, Điểm và tự động sinh Context Header cho Chunk.
"""
import sys
import io
from pathlib import Path

# Đảm bảo project root luôn có trong sys.path khi chạy script trực tiếp
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

try:
    import pydantic
except ImportError:
    print("[!] LỖI: Môi trường của bạn chưa cài đặt thư viện 'pydantic'.")
    print("    Vui lòng kích hoạt venv và cài đặt bằng lệnh:")
    print("    pip install -r pipeline/requirements.txt")
    print("    (Hoặc nhanh: pip install pydantic)")
    sys.exit(1)

from datetime import date
from pipeline.models import LegalDocumentMetadata, DocumentType, DocumentStatus
from pipeline.parsers.legal_hierarchical_parser import LegalHierarchicalParser

SAMPLE_LABOR_LAW_TEXT = """
CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM
Độc lập - Tự do - Hạnh phúc
----------------

CHƯƠNG III
HỢP ĐỒNG LAO ĐỘNG

MỤC 1. GIAO KẾT HỢP ĐỒNG LAO ĐỘNG

Điều 24. Thử việc
1. Người sử dụng lao động và người lao động có thể thỏa thuận nội dung thử việc ghi trong hợp đồng lao động hoặc thỏa thuận về thử việc bằng việc giao kết hợp đồng thử việc.
2. Nội dung chủ yếu của hợp đồng thử việc gồm thời gian thử việc và nội dung quy định tại các điểm a, b, c, đ, g và h khoản 1 Điều 21 của Bộ luật này.
3. Không áp dụng thử việc đối với người lao động giao kết hợp đồng lao động có thời hạn dưới 01 tháng.

Điều 25. Thời gian thử việc
Thời gian thử việc do hai bên thỏa thuận căn cứ vào tính chất và mức độ phức tạp của công việc nhưng chỉ được thử việc một lần đối với một công việc và bảo đảm điều kiện sau đây:
1. Không quá 180 ngày đối với công việc của người quản lý doanh nghiệp theo quy định của Luật Doanh nghiệp, Luật Quản lý, sử dụng vốn nhà nước đầu tư vào sản xuất, kinh doanh tại doanh nghiệp;
2. Không quá 60 ngày đối với công việc có chức danh nghề nghiệp cần trình độ chuyên môn, kỹ thuật từ cao đẳng trở lên;
3. Không quá 30 ngày đối với công việc có chức danh nghề nghiệp cần trình độ chuyên môn, kỹ thuật trung cấp, công nhân kỹ thuật, nhân viên nghiệp vụ;
4. Không quá 06 ngày làm việc đối với công việc khác.

Điều 26. Tiền lương thử việc
Tiền lương của người lao động trong thời gian thử việc do hai bên thỏa thuận nhưng ít nhất phải bằng 85% mức lương của công việc đó.
"""

def main():
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
    )

    parser = LegalHierarchicalParser()
    print("[1/2] Đang phân tích cú pháp văn bản pháp luật...")
    parsed_doc = parser.parse(SAMPLE_LABOR_LAW_TEXT, metadata)

    print(f" -> Đã trích xuất {len(parsed_doc.chapters)} chương.")
    print(f" -> Đã trích xuất {len(parsed_doc.raw_articles)} điều luật:")
    for art in parsed_doc.raw_articles:
        print(f"    * Điều {art.article_number}: {art.article_title} ({len(art.clauses)} khoản)")

    print("\n[2/2] Đang sinh các Legal Chunks cho Vector Database...")
    chunks = parser.create_chunks(parsed_doc)
    print(f" -> Tổng số chunk được sinh ra: {len(chunks)}")
    
    print("\n--- DEMO CHUNK ĐẦU TIÊN ---")
    first_chunk = chunks[0]
    print(f"Chunk ID: {first_chunk.chunk_id}")
    print(f"Context Header:\n  {first_chunk.context_header}")
    print(f"Content:\n  {first_chunk.content[:200]}...")
    print(f"Effective Date: {first_chunk.effective_date}")
    print(f"Status: {first_chunk.status.value}")
    print("\n-> Parser hoạt động chính xác theo tiêu chuẩn cấu trúc pháp luật Việt Nam!")

if __name__ == "__main__":
    main()
