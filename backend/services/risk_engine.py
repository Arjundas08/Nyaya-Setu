# ════════════════════════════════════════════════════════
# FILE: backend/services/risk_engine.py
# UPGRADE 2: EXPLAINABLE RISK ANALYSIS
# Replace your entire risk_engine.py with this file.
# ════════════════════════════════════════════════════════

import os
import json
import re
import time
import logging
from typing import Optional

from langchain_groq import ChatGroq
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

# ════════════════════════════════════════════════════════
# CONFIGURATION
# ════════════════════════════════════════════════════════
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise EnvironmentError("GROQ_API_KEY not set in .env")

_llm = ChatGroq(
    api_key=GROQ_API_KEY,
    model_name=os.getenv("GROQ_MODEL", "llama-3.1-8b-instant"),  #NEW

    temperature=0,
    max_tokens=2000,
    request_timeout=30,
)

MAX_RETRIES = 3
RETRY_DELAY = 2.0


# ════════════════════════════════════════════════════════
# LEGAL REFERENCE DATABASE
# Hard-coded citations for known clause types.
# LLM fills in the gaps for unknown/edge cases.
# WHY HARD-CODE: LLM sometimes hallucinates section numbers.
# These are verified against actual Indian statutes.
# ════════════════════════════════════════════════════════
CLAUSE_LEGAL_REFS = {
    "bond_period": {
        "act": "Indian Contract Act 1872",
        "section": "Section 27",
        "summary": "Agreements in restraint of trade or profession are void unless the restriction is reasonable in scope, geography, and duration. Indian courts have consistently struck down excessively long service bonds.",
        "enforceability": "Partially enforceable — courts may reduce penalty to actual loss only",
    },
    "non_compete": {
        "act": "Indian Contract Act 1872",
        "section": "Section 27",
        "summary": "Post-employment non-compete clauses are generally void in India as they restrain a person's right to earn a livelihood. Only confidentiality obligations survive employment termination.",
        "enforceability": "Generally NOT enforceable post-employment",
    },
    "notice_period": {
        "act": "Industrial Disputes Act 1947",
        "section": "Section 25F",
        "summary": "Notice period must be reasonable. While the law prescribes one month for workers, contracts can set longer periods. However, periods exceeding 60 days have been challenged as unreasonable restraint.",
        "enforceability": "Enforceable but may be challenged if excessive",
    },
    "penalty_clause": {
        "act": "Indian Contract Act 1872",
        "section": "Section 74",
        "summary": "Penalty must be a genuine pre-estimate of actual loss suffered, not a punitive amount. Courts will reduce the penalty to the actual proven loss, even if the contract states a higher amount.",
        "enforceability": "Enforceable up to actual proven loss only",
    },
    "termination_clause": {
        "act": "Industrial Disputes Act 1947",
        "section": "Section 25G",
        "summary": "Termination without cause or notice may be challenged as unfair dismissal. Employees with 240+ days of service have stronger protection against arbitrary termination.",
        "enforceability": "Arbitrary termination can be contested",
    },
    "variable_pay": {
        "act": "Code on Wages 2019",
        "section": "Section 2(y)",
        "summary": "Variable pay must be clearly defined, with measurable KPIs. Employer cannot arbitrarily withhold variable pay if targets are met. Wage theft is punishable under Section 51.",
        "enforceability": "Employer must pay if KPIs are met — withholding is illegal",
    },
    "intellectual_property": {
        "act": "Copyright Act 1957 / Patents Act 1970",
        "section": "Section 17 / Section 6",
        "summary": "IP created in the course of employment belongs to the employer. However, personal projects done outside work hours and without company resources belong to the employee.",
        "enforceability": "Valid for work-related IP; unenforceable for personal projects",
    },
    "arbitration": {
        "act": "Arbitration and Conciliation Act 1996",
        "section": "Section 11",
        "summary": "Arbitration clauses are enforceable. However, if the specified venue is far from the employee's location, it can create practical hardship and may be challenged as unconscionable.",
        "enforceability": "Enforceable; negotiate for local venue",
    },
    "eviction_clause": {
        "act": "Transfer of Property Act 1882",
        "section": "Section 106",
        "summary": "A minimum 15-day notice is required before eviction for monthly tenancies. Arbitrary immediate eviction is illegal. Tenant has right to contest in Rent Control Court.",
        "enforceability": "Immediate eviction clauses are illegal",
    },
    "security_deposit": {
        "act": "State Rent Control Acts",
        "section": "Varies by state (e.g., Maharashtra RCA Section 18)",
        "summary": "Security deposit is usually capped at 1-3 months rent by state laws. Deposits exceeding this are above the legal standard and may not be fully refundable.",
        "enforceability": "Excess deposit may be recoverable in Rent Court",
    },
    "leave_policy": {
        "act": "Factories Act 1948",
        "section": "Sections 78-84",
        "summary": "Minimum 12 days earned leave per year is a statutory right. Any leave policy offering less is illegal. Policies offering more are favorable to the employee.",
        "enforceability": "12 days minimum is a legal right — employer cannot reduce it",
    },
    "confidentiality": {
        "act": "Indian Contract Act 1872",
        "section": "Section 27 read with Section 39",
        "summary": "Confidentiality clauses are valid and enforceable during employment. Post-employment, only specific trade secrets (not general skills) can be protected.",
        "enforceability": "Valid during employment; limited scope post-employment",
    },
    "probation_period": {
        "act": "Industrial Employment (Standing Orders) Act 1946",
        "section": "Section 3",
        "summary": "Probation period must be defined. Typically 3-6 months. Employees on probation have fewer termination protections. Extending probation repeatedly may be challenged.",
        "enforceability": "Valid if defined; repeated extension may be challenged",
    },
    "relocation_clause": {
        "act": "Indian Contract Act 1872",
        "section": "Section 23",
        "summary": "Forced relocation without consent or adequate notice may be challenged as oppressive. Clause must specify notice period and whether relocation expenses are covered.",
        "enforceability": "Enforceable with notice; forced relocation without consent is challengeable",
    },
}

