# ════════════════════════════════════════════════════════
# FILE: backend/routes/predict.py
# ════════════════════════════════════════════════════════

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

_llm = ChatGroq(
    api_key=os.getenv("GROQ_API_KEY"),
    model_name="llama3-8b-8192",
    temperature=0.1,
    max_tokens=1000,
)


class PredictRequest(BaseModel):
    case_description: str         # User describes their legal situation
    document_text:    str = ""    # Optional: their document
    session_id:       str = "default"


# ════════════════════════════════════════════════════════
# ENDPOINT: Predict legal outcome
# POST /predict/outcome
# ════════════════════════════════════════════════════════
@router.post("/outcome")
async def predict_outcome(req: PredictRequest):
    """
    Takes a case description → predicts likely legal outcome.
    Returns win probability, reasoning, and recommended actions.
    """
    if not req.case_description or not req.case_description.strip():
        return {
            "success": False,
            "message": "Please provide a case description."
        }

    doc_context = ""
    if req.document_text:
        doc_context = f"\nRelevant document:\n{req.document_text[:1500]}"

    prompt = f"""You are a legal outcome analyst for Indian courts.

Case description: {req.case_description}{doc_context}

Analyze this case and return ONLY a JSON object (no markdown, no extra text):
{{
  "win_probability": 65,
  "outcome_summary": "One sentence summary of likely outcome",
  "reasoning": "2-3 sentences explaining why",
  "key_factors_for": ["factor that helps the case"],
  "key_factors_against": ["factor that hurts the case"],
  "recommended_actions": ["action 1", "action 2", "action 3"],
  "time_estimate": "6-18 months",
  "disclaimer": "This is an AI estimate only. Consult a licensed advocate."
}}

win_probability: integer 0-100 (realistic estimate based on Indian law)
Return ONLY the JSON:"""

    try:
        response = _llm.invoke(prompt)
        raw      = response.content.strip()
        raw      = re.sub(r"```json|```", "", raw).strip()
        match    = re.search(r"\{.*\}", raw, re.DOTALL)

        if match:
            result = json.loads(match.group())
            # Validate win_probability
            wp = result.get("win_probability", 50)
            result["win_probability"] = max(0, min(100, int(wp)))
            return {"success": True, **result}

    except Exception as e:
        logger.error(f"Outcome predictor error: {e}")

    return {
        "success":             False,
        "win_probability":     50,
        "outcome_summary":     "Could not analyze — please try again.",
        "reasoning":           "",
        "key_factors_for":     [],
        "key_factors_against": [],
        "recommended_actions": ["Consult a licensed advocate"],
        "time_estimate":       "Unknown",
        "disclaimer":          "This is an AI estimate only. Consult a licensed advocate.",
        "message":             "Prediction failed. Please try again."
    }