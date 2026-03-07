# ════════════════════════════════════════════════════════
# FILE: backend/routes/analyze.py
# PRODUCTION-GRADE VERSION
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

from services.ocr       import extract_text_from_image
from services.privacy   import redact_pii
from services.classifier import classify_clauses
from services.risk_engine import calculate_risk_score

logger = logging.getLogger(__name__)
router = APIRouter()


# ════════════════════════════════════════════════════════
# FILE CONFIGURATION
# ════════════════════════════════════════════════════════
MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024   # 10 MB
MIN_TEXT_LENGTH     = 50                  # Minimum chars to be a real document

# All accepted MIME types
ALLOWED_IMAGE_TYPES = {
    "image/jpeg", "image/jpg", "image/png",
    "image/webp", "image/bmp", "image/tiff",
}
ALLOWED_PDF_TYPES = {
    "application/pdf",
}
ALL_ALLOWED_TYPES = ALLOWED_IMAGE_TYPES | ALLOWED_PDF_TYPES


# ════════════════════════════════════════════════════════
# SESSION STORE — thread-safe with TTL auto-expiry
# ════════════════════════════════════════════════════════
# WHY: In-memory dict grows forever → server OOM crash.
# TTL sessions auto-expire after 2 hours.
# Max 500 sessions hard cap → oldest evicted when full.
# Thread lock → safe for concurrent requests.
# ════════════════════════════════════════════════════════

class _SessionData:
    """One user's session — document + clauses + metadata."""
    def __init__(self, session_id: str, document_text: str):
        self.session_id    = session_id
        self.document_text = document_text
        self.clauses       = []          # Populated after classification
        self.risk          = None        # Populated after risk scoring
        self.filename      = ""          # Original uploaded filename
        self.file_type     = ""          # "image" or "pdf"
        self.char_count    = len(document_text)
        self.created_at    = datetime.utcnow()
        self.last_accessed = datetime.utcnow()

    def touch(self):
        """Update last accessed time (called on every read)."""
        self.last_accessed = datetime.utcnow()

    def is_expired(self, ttl_hours: int = 2) -> bool:
        age = datetime.utcnow() - self.last_accessed
        return age > timedelta(hours=ttl_hours)


class SessionStore:
    """
    Thread-safe in-memory session store with TTL expiry.

    Features:
      - Auto-expires sessions after TTL_HOURS (default 2h)
      - Hard cap at MAX_SESSIONS (default 500)
        → evicts oldest session when full
      - Thread-safe: uses threading.Lock for all operations
      - get() updates last_accessed (LRU-style freshness)
    """

    TTL_HOURS    = 2
    MAX_SESSIONS = 500

    def __init__(self):
        self._store: dict[str, _SessionData] = {}
        self._lock  = threading.Lock()

    def set(self, session_id: str, document_text: str, filename: str = "", file_type: str = "") -> _SessionData:
        with self._lock:
            self._evict_expired()

            # If at capacity, evict the oldest session
            if len(self._store) >= self.MAX_SESSIONS:
                oldest_id = min(self._store, key=lambda k: self._store[k].last_accessed)
                del self._store[oldest_id]
                logger.warning(f"Session store at capacity ({self.MAX_SESSIONS}). Evicted oldest: {oldest_id[:8]}...")

            session = _SessionData(session_id, document_text)
            session.filename  = filename
            session.file_type = file_type
            self._store[session_id] = session
            logger.info(f"Session created: {session_id[:8]}... ({len(document_text)} chars) [{file_type}]")
            return session

    def get(self, session_id: str) -> Optional[_SessionData]:
        with self._lock:
            session = self._store.get(session_id)
            if session is None:
                return None
            if session.is_expired(self.TTL_HOURS):
                del self._store[session_id]
                logger.info(f"Session expired and removed: {session_id[:8]}...")
                return None
            session.touch()
            return session

    def delete(self, session_id: str) -> bool:
        with self._lock:
            if session_id in self._store:
                del self._store[session_id]
                logger.info(f"Session deleted: {session_id[:8]}...")
                return True
            return False

    def update_analysis(self, session_id: str, clauses: list, risk: dict):
        """Cache classifier + risk results so /risk endpoint doesn't recompute."""
        with self._lock:
            session = self._store.get(session_id)
            if session:
                session.clauses = clauses
                session.risk    = risk
                session.touch()

    def stats(self) -> dict:
        with self._lock:
            self._evict_expired()
            return {
                "active_sessions": len(self._store),
                "max_sessions":    self.MAX_SESSIONS,
                "ttl_hours":       self.TTL_HOURS,
            }

    def _evict_expired(self):
        """Remove all expired sessions. Call inside lock."""
        expired = [sid for sid, s in self._store.items() if s.is_expired(self.TTL_HOURS)]
        for sid in expired:
            del self._store[sid]
        if expired:
            logger.info(f"Evicted {len(expired)} expired session(s)")


