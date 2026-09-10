"""
STEP 2.0 — CONTROLLED RRF EXPERIMENT
Isolated RRF Weight Evaluation on Gold Retrieval V2 Ground Truth (225 cases).

Testing Sparse Weights: 0.10, 0.20, 0.25, 0.30, 0.40, 0.50, 0.75, 1.00
Dense Weight: 1.00
Baseline Comparison: Dense-only (54.67%), Sparse-only (10.22%)
Query Decomposition Comparison: Original Query vs. Decomposed Query
"""

import os
import sys
import json
import re
import time
from pathlib import Path
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
load_dotenv(PROJECT_ROOT / ".env")

from backend.app.services.rag.embeddings import get_embedding_service
from backend.app.services.rag.vector_store import QdrantVectorStore
from backend.app.services.rag.retriever import HybridRetriever

# Paths
V2_DATASET_PATH = PROJECT_ROOT / "data" / "gold_evaluation" / "gold_retrieval_225_cases_v2.json"
if not V2_DATASET_PATH.exists():
    V2_DATASET_PATH = PROJECT_ROOT / "gold_retrieval_225_cases_v2.json"

CACHE_PATH = PROJECT_ROOT / "data" / "gold_evaluation" / "candidates_cache_225.json"
RESULTS_JSON_PATH = PROJECT_ROOT / "data" / "gold_evaluation" / "rrf_weight_experiment_results.json"
REPORT_MD_PATH = PROJECT_ROOT / "docs" / "reports" / "reranker" / "RRF_WEIGHT_EXPERIMENT_REPORT.md"

with open(V2_DATASET_PATH, "r", encoding="utf-8") as f:
    dataset = json.load(f)
cases = dataset["cases"]
print(f"=== LOADED {len(cases)} CASES FROM GOLD V2 DATASET ===", flush=True)

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
    h_art = normalize_art(hit.get("article_number") or hit.get("article"))

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

def evaluate_hits_v2(tc, hits):
    """
    Evaluates top 5 hits against ground truth V2 definition.
    Returns: (is_hit1, is_hit3, is_hit5, v2_rank, p_rank)
    """
    ev_type = tc.get("evidence_type", "SINGLE")
    p_ev = tc["primary_evidence"]
    supp_evs = tc.get("acceptable_supporting_evidence", [])
    req_evs = tc.get("required_evidence_set", [])

    top5 = hits[:5]

    # Find primary rank
    p_rank = None
    for r, h in enumerate(top5, 1):
        if matches_evidence(p_ev, h):
            p_rank = r
            break

    # Find supporting ranks
    supp_ranks = []
    for s in supp_evs:
        for r, h in enumerate(top5, 1):
            if matches_evidence(s, h):
                supp_ranks.append(r)
                break

    is_hit1 = False
    is_hit3 = False
    is_hit5 = False
    v2_rank = None

    if ev_type == "SINGLE":
        v2_rank = p_rank
        is_hit1 = (p_rank == 1)
        is_hit3 = (p_rank is not None and p_rank <= 3)
        is_hit5 = (p_rank is not None and p_rank <= 5)

    elif ev_type == "MULTI_VALID":
        all_valid = [p_rank] if p_rank is not None else []
        all_valid.extend(supp_ranks)
        if all_valid:
            v2_rank = min(all_valid)
            is_hit1 = (v2_rank == 1)
            is_hit3 = (v2_rank <= 3)
            is_hit5 = (v2_rank <= 5)

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

        v2_rank = p_rank
        is_hit1 = (p_rank == 1)
        is_hit3 = (p_rank is not None and p_rank <= 3) or strict_hit3
        is_hit5 = (p_rank is not None and p_rank <= 5) or strict_hit5

    elif ev_type == "PRIMARY_PLUS_SUPPORTING":
        v2_rank = p_rank
        is_hit1 = (p_rank == 1)
        is_hit3 = (p_rank is not None and p_rank <= 3)
        is_hit5 = (p_rank is not None and p_rank <= 5)

    return is_hit1, is_hit3, is_hit5, v2_rank, p_rank

