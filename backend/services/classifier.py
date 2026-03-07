# ════════════════════════════════════════════════════════
# FILE: backend/services/classifier.py
# PRODUCTION-READY VERSION
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
    raise EnvironmentError(
        "GROQ_API_KEY not found in environment. "
        "Check your .env file has GROQ_API_KEY=your_key_here"
    )

_llm = ChatGroq(
    api_key=GROQ_API_KEY,
    model_name="llama-3.1-8b-instant",
    temperature=0,
    max_tokens=3000,
    request_timeout=30,
)

# ════════════════════════════════════════════════════════
# CONSTANTS
# ════════════════════════════════════════════════════════
CHUNK_SIZE = 3500
CHUNK_OVERLAP = 300
MAX_RETRIES = 3
RETRY_DELAY = 2.0

CLAUSE_TYPES = [
    "notice_period", "non_compete", "confidentiality",
    "salary_structure", "variable_pay", "leave_policy",
    "termination_clause", "bond_period", "penalty_clause",
    "intellectual_property", "arbitration", "jurisdiction",
    "probation_period", "performance_review", "relocation_clause",
    "rent_amount", "security_deposit", "maintenance_charges",
    "eviction_clause", "renewal_clause", "subletting_clause",
    "indemnity_clause", "limitation_of_liability",
    "force_majeure", "dispute_resolution",
]

VALID_RISK_LEVELS = {"high", "medium", "low"}


# ════════════════════════════════════════════════════════
# PROMPT
# ════════════════════════════════════════════════════════
def _build_prompt(document_chunk: str) -> str:

    safe_text = document_chunk.replace("{", "(").replace("}", ")")

    return f"""You are a legal document analyzer specializing in Indian contracts.

Analyze the document chunk below and identify ALL important legal clauses.

Return ONLY a JSON array.

Format:
[
 {{
   "clause_type": "notice_period",
   "text": "Employee must serve 90 days notice period before resignation",
   "risk_level": "high",
   "explanation": "90 days is above industry standard"
 }}
]

Valid clause_type values:
{", ".join(CLAUSE_TYPES)}

Document chunk:
{safe_text}

JSON array:"""


# ════════════════════════════════════════════════════════
# LLM CALL
# ════════════════════════════════════════════════════════
def _call_llm_with_retry(prompt: str) -> Optional[str]:

    delay = RETRY_DELAY

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = _llm.invoke(prompt)
            return response.content

        except Exception as e:

            error_str = str(e).lower()

            if "401" in error_str or "authentication" in error_str:
                logger.error("Groq authentication failed.")
                return None

            if "429" in error_str or "rate limit" in error_str:
                wait = delay * 2
                logger.warning(f"Rate limited. Waiting {wait}s")
                time.sleep(wait)
                delay *= 2
                continue

            if attempt < MAX_RETRIES:
                logger.warning(f"Retry {attempt}/{MAX_RETRIES} after error: {e}")
                time.sleep(delay)
                delay *= 2
            else:
                logger.error(f"All retries failed: {e}")

    return None


# ════════════════════════════════════════════════════════
# RESPONSE PARSER
# ════════════════════════════════════════════════════════
def _parse_clauses_from_response(raw: str) -> list:

    if not raw:
        return []

    cleaned = re.sub(r"```json|```", "", raw).strip()

    # FIXED REGEX
    match = re.search(r"\[.*\]", cleaned, re.DOTALL)

    if not match:
        logger.warning(f"No JSON array found. Raw: {cleaned[:200]}")
        return []

    json_str = match.group()

    try:
        parsed = json.loads(json_str)

    except json.JSONDecodeError:

        fixed = re.sub(r",\s*([}\]])", r"\1", json_str)

        try:
            parsed = json.loads(fixed)
        except json.JSONDecodeError:
            logger.error("JSON parsing failed")
            return []

    valid = []
    required = {"clause_type", "text", "risk_level", "explanation"}

    for item in parsed:

        if not isinstance(item, dict):
            continue

        if not required.issubset(item.keys()):
            continue

        if item["risk_level"] not in VALID_RISK_LEVELS:
            item["risk_level"] = "medium"

        item["text"] = item["text"].strip()
        item["explanation"] = item["explanation"].strip()
        item["clause_type"] = item["clause_type"].strip().lower()

        valid.append(item)

    return valid


# ════════════════════════════════════════════════════════
# CHUNKING
# ════════════════════════════════════════════════════════
def _chunk_document(text: str) -> list:

    if len(text) <= CHUNK_SIZE:
        return [text]

    chunks = []
    start = 0

    while start < len(text):

        end = min(start + CHUNK_SIZE, len(text))
        chunk = text[start:end]

        chunks.append(chunk)

        if end >= len(text):
            break

        start = end - CHUNK_OVERLAP

    return chunks


# ════════════════════════════════════════════════════════
# MAIN CLASSIFIER
# ════════════════════════════════════════════════════════
def classify_clauses(document_text: str) -> list:

    if not document_text or not document_text.strip():
        return []

    if len(document_text.strip()) < 50:
        return []

    chunks = _chunk_document(document_text)

    all_clauses = []

    for chunk in chunks:

        prompt = _build_prompt(chunk)

        raw = _call_llm_with_retry(prompt)

        if raw is None:
            continue

        clauses = _parse_clauses_from_response(raw)

        all_clauses.extend(clauses)

    risk_order = {"high": 0, "medium": 1, "low": 2}

    all_clauses.sort(key=lambda c: risk_order.get(c["risk_level"], 1))

    return all_clauses


# ════════════════════════════════════════════════════════
# SUMMARY
# ════════════════════════════════════════════════════════
def get_clause_summary(clauses: list) -> dict:

    if not clauses:
        return {
            "total": 0,
            "high_risk_count": 0,
            "medium_risk_count": 0,
            "low_risk_count": 0,
            "high_risk_types": []
        }

    return {
        "total": len(clauses),
        "high_risk_count": sum(1 for c in clauses if c["risk_level"] == "high"),
        "medium_risk_count": sum(1 for c in clauses if c["risk_level"] == "medium"),
        "low_risk_count": sum(1 for c in clauses if c["risk_level"] == "low"),
        "high_risk_types": [c["clause_type"] for c in clauses if c["risk_level"] == "high"],
    }