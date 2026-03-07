# ════════════════════════════════════════════════════════
# FILE: backend/routes/search.py
# ════════════════════════════════════════════════════════

import logging
from fastapi import APIRouter
from pydantic import BaseModel

logger = logging.getLogger(__name__)
router = APIRouter()


class CaseSearchRequest(BaseModel):
    query:       str
    top_k:       int = 3     # Number of similar cases to return
    session_id:  str = "default"


# ════════════════════════════════════════════════════════
# ENDPOINT: Search similar court cases
# POST /search/cases
# ════════════════════════════════════════════════════════
@router.post("/cases")
async def search_cases(req: CaseSearchRequest):
    """
    Search for similar Indian court cases using FAISS.
    Returns top-k most similar cases to the query.
    """
    try:
        from services.case_search import find_similar_cases
        results = find_similar_cases(req.query, top_k=req.top_k)
        return {
            "success": True,
            "query":   req.query,
            "results": results,
            "count":   len(results),
        }
    except ImportError:
        # FAISS index not built yet — return helpful message
        logger.warning("case_search service not ready")
        return {
            "success": False,
            "query":   req.query,
            "results": [],
            "count":   0,
            "message": "Case search index not built yet. Run: python scripts/build_faiss_index.py"
        }
    except Exception as e:
        logger.error(f"Case search error: {e}")
        return {
            "success": False,
            "query":   req.query,
            "results": [],
            "count":   0,
            "message": f"Search failed: {str(e)}"
        }