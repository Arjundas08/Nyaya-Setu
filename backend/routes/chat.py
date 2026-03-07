# ════════════════════════════════════════════════════════
# FILE: backend/routes/chat.py
# ════════════════════════════════════════════════════════

import logging
from fastapi import APIRouter
from pydantic import BaseModel

from services.rag import ask_lawyer, clear_session

logger = logging.getLogger(__name__)
router = APIRouter()


# ════════════════════════════════════════════════════════
# REQUEST MODELS
# ════════════════════════════════════════════════════════
class ChatRequest(BaseModel):
    message:    str
    session_id: str   = "default"
    language:   str   = "English"

class ClearRequest(BaseModel):
    session_id: str = "default"

class SalaryRequest(BaseModel):
    ctc_annual: float   # Annual CTC in rupees e.g. 600000


# ════════════════════════════════════════════════════════
# HELPER: get document from analyze session store
# ════════════════════════════════════════════════════════
def _get_doc_text(session_id: str) -> str:
    """Get stored document text from analyze.py session store."""
    try:
        from routes.analyze import _store
        session = _store.get(session_id)
        return session.document_text if session else ""
    except Exception:
        return ""


# ════════════════════════════════════════════════════════
# ENDPOINT 1: Ask the Virtual Lawyer
# POST /chat/ask
# ════════════════════════════════════════════════════════
@router.post("/ask")
async def ask(req: ChatRequest):
    """
    User sends a question → AI answers using ChromaDB + Groq.
    If user has uploaded a document, it's included as context.
    """
    doc_text = _get_doc_text(req.session_id)

    # Add language hint if not English
    question = req.message
    if req.language and req.language.lower() != "english":
        question = f"[Please reply in {req.language}]\n{req.message}"

    result = ask_lawyer(
        question=question,
        document_text=doc_text,
        session_id=req.session_id
    )

    return {
        "answer":       result["answer"],
        "sources":      result["sources"],
        "chunks_used":  result["chunks_used"],
        "session_id":   req.session_id,
        "has_document": bool(doc_text),
        "language":     req.language,
    }


# ════════════════════════════════════════════════════════
# ENDPOINT 2: Clear chat session
# POST /chat/clear
# ════════════════════════════════════════════════════════
@router.post("/clear")
async def clear(req: ClearRequest):
    """Clear chat memory for this session."""
    clear_session(req.session_id)
    return {
        "success":    True,
        "session_id": req.session_id,
        "message":    "Chat history cleared. Ready for new conversation."
    }


# ════════════════════════════════════════════════════════
# ENDPOINT 3: Salary / CTC Decoder
# POST /chat/salary
# ════════════════════════════════════════════════════════
@router.post("/salary")
async def salary_decode(req: SalaryRequest):
    """
    Takes annual CTC → returns full monthly breakdown.
    Based on standard Indian salary structure.
    """
    ctc     = req.ctc_annual
    monthly = ctc / 12

    # Standard Indian salary split
    basic   = monthly * 0.40          # 40% of monthly CTC
    hra     = basic   * 0.50          # 50% of basic (metro HRA)
    special = monthly * 0.20          # Special allowance
    medical = 1250.0                  # Fixed Rs 1250/month
    lta     = basic   / 12            # Leave travel allowance

    # Deductions
    emp_pf    = basic  * 0.12         # Employee PF (12% of basic)
    er_pf     = basic  * 0.12         # Employer PF (in CTC, not in hand)
    prof_tax  = 200.0                 # ~Rs 200/month professional tax
    # Rough income tax (actual depends on 80C investments etc.)
    tax_est   = max(0.0, (ctc - 500000) * 0.05 / 12)

    gross      = basic + hra + special + medical + lta
    deductions = emp_pf + prof_tax + tax_est
    take_home  = gross - deductions

    return {
        "annual_ctc":       round(ctc, 2),
        "monthly_ctc":      round(monthly, 2),
        "earnings": {
            "basic":             round(basic, 2),
            "hra":               round(hra, 2),
            "special_allowance": round(special, 2),
            "medical_allowance": round(medical, 2),
            "lta":               round(lta, 2),
            "gross_salary":      round(gross, 2),
        },
        "deductions": {
            "employee_pf":       round(emp_pf, 2),
            "employer_pf_info":  round(er_pf, 2),
            "professional_tax":  prof_tax,
            "income_tax_est":    round(tax_est, 2),
            "total_deductions":  round(deductions, 2),
        },
        "monthly_take_home":  round(take_home, 2),
        "annual_take_home":   round(take_home * 12, 2),
        "note": (
            "Employer PF is part of CTC but does NOT come to you directly. "
            "Income tax is approximate — actual depends on 80C investments and HRA exemption."
        )
    }