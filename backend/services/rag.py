# ════════════════════════════════════════════════════════
# FILE: backend/services/rag.py  ← REPLACE ENTIRE FILE
# ════════════════════════════════════════════════════════
#
# KEY CHANGES FROM PREVIOUS VERSION:
#
#   1. _embeddings is now exported (used by doc_vectorstore.py)
#   2. ask_lawyer() now does DUAL SEARCH:
#        → search_doc_store()   ← user's contract (NEW)
#        → ChromaDB retriever   ← law PDFs (existing)
#   3. Prompt is restructured with 3 clear sections:
#        → CONTRACT CONTEXT (from FAISS)
#        → LAW CONTEXT (from ChromaDB)
#        → CONVERSATION HISTORY
#   4. Fixed: get_relevant_documents() → invoke() (deprecation)
#   5. Fixed: llm.invoke() → _llm.invoke() (NameError bug)
# ════════════════════════════════════════════════════════

import os
import logging
import time

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

load_dotenv()

# Disable ChromaDB telemetry noise
os.environ["ANONYMIZED_TELEMETRY"] = "False"

logger = logging.getLogger(__name__)

# ════════════════════════════════════════════════════════
# CONFIGURATION
# ════════════════════════════════════════════════════════
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
CHROMA_PATH  = "chroma_db"
COLLECTION   = "nyaya_setu_laws"
EMBED_MODEL  = "sentence-transformers/all-MiniLM-L6-v2"

if not GEMINI_API_KEY:
    print("⚠️ WARNING: GEMINI_API_KEY not set — LLM features will not work")

# ════════════════════════════════════════════════════════
# LOAD GEMINI LLM
# ════════════════════════════════════════════════════════
_llm = None
try:
    if GEMINI_API_KEY:
        print("Loading Gemini LLM...")
        _llm = ChatGoogleGenerativeAI(
            google_api_key=GEMINI_API_KEY,
            model=os.getenv("GEMINI_MODEL", "gemini-2.0-flash"),
            temperature=0.1,
            max_tokens=1024,
            request_timeout=30,
        )
        print("✅ Gemini LLM ready")
except Exception as e:
    print(f"⚠️ Gemini LLM failed to load: {e}")


# ════════════════════════════════════════════════════════
# LOAD EMBEDDING MODEL
# IMPORTANT: _embeddings is exported — doc_vectorstore.py
# imports it to reuse the same model instance.
# This prevents loading the 90MB model twice.
# ════════════════════════════════════════════════════════
print("Loading ChromaDB...")
_embeddings  = None   # exported — used by doc_vectorstore.py
_vectorstore = None
_retriever   = None

try:
    _embeddings = HuggingFaceEmbeddings(
        model_name=EMBED_MODEL,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True}
    )
    _vectorstore = Chroma(
        persist_directory=CHROMA_PATH,
        embedding_function=_embeddings,
        collection_name=COLLECTION
    )
    _retriever = _vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 3}   # Top 3 law chunks — k=4 was hitting TPM limit
    )
    chunk_count = _vectorstore._collection.count()
    print(f"✅ ChromaDB loaded — {chunk_count} law chunks ready")

except Exception as e:
    print(f"⚠️  ChromaDB failed to load: {e}")
    print("   Run: python scripts/build_knowledge_base.py")


# ════════════════════════════════════════════════════════
# SYSTEM PROMPT
# ════════════════════════════════════════════════════════
SYSTEM_PROMPT = """You are Nyaya-Setu, a Virtual Legal Assistant for Indian citizens. However, your personality is NOT a strict, boring lawyer. You are a highly empathetic, supportive, and incredibly helpful "best friend" who just happens to know Indian law perfectly. 

You MUST explain legal concepts in the simplest, most easy-to-understand way possible, as if explaining it to a close friend over a cup of chai. NEVER use complicated legal jargon without immediately explaining what it means in simple terms. Be warm, reassuring, and always on the user's side.

━━━ CRITICAL LEGAL UPDATES (July 1, 2024) ━━━
• BNS 2023 replaced IPC 1860 (criminal offences)
• BNSS 2023 replaced CrPC (criminal procedure)
• BSA 2023 replaced Indian Evidence Act
Rule: Before July 2024 = IPC. After July 2024 = BNS.
IT Act Section 66A was STRUCK DOWN by Supreme Court (2015) — no longer valid.

YOUR RULES:
1. Speak like a supportive friend ("Don't worry, here's what this means for you...", "Basically, this clause is saying...").
2. When answering about a CONTRACT: cite the actual clause text first, then the law.
3. When citing contract text: use format → "Your contract states: [exact text]"
4. When citing law: use format → "Under [Act Name] Section [X]..."
5. Use extremely simple language — absolutely zero confusing legal jargon!
6. Mark risky clauses with ⚠️ and explain why they are bad in simple terms.
7. Always end with "📋 Next Steps:" — 2-3 concrete, friendly, and easy actions they can take right now.
8. If domestic violence question → be extremely gentle and include the Women's Helpline: 1091.
9. NEVER invent clauses or law sections."""


# ════════════════════════════════════════════════════════
# MEMORY STORE — chat history per session
# ════════════════════════════════════════════════════════
_memories: dict = {}

def _get_history(session_id: str) -> list:
    if session_id not in _memories:
        _memories[session_id] = []
    return _memories[session_id]

def clear_session(session_id: str):
    """Clear chat memory AND document vector store."""
    if session_id in _memories:
        del _memories[session_id]
    # Also clear the doc vector store
    try:
        from services.doc_vectorstore import delete_doc_store
        delete_doc_store(session_id)
    except Exception:
        pass