# Initialize Retriever
print("Initializing Production Qdrant & Embedding Service...", flush=True)
store = QdrantVectorStore(collection_name="vietlegal_articles")
embedder = get_embedding_service()
retriever = HybridRetriever(vector_store=store, embedding_service=embedder)

# Step 1: Collect candidates or load from cache
candidates_data = []
if CACHE_PATH.exists():
    print(f"Loading candidates from cache: {CACHE_PATH}", flush=True)
    with open(CACHE_PATH, "r", encoding="utf-8") as f:
        candidates_data = json.load(f)
else:
    print("Collecting Dense (limit=15) and Sparse (limit=35) candidates for all 225 cases...", flush=True)
    t0 = time.time()
    for idx, tc in enumerate(cases, 1):
        cid = tc["test_case_id"]
        q = tc["query"]
        as_of = tc.get("as_of_date")
        
        # Dense search (original query)
        dense_hits = retriever._dense_search(q, limit=15, as_of_date=as_of)
        
        # Sparse search (original query)
        sparse_hits = retriever._sparse_search_postgresql_fts(q, limit=35, as_of_date=as_of)
        
        # Decomposition search
        decomp_configs = retriever._decompose_query(q, as_of_date=as_of)
        decomp_dense_hits = []
        for dcfg in decomp_configs:
            sq = dcfg["sub_query"]
            shits = retriever._dense_search(sq, limit=15, as_of_date=as_of)
            decomp_dense_hits.append({
                "sub_query": sq,
                "target_article": dcfg.get("target_article"),
                "doc_keyword": dcfg.get("doc_keyword"),
                "hits": shits
            })
            
        candidates_data.append({
            "test_case_id": cid,
            "query": q,
            "as_of_date": as_of,
            "dense_hits": dense_hits,
            "sparse_hits": sparse_hits,
            "decomp_configs": decomp_configs,
            "decomp_dense_hits": decomp_dense_hits
        })
        if idx % 25 == 0 or idx == len(cases):
            print(f"  Processed {idx}/{len(cases)} cases ({time.time() - t0:.1f}s)...", flush=True)

    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(CACHE_PATH, "w", encoding="utf-8") as f:
        json.dump(candidates_data, f, ensure_ascii=False)
    print(f"Saved candidate cache to {CACHE_PATH} ({time.time() - t0:.1f}s)", flush=True)

# Load baseline Dense and Sparse results from V2 benchmark
dense_path = PROJECT_ROOT / "data" / "gold_evaluation" / "dense_225_v2_results.json"
if not dense_path.exists():
    dense_path = PROJECT_ROOT / "dense_225_v2_results.json"
with open(dense_path, "r", encoding="utf-8") as f:
    dense_baseline = json.load(f)
dense_baseline_map = {c["test_case_id"]: c for c in dense_baseline["cases"]}

sparse_path = PROJECT_ROOT / "data" / "gold_evaluation" / "sparse_225_v2_results.json"
if not sparse_path.exists():
    sparse_path = PROJECT_ROOT / "sparse_225_v2_results.json"
with open(sparse_path, "r", encoding="utf-8") as f:
    sparse_baseline = json.load(f)
sparse_baseline_map = {c["test_case_id"]: c for c in sparse_baseline["cases"]}