# Global store — one instance for the entire app lifecycle
_store = SessionStore()


# ════════════════════════════════════════════════════════
# FILE PROCESSING HELPERS
# ════════════════════════════════════════════════════════

async def _read_file_safe(file: UploadFile) -> bytes:
    """
    Read file bytes with size limit check.

    WHY: Without this, a user uploading a 500MB file consumes
    500MB of RAM before we can reject it.

    Reads in 64KB chunks. Rejects as soon as limit exceeded.
    """
    chunks     = []
    total_read = 0
    chunk_size = 64 * 1024   # 64 KB per chunk

    while True:
        chunk = await file.read(chunk_size)
        if not chunk:
            break
        total_read += len(chunk)
        if total_read > MAX_FILE_SIZE_BYTES:
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Maximum size is {MAX_FILE_SIZE_BYTES // (1024*1024)}MB."
            )
        chunks.append(chunk)

    return b"".join(chunks)


def _extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """
    Extract text from a PDF file.

    Strategy:
      1. Try direct text extraction (PyPDF) — fast, works for digital PDFs
      2. If extracted text is too short, it's a scanned PDF
         → Fall back to OCR on first page as image

    Returns extracted text string, or raises HTTPException on failure.
    """
    try:
        from pypdf import PdfReader

        reader    = PdfReader(io.BytesIO(pdf_bytes))
        all_text  = []
        num_pages = len(reader.pages)

        for i, page in enumerate(reader.pages):
            page_text = page.extract_text()
            if page_text and page_text.strip():
                all_text.append(page_text.strip())

        combined = "\n\n".join(all_text)

        # If we got decent text — return it
        if len(combined.strip()) >= MIN_TEXT_LENGTH:
            logger.info(f"PDF text extraction: {num_pages} pages, {len(combined)} chars")
            return combined

        # Not enough text — probably a scanned PDF
        logger.info("PDF has little extractable text — attempting OCR on first page")

    except ImportError:
        logger.warning("pypdf not installed. Install it: pip install pypdf")
    except Exception as e:
        logger.warning(f"PDF text extraction failed: {e} — trying OCR")

    # Fallback: OCR the PDF bytes
    # PaddleOCR can handle PDF bytes directly
    try:
        ocr_text = extract_text_from_image(pdf_bytes)
        if ocr_text and len(ocr_text.strip()) >= MIN_TEXT_LENGTH:
            logger.info(f"PDF OCR fallback succeeded: {len(ocr_text)} chars")
            return ocr_text
    except Exception as e:
        logger.error(f"PDF OCR fallback also failed: {e}")

    raise HTTPException(
        status_code=422,
        detail="Could not extract text from this PDF. It may be password-protected or corrupted."
    )


def _validate_extracted_text(text: str) -> str:
    """
    Validate OCR/PDF extraction result.

    Checks:
      - Not empty or whitespace-only
      - Not an error message from OCR engine
      - Minimum meaningful length (50 chars)
      - Has at least some alphabetic content (not just symbols)

    Returns cleaned text or raises HTTPException.
    """
    if not text or not text.strip():
        raise HTTPException(
            status_code=422,
            detail="No text could be extracted from this document. Please try a clearer image."
        )

    cleaned = text.strip()

    # Check for known OCR error messages
    error_patterns = [
        "could not extract", "could not read", "ocr error",
        "failed to process", "error:", "exception:"
    ]
    lower = cleaned.lower()
    for pattern in error_patterns:
        if lower.startswith(pattern):
            raise HTTPException(status_code=422, detail=cleaned)

    # Minimum length check
    if len(cleaned) < MIN_TEXT_LENGTH:
        raise HTTPException(
            status_code=422,
            detail=f"Extracted text is too short ({len(cleaned)} characters). "
                   f"Please upload a clearer image of the full document."
        )

    # Must have some real alphabetic content (not just numbers/symbols)
    alpha_count = sum(1 for c in cleaned if c.isalpha())
    if alpha_count < 20:
        raise HTTPException(
            status_code=422,
            detail="Could not find readable text in this document. "
                   "Make sure the document contains readable text."
        )

    return cleaned


