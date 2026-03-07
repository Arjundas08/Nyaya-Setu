import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.schema import HumanMessage, AIMessage, SystemMessage

os.environ["ANONYMIZED_TELEMETRY"] = "False"   # disables ChromaDB telemetry

load_dotenv()

# CONFIG
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
CHROMA_PATH = "chroma_db"
COLLECTION = "nyaya_setu_laws"
EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


# STEP 1: Load Groq
print("Loading Groq LLM...")

llm = ChatGroq(
    api_key=GROQ_API_KEY,
    model_name="llama-3.1-8b-instant",
    temperature=0.1,
    max_tokens=2000
)

print("✅ Groq LLM ready")


# STEP 2: Load ChromaDB
print("Loading ChromaDB...")

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
        search_kwargs={"k": 4}
    )

    _chunk_count = _vectorstore._collection.count()

    print(f"✅ ChromaDB loaded — {_chunk_count} law chunks ready")

except Exception as e:

    print(f"⚠️ ChromaDB not found: {e}")
    print("Run: python scripts/build_knowledge_base.py first!")

    _vectorstore = None
    _retriever = None


# SYSTEM PROMPT
SYSTEM_PROMPT = """
You are Nyaya-Setu, a Virtual Legal Assistant for Indian citizens.

Your goal: help people understand their legal rights in simple language.

Key rules:
1. Cite specific law sections
2. Use simple explanations
3. Mark risky clauses with ⚠️
4. Respond in user's language
5. End with 'Next Steps'
"""


# MEMORY STORE
_memories = {}


def _get_history(session_id: str):

    if session_id not in _memories:
        _memories[session_id] = []

    return _memories[session_id]


def clear_session(session_id: str):

    if session_id in _memories:
        del _memories[session_id]


# MAIN FUNCTION
def ask_lawyer(question: str, document_text: str, session_id: str):

    retrieved_text = ""
    sources_used = []
    chunks_found = 0

    if _retriever:

        try:

            chunks = _retriever.invoke(question)

            chunks_found = len(chunks)

            pieces = []

            for chunk in chunks:

                act_name = chunk.metadata.get("act_name", "Unknown Act")

                text = chunk.page_content.strip()

                pieces.append(f"[{act_name}]\n{text}")

                if act_name not in sources_used:
                    sources_used.append(act_name)

            retrieved_text = "\n\n".join(pieces)

        except Exception as e:

            print("ChromaDB retrieval error:", e)

    messages = []

    messages.append(SystemMessage(content=SYSTEM_PROMPT))

    if retrieved_text:

        messages.append(SystemMessage(
            content=f"""
RELEVANT LAW SECTIONS FROM DATABASE

{retrieved_text}

Use these sections to answer accurately.
"""
        ))

    if document_text and document_text.strip():

        doc_preview = document_text[:3000]

        messages.append(SystemMessage(
            content=f"""
USER DOCUMENT

{doc_preview}

Analyze this document together with law sections.
"""
        ))

    history = _get_history(session_id)

    for msg in history[-6:]:
        messages.append(msg)

    messages.append(HumanMessage(content=question))

    try:

        response = llm.invoke(messages)

        answer = response.content

        history.append(HumanMessage(content=question))
        history.append(AIMessage(content=answer))

        return {
            "answer": answer,
            "sources": sources_used,
            "chunks_used": chunks_found
        }

    except Exception as e:

        return {
            "answer": f"Error: {str(e)}",
            "sources": [],
            "chunks_used": 0
        }