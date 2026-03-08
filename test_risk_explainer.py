# ════════════════════════════════════════════════════════
# FILE: test_risk_explainer.py  (save in nyaya-setu-1/ root)
# RUN:  python test_risk_explainer.py
# (uvicorn does NOT need to be running)
# ════════════════════════════════════════════════════════

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend"))

PASS = 0
FAIL = 0

def check(name, condition, detail=""):
    global PASS, FAIL
    if condition:
        print(f"  ✅ {name}")
        PASS += 1
    else:
        print(f"  ❌ {name}" + (f"  → {detail}" if detail else ""))
        FAIL += 1

HIGH_RISK_CLAUSES = [
    {"clause_type": "bond_period",   "risk_level": "high",
     "text": "Employee agrees to serve for 3 years. Penalty for early exit: Rs 2,00,000.",
     "explanation": "3 years is a significant commitment"},
    {"clause_type": "non_compete",   "risk_level": "high",
     "text": "Cannot join any competitor for 2 years after leaving.",
     "explanation": "Restricts livelihood"},
    {"clause_type": "notice_period", "risk_level": "high",
     "text": "Employee must serve 90-day notice before resignation.",
     "explanation": "Above industry standard"},
    {"clause_type": "variable_pay",  "risk_level": "medium",
     "text": "25% of CTC is performance-linked variable pay.",
     "explanation": "Variable income risk"},
    {"clause_type": "leave_policy",  "risk_level": "low",
     "text": "24 days paid annual leave.", "explanation": "Above minimum"},
]

HIGH_RISK_DOC = """
EMPLOYMENT AGREEMENT — ABC Technologies Pvt Ltd
Notice Period: Employee must serve 90-day notice before resignation.
Service Bond: 3 years minimum. Penalty for early exit: Rs 2,00,000.
Non-Compete: Cannot join competitors for 2 years after leaving.
Leave: 24 days paid annual leave.
CTC: Rs 8,00,000. Variable: 25% KPI-linked.
"""

print("=" * 60)
print("  UPGRADE 2 — EXPLAINABLE RISK ANALYSIS TESTS")
print("=" * 60)

# ── TEST 1: Import ─────────────────────────────────────
print("\nTest 1: Imports")
try:
    from services.risk_engine import (
        calculate_risk_score, _rule_based_score,
        _explain_clauses, CLAUSE_LEGAL_REFS,
        _score_to_level, _score_to_color,
    )
    check("risk_engine imports OK", True)
    check("CLAUSE_LEGAL_REFS has bond_period", "bond_period" in CLAUSE_LEGAL_REFS)
    check("CLAUSE_LEGAL_REFS has non_compete", "non_compete" in CLAUSE_LEGAL_REFS)
    check("Legal ref has enforceability",
          "enforceability" in CLAUSE_LEGAL_REFS["bond_period"])
except ImportError as e:
    check("risk_engine imports OK", False, str(e))
    sys.exit(1)

# ── TEST 2: Legal reference DB ─────────────────────────
print("\nTest 2: Legal reference database")
for ctype in ["bond_period", "non_compete", "notice_period",
              "penalty_clause", "leave_policy", "variable_pay"]:
    ref = CLAUSE_LEGAL_REFS.get(ctype, {})
    check(f"{ctype} has act+section",
          bool(ref.get("act")) and bool(ref.get("section")))

# ── TEST 3: New output fields ─────────────────────────
print("\nTest 3: calculate_risk_score new fields")
result = calculate_risk_score(HIGH_RISK_DOC, HIGH_RISK_CLAUSES)

check("Returns dict",                 isinstance(result, dict))
check("Has explained_clauses",       "explained_clauses" in result)
check("Has risk_breakdown",          "risk_breakdown" in result)
check("Has scoring_breakdown",       "scoring_breakdown" in result)
check("Has top_concerns",            "top_concerns" in result)
check("Score is int 1-10",
      isinstance(result["score"], int) and 1 <= result["score"] <= 10)
check("High-risk doc scores >= 5",   result["score"] >= 5,
      f"Got {result['score']}")

# ── TEST 4: explained_clauses structure ───────────────
print("\nTest 4: explained_clauses structure")
exp = result.get("explained_clauses", [])
check("Has explained clauses",       len(exp) > 0, f"Got {len(exp)}")

