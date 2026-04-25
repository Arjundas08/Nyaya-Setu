# ════════════════════════════════════════════════════════
# FILE: backend/services/doc_vectorstore.py  ← NEW FILE
# ════════════════════════════════════════════════════════
#
# WHAT THIS FILE DOES:
#   Creates a tiny, per-user FAISS vector index from their
#   uploaded document. Lives in RAM, auto-expires with session.
#
# WHY FAISS (not ChromaDB)?
#   ChromaDB is for permanent storage (our 14 law PDFs).
#   A user's contract is temporary — 1 document, ~20 chunks.
#   FAISS in-memory is perfect: fast, no disk I/O, instant cleanup.
#
# HOW IT FITS IN THE FLOW:
#   upload_document() → build_doc_store() ← called here
#   ask_lawyer()      → search_doc_store() ← called here
#   clear_session()   → delete_doc_store() ← called here
# ════════════════════════════════════════════════════════

import logging
import threading
import time
from datetime import datetime, timedelta
from typing import Optional
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

logger = logging.getLogger(__name__)

# ════════════════════════════════════════════════════════
# CONFIGURATION
# ════════════════════════════════════════════════════════
CHUNK_SIZE    = 600    # Characters per chunk (smaller than law PDFs)
               # WHY 600? A contract clause is ~100-200 words.
               # 600 chars ≈ 1 clause = perfect retrieval granularity.
               # Too big = returns irrelevant context.
               # Too small = cuts clauses in half.

CHUNK_OVERLAP = 100    # Overlap between chunks
               # Prevents a clause from being split across two chunks.

TOP_K_DOC     = 3      # How many contract chunks to retrieve per query
TTL_HOURS     = 2      # Session auto-expires after 2 hours of inactivity


# ════════════════════════════════════════════════════════
# SESSION ENTRY — stores one user's doc vector store
# ════════════════════════════════════════════════════════
class _DocStoreEntry:
    def __init__(self, session_id: str, vectorstore: FAISS, chunk_count: int):
        self.session_id    = session_id
        self.vectorstore   = vectorstore   # FAISS index in RAM
        self.chunk_count   = chunk_count
        self.created_at    = datetime.utcnow()
        self.last_accessed = datetime.utcnow()

    def touch(self):
        self.last_accessed = datetime.utcnow()

    def is_expired(self) -> bool:
        return datetime.utcnow() - self.last_accessed > timedelta(hours=TTL_HOURS)