# ════════════════════════════════════════════════════════
# REQUEST / RESPONSE MODELS
# ════════════════════════════════════════════════════════

class SessionReq(BaseModel):
    session_id: str
    force_reanalyze: bool = False   # Set True to re-run classifier even if cached


# ════════════════════════════════════════════════════════
# ENDPOINT 1: Upload document (image or PDF)
# POST /analyze/upload
# ════════════════════════════════════════════════════════
@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    session_id: str  = Query(default="", description="Session ID. Auto-generated if not provided.")
):
    """
    Upload a document (image or PDF) for analysis.

    Pipeline:
      File → Type validation → Size check → Text extraction
      → Privacy guard → Session store → Classify clauses → Risk score

    Returns complete analysis in one response.
    """
    request_start = time.monotonic()
    timings = {}

    # ── Auto-generate session_id if not provided ─────
    # WHY: If frontend sends no session_id, default="default"
    # means ALL users share ONE session — a serious data leak.
    if not session_id or session_id.strip() == "":
        session_id = str(uuid.uuid4())
        logger.info(f"Auto-generated session_id: {session_id[:8]}...")

    filename = file.filename or "unknown"
    logger.info(f"Upload request: session={session_id[:8]}... file={filename} type={file.content_type}")

    # ── Validate file type ───────────────────────────
    content_type = (file.content_type or "").lower().strip()
    if content_type not in ALL_ALLOWED_TYPES:
        raise HTTPException(
            status_code=400,
            detail=(
                f"File type '{content_type}' is not supported. "
                f"Accepted types: JPG, PNG, WebP, BMP, TIFF, PDF."
            )
        )

    # ── Read file (with streaming size check) ────────
    t0 = time.monotonic()
    file_bytes = await _read_file_safe(file)
    timings["read_ms"] = int((time.monotonic() - t0) * 1000)
    file_size_kb = len(file_bytes) // 1024
    logger.info(f"File read: {file_size_kb} KB in {timings['read_ms']}ms")

    # ── Extract text based on file type ──────────────
    t0 = time.monotonic()
    is_pdf = content_type in ALLOWED_PDF_TYPES

    if is_pdf:
        raw_text = _extract_text_from_pdf(file_bytes)
        file_type_label = "pdf"
    else:
        raw_text = extract_text_from_image(file_bytes)
        file_type_label = "image"

    timings["extraction_ms"] = int((time.monotonic() - t0) * 1000)
    logger.info(f"Text extraction ({file_type_label}): {len(raw_text)} chars in {timings['extraction_ms']}ms")

    # ── Validate extracted text ───────────────────────
    raw_text = _validate_extracted_text(raw_text)

    # ── Privacy guard — remove PII ────────────────────
    t0 = time.monotonic()
    safe_text = redact_pii(raw_text)
    timings["privacy_ms"] = int((time.monotonic() - t0) * 1000)

    # ── Store in session ──────────────────────────────
    _store.set(
        session_id=session_id,
        document_text=safe_text,
        filename=filename,
        file_type=file_type_label
    )

    # ── Classify clauses ──────────────────────────────
    t0 = time.monotonic()
    clauses = classify_clauses(safe_text)
    timings["classify_ms"] = int((time.monotonic() - t0) * 1000)
    logger.info(f"Classification: {len(clauses)} clauses in {timings['classify_ms']}ms")

    # ── Calculate risk score ──────────────────────────
    t0 = time.monotonic()
    risk = calculate_risk_score(safe_text, clauses)
    timings["risk_ms"] = int((time.monotonic() - t0) * 1000)
    logger.info(f"Risk scoring: score={risk['score']} in {timings['risk_ms']}ms method={risk.get('scoring_method','?')}")

    # ── Cache analysis results ────────────────────────
    _store.update_analysis(session_id, clauses, risk)

    total_ms = int((time.monotonic() - request_start) * 1000)
    timings["total_ms"] = total_ms
    logger.info(f"Upload complete: session={session_id[:8]}... total={total_ms}ms")

    return {
        "success":       True,
        "session_id":    session_id,
        "filename":      filename,
        "file_type":     file_type_label,
        "file_size_kb":  file_size_kb,
        "total_chars":   len(safe_text),
        "text_preview":  safe_text[:600],
        "clauses":       clauses,
        "clause_count":  len(clauses),
        "high_risk_count": sum(1 for c in clauses if c.get("risk_level") == "high"),
        "risk":          risk,
        "timings_ms":    timings,
        "message":       "Document analyzed successfully!",
    }


