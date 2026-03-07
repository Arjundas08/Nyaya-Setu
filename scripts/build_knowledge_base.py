# ════════════════════════════════════════════════════════
# FILE: scripts/build_knowledge_base.py
# ════════════════════════════════════════════════════════
# HOW TO RUN (from nyaya-setu/ root folder):
#   python scripts/build_knowledge_base.py
#
# WHAT IT NEEDS:
#   - All PDFs in data/legal_pdfs/ folder
#   - Packages installed (chromadb, sentence-transformers, pypdf)
#   - Internet connection (first run downloads 90MB model)
# ════════════════════════════════════════════════════════

import os
import sys
import shutil

# ─── Make sure Python can find backend/ ─────────────────
# This line lets us import from backend/services/ if needed
sys.path.insert(0, os.path.abspath("."))

from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings


# ════════════════════════════════════════════════════════
# CONFIGURATION — change these if your folders are different
# ════════════════════════════════════════════════════════
PDF_FOLDER  = "data/legal_pdfs"   # Where your 14 PDFs are saved
CHROMA_PATH = "chroma_db"         # ChromaDB will be created here
COLLECTION  = "nyaya_setu_laws"   # Name of the database collection

# This is the FREE embedding model that runs on your laptop.
# First run: downloads ~90MB model to your computer (cached after)
# It converts text → numbers so ChromaDB can search by meaning
EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


# ════════════════════════════════════════════════════════
# PDF METADATA
# This tells ChromaDB WHICH LAW each text chunk came from
# So when AI answers, it can say "Source: BNS 2023, Section 103"
# ════════════════════════════════════════════════════════
PDF_METADATA = {
    "IPC_1860.pdf":                     {
        "act_name":  "Indian Penal Code 1860",
        "act_short": "IPC",
        "category":  "Criminal Law"
    },
    "BNS_2023.pdf":                     {
        "act_name":  "Bharatiya Nyaya Sanhita 2023",
        "act_short": "BNS",
        "category":  "Criminal Law"
    },
    "BNSS_2023.pdf":                    {
        "act_name":  "Bharatiya Nagarik Suraksha Sanhita 2023",
        "act_short": "BNSS",
        "category":  "Criminal Procedure"
    },
    "BSA_2023.pdf":                     {
        "act_name":  "Bharatiya Sakshya Adhiniyam 2023",
        "act_short": "BSA",
        "category":  "Evidence Law"
    },
    "Indian_Contract_Act_1872.pdf":     {
        "act_name":  "Indian Contract Act 1872",
        "act_short": "ICA",
        "category":  "Contract Law"
    },
    "Transfer_of_Property_Act_1882.pdf":{
        "act_name":  "Transfer of Property Act 1882",
        "act_short": "TPA",
        "category":  "Property Law"
    },
    "RTI_Act_2005.pdf":                 {
        "act_name":  "Right to Information Act 2005",
        "act_short": "RTI",
        "category":  "Civil Rights"
    },
    "Consumer_Protection_Act_2019.pdf": {
        "act_name":  "Consumer Protection Act 2019",
        "act_short": "CPA",
        "category":  "Consumer Law"
    },
    "Industrial_Disputes_Act_1947.pdf": {
        "act_name":  "Industrial Disputes Act 1947",
        "act_short": "IDA",
        "category":  "Labour Law"
    },
    "Code_on_Wages_2019.pdf":           {
        "act_name":  "Code on Wages 2019",
        "act_short": "COW",
        "category":  "Labour Law"
    },
    "Domestic_Violence_Act_2005.pdf":   {
        "act_name":  "Protection of Women from Domestic Violence Act 2005",
        "act_short": "PWDVA",
        "category":  "Family Law"
    },
    "IT_Act_2000.pdf":                  {
        "act_name":  "Information Technology Act 2000",
        "act_short": "ITA",
        "category":  "Cyber Law"
    },
    "Hindu_Marriage_Act_1955.pdf":      {
        "act_name":  "Hindu Marriage Act 1955",
        "act_short": "HMA",
        "category":  "Family Law"
    },
    "Specific_Relief_Act_1963.pdf":     {
        "act_name":  "Specific Relief Act 1963",
        "act_short": "SRA",
        "category":  "Civil Law"
    },
}


