import sys
import os
import re
import json
import hashlib
from pathlib import Path
from bs4 import BeautifulSoup

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
RAW_DIR = PROJECT_ROOT / "data" / "01_raw" / "traffic_p1_2_batch"
PARSED_DIR = PROJECT_ROOT / "data" / "03_parsed" / "traffic_p1_2_batch"
PARSED_DIR.mkdir(parents=True, exist_ok=True)

MANIFEST_FILE = RAW_DIR / "manifest.json"

with open(MANIFEST_FILE, "r", encoding="utf-8") as f:
    manifest = json.load(f)

# Provision-Level Legal Relations Registry
RELATIONS_REGISTRY = {
    "traffic_driver_training_94_2026_nd_cp": {
        "Điều 41": {
            "replaces": [
                {"target_document": "65/2016/NĐ-CP", "scope": "ALL", "effective_date": "2026-07-01"},
                {"target_document": "138/2018/NĐ-CP", "scope": "ALL", "effective_date": "2026-07-01"}
            ]
        }
    },
    "traffic_road_infra_amendment_241_2026_nd_cp": {
        "Điều 1": {
            "amends": [
                {"target_document": "165/2024/NĐ-CP", "target_provision": "Điều 8", "description": "Số hóa định danh tài sản kết cấu hạ tầng đường bộ", "effective_date": "2026-07-01"},
                {"target_document": "165/2024/NĐ-CP", "target_provision": "Điều 12", "description": "Tiêu chuẩn bảo trì đường bộ và đình chỉ thu phí nếu mất an toàn", "effective_date": "2026-07-01"},
                {"target_document": "165/2024/NĐ-CP", "target_provision": "Điều 15", "description": "Hành lang an toàn cao tốc 17,0m - 20,0m", "effective_date": "2026-07-01"},
                {"target_document": "165/2024/NĐ-CP", "target_provision": "Điều 19", "description": "Quy định đấu nối đường nhánh bắt buộc qua nút giao liên thông", "effective_date": "2026-07-01"},
                {"target_document": "165/2024/NĐ-CP", "target_provision": "Điều 24", "description": "Bắt buộc hệ thống giao thông thông minh ITS 24/7 trên cao tốc", "effective_date": "2026-07-01"},
                {"target_document": "165/2024/NĐ-CP", "target_provision": "Điều 28", "description": "Chia sẻ dữ liệu giám sát giao thông theo thời gian thực với CSGT (Điều 77 Luật TTATGTĐB)", "effective_date": "2026-07-01"},
                {"target_document": "165/2024/NĐ-CP", "target_provision": "Điều 32", "description": "Thu phí tự động ETC không dừng không barie trên cao tốc đầu tư công", "effective_date": "2026-07-01"},
                {"target_document": "165/2024/NĐ-CP", "target_provision": "Điều 36", "description": "Quy chuẩn trạm dừng nghỉ cao tốc cách nhau 50-60km có dịch vụ thiết yếu miễn phí", "effective_date": "2026-07-01"},
                {"target_document": "165/2024/NĐ-CP", "target_provision": "Điều 41", "description": "Giá trị pháp lý trực tiếp của hệ thống cân tải trọng tự động tốc độ cao High-speed WIM", "effective_date": "2026-07-01"},
                {"target_document": "165/2024/NĐ-CP", "target_provision": "Điều 48", "description": "Trách nhiệm công khai minh bạch số liệu thu phí và bồi thường sự cố của doanh nghiệp PPP", "effective_date": "2026-07-01"}
            ]
        },
        "Điều 2": {
            "repeals": [
                {"target_document": "165/2024/NĐ-CP", "target_provision": "Điều 21", "effective_date": "2026-07-01"},
                {"target_document": "165/2024/NĐ-CP", "target_provision": "Điều 30 Khoản 4", "effective_date": "2026-07-01"}
            ]
        }
    },
    "traffic_inspection_amendment_45_2026_tt_bxd": {
        "Điều 1": {
            "amends": [
                {"target_document": "30/2026/TT-BXD", "target_provision": "Điều 4 Khoản 2", "description": "Chu kỳ kiểm định xe cơ giới chuyên dùng 24 tháng lần đầu, 12 tháng định kỳ", "effective_date": "2026-07-01"},
                {"target_document": "30/2026/TT-BXD", "target_provision": "Điều 7 Khoản 3", "description": "Kiểm chuẩn thiết bị đo phanh và khí thải tự động chống can thiệp", "effective_date": "2026-07-01"},
                {"target_document": "30/2026/TT-BXD", "target_provision": "Điều 9 Khoản 1", "description": "Tích hợp Giấy chứng nhận điện tử và mã QR lên VNeID trong 2 giờ", "effective_date": "2026-07-01"},
                {"target_document": "30/2026/TT-BXD", "target_provision": "Điều 11 Khoản 2", "description": "Các trường hợp lắp phụ kiện không coi là cải tạo phương tiện", "effective_date": "2026-07-01"},
                {"target_document": "30/2026/TT-BXD", "target_provision": "Điều 15 Khoản 1", "description": "Camera AI giám sát dây chuyền kiểm định lưu trữ 36 tháng", "effective_date": "2026-07-01"}
            ]
        },
        "Điều 2": {
            "repeals": [
                {"target_document": "30/2026/TT-BXD", "target_provision": "Điều 9 Khoản 4", "effective_date": "2026-07-01"}
            ]
        }
    },
    "traffic_road_signs_qcvn41_51_2024_tt_bgtvt": {
        "Điều 2": {
            "replaces": [
                {"target_document": "54/2019/TT-BGTVT", "scope": "ALL", "effective_date": "2025-01-01"}
            ]
        }
    }
}

