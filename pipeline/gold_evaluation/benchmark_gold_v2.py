import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
import os
import re
import json
import time
from pathlib import Path
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
load_dotenv(PROJECT_ROOT / ".env")

from backend.app.services.rag.embeddings import get_embedding_service
from backend.app.services.rag.vector_store import QdrantVectorStore
from backend.app.services.rag.retriever import HybridRetriever

# Load revised v2 dataset
v2_path = PROJECT_ROOT / "data" / "gold_evaluation" / "gold_retrieval_225_cases_v2.json"
if not v2_path.exists():
    v2_path = PROJECT_ROOT / "gold_retrieval_225_cases_v2.json"

with open(v2_path, "r", encoding="utf-8") as f:
    dataset = json.load(f)

cases = dataset["cases"]
print(f"=== LOADED {len(cases)} CASES FROM GOLD V2 DATASET ===", flush=True)

# 17 False-Miss Cases identified in Tier 1.5
FALSE_MISS_17 = [
    "GOLD-DIR-04", "GOLD-DIR-05", "GOLD-DIR-06", "GOLD-DIR-13", "GOLD-DIR-14",
    "GOLD-DIR-15", "GOLD-DIR-20", "GOLD-ART-12", "GOLD-ART-24", "GOLD-EXC-04",
    "GOLD-EXC-09", "GOLD-MUL-03", "GOLD-MUL-07", "GOLD-MUL-24", "GOLD-AMD-20",
    "GOLD-HRD-02", "GOLD-HRD-13"
]

def normalize_art(art_val):
    if art_val is None:
        return None
    s = str(art_val).strip()
    s = re.sub(r"^[Đđ]iều\s*", "", s, flags=re.IGNORECASE).strip()
    return s

def matches_evidence(ev, hit):
    if not hit or not ev:
        return False
    
    h_doc = str(hit.get("doc_id") or hit.get("document_id") or "").lower()
    h_off = str(hit.get("official_number") or "").lower()
    h_title = str(hit.get("doc_title") or hit.get("article_title") or "").lower()
    h_header = str(hit.get("context_header") or "").lower()
    h_art = normalize_art(hit.get("article_number"))

    ev_doc = str(ev.get("document_id") or "").lower()
    ev_off = str(ev.get("official_number") or "").lower()
    ev_art = normalize_art(ev.get("article"))

    doc_matched = (
        (ev_doc and (ev_doc in h_doc or h_doc in ev_doc)) or
        (ev_off and (ev_off in h_off or ev_off in h_header or ev_off in h_title))
    )

    if not doc_matched:
        return False

    if ev_art is None:
        return True

    if ev_art == h_art:
        return True

    if f"điều {ev_art}" in h_header or f"điều {ev_art}." in h_title or f"điều {ev_art} " in h_title:
        return True

    return False

# Initialize Retriever with production vector store & embeddings
print("Initializing Production Qdrant & Embedding Service...", flush=True)
store = QdrantVectorStore(collection_name="vietlegal_articles")
embedder = get_embedding_service()
retriever = HybridRetriever(vector_store=store, embedding_service=embedder)

print("\n" + "=" * 90)
print("1. RUNNING DENSE-ONLY RETRIEVAL BENCHMARK ON 225 CASES (V2 GROUND TRUTH)")
print("=" * 90)

dense_results = []
dense_v1_hit1, dense_v1_hit3, dense_v1_hit5 = 0, 0, 0
dense_v2_hit1, dense_v2_hit3, dense_v2_hit5 = 0, 0, 0

dense_by_type = {
    "SINGLE": {"total": 0, "hit1": 0, "hit3": 0, "hit5": 0},
    "MULTI_VALID": {"total": 0, "hit1": 0, "hit3": 0, "hit5": 0, "primary_hit5": 0, "supporting_hit5": 0},
    "CO_REQUISITE": {"total": 0, "hit1": 0, "hit3": 0, "hit5": 0, "strict_hit3": 0, "strict_hit5": 0},
    "PRIMARY_PLUS_SUPPORTING": {"total": 0, "hit1": 0, "hit3": 0, "hit5": 0, "primary_hit5": 0, "supporting_hit5": 0}
}

dense_false_miss_impact = []

