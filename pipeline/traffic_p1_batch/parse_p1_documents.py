import sys
import os
import re
import json
import hashlib
from pathlib import Path
from bs4 import BeautifulSoup

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

RAW_DIR = Path("data/01_raw/traffic_p1_batch")
PARSED_DIR = Path("data/03_parsed/traffic_p1_batch")
PARSED_DIR.mkdir(parents=True, exist_ok=True)

MANIFEST_FILE = RAW_DIR / "manifest.json"

with open(MANIFEST_FILE, "r", encoding="utf-8") as f:
    manifest = json.load(f)

# Specific Legal Relations Registry at Provision Level
RELATIONS_REGISTRY = {
    "traffic_police_patrol_73_2024_tt_bca": {
        "Điều 32": {
            "replaces": [{"target_document": "32/2023/TT-BCA", "scope": "ALL", "effective_date": "2025-01-01"}],
            "repeals": [{"target_document": "28/2024/TT-BCA", "target_provision": "Điều 1", "effective_date": "2025-01-01"}]
        }
    },
    "traffic_inspection_procedures_30_2026_tt_bxd": {
        "Điều 32": {
            "replaces": [{"target_document": "47/2024/TT-BGTVT", "scope": "ALL", "effective_date": "2026-07-01"}]
        }
    },
    "traffic_weight_amendment_19_2026_tt_bxd": {
        "Điều 1": {
            "amends": [
                {
                    "target_document": "12/2025/TT-BXD",
                    "target_provision": "Điều 5 Khoản 2",
                    "description": "Nâng tải trọng cụm trục kép sử dụng hệ thống treo khí nén lên 19,0 tấn",
                    "effective_date": "2026-07-01"
                },
                {
                    "target_document": "12/2025/TT-BXD",
                    "target_provision": "Điều 7 Khoản 3",
                    "description": "Nâng tổng trọng lượng tổ hợp xe đầu kéo 5 trục dùng bóng hơi trên cao tốc lên 45,0 tấn",
                    "effective_date": "2026-07-01"
                },
                {
                    "target_document": "12/2025/TT-BXD",
                    "target_provision": "Điều 16",
                    "description": "Rút ngắn thời gian cấp Giấy phép lưu hành trực tuyến xuống 24 giờ",
                    "effective_date": "2026-07-01"
                }
            ]
        }
    },
    "traffic_police_amendment_28_2024_tt_bca": {
        "Điều 1": {
            "repealed_by": [{"target_document": "73/2024/TT-BCA", "target_provision": "Điều 32", "effective_date": "2025-01-01"}]
        },
        "Điều 2": {
            "repealed_by": [{"target_document": "79/2024/TT-BCA", "target_provision": "Điều 39", "effective_date": "2025-01-01"}]
        }
    }
}

def parse_html_document(doc_meta):
    file_path = RAW_DIR / doc_meta["filename"]
    raw_bytes = file_path.read_bytes()
    computed_hash = hashlib.sha256(raw_bytes).hexdigest()
    
    # Hash verification
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
        
    for art in articles:
        clauses = []
        current_clause = None
        lead_in_text = ""
        
        # Check if paragraphs contain numbered clauses "1. ", "2. "
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
                    # Lead-in paragraph before Clause 1 (e.g. "Cảnh sát giao thông được dừng xe trong 4 trường hợp sau đây:")
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
            
        if not clauses:
            clauses.append({
                "clause_number": "Khoản 1",
                "clause_index": 1,
                "clause_text": art["article_title"],
                "points": []
            })
            
        art["clauses"] = clauses
        del art["raw_text_paragraphs"]
        
    return articles

