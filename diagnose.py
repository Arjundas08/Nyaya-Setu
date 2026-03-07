import requests
import sys

BASE = "http://localhost:8000"

print("=" * 55)
print("  NYAYA-SETU DIAGNOSTIC TOOL")
print("=" * 55)

# ── Check 1: Is server running at all? ────────────────
print("\n🔍 CHECK 1: Is uvicorn running?")
try:
    r = requests.get(BASE, timeout=3)
    print(f"  ✅ Server is UP — status {r.status_code}")
    print(f"  Response: {r.text[:200]}")
except requests.exceptions.ConnectionError:
    print("  ❌ CANNOT CONNECT TO SERVER")
    print("  → Open a NEW terminal and run:")
    print("     cd nyaya-setu-1")
    print("     cd backend")
    print("     uvicorn main:app --reload")
    print("\n  Then re-run this diagnostic.")
    sys.exit(1)
except Exception as e:
    print(f"  ❌ Error: {e}")
    sys.exit(1)

# ── Check 2: What routes exist? ───────────────────────
print("\n🔍 CHECK 2: What routes are registered?")
try:
    r = requests.get(f"{BASE}/openapi.json", timeout=5)
    if r.status_code == 200:
        paths = list(r.json().get("paths", {}).keys())
        print(f"  Found {len(paths)} routes:")
        for p in sorted(paths):
            print(f"    {p}")
    else:
        print(f"  ❌ Could not get routes: {r.status_code}")
except Exception as e:
    print(f"  ❌ Error: {e}")

# ── Check 3: Test each endpoint individually ──────────
print("\n🔍 CHECK 3: Individual endpoint checks")

endpoints = [
    ("GET",    "/",                     None),
    ("GET",    "/health",               None),
    ("GET",    "/analyze/stats",        None),
    ("GET",    "/analyze/doc/test123",  None),
    ("POST",   "/analyze/risk",         {"session_id": "test123", "force_reanalyze": False}),
    ("DELETE", "/analyze/doc/test123",  None),
    ("POST",   "/chat/ask",             {"message": "hi", "session_id": "test"}),
    ("POST",   "/chat/salary",          {"ctc_annual": 600000}),
]

for method, path, body in endpoints:
    try:
        if method == "GET":
            resp = requests.get(f"{BASE}{path}", timeout=5)
        elif method == "POST":
            resp = requests.post(f"{BASE}{path}", json=body, timeout=5)
        elif method == "DELETE":
            resp = requests.delete(f"{BASE}{path}", timeout=5)

        status = resp.status_code
        icon = "✅" if status < 500 else "❌"
        print(f"  {icon} {method} {path} → {status}")
        if status == 404:
            print(f"       ↳ Route does NOT exist in main.py")
        elif status == 422:
            print(f"       ↳ Validation error: {resp.text[:100]}")
        elif status == 500:
            print(f"       ↳ SERVER ERROR: {resp.text[:200]}")
    except Exception as e:
        print(f"  ❌ {method} {path} → FAILED: {e}")

print("\n" + "=" * 55)
print("  Send the output above — I will fix it immediately.")
print("=" * 55)