# ════════════════════════════════════════════════════════
# FUNCTION 1: Load all PDFs
# ════════════════════════════════════════════════════════
def load_all_pdfs():
    """
    Reads every PDF in data/legal_pdfs/ and returns
    a list of Document objects with metadata attached.
    """
    print("\n📂 STEP 1: Loading PDFs...")
    print(f"   Looking in: {os.path.abspath(PDF_FOLDER)}")
    print("-" * 50)

    all_docs = []
    pdf_files = sorted([f for f in os.listdir(PDF_FOLDER) if f.endswith(".pdf")])

    if not pdf_files:
        print("❌ No PDF files found!")
        print(f"   Make sure your PDFs are in: {PDF_FOLDER}/")
        sys.exit(1)

    print(f"   Found {len(pdf_files)} PDF files:\n")

    for filename in pdf_files:
        filepath = os.path.join(PDF_FOLDER, filename)

        # Get metadata for this PDF (or use filename as fallback)
        meta = PDF_METADATA.get(filename, {
            "act_name":  filename.replace(".pdf", "").replace("_", " "),
            "act_short": filename[:10],
            "category":  "Law"
        })

        print(f"   Loading: {filename}", end="  ", flush=True)

        try:
            loader = PyPDFLoader(filepath)
            pages  = loader.load()

            # Attach metadata to EVERY page of this PDF
            for page in pages:
                page.metadata["source_file"] = filename
                page.metadata["act_name"]    = meta["act_name"]
                page.metadata["act_short"]   = meta["act_short"]
                page.metadata["category"]    = meta["category"]

            all_docs.extend(pages)
            file_size = os.path.getsize(filepath) // 1024
            print(f"✅  {len(pages)} pages  ({file_size} KB)")

        except Exception as e:
            print(f"❌  Failed: {e}")
            print(f"       → Skipping {filename} and continuing...")

    print(f"\n   ✅ Total pages loaded: {len(all_docs)}")
    return all_docs


# ════════════════════════════════════════════════════════
# FUNCTION 2: Split into chunks
# ════════════════════════════════════════════════════════
def split_into_chunks(docs):
    """
    Splits long pages into smaller overlapping chunks.

    WHY SPLIT?
    A full PDF page has ~3000 characters.
    ChromaDB searches better with smaller focused chunks.
    Each chunk should contain ONE idea / ONE section.

    chunk_size=1000   → each chunk is ~150 words
    chunk_overlap=200 → last 200 chars of chunk N = first 200 chars of chunk N+1
                        This prevents important context from being cut off
    """
    print("\n✂️  STEP 2: Splitting pages into chunks...")
    print("-" * 50)

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        # Try to split at these boundaries in order:
        # paragraph break → line break → sentence → word → character
        separators=["\n\n", "\n", ". ", " ", ""]
    )

    chunks = splitter.split_documents(docs)

    print(f"   ✅ Created {len(chunks)} chunks from {len(docs)} pages")
    print(f"   Average chunk size: ~{sum(len(c.page_content) for c in chunks) // len(chunks)} characters")

    # Show a sample chunk so you can verify it looks right
    print(f"\n   Sample chunk from IPC:")
    sample = next((c for c in chunks if "IPC" in c.metadata.get("act_short", "")), chunks[0])
    print(f"   Source: {sample.metadata.get('act_name', 'Unknown')}")
    print(f"   Text preview: {sample.page_content[:150].strip()}...")

    return chunks