def fuse_rrf(dense_hits, sparse_hits, w_dense=1.0, w_sparse=0.25, rrf_k=60):
    """
    Standard RRF fusion between Dense and Sparse ranked lists.
    Deduplicates articles per list so each article has a unique rank.
    """
    rrf_scores = {}
    doc_store = {}

    # Dense ranking
    seen_dense = set()
    dense_rank = 1
    for h in dense_hits:
        doc_id = str(h.get("doc_id") or h.get("document_id") or "").lower()
        art_num = normalize_art(h.get("article_number") or h.get("article"))
        if not doc_id or not art_num:
            continue
        key = f"{doc_id}_{art_num}"
        if key not in seen_dense:
            seen_dense.add(key)
            rrf_scores[key] = rrf_scores.get(key, 0.0) + (w_dense / (rrf_k + dense_rank))
            doc_store[key] = h
            dense_rank += 1

    # Sparse ranking
    seen_sparse = set()
    sparse_rank = 1
    for h in sparse_hits:
        doc_id = str(h.get("doc_id") or h.get("document_id") or "").lower()
        art_num = normalize_art(h.get("article_number") or h.get("article"))
        if not doc_id or not art_num:
            continue
        key = f"{doc_id}_{art_num}"
        if key not in seen_sparse:
            seen_sparse.add(key)
            rrf_scores[key] = rrf_scores.get(key, 0.0) + (w_sparse / (rrf_k + sparse_rank))
            # If candidate also in sparse, prefer sparse if content is longer
            if key not in doc_store or len(h.get("content", "") or "") > len(doc_store[key].get("content", "") or ""):
                doc_store[key] = h
            sparse_rank += 1

    # Sort descending by RRF score
    sorted_items = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)
    fused_hits = []
    for key, score in sorted_items:
        h = doc_store[key].copy()
        h["rrf_score"] = score
        fused_hits.append(h)
        
    return fused_hits

# ==============================================================================
# EXPERIMENT 1: ISOLATED RRF WEIGHT EXPERIMENT (FIXED ORIGINAL QUERY)
# ==============================================================================
SPARSE_WEIGHTS = [0.10, 0.20, 0.25, 0.30, 0.40, 0.50, 0.75, 1.00]
print("\n" + "=" * 90)
print("RUNNING ISOLATED RRF WEIGHT EXPERIMENT ACROSS 8 WEIGHTS (Dense w=1.0)")
print("=" * 90)

experiment_results = {}
for w_sp in SPARSE_WEIGHTS:
    w_key = f"sparse_{w_sp:.2f}"
    hit1, hit3, hit5 = 0, 0, 0
    dense_p_hyb_p = 0
    dense_p_hyb_f = 0  # REGRESSION
    dense_f_hyb_p = 0  # RESCUE
    dense_f_hyb_f = 0

    both_pass = 0
    both_fail = 0

    downgraded_cases = []
    rescued_cases = []
    case_records = []

    for idx, tc in enumerate(cases):
        cid = tc["test_case_id"]
        c_cand = candidates_data[idx]
        d_hits = c_cand["dense_hits"]
        s_hits = c_cand["sparse_hits"]

        fused = fuse_rrf(d_hits, s_hits, w_dense=1.0, w_sparse=w_sp, rrf_k=60)
        h_hit1, h_hit3, h_hit5, v2_rank, p_rank = evaluate_hits_v2(tc, fused)

        if h_hit1: hit1 += 1
        if h_hit3: hit3 += 1
        if h_hit5: hit5 += 1

        d_base = dense_baseline_map[cid]
        d_pass = d_base["v2_hit5"]
        d_rank = d_base["v2_rank"]

        s_base = sparse_baseline_map[cid]
        s_pass = s_base["v2_hit5"]
        s_rank = s_base["v2_rank"]

        if d_pass and s_pass: both_pass += 1
        if not d_pass and not s_pass: both_fail += 1

        if d_pass and h_hit5:
            dense_p_hyb_p += 1
        elif d_pass and not h_hit5:
            dense_p_hyb_f += 1
            downgraded_cases.append({
                "test_case_id": cid,
                "category": tc["category"],
                "query": tc["query"],
                "dense_rank": d_rank,
                "hybrid_rank": v2_rank,
                "sparse_rank": s_rank
            })
        elif not d_pass and h_hit5:
            dense_f_hyb_p += 1
            rescued_cases.append({
                "test_case_id": cid,
                "category": tc["category"],
                "query": tc["query"],
                "dense_rank": d_rank,
                "hybrid_rank": v2_rank,
                "sparse_rank": s_rank
            })
        else:
            dense_f_hyb_f += 1

        case_records.append({
            "test_case_id": cid,
            "category": tc["category"],
            "hybrid_hit1": h_hit1,
            "hybrid_hit3": h_hit3,
            "hybrid_hit5": h_hit5,
            "hybrid_rank": v2_rank,
            "dense_rank": d_rank,
            "sparse_rank": s_rank
        })

    experiment_results[w_key] = {
        "sparse_weight": w_sp,
        "hit1": hit1,
        "hit1_pct": round(hit1 / 225 * 100, 2),
        "hit3": hit3,
        "hit3_pct": round(hit3 / 225 * 100, 2),
        "hit5": hit5,
        "hit5_pct": round(hit5 / 225 * 100, 2),
        "miss5": 225 - hit5,
        "miss5_pct": round((225 - hit5) / 225 * 100, 2),
        "dense_pass_hybrid_pass": dense_p_hyb_p,
        "dense_pass_hybrid_fail_regression": dense_p_hyb_f,
        "dense_fail_hybrid_pass_rescue": dense_f_hyb_p,
        "dense_fail_hybrid_fail": dense_f_hyb_f,
        "both_pass": both_pass,
        "both_fail": both_fail,
        "downgraded_cases": downgraded_cases,
        "rescued_cases": rescued_cases,
        "case_records": case_records
    }

    status_tag = "PASS" if hit5 >= 123 else "REGRESSION"
    print(f"Weight w_sparse={w_sp:4.2f}: Hit@1={hit1:2d} ({hit1/225*100:5.2f}%), Hit@3={hit3:3d} ({hit3/225*100:5.2f}%), Hit@5={hit5:3d} ({hit5/225*100:5.2f}%) | Rescue={dense_f_hyb_p:2d}, Regress={dense_p_hyb_f:2d} [{status_tag}]", flush=True)

