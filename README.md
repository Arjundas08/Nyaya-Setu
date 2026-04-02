# nyaya-setu
# ⚖️ Nyaya-Setu — न्याय सेतु
### Bridge to Justice · AI-Powered Legal Assistance for Every Indian Citizen

> **"Every Indian deserves to know their rights — before they sign any paper."**

---

## 🇮🇳 What is Nyaya-Setu?

**Nyaya-Setu** (Hindi for "Legal Bridge") is a free, AI-powered legal assistance platform built for Indian citizens who cannot afford a lawyer. It translates complex Indian law into plain language across **5 languages** — Hindi, Telugu, Tamil, Kannada, and English.

Most Indians sign employment contracts, rental agreements, or loan documents without understanding what they are agreeing to. By the time they discover an illegal clause or a violated right, it is often too late. Nyaya-Setu solves this by bringing legal intelligence to every citizen — not just those who can pay for it.

**Built by:** D. Arjun, P. Jayanth, G. Pavan Teja
**Institution:** CVR College of Engineering, Hyderabad
**Domain:** nyayasetu.me
**Project Type:** B.Tech Final Year Project (Non-commercial)

---

## 📊 Project at a Glance

| Metric | Value |
|---|---|
| Total Lines of Code | 7,313 |
| Frontend Pages | 7 |
| Backend API Endpoints | 14 |
| Indian Law Chunks (ChromaDB) | 3,593 |
| Indian Court Judgments (IK API) | 3 Crore+ |
| Tests Passing | 78 / 78 |
| Languages Supported | 5 |
| Legal Document Templates | 5 |
| Verified Landmark Fallback Cases | 16 |

---

## 🔥 The 7 Features

### 1 — The Witness Stand (Contract Scanner)
Upload any employment or rental contract (image, PDF, or camera photo). The system:
- Extracts text using **PaddleOCR** — handles low-quality scans, rotated images, multiple scripts
- Removes all personal information (Aadhaar, PAN, phone) **before** any AI sees the text
- Identifies **14 clause types** using pattern matching against known illegal patterns
- Scores overall risk **0–10** using hybrid scoring: 60% rule-based + 40% LLM
- Explains every risky clause with: the Indian law it violates, why it's risky, severity score 1–10, negotiation advice, and whether the clause is even legally enforceable

### 2 — Virtual Advocate (AI Legal Chat)
Ask any legal question in your own language. Uses **Dual Search**:
- Searches your uploaded contract (per-session FAISS vector store)
- Searches 14 Indian law PDFs simultaneously (ChromaDB with 3,593 chunks)
- Combines both results into one Groq LLM prompt
- Answers in the same language as the question

### 3 — Case Archives (Real Court Judgments)
Search 3 crore real Indian court judgments in plain words. You type "my landlord won't return my deposit" — the system:
- Builds a smart keyword query from your actual words (not generic templates)
- Calls the Indian Kanoon API for real Supreme Court and High Court judgments
- Fetches actual judgment text from the top 2 results
- Uses AI to score every case 0–100 for relevance to your specific situation
- Discards anything scoring below 55 — only shows 2–3 highly relevant cases
- Explains every result in plain language: what the court decided, what it means for you

### 4 — Document Forge (Legal Document Generator)
Generates 5 types of ready-to-use legal documents in seconds:
- RTI Application (Right to Information Act, 2005)
- Legal Notice (Indian Contract Act, 1872)
- Rental Agreement (Transfer of Property Act, 1882)
- Consumer Complaint (Consumer Protection Act, 2019)
- Employment Grievance Letter (Industrial Disputes Act, 1947)

All 5 templates are embedded directly in the Python file — zero backend dependency, instant generation.

### 5 — The Oracle (Outcome Predictor)
Describe your legal situation. The system:
- Searches Indian Kanoon for real precedents matching your case type
- Fetches actual judgment text from top results
- Feeds real case law as context to the AI (not just category keywords)
- Returns: Win probability (0–100%), recommended court or forum, expected timeline, 3–4 specific legal strengths, 2–3 honest risks, numbered 4-step action roadmap, applicable law sections, and settlement advice if relevant

### 6 — Chamber Records (Session Dashboard)
Full history of all past document analyses from MongoDB:
- 4 animated stats cards (total analyses, high risk count, safe count, average score)
- Risk distribution bar (proportional red / amber / green)
- Every past analysis with mini gauge, clause count, top concerns as chips
- Click any record to expand full details inline
- Three action buttons per record: Ask about this doc → Chat, Predict outcome → Oracle, Generate notice → Document Forge

