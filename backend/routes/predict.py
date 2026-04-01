# ════════════════════════════════════════════════════════════
# FILE: backend/routes/predict.py
# The Oracle — Legal Outcome Predictor
#
# Pipeline:
#   1. Accept rich case input
#   2. Search Indian Kanoon for real precedents
#   3. Fetch judgment fragments for context
#   4. Groq LLM analyzes with real case law as context
#   5. Return comprehensive structured prediction
# ════════════════════════════════════════════════════════════

import os
import json
import re
import logging
from fastapi import APIRouter
from pydantic import BaseModel
from langchain_groq import ChatGroq
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)
router = APIRouter()

# ── LLM setup — uses centralized GROQ_MODEL from .env ─────
_llm = ChatGroq(
    api_key    = os.getenv("GROQ_API_KEY"),
    model_name = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant"),
    temperature = 0.1,
    max_tokens  = 1200,
)


# ════════════════════════════════════════════════════════════
# REQUEST MODEL
# ════════════════════════════════════════════════════════════
class PredictRequest(BaseModel):
    case_description: str
    case_type:        str = "general"    # employment|consumer|property|criminal|family|rti
    jurisdiction:     str = "India"      # state name
    user_side:        str = "complainant" # complainant|respondent
    amount_involved:  str = ""           # Rs. amount as string
    urgency:          str = "normal"     # normal|urgent|emergency
    document_text:    str = ""           # optional uploaded doc text
    session_id:       str = "default"


# ════════════════════════════════════════════════════════════
# FORUM SELECTION LOGIC
# Based on case type + amount — determines correct court
# ════════════════════════════════════════════════════════════
def _determine_forum(case_type: str, amount_str: str) -> str:
    try:
        amount = float(re.sub(r"[^\d.]", "", amount_str)) if amount_str else 0
    except Exception:
        amount = 0

    if case_type == "employment":
        return "Labour Court (via Labour Commissioner)"
    elif case_type == "consumer":
        if amount > 20000000:   # > 2 crore
            return "National Consumer Disputes Redressal Commission (NCDRC)"
        elif amount > 5000000:  # > 50 lakh
            return "State Consumer Disputes Redressal Commission"
        else:
            return "District Consumer Disputes Redressal Commission"
    elif case_type == "property":
        return "Civil Court / Rent Controller (State)"
    elif case_type == "criminal":
        return "Police Station (FIR) → Magistrate Court"
    elif case_type == "family":
        return "Family Court"
    elif case_type == "rti":
        return "First Appellate Authority → State/Central Information Commission"
    else:
        return "Civil Court / Appropriate Tribunal"


# ════════════════════════════════════════════════════════════
# ORACLE SYSTEM PROMPT
# ════════════════════════════════════════════════════════════
def _build_prompt(req: PredictRequest, ik_context: str) -> str:
    doc_ctx = ""
    if req.document_text:
        doc_ctx = f"\nUSER'S DOCUMENT EXCERPT:\n{req.document_text[:800]}\n"

    forum = _determine_forum(req.case_type, req.amount_involved)

    return f"""You are The Oracle — India's legal outcome prediction system. Be precise, realistic, honest.

CASE INPUT:
Type        : {req.case_type}
Description : {req.case_description}
Jurisdiction: {req.jurisdiction}
Side        : {req.user_side}
Amount      : Rs. {req.amount_involved or "not specified"}
Urgency     : {req.urgency}
Forum       : {forum}
{doc_ctx}

{ik_context if ik_context else "No case law retrieved — use your legal knowledge."}

CRITICAL LEGAL RULES:
- Offences BEFORE July 1 2024 → IPC/CrPC. AFTER July 1 2024 → BNS/BNSS/BSA
- IPC 302=BNS 103 | IPC 420=BNS 318 | IPC 376=BNS 63 | IPC 498A=BNS 85
- IT Act Section 66A → STRUCK DOWN 2015 (Shreya Singhal v UoI)
- Consumer forum jurisdiction based on claim amount (see above)
- Employment disputes: IDA 1947 Section 25F (retrenchment), 25G (procedure)
- win_probability must be realistic — do NOT give 90%+ unless extremely clear-cut

Return ONLY this JSON object — no markdown, no text outside the JSON:
{{
  "win_probability": <integer 0-100>,
  "verdict_label": <"Strong Case" | "Moderate Case" | "Challenging Case" | "High Risk">,
  "verdict_summary": <one precise sentence on likely outcome>,
  "recommended_forum": "{forum}",
  "timeline": <realistic estimate like "3-6 months" or "6-18 months">,
  "strengths": [<3-4 specific legal strengths, cite act+section where possible>],
  "weaknesses": [<2-3 honest risks or counter-arguments>],
  "action_steps": [
    {{"timeframe": "This week",    "action": <specific step>, "page": <"legal_notice"|"chat"|null>}},
    {{"timeframe": "Week 2-3",     "action": <specific step>, "page": null}},
    {{"timeframe": "If ignored",   "action": <specific step>, "page": null}},
    {{"timeframe": "Final option", "action": <specific step>, "page": null}}
  ],
  "applicable_laws": [<up to 5 strings like "IDA 1947 Section 25F">],
  "settlement_advice": <one sentence on settlement if relevant, else null>
}}"""