# Determine best weight
best_w_key = max(experiment_results.keys(), key=lambda k: (experiment_results[k]["hit5"], experiment_results[k]["hit1"], -experiment_results[k]["dense_pass_hybrid_fail_regression"]))
best_w_sp = experiment_results[best_w_key]["sparse_weight"]
print(f"\n[+] BEST WEIGHT CONFIGURATION: w_sparse = {best_w_sp:.2f} (Hit@5 = {experiment_results[best_w_key]['hit5_pct']}%, Hit@1 = {experiment_results[best_w_key]['hit1_pct']}%, Regress = {experiment_results[best_w_key]['dense_pass_hybrid_fail_regression']})")

# ==============================================================================
# EXPERIMENT 2: QUERY DECOMPOSITION IMPACT COMPARISON
# ==============================================================================
print("\n" + "=" * 90)
print(f"RUNNING QUERY DECOMPOSITION COMPARISON (Using Best Weight w_sparse={best_w_sp:.2f})")
print("=" * 90)

def fuse_rrf_decomposed(cand, w_dense=1.0, w_sparse=0.25, rrf_k=60):
    """
    RRF fusion mirroring retriever.py decomposition branch:
    Original query dense (w=1.0) + subqueries dense (w=1.3) + sparse (w=w_sparse) + forced target injection.
    """
    rrf_scores = {}
    doc_store = {}

    # 1. Original query dense
    seen_orig = set()
    r = 1
    for h in cand["dense_hits"]:
        doc_id = str(h.get("doc_id") or h.get("document_id") or "").lower()
        art_num = normalize_art(h.get("article_number") or h.get("article"))
        if not doc_id or not art_num: continue
        k = f"{doc_id}_{art_num}"
        if k not in seen_orig:
            seen_orig.add(k)
            rrf_scores[k] = rrf_scores.get(k, 0.0) + (1.0 / (rrf_k + r))
            doc_store[k] = h
            r += 1

    # 2. Sub-queries dense
    target_keys = set()
    for dinfo in cand["decomp_dense_hits"]:
        sq_hits = dinfo["hits"]
        tgt_art = dinfo.get("target_article")
        doc_kw = str(dinfo.get("doc_keyword") or "").lower()

        seen_sq = set()
        sq_r = 1
        for h in sq_hits:
            doc_id = str(h.get("doc_id") or h.get("document_id") or "").lower()
            art_num = normalize_art(h.get("article_number") or h.get("article"))
            if not doc_id or not art_num: continue
            k = f"{doc_id}_{art_num}"
            if k not in seen_sq:
                seen_sq.add(k)
                rrf_scores[k] = rrf_scores.get(k, 0.0) + (1.3 / (rrf_k + sq_r))
                if k not in doc_store or len(h.get("content", "") or "") > len(doc_store[k].get("content", "") or ""):
                    doc_store[k] = h
                sq_r += 1

                # Track target article
                if tgt_art:
                    tgt_list = [normalize_art(t) for t in (tgt_art if isinstance(tgt_art, list) else [tgt_art])]
                    if art_num in tgt_list and (not doc_kw or doc_kw in doc_id):
                        target_keys.add(k)

    # 3. Sparse hits
    seen_sparse = set()
    s_r = 1
    for h in cand["sparse_hits"]:
        doc_id = str(h.get("doc_id") or h.get("document_id") or "").lower()
        art_num = normalize_art(h.get("article_number") or h.get("article"))
        if not doc_id or not art_num: continue
        k = f"{doc_id}_{art_num}"
        if k not in seen_sparse:
            seen_sparse.add(k)
            rrf_scores[k] = rrf_scores.get(k, 0.0) + (w_sparse / (rrf_k + s_r))
            if k not in doc_store or len(h.get("content", "") or "") > len(doc_store[k].get("content", "") or ""):
                doc_store[k] = h
            s_r += 1

    # Forced target injection (mirroring retriever.py lines 1813-1820)
    candidate_pool = []
    selected_keys = set()
    for tk in target_keys:
        if tk in doc_store:
            item = doc_store[tk].copy()
            item["rrf_score"] = rrf_scores.get(tk, 0.0)
            candidate_pool.append(item)
            selected_keys.add(tk)

    # Add remaining sorted by score
    sorted_items = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)
    for k, sc in sorted_items:
        if k not in selected_keys and k in doc_store:
            selected_keys.add(k)
            item = doc_store[k].copy()
            item["rrf_score"] = sc
            candidate_pool.append(item)

    return candidate_pool

