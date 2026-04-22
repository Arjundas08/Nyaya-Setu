# ════════════════════════════════════════════════════════
# FILE: backend/services/database.py  ← REPLACE ENTIRE FILE
# ════════════════════════════════════════════════════════

import os
import logging
from datetime import datetime, timezone
from typing import Optional

from dotenv import load_dotenv
load_dotenv()

logger = logging.getLogger(__name__)

MONGO_URI = os.getenv("MONGO_URI", "")
_client   = None
_db       = None
_analyses = None   # collection: nyayasetu.analyses

# ────────────────────────────────────────────────────────
# CONNECTION — lazy, fails gracefully
# ────────────────────────────────────────────────────────
def _get_collection():
    """
    Returns the MongoDB collection.
    Returns None if MongoDB is not configured — all functions
    handle None gracefully so the app works without MongoDB.
    """
    global _client, _db, _analyses

    if _analyses is not None:
        return _analyses

    if not MONGO_URI:
        logger.warning("MONGO_URI not set — MongoDB disabled")
        return None

    try:
        from pymongo import MongoClient
        from pymongo.server_api import ServerApi
        _client   = MongoClient(MONGO_URI, server_api=ServerApi("1"),
                                serverSelectionTimeoutMS=5000)
        _client.admin.command("ping")   # test connection
        _db       = _client["nyayasetu"]
        _analyses = _db["analyses"]

        # Create indexes for fast lookups
        _analyses.create_index("session_id", unique=True)
        _analyses.create_index("created_at")

        logger.info("✅ MongoDB connected — nyayasetu.analyses ready")
        return _analyses

    except Exception as e:
        logger.error(f"MongoDB connection failed: {e}")
        logger.warning("App will continue without MongoDB persistence")
        _analyses = None
        return None


# ────────────────────────────────────────────────────────
# PUBLIC API
# ────────────────────────────────────────────────────────

def save_analysis(session_id: str, data: dict) -> bool:
    """
    Save or update a complete analysis result.

    Called from analyze.py after upload_document() completes.
    Uses upsert so re-uploads overwrite the previous record.

    data should contain: filename, file_type, total_chars,
    clauses, risk (score, level, explained_clauses, etc.)

    Returns True if saved, False if MongoDB unavailable.
    """
    col = _get_collection()
    if col is None:
        return False

    try:
        doc = {
            "session_id":  session_id,
            "filename":    data.get("filename", "unknown"),
            "file_type":   data.get("file_type", "unknown"),
            "total_chars": data.get("total_chars", 0),
            "created_at":  datetime.now(timezone.utc),

            # Risk analysis
            "risk_score":  data.get("risk", {}).get("score"),
            "risk_level":  data.get("risk", {}).get("level"),
            "risk_color":  data.get("risk", {}).get("color"),
            "top_concerns":data.get("risk", {}).get("top_concerns", []),
            "risk_breakdown": data.get("risk", {}).get("risk_breakdown", {}),

            # Clauses
            "clause_count":     data.get("clause_count", 0),
            "high_risk_count":  data.get("high_risk_count", 0),
            "clauses":          data.get("clauses", []),

            # Explained clauses (Upgrade 2)
            "explained_clauses": data.get("risk", {}).get("explained_clauses", []),

            # Full risk object for completeness
            "full_risk": data.get("risk", {}),
        }

        col.update_one(
            {"session_id": session_id},
            {"$set": doc},
            upsert=True
        )
        logger.info(f"Saved analysis: {session_id[:8]}... score={doc['risk_score']}")
        return True

    except Exception as e:
        logger.error(f"save_analysis failed: {e}")
        return False


def get_analysis(session_id: str) -> Optional[dict]:
    """
    Retrieve a saved analysis by session_id.
    Returns None if not found or MongoDB unavailable.
    """
    col = _get_collection()
    if col is None:
        return None

    try:
        doc = col.find_one({"session_id": session_id}, {"_id": 0})
        return doc
    except Exception as e:
        logger.error(f"get_analysis failed: {e}")
        return None


def get_recent_analyses(limit: int = 10) -> list:
    """
    Get the most recent analyses (for dashboard).
    Returns empty list if MongoDB unavailable.
    """
    col = _get_collection()
    if col is None:
        return []

    try:
        docs = col.find(
            {},
            {
                "_id": 0,
                "session_id": 1,
                "filename": 1,
                "risk_score": 1,
                "risk_level": 1,
                "risk_color": 1,
                "clause_count": 1,
                "high_risk_count": 1,
                "top_concerns": 1,
                "created_at": 1,
            }
        ).sort("created_at", -1).limit(limit)
        return list(docs)
    except Exception as e:
        logger.error(f"get_recent_analyses failed: {e}")
        return []


def get_stats() -> dict:
    """
    Get aggregate statistics for the dashboard.
    Returns empty dict if MongoDB unavailable.
    """
    col = _get_collection()
    if col is None:
        return {"mongodb": "not_connected"}

    try:
        total = col.count_documents({})
        high_risk = col.count_documents({"risk_score": {"$gte": 7}})
        avg_cursor = col.aggregate([
            {"$group": {"_id": None, "avg_score": {"$avg": "$risk_score"}}}
        ])
        avg_list = list(avg_cursor)
        avg_score = round(avg_list[0]["avg_score"], 1) if avg_list else 0

        return {
            "total_analyses": total,
            "high_risk_count": high_risk,
            "avg_risk_score": avg_score,
            "mongodb": "connected",
        }
    except Exception as e:
        logger.error(f"get_stats failed: {e}")
        return {}


def is_connected() -> bool:
    """Check if MongoDB is connected. Used by /health endpoint."""
    return _get_collection() is not None