# ════════════════════════════════════════════════════════
# DOC VECTOR STORE MANAGER
# Thread-safe. One FAISS index per user session.
# ════════════════════════════════════════════════════════
class _DocVectorStoreManager:

    def __init__(self):
        self._stores: dict[str, _DocStoreEntry] = {}
        self._lock   = threading.Lock()
        self._splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
            separators=["\n\n", "\n", ". ", " ", ""]
        )

    def build(self, session_id: str, document_text: str,
              embeddings) -> int:
        """
        Split document into chunks → embed → store in FAISS.

        INPUT:
          session_id    → unique session identifier
          document_text → full OCR/PDF-extracted text
          embeddings    → HuggingFace embedding model (shared from rag.py)
                          We reuse rag.py's embedding model so it's only
                          loaded once — not twice.

        OUTPUT:
          chunk_count   → number of chunks indexed

        PERFORMANCE:
          A 2000-char contract → ~4 chunks → ~0.1 seconds
          A 10000-char contract → ~20 chunks → ~0.5 seconds
        """
        if not document_text or not document_text.strip():
            logger.warning(f"build_doc_store called with empty text for {session_id[:8]}...")
            return 0

        try:
            t_start = time.monotonic()

            # Step 1: Split into chunks
            raw_chunks = self._splitter.split_text(document_text)

            if not raw_chunks:
                logger.warning(f"No chunks created for session {session_id[:8]}...")
                return 0

            # Step 2: Wrap in Document objects with metadata
            # The metadata tells the AI WHERE this text came from
            docs = [
                Document(
                    page_content=chunk,
                    metadata={
                        "source":     "uploaded_contract",   # ← key metadata
                        "chunk_index": i,
                        "session_id":  session_id,
                    }
                )
                for i, chunk in enumerate(raw_chunks)
            ]

            # Step 3: Create FAISS index from documents
            # This embeds every chunk using HuggingFace model
            vectorstore = FAISS.from_documents(docs, embeddings)

            # Step 4: Store with TTL
            with self._lock:
                self._evict_expired()
                self._stores[session_id] = _DocStoreEntry(
                    session_id=session_id,
                    vectorstore=vectorstore,
                    chunk_count=len(docs)
                )

            elapsed = (time.monotonic() - t_start) * 1000
            logger.info(
                f"Doc store built: session={session_id[:8]}... "
                f"chunks={len(docs)} time={elapsed:.0f}ms"
            )
            return len(docs)

        except Exception as e:
            logger.error(f"Failed to build doc store for {session_id[:8]}...: {e}")
            return 0

    def search(self, session_id: str, query: str) -> list[Document]:
        """
        Search the user's document for text relevant to the query.

        Returns list of Document objects (contract chunks).
        Returns [] if no store exists for this session.
        """
        with self._lock:
            entry = self._stores.get(session_id)
            if not entry:
                return []
            if entry.is_expired():
                del self._stores[session_id]
                logger.info(f"Doc store expired: {session_id[:8]}...")
                return []
            entry.touch()

        try:
            results = entry.vectorstore.similarity_search(query, k=TOP_K_DOC)
            logger.debug(
                f"Doc store search: session={session_id[:8]}... "
                f"query='{query[:40]}' found={len(results)} chunks"
            )
            return results
        except Exception as e:
            logger.error(f"Doc store search error: {e}")
            return []

    def delete(self, session_id: str) -> bool:
        """Remove session's doc store. Called on session clear."""
        with self._lock:
            if session_id in self._stores:
                del self._stores[session_id]
                logger.info(f"Doc store deleted: {session_id[:8]}...")
                return True
            return False

    def has_store(self, session_id: str) -> bool:
        """Check if a session has a doc store built."""
        with self._lock:
            entry = self._stores.get(session_id)
            if not entry or entry.is_expired():
                return False
            return True

    def stats(self, session_id: str) -> dict:
        """Get stats for a session's doc store."""
        with self._lock:
            entry = self._stores.get(session_id)
            if not entry:
                return {"has_store": False}
            return {
                "has_store":   True,
                "chunk_count": entry.chunk_count,
                "created_at":  entry.created_at.isoformat(),
                "expired":     entry.is_expired(),
            }

    def _evict_expired(self):
        """Remove all expired stores. Must be called inside lock."""
        expired = [sid for sid, e in self._stores.items() if e.is_expired()]
        for sid in expired:
            del self._stores[sid]
        if expired:
            logger.info(f"Evicted {len(expired)} expired doc store(s)")


# ════════════════════════════════════════════════════════
# GLOBAL INSTANCE — one manager for entire app lifecycle
# ════════════════════════════════════════════════════════
_manager = _DocVectorStoreManager()


# ════════════════════════════════════════════════════════
# PUBLIC API — these are the 4 functions used by other files
# ════════════════════════════════════════════════════════

def build_doc_store(session_id: str, document_text: str) -> int:
    """
    Build a FAISS vector index from a user's document.
    Call this ONCE after OCR, in routes/analyze.py upload endpoint.

    Returns number of chunks indexed (0 if failed).
    Never raises — all errors logged and handled gracefully.
    """
    # Import embeddings from rag.py to reuse the already-loaded model
    # This is critical — we must NOT load a second copy of the 90MB model
    try:
        # Add backend to path so 'services' is importable
        import sys as _sys, os as _os
        _backend = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
        if _backend not in _sys.path:
            _sys.path.insert(0, _backend)
        from services.rag import _embeddings
        if _embeddings is None:
            logger.error("Embedding model not loaded in rag.py")
            return 0
        return _manager.build(session_id, document_text, _embeddings)
    except ImportError as e:
        logger.error(f"Cannot import embeddings from rag.py: {e}")
        return 0


def search_doc_store(session_id: str, query: str) -> list[Document]:
    """
    Search user's document for query-relevant chunks.
    Call this in rag.py ask_lawyer() before building the prompt.

    Returns list of Document objects. Empty list if no store.
    """
    return _manager.search(session_id, query)


def delete_doc_store(session_id: str) -> bool:
    """
    Delete doc store for a session.
    Call this when user clears session or uploads new document.
    """
    return _manager.delete(session_id)


def has_doc_store(session_id: str) -> bool:
    """Check if session has a valid doc store. Used in rag.py."""
    return _manager.has_store(session_id)


def get_doc_store_stats(session_id: str) -> dict:
    """Get doc store stats. Used by dashboard endpoint."""
    return _manager.stats(session_id)