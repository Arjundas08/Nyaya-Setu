# ════════════════════════════════════════════════════════════
# FILE: backend/routes/dashboard.py
# Chamber Records — Session Dashboard
#
# Two data sources:
#   1. _store (in-memory)  → current session's live data
#   2. MongoDB             → all past analyses (persistent)
#
# Endpoints:
#   GET /dashboard/{session_id}  → current session summary
#   GET /dashboard/history/all   → last 10 analyses from MongoDB
#   GET /dashboard/stats/global  → aggregate stats from MongoDB
# ════════════════════════════════════════════════════════════

import logging
from fastapi import APIRouter

logger = logging.getLogger(__name__)
router = APIRouter()


# ════════════════════════════════════════════════════════════
# ENDPOINT 1: Current session dashboard
# GET /dashboard/{session_id}
# ════════════════════════════════════════════════════════════
@router.get("/{session_id}")
async def get_dashboard(session_id: str):
    """
    Returns dashboard data for the current session.
    Tries in-memory store first, then MongoDB as fallback.
    """
    # Skip special route keywords
    if session_id in ("history", "stats"):
        return {"has_data": False, "message": "Use /dashboard/history/all or /dashboard/stats/global"}

    # ── Try in-memory store ──────────────────────────────────
    session_data = None
    try:
        from routes.analyze import _store
        session_data = _store.get(session_id)
    except Exception as e:
        logger.warning(f"In-memory store unavailable: {e}")

    if session_data:
        clauses = session_data.clauses or []
        risk    = session_data.risk    or {}

        high_c   = [c for c in clauses if c.get("risk_level") == "high"]
        medium_c = [c for c in clauses if c.get("risk_level") == "medium"]
        low_c    = [c for c in clauses if c.get("risk_level") == "low"]

        return {
            "session_id":  session_id,
            "has_data":    True,
            "source":      "live",
            "document": {
                "filename":    session_data.filename,
                "file_type":   session_data.file_type,
                "char_count":  session_data.char_count,
                "uploaded_at": session_data.created_at.isoformat(),
            },
            "risk_summary": {
                "score":           risk.get("score", 0),
                "level":           risk.get("level", "Unknown"),
                "color":           risk.get("color", "grey"),
                "top_concerns":    risk.get("top_concerns", []),
                "scoring_method":  risk.get("scoring_method", "hybrid"),
                "explained_clauses": risk.get("explained_clauses", []),
            },
            "clauses": {
                "total":          len(clauses),
                "high_risk":      len(high_c),
                "medium_risk":    len(medium_c),
                "low_risk":       len(low_c),
                "high_details":   high_c[:5],
                "medium_details": medium_c[:5],
            },
        }

    # ── Try MongoDB fallback ─────────────────────────────────
    try:
        from services.database import get_analysis
        mongo_data = get_analysis(session_id)
        if mongo_data:
            return {
                "session_id":  session_id,
                "has_data":    True,
                "source":      "mongodb",
                "document": {
                    "filename":    mongo_data.get("filename", "Unknown"),
                    "file_type":   mongo_data.get("file_type", "Unknown"),
                    "char_count":  mongo_data.get("total_chars", 0),
                    "uploaded_at": str(mongo_data.get("created_at", "")),
                },
                "risk_summary": {
                    "score":           mongo_data.get("risk_score", 0),
                    "level":           mongo_data.get("risk_level", "Unknown"),
                    "color":           mongo_data.get("risk_color", "grey"),
                    "top_concerns":    mongo_data.get("top_concerns", []),
                    "scoring_method":  "hybrid",
                    "explained_clauses": mongo_data.get("explained_clauses", []),
                },
                "clauses": {
                    "total":          mongo_data.get("clause_count", 0),
                    "high_risk":      mongo_data.get("high_risk_count", 0),
                    "medium_risk":    0,
                    "low_risk":       0,
                    "high_details":   [],
                    "medium_details": [],
                },
            }
    except Exception as e:
        logger.error(f"MongoDB lookup failed: {e}")

    return {
        "session_id": session_id,
        "has_data":   False,
        "message":    "No analysis found for this session. Upload a document first.",
    }


# ════════════════════════════════════════════════════════════
# ENDPOINT 2: Recent analyses history
# GET /dashboard/history/all
# ════════════════════════════════════════════════════════════
@router.get("/history/all")
async def get_history():
    """
    Returns the last 10 analyses from MongoDB.
    Used by the Chamber Records page to show history.
    """
    try:
        from services.database import get_recent_analyses
        analyses = get_recent_analyses(limit=10)

        # Sanitise MongoDB ObjectId / datetime fields
        clean = []
        for a in analyses:
            clean.append({
                "session_id":      a.get("session_id", ""),
                "filename":        a.get("filename", "Unknown Document"),
                "file_type":       a.get("file_type", "Unknown"),
                "risk_score":      a.get("risk_score", 0),
                "risk_level":      a.get("risk_level", "Unknown"),
                "risk_color":      a.get("risk_color", "grey"),
                "clause_count":    a.get("clause_count", 0),
                "high_risk_count": a.get("high_risk_count", 0),
                "top_concerns":    a.get("top_concerns", [])[:2],
                "created_at":      str(a.get("created_at", ""))[:19],
            })

        return {"success": True, "analyses": clean, "count": len(clean)}

    except Exception as e:
        logger.error(f"History fetch error: {e}")
        return {"success": False, "analyses": [], "count": 0,
                "message": "Could not load history. MongoDB may not be connected."}


# ════════════════════════════════════════════════════════════
# ENDPOINT 3: Global aggregate stats
# GET /dashboard/stats/global
# ════════════════════════════════════════════════════════════
@router.get("/stats/global")
async def get_global_stats():
    """
    Returns aggregate statistics across all analyses.
    Used for the stats cards at the top of Chamber Records.
    """
    try:
        from services.database import get_stats
        stats = get_stats()
        return {"success": True, **stats}
    except Exception as e:
        logger.error(f"Stats error: {e}")
        return {
            "success":         False,
            "total_analyses":  0,
            "high_risk_count": 0,
            "avg_risk_score":  0,
            "mongodb":         "not_connected",
        }