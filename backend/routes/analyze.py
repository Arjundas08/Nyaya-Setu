# ════════════════════════════════════════════════════════
# FILE: backend/routes/analyze.py
# PRODUCTION-GRADE VERSION WITH VECTOR STORE UPDATES
# ════════════════════════════════════════════════════════

import io
import logging
import time
import uuid
import threading
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, UploadFile, File, HTTPException, Query
from pydantic import BaseModel

from services.ocr         import extract_text_from_image
from services.privacy     import redact_pii
from services.classifier  import classify_clauses
from services.risk_engine import calculate_risk_score

logger = logging.getLogger(__name__)
router = APIRouter()


# ════════════════════════════════════════════════════════
# FILE CONFIGURATION
# ════════════════════════════════════════════════════════
MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024   # 10 MB
MIN_TEXT_LENGTH     = 50                  # Minimum chars to be a real document

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/jpg", "image/png", "image/webp", "image/bmp", "image/tiff"}
ALLOWED_PDF_TYPES   = {"application/pdf"}
ALL_ALLOWED_TYPES   = ALLOWED_IMAGE_TYPES | ALLOWED_PDF_TYPES


# ════════════════════════════════════════════════════════
# SESSION STORE
# ════════════════════════════════════════════════════════

class _SessionData:
    def __init__(self, session_id: str, document_text: str):
        self.session_id    = session_id
        self.document_text = document_text
        self.clauses       = []
        self.risk          = None
        self.filename      = ""
        self.file_type     = ""
        self.char_count    = len(document_text)
        self.created_at    = datetime.utcnow()
        self.last_accessed = datetime.utcnow()

    def touch(self):
        self.last_accessed = datetime.utcnow()

    def is_expired(self, ttl_hours: int = 2) -> bool:
        return (datetime.utcnow() - self.last_accessed) > timedelta(hours=ttl_hours)


class SessionStore:
    TTL_HOURS    = 2
    MAX_SESSIONS = 500

    def __init__(self):
        self._store: dict[str, _SessionData] = {}
        self._lock  = threading.Lock()

    def set(self, session_id: str, document_text: str, filename: str = "", file_type: str = "") -> _SessionData:
        with self._lock:
            self._evict_expired()
            if len(self._store) >= self.MAX_SESSIONS:
                oldest_id = min(self._store, key=lambda k: self._store[k].last_accessed)
                del self._store[oldest_id]
            
            session = _SessionData(session_id, document_text)
            session.filename  = filename
            session.file_type = file_type
            self._store[session_id] = session
            return session

    def get(self, session_id: str) -> Optional[_SessionData]:
        with self._lock:
            session = self._store.get(session_id)
            if session is None: return None
            if session.is_expired(self.TTL_HOURS):
                del self._store[session_id]
                return None
            session.touch()
            return session

    def delete(self, session_id: str) -> bool:
        with self._lock:
            if session_id in self._store:
                del self._store[session_id]
                return True
            return False

    def update_analysis(self, session_id: str, clauses: list, risk: dict):
        with self._lock:
            session = self._store.get(session_id)
            if session:
                session.clauses = clauses
                session.risk    = risk
                session.touch()

    def stats(self) -> dict:
        with self._lock:
            self._evict_expired()
            return {"active_sessions": len(self._store), "max_sessions": self.MAX_SESSIONS}

    def _evict_expired(self):
        expired = [sid for sid, s in self._store.items() if s.is_expired(self.TTL_HOURS)]
        for sid in expired: del self._store[sid]


_store = SessionStore()


# ════════════════════════════════════════════════════════
# HELPERS
# ════════════════════════════════════════════════════════

async def _read_file_safe(file: UploadFile) -> bytes:
    chunks = []
    total_read = 0
    while True:
        chunk = await file.read(64 * 1024)
        if not chunk: break
        total_read += len(chunk)
        if total_read > MAX_FILE_SIZE_BYTES:
            raise HTTPException(status_code=413, detail="File too large.")
        chunks.append(chunk)
    return b"".join(chunks)

def _extract_text_from_pdf(pdf_bytes: bytes) -> str:
    try:
        from pypdf import PdfReader
        reader = PdfReader(io.BytesIO(pdf_bytes))
        all_text = [p.extract_text().strip() for p in reader.pages if p.extract_text()]
        combined = "\n\n".join(all_text)
        if len(combined.strip()) >= MIN_TEXT_LENGTH: return combined
    except Exception: pass
    return extract_text_from_image(pdf_bytes)

def _validate_extracted_text(text: str) -> str:
    if not text or len(text.strip()) < MIN_TEXT_LENGTH:
        raise HTTPException(status_code=422, detail="Insufficient text extracted.")
    return text.strip()