dense_start = time.time()
for idx, tc in enumerate(cases, 1):
    cid = tc["test_case_id"]
    cat = tc["category"]
    q = tc["query"]
    as_of = tc.get("as_of_date")
    ev_type = tc.get("evidence_type", "SINGLE")
    p_ev = tc["primary_evidence"]
    supp_evs = tc.get("acceptable_supporting_evidence", [])
    req_evs = tc.get("required_evidence_set", [])

    dense_hits = retriever._dense_search(q, limit=10, as_of_date=as_of)
    top5 = dense_hits[:5]

    # Evaluation V1: Primary-only
    p_rank = None
    for r, h in enumerate(top5, 1):
        if matches_evidence(p_ev, h):
            p_rank = r
            break

    if p_rank == 1:
        dense_v1_hit1 += 1
        dense_v1_hit3 += 1
        dense_v1_hit5 += 1
    elif p_rank in [2, 3]:
        dense_v1_hit3 += 1
        dense_v1_hit5 += 1
    elif p_rank in [4, 5]:
        dense_v1_hit5 += 1

    # Evaluation V2: According to evidence_type
    matched_evidences = []
    matched_roles = []
    v2_rank = None
    
    # Check primary
    if p_rank is not None:
        matched_evidences.append(p_ev)
        matched_roles.append(p_ev.get("evidence_role", "PRIMARY"))

    # Check supporting
    supp_ranks = []
    for s_idx, s in enumerate(supp_evs):
        s_rank = None
        for r, h in enumerate(top5, 1):
            if matches_evidence(s, h):
                s_rank = r
                break
        if s_rank is not None:
            supp_ranks.append((s_rank, s))
            matched_evidences.append(s)
            matched_roles.append(s.get("evidence_role", "SUPPORTING"))

    # Determine V2 Hit@1, Hit@3, Hit@5
    is_v2_hit1 = False
    is_v2_hit3 = False
    is_v2_hit5 = False

    dense_by_type[ev_type]["total"] += 1

    if ev_type == "SINGLE":
        is_v2_hit1 = (p_rank == 1)
        is_v2_hit3 = (p_rank is not None and p_rank <= 3)
        is_v2_hit5 = (p_rank is not None and p_rank <= 5)
        v2_rank = p_rank

    elif ev_type == "MULTI_VALID":
        # Any valid ground in top k
        all_valid_ranks = [p_rank] if p_rank is not None else []
        all_valid_ranks.extend([sr[0] for sr in supp_ranks])
        if all_valid_ranks:
            v2_rank = min(all_valid_ranks)
            is_v2_hit1 = (v2_rank == 1)
            is_v2_hit3 = (v2_rank <= 3)
            is_v2_hit5 = (v2_rank <= 5)
        if p_rank is not None and p_rank <= 5:
            dense_by_type["MULTI_VALID"]["primary_hit5"] += 1
        if supp_ranks and any(sr[0] <= 5 for sr in supp_ranks):
            dense_by_type["MULTI_VALID"]["supporting_hit5"] += 1

    elif ev_type == "CO_REQUISITE":
        # Check required set
        req_matched_count = 0
        req_ranks = []
        for req in req_evs:
            r_matched = None
            for r, h in enumerate(top5, 1):
                if matches_evidence(req, h):
                    r_matched = r
                    break
            if r_matched is not None:
                req_matched_count += 1
                req_ranks.append(r_matched)
        
        strict_hit3 = (req_matched_count == len(req_evs) and len(req_evs) > 0 and all(rk <= 3 for rk in req_ranks))
        strict_hit5 = (req_matched_count == len(req_evs) and len(req_evs) > 0 and all(rk <= 5 for rk in req_ranks))
        
        if strict_hit3:
            dense_by_type["CO_REQUISITE"]["strict_hit3"] += 1
        if strict_hit5:
            dense_by_type["CO_REQUISITE"]["strict_hit5"] += 1

        # V2 standard for co-requisite: primary is present or full set present
        v2_rank = p_rank
        is_v2_hit1 = (p_rank == 1)
        is_v2_hit3 = (p_rank is not None and p_rank <= 3) or strict_hit3
        is_v2_hit5 = (p_rank is not None and p_rank <= 5) or strict_hit5

    elif ev_type == "PRIMARY_PLUS_SUPPORTING":
        v2_rank = p_rank
        is_v2_hit1 = (p_rank == 1)
        is_v2_hit3 = (p_rank is not None and p_rank <= 3)
        is_v2_hit5 = (p_rank is not None and p_rank <= 5)
        
        if p_rank is not None and p_rank <= 5:
            dense_by_type["PRIMARY_PLUS_SUPPORTING"]["primary_hit5"] += 1
        if supp_ranks and any(sr[0] <= 5 for sr in supp_ranks):
            dense_by_type["PRIMARY_PLUS_SUPPORTING"]["supporting_hit5"] += 1

    if is_v2_hit1:
        dense_v2_hit1 += 1
        dense_by_type[ev_type]["hit1"] += 1
    if is_v2_hit3:
        dense_v2_hit3 += 1
        dense_by_type[ev_type]["hit3"] += 1
    if is_v2_hit5:
        dense_v2_hit5 += 1
        dense_by_type[ev_type]["hit5"] += 1

    # False miss analysis
    if cid in FALSE_MISS_17:
        dense_false_miss_impact.append({
            "test_case_id": cid,
            "query": q,
            "evidence_type": ev_type,
            "v1_primary_rank": p_rank,
            "v1_status": "PASS" if p_rank and p_rank <= 5 else "MISS",
            "v2_rank": v2_rank,
            "v2_status": "PASS" if is_v2_hit5 else "MISS",
            "matched_roles": matched_roles,
            "note": "Recovered by Multi-Valid/Supporting" if (not p_rank or p_rank > 5) and is_v2_hit5 else "Unchanged"
        })

    dense_results.append({
        "test_case_id": cid,
        "category": cat,
        "query": q,
        "evidence_type": ev_type,
        "v1_primary_rank": p_rank,
        "v2_rank": v2_rank,
        "v2_hit1": is_v2_hit1,
        "v2_hit3": is_v2_hit3,
        "v2_hit5": is_v2_hit5,
        "matched_roles": matched_roles,
        "top5_retrieved": [
            {
                "rank": r_i,
                "doc_id": h.get("doc_id"),
                "official_number": h.get("official_number"),
                "article": h.get("article_number"),
                "score": h.get("score")
            }
            for r_i, h in enumerate(top5, 1)
        ]
    })

