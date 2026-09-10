import sys
import json
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
RAW_DIR = PROJECT_ROOT / "data" / "01_raw" / "traffic_p1_2_batch"
PARSED_DIR = PROJECT_ROOT / "data" / "03_parsed" / "traffic_p1_2_batch"

MANIFEST_FILE = RAW_DIR / "manifest.json"
CHUNKS_FILE = PARSED_DIR / "all_traffic_p1_2_chunks.json"
SUMMARY_FILE = PARSED_DIR / "parsing_summary.json"

def validate():
    print("=" * 80)
    print("   TRAFFIC P1.2: VALIDATION OF PARSED DATA & CHUNKS")
    print("=" * 80)

    with open(MANIFEST_FILE, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    with open(CHUNKS_FILE, "r", encoding="utf-8") as f:
        chunks = json.load(f)

    with open(SUMMARY_FILE, "r", encoding="utf-8") as f:
        summary = json.load(f)

    errors = []
    warnings = []

    # 1. Document Count & Article Count Alignment
    manifest_docs = {d["source_document_id"]: d for d in manifest["documents"]}
    summary_docs = {d["document_id"]: d for d in summary["details"]}

    if set(manifest_docs.keys()) != set(summary_docs.keys()):
        errors.append(f"Mismatch in document IDs between manifest and summary: {set(manifest_docs.keys()) ^ set(summary_docs.keys())}")

    for doc_id, m_doc in manifest_docs.items():
        s_doc = summary_docs.get(doc_id)
        if not s_doc:
            continue
        exp_art = m_doc["source_articles_count"]
        act_art = s_doc["articles_count"]
        if exp_art != act_art:
            errors.append(f"Article count mismatch for {doc_id}: expected {exp_art}, got {act_art}")
        else:
            print(f"[OK] {m_doc['filename']}: {act_art}/{exp_art} articles verified.")

    # 2. Chunk Schema & Content Integrity
    required_fields = [
        "chunk_id", "document_id", "official_number", "title",
        "issuing_authority", "chapter", "article", "article_title",
        "clause", "effective_from", "legal_status", "ingestion_status",
        "source_status", "normalized_status", "current_retrieval_eligible",
        "primary_current_core", "document_role", "relations", "text", "word_count"
    ]

    chunk_ids = set()
    empty_chunks = 0
    short_chunks = 0

    for i, c in enumerate(chunks):
        # Check required fields
        missing = [rf for rf in required_fields if rf not in c]
        if missing:
            errors.append(f"Chunk index {i} ({c.get('chunk_id')}) missing fields: {missing}")

        cid = c.get("chunk_id")
        if cid in chunk_ids:
            errors.append(f"Duplicate chunk_id: {cid}")
        chunk_ids.add(cid)

        text = c.get("text", "").strip()
        if not text:
            empty_chunks += 1
            errors.append(f"Empty text in chunk: {cid}")
        elif len(text.split()) < 5:
            short_chunks += 1
            warnings.append(f"Very short chunk text (< 5 words): {cid}")

        if c.get("effective_from") is None:
            errors.append(f"Missing effective_from in chunk: {cid}")

    # 3. Relations Validation
    relations_count = 0
    for c in chunks:
        rels = c.get("relations", {})
        if rels:
            relations_count += 1

    # Check legal articles & QCVN technical units
    expected_legal_articles = 53
    expected_qcvn_units = 21
    expected_chunks = 163

    act_legal_articles = summary.get("total_legal_articles", 0)
    act_qcvn_units = summary.get("total_qcvn_technical_units", 0)

    if act_legal_articles != expected_legal_articles:
        errors.append(f"Total legal articles mismatch: expected {expected_legal_articles}, got {act_legal_articles}")
    if act_qcvn_units != expected_qcvn_units:
        errors.append(f"Total QCVN technical units mismatch: expected {expected_qcvn_units}, got {act_qcvn_units}")
    if len(chunks) != expected_chunks:
        errors.append(f"Total chunks mismatch: expected {expected_chunks}, got {len(chunks)}")

    validation_result = {
        "status": "PASS" if not errors else "FAIL",
        "total_documents": len(manifest_docs),
        "total_legal_articles": act_legal_articles,
        "total_qcvn_technical_units": act_qcvn_units,
        "total_clauses": summary.get("total_clauses", 0),
        "total_points": summary.get("total_points", 0),
        "total_chunks": len(chunks),
        "chunks_with_relations": relations_count,
        "errors": errors,
        "warnings": warnings
    }

    result_path = PARSED_DIR / "validation_results.json"
    with open(result_path, "w", encoding="utf-8") as f:
        json.dump(validation_result, f, ensure_ascii=False, indent=2)

    print("-" * 80)
    print(f"Validation Result: {validation_result['status']}")
    print(f"Total Legal Articles: {act_legal_articles}/{expected_legal_articles}")
    print(f"Total QCVN Technical Units: {act_qcvn_units}/{expected_qcvn_units}")
    print(f"Total Chunks Checked: {len(chunks)}/{expected_chunks}")
    print(f"Chunks with Explicit Legal Relations: {relations_count}")
    print(f"Errors: {len(errors)}")
    print(f"Warnings: {len(warnings)}")
    print(f"Results saved to: {result_path}")
    print("=" * 80)

    if errors:
        sys.exit(1)

if __name__ == "__main__":
    validate()
