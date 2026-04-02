# ════════════════════════════════════════════════════════════
# FILE: backend/services/voice.py
# Bhashini Voice Service — ASR, TTS, NMT, Language Detection
# ════════════════════════════════════════════════════════════

import os
import io
import base64
import requests
from typing import Optional, Tuple
from dotenv import load_dotenv

load_dotenv()

# ── Bhashini Credentials ────────────────────────────────────
BHASHINI_USER_ID      = os.getenv("BHASHINI_USER_ID", "")
BHASHINI_API_KEY      = os.getenv("BHASHINI_API_KEY", "")
BHASHINI_INFERENCE_KEY = os.getenv("BHASHINI_INFERENCE_KEY", "")

# ── API Endpoints ───────────────────────────────────────────
PIPELINE_CONFIG_URL = "https://meity-auth.ulcacontrib.org/ulca/apis/v0/model/getModelsPipeline"
INFERENCE_URL       = "https://dhruva-api.bhashini.gov.in/services/inference/pipeline"

# ── Language Mapping ────────────────────────────────────────
LANG_CODES = {
    "Hindi":    "hi",
    "Telugu":   "te", 
    "Tamil":    "ta",
    "Kannada":  "kn",
    "English":  "en",
    "Bengali":  "bn",
    "Marathi":  "mr",
    "Gujarati": "gu",
    "Malayalam":"ml",
    "Punjabi":  "pa",
    "Auto-Detect": "auto",
}

# Reverse mapping
CODE_TO_LANG = {v: k for k, v in LANG_CODES.items()}


def _get_headers(for_inference: bool = False) -> dict:
    """Get headers for Bhashini API calls."""
    if for_inference:
        return {
            "Content-Type": "application/json",
            "Authorization": BHASHINI_INFERENCE_KEY,
        }
    return {
        "Content-Type": "application/json",
        "ulcaApiKey": BHASHINI_API_KEY,
        "userID": BHASHINI_USER_ID,
    }


def _get_pipeline_config(task_type: str, source_lang: str, target_lang: str = None) -> dict:
    """
    Get pipeline configuration from Bhashini.
    
    task_type: "asr" | "tts" | "translation" | "tld"
    source_lang: ISO 639-1 code (hi, en, te, etc.)
    target_lang: For translation only
    """
    if not all([BHASHINI_USER_ID, BHASHINI_API_KEY]):
        return None
    
    # Build pipeline tasks
    if task_type == "asr":
        tasks = [{"taskType": "asr", "config": {"language": {"sourceLanguage": source_lang}}}]
    elif task_type == "tts":
        tasks = [{"taskType": "tts", "config": {"language": {"sourceLanguage": source_lang}}}]
    elif task_type == "translation":
        tasks = [{"taskType": "translation", "config": {"language": {"sourceLanguage": source_lang, "targetLanguage": target_lang}}}]
    elif task_type == "tld":
        tasks = [{"taskType": "tld"}]  # Text Language Detection
    else:
        return None
    
    payload = {
        "pipelineTasks": tasks,
        "pipelineRequestConfig": {"pipelineId": "64392f96daac500b55c543cd"}
    }
    
    try:
        resp = requests.post(
            PIPELINE_CONFIG_URL,
            json=payload,
            headers=_get_headers(for_inference=False),
            timeout=15
        )
        if resp.status_code == 200:
            return resp.json()
    except Exception as e:
        print(f"[Bhashini] Pipeline config error: {e}")
    
    return None


# ════════════════════════════════════════════════════════════
# ASR — Speech to Text
# ════════════════════════════════════════════════════════════
def speech_to_text(audio_bytes: bytes, language: str = "Hindi") -> Tuple[Optional[str], Optional[str]]:
    """
    Convert speech audio to text using Bhashini ASR.
    
    Args:
        audio_bytes: Raw audio bytes (WAV/MP3)
        language: "Hindi", "Telugu", "Tamil", "Kannada", "English", or "Auto-Detect"
    
    Returns:
        Tuple of (transcribed_text, detected_language_code) or (None, None) on failure
    """
    lang_code = LANG_CODES.get(language, "hi")
    
    # For auto-detect, default to Hindi for ASR (Bhashini needs a language)
    if lang_code == "auto":
        lang_code = "hi"
    
    # Get pipeline config for ASR
    config = _get_pipeline_config("asr", lang_code)
    if not config:
        print("[Bhashini] Could not get ASR pipeline config")
        return None, None
    
    try:
        # Extract service info from config
        pipeline_response = config.get("pipelineResponseConfig", [])
        if not pipeline_response:
            return None, None
        
        asr_config = pipeline_response[0].get("config", [])
        if not asr_config:
            return None, None
        
        service_id = asr_config[0].get("serviceId", "")
        callback_url = config.get("pipelineInferenceAPIEndPoint", {}).get("callbackUrl", INFERENCE_URL)
        inference_key = config.get("pipelineInferenceAPIEndPoint", {}).get("inferenceApiKey", {}).get("value", BHASHINI_INFERENCE_KEY)
        
        # Prepare inference request
        audio_base64 = base64.b64encode(audio_bytes).decode("utf-8")
        
        payload = {
            "pipelineTasks": [{
                "taskType": "asr",
                "config": {
                    "language": {"sourceLanguage": lang_code},
                    "serviceId": service_id,
                    "audioFormat": "wav",
                    "samplingRate": 16000,
                }
            }],
            "inputData": {
                "audio": [{"audioContent": audio_base64}]
            }
        }
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": inference_key,
        }
        
        resp = requests.post(callback_url, json=payload, headers=headers, timeout=30)
        
        if resp.status_code == 200:
            result = resp.json()
            output = result.get("pipelineResponse", [])
            if output:
                text_output = output[0].get("output", [])
                if text_output:
                    transcribed = text_output[0].get("source", "")
                    detected_lang = text_output[0].get("langCode", lang_code)
                    return transcribed, detected_lang
        else:
            print(f"[Bhashini ASR] Error {resp.status_code}: {resp.text[:200]}")
    
    except Exception as e:
        print(f"[Bhashini ASR] Exception: {e}")
    
    return None, None