dense_elapsed = time.time() - dense_start
print(f"Dense-only benchmark completed in {dense_elapsed:.1f}s")
print(f"Dense V1: Hit@1 = {dense_v1_hit1}/225 ({dense_v1_hit1/225*100:.1f}%), Hit@3 = {dense_v1_hit3}/225 ({dense_v1_hit3/225*100:.1f}%), Hit@5 = {dense_v1_hit5}/225 ({dense_v1_hit5/225*100:.1f}%)")
print(f"Dense V2: Hit@1 = {dense_v2_hit1}/225 ({dense_v2_hit1/225*100:.1f}%), Hit@3 = {dense_v2_hit3}/225 ({dense_v2_hit3/225*100:.1f}%), Hit@5 = {dense_v2_hit5}/225 ({dense_v2_hit5/225*100:.1f}%)")

print("\n" + "=" * 90)
print("2. RUNNING SPARSE-ONLY RETRIEVAL BENCHMARK ON 225 CASES (V2 GROUND TRUTH)")
print("=" * 90)

sparse_results = []
sparse_v1_hit1, sparse_v1_hit3, sparse_v1_hit5 = 0, 0, 0
sparse_v2_hit1, sparse_v2_hit3, sparse_v2_hit5 = 0, 0, 0

sparse_by_type = {
    "SINGLE": {"total": 0, "hit1": 0, "hit3": 0, "hit5": 0},
    "MULTI_VALID": {"total": 0, "hit1": 0, "hit3": 0, "hit5": 0, "primary_hit5": 0, "supporting_hit5": 0},
    "CO_REQUISITE": {"total": 0, "hit1": 0, "hit3": 0, "hit5": 0, "strict_hit3": 0, "strict_hit5": 0},
    "PRIMARY_PLUS_SUPPORTING": {"total": 0, "hit1": 0, "hit3": 0, "hit5": 0, "primary_hit5": 0, "supporting_hit5": 0}
}

sparse_false_miss_impact = []