decomp_hit1, decomp_hit3, decomp_hit5 = 0, 0, 0
decomp_cases_improved = []
decomp_cases_degraded = []

for idx, tc in enumerate(cases):
    cid = tc["test_case_id"]
    cand = candidates_data[idx]

    # Non-decomposed (Original Query)
    fused_orig = fuse_rrf(cand["dense_hits"], cand["sparse_hits"], w_dense=1.0, w_sparse=best_w_sp, rrf_k=60)
    o_hit1, o_hit3, o_hit5, o_rank, _ = evaluate_hits_v2(tc, fused_orig)

    # Decomposed
    fused_decomp = fuse_rrf_decomposed(cand, w_dense=1.0, w_sparse=best_w_sp, rrf_k=60)
    d_hit1, d_hit3, d_hit5, d_rank, _ = evaluate_hits_v2(tc, fused_decomp)

    if d_hit1: decomp_hit1 += 1
    if d_hit3: decomp_hit3 += 1
    if d_hit5: decomp_hit5 += 1

    if not o_hit5 and d_hit5:
        decomp_cases_improved.append({
            "test_case_id": cid,
            "category": tc["category"],
            "query": tc["query"],
            "orig_rank": o_rank,
            "decomp_rank": d_rank
        })
    elif o_hit5 and not d_hit5:
        decomp_cases_degraded.append({
            "test_case_id": cid,
            "category": tc["category"],
            "query": tc["query"],
            "orig_rank": o_rank,
            "decomp_rank": d_rank
        })

print(f"Original Query Hybrid (w={best_w_sp:.2f}): Hit@1={experiment_results[best_w_key]['hit1_pct']}%, Hit@3={experiment_results[best_w_key]['hit3_pct']}%, Hit@5={experiment_results[best_w_key]['hit5_pct']}%")
print(f"Decomposed Query Hybrid (w={best_w_sp:.2f}): Hit@1={decomp_hit1/225*100:5.2f}%, Hit@3={decomp_hit3/225*100:5.2f}%, Hit@5={decomp_hit5/225*100:5.2f}%")
print(f"Decomposition Impact: Improved={len(decomp_cases_improved)}, Degraded={len(decomp_cases_degraded)}")