### 7 — Home Page
- 8 rotating "Did You Know" law quotes — JS-powered auto-slider, no page reload, dot navigation, pause/play, 7-second auto-advance
- Intelligence HUD with 5 animated statistics
- All 7 feature cards with hover lift and glow transitions
- Auto-scrolling laws ticker (all 14 acts)
- 6 emergency helplines always visible
- Free Legal Aid finder with Google Maps integration
- Constitution Article 39A banner
- Floating gold particle background

---

## 🏗️ System Architecture

```
┌──────────────────────────────────────────────────────┐
│                  BROWSER (User)                      │
└────────────────────────┬─────────────────────────────┘
                         │
┌────────────────────────▼─────────────────────────────┐
│          FRONTEND — Streamlit :8501                  │
│  app.py (home) + 6 sub-pages                        │
│  Gold over Obsidian design system                   │
│  Custom HTML/CSS/JS — no React, no Node             │
└────────────────────────┬─────────────────────────────┘
                         │  HTTP POST / GET
┌────────────────────────▼─────────────────────────────┐
│          BACKEND — FastAPI :8000                     │
│  14 endpoints across 6 route files                  │
│  Pydantic validation · Uvicorn ASGI server          │
│  Swagger UI at /docs                                │
└──┬──────────┬──────────┬──────────┬──────────────────┘
   │          │          │          │
┌──▼──┐  ┌───▼──┐  ┌────▼──┐  ┌───▼──────┐
│ChromaDB│ │FAISS │  │MongoDB│  │ Groq API │
│3,593  │  │per-  │  │Atlas  │  │llama-3.1 │
│law    │  │user  │  │persist│  │-8b-inst  │
│chunks │  │TTL2h │  │history│  │(LLM)     │
└───────┘  └──────┘  └───────┘  └──────────┘
                                      │
                               ┌──────▼──────┐
                               │Indian Kanoon│
                               │API — 3Cr+   │
                               │judgments    │
                               └─────────────┘
```

---

## 🗂️ Project Structure

```
nyaya-setu-1/
├── backend/
│   ├── main.py                    # FastAPI app, all 6 routers registered
│   ├── routes/
│   │   ├── analyze.py             # /analyze/* — full upload pipeline
│   │   ├── chat.py                # /chat/ask, /chat/clear
│   │   ├── search.py              # /search/cases — IK + AI relevance filter
│   │   ├── generate.py            # /generate/document, /generate/templates
│   │   ├── predict.py             # /predict/outcome — Oracle pipeline
│   │   └── dashboard.py           # /dashboard/* — history + stats
│   └── services/
│       ├── rag.py                 # DUAL SEARCH ENGINE (most critical file)
│       ├── risk_engine.py         # Explainable risk with Indian law citations
│       ├── classifier.py          # 14 clause type detector
│       ├── doc_vectorstore.py     # Per-session FAISS (TTL 2hr, max 500 sessions)
│       ├── indiankanoon.py        # IK API client + smart query builder
│       ├── knowledge_base.py      # ChromaDB loader and PDF chunker
│       ├── database.py            # MongoDB operations — save/get/recent/stats
│       ├── privacy.py             # PII removal before any AI processing
│       ├── ocr.py                 # PaddleOCR text extraction
│       ├── voice.py               # Bhashini API + gTTS fallback
│       ├── case_search.py         # Local case search fallback
│       ├── doc_generator.py       # Template variable substitution
│       └── outcome_predictor.py   # Oracle logic
├── frontend/
│   ├── app.py                     # Home page — 957 lines
│   ├── nyayasetu_logo.jpg         # Logo file
│   ├── nyaya_setu_bridge.png      # Background image
│   └── pages/
│       ├── 1_chat.py              # Virtual Advocate — 339 lines
│       ├── 2_upload.py            # Witness Stand — 665 lines
│       ├── 3_case_search.py       # Case Archives — 531 lines
│       ├── 4_generator.py         # Document Forge — 779 lines
│       ├── 5_predict.py           # The Oracle — 733 lines
│       └── 6_dashboard.py         # Chamber Records — 654 lines
├── data/
│   ├── legal_pdfs/                # 14 Indian law PDFs
│   ├── case_law/cases.json        # Local case data
│   └── templates/                 # 5 document template files (stubs)
├── chroma_db/                     # 3,593 law chunks — gitignored (200MB+)
├── tests/
│   ├── test_document_chat.py      # 27 tests — Upgrade 1: Document Chat
│   └── test_risk_explainer.py     # 51 tests — Upgrade 2: Explainable Risk
├── .env                           # All API keys — NEVER commit this
├── .gitignore
└── requirements.txt
```