if exp:
    first = exp[0]
    check("Has clause_type",         "clause_type"      in first)
    check("Has why_risky",           "why_risky"        in first)
    check("Has legal_reference",     "legal_reference"  in first)
    check("Has recommendation",      "recommendation"   in first)
    check("Has negotiable bool",     isinstance(first.get("negotiable"), bool))
    check("Has severity_score 1-10",
          1 <= first.get("severity_score", 0) <= 10,
          f"Got {first.get('severity_score')}")
    check("Has red_flag bool",       isinstance(first.get("red_flag"), bool))

    legal = first.get("legal_reference", {})
    check("Legal ref has act",       bool(legal.get("act")))
    check("Legal ref has section",   bool(legal.get("section")))
    check("Legal ref has summary",   bool(legal.get("summary")))
    check("Legal ref has enforceability", bool(legal.get("enforceability")))

    print(f"\n  First clause: {first.get('clause_type')} "
          f"(severity={first.get('severity_score')})")
    print(f"  Law cited: {legal.get('act')} {legal.get('section')}")
    print(f"  Why risky: {first.get('why_risky','')[:100]}...")
    print(f"  Recommendation: {first.get('recommendation','')[:100]}...")

# ── TEST 5: risk_breakdown ────────────────────────────
print("\nTest 5: risk_breakdown structure")
rb = result.get("risk_breakdown", {})
check("Has total_clauses",      "total_clauses"     in rb)
check("Has high_risk count",    "high_risk"          in rb)
check("Has medium_risk count",  "medium_risk"        in rb)
check("Has low_risk count",     "low_risk"           in rb)
check("Has negotiable_count",   "negotiable_count"   in rb)
check("Has red_flag_count",     "red_flag_count"     in rb)
check("Total matches input",    rb.get("total_clauses") == len(HIGH_RISK_CLAUSES),
      f"Expected {len(HIGH_RISK_CLAUSES)}, got {rb.get('total_clauses')}")
check("High count = 3",         rb.get("high_risk") == 3,
      f"Got {rb.get('high_risk')}")
print(f"  Breakdown: {rb}")

# ── TEST 6: scoring_breakdown ─────────────────────────
print("\nTest 6: scoring_breakdown")
sb = result.get("scoring_breakdown", {})
check("Has rule_score",         sb.get("rule_score") is not None)
check("Has final_score",        sb.get("final_score") is not None)
check("Has method",             sb.get("method") in ("hybrid","rule_only","llm_only"))
print(f"  Scoring: rule={sb.get('rule_score')} llm={sb.get('llm_score')} "
      f"final={sb.get('final_score')} method={sb.get('method')}")

# ── TEST 7: top_concerns ─────────────────────────────
print("\nTest 7: top_concerns")
tc = result.get("top_concerns", [])
check("Has top_concerns list",  isinstance(tc, list))
check("Max 3 concerns",         len(tc) <= 3, f"Got {len(tc)}")
check("At least 1 concern",     len(tc) >= 1, f"Got {len(tc)}")
if tc:
    print(f"  Top concerns:")
    for c in tc:
        print(f"    • {c}")

# ── TEST 8: Backward compatibility ───────────────────
print("\nTest 8: Backward compatibility (old fields still exist)")
check("Has risky_clauses list", isinstance(result.get("risky_clauses"), list))
check("Has safe_clauses list",  isinstance(result.get("safe_clauses"),  list))
check("Has scoring_method str", isinstance(result.get("scoring_method"), str))
check("Has rule_score",         result.get("rule_score") is not None)

# ── TEST 9: Edge cases ────────────────────────────────
print("\nTest 9: Edge cases")
empty = calculate_risk_score("")
check("Empty doc → default",    empty.get("scoring_method") == "default")
check("Default has explained",  "explained_clauses" in empty)
check("Default explained = []", empty.get("explained_clauses") == [])

no_clauses = calculate_risk_score(HIGH_RISK_DOC, [])
check("No clauses still works", "score" in no_clauses)

# ── RESULTS ───────────────────────────────────────────
total = PASS + FAIL
print("\n" + "=" * 60)
print(f"  {PASS}/{total} tests passed")
if FAIL == 0:
    print("  ✅ Upgrade 2 (Explainable Risk) is working!")
    print()
    print("  Each clause now has:")
    print("  → exact Indian law citation (Act + Section)")
    print("  → plain English why_risky explanation")
    print("  → negotiation recommendation")
    print("  → red_flag if potentially illegal")
    print()
    print("  Ready for Phase 3 — Streamlit Frontend! 🚀")
else:
    print(f"  ❌ {FAIL} failed — check errors above")
print("=" * 60)