def parse_html_document(doc_meta):
    file_path = RAW_DIR / doc_meta["filename"]
    raw_bytes = file_path.read_bytes()
    computed_hash = hashlib.sha256(raw_bytes).hexdigest()

    if computed_hash != doc_meta["sha256"]:
        raise ValueError(f"Hash mismatch for {doc_meta['filename']}: expected {doc_meta['sha256']}, got {computed_hash}")

    html_content = raw_bytes.decode("utf-8")
    soup = BeautifulSoup(html_content, "html.parser")
    doc_body = soup.find("div", class_="doc-body")
    if not doc_body:
        raise ValueError(f"No doc-body found in {doc_meta['filename']}")

    current_chapter = "QUY ĐỊNH CHUNG"
    current_section = None

    articles = []
    current_article = None

    for el in doc_body.find_all(["h3", "h4", "p"]):
        text = el.get_text(strip=True)
        if not text:
            continue

        if el.name in ["h3", "h4"] and ("CHƯƠNG" in text.upper() or "PHẦN" in text.upper()):
            current_chapter = text
            current_section = None
            continue

        if el.name in ["h3", "h4"] and "MỤC" in text.upper():
            current_section = text
            continue

        art_match = re.match(r"^Điều\s+(\d+)\.\s*(.*)", text)
        if art_match:
            if current_article:
                articles.append(current_article)
            art_num = f"Điều {art_match.group(1)}"
            art_idx = int(art_match.group(1))
            art_title = art_match.group(2).strip()

            current_article = {
                "unit_type": "STATUTE_ARTICLE",
                "article_number": art_num,
                "article_index": art_idx,
                "article_title": art_title,
                "chapter": current_chapter,
                "section": current_section,
                "raw_text_paragraphs": [],
                "clauses": []
            }
            continue

        if current_article:
            current_article["raw_text_paragraphs"].append(text)

    if current_article:
        articles.append(current_article)

    # Clause and point extraction for statute articles
    for art in articles:
        clauses = []
        current_clause = None
        lead_in_text = ""

        has_numbered_clauses = any(re.match(r"^\d+\.\s+", p) for p in art["raw_text_paragraphs"])

        for p in art["raw_text_paragraphs"]:
            clause_match = re.match(r"^(\d+)\.\s+(.*)", p)
            point_match = re.match(r"^([a-zđ])\)\s+(.*)", p)

            if clause_match:
                if current_clause:
                    clauses.append(current_clause)
                c_num = f"Khoản {clause_match.group(1)}"
                c_idx = int(clause_match.group(1))
                c_text = clause_match.group(2).strip()
                if lead_in_text and c_idx == 1:
                    c_text = f"{lead_in_text} {c_text}"
                current_clause = {
                    "clause_number": c_num,
                    "clause_index": c_idx,
                    "clause_text": c_text,
                    "points": []
                }
            elif point_match:
                p_num = f"Điểm {point_match.group(1)}"
                p_char = point_match.group(1)
                p_text = point_match.group(2).strip()
                if not current_clause:
                    current_clause = {
                        "clause_number": "Khoản 1",
                        "clause_index": 1,
                        "clause_text": lead_in_text if lead_in_text else "",
                        "points": []
                    }
                current_clause["points"].append({
                    "point_letter": p_num,
                    "point_char": p_char,
                    "point_text": p_text
                })
            else:
                if has_numbered_clauses and not current_clause:
                    if lead_in_text:
                        lead_in_text += f" {p}"
                    else:
                        lead_in_text = p
                elif current_clause:
                    current_clause["clause_text"] += f"\n{p}"
                else:
                    current_clause = {
                        "clause_number": "Khoản 1",
                        "clause_index": 1,
                        "clause_text": p,
                        "points": []
                    }

        if current_clause:
            clauses.append(current_clause)

        if not clauses and art["raw_text_paragraphs"]:
            clauses.append({
                "clause_number": "Khoản 1",
                "clause_index": 1,
                "clause_text": "\n".join(art["raw_text_paragraphs"]),
                "points": []
            })

        art["clauses"] = clauses

    # Check for attached regulation (e.g. QCVN 41:2024/BGTVT)
    attached_reg_el = soup.find("div", class_="attached-regulation")
    attached_regulation = None
    if attached_reg_el:
        attached_title_el = attached_reg_el.find("h2")
        attached_title = attached_title_el.get_text(strip=True) if attached_title_el else "QUY CHUẨN KỸ THUẬT QUỐC GIA"
        
        qcvn_units = []
        current_qcvn_part = "QUY ĐỊNH CHUNG"

        for child in attached_reg_el.children:
            if child.name == "h3":
                current_qcvn_part = child.get_text(strip=True)
            elif child.name == "div" and "technical-unit" in child.get("class", []):
                sec_paragraphs = [p.get_text(strip=True) for p in child.find_all("p") if p.get_text(strip=True)]
                if not sec_paragraphs:
                    continue

                header_p = sec_paragraphs[0]
                m = re.match(r"^Mục\s+(\d+)\.\s*(.*)", header_p)
                if m:
                    sec_num = f"Mục {m.group(1)}"
                    sec_idx = int(m.group(1))
                    sec_title = m.group(2).strip()
                    body_paras = sec_paragraphs[1:]
                else:
                    sec_num = f"Mục {len(qcvn_units) + 1}"
                    sec_idx = len(qcvn_units) + 1
                    sec_title = header_p
                    body_paras = sec_paragraphs[1:]

                qcvn_units.append({
                    "unit_type": "TECHNICAL_REGULATION_UNIT",
                    "attached_regulation_code": "QCVN 41:2024/BGTVT",
                    "part": current_qcvn_part,
                    "section_number": sec_num,
                    "section_index": sec_idx,
                    "section_title": sec_title,
                    "paragraphs": body_paras
                })

        attached_regulation = {
            "regulation_code": "QCVN 41:2024/BGTVT",
            "regulation_title": attached_title,
            "total_technical_units": len(qcvn_units),
            "units": qcvn_units
        }

    return {
        "document_id": doc_meta["source_document_id"],
        "official_number": doc_meta["official_number"],
        "title": doc_meta["title"],
        "authority": doc_meta["source_authority"],
        "issue_date": doc_meta["issue_date"],
        "effective_date": doc_meta["effective_date"],
        "legal_status": doc_meta["legal_status"],
        "ingestion_status": doc_meta["ingestion_status"],
        "document_role": doc_meta["document_role"],
        "source_status": doc_meta["source_status"],
        "source_status_authority": doc_meta["source_status_authority"],
        "normalized_status": doc_meta["normalized_status"],
        "source_url": doc_meta["source_url"],
        "sha256": doc_meta["sha256"],
        "articles": articles,
        "attached_regulation": attached_regulation
    }