sparse_start = time.time()
for idx, tc in enumerate(cases, 1):
    cid = tc["test_case_id"]
    cat = tc["category"]
    q = tc["query"]
    as_of = tc.get("as_of_date")
    ev_type = tc.get("evidence_type", "SINGLE")
    p_ev = tc["primary_evidence"]
    supp_evs = tc.get("acceptable_supporting_evidence", [])
    req_evs = tc.get("required_evidence_set", [])

    sparse_hits = retriever._sparse_search_postgresql_fts(q, limit=5, as_of_date=as_of)
    top5 = sparse_hits[:5]

    # Evaluation V1: Primary-only
    p_rank = None
    for r, h in enumerate(top5, 1):
        if matches_evidence(p_ev, h):
            p_rank = r
            break

    if p_rank == 1:
        sparse_v1_hit1 += 1
        sparse_v1_hit3 += 1
        sparse_v1_hit5 += 1
    elif p_rank in [2, 3]:
        sparse_v1_hit3 += 1
        sparse_v1_hit5 += 1
    elif p_rank in [4, 5]:
        sparse_v1_hit5 += 1

    # Evaluation V2: According to evidence_type
    matched_evidences = []
    matched_roles = []
    v2_rank = None

    # Check primary
    if p_rank is not None:
        matched_evidences.append(p_ev)
        matched_roles.append(p_ev.get("evidence_role", "PRIMARY"))

    # Check supporting
    supp_ranks = []
    for s_idx, s in enumerate(supp_evs):
        s_rank = None
        for r, h in enumerate(top5, 1):
            if matches_evidence(s, h):
                s_rank = r
                break
        if s_rank is not None:
            supp_ranks.append((s_rank, s))
            matched_evidences.append(s)
            matched_roles.append(s.get("evidence_role", "SUPPORTING"))

    is_v2_hit1 = False
    is_v2_hit3 = False
    is_v2_hit5 = False

    sparse_by_type[ev_type]["total"] += 1

    if ev_type == "SINGLE":
        is_v2_hit1 = (p_rank == 1)
        is_v2_hit3 = (p_rank is not None and p_rank <= 3)
        is_v2_hit5 = (p_rank is not None and p_rank <= 5)
        v2_rank = p_rank

    elif ev_type == "MULTI_VALID":
        all_valid_ranks = [p_rank] if p_rank is not None else []
        all_valid_ranks.extend([sr[0] for sr in supp_ranks])
        if all_valid_ranks:
            v2_rank = min(all_valid_ranks)
            is_v2_hit1 = (v2_rank == 1)
            is_v2_hit3 = (v2_rank <= 3)
            is_v2_hit5 = (v2_rank <= 5)
        if p_rank is not None and p_rank <= 5:
            sparse_by_type["MULTI_VALID"]["primary_hit5"] += 1
        if supp_ranks and any(sr[0] <= 5 for sr in supp_ranks):
            sparse_by_type["MULTI_VALID"]["supporting_hit5"] += 1

    elif ev_type == "CO_REQUISITE":
        req_matched_count = 0
        req_ranks = []
        for req in req_evs:
            r_matched = None
            for r, h in enumerate(top5, 1):
                if matches_evidence(req, h):
                    r_matched = r
                    break
            if r_matched is not None:
                req_matched_count += 1
                req_ranks.append(r_matched)

        strict_hit3 = (req_matched_count == len(req_evs) and len(req_evs) > 0 and all(rk <= 3 for rk in req_ranks))
        strict_hit5 = (req_matched_count == len(req_evs) and len(req_evs) > 0 and all(rk <= 5 for rk in req_ranks))
        if strict_hit3:
            sparse_by_type["CO_REQUISITE"]["strict_hit3"] += 1
        if strict_hit5:
            sparse_by_type["CO_REQUISITE"]["strict_hit5"] += 1

        v2_rank = p_rank
        is_v2_hit1 = (p_rank == 1)
        is_v2_hit3 = (p_rank is not None and p_rank <= 3) or strict_hit3
        is_v2_hit5 = (p_rank is not None and p_rank <= 5) or strict_hit5

    elif ev_type == "PRIMARY_PLUS_SUPPORTING":
        v2_rank = p_rank
        is_v2_hit1 = (p_rank == 1)
        is_v2_hit3 = (p_rank is not None and p_rank <= 3)
        is_v2_hit5 = (p_rank is not None and p_rank <= 5)

        if p_rank is not None and p_rank <= 5:
            sparse_by_type["PRIMARY_PLUS_SUPPORTING"]["primary_hit5"] += 1
        if supp_ranks and any(sr[0] <= 5 for sr in supp_ranks):
            sparse_by_type["PRIMARY_PLUS_SUPPORTING"]["supporting_hit5"] += 1

    if is_v2_hit1:
        sparse_v2_hit1 += 1
        sparse_by_type[ev_type]["hit1"] += 1
    if is_v2_hit3:
        sparse_v2_hit3 += 1
        sparse_by_type[ev_type]["hit3"] += 1
    if is_v2_hit5:
        sparse_v2_hit5 += 1
        sparse_by_type[ev_type]["hit5"] += 1

    if cid in FALSE_MISS_17:
        sparse_false_miss_impact.append({
            "test_case_id": cid,
            "query": q,
            "evidence_type": ev_type,
            "v1_primary_rank": p_rank,
            "v1_status": "PASS" if p_rank and p_rank <= 5 else "MISS",
            "v2_rank": v2_rank,
            "v2_status": "PASS" if is_v2_hit5 else "MISS",
            "matched_roles": matched_roles
        })

    sparse_results.append({
        "test_case_id": cid,
        "category": cat,
        "query": q,
        "evidence_type": ev_type,
        "v1_primary_rank": p_rank,
        "v2_rank": v2_rank,
        "v2_hit1": is_v2_hit1,
        "v2_hit3": is_v2_hit3,
        "v2_hit5": is_v2_hit5,
        "matched_roles": matched_roles,
        "top5_retrieved": [
            {
                "rank": r_i,
                "document_id": h.get("document_id"),
                "official_number": h.get("official_number"),
                "article": h.get("article_number"),
                "score": h.get("score")
            }
            for r_i, h in enumerate(top5, 1)
        ]
    })