# ════════════════════════════════════════════════════════════
# ENDPOINT — POST /predict/outcome
# ════════════════════════════════════════════════════════════
@router.post("/outcome")
async def predict_outcome(req: PredictRequest):
    """
    Full Oracle pipeline:
      1. Validate input
      2. Search Indian Kanoon for real precedents
      3. Build LLM prompt enriched with real case law
      4. Get structured prediction from Groq
      5. Return everything — cases + prediction
    """
    if not req.case_description or not req.case_description.strip():
        return {"success": False, "message": "Please describe your legal situation."}

    # ── STEP 1: Search Indian Kanoon ────────────────────────
    cases      = []
    ik_context = ""

    try:
        from services.indiankanoon import get_relevant_cases, is_configured
        if is_configured():
            cases, ik_context = get_relevant_cases(
                description = req.case_description,
                case_type   = req.case_type,
                n_cases     = 4,    # fetch 4 cases metadata
                n_fragments = 2,    # fetch fragments from top 2
            )
            logger.info(f"IK returned {len(cases)} cases for Oracle")
        else:
            logger.warning("IK API not configured — Oracle using LLM-only mode")
    except Exception as e:
        logger.error(f"IK search failed (non-fatal): {e}")

    # ── STEP 2: Build prompt + call Groq ───────────────────
    prompt = _build_prompt(req, ik_context)

    try:
        response = _llm.invoke(prompt)
        raw      = response.content.strip()

        # Strip markdown fences if LLM adds them
        raw = re.sub(r"```json|```", "", raw).strip()

        # Extract JSON object
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if not match:
            raise ValueError("No JSON object found in LLM response")

        result = json.loads(match.group())

        # Validate + clamp win_probability
        wp = result.get("win_probability", 50)
        result["win_probability"] = max(0, min(100, int(wp)))

        # Attach real IK cases to result
        result["ik_cases"] = cases
        result["ik_used"]  = len(cases) > 0

        logger.info(
            f"Oracle complete: prob={result['win_probability']}% "
            f"forum='{result.get('recommended_forum','')}' "
            f"ik_cases={len(cases)}"
        )

        return {"success": True, **result}

    except json.JSONDecodeError as e:
        logger.error(f"JSON parse error: {e} | raw='{raw[:200]}'")
    except Exception as e:
        logger.error(f"Oracle LLM error: {e}")

    # ── FALLBACK ────────────────────────────────────────────
    forum = _determine_forum(req.case_type, req.amount_involved)
    return {
        "success":            False,
        "win_probability":    50,
        "verdict_label":      "Analysis Failed",
        "verdict_summary":    "Could not complete analysis. Please try again.",
        "recommended_forum":  forum,
        "timeline":           "Unknown",
        "strengths":          [],
        "weaknesses":         [],
        "action_steps":       [{"timeframe": "Now", "action": "Consult a licensed advocate", "page": "chat"}],
        "applicable_laws":    [],
        "settlement_advice":  None,
        "ik_cases":           cases,
        "ik_used":            len(cases) > 0,
        "message":            "Prediction failed — please try again.",
    }