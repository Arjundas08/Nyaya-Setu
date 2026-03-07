import requests
import os
import sys

BASE   = "http://localhost:8000"
PASS   = 0
FAIL   = 0

def check(name, condition, detail=""):
    global PASS, FAIL
    if condition:
        print(f"  ✅ {name}")
        PASS += 1
    else:
        print(f"  ❌ {name}" + (f"  →  {detail}" if detail else ""))
        FAIL += 1

print("=" * 60)
print("  ANALYZE ROUTES — PRODUCTION TESTS")
print("=" * 60)

# ── TEST 1: Stats endpoint ─────────────────────────────
print("\nTest 1: Stats endpoint")
r = requests.get(f"{BASE}/analyze/stats")
d = r.json()
check("Status 200",              r.status_code == 200)
check("Has active_sessions",     "active_sessions" in d)
check("Has max_sessions",        "max_sessions" in d)

# ── TEST 2: Bad file type rejected ────────────────────
print("\nTest 2: Invalid file type rejection")
r = requests.post(
    f"{BASE}/analyze/upload",
    files={"file": ("test.txt", b"hello world", "text/plain")}
)
check("Text file rejected with 400", r.status_code == 400)
check("Error message helpful",       "not supported" in r.json().get("detail","").lower())

# ── TEST 3: File too large ─────────────────────────────
print("\nTest 3: Oversized file rejection")
big_data = b"x" * (11 * 1024 * 1024)   # 11 MB
r = requests.post(
    f"{BASE}/analyze/upload",
    files={"file": ("big.jpg", big_data, "image/jpeg")}
)
check("11MB file rejected with 413",  r.status_code == 413)

# ── TEST 4: Session auto-generated ───────────────────
print("\nTest 4: Auto session_id generation")
# Create a minimal valid JPEG (1x1 pixel)
tiny_jpg = (
    b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00"
    b"\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t"
    b"\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a"
    b"\x1f\x1e\x1d\x1a\x1c\x1c $.' \",#\x1c\x1c(7),01444\x1f\'9=82<.342\x1eZ..."
    b"\xff\xd9"
)
# Note: This tiny JPEG will fail OCR — we're testing session_id auto-gen behavior
r = requests.post(
    f"{BASE}/analyze/upload",
    files={"file": ("doc.jpg", tiny_jpg, "image/jpeg")}
)
# Either succeeds or fails with 422 (unreadable image) — NOT 500
check("Does not crash server",        r.status_code in [200, 422])
check("Returns session_id if success",r.status_code != 200 or "session_id" in r.json())

# ── TEST 5: Document not found ────────────────────────
print("\nTest 5: Missing session handling")
r = requests.get(f"{BASE}/analyze/doc/nonexistent-session-id-99999")
d = r.json()
check("Returns 200 (not 500)",        r.status_code == 200)
check("has_document is False",        d.get("has_document") == False)
check("document_text is empty",       d.get("document_text") == "")

# ── TEST 6: /risk without upload ─────────────────────
print("\nTest 6: Risk endpoint without document")
r = requests.post(f"{BASE}/analyze/risk",
    json={"session_id": "fake-session-99999", "force_reanalyze": False})
check("Returns 404 for missing session", r.status_code == 404)
check("Clear error message",             "not found" in r.json().get("detail","").lower())

# ── TEST 7: Delete non-existent session ───────────────
print("\nTest 7: Delete session")
r = requests.delete(f"{BASE}/analyze/doc/doesnotexist")
d = r.json()
check("Delete returns 200",      r.status_code == 200)
check("success=False (not found)", d.get("success") == False)
check("Has helpful message",     "message" in d)

# ── RESULTS ───────────────────────────────────────────
total = PASS + FAIL
print("\n" + "=" * 60)
print(f"  {PASS}/{total} tests passed")
if FAIL == 0:
    print("  ✅ Analyze routes are production ready!")
else:
    print(f"  ❌ {FAIL} failed — fix before moving to Phase 3")
print("=" * 60)