def generate_semantic_chunks(parsed_doc, doc_meta):
    chunks = []
    doc_id = parsed_doc["document_id"]
    doc_num = parsed_doc["official_number"]
    doc_relations = RELATIONS_REGISTRY.get(doc_id, {})

    retrieval_eligible = True
    primary_core = True

    # 1. Chunks for Statute Articles (ĐIỀU KHOẢN LUẬT / NGHỊ ĐỊNH / THÔNG TƯ)
    for art in parsed_doc["articles"]:
        art_num = art["article_number"]
        art_idx = art["article_index"]
        art_title = art["article_title"]
        chapter = art["chapter"]
        section = art["section"]

        art_relations = doc_relations.get(art_num, {})
        a_tag = f"d{art_idx}"

        for cl in art["clauses"]:
            clause_num = cl["clause_number"]
            clause_idx = cl["clause_index"]
            clause_text = cl["clause_text"]
            points = cl["points"]

            c_tag = f"k{clause_idx}"
            header_prefix = f"[{doc_num} - {chapter} - {art_num}: {art_title} - {clause_num}]"

            if not points:
                full_text = f"{header_prefix}\n{clause_text}".strip()
                words = len(full_text.split())
                chunk_id = f"traffic_p1_2_{doc_id}_{a_tag}_{c_tag}"
                chunk = {
                    "chunk_id": chunk_id,
                    "unit_type": "STATUTE_ARTICLE",
                    "document_id": doc_id,
                    "official_number": doc_meta["official_number"],
                    "title": doc_meta["title"],
                    "issuing_authority": doc_meta["source_authority"],
                    "chapter": chapter,
                    "section": section,
                    "article": art_num,
                    "article_title": art_title,
                    "clause": clause_num,
                    "point": None,
                    "annex_table_identifier": None,
                    "source_url": doc_meta["source_url"],
                    "source_hash": doc_meta["sha256"],
                    "effective_from": doc_meta["effective_date"],
                    "effective_until": None,
                    "legal_status": doc_meta["legal_status"],
                    "ingestion_status": doc_meta["ingestion_status"],
                    "source_status": doc_meta["source_status"],
                    "normalized_status": doc_meta["normalized_status"],
                    "current_retrieval_eligible": retrieval_eligible,
                    "primary_current_core": primary_core,
                    "document_role": doc_meta["document_role"],
                    "relations": art_relations,
                    "text": full_text,
                    "word_count": words
                }
                chunks.append(chunk)
            else:
                all_points_text = "\n".join([f"{pt['point_letter']}) {pt['point_text']}" for pt in points])
                full_clause_text = f"{header_prefix}\n{clause_text}\n{all_points_text}".strip()
                words_full = len(full_clause_text.split())

                if words_full <= 140:
                    chunk_id = f"traffic_p1_2_{doc_id}_{a_tag}_{c_tag}"
                    chunk = {
                        "chunk_id": chunk_id,
                        "unit_type": "STATUTE_ARTICLE",
                        "document_id": doc_id,
                        "official_number": doc_meta["official_number"],
                        "title": doc_meta["title"],
                        "issuing_authority": doc_meta["source_authority"],
                        "chapter": chapter,
                        "section": section,
                        "article": art_num,
                        "article_title": art_title,
                        "clause": clause_num,
                        "point": "ALL_POINTS",
                        "annex_table_identifier": None,
                        "source_url": doc_meta["source_url"],
                        "source_hash": doc_meta["sha256"],
                        "effective_from": doc_meta["effective_date"],
                        "effective_until": None,
                        "legal_status": doc_meta["legal_status"],
                        "ingestion_status": doc_meta["ingestion_status"],
                        "source_status": doc_meta["source_status"],
                        "normalized_status": doc_meta["normalized_status"],
                        "current_retrieval_eligible": retrieval_eligible,
                        "primary_current_core": primary_core,
                        "document_role": doc_meta["document_role"],
                        "relations": art_relations,
                        "text": full_clause_text,
                        "word_count": words_full
                    }
                    chunks.append(chunk)
                else:
                    for pt in points:
                        pt_letter = pt["point_letter"]
                        pt_text = pt["point_text"]
                        pt_char = pt["point_char"]

                        pt_full_text = f"{header_prefix} {clause_text}\n{pt_letter}) {pt_text}".strip()
                        pt_words = len(pt_full_text.split())
                        chunk_id = f"traffic_p1_2_{doc_id}_{a_tag}_{c_tag}_{pt_char}"

                        chunk = {
                            "chunk_id": chunk_id,
                            "unit_type": "STATUTE_ARTICLE",
                            "document_id": doc_id,
                            "official_number": doc_meta["official_number"],
                            "title": doc_meta["title"],
                            "issuing_authority": doc_meta["source_authority"],
                            "chapter": chapter,
                            "section": section,
                            "article": art_num,
                            "article_title": art_title,
                            "clause": clause_num,
                            "point": pt_letter,
                            "annex_table_identifier": None,
                            "source_url": doc_meta["source_url"],
                            "source_hash": doc_meta["sha256"],
                            "effective_from": doc_meta["effective_date"],
                            "effective_until": None,
                            "legal_status": doc_meta["legal_status"],
                            "ingestion_status": doc_meta["ingestion_status"],
                            "source_status": doc_meta["source_status"],
                            "normalized_status": doc_meta["normalized_status"],
                            "current_retrieval_eligible": retrieval_eligible,
                            "primary_current_core": primary_core,
                            "document_role": doc_meta["document_role"],
                            "relations": art_relations,
                            "text": pt_full_text,
                            "word_count": pt_words
                        }
                        chunks.append(chunk)

    # 2. Chunks for Attached Technical Regulation (QUY CHUẨN KỸ THUẬT QCVN 41:2024/BGTVT)
    if parsed_doc.get("attached_regulation"):
        reg = parsed_doc["attached_regulation"]
        reg_code = reg["regulation_code"]

        for unit in reg["units"]:
            sec_num = unit["section_number"]
            sec_idx = unit["section_index"]
            sec_title = unit["section_title"]
            part = unit["part"]
            paras = unit["paragraphs"]

            header_prefix = f"[{doc_num} - {reg_code} - {part} - {sec_num}: {sec_title}]"
            body_text = "\n".join(paras)
            full_text = f"{header_prefix}\n{body_text}".strip()
            words = len(full_text.split())

            chunk_id = f"traffic_p1_2_{doc_id}_qcvn41_m{sec_idx}"
            chunk = {
                "chunk_id": chunk_id,
                "unit_type": "TECHNICAL_REGULATION_UNIT",
                "document_id": doc_id,
                "official_number": doc_meta["official_number"],
                "attached_regulation": reg_code,
                "title": f"{doc_meta['title']} ({reg_code})",
                "issuing_authority": doc_meta["source_authority"],
                "chapter": part,
                "section": sec_num,
                "article": f"{reg_code} {sec_num}",
                "article_title": sec_title,
                "clause": None,
                "point": None,
                "annex_table_identifier": None,
                "source_url": doc_meta["source_url"],
                "source_hash": doc_meta["sha256"],
                "effective_from": doc_meta["effective_date"],
                "effective_until": None,
                "legal_status": doc_meta["legal_status"],
                "ingestion_status": doc_meta["ingestion_status"],
                "source_status": doc_meta["source_status"],
                "normalized_status": doc_meta["normalized_status"],
                "current_retrieval_eligible": retrieval_eligible,
                "primary_current_core": primary_core,
                "document_role": "TECHNICAL_REGULATION",
                "relations": {},
                "text": full_text,
                "word_count": words
            }
            chunks.append(chunk)

    return chunks

