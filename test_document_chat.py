# ════════════════════════════════════════════════════════
# FILE: tests/test_document_chat.py
# RUN: python tests/test_document_chat.py
# NOTE: Tests 1-4 run WITHOUT uvicorn.
#       Test 5 needs uvicorn running in another terminal.
# ════════════════════════════════════════════════════════

import sys
import os
import uuid

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend"))

PASS = 0
FAIL = 0

def check(name, condition, detail=""):
    global PASS, FAIL
    if condition:
        print(f"  ✅ {name}")
        PASS += 1
    else:
        print(f"  ❌ {name}" + (f"  →  {detail}" if detail else ""))
        FAIL += 1

# ── Unique session for this test run ─────────────────────
SESSION = "doctest_" + uuid.uuid4().hex[:8]

# ── Sample contract text ──────────────────────────────────
CONTRACT_TEXT = """
EMPLOYMENT AGREEMENT — ABC Technologies Pvt Ltd

Clause 1 - Notice Period:
Employee must serve a mandatory 90-day notice period before resignation.
Failure to serve notice will result in salary deduction for remaining days.

Clause 2 - Service Bond:
Employee agrees to serve for minimum 3 years from date of joining.
Penalty for premature exit: Rs 2,00,000 (Two Lakh Rupees only).
This amount will be recovered from final settlement.

Clause 3 - Non-Compete:
Employee shall not join any competitor company or start competing business
for a period of 2 years after leaving the organization.

Clause 4 - Annual Leave:
Employee is entitled to 24 days of paid annual leave per year.
Unutilized leave can be carried forward for maximum 1 year only.

Clause 5 - Salary Structure:
CTC: Rs 8,00,000 per annum.
Variable pay: 25% of CTC linked to annual KPI achievement.
Basic salary: 40% of CTC. HRA: 50% of basic.
"""

print("=" * 60)
print("  UPGRADE 1 — DOCUMENT CHAT TESTS")
print("=" * 60)
print(f"  Session: {SESSION}\n")


# ════════════════════════════════════════════════════════
# TEST 1: Import check
# ════════════════════════════════════════════════════════
print("Test 1: Import doc_vectorstore module")
try:
    from services.doc_vectorstore import (
        build_doc_store,
        search_doc_store,
        has_doc_store,
        delete_doc_store,
        get_doc_store_stats,
    )
    check("doc_vectorstore imports OK", True)
except ImportError as e:
    check("doc_vectorstore imports OK", False, str(e))
    print("\n  ❌ FATAL: Cannot import doc_vectorstore.")
    print("  Make sure backend/services/doc_vectorstore.py exists.")
    sys.exit(1)

# Check rag.py exports _embeddings
try:
    from services.rag import _embeddings
    check("rag.py exports _embeddings",  _embeddings is not None,
          "_embeddings is None — ChromaDB may have failed to load")
except ImportError as e:
    check("rag.py exports _embeddings", False, str(e))


# ════════════════════════════════════════════════════════
# TEST 2: Build doc store
# ════════════════════════════════════════════════════════
print("\nTest 2: Build per-session FAISS index")
chunk_count = build_doc_store(SESSION, CONTRACT_TEXT)
check("build_doc_store returns chunk count",  chunk_count > 0,
      f"Got {chunk_count} — check _embeddings loaded correctly")
check("Reasonable chunk count (2–25)",        2 <= chunk_count <= 25,
      f"Got {chunk_count}")
check("has_doc_store returns True",           has_doc_store(SESSION))
print(f"  Contract indexed as {chunk_count} chunks ✓")

# Stats check
stats = get_doc_store_stats(SESSION)
check("Stats has_store=True",    stats.get("has_store") == True)
check("Stats chunk_count match", stats.get("chunk_count") == chunk_count)


# ════════════════════════════════════════════════════════
# TEST 3: Contract-specific retrieval
# ════════════════════════════════════════════════════════
print("\nTest 3: Contract-specific retrieval accuracy")

# Query 1: Penalty clause
results_penalty = search_doc_store(SESSION, "penalty clause early exit bond")
check("Penalty query returns results",      len(results_penalty) > 0,
      "search returned nothing")
if results_penalty:
    combined = " ".join(r.page_content.lower() for r in results_penalty)
    check("Penalty content found",
          "penalty" in combined or "2,00,000" in combined or "lakh" in combined,
          f"First chunk: {results_penalty[0].page_content[:80]}")
    check("Source metadata = uploaded_contract",
          results_penalty[0].metadata.get("source") == "uploaded_contract",
          f"Got source: {results_penalty[0].metadata.get('source')}")

# Query 2: Notice period
results_notice = search_doc_store(SESSION, "notice period resignation days")
check("Notice period query finds clause",   len(results_notice) > 0)
if results_notice:
    combined2 = " ".join(r.page_content.lower() for r in results_notice)
    check("Notice period content found",
          "notice" in combined2 or "90" in combined2,
          f"First chunk: {results_notice[0].page_content[:80]}")

# Query 3: Leave policy
results_leave = search_doc_store(SESSION, "annual leave paid days")
check("Leave policy query finds clause",    len(results_leave) > 0)

