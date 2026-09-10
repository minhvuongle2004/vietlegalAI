import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
import json
from pathlib import Path

MANIFEST_DIR = Path(__file__).resolve().parent
DELEGATION_MANIFEST_FILE = MANIFEST_DIR / "authority_delegation_manifest.json"

def build_delegation_manifest():
    delegations = {
        "metadata": {
            "root_document": "165/2024/NĐ-CP",
            "delegation_model": "authority_and_procedural_overlay (Provision-level Non-text modifying)",
            "temporal_convention": "[valid_from, valid_to)"
        },
        "nd140_authority_delegations": [
            {
                "source_document": "140/2025/NĐ-CP",
                "source_article": "Điều 23",
                "source_clause": "Khoản 2",
                "target_document": "165/2024/NĐ-CP",
                "target_article": "Điều 8",
                "target_clause": "Khoản 9",
                "target_point": "Điểm c",
                "delegated_authority": "UBND cấp tỉnh",
                "effect_type": "AUTHORITY_DELEGATION",
                "valid_from": "2025-07-01",
                "valid_to": "2026-07-01",
                "valid_interval": "[2025-07-01, 2026-07-01)",
                "source_locator": "NĐ 140/2025 Điều 23 Khoản 2; bãi bỏ bởi NĐ 241 Điều 26 Khoản 2"
            },
            {
                "source_document": "140/2025/NĐ-CP",
                "source_article": "Điều 23",
                "source_clause": "Khoản 3",
                "target_document": "165/2024/NĐ-CP",
                "target_article": "Điều 18",
                "target_clause": "Khoản 2",
                "target_point": "Điểm c",
                "delegated_authority": "UBND cấp xã",
                "effect_type": "AUTHORITY_DELEGATION",
                "valid_from": "2025-07-01",
                "valid_to": "2026-07-01",
                "valid_interval": "[2025-07-01, 2026-07-01)",
                "source_locator": "NĐ 140/2025 Điều 23 Khoản 3; bãi bỏ bởi NĐ 241 Điều 26 Khoản 2"
            },
            {
                "source_document": "140/2025/NĐ-CP",
                "source_article": "Điều 23",
                "source_clause": "Khoản 4",
                "target_document": "165/2024/NĐ-CP",
                "target_article": "Điều 20",
                "target_clause": "Khoản 7",
                "target_point": None,
                "delegated_authority": "UBND cấp xã",
                "effect_type": "AUTHORITY_DELEGATION",
                "valid_from": "2025-07-01",
                "valid_to": "2026-07-01",
                "valid_interval": "[2025-07-01, 2026-07-01)",
                "source_locator": "NĐ 140/2025 Điều 23 Khoản 4; bãi bỏ bởi NĐ 241 Điều 26 Khoản 2"
            },
            {
                "source_document": "140/2025/NĐ-CP",
                "source_article": "Điều 23",
                "source_clause": "Khoản 5",
                "target_document": "165/2024/NĐ-CP",
                "target_article": "Điều 21",
                "target_clause": "Khoản 5",
                "target_point": "Điểm c",
                "delegated_authority": "UBND cấp xã",
                "effect_type": "AUTHORITY_DELEGATION",
                "valid_from": "2025-07-01",
                "valid_to": "2026-07-01",
                "valid_interval": "[2025-07-01, 2026-07-01)",
                "source_locator": "NĐ 140/2025 Điều 23 Khoản 5; bãi bỏ bởi NĐ 241 Điều 26 Khoản 2"
            },
            {
                "source_document": "140/2025/NĐ-CP",
                "source_article": "Điều 23",
                "source_clause": "Khoản 6",
                "target_document": "165/2024/NĐ-CP",
                "target_article": "Điều 24",
                "target_clause": "Khoản 3",
                "target_point": None,
                "delegated_authority": "Cục Đường bộ Việt Nam, Sở Xây dựng, UBND cấp xã theo đường được giao quản lý",
                "effect_type": "AUTHORITY_DELEGATION",
                "valid_from": "2025-07-01",
                "valid_to": "2026-07-01",
                "valid_interval": "[2025-07-01, 2026-07-01)",
                "source_locator": "NĐ 140/2025 Điều 23 Khoản 6; bãi bỏ bởi NĐ 241 Điều 26 Khoản 2"
            },
            {
                "source_document": "140/2025/NĐ-CP",
                "source_article": "Điều 23",
                "source_clause": "Khoản 7",
                "target_document": "165/2024/NĐ-CP",
                "target_article": "Điều 31",
                "target_clause": "Khoản 3",
                "target_point": "Điểm c",
                "delegated_authority": "UBND cấp xã",
                "effect_type": "AUTHORITY_DELEGATION",
                "valid_from": "2025-07-01",
                "valid_to": "2026-07-01",
                "valid_interval": "[2025-07-01, 2026-07-01)",
                "source_locator": "NĐ 140/2025 Điều 23 Khoản 7; bãi bỏ bởi NĐ 241 Điều 26 Khoản 2"
            },
            {
                "source_document": "140/2025/NĐ-CP",
                "source_article": "Điều 23",
                "source_clause": "Khoản 8",
                "target_document": "165/2024/NĐ-CP",
                "target_article": "Điều 32",
                "target_clause": "Khoản 3",
                "target_point": None,
                "delegated_authority": "Cục Đường bộ Việt Nam, Sở Xây dựng, UBND cấp xã, người quản lý/sử dụng đường bộ theo đường được giao quản lý",
                "effect_type": "AUTHORITY_DELEGATION",
                "valid_from": "2025-07-01",
                "valid_to": None,
                "valid_interval": "[2025-07-01, null)",
                "source_locator": "NĐ 140/2025 Điều 23 Khoản 8; KHÔNG BỊ BÃI BỎ bởi NĐ 241 Điều 26 Khoản 2"
            }
        ],
        "nd144_road_manifest": {
            "source_chapter": "Chương IV - Phân quyền, phân cấp trong lĩnh vực giao thông đường bộ",
            "source_article": "Điều 30",
            "deleted_invalid_mappings": [
                {"invalid_source": "Điều 32", "reason": "Thuộc Mục 2 Giao thông đường sắt (NĐ 56/2018)"},
                {"invalid_source": "Điều 33", "reason": "Thuộc Mục 2 Giao thông đường sắt"},
                {"invalid_source": "Điều 34", "reason": "Thuộc Mục 3 Giao thông hàng hải"},
                {"invalid_source": "Điều 35", "reason": "Thuộc Mục 4 Giao thông đường thủy nội địa"}
            ],
            "authority_delegations": [
                {
                    "source_clause": "Khoản 1",
                    "target_document": "165/2024/NĐ-CP",
                    "target_provisions": [
                        "Điều 37",
                        "Điều 39",
                        "Điều 40",
                        "Điều 41",
                        "Khoản 3 Điều 44"
                    ],
                    "delegated_authority": "UBND cấp tỉnh",
                    "effect_type": "AUTHORITY_DELEGATION",
                    "valid_from": "2025-07-01",
                    "valid_to": None,
                    "valid_interval": "[2025-07-01, null)",
                    "source_locator": "NĐ 144/2025 Điều 30 Khoản 1"
                },
                {
                    "source_clause": "Khoản 2",
                    "target_document": "165/2024/NĐ-CP",
                    "target_provisions": [
                        "Khoản 1 Điều 45",
                        "Khoản 2 Điểm h Điều 45"
                    ],
                    "delegated_authority": "UBND cấp tỉnh",
                    "effect_type": "AUTHORITY_DELEGATION",
                    "valid_from": "2025-07-01",
                    "valid_to": None,
                    "valid_interval": "[2025-07-01, null)",
                    "source_locator": "NĐ 144/2025 Điều 30 Khoản 2"
                },
                {
                    "source_clause": "Khoản 8",
                    "target_document": "165/2024/NĐ-CP",
                    "target_provisions": [
                        "Khoản 2 Điểm b Điều 26"
                    ],
                    "delegated_authority": "Cơ quan chuyên môn thuộc UBND cấp tỉnh",
                    "effect_type": "AUTHORITY_DELEGATION",
                    "valid_from": "2025-07-01",
                    "valid_to": None,
                    "valid_interval": "[2025-07-01, null)",
                    "source_locator": "NĐ 144/2025 Điều 30 Khoản 8"
                }
            ],
            "procedural_overlays": [
                {
                    "source_clause": "Khoản 4",
                    "target_document": "165/2024/NĐ-CP",
                    "target_provisions": [
                        "Điều 37",
                        "Điều 39"
                    ],
                    "effect_type": "PROCEDURAL_OVERLAY",
                    "description": "Rút ngắn và chuẩn hóa thời hạn xử lý thủ tục hành chính liên quan NĐ 165",
                    "valid_from": "2025-07-01",
                    "valid_to": None,
                    "valid_interval": "[2025-07-01, null)",
                    "source_locator": "NĐ 144/2025 Điều 30 Khoản 4"
                },
                {
                    "source_clause": "Khoản 5",
                    "target_document": "165/2024/NĐ-CP",
                    "target_provisions": [
                        "Thủ tục hành chính đường bộ chung"
                    ],
                    "effect_type": "PROCEDURAL_OVERLAY",
                    "description": "Quy định hình thức nộp hồ sơ trực tuyến, qua bưu chính công ích hoặc trực tiếp",
                    "valid_from": "2025-07-01",
                    "valid_to": None,
                    "valid_interval": "[2025-07-01, null)",
                    "source_locator": "NĐ 144/2025 Điều 30 Khoản 5"
                },
                {
                    "source_clause": "Khoản 7",
                    "target_document": "165/2024/NĐ-CP",
                    "target_provisions": [
                        "Khoản 5 Điểm a Điều 29"
                    ],
                    "effect_type": "PROCEDURAL_MODIFICATION",
                    "description": "Bãi bỏ yêu cầu lấy ý kiến một số cơ quan trong quy trình cấp phép tại Điểm a Khoản 5 Điều 29 NĐ 165",
                    "valid_from": "2025-07-01",
                    "valid_to": None,
                    "valid_interval": "[2025-07-01, null)",
                    "source_locator": "NĐ 144/2025 Điều 30 Khoản 7"
                }
            ]
        }
    }
    with open(DELEGATION_MANIFEST_FILE, "w", encoding="utf-8") as f:
        json.dump(delegations, f, ensure_ascii=False, indent=2)
    print(f"[+] Successfully regenerated {DELEGATION_MANIFEST_FILE.name}")
    return delegations

if __name__ == "__main__":
    build_delegation_manifest()
