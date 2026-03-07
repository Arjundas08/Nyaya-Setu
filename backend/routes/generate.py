# ════════════════════════════════════════════════════════
# FILE: backend/routes/generate.py
# ════════════════════════════════════════════════════════

import os
import logging
from fastapi import APIRouter
from pydantic import BaseModel

logger = logging.getLogger(__name__)
router = APIRouter()

TEMPLATES_DIR = "data/templates"

# Available template types
TEMPLATE_MAP = {
    "rti_application":      "rti_application.txt",
    "legal_notice":         "legal_notice.txt",
    "rental_agreement":     "rental_agreement.txt",
    "consumer_complaint":   "consumer_complaint.txt",
    "employment_complaint": "employment_complaint.txt",
}


class GenerateRequest(BaseModel):
    template_type: str          # e.g. "rti_application"
    variables:     dict = {}    # e.g. {"applicant_name": "Arjun Kumar", ...}
    session_id:    str  = "default"


# ════════════════════════════════════════════════════════
# ENDPOINT 1: Generate a legal document
# POST /generate/document
# ════════════════════════════════════════════════════════
@router.post("/document")
async def generate_document(req: GenerateRequest):
    """
    Fill a legal document template with user-provided variables.
    Returns the completed document as a string.
    """
    if req.template_type not in TEMPLATE_MAP:
        return {
            "success":           False,
            "message":           f"Unknown template: '{req.template_type}'",
            "available_templates": list(TEMPLATE_MAP.keys()),
        }

    template_file = os.path.join(TEMPLATES_DIR, TEMPLATE_MAP[req.template_type])

    try:
        with open(template_file, "r", encoding="utf-8") as f:
            template_text = f.read()

        # Replace placeholders like {{applicant_name}} with actual values
        filled = template_text
        for key, value in req.variables.items():
            placeholder = "{{" + key + "}}"
            filled = filled.replace(placeholder, str(value))

        return {
            "success":       True,
            "template_type": req.template_type,
            "document":      filled,
            "char_count":    len(filled),
            "message":       "Document generated successfully!"
        }

    except FileNotFoundError:
        logger.error(f"Template file not found: {template_file}")
        return {
            "success": False,
            "message": f"Template file not found: {TEMPLATE_MAP[req.template_type]}. "
                       "Make sure data/templates/ folder has the template files."
        }
    except Exception as e:
        logger.error(f"Document generation error: {e}")
        return {
            "success": False,
            "message": f"Generation failed: {str(e)}"
        }


# ════════════════════════════════════════════════════════
# ENDPOINT 2: List available templates
# GET /generate/templates
# ════════════════════════════════════════════════════════
@router.get("/templates")
async def list_templates():
    """Returns all available legal document templates."""
    templates = []
    for key, filename in TEMPLATE_MAP.items():
        filepath = os.path.join(TEMPLATES_DIR, filename)
        templates.append({
            "type":      key,
            "filename":  filename,
            "available": os.path.exists(filepath),
        })
    return {"templates": templates}