# ════════════════════════════════════════════════════════
# FILE: backend/services/risk_engine.py
# PRODUCTION-READY — HYBRID SCORING
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
    raise EnvironmentError("GROQ_API_KEY not found. Check your .env file.")

_llm = ChatGroq(
    api_key=GROQ_API_KEY,
    model_name="llama3-8b-8192",   # More reliable JSON output than 3.1-instant
    temperature=0,
    max_tokens=1000,
    request_timeout=30,
)

MAX_RETRIES  = 3
RETRY_DELAY  = 2.0
CHUNK_SIZE   = 3000   # Chars per chunk for long documents


# ════════════════════════════════════════════════════════
# RULE-BASED SCORING TABLE
# ════════════════════════════════════════════════════════
CLAUSE_RISK_WEIGHTS = {
    "bond_period":              2.5,
    "non_compete":              2.0,
    "penalty_clause":           1.5,
    "notice_period":            1.5,
    "termination_clause":       1.0,
    "variable_pay":              1.0,
    "probation_period":         0.5,
    "relocation_clause":        1.0,
    "intellectual_property":    0.5,
    "eviction_clause":          1.5,
    "security_deposit":         1.0,
    "maintenance_charges":      0.5,
    "indemnity_clause":         1.5,
    "limitation_of_liability":  1.0,
    "arbitration":              0.5,
    "jurisdiction":             0.5,
    "leave_policy":            -0.5,
    "performance_review":      -0.2,
    "renewal_clause":          -0.3,
}

RISK_LEVEL_MULTIPLIER = {
    "high":   1.5,
    "medium": 1.0,
    "low":    0.3,
}

def _rule_based_score(clauses: list) -> float:
    """Calculate a deterministic risk score (1-10)."""
    if not clauses:
        return 5.0

    base_score  = 2.0
    total_added = 0.0

    for clause in clauses:
        clause_type = clause.get("clause_type", "")
        risk_level  = clause.get("risk_level", "medium")
        weight = CLAUSE_RISK_WEIGHTS.get(clause_type, 0.3)
        multiplier  = RISK_LEVEL_MULTIPLIER.get(risk_level, 1.0)
        total_added += (weight * multiplier)

    return max(1.0, min(10.0, base_score + total_added))

def _build_llm_prompt(document_text: str, clause_context: str) -> str:
    safe_doc = document_text.replace("{", "(").replace("}", ")")
    return f"""Analyze this document and return ONLY a JSON object:
{{
  "llm_score": 7,
  "risky_clauses": ["Example"],
  "safe_clauses": ["Example"],
  "summary": "Summary text."
}}
{clause_context}
Document: {safe_doc[:3000]}"""

def _call_llm_with_retry(prompt: str) -> Optional[str]:
    delay = RETRY_DELAY
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            resp = _llm.invoke(prompt)
            return resp.content
        except Exception as e:
            time.sleep(delay)
            delay *= 2
    return None

def _parse_llm_response(raw: str) -> Optional[dict]:
    if not raw: return None
    cleaned = re.sub(r"\\\`\\\`\\\`json\\\\s*|\\\`\\\`\\\`\\\\s*", "", raw).strip()
    match = re.search(r"\\{.*\\}", cleaned, re.DOTALL)
    if not match: return None
    try:
        data = json.loads(match.group())
        # Validate score
        score = float(data.get("llm_score", 5))
        data["llm_score"] = max(1.0, min(10.0, score))
        return data
    except: return None

def calculate_risk_score(document_text: str, clauses: list = None) -> dict:
    clauses = clauses or []
    rule_score = _rule_based_score(clauses)
    
    prompt = _build_llm_prompt(document_text, str(clauses[:5]))
    raw_resp = _call_llm_with_retry(prompt)
    llm_parsed = _parse_llm_response(raw_resp)
    
    llm_score = llm_parsed["llm_score"] if llm_parsed else 5.0
    final_float = (rule_score * 0.60) + (llm_score * 0.40)
    
    return {
        "score": round(final_float),
        "level": "High Risk" if final_float > 7 else "Safe",
        "scoring_method": "hybrid"
    }