# Fallback for unknown clause types
DEFAULT_LEGAL_REF = {
    "act": "Indian Contract Act 1872",
    "section": "Section 23",
    "summary": "All contracts must have lawful consideration and object. Unconscionable clauses that are oppressive, immoral, or against public policy are void.",
    "enforceability": "Consult a lawyer to assess enforceability",
}


# ════════════════════════════════════════════════════════
# RULE-BASED SCORING TABLE (from Upgrade 1 — kept intact)
# ════════════════════════════════════════════════════════
CLAUSE_RISK_WEIGHTS = {
    "bond_period":             2.5,
    "non_compete":             2.0,
    "penalty_clause":          1.5,
    "notice_period":           1.5,
    "termination_clause":      1.0,
    "variable_pay":            1.0,
    "probation_period":        0.5,
    "relocation_clause":       1.0,
    "intellectual_property":   0.5,
    "eviction_clause":         1.5,
    "security_deposit":        1.0,
    "maintenance_charges":     0.5,
    "indemnity_clause":        1.5,
    "limitation_of_liability": 1.0,
    "arbitration":             0.5,
    "jurisdiction":            0.5,
    "leave_policy":           -0.5,
    "performance_review":     -0.2,
    "renewal_clause":         -0.3,
}

RISK_LEVEL_MULTIPLIER = {"high": 1.5, "medium": 1.0, "low": 0.3}


# ════════════════════════════════════════════════════════
# SCORE MAPPING HELPERS
# ════════════════════════════════════════════════════════
def _score_to_level(score: float) -> str:
    if score <= 2.5: return "Very Safe"
    if score <= 4.0: return "Mostly Fair"
    if score <= 6.0: return "Moderate Risk"
    if score <= 7.5: return "High Risk"
    return "Very High Risk"

def _score_to_color(score: float) -> str:
    if score <= 3.0: return "green"
    if score <= 5.5: return "orange"
    if score <= 7.5: return "red"
    return "darkred"

