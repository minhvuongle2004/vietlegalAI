import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
import os
import json
import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
GOLD_DATASET_FILE = PROJECT_ROOT / "data" / "gold_evaluation" / "gold_retrieval_225_cases.json"
DIAGNOSIS_JSON = PROJECT_ROOT / "data" / "gold_evaluation" / "retrieval_failure_diagnosis.json"
OUTPUT_AUDIT_JSON = PROJECT_ROOT / "data" / "gold_evaluation" / "gold_225_dataset_audit.json"

with open(GOLD_DATASET_FILE, "r", encoding="utf-8") as f:
    gold_data = json.load(f)
cases = gold_data["cases"]

with open(DIAGNOSIS_JSON, "r", encoding="utf-8") as f:
    diag_data = json.load(f)
diag_cases = {c["test_case_id"]: c for c in diag_data["cases"]}

# Domain multi-evidence mapping for Vietnamese Traffic Law
# Maps query intent keywords to legal hierarchy relationships
LEGAL_HIERARCHY_MAP = {
    "tốc độ": {
        "primary": ("38/2024/TT-BGTVT", "traffic_speed_distance_38_2024_tt_bgtvt", [6, 7, 8, 9, 11]),
        "supporting": [
            ("36/2024/QH15", "traffic_order_36_2024_qh15", [12], "Luật mẹ quy định nguyên tắc chấp hành tốc độ"),
            ("168/2024/NĐ-CP", "traffic_penalty_168_2024_nd_cp", [5, 6, 7], "Nghị định quy định chế tài xử phạt khi vi phạm tốc độ")
        ],
        "default_type": "B" # Nếu hỏi tốc độ tối đa có thể vừa áp dụng TT38 (kỹ thuật) vừa áp dụng Luật 36 (nguyên tắc)
    },
    "khoảng cách": {
        "primary": ("38/2024/TT-BGTVT", "traffic_speed_distance_38_2024_tt_bgtvt", [11]),
        "supporting": [
            ("36/2024/QH15", "traffic_order_36_2024_qh15", [12], "Luật mẹ quy định khoảng cách an toàn")
        ],
        "default_type": "D"
    },
    "đèn đỏ": {
        "primary": ("36/2024/QH15", "traffic_order_36_2024_qh15", [11]),
        "supporting": [
            ("168/2024/NĐ-CP", "traffic_penalty_168_2024_nd_cp", [5, 6], "Chế tài xử phạt vượt đèn đỏ"),
            ("51/2024/TT-BGTVT", "traffic_road_signs_qcvn41_51_2024_tt_bgtvt", [4, 10], "Quy chuẩn kỹ thuật tín hiệu đèn")
        ],
        "default_type": "B"
    },
    "dừng phương tiện": {
        "primary": ("73/2024/TT-BCA", "traffic_police_patrol_73_2024_tt_bca", [12, 13]),
        "supporting": [
            ("36/2024/QH15", "traffic_order_36_2024_qh15", [65, 66], "Luật mẹ quy định quyền hạn tuần tra kiểm soát dừng xe của CSGT")
        ],
        "default_type": "B"
    },
    "vneid": {
        "primary": ("73/2024/TT-BCA", "traffic_police_patrol_73_2024_tt_bca", [13]),
        "supporting": [
            ("151/2024/NĐ-CP", "traffic_guideline_151_2024_nd_cp", [10], "Nghị định hướng dẫn kiểm tra giấy tờ qua VNeID")
        ],
        "default_type": "B"
    },
    "biển số định danh": {
        "primary": ("79/2024/TT-BCA", "traffic_vehicle_registration_79_2024_tt_bca", [4, 7, 14, 23]),
        "supporting": [
            ("36/2024/QH15", "traffic_order_36_2024_qh15", [36, 37, 39], "Nguyên tắc cấp và quản lý biển số xe")
        ],
        "default_type": "B"
    },
    "trừ điểm": {
        "primary": ("36/2024/QH15", "traffic_order_36_2024_qh15", [62]),
        "supporting": [
            ("168/2024/NĐ-CP", "traffic_penalty_168_2024_nd_cp", [32], "Quy định chi tiết các hành vi bị trừ điểm GPLX")
        ],
        "default_type": "B"
    },
    "phục hồi điểm": {
        "primary": ("65/2024/TT-BCA", "traffic_points_recovery_65_2024_tt_bca", [6, 9]),
        "supporting": [
            ("105/2026/TT-BCA", "traffic_points_recovery_105_2026_tt_bca", [1], "Sửa đổi điều kiện phục hồi điểm từ 01/07/2026"),
            ("36/2024/QH15", "traffic_order_36_2024_qh15", [62], "Nguyên tắc phục hồi điểm trong Luật")
        ],
        "default_type": "C"
    },
    "niên hạn": {
        "primary": ("89/2026/NĐ-CP", "traffic_inspection_framework_89_2026_nd_cp", [3]),
        "supporting": [
            ("36/2024/QH15", "traffic_order_36_2024_qh15", [40], "Luật quy định niên hạn sử dụng xe")
        ],
        "default_type": "B"
    },
    "đăng kiểm": {
        "primary": ("30/2026/TT-BXD", "traffic_inspection_procedures_30_2026_tt_bxd", [5, 8, 12]),
        "supporting": [
            ("89/2026/NĐ-CP", "traffic_inspection_framework_89_2026_nd_cp", [6], "Điều kiện kinh doanh dịch vụ đăng kiểm"),
            ("45/2026/TT-BXD", "traffic_inspection_amendment_45_2026_tt_bxd", [1], "Sửa đổi thủ tục đăng kiểm")
        ],
        "default_type": "B"
    },
    "sát hạch": {
        "primary": ("12/2025/TT-BCA", "traffic_driving_license_12_2025_tt_bca", [12, 14]),
        "supporting": [
            ("108/2026/TT-BCA", "traffic_driving_license_108_2026_tt_bca", [15, 22], "Quy chuẩn mới từ 01/07/2026"),
            ("94/2026/NĐ-CP", "traffic_driver_training_94_2026_nd_cp", [24, 26], "Điều kiện cơ sở sát hạch đào tạo lái xe"),
            ("36/2024/QH15", "traffic_order_36_2024_qh15", [58, 61], "Quy định khung về sát hạch GPLX")
        ],
        "default_type": "B"
    },
    "hợp đồng": {
        "primary": ("158/2024/NĐ-CP", "traffic_transport_158_2024_nd_cp", [7, 8]),
        "supporting": [
            ("161/2026/NĐ-CP", "traffic_transport_amendment_161_2026_nd_cp", [1], "Sửa đổi điều kiện kinh doanh vận tải xe hợp đồng"),
            ("35/2024/QH15", "road_35_2024_qh15", [56], "Quy định về kinh doanh vận tải đường bộ")
        ],
        "default_type": "C"
    }
}