def create_semantic_chunks(doc_meta, articles):
    chunks = []
    doc_id = doc_meta["source_document_id"]
    doc_relations = RELATIONS_REGISTRY.get(doc_id, {})
    
    for art in articles:
        art_num = art["article_number"]
        art_title = art["article_title"]
        chapter = art["chapter"]
        section = art["section"]
        
        art_relations = doc_relations.get(art_num, {})
        
        for clause in art["clauses"]:
            clause_num = clause["clause_number"]
            clause_text = clause["clause_text"]
            points = clause.get("points", [])
            
            header_prefix = f"[{doc_meta['official_number']} - {chapter} - {art_num}: {art_title} - {clause_num}]"
            
            retrieval_eligible = doc_meta["legal_status"] == "CURRENT"
            primary_core = doc_meta["ingestion_status"] == "CORE" and doc_meta["legal_status"] == "CURRENT"
            
            if doc_id == "traffic_police_amendment_28_2024_tt_bca":
                if art_num in ["Điều 1", "Điều 2"]:
                    retrieval_eligible = False
                    primary_core = False
                else:
                    retrieval_eligible = True
                    primary_core = False
            
            # Formulate unique clause tag for chunk_id
            c_tag = clause_num.replace(' ', '_').lower()
            a_tag = art_num.replace(' ', '_').lower()
            
            if not points:
                full_text = f"{header_prefix}\n{clause_text}".strip()
                words = len(full_text.split())
                chunk_id = f"traffic_p1_{doc_id}_{a_tag}_{c_tag}"
                
                chunk = {
                    "chunk_id": chunk_id,
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
                    "effective_until": None if doc_meta["legal_status"] == "CURRENT" else "2025-01-01",
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
                
                if words_full <= 120:
                    chunk_id = f"traffic_p1_{doc_id}_{a_tag}_{c_tag}"
                    chunk = {
                        "chunk_id": chunk_id,
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
                        "effective_until": None if doc_meta["legal_status"] == "CURRENT" else "2025-01-01",
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
                        chunk_id = f"traffic_p1_{doc_id}_{a_tag}_{c_tag}_{pt_char}"
                        
                        chunk = {
                            "chunk_id": chunk_id,
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
                            "effective_until": None if doc_meta["legal_status"] == "CURRENT" else "2025-01-01",
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
                        
    return chunks

def main():
    print("=" * 70)
    print("   TRAFFIC P1 BATCH: FULL-DOCUMENT CLAUSE PARSER & CHUNKER")
    print("=" * 70)
    
    total_stats = {
        "documents_processed": 0,
        "total_chapters": 0,
        "total_articles": 0,
        "core_articles": 0,
        "total_clauses": 0,
        "total_points": 0,
        "total_chunks": 0,
        "amendment_provisions": 0,
        "document_breakdown": []
    }
    
    all_chunks = []
    seen_chunk_ids = set()
    
    for doc in manifest["documents"]:
        doc_id = doc["source_document_id"]
        filename = doc["filename"]
        print(f"\n[*] Parsing {doc['official_number']} ({filename})...")
        
        articles = parse_html_document(doc)
        chunks = create_semantic_chunks(doc, articles)
        
        chapters = set(a["chapter"] for a in articles)
        clause_count = sum(len(a["clauses"]) for a in articles)
        point_count = sum(sum(len(c.get("points", [])) for c in a["clauses"]) for a in articles)
        
        for chk in chunks:
            cid = chk["chunk_id"]
            if cid in seen_chunk_ids:
                raise ValueError(f"CRITICAL: Duplicate chunk_id detected: {cid}")
            seen_chunk_ids.add(cid)
            all_chunks.append(chk)
            
        doc_amendments = len([chk for chk in chunks if chk.get("relations") and len(chk["relations"]) > 0])
        
        doc_stat = {
            "source_document_id": doc_id,
            "official_number": doc["official_number"],
            "legal_status": doc["legal_status"],
            "ingestion_status": doc["ingestion_status"],
            "document_role": doc["document_role"],
            "chapters_count": len(chapters),
            "articles_count": len(articles),
            "clauses_count": clause_count,
            "points_count": point_count,
            "chunks_count": len(chunks),
            "amendment_provisions_count": doc_amendments
        }
        total_stats["document_breakdown"].append(doc_stat)
        total_stats["documents_processed"] += 1
        total_stats["total_chapters"] += len(chapters)
        total_stats["total_articles"] += len(articles)
        if doc["ingestion_status"] == "CORE" and doc["legal_status"] == "CURRENT":
            total_stats["core_articles"] += len(articles)
        total_stats["total_clauses"] += clause_count
        total_stats["total_points"] += point_count
        total_stats["total_chunks"] += len(chunks)
        total_stats["amendment_provisions"] += doc_amendments
        
        doc_parsed_output = {
            "metadata": doc,
            "statistics": doc_stat,
            "hierarchy": {
                "chapters": list(chapters),
                "articles": articles
            },
            "chunks": chunks
        }
        doc_out_path = PARSED_DIR / f"{doc_id}.json"
        doc_out_path.write_text(json.dumps(doc_parsed_output, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f" [+] Saved parsed doc: {doc_out_path.name} ({len(chunks)} chunks, {len(articles)} articles)")

    all_chunks_path = PARSED_DIR / "all_traffic_p1_chunks.json"
    all_chunks_path.write_text(json.dumps(all_chunks, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n[+] Saved all {len(all_chunks)} chunks to {all_chunks_path.name}")
    
    summary_path = PARSED_DIR / "parsing_summary.json"
    summary_path.write_text(json.dumps(total_stats, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[+] Saved parsing summary to {summary_path.name}")
    
    print("\n" + "=" * 70)
    print("   PARSING SUMMARY STATISTICS")
    print("=" * 70)
    print(f"Total Documents Processed:      {total_stats['documents_processed']}")
    print(f"Total Chapters:                 {total_stats['total_chapters']}")
    print(f"Total Articles:                 {total_stats['total_articles']}")
    print(f"Current Core Articles:          {total_stats['core_articles']} (Expected: 137)")
    print(f"Total Clauses:                  {total_stats['total_clauses']}")
    print(f"Total Points:                   {total_stats['total_points']}")
    print(f"Total Semantic Chunks:          {total_stats['total_chunks']}")
    print(f"Amendment/Repeal Provisions:    {total_stats['amendment_provisions']}")
    print("=" * 70)

if __name__ == "__main__":
    main()