sparse_elapsed = time.time() - sparse_start
print(f"Sparse-only benchmark completed in {sparse_elapsed:.1f}s")
print(f"Sparse V1: Hit@1 = {sparse_v1_hit1}/225 ({sparse_v1_hit1/225*100:.1f}%), Hit@3 = {sparse_v1_hit3}/225 ({sparse_v1_hit3/225*100:.1f}%), Hit@5 = {sparse_v1_hit5}/225 ({sparse_v1_hit5/225*100:.1f}%)")
print(f"Sparse V2: Hit@1 = {sparse_v2_hit1}/225 ({sparse_v2_hit1/225*100:.1f}%), Hit@3 = {sparse_v2_hit3}/225 ({sparse_v2_hit3/225*100:.1f}%), Hit@5 = {sparse_v2_hit5}/225 ({sparse_v2_hit5/225*100:.1f}%)")

print("\n" + "=" * 90)
print("3. COMPLEMENTARITY ANALYSIS (DENSE VS. SPARSE ON V2 GROUND TRUTH)")
print("=" * 90)

dense_pass_sparse_fail = []
dense_fail_sparse_pass = []
both_pass = []
both_fail = []

for d_res, s_res in zip(dense_results, sparse_results):
    cid = d_res["test_case_id"]
    q = d_res["query"]
    cat = d_res["category"]
    d_pass = d_res["v2_hit5"]
    s_pass = s_res["v2_hit5"]

    info = {
        "test_case_id": cid,
        "category": cat,
        "query": q,
        "dense_rank": d_res["v2_rank"],
        "sparse_rank": s_res["v2_rank"],
        "dense_roles": d_res["matched_roles"],
        "sparse_roles": s_res["matched_roles"]
    }

    if d_pass and not s_pass:
        dense_pass_sparse_fail.append(info)
    elif not d_pass and s_pass:
        dense_fail_sparse_pass.append(info)
    elif d_pass and s_pass:
        both_pass.append(info)
    else:
        both_fail.append(info)

print(f"Dense PASS / Sparse FAIL : {len(dense_pass_sparse_fail)} cases ({len(dense_pass_sparse_fail)/225*100:.1f}%)")
print(f"Dense FAIL / Sparse PASS : {len(dense_fail_sparse_pass)} cases ({len(dense_fail_sparse_pass)/225*100:.1f}%)  <-- KEY RESCUE POTENTIAL FOR HYBRID")
print(f"Both PASS                : {len(both_pass)} cases ({len(both_pass)/225*100:.1f}%)")
print(f"Both FAIL                : {len(both_fail)} cases ({len(both_fail)/225*100:.1f}%)")
print(f"Theoretical Upper Bound (Dense OR Sparse) : {len(dense_pass_sparse_fail) + len(dense_fail_sparse_pass) + len(both_pass)} / 225 ({(len(dense_pass_sparse_fail) + len(dense_fail_sparse_pass) + len(both_pass))/225*100:.1f}%)")

