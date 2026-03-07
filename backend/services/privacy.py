# ════════════════════════════════════════════════════════
# FILE: backend/services/privacy.py
# ════════════════════════════════════════════════════════
# Removes personally identifiable information (PII) from
# document text before storing or sending to AI.
#
# WHY: We must NOT send real names, phone numbers, Aadhaar
# numbers, bank details etc. to external AI APIs (Groq).
# This file redacts them before any AI processing.
# ════════════════════════════════════════════════════════

import re
import logging

logger = logging.getLogger(__name__)


# ════════════════════════════════════════════════════════
# PII PATTERNS — Indian-specific
# ════════════════════════════════════════════════════════
_PII_PATTERNS = [

    # ── Aadhaar number: 12 digits, often with spaces/dashes ──
    # Format: 1234 5678 9012 or 1234-5678-9012 or 123456789012
    (re.compile(r'\b\d{4}[\s\-]?\d{4}[\s\-]?\d{4}\b'), '[AADHAAR REDACTED]'),

    # ── PAN card: 5 letters + 4 digits + 1 letter ────────────
    # Format: ABCDE1234F
    (re.compile(r'\b[A-Z]{5}[0-9]{4}[A-Z]\b'), '[PAN REDACTED]'),

    # ── Indian mobile numbers ─────────────────────────────────
    # Format: +91 9876543210 or 09876543210 or 9876543210
    (re.compile(r'(\+91[\s\-]?)?[6-9]\d{9}\b'), '[PHONE REDACTED]'),

    # ── Indian landline numbers ───────────────────────────────
    # Format: 011-12345678 or (022)12345678
    (re.compile(r'\b(?:\d{2,4}[\s\-])?\d{6,8}\b'), '[PHONE REDACTED]'),

    # ── Email addresses ───────────────────────────────────────
    (re.compile(r'\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b'),
     '[EMAIL REDACTED]'),

    # ── Bank account numbers (9-18 digits) ───────────────────
    (re.compile(r'\b\d{9,18}\b'), '[ACCOUNT REDACTED]'),

    # ── IFSC codes: 4 letters + 0 + 6 alphanumeric ───────────
    (re.compile(r'\b[A-Z]{4}0[A-Z0-9]{6}\b'), '[IFSC REDACTED]'),

    # ── Passport number: 1 letter + 7 digits ─────────────────
    (re.compile(r'\b[A-Z][0-9]{7}\b'), '[PASSPORT REDACTED]'),

    # ── Voter ID: 3 letters + 7 digits ───────────────────────
    (re.compile(r'\b[A-Z]{3}[0-9]{7}\b'), '[VOTER_ID REDACTED]'),

    # ── GST number: 2 digits + 5 letters + 4 digits + 1 + Z + digit ─
    (re.compile(r'\b\d{2}[A-Z]{5}\d{4}[A-Z][1-9A-Z]Z[0-9A-Z]\b'),
     '[GST REDACTED]'),

    # ── Pincode ───────────────────────────────────────────────
    (re.compile(r'\b[1-9][0-9]{5}\b'), '[PINCODE REDACTED]'),

    # ── Date of birth patterns ────────────────────────────────
    # Format: DD/MM/YYYY or DD-MM-YYYY or YYYY-MM-DD
    (re.compile(r'\b\d{1,2}[/\-]\d{1,2}[/\-]\d{4}\b'), '[DOB REDACTED]'),
    (re.compile(r'\b\d{4}[/\-]\d{1,2}[/\-]\d{1,2}\b'), '[DOB REDACTED]'),
]

# ── Name patterns (common Indian naming formats) ─────────
# We look for lines starting with "Name:", "Employee:", etc.
_NAME_LINE_PATTERNS = [
    re.compile(r'((?:Name|Employee Name|Employer|Party|Between|Tenant|Landlord|Lessor|Lessee)\s*:\s*)([A-Za-z\s]{3,50})', re.IGNORECASE),
    re.compile(r'(Mr\.|Mrs\.|Ms\.|Dr\.|Shri\s|Smt\.\s)([A-Za-z\s]{3,40})', re.IGNORECASE),
]


def redact_pii(text: str) -> str:
    """
    Remove PII from document text before AI processing or storage.

    Redacts:
      - Aadhaar numbers
      - PAN card numbers
      - Mobile and landline phone numbers
      - Email addresses
      - Bank account numbers
      - IFSC codes
      - Passport numbers
      - Voter IDs
      - GST numbers
      - Pincodes
      - Dates of birth
      - Names (when labeled with prefixes like "Name:", "Mr.", "Mrs.")

    INPUT:  raw document text string
    OUTPUT: text with PII replaced by [TYPE REDACTED] placeholders

    Never raises exceptions — returns original text on any error.
    """
    if not text or not text.strip():
        return text

    try:
        redacted = text
        redaction_count = 0

        # Apply all pattern-based redactions
        for pattern, replacement in _PII_PATTERNS:
            new_text, count = pattern.subn(replacement, redacted)
            if count:
                redaction_count += count
                redacted = new_text

        # Apply name redactions (replace only the name part, keep label)
        for pattern in _NAME_LINE_PATTERNS:
            def replace_name(match):
                return match.group(1) + '[NAME REDACTED]'
            new_text, count = pattern.subn(replace_name, redacted)
            if count:
                redaction_count += count
                redacted = new_text

        if redaction_count > 0:
            logger.info(f"Privacy guard: redacted {redaction_count} PII items")

        return redacted

    except Exception as e:
        logger.error(f"Privacy redaction failed: {e} — returning original text")
        return text  # Safe fallback — never crash


# ════════════════════════════════════════════════════════
# ALIAS — in case any old code uses a different name
# ════════════════════════════════════════════════════════
# If your old privacy.py had a different function name,
# these aliases ensure backward compatibility.
anonymize_text    = redact_pii
remove_pii        = redact_pii
privacy_guard     = redact_pii
sanitize_document = redact_pii


# ════════════════════════════════════════════════════════
# QUICK TEST — run this file directly to verify
# python backend/services/privacy.py
# ════════════════════════════════════════════════════════
if __name__ == "__main__":
    test_text = """
    EMPLOYMENT AGREEMENT

    Name: Arjun Kumar
    Employee: Mr. Ravi Sharma
    Aadhaar: 1234 5678 9012
    PAN: ABCDE1234F
    Mobile: +91 9876543210
    Email: arjun.kumar@example.com
    Bank Account: 123456789012
    IFSC: HDFC0001234
    DOB: 15/08/1995
    Pincode: 500032

    This agreement is between ABC Technologies Pvt Ltd
    and the employee named above.
    """

    result = redact_pii(test_text)
    print("ORIGINAL:")
    print(test_text)
    print("\nAFTER REDACTION:")
    print(result)

    # Verify PII is gone
    checks = [
        ("Aadhaar gone",  "1234 5678 9012" not in result),
        ("PAN gone",      "ABCDE1234F"     not in result),
        ("Phone gone",    "9876543210"     not in result),
        ("Email gone",    "arjun.kumar@"   not in result),
        ("IFSC gone",     "HDFC0001234"    not in result),
    ]
    print("\nVERIFICATION:")
    for name, passed in checks:
        print(f"  {'✅' if passed else '❌'} {name}")