---

## ⚙️ Tech Stack

| Layer | Technology | Version | Purpose |
|---|---|---|---|
| Frontend | Streamlit | Latest | Python-native web UI |
| Styling | Custom HTML + CSS + JS | — | Gold over Obsidian design, advanced animations |
| Backend | FastAPI + Uvicorn | Latest | Async REST API, auto Swagger docs at /docs |
| LLM | Groq — llama-3.1-8b-instant | — | 300 tokens/sec inference, free tier |
| LLM Wrapper | LangChain (langchain-groq) | Latest | Message history, retriever interface |
| Law Vector DB | ChromaDB | Latest | Persistent local vector store for law PDFs |
| Doc Vector DB | **faiss-cpu 1.7.4** | **PINNED** | Fast in-memory per-session search |
| Embeddings | sentence-transformers/all-MiniLM-L6-v2 | — | 90MB CPU model, strong legal text similarity |
| OCR | PaddleOCR | Latest | Best free OCR for Indian language documents |
| Case Law | Indian Kanoon API | — | 3 crore+ real Indian court judgments |
| Database | MongoDB Atlas | Free tier | Persistent analysis history (512MB free) |
| Voice | Bhashini API + gTTS fallback | — | Government-approved Indian language voice |
| Monitoring | Sentry | — | Production error tracking |
| Fonts | Plus Jakarta Sans + Playfair Display | Google Fonts | Clean modern body + legal serif headings |

> **CRITICAL:** `faiss-cpu` must be pinned to exactly `1.7.4`. Versions 1.7.5 and later broke LangChain's `FAISS.load_local()` and `FAISS.from_documents()` — causing silent failures that took hours to debug. Do NOT upgrade without thorough testing.

---

## 🚀 Installation & Setup

### Prerequisites
- Python 3.10 or higher
- pip (comes with Python)
- Git
- A terminal (PowerShell on Windows, Terminal on Mac/Linux)

### Step 1 — Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/nyaya-setu.git
cd nyaya-setu-1
```

### Step 2 — Create and activate virtual environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac / Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3 — Install all dependencies

```bash
pip install -r requirements.txt
```

Key packages:
```
streamlit
fastapi
uvicorn[standard]
langchain
langchain-groq
langchain-community
chromadb
faiss-cpu==1.7.4        ← MUST be exactly this version
sentence-transformers
paddleocr
paddlepaddle
pymongo
python-dotenv
requests
sentry-sdk
gtts
```

### Step 4 — Create the .env file

Create a file named `.env` in the `nyaya-setu-1/` root folder with the following contents:

```env
# Required
GROQ_API_KEY=gsk_your_groq_key_here
GROQ_MODEL=llama-3.1-8b-instant
MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/nyayasetu?retryWrites=true&w=majority

# Recommended
INDIANKANOON_API_KEY=your_ik_token_here

# Optional (for voice feature — ASR, TTS, Translation)
BHASHINI_USER_ID=your_user_id_here
BHASHINI_API_KEY=your_ulca_api_key_here
BHASHINI_INFERENCE_KEY=your_inference_api_key_here
```

**Where to get each key:**

| Key | Source | Cost |
|---|---|---|
| GROQ_API_KEY | console.groq.com — sign up with email | Free |
| MONGO_URI | cloud.mongodb.com → Create free cluster → Connect → Drivers | Free (512MB) |
| INDIANKANOON_API_KEY | api.indiankanoon.org/signup → sign up | ₹500 free credit on signup |
| BHASHINI_* (all 3) | bhashini.gov.in/ulca → My Profile → API Keys | Free (govt API) |

### Step 5 — Build the ChromaDB knowledge base

This step reads 14 Indian law PDFs, splits them into 500-character chunks, embeds them using HuggingFace, and stores them in ChromaDB. Run this once — it takes about 5 minutes.

```bash
python scripts/build_knowledge_base.py
```

This creates the `chroma_db/` folder containing 3,593 law chunks.

### Step 6 — Run the application

Open **two terminals** in the `nyaya-setu-1/` folder.

**Terminal 1 — Start the backend:**
```bash
venv\Scripts\activate
uvicorn backend.main:app --reload --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