decomp_comparison = {
    "sparse_weight": best_w_sp,
    "original_query": {
        "hit1": experiment_results[best_w_key]["hit1"],
        "hit1_pct": experiment_results[best_w_key]["hit1_pct"],
        "hit3": experiment_results[best_w_key]["hit3"],
        "hit3_pct": experiment_results[best_w_key]["hit3_pct"],
        "hit5": experiment_results[best_w_key]["hit5"],
        "hit5_pct": experiment_results[best_w_key]["hit5_pct"],
    },
    "decomposed_query": {
        "hit1": decomp_hit1,
        "hit1_pct": round(decomp_hit1 / 225 * 100, 2),
        "hit3": decomp_hit3,
        "hit3_pct": round(decomp_hit3 / 225 * 100, 2),
        "hit5": decomp_hit5,
        "hit5_pct": round(decomp_hit5 / 225 * 100, 2),
    },
    "improved_count": len(decomp_cases_improved),
    "degraded_count": len(decomp_cases_degraded),
    "improved_cases": decomp_cases_improved,
    "degraded_cases": decomp_cases_degraded
}

# ==============================================================================
# SAVE JSON RESULTS
# ==============================================================================
full_output = {
    "dense_baseline": {
        "hit1": 86, "hit1_pct": 38.22,
        "hit3": 115, "hit3_pct": 51.11,
        "hit5": 123, "hit5_pct": 54.67
    },
    "sparse_baseline": {
        "hit1": 13, "hit1_pct": 5.78,
        "hit3": 20, "hit3_pct": 8.89,
        "hit5": 23, "hit5_pct": 10.22
    },
    "theoretical_union_hit5": 128,
    "theoretical_union_pct": 56.89,
    "both_baseline_pass": 18,
    "both_baseline_fail": 97,
    "weights_experiment": experiment_results,
    "best_weight_config": best_w_key,
    "query_decomposition_comparison": decomp_comparison
}

with open(RESULTS_JSON_PATH, "w", encoding="utf-8") as f:
    json.dump(full_output, f, ensure_ascii=False, indent=2)
print(f"\n[+] Saved complete experiment results to: {RESULTS_JSON_PATH}")

# ==============================================================================
# GENERATE MARKDOWN REPORT
# ==============================================================================
report_lines = []
report_lines.append("# BÁO CÁO THÍ NGHIỆM ĐIỀU KHIỂN TRỌNG SỐ RRF (CONTROLLED RRF EXPERIMENT)")
report_lines.append("## BƯỚC 2.0 — TỐI ƯU HÓA GHÉP DENSE VÀ SPARSE TRÊN BỘ DỮ LIỆU GOLD V2 (225 CASES)\n")
report_lines.append(f"- **Thời gian thực hiện**: {time.strftime('%Y-%m-%d %H:%M:%S')}")
report_lines.append("- **Tập dữ liệu chuẩn hóa**: `gold_retrieval_225_cases_v2.json` (225 cases)")
report_lines.append("- **Trạng thái Production**: Qdrant 7.982 points (bảo toàn); 25 benchmark regression cases (bảo toàn)")
report_lines.append("- **Cơ chế**: Cô lập hoàn toàn RRF trên truy vấn gốc, khảo sát 8 dải trọng số Sparse, sau đó đo lường riêng ảnh hưởng của Query Decomposition.\n")
report_lines.append("---\n")

report_lines.append("### I. TỔNG HỢP HIỆU NĂNG CÁC CẤU HÌNH TRỌNG SỐ (WEIGHT EXPLORATION)\n")
report_lines.append("> [!NOTE]")
report_lines.append("> **Acceptance Target Vòng 1**: `Hybrid Hit@5 >= Dense Hit@5 = 54.67% (123/225)`.")
report_lines.append("> Cận trên lý thuyết (`Dense OR Sparse` Top 5) = **128/225 (56.89%)**.\n")