def main():
    print("=" * 80)
    print("   TRAFFIC P1.2: REVISED PARSER (53 LEGAL ARTICLES + 21 QCVN UNITS)")
    print("=" * 80)

    all_chunks = []
    summary = []

    for doc_meta in manifest["documents"]:
        filename = doc_meta["filename"]
        print(f"[*] Parsing {filename}...")
        parsed_doc = parse_html_document(doc_meta)

        out_json_path = PARSED_DIR / f"{parsed_doc['document_id']}.json"
        with open(out_json_path, "w", encoding="utf-8") as f:
            json.dump(parsed_doc, f, ensure_ascii=False, indent=2)

        chunks = generate_semantic_chunks(parsed_doc, doc_meta)
        all_chunks.extend(chunks)

        total_clauses = sum(len(a["clauses"]) for a in parsed_doc["articles"])
        total_points = sum(sum(len(c["points"]) for c in a["clauses"]) for a in parsed_doc["articles"])
        qcvn_units_count = parsed_doc["attached_regulation"]["total_technical_units"] if parsed_doc.get("attached_regulation") else 0

        doc_summary = {
            "document_id": parsed_doc["document_id"],
            "official_number": parsed_doc["official_number"],
            "articles_count": len(parsed_doc["articles"]),
            "clauses_count": total_clauses,
            "points_count": total_points,
            "qcvn_technical_units": qcvn_units_count,
            "chunks_count": len(chunks)
        }
        summary.append(doc_summary)
        print(f"    -> Parsed {len(parsed_doc['articles'])} Legal Articles, {total_clauses} Clauses, {qcvn_units_count} QCVN Units")
        print(f"    -> Generated {len(chunks)} Semantic Chunks")

    all_chunks_path = PARSED_DIR / "all_traffic_p1_2_chunks.json"
    with open(all_chunks_path, "w", encoding="utf-8") as f:
        json.dump(all_chunks, f, ensure_ascii=False, indent=2)

    total_legal_articles = sum(s["articles_count"] for s in summary)
    total_qcvn_units = sum(s["qcvn_technical_units"] for s in summary)

    summary_path = PARSED_DIR / "parsing_summary.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump({
            "batch_name": manifest["batch_name"],
            "total_documents": len(summary),
            "total_legal_articles": total_legal_articles,
            "total_qcvn_technical_units": total_qcvn_units,
            "total_clauses": sum(s["clauses_count"] for s in summary),
            "total_points": sum(s["points_count"] for s in summary),
            "total_chunks": len(all_chunks),
            "details": summary
        }, f, ensure_ascii=False, indent=2)

    print("=" * 80)
    print(f"[*] Parsing complete!")
    print(f"    Total Documents:             {len(summary)}")
    print(f"    Total Legal Articles:        {total_legal_articles} (Expected: 53 = 43 + 4 + 4 + 2)")
    print(f"    Total QCVN Technical Units:  {total_qcvn_units} (Expected: 21)")
    print(f"    Total Clauses:               {sum(s['clauses_count'] for s in summary)}")
    print(f"    Total Points:                {sum(s['points_count'] for s in summary)}")
    print(f"    Total Chunks:                {len(all_chunks)}")
    print(f"    All chunks saved to:         {all_chunks_path}")
    print("=" * 80)

if __name__ == "__main__":
    main()