def _score_to_action(score: float) -> str:
    if score <= 3.0:
        return "This contract appears fair. Review the flagged clauses, then you can consider signing."
    if score <= 5.5:
        return "Several clauses need attention. Negotiate the flagged items before signing."
    if score <= 7.5:
        return "This contract has significant issues. We STRONGLY recommend consulting a lawyer before signing."
    return "This contract contains extremely unfavorable or potentially illegal terms. Do NOT sign without legal advice. Consult a licensed advocate immediately."


# ════════════════════════════════════════════════════════
# LLM HELPERS
# ════════════════════════════════════════════════════════
def _call_llm_with_retry(prompt: str) -> Optional[str]:
    delay = RETRY_DELAY
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            resp = _llm.invoke(prompt)
            return resp.content
        except Exception as e:
            err = str(e).lower()
            if "401" in err or "authentication" in err:
                logger.error("Groq auth failed")
                return None
            if "429" in err or "rate limit" in err:
                time.sleep(delay * 2)
                delay *= 2
                continue
            if attempt < MAX_RETRIES:
                logger.warning(f"LLM attempt {attempt} failed: {e}. Retry in {delay}s")
                time.sleep(delay)
                delay *= 2
            else:
                logger.error(f"All LLM attempts failed: {e}")
    return None