# ════════════════════════════════════════════════════════════
# TTS — Text to Speech
# ════════════════════════════════════════════════════════════
def text_to_speech(text: str, language: str = "Hindi", gender: str = "female") -> Optional[bytes]:
    """
    Convert text to speech using Bhashini TTS.
    
    Args:
        text: Text to synthesize
        language: "Hindi", "Telugu", "Tamil", "Kannada", "English"
        gender: "male" or "female"
    
    Returns:
        Audio bytes (WAV) or None on failure
    """
    if not text or not text.strip():
        return None
    
    lang_code = LANG_CODES.get(language, "hi")
    if lang_code == "auto":
        lang_code = "hi"  # Default for TTS
    
    # Get pipeline config for TTS
    config = _get_pipeline_config("tts", lang_code)
    if not config:
        print("[Bhashini] Could not get TTS pipeline config, falling back to gTTS")
        return _fallback_tts(text, lang_code)
    
    try:
        # Extract service info
        pipeline_response = config.get("pipelineResponseConfig", [])
        if not pipeline_response:
            return _fallback_tts(text, lang_code)
        
        tts_config = pipeline_response[0].get("config", [])
        if not tts_config:
            return _fallback_tts(text, lang_code)
        
        service_id = tts_config[0].get("serviceId", "")
        callback_url = config.get("pipelineInferenceAPIEndPoint", {}).get("callbackUrl", INFERENCE_URL)
        inference_key = config.get("pipelineInferenceAPIEndPoint", {}).get("inferenceApiKey", {}).get("value", BHASHINI_INFERENCE_KEY)
        
        payload = {
            "pipelineTasks": [{
                "taskType": "tts",
                "config": {
                    "language": {"sourceLanguage": lang_code},
                    "serviceId": service_id,
                    "gender": gender,
                    "samplingRate": 8000,
                }
            }],
            "inputData": {
                "input": [{"source": text}]
            }
        }
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": inference_key,
        }
        
        resp = requests.post(callback_url, json=payload, headers=headers, timeout=30)
        
        if resp.status_code == 200:
            result = resp.json()
            output = result.get("pipelineResponse", [])
            if output:
                audio_output = output[0].get("audio", [])
                if audio_output:
                    audio_base64 = audio_output[0].get("audioContent", "")
                    if audio_base64:
                        return base64.b64decode(audio_base64)
        else:
            print(f"[Bhashini TTS] Error {resp.status_code}: {resp.text[:200]}")
    
    except Exception as e:
        print(f"[Bhashini TTS] Exception: {e}")
    
    # Fallback to gTTS
    return _fallback_tts(text, lang_code)


def _fallback_tts(text: str, lang_code: str) -> Optional[bytes]:
    """Fallback TTS using gTTS (Google Text-to-Speech)."""
    try:
        from gtts import gTTS
        
        # gTTS uses same ISO codes
        tts = gTTS(text=text, lang=lang_code if lang_code != "auto" else "en")
        audio_buffer = io.BytesIO()
        tts.write_to_fp(audio_buffer)
        audio_buffer.seek(0)
        return audio_buffer.read()
    except Exception as e:
        print(f"[gTTS Fallback] Error: {e}")
        return None


