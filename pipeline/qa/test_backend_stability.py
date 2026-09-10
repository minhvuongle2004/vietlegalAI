import os
import sys
import json
import requests
from pathlib import Path

# Windows encoding fix
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

print("=" * 80)
print("TRACK 2: BACKEND STABILITY & RESILIENCE AUDIT")
print("=" * 80)

results = []

def test_check(name, passed, details=""):
    status = "PASS 🟢" if passed else "FAIL 🔴"
    print(f"[{status}] {name}")
    if details:
        print(f"        {details}")
    results.append({"name": name, "passed": passed, "details": details})

# 1. Test /health (Liveness)
res = client.get("/health")
test_check(
    "Liveness Probe (/health)",
    res.status_code == 200 and res.json().get("status") == "alive",
    f"Status: {res.status_code}, Body: {res.json()}"
)

# 2. Test /api/v1/health (Readiness)
res = client.get("/api/v1/health")
data = res.json() if res.status_code == 200 else {}
comps = data.get("components", {})
test_check(
    "Readiness Probe (/api/v1/health)",
    res.status_code == 200 and data.get("status") in ["healthy", "degraded"],
    f"Status: {res.status_code}, Qdrant: {comps.get('qdrant')}, Reranker: {comps.get('reranker', {}).get('device')}, Supabase: {comps.get('supabase')}"
)

# 3. Test Malformed Request: Empty Body
res = client.post("/api/v1/chat/completions", json={})
test_check(
    "Malformed Request: Empty JSON body",
    res.status_code == 422,
    f"HTTP {res.status_code} (Pydantic validation caught missing fields)"
)

# 4. Test Malformed Request: Empty Query string
res = client.post("/api/v1/chat/completions", json={"query": ""})
test_check(
    "Malformed Request: Empty query string",
    res.status_code == 422,
    f"HTTP {res.status_code} (min_length=2 enforced by schema)"
)

# 5. Test Malformed Request: Query string with 1 char
res = client.post("/api/v1/chat/completions", json={"query": "a"})
test_check(
    "Malformed Request: Single character query",
    res.status_code == 422,
    f"HTTP {res.status_code} (Pydantic rejected single char)"
)

# 6. Test Unauthenticated access to protected conversation endpoints
res = client.get("/api/v1/conversations")
test_check(
    "Auth Check: GET /conversations without token",
    res.status_code in [401, 403],
    f"HTTP {res.status_code} (Properly blocks unauthenticated request)"
)

# 7. Test Protected endpoint with malformed bearer token
res = client.get("/api/v1/conversations", headers={"Authorization": "Bearer invalid_token_xyz"})
test_check(
    "Auth Check: GET /conversations with invalid token",
    res.status_code in [401, 403],
    f"HTTP {res.status_code} (Properly rejects forged/expired JWT)"
)

# 8. Test Rate Limiter configuration
from backend.app.core.config import settings
test_check(
    f"Rate Limiter Configuration ({settings.RATE_LIMIT_PER_MINUTE}/min)",
    settings.RATE_LIMIT_PER_MINUTE > 0,
    f"Configured limit: {settings.RATE_LIMIT_PER_MINUTE} requests/minute per IP"
)

# Summary
passed_cnt = sum(1 for r in results if r["passed"])
print(f"\n[+] Stability Test Completed: {passed_cnt}/{len(results)} PASSED")

OUT_JSON = PROJECT_ROOT / "data" / "qa" / "backend_stability_results.json"
OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
with open(OUT_JSON, "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
print(f"[+] Saved test results to: {OUT_JSON}")