audit_results = []
classification_counts = {
    "A": 0, # Chỉ có 1 căn cứ đúng
    "B": 0, # Có nhiều căn cứ đúng (Alternative valid grounds)
    "C": 0, # Cần đồng thời nhiều căn cứ (Co-requisite / Required set)
    "D": 0, # Cần căn cứ chính + căn cứ bổ trợ (Primary + Supporting)
    "E": 0  # Nhãn hiện tại chưa đủ rõ
}

false_miss_cases = []

for tc in cases:
    cid = tc["test_case_id"]
    q = tc["query"]
    q_l = q.lower()
    cat = tc["category"]
    exp = tc["expected_evidence"]
    as_of = tc.get("as_of_date")
    
    diag_c = diag_cases.get(cid, {})
    dense_rank = diag_c.get("dense_rank")
    rrf_rank = diag_c.get("rrf_rank")
    
    # Check if case matches any multi-evidence pattern
    matched_topic = None
    topic_data = None
    for kw, data in LEGAL_HIERARCHY_MAP.items():
        if kw in q_l:
            matched_topic = kw
            topic_data = data
            break
            
    # Classify case
    case_type = "A"
    primary_evidence = {
        "official_number": exp.get("official_number"),
        "document_id": exp.get("document_id"),
        "article": exp.get("article"),
        "clause": exp.get("clause"),
        "point": exp.get("point")
    }
    acceptable_supporting_evidence = []
    required_evidence_set = []
    evidence_type = "single_provision"
    evidence_relationship = "exclusive_ground"
    
    if cat in ["MULTI_DOCUMENT", "AMENDMENT_LINEAGE", "TEMPORAL_CONTRAST"]:
        # Naturally multi-evidence
        if cat == "AMENDMENT_LINEAGE":
            case_type = "C"
            evidence_type = "amendment_pair"
            evidence_relationship = "amended_by"
        elif cat == "TEMPORAL_CONTRAST":
            case_type = "C"
            evidence_type = "temporal_contrast_pair"
            evidence_relationship = "version_transition"
        elif cat == "MULTI_DOCUMENT":
            case_type = "D"
            evidence_type = "cross_regulatory_hierarchy"
            evidence_relationship = "law_and_implementing_decree"
    elif matched_topic and topic_data:
        case_type = topic_data.get("default_type", "B")
        evidence_type = "multi_tier_co_regulation"
        evidence_relationship = "statutory_and_regulatory_parallel"
        
        # Build supporting grounds
        for supp_off, supp_doc, supp_arts, desc in topic_data["supporting"]:
            if supp_doc.lower() != exp.get("document_id", "").lower():
                acceptable_supporting_evidence.append({
                    "official_number": supp_off,
                    "document_id": supp_doc,
                    "articles": supp_arts,
                    "description": desc
                })
        
        # If question is asking about both rule and penalty
        if any(k in q_l for k in ["mức phạt", "bị xử phạt", "phạt bao nhiêu"]):
            if "tốc độ" in q_l or "đèn đỏ" in q_l:
                case_type = "C"
                evidence_type = "violation_rule_plus_sanction"
                evidence_relationship = "co_requisite_rule_and_penalty"
    
    # Check for unclear label
    if not exp.get("document_id") or not exp.get("official_number"):
        case_type = "E"
        evidence_type = "incomplete_label"
        evidence_relationship = "unspecified"
        
    classification_counts[case_type] += 1
    
    # Check if this case was penalized as a false MISS
    # E.g. retriever found one of the acceptable supporting evidence at Rank 1-3, but got marked as MISS
    is_false_miss = bool(diag_c.get("retrieved_is_alternative"))
    false_miss_detail = diag_c.get("alt_matched_info")
    
    if is_false_miss:
        false_miss_cases.append({
            "test_case_id": cid,
            "query": q,
            "expected_single_label": f"{exp.get('official_number')} Điều {exp.get('article')}",
            "retrieved_evidence": diag_c.get("rrf_top3", [""])[0] if diag_c.get("rrf_top3") else "None",
            "alternative_match_info": false_miss_detail,
            "classification": case_type
        })
        
    audit_entry = {
        "test_case_id": cid,
        "category": cat,
        "query": q,
        "case_classification": case_type,
        "classification_meaning": {
            "A": "Chỉ có một căn cứ đúng duy nhất",
            "B": "Có nhiều căn cứ đúng đồng thời (Song song Luật - Nghị định - Thông tư)",
            "C": "Cần đồng thời nhiều căn cứ (Co-requisite: Quy tắc + Xử phạt, hoặc Cũ + Mới)",
            "D": "Cần căn cứ chính + căn cứ bổ trợ",
            "E": "Nhãn hiện tại chưa đủ rõ"
        }[case_type],
        "primary_evidence": primary_evidence,
        "acceptable_supporting_evidence": acceptable_supporting_evidence,
        "required_evidence_set": required_evidence_set,
        "evidence_type": evidence_type,
        "evidence_relationship": evidence_relationship,
        "audit_findings": {
            "dense_rank": dense_rank,
            "rrf_rank": rrf_rank,
            "is_false_miss_due_to_strict_label": is_false_miss,
            "false_miss_detail": false_miss_detail
        }
    }
    audit_results.append(audit_entry)