# ════════════════════════════════════════════════════════
# ENDPOINT: Upload & Index
# ════════════════════════════════════════════════════════

@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    session_id: str  = Query(default="", description="Session ID.")
):
    request_start = time.monotonic()
    timings = {}

    if not session_id or session_id.strip() == "":
        session_id = str(uuid.uuid4())

    filename = file.filename or "unknown"
    content_type = (file.content_type or "").lower().strip()
    
    if content_type not in ALL_ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail="Unsupported file type.")

    # 1. Read
    t0 = time.monotonic()
    file_bytes = await _read_file_safe(file)
    timings["read_ms"] = int((time.monotonic() - t0) * 1000)

    # 2. Extract
    t0 = time.monotonic()
    is_pdf = content_type in ALLOWED_PDF_TYPES
    raw_text = _extract_text_from_pdf(file_bytes) if is_pdf else extract_text_from_image(file_bytes)
    raw_text = _validate_extracted_text(raw_text)
    timings["extraction_ms"] = int((time.monotonic() - t0) * 1000)

    # 3. Privacy
    t0 = time.monotonic()
    safe_text = redact_pii(raw_text)
    timings["privacy_ms"] = int((time.monotonic() - t0) * 1000)

    # 4. Store Session
    file_type_label = "pdf" if is_pdf else "image"
    _store.set(session_id, safe_text, filename, file_type_label)

    # ── [FIX] Clear old doc store before building new ────────
    try:
        from services.doc_vectorstore import delete_doc_store
        delete_doc_store(session_id)
        logger.info(f"Cleared old doc store for {session_id[:8]}...")
    except Exception as e:
        logger.warning(f"Failed to clear old doc store: {e}")
    # ─────────────────────────────────────────────────────────

    # 5. Build per-session document vector store
    t0 = time.monotonic()
    doc_chunks = 0
    try:
        from services.doc_vectorstore import build_doc_store
        doc_chunks = build_doc_store(session_id, safe_text)
        timings["doc_store_ms"] = int((time.monotonic() - t0) * 1000)
        logger.info(f"Doc store built: {doc_chunks} chunks for {session_id[:8]}")
    except Exception as e:
        logger.error(f"Doc store build failed (non-fatal): {e}")
        doc_chunks = 0
        timings["doc_store_ms"] = 0

    # 6. Classify
    t0 = time.monotonic()
    clauses = classify_clauses(safe_text)
    timings["classify_ms"] = int((time.monotonic() - t0) * 1000)

    # Rate limit protection — wait before next LLM call
    time.sleep(5)

    # 7. Risk
    t0 = time.monotonic()
    risk = calculate_risk_score(safe_text, clauses)
    timings["risk_ms"] = int((time.monotonic() - t0) * 1000)

    _store.update_analysis(session_id, clauses, risk)
    timings["total_ms"] = int((time.monotonic() - request_start) * 1000)

    return {
        "success": True,
        "session_id": session_id,
        "filename": filename,
        "file_type": file_type_label,
        "file_size_kb": len(file_bytes) // 1024,
        "total_chars": len(safe_text),
        "text_preview": safe_text[:600],
        "doc_chunks": doc_chunks,
        "doc_searchable": doc_chunks > 0,
        "clauses": clauses,
        "clause_count": len(clauses),
        "high_risk_count": sum(1 for c in clauses if c.get("risk_level") == "high"),
        "risk": risk,
        "timings_ms": timings,
        "message": "Document analyzed and indexed for chat!" if doc_chunks > 0 else "Analyzed successfully!",
    }


@router.delete("/doc/{session_id}")
async def delete_document(session_id: str):
    deleted = _store.delete(session_id)
    # Also delete the document vector store
    try:
        from services.doc_vectorstore import delete_doc_store
        delete_doc_store(session_id)
    except Exception as e:
        logger.error(f"Failed to delete FAISS store: {e}")
        
    return {
        "success": deleted,
        "session_id": session_id,
        "message": "Session cleared." if deleted else "Session not found."
    }


# ── FIX IS HERE: Create a specific request model ──
class RiskRequest(BaseModel):
    session_id: str

@router.post("/risk")
async def get_risk(req: RiskRequest):
    session = _store.get(req.session_id)
    if not session: 
        raise HTTPException(status_code=404, detail="Session not found.")
    return {"session_id": req.session_id, "risk": session.risk, "clauses": session.clauses, "cached": True}
# ──────────────────────────────────────────────────


@router.get("/doc/{session_id}")
async def get_document(session_id: str):
    session = _store.get(session_id)
    if not session: return {"session_id": session_id, "has_document": False}
    return {"session_id": session_id, "has_document": True, "document_text": session.document_text}

@router.get("/stats")
async def get_stats():
    return _store.stats()