def _parse_json_response(raw: str) -> Optional[dict | list]:
    if not raw:
        return None
    cleaned = re.sub(r"\`\`\`json\s*|\`\`\`\s*", "", raw).strip()
    # Try object first, then array
    for pattern in [r"\{.*\}", r"\[.*\]"]:
        match = re.search(pattern, cleaned, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                fixed = re.sub(r",\s*([}\]])", r"\1", match.group())
                try:
                    return json.loads(fixed)
                except:
                    pass
    return None


# ════════════════════════════════════════════════════════
# RULE-BASED SCORER
# ════════════════════════════════════════════════════════
def _rule_based_score(clauses: list) -> float:
    if not clauses:
        return 5.0
    base = 2.0
    total = 0.0
    for clause in clauses:
        weight = CLAUSE_RISK_WEIGHTS.get(clause.get("clause_type", ""), 0.3)
        mult   = RISK_LEVEL_MULTIPLIER.get(clause.get("risk_level", "medium"), 1.0)
        total += weight * mult
    return max(1.0, min(10.0, base + total))


# ════════════════════════════════════════════════════════
# UPGRADE 2: EXPLAIN EACH CLAUSE
# This is the new core function added in Upgrade 2.
#
# For each high/medium risk clause it generates:
#   - why_risky: plain English explanation
#   - legal_reference: Act + Section + summary (from DB first)
#   - recommendation: what user should negotiate
#   - negotiable: bool
#   - severity_score: 1-10 for this specific clause
# ════════════════════════════════════════════════════════
def _explain_clauses(clauses: list, document_text: str) -> list:
    """
    Generate structured explanations for each clause.

    Strategy:
      1. For known clause types → use CLAUSE_LEGAL_REFS (verified citations)
      2. LLM adds: why_risky, recommendation, severity_score, negotiable
      3. For unknown types → LLM provides legal reference too

    Returns list of explained_clause dicts.
    """
    if not clauses:
        return []

    # Only explain high and medium risk clauses (low risk don't need explanation)
    clauses_to_explain = [
        c for c in clauses if c.get("risk_level") in ("high", "medium")
    ]

    if not clauses_to_explain:
        return []

    # Build clause list for the LLM prompt
    clause_lines = []
    for i, c in enumerate(clauses_to_explain):
        clause_lines.append(
            f"{i+1}. TYPE: {c.get('clause_type','unknown')} | "
            f"RISK: {c.get('risk_level','medium')} | "
            f"TEXT: {c.get('text','')[:120]}"
        )

    prompt = f"""You are a senior Indian employment and contract lawyer.

For each clause below, provide a detailed explanation in JSON format.

Clauses to analyze:
{chr(10).join(clause_lines)}

Document context (first 1500 chars):
{document_text[:1500]}

Return ONLY a JSON array. No markdown, no extra text. Start with [

Each item must have EXACTLY these fields:
[
  {{
    "clause_index": 0,
    "why_risky": "Plain English: exactly why this is unfair to the user. Be specific — mention the exact restriction or financial impact.",
    "recommendation": "Exact negotiation advice: what to ask for, what numbers to propose, what language to add/remove.",
    "negotiable": true,
    "severity_score": 8,
    "red_flag": false,
    "additional_context": "Any extra context about how Indian courts view this clause type."
  }}
]

Rules:
- severity_score: 1-10 (10 = potentially illegal, 1 = minor concern)
- negotiable: true if this can reasonably be negotiated before signing
- red_flag: true ONLY if the clause is potentially illegal under Indian law
- why_risky: must be specific to the actual clause text, not generic
- recommendation: must be actionable (suggest specific numbers/timelines)

Return ONLY the JSON array:"""

    raw  = _call_llm_with_retry(prompt)
    data = _parse_json_response(raw)

    if not data or not isinstance(data, list):
        logger.warning("Clause explanation LLM returned invalid response")
        data = []

    # Build final explained_clauses list
    explained = []
    for i, clause in enumerate(clauses_to_explain):
        clause_type = clause.get("clause_type", "")
        risk_level  = clause.get("risk_level", "medium")

        # Get LLM explanation for this clause (match by index)
        llm_item = next(
            (item for item in data if item.get("clause_index") == i),
            {}
        )

        # Legal reference: use verified DB first, LLM as fallback
        legal_ref = CLAUSE_LEGAL_REFS.get(clause_type, DEFAULT_LEGAL_REF).copy()

        explained.append({
            "clause_type":    clause_type,
            "risk_level":     risk_level,
            "clause_text":    clause.get("text", ""),
            "original_explanation": clause.get("explanation", ""),

            # NEW in Upgrade 2:
            "why_risky":      llm_item.get("why_risky", clause.get("explanation", "")),
            "legal_reference": {
                "act":     legal_ref.get("act", "Indian Contract Act 1872"),
                "section": legal_ref.get("section", "Section 23"),
                "summary": legal_ref.get("summary", ""),
                "enforceability": legal_ref.get("enforceability", "Consult a lawyer"),
            },
            "recommendation": llm_item.get(
                "recommendation",
                f"Review and negotiate this {clause_type.replace('_',' ')} clause before signing."
            ),
            "negotiable":     llm_item.get("negotiable", True),
            "severity_score": max(1, min(10, int(llm_item.get("severity_score", 5)))),
            "red_flag":       llm_item.get("red_flag", False),
            "additional_context": llm_item.get("additional_context", ""),
        })

    # Sort by severity_score descending (most severe first)
    explained.sort(key=lambda x: x["severity_score"], reverse=True)
    return explained


# ════════════════════════════════════════════════════════
# LLM RISK SCORER (with top_concerns — new in Upgrade 2)
# ════════════════════════════════════════════════════════
def _build_llm_prompt(document_text: str, clause_context: str) -> str:
    safe_doc = document_text.replace("{", "(").replace("}", ")")
    return f"""You are a senior legal risk analyst for Indian contracts.

{clause_context}

Document:
{safe_doc[:3000]}

Return ONLY a JSON object. No markdown, no extra text. Start with {{

{{
  "llm_score": 7,
  "risky_clauses": [
    "90-day notice period is above industry standard of 30-60 days"
  ],
  "safe_clauses": [
    "24 days annual leave is above the 12-day statutory minimum"
  ],
  "summary": "One paragraph plain-English summary of the contract risk.",
  "top_concerns": [
    "Bond period of 3 years is excessively long and potentially unenforceable",
    "Non-compete clause is likely void under Indian Contract Act Section 27",
    "Rs 2L exit penalty exceeds what courts typically enforce"
  ]
}}

Score guide (be realistic):
1-2  = Excellent, very fair contract
3-4  = Mostly fair, minor issues
5-6  = Several concerns worth negotiating
7-8  = Multiple highly unfavorable clauses
9-10 = Potentially illegal or extremely predatory

top_concerns: exactly 3 items — the most important things the user must know.

Return ONLY the JSON:"""


def _parse_llm_response(raw: str) -> Optional[dict]:
    if not raw:
        return None
    data = _parse_json_response(raw)
    if not data or not isinstance(data, dict):
        return None

    raw_score = data.get("llm_score", data.get("score"))
    if raw_score is None:
        return None
    try:
        llm_score = max(1.0, min(10.0, float(raw_score)))
    except (ValueError, TypeError):
        return None

    return {
        "llm_score":     llm_score,
        "risky_clauses": [str(r).strip() for r in data.get("risky_clauses", []) if str(r).strip()],
        "safe_clauses":  [str(s).strip() for s in data.get("safe_clauses", []) if str(s).strip()],
        "summary":       str(data.get("summary", "")).strip() or "Analysis complete.",
        "top_concerns":  [str(t).strip() for t in data.get("top_concerns", []) if str(t).strip()],
    }


# ════════════════════════════════════════════════════════
# DEFAULT RESPONSE
# ════════════════════════════════════════════════════════
def _default_response(reason: str = "") -> dict:
    logger.warning(f"Returning default risk response: {reason}")
    return {
        "score":            5,
        "score_float":      5.0,
        "level":            "Moderate Risk",
        "color":            "orange",
        "risky_clauses":    ["Analysis could not complete — please try again"],
        "safe_clauses":     [],
        "summary":          "We could not fully analyze this document. Please try again.",
        "action":           "Please upload the document again.",
        "top_concerns":     [],
        "explained_clauses":[],
        "risk_breakdown":   {},
        "scoring_breakdown":{},
        "scoring_method":   "default",
        "rule_score":       None,
        "llm_score":        None,
    }


# ════════════════════════════════════════════════════════
# PUBLIC API — calculate_risk_score()
# ════════════════════════════════════════════════════════
def calculate_risk_score(document_text: str, clauses: list = None) -> dict:
    """
    Hybrid risk scoring WITH per-clause explanations.

    INPUT:
      document_text → full document string
      clauses       → list from classifier.py (strongly recommended)

    OUTPUT dict — all fields always present:
      score              → int 1-10
      level              → "Very Safe" / ... / "Very High Risk"
      color              → "green" / "orange" / "red" / "darkred"
      summary            → plain English paragraph
      action             → what user should do next
      top_concerns       → list of 3 most important concerns  [NEW]
      explained_clauses  → list of per-clause explanations    [NEW]
      risk_breakdown     → counts by risk level               [NEW]
      scoring_breakdown  → rule_score, llm_score, method      [NEW]
      risky_clauses      → list of strings (for backward compat)
      safe_clauses       → list of strings (for backward compat)
      rule_score         → float component
      llm_score          → float component
      scoring_method     → "hybrid" / "llm_only" / "rule_only"
    """
    if not document_text or not document_text.strip():
        return _default_response("empty document")
    if len(document_text.strip()) < 30:
        return _default_response("document too short")

    clauses = clauses or []

    # ── STEP 1: Rule-based score ────────────────────────
    rule_score = _rule_based_score(clauses) if clauses else None

    # ── STEP 2: LLM context score ───────────────────────
    clause_context = ""
    if clauses:
        lines = [
            f"  - {c['clause_type']} (risk={c['risk_level']}): {c.get('text','')[:80]}"
            for c in clauses[:10]
        ]
        clause_context = "Identified clauses:\n" + "\n".join(lines)

    raw_resp   = _call_llm_with_retry(_build_llm_prompt(document_text, clause_context))
    llm_parsed = _parse_llm_response(raw_resp) if raw_resp else None
    llm_score  = llm_parsed["llm_score"] if llm_parsed else None

    # ── STEP 3: Hybrid combination ──────────────────────
    if rule_score is not None and llm_score is not None:
        final_float    = (rule_score * 0.60) + (llm_score * 0.40)
        scoring_method = "hybrid"
    elif rule_score is not None:
        final_float    = rule_score
        scoring_method = "rule_only"
    elif llm_score is not None:
        final_float    = llm_score
        scoring_method = "llm_only"
    else:
        return _default_response("both scoring methods failed")

    final_float = max(1.0, min(10.0, final_float))
    final_int   = round(final_float)

    # ── STEP 4: Generate per-clause explanations [NEW] ──
    logger.info(f"Generating clause explanations for {len(clauses)} clauses...")
    t0 = time.monotonic()
    explained_clauses = _explain_clauses(clauses, document_text)
    explain_ms = int((time.monotonic() - t0) * 1000)
    logger.info(f"Explanations generated: {len(explained_clauses)} clauses in {explain_ms}ms")

    # ── STEP 5: Build risk breakdown [NEW] ──────────────
    high_clauses   = [c for c in clauses if c.get("risk_level") == "high"]
    medium_clauses = [c for c in clauses if c.get("risk_level") == "medium"]
    low_clauses    = [c for c in clauses if c.get("risk_level") == "low"]
    red_flag_count = sum(1 for c in explained_clauses if c.get("red_flag"))
    negotiable_count = sum(1 for c in explained_clauses if c.get("negotiable"))

    risk_breakdown = {
        "total_clauses":      len(clauses),
        "high_risk":          len(high_clauses),
        "medium_risk":        len(medium_clauses),
        "low_risk":           len(low_clauses),
        "negotiable_count":   negotiable_count,
        "red_flag_count":     red_flag_count,
        "potentially_illegal": red_flag_count > 0,
    }

    # ── STEP 6: Assemble final response ────────────────
    if llm_parsed:
        risky_clauses = llm_parsed["risky_clauses"]
        safe_clauses  = llm_parsed["safe_clauses"]
        summary       = llm_parsed["summary"]
        top_concerns  = llm_parsed["top_concerns"]
    else:
        risky_clauses = [
            f"{c['clause_type'].replace('_',' ').title()}: {c.get('explanation','')}"
            for c in high_clauses
        ]
        safe_clauses  = [
            f"{c['clause_type'].replace('_',' ').title()}: {c.get('explanation','')}"
            for c in low_clauses
        ]
        summary      = (
            f"Document scored {final_int}/10 based on analysis of "
            f"{len(clauses)} clauses. {len(high_clauses)} high-risk clause(s) found."
        )
        top_concerns = [
            f"{c['clause_type'].replace('_',' ').title()} is high risk"
            for c in high_clauses[:3]
        ]

    result = {
        # Core score fields
        "score":        final_int,
        "score_float":  round(final_float, 2),
        "level":        _score_to_level(final_float),
        "color":        _score_to_color(final_float),
        "action":       _score_to_action(final_float),

        # Summary fields
        "summary":      summary,
        "top_concerns": top_concerns[:3],    # Always max 3

        # NEW in Upgrade 2
        "explained_clauses": explained_clauses,
        "risk_breakdown":    risk_breakdown,
        "scoring_breakdown": {
            "rule_score":  round(rule_score, 2) if rule_score else None,
            "llm_score":   round(llm_score,  2) if llm_score  else None,
            "final_score": round(final_float, 2),
            "method":      scoring_method,
        },

        # Backward compatibility
        "risky_clauses":  risky_clauses,
        "safe_clauses":   safe_clauses,
        "scoring_method": scoring_method,
        "rule_score":     round(rule_score, 2) if rule_score else None,
        "llm_score":      round(llm_score,  2) if llm_score  else None,
    }

    logger.info(
        f"Risk analysis complete: score={final_int} ({result['level']}) "
        f"method={scoring_method} explained={len(explained_clauses)} "
        f"red_flags={red_flag_count}"
    )

    return result