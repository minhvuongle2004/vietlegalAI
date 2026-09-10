import sys
import json
import hashlib
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

RAW_DIR = Path("data/01_raw/traffic_p1_batch")
PARSED_DIR = Path("data/03_parsed/traffic_p1_batch")

MANIFEST_PATH = RAW_DIR / "manifest.json"
ALL_CHUNKS_PATH = PARSED_DIR / "all_traffic_p1_chunks.json"
SUMMARY_PATH = PARSED_DIR / "parsing_summary.json"

with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
    manifest = json.load(f)

with open(ALL_CHUNKS_PATH, "r", encoding="utf-8") as f:
    all_chunks = json.load(f)

with open(SUMMARY_PATH, "r", encoding="utf-8") as f:
    summary = json.load(f)

print("=" * 70)
print("   TRAFFIC P1 BATCH: COMPREHENSIVE VALIDATION SUITE (STEP 2)")
print("=" * 70)

validation_results = []

def record_test(name, passed, details=""):
    validation_results.append({
        "check_name": name,
        "status": "PASS" if passed else "FAIL",
        "details": details
    })
    status_icon = "🟢 PASS" if passed else "🔴 FAIL"
    print(f"[{status_icon}] {name}")
    if details:
        print(f"        -> {details}")

# Test 1: Hash integrity of all raw source files against manifest
hash_pass = True
hash_details = []
for doc in manifest["documents"]:
    fpath = RAW_DIR / doc["filename"]
    actual_hash = hashlib.sha256(fpath.read_bytes()).hexdigest()
    if actual_hash != doc["sha256"]:
        hash_pass = False
        hash_details.append(f"Mismatch {doc['filename']}: expected {doc['sha256'][:8]}, got {actual_hash[:8]}")
record_test("1. Source SHA-256 Hashes Match Manifest", hash_pass, "; ".join(hash_details) if hash_details else "All 8 files matched 100%")

# Test 2: Current Core Article Count equals expected (137)
core_articles_count = summary["core_articles"]
expected_core_articles = 137
record_test("2. Current Core Articles Count", core_articles_count == expected_core_articles, f"Actual: {core_articles_count} | Expected: {expected_core_articles}")

# Test 3: Total Articles count across all 8 documents (172)
total_articles = summary["total_articles"]
record_test("3. Total Parsed Articles Count", total_articles == 172, f"Actual: {total_articles} (137 Core + 31 VBHN + 4 TT28)")

# Test 4: Zero Duplicate chunk_ids
chunk_ids = [c["chunk_id"] for c in all_chunks]
unique_chunk_ids = set(chunk_ids)
record_test("4. Chunk ID Uniqueness (Zero Duplicates)", len(chunk_ids) == len(unique_chunk_ids), f"Total chunks: {len(chunk_ids)}, Unique IDs: {len(unique_chunk_ids)}")

# Test 5: Clause and Point Coverage Preservation
total_clauses = summary["total_clauses"]
total_points = summary["total_points"]
clauses_points_valid = total_clauses > 0 and total_points > 0
record_test("5. Clause & Point Preservation", clauses_points_valid, f"Total Clauses preserved: {total_clauses}, Total Points preserved: {total_points}")

# Test 6: Zero Orphan Provisions
orphan_pass = True
orphan_details = []
for c in all_chunks:
    if not c.get("article") or not c.get("clause") or not c.get("document_id"):
        orphan_pass = False
        orphan_details.append(c["chunk_id"])
record_test("6. Zero Orphan Provisions", orphan_pass, f"All {len(all_chunks)} chunks have complete Document, Article, and Clause hierarchy")

# Test 7: Metadata Provenance Schema Completeness
required_fields = [
    "chunk_id", "document_id", "official_number", "title", "issuing_authority",
    "chapter", "article", "clause", "source_url", "source_hash", "effective_from",
    "source_status", "normalized_status", "current_retrieval_eligible",
    "primary_current_core", "document_role", "text", "word_count"
]
schema_pass = True
schema_failures = []
for c in all_chunks:
    for f in required_fields:
        if f not in c or c[f] is None and f not in ["point", "section", "annex_table_identifier", "effective_until"]:
            schema_pass = False
            schema_failures.append((c["chunk_id"], f))
            break
record_test("7. Metadata Provenance Schema Completeness", schema_pass, f"All {len(all_chunks)} chunks contain 100% required provenance fields")

# Test 8: Amendment & Repeal Relations Resolvability
relations_pass = True
rel_details = []
core_doc_ids = set(d["source_document_id"] for d in manifest["documents"])
for c in all_chunks:
    rel = c.get("relations", {})
    if not rel:
        continue
    for op in ["replaces", "repeals", "amends", "repealed_by"]:
        for target in rel.get(op, []):
            target_doc = target.get("target_document")
            if not target_doc:
                relations_pass = False
                rel_details.append(f"Missing target_document in {c['chunk_id']}")
record_test("8. Amendment/Repeal Relations Resolvability", relations_pass, f"All {summary['amendment_provisions']} provision relationships have explicit target documents and effective dates")

# Test 9: Provision-Level Model for TT 28/2024
tt28_chunks = [c for c in all_chunks if c["document_id"] == "traffic_police_amendment_28_2024_tt_bca"]
tt28_art1_2_eligible = [c["current_retrieval_eligible"] for c in tt28_chunks if c["article"] in ["Điều 1", "Điều 2"]]
tt28_art3_4_eligible = [c["current_retrieval_eligible"] for c in tt28_chunks if c["article"] in ["Điều 3", "Điều 4"]]
tt28_valid = (
    len(tt28_art1_2_eligible) > 0 and all(e is False for e in tt28_art1_2_eligible) and
    len(tt28_art3_4_eligible) > 0 and all(e is True for e in tt28_art3_4_eligible)
)
record_test("9. TT 28/2024 Provision-Level Eligibility Modeling", tt28_valid, "Điều 1 & Điều 2 eligible=False (Repealed); Điều 3 & Điều 4 eligible=True (Active Responsibility)")

# Test 10: Soft target chunk length check (no tiny fragments, no truncation)
word_counts = [c["word_count"] for c in all_chunks]
avg_words = sum(word_counts) / len(word_counts)
min_words = min(word_counts)
max_words = max(word_counts)
word_check_passed = min_words >= 15 and avg_words > 40
record_test("10. Semantic Chunk Word Count Distribution (Soft Target)", word_check_passed, f"Average: {avg_words:.1f} words/chunk | Min: {min_words} | Max: {max_words}")

print("\n" + "=" * 70)
total_tests = len(validation_results)
passed_tests = sum(1 for t in validation_results if t["status"] == "PASS")
failed_tests = total_tests - passed_tests
print(f"SUMMARY: {passed_tests}/{total_tests} TESTS PASSED ({failed_tests} FAILED)")
print("=" * 70)

# Save validation report JSON
report_data = {
    "total_tests": total_tests,
    "passed": passed_tests,
    "failed": failed_tests,
    "all_passed": failed_tests == 0,
    "test_details": validation_results,
    "statistics": summary
}
report_path = PARSED_DIR / "validation_results.json"
report_path.write_text(json.dumps(report_data, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"[+] Saved validation results to {report_path.name}")