print("\nDetail of Dense FAIL + Sparse PASS cases:")
for c in dense_fail_sparse_pass:
    print(f"  [{c['test_case_id']}] (Rank {c['sparse_rank']}) {c['query'][:70]}...")

# Save output JSONs
dense_output = {
    "version": "v2",
    "retrieval_mode": "dense_only",
    "total_cases": 225,
    "metrics_v1_primary_only": {
        "hit1": dense_v1_hit1,
        "hit3": dense_v1_hit3,
        "hit5": dense_v1_hit5,
        "hit1_pct": round(dense_v1_hit1 / 225 * 100, 2),
        "hit3_pct": round(dense_v1_hit3 / 225 * 100, 2),
        "hit5_pct": round(dense_v1_hit5 / 225 * 100, 2)
    },
    "metrics_v2_revised_ground_truth": {
        "hit1": dense_v2_hit1,
        "hit3": dense_v2_hit3,
        "hit5": dense_v2_hit5,
        "hit1_pct": round(dense_v2_hit1 / 225 * 100, 2),
        "hit3_pct": round(dense_v2_hit3 / 225 * 100, 2),
        "hit5_pct": round(dense_v2_hit5 / 225 * 100, 2)
    },
    "by_evidence_type": dense_by_type,
    "false_miss_17_impact": dense_false_miss_impact,
    "cases": dense_results
}

sparse_output = {
    "version": "v2",
    "retrieval_mode": "sparse_only_postgresql_fts",
    "total_cases": 225,
    "metrics_v1_primary_only": {
        "hit1": sparse_v1_hit1,
        "hit3": sparse_v1_hit3,
        "hit5": sparse_v1_hit5,
        "hit1_pct": round(sparse_v1_hit1 / 225 * 100, 2),
        "hit3_pct": round(sparse_v1_hit3 / 225 * 100, 2),
        "hit5_pct": round(sparse_v1_hit5 / 225 * 100, 2)
    },
    "metrics_v2_revised_ground_truth": {
        "hit1": sparse_v2_hit1,
        "hit3": sparse_v2_hit3,
        "hit5": sparse_v2_hit5,
        "hit1_pct": round(sparse_v2_hit1 / 225 * 100, 2),
        "hit3_pct": round(sparse_v2_hit3 / 225 * 100, 2),
        "hit5_pct": round(sparse_v2_hit5 / 225 * 100, 2)
    },
    "by_evidence_type": sparse_by_type,
    "false_miss_17_impact": sparse_false_miss_impact,
    "complementarity_summary": {
        "dense_pass_sparse_fail": len(dense_pass_sparse_fail),
        "dense_fail_sparse_pass": len(dense_fail_sparse_pass),
        "both_pass": len(both_pass),
        "both_fail": len(both_fail),
        "dense_fail_sparse_pass_cases": dense_fail_sparse_pass
    },
    "cases": sparse_results
}

# Save files in both data/ and root
with open(PROJECT_ROOT / "dense_225_v2_results.json", "w", encoding="utf-8") as f:
    json.dump(dense_output, f, ensure_ascii=False, indent=2)
with open(PROJECT_ROOT / "data" / "gold_evaluation" / "dense_225_v2_results.json", "w", encoding="utf-8") as f:
    json.dump(dense_output, f, ensure_ascii=False, indent=2)

with open(PROJECT_ROOT / "sparse_225_v2_results.json", "w", encoding="utf-8") as f:
    json.dump(sparse_output, f, ensure_ascii=False, indent=2)
with open(PROJECT_ROOT / "data" / "gold_evaluation" / "sparse_225_v2_results.json", "w", encoding="utf-8") as f:
    json.dump(sparse_output, f, ensure_ascii=False, indent=2)

print("\nSuccessfully saved dense_225_v2_results.json and sparse_225_v2_results.json! 🟢")
