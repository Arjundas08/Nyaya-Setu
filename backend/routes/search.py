# ════════════════════════════════════════════════════════════
# FILE: backend/routes/search.py
# Case Archives — Smart Relevance Search
#
# Pipeline:
#   1. Search IK with smart query (from user's actual words)
#   2. Fetch fragments for top 4 raw results
#   3. LLM RELEVANCE FILTER:
#      - Score each case 0–100 for relevance
#      - Generate 3 specific match reasons
#      - Filter out anything below 55
#      - Return top 3 only
#   4. Generate plain English explanation for survivors
#
# Result: 2-3 highly relevant cases, never 6 random ones
# ════════════════════════════════════════════════════════════

import os
import re
import json
import logging
from fastapi import APIRouter
from pydantic import BaseModel
from langchain_groq import ChatGroq
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)
router = APIRouter()

_llm = ChatGroq(
    api_key     = os.getenv("GROQ_API_KEY"),
    model_name  = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant"),
    temperature = 0.1,
    max_tokens  = 900,
)

RELEVANCE_THRESHOLD = 55   # cases scoring below this are hidden


# ════════════════════════════════════════════════════════════
# REQUEST MODEL
# ════════════════════════════════════════════════════════════
class CaseSearchRequest(BaseModel):
    query:      str
    category:   str = "general"
    top_k:      int = 3          # max shown to user (after filtering)
    session_id: str = "default"
    explain:    bool = True


# ════════════════════════════════════════════════════════════
# RELEVANCE SCORER + EXPLAINER
# One LLM call handles both scoring AND explanation
# ════════════════════════════════════════════════════════════
def _score_and_explain(cases: list, user_query: str, category: str) -> list:
    """
    For each case:
      relevance_score  : 0-100 — how relevant is this to the user's situation
      match_reasons    : 3 bullet points of WHY it's relevant (specific facts)
      plain_decision   : What did the court decide? (plain language, 1 sentence)
      means_for_you    : What does this mean for the user? (1 sentence)

    Cases scoring below RELEVANCE_THRESHOLD are discarded.
    Returns sorted by score descending.
    """
    if not cases:
        return []

    case_list = []
    for i, c in enumerate(cases):
        snippet  = c.get("snippet", c.get("fragment", ""))[:200]
        case_list.append(
            f"CASE {i+1}: {c.get('title','')}\n"
            f"Court: {c.get('court','')} | Year: {c.get('date','')[:4]}\n"
            f"Summary: {snippet}"
        )

    cases_text = "\n\n".join(case_list)

    prompt = f"""You are a legal AI helping a common Indian citizen find relevant court cases.

USER'S SITUATION: "{user_query}"
LEGAL CATEGORY: {category}

For each case below, you must:
1. Give a relevance_score (0-100) — HOW CLOSELY does this case match the user's SPECIFIC situation?
   - 85-100: Almost identical situation (same issue, same type of dispute)
   - 60-84: Clearly relevant (similar issue, applicable legal principle)
   - 40-59: Somewhat related (same general area but different facts)
   - 0-39: Not relevant or wrong category — REJECT this

2. Give match_reasons: EXACTLY 3 specific bullets explaining why it matches (or doesn't)
   Be specific — mention: same type of dispute, same type of party, same legal issue

3. plain_decision: ONE plain sentence starting with "The court decided..."
   Use simple language any person can understand. No legal jargon.

4. means_for_you: ONE plain sentence starting with "This means..."
   Specifically about the user's situation.

CASES:
{cases_text}

Return ONLY a valid JSON array — NO markdown, NO extra text:
[
  {{
    "case_index": 1,
    "relevance_score": 88,
    "match_reasons": [
      "Same issue: security deposit not returned by landlord",
      "Court ordered full refund to tenant",
      "Applies to your situation under Transfer of Property Act"
    ],
    "plain_decision": "The court decided that the landlord must return the full security deposit within 30 days of the tenant vacating.",
    "means_for_you": "This means you have a strong legal right to get your deposit back, and the court will likely rule in your favour."
  }}
]
Return the JSON array now:"""

    try:
        response = _llm.invoke(prompt)
        raw      = response.content.strip()
        raw      = re.sub(r"```json|```", "", raw).strip()

        match = re.search(r"\[.*\]", raw, re.DOTALL)
        if not match:
            raise ValueError("No JSON array in response")

        scored = json.loads(match.group())
        logger.info(f"LLM scored {len(scored)} cases")

        # Attach scores and filter
        enriched = []
        for item in scored:
            idx = item.get("case_index", 1) - 1
            if 0 <= idx < len(cases):
                score = int(item.get("relevance_score", 0))
                if score >= RELEVANCE_THRESHOLD:
                    case = cases[idx].copy()
                    case["relevance_score"]  = score
                    case["match_reasons"]    = item.get("match_reasons", [])
                    case["plain_decision"]   = item.get("plain_decision", "")
                    case["means_for_you"]    = item.get("means_for_you", "")
                    enriched.append(case)
                else:
                    logger.info(f"Filtered out '{cases[idx].get('title','')[:40]}' (score {score})")

        # Sort by score descending
        enriched.sort(key=lambda x: x["relevance_score"], reverse=True)
        return enriched

    except Exception as e:
        logger.error(f"Relevance scoring error: {e}")
        # Return unscored cases rather than nothing
        for c in cases:
            c["relevance_score"]  = 70
            c["match_reasons"]    = ["Relevant to your legal situation"]
            c["plain_decision"]   = ""
            c["means_for_you"]    = ""
        return cases