**Terminal 2 — Start the frontend:**
```bash
venv\Scripts\activate
streamlit run frontend/app.py --server.port 8501
```

Then open your browser at **http://localhost:8501**

View the API documentation (all 14 endpoints with testing UI) at **http://localhost:8000/docs**

---

## 🔌 All 19 API Endpoints

| Method | Endpoint | What It Does |
|---|---|---|
| `POST` | `/analyze/upload` | Full pipeline: OCR → Privacy → Classify → Risk → FAISS → MongoDB |
| `POST` | `/analyze/risk` | Risk score only for pre-extracted text |
| `GET` | `/analyze/doc/{session_id}` | Retrieve session document from memory |
| `DELETE` | `/analyze/doc/{session_id}` | Delete session data and FAISS index |
| `GET` | `/analyze/stats` | In-memory store statistics |
| `POST` | `/chat/ask` | Legal question → dual search → Groq → answer |
| `POST` | `/chat/clear` | Clear chat history and FAISS for session |
| `POST` | `/search/cases` | IK search + AI relevance scoring + plain explanations |
| `POST` | `/generate/document` | Fill legal document template with user variables |
| `GET` | `/generate/templates` | List all 5 available templates |
| `POST` | `/predict/outcome` | IK case search + Groq analysis → Oracle output |
| `GET` | `/dashboard/{session_id}` | Session dashboard from memory or MongoDB fallback |
| `GET` | `/dashboard/history/all` | Last 10 analyses from MongoDB |
| `GET` | `/dashboard/stats/global` | Aggregate statistics across all sessions |
| `GET` | `/voice/status` | Check if Bhashini voice services are configured |
| `POST` | `/voice/transcribe` | Speech-to-text via Bhashini ASR |
| `POST` | `/voice/synthesize` | Text-to-speech via Bhashini TTS (gTTS fallback) |
| `POST` | `/voice/translate` | Translate text between Indian languages |
| `POST` | `/voice/detect` | Detect language of input text |

---

## 🧠 How the AI Pipeline Works

### The Dual Search Engine (rag.py)

When a user asks a legal question, two searches fire simultaneously:

```
User's question
    │
    ├──► _search_contract()
    │    └── Per-session FAISS index
    │        (chunks of the user's uploaded document)
    │        Returns: relevant clauses from their specific contract
    │
    └──► _search_laws()
         └── ChromaDB global knowledge base
             (3,593 chunks from 14 Indian law PDFs)
             Returns: relevant law sections from real statutes

Both results → _build_dual_context() → One Groq prompt → Answer
```

The answer therefore cites both the user's specific contract clauses AND the applicable law. This is what separates Nyaya-Setu from generic legal chatbots.

**Token budget (to stay within Groq free tier 6,000 TPM limit):**

| Parameter | Value | Why |
|---|---|---|
| max_tokens | 1,024 | Output budget |
| k (law chunks) | 3 | Fewer chunks = less input tokens |
| Chat history | Last 4 messages | 2 exchanges only |
| Per-chunk cap | 400 characters | Prevents one large chunk exploding context |
| Fallback doc text | 1,200 characters | When FAISS not built yet |

### Explainable Risk Scoring (risk_engine.py)

**Formula:** 60% rule-based + 40% LLM

- **Rule-based (60%):** Direct pattern matching for 14 known clause types. Fast, reliable, ~90%+ accuracy because the rules directly implement statute text.
- **LLM (40%):** Catches nuanced issues — unusual penalty structures, vague IP ownership, indirect coercion clauses. Prevents false negatives that pure rules would miss.

**Per-clause output:**
```json
{
  "clause_type":   "non_compete",
  "law_citation":  "Indian Contract Act, 1872 — Section 27",
  "why_risky":     "Restraint of trade clauses are void in India",
  "recommendation":"Negotiate to remove or limit geographically",
  "severity":      9,
  "red_flag":      true,
  "negotiable":    true
}
```

### Smart Query Builder (indiankanoon.py)

The IK API works like a court database search engine. Long sentences reduce result quality. The system extracts specific keywords from the user's actual words:

```
User types: "my landlord won't give back my security deposit"

→ Keyword rule match: ["deposit", "security deposit"]
→ Legal term: "security deposit refund landlord"
→ Category anchor: "court judgment"
→ Final query: "security deposit refund landlord tenant court judgment"
→ Max 8 words · IK returns relevant judgments
→ AI scores each 0–100 · Below 55 discarded · Top 3 shown
```

**16 verified fallback cases** are embedded in the code for when the IK API is unavailable. The screen is never blank during a demo.

---

## 🔒 Privacy & Security

### PII Removal — Before Any AI Sees Your Document

`privacy.py` runs before the text reaches Groq, Indian Kanoon, or MongoDB:

| What is Removed | Pattern | Replaced With |
|---|---|---|
| Aadhaar number | 12-digit XXXX-XXXX-XXXX format | `[AADHAAR_REMOVED]` |
| PAN card | AAAAA9999A (5 letters + 4 digits + 1 letter) | `[PAN_REMOVED]` |
| Phone numbers | +91 prefix or 10-digit mobile | `[PHONE_REMOVED]` |
| Email addresses | Standard email regex | `[EMAIL_REMOVED]` |
| Bank account numbers | 9–18 digits near banking keywords | `[ACCOUNT_REMOVED]` |

Groq's servers receive `[AADHAAR_REMOVED]` — never the actual number.

### API Key Safety

- All API keys are in `.env` only
- `.env` is in `.gitignore` — never pushed to GitHub
- Never hardcoded in any Python file
- All external API calls use HTTPS and TLS

### Session Isolation

Every user gets a unique UUID `session_id`. FAISS indexes, MongoDB documents, and chat history are all keyed by this ID. One user cannot access another user's data.

### What Data Leaves Your Device

| Destination | What Is Sent | What Is NOT Sent |
|---|---|---|
| Groq API | Document text (after PII removal), questions, recent chat history | Your actual Aadhaar, PAN, phone numbers |
| Indian Kanoon API | Search keyword query only | Your document text |
| MongoDB Atlas | Risk scores, clause data, analysis results | Raw document text |

---

## ✅ Running Tests

```bash
# Document Chat — Upgrade 1 (27 tests)
python -m pytest tests/test_document_chat.py -v

# Risk Explainer — Upgrade 2 (51 tests)
python -m pytest tests/test_risk_explainer.py -v

# All tests
python -m pytest tests/ -v

# Expected output
# 78 passed in X.XXs
```

---

## 🐛 All 8 Bugs Fixed

| # | Symptom | Root Cause | Fix |
|---|---|---|---|
| 1 | HTTP 422 on every chat message | Frontend sent `{"question":...}` but backend uses field `"message"` | Changed to `{"message": question}` |
| 2 | Raw HTML appeared as code blocks on screen | CommonMark spec: 4+ leading spaces in `st.markdown()` = `<code>` block | All HTML strings rewritten to start at column 0 |
| 3 | `NameError: name 'llm' is not defined` | `rag.py` used bare `llm.invoke()` — module variable is `_llm` with underscore | Changed to `_llm.invoke(messages)` |
| 4 | HTTP 413 — request too large | Context was 6,080 tokens; Groq free tier limit is 6,000 | Trimmed max_tokens, k, history length, chunk sizes |
| 5 | Generate Document — nothing happened | Template `.txt` files on disk are empty stubs. Error was invisible in narrow column. | All 5 templates embedded directly in Python |
| 6 | Wrong cases shown (electricity for landlord query) | Generic category template sent regardless of user's words | Rewrote `build_smart_query()` to extract from user's actual words |
| 7 | `TypeError: label_visibility` on button | `st.button()` does not support `label_visibility` — only input widgets do | Removed the parameter from all `st.button()` calls |
| 8 | New upload showed previous contract's analysis | `delete_doc_store()` was not called before `build_doc_store()` in upload route | Added delete call before every new build |

---

## 🏛️ Supported Indian Laws

| Short Code | Full Name | Year |
|---|---|---|
| IDA | Industrial Disputes Act | 1947 |
| ICA | Indian Contract Act | 1872 |
| RTI | Right to Information Act | 2005 |
| CPA | Consumer Protection Act | 2019 |
| TPA | Transfer of Property Act | 1882 |
| BNS | Bharatiya Nyaya Sanhita | 2023 |
| BNSS | Bharatiya Nagarik Suraksha Sanhita | 2023 |
| BSA | Bharatiya Sakshya Adhiniyam | 2023 |
| PWA | Payment of Wages Act | 1936 |
| HMA | Hindu Marriage Act | 1955 |
| PWDVA | Protection of Women from Domestic Violence Act | 2005 |
| FA | Factories Act | 1948 |
| MA | Minimum Wages Act | 1948 |
| IEA | Indian Evidence Act | 1872 |