# ════════════════════════════════════════════════════════
# FUNCTION 3: Build ChromaDB
# ════════════════════════════════════════════════════════
def build_chromadb(chunks):
    """
    Converts every chunk into embedding numbers and stores in ChromaDB.

    THIS IS THE SLOW STEP — takes 3-10 minutes depending on your laptop.
    DO NOT close the terminal while this is running!
    """
    print("\n🧠 STEP 3: Building ChromaDB (the slow step)...")
    print("-" * 50)
    print("   DO NOT close terminal — this takes 3-10 minutes")
    print()

    # Load the embedding model
    # First run: downloads ~90MB to ~/.cache/huggingface/
    print("   Loading embedding model (may download ~90MB first time)...")
    embeddings = HuggingFaceEmbeddings(
        model_name=EMBED_MODEL,
        model_kwargs={"device": "cpu"},          # Use CPU (no GPU needed)
        encode_kwargs={"normalize_embeddings": True}
    )
    print("   ✅ Embedding model loaded")

    # Process in batches of 200 to show progress
    # and avoid memory issues on low-RAM laptops
    BATCH_SIZE = 200
    total_batches = (len(chunks) + BATCH_SIZE - 1) // BATCH_SIZE

    print(f"\n   Embedding {len(chunks)} chunks in {total_batches} batches...")
    print()

    vectorstore = None

    for i in range(0, len(chunks), BATCH_SIZE):
        batch      = chunks[i : i + BATCH_SIZE]
        batch_num  = (i // BATCH_SIZE) + 1
        percent    = int((batch_num / total_batches) * 100)
        bar        = "█" * (percent // 5) + "░" * (20 - percent // 5)

        print(f"   [{bar}] {percent}%  Batch {batch_num}/{total_batches}", end="\r", flush=True)

        if vectorstore is None:
            # First batch — create the database
            vectorstore = Chroma.from_documents(
                documents=batch,
                embedding=embeddings,
                persist_directory=CHROMA_PATH,
                collection_name=COLLECTION
            )
        else:
            # Subsequent batches — add to existing database
            vectorstore.add_documents(batch)

    # Save to disk (important!)
    vectorstore.persist()

    final_count = vectorstore._collection.count()
    print(f"\n\n   ✅ ChromaDB built and saved!")
    print(f"   Total chunks stored: {final_count}")
    print(f"   Location: {os.path.abspath(CHROMA_PATH)}/")

    return vectorstore


# ════════════════════════════════════════════════════════
# FUNCTION 4: Test the database
# ════════════════════════════════════════════════════════
def test_retrieval(vectorstore):
    """
    Run 6 test searches to verify ChromaDB is working correctly.
    All should return relevant results.
    """
    print("\n🔍 STEP 4: Testing retrieval...")
    print("-" * 50)

    test_queries = [
        ("What is punishment for murder?",                "IPC/BNS"),
        ("How to file RTI application time limit?",       "RTI"),
        ("Notice period employment contract clause?",     "ICA/IDA"),
        ("Consumer complaint product defect procedure?",  "CPA"),
        ("Domestic violence protection order wife?",      "PWDVA"),
        ("Minimum wage payment bonus overtime?",          "COW/IDA"),
    ]

    all_passed = True
    for query, expected_source in test_queries:
        results = vectorstore.similarity_search(query, k=2)

        if results:
            source = results[0].metadata.get("act_short", "?")
            text   = results[0].page_content[:80].replace("\n", " ").strip()
            print(f"   ✅ '{query[:40]}...'")
            print(f"      Found in: [{source}] — {text}...")
        else:
            print(f"   ❌ No result for: '{query}'")
            all_passed = False
        print()

    if all_passed:
        print("   ✅ All retrieval tests passed!")
    else:
        print("   ⚠️  Some tests failed — PDF may be missing or unreadable")

    return all_passed


# ════════════════════════════════════════════════════════
# MAIN — runs when you execute this script
# ════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("=" * 55)
    print("  NYAYA-SETU — KNOWLEDGE BASE BUILDER")
    print("=" * 55)

    # ── Check PDF folder ─────────────────────────
    if not os.path.exists(PDF_FOLDER):
        print(f"\n❌ PDF folder not found: '{PDF_FOLDER}'")
        print(f"   Create it and add your PDFs:")
        print(f"   mkdir -p {PDF_FOLDER}")
        sys.exit(1)

    pdf_count = len([f for f in os.listdir(PDF_FOLDER) if f.endswith(".pdf")])
    print(f"\n   PDFs found: {pdf_count}")

    if pdf_count == 0:
        print(f"❌ No PDFs in {PDF_FOLDER}/")
        sys.exit(1)

    # ── Check if ChromaDB already exists ─────────
    if os.path.exists(CHROMA_PATH):
        print(f"\n⚠️  ChromaDB already exists at '{CHROMA_PATH}/'")
        ans = input("   Rebuild from scratch? (y/n): ").strip().lower()
        if ans == "y":
            shutil.rmtree(CHROMA_PATH)
            print("   Old ChromaDB deleted.\n")
        else:
            print("   Keeping existing ChromaDB.")
            print("   To test it, run: python scripts/test_knowledge_base.py")
            sys.exit(0)

    # ── Run the pipeline ─────────────────────────
    docs    = load_all_pdfs()
    chunks  = split_into_chunks(docs)
    vs      = build_chromadb(chunks)
    passed  = test_retrieval(vs)

    # ── Final summary ────────────────────────────
    print("=" * 55)
    if passed:
        print("  ✅ KNOWLEDGE BASE READY!")
        print(f"  {vs._collection.count()} law chunks in ChromaDB")
        print()
        print("  NEXT STEP:")
        print("  → Create backend/services/rag.py")
        print("  → Then run: uvicorn backend.main:app --reload")
    else:
        print("  ⚠️  Built with some warnings — check above")
    print("=" * 55)