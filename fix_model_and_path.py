"""
Run this from nyaya-setu-1/ root:
  python fix_model_and_path.py

It does 2 things:
  1. Updates decommissioned llama-3.1-8b-instant → llama-3.1-8b-instant in ALL files
  2. Fixes the sys.path in test_document_chat.py
"""

import os
import re

ROOT    = os.getcwd()
BACKEND = os.path.join(ROOT, "backend")

# ── Fix 1: Update model name in all Python files ──────────
OLD_MODEL = "llama-3.1-8b-instant"
NEW_MODEL = "llama-3.1-8b-instant"

files_to_check = []
for dirpath, dirs, files in os.walk(ROOT):
    # Skip .venv, venv, .git
    dirs[:] = [d for d in dirs if d not in {'.venv', 'venv', 'venv311', '.git', '__pycache__'}]
    for f in files:
        if f.endswith(".py"):
            files_to_check.append(os.path.join(dirpath, f))

print(f"Checking {len(files_to_check)} Python files for old model name...\n")

fixed_files = []
for filepath in files_to_check:
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        if OLD_MODEL in content:
            new_content = content.replace(OLD_MODEL, NEW_MODEL)
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(new_content)
            rel = os.path.relpath(filepath, ROOT)
            print(f"  ✅ Updated model in: {rel}")
            fixed_files.append(rel)
    except Exception as e:
        print(f"  ⚠️  Could not read {filepath}: {e}")

if not fixed_files:
    print("  (no files contained old model name)")

# ── Fix 2: Fix sys.path in test_document_chat.py ─────────
print("\nFixing sys.path in test_document_chat.py...")

# Find the test file (could be in root or tests/)
test_paths = [
    os.path.join(ROOT, "test_document_chat.py"),
    os.path.join(ROOT, "tests", "test_document_chat.py"),
]

for test_path in test_paths:
    if os.path.exists(test_path):
        with open(test_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Replace whatever sys.path.insert line is there with the correct one
        old_line = 'sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))'
        new_line = 'sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend"))'

        if old_line in content:
            content = content.replace(old_line, new_line)
            with open(test_path, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"  ✅ Fixed sys.path in: {os.path.relpath(test_path, ROOT)}")
        elif new_line in content:
            print(f"  ✅ sys.path already correct in: {os.path.relpath(test_path, ROOT)}")
        else:
            # The line might look different — rewrite the top of the file
            print(f"  ⚠️  Could not find expected sys.path line in {os.path.relpath(test_path, ROOT)}")
            print(f"     Manually replace the sys.path.insert line with:")
            print(f"     {new_line}")

# ── Also fix doc_vectorstore.py's internal import ─────────
print("\nFixing doc_vectorstore.py internal import path...")

doc_vs_path = os.path.join(BACKEND, "services", "doc_vectorstore.py")
if os.path.exists(doc_vs_path):
    with open(doc_vs_path, "r", encoding="utf-8") as f:
        content = f.read()

    # The import inside build() needs sys.path awareness
    old_import = "        from services.rag import _embeddings"
    new_import = """        # Add backend to path so 'services' is importable
        import sys as _sys, os as _os
        _backend = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
        if _backend not in _sys.path:
            _sys.path.insert(0, _backend)
        from services.rag import _embeddings"""

    if old_import in content and new_import not in content:
        content = content.replace(old_import, new_import)
        with open(doc_vs_path, "w", encoding="utf-8") as f:
            f.write(content)
        print("  ✅ Fixed internal import in doc_vectorstore.py")
    else:
        print("  ✅ doc_vectorstore.py import already OK (or already fixed)")
else:
    print(f"  ❌ doc_vectorstore.py not found at {doc_vs_path}")

# ── Summary ────────────────────────────────────────────────
print("\n" + "=" * 55)
print("  DONE. Now run:")
print()
print("  1. Restart uvicorn:")
print("     uvicorn backend.main:app --reload")
print()
print("  2. Run tests:")
print("     python test_document_chat.py")
print("=" * 55)