# ════════════════════════════════════════════════════════════
# NMT — Neural Machine Translation
# ════════════════════════════════════════════════════════════
def translate_text(text: str, source_lang: str, target_lang: str) -> Optional[str]:
    """
    Translate text between languages using Bhashini NMT.
    
    Args:
        text: Text to translate
        source_lang: Source language code (hi, en, te, etc.)
        target_lang: Target language code
    
    Returns:
        Translated text or None on failure
    """
    if not text or not text.strip():
        return None
    
    config = _get_pipeline_config("translation", source_lang, target_lang)
    if not config:
        print("[Bhashini] Could not get translation pipeline config")
        return None
    
    try:
        pipeline_response = config.get("pipelineResponseConfig", [])
        if not pipeline_response:
            return None
        
        nmt_config = pipeline_response[0].get("config", [])
        if not nmt_config:
            return None
        
        service_id = nmt_config[0].get("serviceId", "")
        callback_url = config.get("pipelineInferenceAPIEndPoint", {}).get("callbackUrl", INFERENCE_URL)
        inference_key = config.get("pipelineInferenceAPIEndPoint", {}).get("inferenceApiKey", {}).get("value", BHASHINI_INFERENCE_KEY)
        
        payload = {
            "pipelineTasks": [{
                "taskType": "translation",
                "config": {
                    "language": {
                        "sourceLanguage": source_lang,
                        "targetLanguage": target_lang
                    },
                    "serviceId": service_id,
                }
            }],
            "inputData": {
                "input": [{"source": text}]
            }
        }
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": inference_key,
        }
        
        resp = requests.post(callback_url, json=payload, headers=headers, timeout=30)
        
        if resp.status_code == 200:
            result = resp.json()
            output = result.get("pipelineResponse", [])
            if output:
                text_output = output[0].get("output", [])
                if text_output:
                    return text_output[0].get("target", "")
        else:
            print(f"[Bhashini NMT] Error {resp.status_code}: {resp.text[:200]}")
    
    except Exception as e:
        print(f"[Bhashini NMT] Exception: {e}")
    
    return None


# ════════════════════════════════════════════════════════════
# TLD — Text Language Detection
# ════════════════════════════════════════════════════════════
def detect_language(text: str) -> Optional[str]:
    """
    Detect the language of given text using Bhashini TLD.
    
    Args:
        text: Text to analyze
    
    Returns:
        Language code (hi, en, te, etc.) or None on failure
    """
    if not text or not text.strip():
        return None
    
    config = _get_pipeline_config("tld", "hi")  # source_lang doesn't matter for TLD
    if not config:
        # Fallback to simple detection
        return _fallback_detect_language(text)
    
    try:
        pipeline_response = config.get("pipelineResponseConfig", [])
        if not pipeline_response:
            return _fallback_detect_language(text)
        
        tld_config = pipeline_response[0].get("config", [])
        if not tld_config:
            return _fallback_detect_language(text)
        
        service_id = tld_config[0].get("serviceId", "")
        callback_url = config.get("pipelineInferenceAPIEndPoint", {}).get("callbackUrl", INFERENCE_URL)
        inference_key = config.get("pipelineInferenceAPIEndPoint", {}).get("inferenceApiKey", {}).get("value", BHASHINI_INFERENCE_KEY)
        
        payload = {
            "pipelineTasks": [{
                "taskType": "tld",
                "config": {"serviceId": service_id}
            }],
            "inputData": {
                "input": [{"source": text}]
            }
        }
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": inference_key,
        }
        
        resp = requests.post(callback_url, json=payload, headers=headers, timeout=15)
        
        if resp.status_code == 200:
            result = resp.json()
            output = result.get("pipelineResponse", [])
            if output:
                lang_output = output[0].get("output", [])
                if lang_output:
                    return lang_output[0].get("langCode", None)
        else:
            print(f"[Bhashini TLD] Error {resp.status_code}: {resp.text[:200]}")
    
    except Exception as e:
        print(f"[Bhashini TLD] Exception: {e}")
    
    return _fallback_detect_language(text)


def _fallback_detect_language(text: str) -> str:
    """Simple fallback language detection based on character ranges."""
    # Devanagari (Hindi, Marathi, etc.)
    if any('\u0900' <= c <= '\u097F' for c in text):
        return "hi"
    # Telugu
    if any('\u0C00' <= c <= '\u0C7F' for c in text):
        return "te"
    # Tamil
    if any('\u0B80' <= c <= '\u0BFF' for c in text):
        return "ta"
    # Kannada
    if any('\u0C80' <= c <= '\u0CFF' for c in text):
        return "kn"
    # Bengali
    if any('\u0980' <= c <= '\u09FF' for c in text):
        return "bn"
    # Gujarati
    if any('\u0A80' <= c <= '\u0AFF' for c in text):
        return "gu"
    # Malayalam
    if any('\u0D00' <= c <= '\u0D7F' for c in text):
        return "ml"
    # Punjabi (Gurmukhi)
    if any('\u0A00' <= c <= '\u0A7F' for c in text):
        return "pa"
    
    # Default to English
    return "en"


# ════════════════════════════════════════════════════════════
# UTILITY FUNCTIONS
# ════════════════════════════════════════════════════════════
def get_language_name(code: str) -> str:
    """Convert language code to human-readable name."""
    return CODE_TO_LANG.get(code, "Unknown")


def get_language_code(name: str) -> str:
    """Convert language name to ISO code."""
    return LANG_CODES.get(name, "en")


def is_bhashini_configured() -> bool:
    """Check if Bhashini credentials are configured."""
    return all([BHASHINI_USER_ID, BHASHINI_API_KEY, BHASHINI_INFERENCE_KEY])