### Critical Legal Update — July 1, 2024

Three new criminal codes replaced the old ones. The system handles this automatically via the LLM system prompt:

| Old (before July 2024) | New (after July 2024) |
|---|---|
| IPC 1860 | BNS 2023 |
| CrPC 1973 | BNSS 2023 |
| Indian Evidence Act 1872 | BSA 2023 |

**Key IPC → BNS mappings built into every prompt:**
- IPC 302 = BNS 103 (Murder)
- IPC 420 = BNS 318 (Cheating)
- IPC 376 = BNS 63 (Rape)
- IPC 498A = BNS 85 (Cruelty to wife)
- **IT Act Section 66A → STRUCK DOWN in 2015** (Shreya Singhal v UoI)

---

## 🚢 Deployment

### Target Setup: nyayasetu.me on DigitalOcean

```
DigitalOcean Droplet (Ubuntu 22.04)
    ↓
Nginx (reverse proxy)
    ├── Port 80/443 → nyayasetu.me (with SSL)
    ├── /api/*     → Backend :8000 (internal)
    └── /*         → Frontend :8501 (internal)
    ↓
Let's Encrypt SSL Certificate (via Certbot)
```

### Production Commands

```bash
# Backend (run as a systemd service for auto-restart)
uvicorn backend.main:app \
  --host 0.0.0.0 \
  --port 8000 \
  --workers 2

# Frontend
streamlit run frontend/app.py \
  --server.port 8501 \
  --server.address 0.0.0.0 \
  --server.headless true \
  --server.enableCORS false
```

### .gitignore — Critical Entries

```
.env              # Contains all API keys — never commit
chroma_db/        # 200MB+ vector database — never commit
venv/             # Python virtual environment
__pycache__/
*.pyc
*.pyo
.venv/
```

---

## ⚠️ Known Limitations

1. **State-specific laws** — ChromaDB contains only central acts. State-specific rent control laws (Karnataka, Maharashtra, etc.) are not in the knowledge base.

2. **OCR quality** — Handwritten documents or very blurry scans may have text extraction errors that propagate through the analysis pipeline.

3. **LLM hallucination** — For non-landmark cases, the LLM may occasionally invent case citations. Mitigated by: Indian Kanoon API for real cases, 16 manually verified fallback cases, and an explicit disclaimer on every Oracle output directing users to indiankanoon.org for verification.

4. **Win probability** — The Oracle's probability is directionally correct but not actuarially precise. It is an AI estimate based on similar historical cases, not a statistical model trained on outcome data.

5. **Groq TPM limit** — Groq free tier allows 6,000 tokens per minute. Very long conversations may occasionally hit this limit. Context has been carefully trimmed to stay within limits under normal usage.

---

## 📞 Emergency Helplines

These numbers are displayed permanently on the home page of the application.

| Service | Number | Available |
|---|---|---|
| Police | 100 | 24/7 |
| Ambulance | 108 | 24/7 |
| Women Helpline | 1091 | 24/7 |
| Free Legal Aid (NALSA) | 15100 | 24/7 |
| Consumer Helpline | 1800-11-4000 | 24/7 |
| Child Helpline | 1098 | 24/7 |

---

## ⚖️ Legal Disclaimer

This platform provides **general legal information only**. It does not constitute legal advice and does not create a lawyer-client relationship. For complex legal matters, always consult a licensed advocate.

**Free legal aid is available to eligible citizens.** Call **15100** (National Legal Services Authority). Eligibility includes: annual income below ₹1 lakh, all women, persons with disabilities, SC/ST community members, industrial workmen, and victims of trafficking or disasters.

---

## 🙏 Acknowledgements

- **Indian Kanoon** — for API access to 3 crore+ Indian court judgments under non-commercial terms
- **Groq** — for ultra-fast LLM inference (300 tokens/second on free tier)
- **Bhashini** — Government of India's language API for Indian language support
- **HuggingFace** — for the `sentence-transformers/all-MiniLM-L6-v2` embedding model
- **MongoDB Atlas** — for the free-tier cloud database
- **CVR College of Engineering** — for supporting this project

---

*Nyaya-Setu · न्याय सेतु · Bridge to Justice · India · 2026*