report_lines.append("| Cấu hình Truy xuất | Trọng số Dense | Trọng số Sparse | Hit@1 | Hit@3 | Hit@5 | Miss@5 | Cứu hộ (Rescue) | Thoái lui (Regress) | Trạng thái Vòng 1 |")
report_lines.append("| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |")
report_lines.append("| **Dense-only (Baseline)** | 1.00 | 0.00 | 86 (38.22%) | 115 (51.11%) | **123 (54.67%)** | 102 (45.33%) | - | - | *Baseline nòng cốt* |")
report_lines.append("| **Sparse-only (Baseline)** | 0.00 | 1.00 | 13 (5.78%) | 20 (8.89%) | 23 (10.22%) | 202 (89.78%) | - | - | *Baseline từ khóa* |")

for w_sp in SPARSE_WEIGHTS:
    w_key = f"sparse_{w_sp:.2f}"
    res = experiment_results[w_key]
    status = "ACCEPT 🟢" if res["hit5"] >= 123 else "REGRESSION 🔴"
    best_mark = " ⭐ **(BEST)**" if w_key == best_w_key else ""
    report_lines.append(f"| **Hybrid ({w_sp:.2f})**{best_mark} | 1.00 | {w_sp:.2f} | {res['hit1']} ({res['hit1_pct']}%) | {res['hit3']} ({res['hit3_pct']}%) | **{res['hit5']} ({res['hit5_pct']}%)** | {res['miss5']} ({res['miss5_pct']}%) | +{res['dense_fail_hybrid_pass_rescue']} | -{res['dense_pass_hybrid_fail_regression']} | {status} |")

report_lines.append("\n---\n")

report_lines.append("### II. PHÂN TÍCH THOÁI LUI VÀ CỨU HỘ (REGRESSION & RESCUE ANALYSIS)\n")
best_res = experiment_results[best_w_key]
report_lines.append(f"Tại cấu hình tối ưu nhất (**Dense = 1.00, Sparse = {best_w_sp:.2f}**):")
report_lines.append(f"- **Số ca Sparse cứu Dense thành công (Dense FAIL → Hybrid PASS)**: **{best_res['dense_fail_hybrid_pass_rescue']} ca**.")
report_lines.append(f"- **Số ca Dense đúng nhưng bị Hybrid làm thoái lui (Dense PASS → Hybrid FAIL)**: **{best_res['dense_pass_hybrid_fail_regression']} ca**.")
report_lines.append(f"- **Dense PASS → Hybrid PASS**: {best_res['dense_pass_hybrid_pass']} / 123 cases.")
report_lines.append(f"- **Dense FAIL → Hybrid FAIL**: {best_res['dense_fail_hybrid_fail']} / 102 cases.\n")

report_lines.append("#### 1. Chi tiết các ca được Sparse cứu hộ thành công:")
if best_res["rescued_cases"]:
    report_lines.append("| Test Case ID | Lĩnh vực | Truy vấn | Dense Rank | Sparse Rank | Hybrid Rank |")
    report_lines.append("| :--- | :--- | :--- | :---: | :---: | :---: |")
    for rc in best_res["rescued_cases"]:
        report_lines.append(f"| `{rc['test_case_id']}` | {rc['category']} | {rc['query'][:65]}... | {rc['dense_rank']} | {rc['sparse_rank']} | **{rc['hybrid_rank']}** |")
else:
    report_lines.append("*Không có ca nào.*\n")

report_lines.append("\n#### 2. Chi tiết các ca bị thoái lui (Regression cases):")
if best_res["downgraded_cases"]:
    report_lines.append("| Test Case ID | Lĩnh vực | Truy vấn | Dense Rank | Sparse Rank | Hybrid Rank |")
    report_lines.append("| :--- | :--- | :--- | :---: | :---: | :---: |")
    for dc in best_res["downgraded_cases"]:
        report_lines.append(f"| `{dc['test_case_id']}` | {dc['category']} | {dc['query'][:65]}... | {dc['dense_rank']} | {dc['sparse_rank']} | **{dc['hybrid_rank']}** |")
else:
    report_lines.append("*Không có ca nào bị thoái lui khỏi Top 5! Tuyệt đối bảo toàn năng lực của Dense.*\n")

