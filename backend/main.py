# ════════════════════════════════════════════════════════
# FILE: backend/main.py
# ════════════════════════════════════════════════════════

import os
os.environ["ANONYMIZED_TELEMETRY"] = "False"   # kills ChromaDB noise
os.environ["CHROMA_TELEMETRY"]     = "False"   # belt and suspenders
import sys




# ── This line lets Python find services/ and routes/ ───
# Required because we run uvicorn from nyaya-setu-1/ root
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# ── Import ALL routers ──────────────────────────────────
from routes.analyze   import router as analyze_router
from routes.chat      import router as chat_router
from routes.search    import router as search_router
from routes.generate  import router as generate_router
from routes.predict   import router as predict_router
from routes.dashboard import router as dashboard_router
from routes.voice     import router as voice_router


def _validate_env():
    """Check all required env vars exist before server starts."""
    required = {
        "GROQ_API_KEY": "Get from https://console.groq.com",
        "GROQ_MODEL":   "e.g. llama-3.1-8b-instant",
        "MONGO_URI":    "Get from MongoDB Atlas dashboard",
    }
    missing = []
    for key, hint in required.items():
        if not os.getenv(key):
            missing.append(f"  ❌ {key} — {hint}")

    if missing:
        print("\n" + "="*50)
        print("  MISSING ENV VARIABLES — server cannot start")
        print("="*50)
        for m in missing:
            print(m)
        print("\n  Add these to your .env file and restart.")
        print("="*50 + "\n")
        # Don't raise — warn and continue so other endpoints work
        # raise EnvironmentError("Missing env vars")

_validate_env()   # call this right after imports in main.py

# ── Create the FastAPI app ──────────────────────────────
app = FastAPI(
    title="Nyaya-Setu API",
    description="AI-powered Virtual Legal Assistant for Indian Citizens",
    version="2.0.0",
    docs_url="/docs",       # Swagger UI at http://localhost:8000/docs
    redoc_url="/redoc",
)

# ── CORS — allows Streamlit frontend to call this API ───
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Register ALL routers ────────────────────────────────
app.include_router(analyze_router,  prefix="/analyze",   tags=["Document Analysis"])
app.include_router(chat_router,     prefix="/chat",      tags=["Virtual Lawyer"])
app.include_router(search_router,   prefix="/search",    tags=["Case Search"])
app.include_router(generate_router, prefix="/generate",  tags=["Doc Generator"])
app.include_router(predict_router,  prefix="/predict",   tags=["Outcome Predictor"])
app.include_router(dashboard_router,prefix="/dashboard", tags=["Dashboard"])
app.include_router(voice_router,    prefix="/voice",     tags=["Voice Services"])


# ── Root endpoint ───────────────────────────────────────
@app.get("/", tags=["Health"])
def root():
    return {
        "app":     "Nyaya-Setu API v2.0",
        "status":  "running ✅",
        "docs":    "http://localhost:8000/docs",
        "endpoints": {
            "upload_document":   "POST /analyze/upload",
            "get_risk":          "POST /analyze/risk",
            "get_document":      "GET  /analyze/doc/{session_id}",
            "delete_document":   "DELETE /analyze/doc/{session_id}",
            "store_stats":       "GET  /analyze/stats",
            "ask_lawyer":        "POST /chat/ask",
            "salary_decoder":    "POST /chat/salary",
            "clear_session":     "POST /chat/clear",
            "case_search":       "POST /search/cases",
            "generate_doc":      "POST /generate/document",
            "predict_outcome":   "POST /predict/outcome",
            "dashboard":         "GET  /dashboard/{session_id}",
            "voice_transcribe":  "POST /voice/transcribe",
            "voice_synthesize":  "POST /voice/synthesize",
            "voice_translate":   "POST /voice/translate",
            "voice_detect":      "POST /voice/detect",
            "voice_status":      "GET  /voice/status",
        }
    }

@app.get("/health", tags=["Health"])
async def health():
    from services.database import is_connected
    return {
        "status":   "healthy",
        "version":  "2.0",
        "mongodb":  "connected" if is_connected() else "not_connected",
        "model":    os.getenv("GROQ_MODEL", "llama-3.1-8b-instant"),
    }

# ════════════════════════════════════════════════════════
# HOW TO RUN (from nyaya-setu-1/ root folder):
#   uvicorn backend.main:app --reload
#
# Then open:
#   http://localhost:8000        → see all endpoints
#   http://localhost:8000/docs   → Swagger UI (test all endpoints)
# ════════════════════════════════════════════════════════