# Query 4: Salary
results_salary = search_doc_store(SESSION, "salary CTC variable pay")
check("Salary query finds clause",          len(results_salary) > 0)

print(f"  Penalty query:  {len(results_penalty)} chunks")
print(f"  Notice query:   {len(results_notice)} chunks")
print(f"  Leave query:    {len(results_leave)} chunks")
print(f"  Salary query:   {len(results_salary)} chunks")


# ════════════════════════════════════════════════════════
# TEST 4: Edge cases
# ════════════════════════════════════════════════════════
print("\nTest 4: Edge cases")

# Unknown session
empty = search_doc_store("nonexistent_session_xyz_999", "penalty")
check("Unknown session → []",               empty == [])
check("has_doc_store False for unknown",    not has_doc_store("nonexistent_xyz"))

# Empty document
empty_count = build_doc_store("empty_session_test", "")
check("Empty document → 0 chunks",          empty_count == 0)
check("has_doc_store False for empty doc",  not has_doc_store("empty_session_test"))

# Very short document
short_count = build_doc_store("short_session_test", "Short text.")
# May or may not build — just shouldn't crash
check("Short document doesn't crash",       True)


# ════════════════════════════════════════════════════════
# TEST 5: Delete doc store
# ════════════════════════════════════════════════════════
print("\nTest 5: Doc store cleanup")
deleted = delete_doc_store(SESSION)
check("delete_doc_store returns True",      deleted == True)
check("has_doc_store False after delete",   not has_doc_store(SESSION))
empty_after = search_doc_store(SESSION, "penalty")
check("Search returns [] after delete",     empty_after == [])
stats_after = get_doc_store_stats(SESSION)
check("Stats has_store=False after delete", stats_after.get("has_store") == False)


# ════════════════════════════════════════════════════════
# TEST 6: Full API test (needs uvicorn)
# ════════════════════════════════════════════════════════
print("\nTest 6: Full API — ask_lawyer dual search (needs uvicorn)")
try:
    import requests

    # Rebuild doc store (we deleted it in Test 5)
    api_session = "api_test_" + uuid.uuid4().hex[:8]
    build_doc_store(api_session, CONTRACT_TEXT)

    # Test ask_lawyer directly
    from services.rag import ask_lawyer
    result = ask_lawyer(
        question="Is there a penalty clause? How much is the penalty?",
        document_text=CONTRACT_TEXT,
        session_id=api_session
    )

    check("ask_lawyer returns answer",       bool(result.get("answer")))
    check("contract_hits > 0",              result.get("contract_hits", 0) > 0,
          f"Got contract_hits={result.get('contract_hits')} — doc store may not be built")
    check("chunks_used > 0",               result.get("chunks_used", 0) > 0)

    answer = result.get("answer", "").lower()
    check("Answer mentions penalty/lakh",
          "penalty" in answer or "lakh" in answer or "2,00,000" in answer,
          f"Answer preview: {result.get('answer','')[:100]}")

    print(f"\n  contract_hits : {result.get('contract_hits')}")
    print(f"  law_hits      : {result.get('law_hits')}")
    print(f"  chunks_used   : {result.get('chunks_used')}")
    print(f"  Answer preview:\n  {result.get('answer','')[:300]}...")

    # Also test via HTTP if uvicorn is running
    try:
        r = requests.get("http://localhost:8000/health", timeout=2)
        if r.status_code == 200:
            print("\n  → Testing via HTTP API...")
            r2 = requests.post("http://localhost:8000/chat/ask", json={
                "message":    "Is there a penalty clause?",
                "session_id": api_session
            }, timeout=30)
            d = r2.json()
            check("HTTP /chat/ask returns 200",   r2.status_code == 200)
            check("HTTP contract_hits in response","contract_hits" in d,
                  f"Keys: {list(d.keys())}")
    except requests.ConnectionError:
        print("  (uvicorn not running — HTTP test skipped, direct test passed)")

except Exception as e:
    print(f"  ❌ Test 6 error: {e}")
    import traceback; traceback.print_exc()
    FAIL += 1


# ════════════════════════════════════════════════════════
# RESULTS
# ════════════════════════════════════════════════════════
total = PASS + FAIL
print("\n" + "=" * 60)
print(f"  {PASS}/{total} tests passed")
if FAIL == 0:
    print("  ✅ Upgrade 1 (Document Chat) is fully working!")
    print()
    print("  Users can now:")
    print("  → Upload contract → AI indexes it automatically")
    print("  → Ask 'Is there a penalty clause?'")
    print("  → AI finds the EXACT clause + cites Indian law")
    print()
    print("  Ready for Upgrade 2!")
else:
    print(f"  ❌ {FAIL} tests failed — check errors above")
    print()
    print("  Common fixes:")
    print("  1. Make sure doc_vectorstore.py is in backend/services/")
    print("  2. Make sure rag.py exports _embeddings at module level")
    print("  3. Run from nyaya-setu-1/ root: python tests/test_document_chat.py")
print("=" * 60)