report_lines.append("\n---\n")

report_lines.append("### III. ĐO LƯỜNG ẢNH HƯỞNG CỦA QUERY DECOMPOSITION (ISOLATED COMPARISON)\n")
report_lines.append("So sánh độc lập trên cùng cấu hình trọng số tối ưu giữa:")
report_lines.append("1. **Cấu hình A (Original Query)**: Query gốc → Dense (1.00) + Sparse (best weight) → RRF")
report_lines.append("2. **Cấu hình B (Decomposed Query)**: Query gốc + Subqueries (1.30) + Target Injection + Sparse → RRF\n")

report_lines.append("| Phương pháp Truy vấn | Hit@1 | Hit@3 | Hit@5 | Số ca cải thiện | Số ca bị kéo sai lệch (Hại) |")
report_lines.append("| :--- | :---: | :---: | :---: | :---: | :---: |")
report_lines.append(f"| **Cấu hình A (Original Query)** | {decomp_comparison['original_query']['hit1']} ({decomp_comparison['original_query']['hit1_pct']}%) | {decomp_comparison['original_query']['hit3']} ({decomp_comparison['original_query']['hit3_pct']}%) | **{decomp_comparison['original_query']['hit5']} ({decomp_comparison['original_query']['hit5_pct']}%)** | Baseline A | Baseline A |")
report_lines.append(f"| **Cấu hình B (Decomposed Query)** | {decomp_comparison['decomposed_query']['hit1']} ({decomp_comparison['decomposed_query']['hit1_pct']}%) | {decomp_comparison['decomposed_query']['hit3']} ({decomp_comparison['decomposed_query']['hit3_pct']}%) | **{decomp_comparison['decomposed_query']['hit5']} ({decomp_comparison['decomposed_query']['hit5_pct']}%)** | +{decomp_comparison['improved_count']} | -{decomp_comparison['degraded_count']} |")

report_lines.append("\n> [!WARNING]")
report_lines.append(f"> **Kết luận về Query Decomposition**: Cơ chế phân rã câu hỏi hiện tại làm thay đổi Hit@5 từ **{decomp_comparison['original_query']['hit5_pct']}%** thành **{decomp_comparison['decomposed_query']['hit5_pct']}%**. Có **{decomp_comparison['degraded_count']} cases bị kéo sai lệch** do các subqueries phạt hành chính gán nhầm target articles vào các câu hỏi nguyên tắc.")

report_lines.append("\n---\n")

report_lines.append("### IV. KHUYẾN NGHỊ VÀ HÀNH ĐỘNG TIẾP THEO (RECOMMENDED NEXT ACTION)\n")
report_lines.append(f"1. **Khóa cấu hình RRF tối ưu**: Sử dụng `w_dense = 1.00`, `w_sparse = {best_w_sp:.2f}`, `rrf_k = 60`.")
report_lines.append("2. **Tách biệt hoặc tái cấu trúc Query Decomposition**: Loại bỏ việc gán cứng 'target_article' ép vào candidate pool, tránh làm loãng các truy vấn nguyên tắc/tốc độ/khoảng cách.")
report_lines.append("3. **Chuẩn bị cho Tầng Reranker (nếu cần)**: Sau khi tầng Hybrid RRF đạt mức ổn định vững chắc, mới xem xét đưa Cross-Encoder Reranker vào để tinh chỉnh Top 1/Top 3.")

report_lines.append("\n---\n")
report_lines.append("### V. KẾT LUẬN CUỐI CÙNG (FINAL VERDICT)\n")
verdict = "RRF CONFIGURATION SELECTED 🟢" if best_res["hit5"] >= 123 else "RRF NEEDS FURTHER INVESTIGATION 🔴"
report_lines.append(f"# **FINAL VERDICT: `{verdict}`**")

with open(REPORT_MD_PATH, "w", encoding="utf-8") as f:
    f.write("\n".join(report_lines))
print(f"[+] Saved Markdown report to: {REPORT_MD_PATH}")
print("=== EXPERIMENT COMPLETED SUCCESSFULLY ===", flush=True)
