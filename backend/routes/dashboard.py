# ════════════════════════════════════════════════════════
# FILE: backend/routes/dashboard.py
# ════════════════════════════════════════════════════════

import logging
from fastapi import APIRouter

logger = logging.getLogger(__name__)
router = APIRouter()


# ════════════════════════════════════════════════════════
# ENDPOINT: Get dashboard data for a session
# GET /dashboard/{session_id}
# ════════════════════════════════════════════════════════
@router.get("/{session_id}")
async def get_dashboard(session_id: str):
    """
    Returns a summary dashboard for a user session.
    Includes document info, clause breakdown, risk score.
    """
    try:
        from routes.analyze import _store
        session = _store.get(session_id)

        if not session:
            return {
                "session_id":   session_id,
                "has_data":     False,
                "message":      "No session data found. Upload a document first."
            }

        clauses = session.clauses or []
        risk    = session.risk    or {}

        # Clause breakdown by risk level
        high_clauses   = [c for c in clauses if c.get("risk_level") == "high"]
        medium_clauses = [c for c in clauses if c.get("risk_level") == "medium"]
        low_clauses    = [c for c in clauses if c.get("risk_level") == "low"]

        return {
            "session_id":   session_id,
            "has_data":     True,

            # Document info
            "document": {
                "filename":   session.filename,
                "file_type":  session.file_type,
                "char_count": session.char_count,
                "uploaded_at": session.created_at.isoformat(),
            },

            # Risk summary
            "risk_summary": {
                "score":          risk.get("score", 0),
                "level":          risk.get("level", "Unknown"),
                "color":          risk.get("color", "grey"),
                "scoring_method": risk.get("scoring_method", "unknown"),
                "summary":        risk.get("summary", ""),
                "action":         risk.get("action", ""),
            },

            # Clause breakdown
            "clauses": {
                "total":          len(clauses),
                "high_risk":      len(high_clauses),
                "medium_risk":    len(medium_clauses),
                "low_risk":       len(low_clauses),
                "high_details":   high_clauses,
                "medium_details": medium_clauses,
                "low_details":    low_clauses,
            },

            # Quick stats for frontend cards
            "stats": {
                "risky_clauses_count": len(risk.get("risky_clauses", [])),
                "safe_clauses_count":  len(risk.get("safe_clauses", [])),
                "high_risk_types":     [c["clause_type"] for c in high_clauses],
            }
        }

    except Exception as e:
        logger.error(f"Dashboard error: {e}")
        return {
            "session_id": session_id,
            "has_data":   False,
            "message":    f"Dashboard error: {str(e)}"
        }