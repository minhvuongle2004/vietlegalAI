import json
from pathlib import Path

benchmark_path = Path("evals/vietlegal_benchmark.json")

with open(benchmark_path, "r", encoding="utf-8") as f:
    cases = json.load(f)

print(f"Current cases count: {len(cases)}")

# 1. Tag TC-01 -> TC-30 with as_of_date: "2024-12-31"
for tc in cases:
    if "as_of_date" not in tc:
        tc["as_of_date"] = "2024-12-31"

# 2. Define TC-31 to TC-34
new_cases = [
    {
        "id": "TC-31",
        "category": "temporal_version",
        "title": "Rút BHXH một lần trước ngày 01/07/2025 (Áp dụng Luật BHXH 2014)",
        "as_of_date": "2024-12-31",
        "query": "Tại thời điểm tháng 12/2024, người lao động sau 1 năm nghỉ việc không tiếp tục đóng BHXH và chưa đủ 20 năm đóng BHXH có được rút BHXH một lần không theo quy định Luật BHXH?",
        "expected_articles": [
            {"doc_keyword": "bhxh_58", "article_number": 60}
        ],
        "ground_truth": "Tại thời điểm năm 2024 (trước ngày 01/07/2025), áp dụng Điều 60 Luật BHXH 2014 và Nghị quyết 93/2015/QH13, người lao động sau 1 năm nghỉ việc không tiếp tục đóng BHXH mà chưa đủ 20 năm đóng BHXH có yêu cầu thì được hưởng BHXH một lần.",
        "expected_keywords": ["Điều 60", "Luật Bảo hiểm xã hội", "được hưởng|được rút", "một lần"],
        "forbidden_keywords": ["áp dụng luật bảo hiểm xã hội 2024"],
        "trap_type": "Temporal routing: Phải trích xuất Điều 60 Luật BHXH 2014 khi as_of_date là năm 2024, không được áp dụng Luật 2024."
    },
    {
        "id": "TC-32",
        "category": "temporal_version",
        "title": "Rút BHXH một lần từ ngày 01/07/2025 (Áp dụng Luật BHXH 2024)",
        "as_of_date": "2025-08-01",
        "query": "Từ ngày 01/07/2025 khi Luật BHXH 2024 có hiệu lực thi hành, điều kiện rút BHXH một lần đối với người lao động sau 12 tháng không thuộc diện tham gia BHXH bắt buộc được quy định tại điều nào?",
        "expected_articles": [
            {"doc_keyword": "bhxh_41", "article_number": [70, 102]}
        ],
        "ground_truth": "Từ ngày 01/07/2025, áp dụng Điều 70 (và Điều 102 cho BHXH tự nguyện) Luật Bảo hiểm xã hội 2024 (số 41/2024/QH15). Người lao động tham gia BHXH trước ngày 01/07/2025 sau 12 tháng không thuộc diện tham gia BHXH bắt buộc mà chưa đủ 20 năm đóng thì được hưởng BHXH một lần.",
        "expected_keywords": ["Điều 70|Điều 102", "Luật Bảo hiểm xã hội 2024|41/2024/QH15", "một lần"],
        "forbidden_keywords": ["Điều 60 Luật Bảo hiểm xã hội 2014"],
        "trap_type": "Temporal routing: Phải chuyển sang Điều 70/102 Luật BHXH 2024 khi as_of_date sau 01/07/2025."
    },
    {
        "id": "TC-33",
        "category": "temporal_version",
        "title": "Thời gian đóng BHXH tối thiểu hưởng lương hưu 15 năm (Luật BHXH 2024)",
        "as_of_date": "2025-08-01",
        "query": "Theo Luật Bảo hiểm xã hội 2024 có hiệu lực từ ngày 01/07/2025, người lao động đủ tuổi nghỉ hưu cần đóng BHXH tối thiểu bao nhiêu năm để được hưởng lương hưu hàng tháng theo Điều 64?",
        "expected_articles": [
            {"doc_keyword": "bhxh_41", "article_number": 64}
        ],
        "ground_truth": "Theo Điều 64 Luật Bảo hiểm xã hội 2024, người lao động đủ tuổi nghỉ hưu và có thời gian đóng BHXH bắt buộc từ đủ 15 năm trở lên (thay vì 20 năm như Luật 2014) thì được hưởng lương hưu hàng tháng.",
        "expected_keywords": ["Điều 64", "15 năm", "Luật Bảo hiểm xã hội 2024|41/2024/QH15", "lương hưu"],
        "forbidden_keywords": ["bắt buộc phải đủ 20 năm mới được hưởng lương hưu"],
        "trap_type": "Substantive change: Giảm từ 20 năm xuống 15 năm đóng BHXH tối thiểu theo Điều 64 Luật 2024."
    },
    {
        "id": "TC-34",
        "category": "temporal_version",
        "title": "Quyền lợi và phạm vi điều chỉnh theo Luật BHYT sửa đổi 2024 (số 51/2024/QH15)",
        "as_of_date": "2025-08-01",
        "query": "Luật sửa đổi, bổ sung một số điều của Luật Bảo hiểm y tế số 51/2024/QH15 có hiệu lực từ ngày 01/07/2025 sửa đổi quy định gì về mức hưởng và đăng ký khám bệnh, chữa bệnh bảo hiểm y tế?",
        "expected_articles": [
            {"doc_keyword": "bhyt_51", "article_number": 1}
        ],
        "ground_truth": "Theo Điều 1 Luật sửa đổi, bổ sung một số điều của Luật Bảo hiểm y tế 2024 (số 51/2024/QH15), luật sửa đổi các quy định về đối tượng tham gia, đăng ký KCB ban đầu, chuyển tuyến và mức hưởng BHYT khi KCB đúng tuyến, trái tuyến.",
        "expected_keywords": ["51/2024/QH15|Luật Bảo hiểm y tế", "Điều 1", "khám bệnh|chữa bệnh", "mức hưởng|tuyến"],
        "forbidden_keywords": [],
        "trap_type": "New statute retrieval: Trích xuất chính xác văn bản sửa đổi BHYT số 51/2024/QH15."
    }
]

# Check existing IDs to avoid duplicates
existing_ids = {tc["id"] for tc in cases}
for nc in new_cases:
    if nc["id"] not in existing_ids:
        cases.append(nc)
        print(f"Added {nc['id']}: {nc['title']}")
    else:
        print(f"Skipping existing {nc['id']}")

with open(benchmark_path, "w", encoding="utf-8") as f:
    json.dump(cases, f, ensure_ascii=False, indent=2)

print(f"Updated benchmark saved! Total cases: {len(cases)}")
