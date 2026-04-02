# ════════════════════════════════════════════════════════════
# FILE: backend/routes/voice.py
# Voice API Routes — ASR, TTS, Translation, Language Detection
# ════════════════════════════════════════════════════════════

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel
from typing import Optional

from services.voice import (
    speech_to_text,
    text_to_speech,
    translate_text,
    detect_language,
    get_language_name,
    is_bhashini_configured,
    LANG_CODES,
)

router = APIRouter()


# ════════════════════════════════════════════════════════════
# MODELS
# ════════════════════════════════════════════════════════════
class TTSRequest(BaseModel):
    text: str
    language: str = "Hindi"
    gender: str = "female"


class TranslateRequest(BaseModel):
    text: str
    source_language: str
    target_language: str


class DetectRequest(BaseModel):
    text: str


# ════════════════════════════════════════════════════════════
# ENDPOINTS
# ════════════════════════════════════════════════════════════

@router.get("/status")
async def voice_status():
    """Check if Bhashini voice services are configured."""
    return {
        "configured": is_bhashini_configured(),
        "supported_languages": list(LANG_CODES.keys()),
        "services": ["asr", "tts", "nmt", "tld"],
    }


@router.post("/transcribe")
async def transcribe_audio(
    audio: UploadFile = File(...),
    language: str = Form("Hindi"),
):
    """
    Convert speech audio to text using Bhashini ASR.
    
    - **audio**: Audio file (WAV, MP3, WebM)
    - **language**: Hindi, Telugu, Tamil, Kannada, English, Auto-Detect
    
    Returns transcribed text and detected language.
    """
    if not is_bhashini_configured():
        raise HTTPException(
            status_code=503,
            detail="Bhashini voice services not configured. Check BHASHINI_* env vars."
        )
    
    # Read audio bytes
    audio_bytes = await audio.read()
    
    if not audio_bytes:
        raise HTTPException(status_code=400, detail="Empty audio file")
    
    # Transcribe
    text, detected_lang = speech_to_text(audio_bytes, language)
    
    if text is None:
        raise HTTPException(
            status_code=500,
            detail="Could not transcribe audio. Try speaking more clearly or check audio quality."
        )
    
    return {
        "text": text,
        "language_code": detected_lang,
        "language_name": get_language_name(detected_lang) if detected_lang else "Unknown",
        "input_language": language,
    }


@router.post("/synthesize")
async def synthesize_speech(request: TTSRequest):
    """
    Convert text to speech using Bhashini TTS.
    
    - **text**: Text to synthesize
    - **language**: Hindi, Telugu, Tamil, Kannada, English
    - **gender**: male or female
    
    Returns audio bytes (WAV format).
    """
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")
    
    # Generate audio
    audio_bytes = text_to_speech(request.text, request.language, request.gender)
    
    if audio_bytes is None:
        raise HTTPException(
            status_code=500,
            detail="Could not generate speech. TTS service may be unavailable."
        )
    
    return Response(
        content=audio_bytes,
        media_type="audio/wav",
        headers={"Content-Disposition": "inline; filename=speech.wav"}
    )


@router.post("/translate")
async def translate(request: TranslateRequest):
    """
    Translate text between Indian languages using Bhashini NMT.
    
    - **text**: Text to translate
    - **source_language**: Source language code (hi, en, te, ta, kn)
    - **target_language**: Target language code
    
    Returns translated text.
    """
    if not is_bhashini_configured():
        raise HTTPException(
            status_code=503,
            detail="Bhashini services not configured. Check BHASHINI_* env vars."
        )
    
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")
    
    translated = translate_text(
        request.text,
        request.source_language,
        request.target_language
    )
    
    if translated is None:
        raise HTTPException(
            status_code=500,
            detail=f"Could not translate from {request.source_language} to {request.target_language}"
        )
    
    return {
        "original": request.text,
        "translated": translated,
        "source_language": request.source_language,
        "target_language": request.target_language,
    }


@router.post("/detect")
async def detect(request: DetectRequest):
    """
    Detect the language of given text using Bhashini TLD.
    
    - **text**: Text to analyze
    
    Returns detected language code and name.
    """
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")
    
    lang_code = detect_language(request.text)
    
    return {
        "text": request.text[:100] + ("..." if len(request.text) > 100 else ""),
        "language_code": lang_code,
        "language_name": get_language_name(lang_code) if lang_code else "Unknown",
    }