summary_stats = {
    "total_cases_audited": len(cases),
    "classification_distribution": classification_counts,
    "multi_evidence_total": classification_counts["B"] + classification_counts["C"] + classification_counts["D"],
    "single_evidence_total": classification_counts["A"],
    "unclear_label_total": classification_counts["E"],
    "false_miss_count": len(false_miss_cases),
    "false_miss_cases_sample": false_miss_cases[:10]
}

final_output = {
    "metadata": {
        "version": "1.0_tier1.6_audit",
        "description": "Gold 225 Dataset Label Audit & Multi-Evidence Analysis",
        "corpus_points_frozen": 7982
    },
    "summary": summary_stats,
    "cases_audit": audit_results
}

with open(OUTPUT_AUDIT_JSON, "w", encoding="utf-8") as f:
    json.dump(final_output, f, ensure_ascii=False, indent=2)

print("=== DATASET AUDIT SUMMARY ===")
print(f"Total cases audited: {len(cases)}")
print("Classification Breakdown:")
for k, v in classification_counts.items():
    pct = (v / len(cases)) * 100
    print(f"  Class {k}: {v:3d} cases ({pct:5.1f}%)")
print(f"Multi-evidence cases (B + C + D): {summary_stats['multi_evidence_total']} ({summary_stats['multi_evidence_total']/len(cases)*100:.1f}%)")
print(f"Total verified False Miss cases (retriever found valid supporting ground): {len(false_miss_cases)}")