# ════════════════════════════════════════════════════════
# DUAL SEARCH — the core of Upgrade 1
# ════════════════════════════════════════════════════════
def _search_contract(session_id: str, query: str) -> list:
    """
    Search the user's uploaded contract for relevant clauses.
    Returns list of Document objects from their contract.
    """
    try:
        from services.doc_vectorstore import search_doc_store, has_doc_store
        if not has_doc_store(session_id):
            return []
        return search_doc_store(session_id, query)
    except Exception as e:
        logger.error(f"Contract search error: {e}")
        return []


def _search_laws(query: str) -> list:
    """
    Search the global ChromaDB for relevant law sections.
    Returns list of Document objects from law PDFs.
    """
    if not _retriever:
        return []
    try:
        return _retriever.invoke(query)
    except Exception as e:
        logger.error(f"Law search error: {e}")
        return []


def _build_dual_context(
    contract_chunks: list,
    law_chunks: list
) -> tuple[str, list]:
    """
    Combine contract chunks + law chunks into a single context string.
    Returns (context_text, sources_list).
    """
    parts   = []
    sources = []

    # Section 1: User's contract (if found)
    if contract_chunks:
        parts.append("══ RELEVANT CLAUSES FROM YOUR UPLOADED CONTRACT ══")
        for i, chunk in enumerate(contract_chunks):
            text = chunk.page_content.strip()[:400]   # cap per chunk to save tokens
            parts.append(f"[Contract Clause {i+1}]\n{text}")
        parts.append("══ END OF CONTRACT CONTEXT ══")

    # Section 2: Relevant law (from ChromaDB)
    if law_chunks:
        parts.append("\n══ RELEVANT INDIAN LAW SECTIONS ══")
        for chunk in law_chunks:
            act_name  = chunk.metadata.get("act_name", "Indian Law")
            act_short = chunk.metadata.get("act_short", "")
            text      = chunk.page_content.strip()[:400]   # cap per chunk to save tokens
            parts.append(f"[{act_name}]\n{text}")
            if act_name not in sources:
                sources.append(act_name)
        parts.append("══ END OF LAW CONTEXT ══")

    return "\n\n".join(parts), sources


# ════════════════════════════════════════════════════════
# MAIN FUNCTION — ask_lawyer()
# ════════════════════════════════════════════════════════
def ask_lawyer(question: str, document_text: str, session_id: str) -> dict:
    """
    Answer a legal question using DUAL SEARCH:
      1. Search user's contract (session FAISS)
      2. Search law PDFs (global ChromaDB)

    INPUT:
      question      → user's question string
      document_text → raw text from upload (used as fallback context)
      session_id    → user's session ID

    OUTPUT:
      answer        → AI answer string
      sources       → list of law Acts cited
      chunks_used   → total chunks retrieved
      contract_hits → how many chunks came from user's contract
      law_hits      → how many chunks came from law PDFs
    """
    t_start = time.monotonic()

    # ── STEP 1: Dual search ─────────────────────────────
    contract_chunks = _search_contract(session_id, question)
    law_chunks      = _search_laws(question)

    logger.info(
        f"Dual search: session={session_id[:8]}... "
        f"contract_hits={len(contract_chunks)} "
        f"law_hits={len(law_chunks)}"
    )

    # ── STEP 2: Build combined context ──────────────────
    context_text, sources = _build_dual_context(contract_chunks, law_chunks)

    # ── STEP 3: Build message chain ─────────────────────
    messages = []

    # System prompt — who the AI is
    messages.append(SystemMessage(content=SYSTEM_PROMPT))

    # Combined context (contract + law)
    if context_text:
        messages.append(SystemMessage(
            content=f"RETRIEVED CONTEXT — use this to answer accurately:\n\n{context_text}"
        ))

    # Fallback: if FAISS not built yet, use raw document text
    if not contract_chunks and document_text and document_text.strip():
        fallback = document_text[:1200]   # ← reduced: was 2000
        messages.append(SystemMessage(
            content=f"USER'S DOCUMENT (direct text — no vector search):\n{fallback}"
        ))
        logger.debug(f"Using document text fallback for {session_id[:8]}...")

    # Previous conversation — last 4 messages (2 exchanges) — reduced from 6 to save tokens
    history = _get_history(session_id)
    for msg in history[-4:]:
        messages.append(msg)

    # Current question
    messages.append(HumanMessage(content=question))

    # ── STEP 4: Get answer from Groq ────────────────────
    try:
        response = _llm.invoke(messages)   # ← FIX: was bare `llm` (NameError)
        answer   = response.content

        # Save to memory
        history.append(HumanMessage(content=question))
        history.append(AIMessage(content=answer))

        elapsed_ms = int((time.monotonic() - t_start) * 1000)
        logger.info(
            f"ask_lawyer complete: {elapsed_ms}ms "
            f"answer_len={len(answer)} sources={len(sources)}"
        )

        return {
            "answer":        answer,
            "sources":       sources,
            "chunks_used":   len(contract_chunks) + len(law_chunks),
            "contract_hits": len(contract_chunks),
            "law_hits":      len(law_chunks),
            "elapsed_ms":    elapsed_ms,
        }

    except Exception as e:
        logger.error(f"Gemini LLM error: {e}")
        return {
            "answer":        f"Sorry, I encountered an error: {str(e)}. Please try again.",
            "sources":       [],
            "chunks_used":   0,
            "contract_hits": 0,
            "law_hits":      0,
            "elapsed_ms":    0,
        }