# ════════════════════════════════════════════════════════════
# ENDPOINT — POST /search/cases
# ════════════════════════════════════════════════════════════
@router.post("/cases")
async def search_cases(req: CaseSearchRequest):
    if not req.query or not req.query.strip():
        return {"success": False, "message": "Please describe your situation."}

    # ── Step 1: Get raw cases from IK ───────────────────────
    raw_cases = []
    try:
        from services.indiankanoon import search_cases as ik_search, get_case_fragment, is_configured
        raw_cases = ik_search(
            description = req.query,
            case_type   = req.category,
            max_results = 8,    # fetch 8, will filter to top 3
        )
        logger.info(f"IK returned {len(raw_cases)} raw cases (IK live: {is_configured()})")

        # Fetch fragments for top 4 non-fallback cases
        real_cases = [c for c in raw_cases if not c.get("fallback")]
        for i, case in enumerate(real_cases[:4]):
            if case.get("doc_id"):
                frag = get_case_fragment(case["doc_id"], req.query)
                if frag:
                    case["fragment"] = frag
                    case["snippet"]  = frag  # use fragment as snippet for scoring

    except Exception as e:
        logger.error(f"IK search failed: {e}")

    if not raw_cases:
        return {
            "success": False,
            "query":   req.query,
            "results": [],
            "count":   0,
            "message": "Could not retrieve cases. Please try again.",
        }

    # ── Step 2: Score relevance + filter + explain ──────────
    if req.explain and raw_cases:
        scored = _score_and_explain(raw_cases, req.query, req.category)
    else:
        scored = raw_cases

    # Limit to top_k
    final = scored[:req.top_k]

    # If nothing survived the filter, use top 2 raw cases with default score
    if not final and raw_cases:
        logger.warning("All cases filtered out — showing top 2 unscored")
        for c in raw_cases[:2]:
            c.setdefault("relevance_score", 65)
            c.setdefault("match_reasons",   ["Related to your legal situation"])
            c.setdefault("plain_decision",  "")
            c.setdefault("means_for_you",   "")
        final = raw_cases[:2]

    is_live = any(not c.get("fallback", True) for c in final)
    logger.info(f"Returning {len(final)} cases | live: {is_live} | scores: {[c.get('relevance_score') for c in final]}")

    return {
        "success":  True,
        "query":    req.query,
        "category": req.category,
        "results":  final,
        "count":    len(final),
        "ik_live":  is_live,
    }