# ════════════════════════════════════════════════════════
# ENDPOINT 2: Re-run or retrieve risk analysis
# POST /analyze/risk
# ════════════════════════════════════════════════════════
@router.post("/risk")
async def get_risk(req: SessionReq):
    """
    Get risk analysis for an uploaded document.

    If force_reanalyze=False (default):
      → Returns CACHED clauses + risk (no extra API calls, instant)
    If force_reanalyze=True:
      → Runs classifier + risk engine again (fresh, costs API call)

    WHY CACHE: The old version re-ran classify_clauses() every time.
    That's a Groq API call every click. Caching is free and consistent.
    """
    session = _store.get(req.session_id)
    if not session:
        raise HTTPException(
            status_code=404,
            detail="Session not found or expired. Please upload your document again."
        )

    # Return cached result (default, fast path)
    if not req.force_reanalyze and session.clauses:
        logger.info(f"Returning cached analysis for session {req.session_id[:8]}...")
        return {
            "session_id":  req.session_id,
            "risk":        session.risk,
            "clauses":     session.clauses,
            "cached":      True,
        }

    # Re-analyze (slow path, fresh API call)
    logger.info(f"Re-analyzing session {req.session_id[:8]}... (force={req.force_reanalyze})")
    clauses = classify_clauses(session.document_text)
    risk    = calculate_risk_score(session.document_text, clauses)
    _store.update_analysis(req.session_id, clauses, risk)

    return {
        "session_id":  req.session_id,
        "risk":        risk,
        "clauses":     clauses,
        "cached":      False,
    }


# ════════════════════════════════════════════════════════
# ENDPOINT 3: Get stored document text
# GET /analyze/doc/{session_id}
# ════════════════════════════════════════════════════════
@router.get("/doc/{session_id}")
async def get_document(session_id: str):
    """
    Retrieve stored document text for a session.
    Used by chat routes to get document context for AI answers.
    """
    session = _store.get(session_id)
    if not session:
        return {
            "session_id":    session_id,
            "has_document":  False,
            "document_text": "",
            "total_chars":   0,
        }

    return {
        "session_id":    session_id,
        "has_document":  True,
        "document_text": session.document_text,
        "total_chars":   session.char_count,
        "filename":      session.filename,
        "file_type":     session.file_type,
        "clauses":       session.clauses,
    }


# ════════════════════════════════════════════════════════
# ENDPOINT 4: Delete session (clear document)
# DELETE /analyze/doc/{session_id}
# ════════════════════════════════════════════════════════
@router.delete("/doc/{session_id}")
async def delete_document(session_id: str):
    """Clear a session and its document. Called on 'Start Fresh' button."""
    deleted = _store.delete(session_id)
    return {
        "success":    deleted,
        "session_id": session_id,
        "message":    "Session cleared." if deleted else "Session not found (may have already expired)."
    }


# ════════════════════════════════════════════════════════
# ENDPOINT 5: Session store health stats
# GET /analyze/stats
# (useful for monitoring / admin dashboard)
# ════════════════════════════════════════════════════════
@router.get("/stats")
async def get_stats():
    """Returns session store statistics. Useful for monitoring."""
    return _store.stats()