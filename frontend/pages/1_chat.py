import streamlit as st
import base64, os, uuid, requests, textwrap, io

st.set_page_config(
    page_title="Nyaya-Setu | Legal Chat",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

API = "http://localhost:8000"
BG_PATH = os.path.join(os.path.dirname(__file__), "nyaya_setu_bridge.png")

def b64(path):
    try:
        with open(path, "rb") as f: return base64.b64encode(f.read()).decode()
    except: return None

BG = b64(BG_PATH)

# ── helper: strips indentation so Streamlit never sees 4-space code blocks ──
def md(html, **kw):
    st.markdown(textwrap.dedent(html), unsafe_allow_html=True, **kw)


# ════════════════════════════════════════════════════════════
# VOICE API FUNCTIONS
# ════════════════════════════════════════════════════════════
def transcribe_audio(audio_bytes: bytes, language: str = "Hindi") -> str:
    """Send audio to backend for transcription."""
    try:
        files = {"audio": ("recording.wav", audio_bytes, "audio/wav")}
        data = {"language": language}
        r = requests.post(f"{API}/voice/transcribe", files=files, data=data, timeout=30)
        if r.status_code == 200:
            return r.json().get("text", "")
    except Exception as e:
        st.error(f"Transcription failed: {e}")
    return ""


def synthesize_speech(text: str, language: str = "Hindi") -> bytes:
    """Get audio bytes from backend TTS."""
    try:
        r = requests.post(
            f"{API}/voice/synthesize",
            json={"text": text, "language": language, "gender": "female"},
            timeout=30
        )
        if r.status_code == 200:
            return r.content
    except Exception as e:
        st.error(f"Speech synthesis failed: {e}")
    return None


# ════════════════════════════════════════════════════════════
# CSS
# ════════════════════════════════════════════════════════════
def inject_css():
    bg_rule = (
        f"background-image:linear-gradient(rgba(3,3,5,0.9),rgba(3,3,5,0.98)),"
        f"url('data:image/png;base64,{BG}');"
        f"background-size:cover;background-position:center;background-attachment:fixed;"
    ) if BG else "background-color:#030305;"

    st.markdown(f"""<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;600;700&family=Playfair+Display:ital,wght@0,400;0,700;1,400&display=swap');
html,body,[data-testid="stAppViewContainer"]{{ {bg_rule} color:#F5F5F7; font-family:'Plus Jakarta Sans',sans-serif; }}
[data-testid="block-container"]{{padding:0!important;max-width:100%!important;}}
#MainMenu,header,footer{{display:none!important;}}
.stDeployButton{{display:none!important;}}
[data-testid="stSidebarNav"],[data-testid="stSidebarNavItems"],
nav[data-testid="stSidebarNav"],[data-testid="stSidebarContent"] ul,
[data-testid="stSidebarContent"] nav{{display:none!important;}}
::-webkit-scrollbar{{width:5px;}}
::-webkit-scrollbar-track{{background:#030305;}}
::-webkit-scrollbar-thumb{{background:#D4AF37;border-radius:3px;}}
[data-testid="stChatInput"]{{background:rgba(20,20,30,0.85)!important;border:1px solid rgba(212,175,55,0.3)!important;border-radius:50px!important;}}
[data-testid="stChatInput"]:focus-within{{border-color:#D4AF37!important;box-shadow:0 0 20px rgba(212,175,55,0.15)!important;}}
[data-testid="stChatInput"] textarea{{color:#F5F5F7!important;background:transparent!important;}}
[data-testid="stChatMessage"]{{background:transparent!important;border:none!important;padding:4px 0!important;}}
.stButton>button{{background:transparent!important;border:1px solid #D4AF37!important;color:#D4AF37!important;border-radius:50px!important;padding:8px 22px!important;font-weight:600!important;letter-spacing:1px!important;font-size:12px!important;transition:0.3s!important;font-family:'Plus Jakarta Sans',sans-serif!important;}}
.stButton>button:hover{{background:#D4AF37!important;color:#000!important;box-shadow:0 0 20px rgba(212,175,55,0.4)!important;}}
[data-testid="stSelectbox"]>div>div{{background:rgba(20,20,30,0.8)!important;border:1px solid rgba(212,175,55,0.25)!important;border-radius:12px!important;color:#F5F5F7!important;}}
@keyframes fadein{{from{{opacity:0;transform:translateY(10px);}}to{{opacity:1;transform:translateY(0);}}}}
@keyframes flicker{{0%,100%{{opacity:1;}}50%{{opacity:0.75;}}}}
@keyframes pulse{{0%,100%{{box-shadow:0 0 0 0 rgba(212,175,55,0.2);}}50%{{box-shadow:0 0 0 8px rgba(212,175,55,0);}}}}

/* ══ MOBILE RESPONSIVE ══ */
@media (max-width: 768px) {{
    h1 {{ font-size: 32px !important; }}
    [data-testid="stChatInput"] {{ border-radius: 25px !important; }}
    [data-testid="stChatInput"] textarea {{ font-size: 16px !important; min-height: 44px !important; }}
    .stButton>button {{ padding: 12px 18px !important; font-size: 13px !important; min-height: 48px !important; }}
    [data-testid="stAudioInput"] {{ transform: scale(1.2) !important; }}
    [data-testid="stExpander"] {{ margin: 8px 0 !important; }}
}}
@media (max-width: 480px) {{
    h1 {{ font-size: 24px !important; line-height: 1.2 !important; }}
    [data-testid="block-container"] > div {{ padding: 0 8px !important; }}
}}
</style>""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════
# HEADER
# ════════════════════════════════════════════════════════════
def render_header():
    st.markdown(
"""<div style="text-align:center;padding:56px 5% 32px;position:relative;overflow:hidden;">
<div style="position:absolute;top:0;left:50%;transform:translateX(-50%);width:600px;height:280px;pointer-events:none;background:radial-gradient(ellipse at 50% 0%,rgba(212,175,55,0.07) 0%,transparent 70%);"></div>
<div style="font-size:11px;color:#FF7722;letter-spacing:6px;text-transform:uppercase;margin-bottom:14px;">The Virtual Advocate</div>
<h1 style="font-family:'Playfair Display',serif;font-size:58px;margin:0 0 10px;line-height:1.1;background:linear-gradient(to bottom,#FFFFFF 30%,#D4AF37 100%);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">Ask Any Legal Question.<br/>Get a Real Answer.</h1>
<p style="font-size:16px;color:#8E8E93;max-width:580px;margin:16px auto 0;line-height:1.75;">Ask in Hindi, Telugu, English, Tamil, or Kannada. Answers grounded in real Indian law — ICA, IDA, RTI, CPA, BNS 2023. Free. Always.</p>
</div>""",
        unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════
# QUICK QUESTION PILLS
# ════════════════════════════════════════════════════════════
QUICK_QS = [
    "My employer hasn't paid salary for 2 months. What can I do?",
    "Can my landlord evict me without notice?",
    "My boss is threatening me under Section 66A. Is that legal?",
    "How do I file an RTI application?",
    "My landlord won't return the security deposit. What are my rights?",
    "I was fired without any reason after 3 years. What's my compensation?",
    "मेरा मकान मालिक किरायानामा नहीं दे रहा — मैं क्या करूँ?",
    "నా యజమాని నా జీతం ఇవ్వడం లేదు — నేను ఏమి చేయగలను?",
]

def quick_questions():
    st.markdown(
'<div style="text-align:center;margin-bottom:8px;"><div style="font-size:10px;color:#555;letter-spacing:3px;text-transform:uppercase;">Common Questions — Click to Ask</div></div>',
        unsafe_allow_html=True)
    cols = st.columns(4)
    for i, q in enumerate(QUICK_QS[:8]):
        with cols[i % 4]:
            if st.button(q[:42] + ("..." if len(q) > 42 else ""), key=f"qq_{i}"):
                return q
    return None


# ════════════════════════════════════════════════════════════
# USER BUBBLE
# ════════════════════════════════════════════════════════════
def user_bubble(text):
    st.markdown(
f'<div style="display:flex;justify-content:flex-end;margin:12px 0;animation:fadein 0.4s ease both;">'
f'<div style="max-width:72%;background:linear-gradient(135deg,rgba(212,175,55,0.15),rgba(212,175,55,0.08));border:1px solid rgba(212,175,55,0.25);border-radius:20px 20px 4px 20px;padding:16px 20px;font-size:14px;color:#F5F5F7;line-height:1.7;">{text}</div>'
f'<div style="margin-left:10px;width:32px;height:32px;border-radius:50%;background:rgba(212,175,55,0.2);border:1px solid rgba(212,175,55,0.3);display:flex;align-items:center;justify-content:center;font-size:14px;flex-shrink:0;margin-top:4px;">👤</div>'
f'</div>',
        unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════
# AI BUBBLE (with optional speaker button)
# ════════════════════════════════════════════════════════════
def ai_bubble(text, contract_hits=0, law_hits=0, msg_idx=None, lang="English"):
    parts      = text.split("📋 Next Steps:") if "📋 Next Steps:" in text else [text, None]
    main_text  = parts[0].strip()
    next_steps = parts[1].strip() if parts[1] else None

    src = ""
    if contract_hits or law_hits:
        c_pill = (f'<div style="padding:3px 12px;background:rgba(212,175,55,0.08);border:1px solid rgba(212,175,55,0.2);border-radius:50px;font-size:11px;color:#D4AF37;">📄 {contract_hits} clause{"s" if contract_hits!=1 else ""}</div>'
                  if contract_hits else "")
        l_pill = (f'<div style="padding:3px 12px;background:rgba(255,119,34,0.08);border:1px solid rgba(255,119,34,0.2);border-radius:50px;font-size:11px;color:#FF7722;">⚖️ {law_hits} law chunk{"s" if law_hits!=1 else ""}</div>'
                  if law_hits else "")
        src = f'<div style="display:flex;gap:8px;flex-wrap:wrap;margin-top:14px;padding-top:12px;border-top:1px solid rgba(255,255,255,0.05);">{c_pill}{l_pill}</div>'

    nxt = ""
    if next_steps:
        lines = [l.strip() for l in next_steps.split("\n") if l.strip()]
        items = "".join([
            f'<div style="display:flex;gap:10px;align-items:flex-start;margin-bottom:8px;">'
            f'<div style="width:18px;height:18px;min-width:18px;border-radius:50%;background:rgba(212,175,55,0.2);border:1px solid rgba(212,175,55,0.3);display:flex;align-items:center;justify-content:center;font-size:9px;color:#D4AF37;margin-top:2px;">{idx+1}</div>'
            f'<div style="font-size:13px;color:#C1C1C7;line-height:1.6;">{l}</div></div>'
            for idx, l in enumerate(lines[:6])
        ])
        nxt = (f'<div style="background:rgba(212,175,55,0.05);border:1px solid rgba(212,175,55,0.14);border-radius:12px;padding:14px 18px;margin-top:12px;">'
               f'<div style="font-size:10px;color:#D4AF37;letter-spacing:2px;text-transform:uppercase;margin-bottom:10px;">📋 Next Steps</div>{items}</div>')

    st.markdown(
f'<div style="display:flex;justify-content:flex-start;margin:12px 0;animation:fadein 0.4s ease both;">'
f'<div style="margin-right:10px;width:32px;height:32px;border-radius:50%;background:rgba(255,119,34,0.15);border:1px solid rgba(255,119,34,0.3);display:flex;align-items:center;justify-content:center;font-size:14px;flex-shrink:0;margin-top:4px;animation:flicker 5s infinite;">⚖️</div>'
f'<div style="max-width:78%;">'
f'<div style="background:linear-gradient(145deg,rgba(18,14,8,0.95),rgba(10,8,4,0.98));border:1px solid rgba(255,255,255,0.06);border-radius:4px 20px 20px 20px;padding:18px 22px;">'
f'<div style="font-size:14px;color:#E0E0E7;line-height:1.82;">{main_text}</div>{nxt}{src}</div>'
f'<div style="font-size:10px;color:#333;margin-top:4px;padding-left:6px;letter-spacing:1px;">Nyaya-Setu AI · Powered by Groq</div>'
f'</div></div>',
        unsafe_allow_html=True)
    
    # Add speaker button after the bubble
    if msg_idx is not None:
        col1, col2 = st.columns([1, 8])
        with col1:
            if st.button("🔊", key=f"speak_{msg_idx}", help="Listen to this response"):
                with st.spinner("Generating speech..."):
                    audio = synthesize_speech(text, lang)
                    if audio:
                        st.session_state[f"audio_{msg_idx}"] = audio
        
        # Play audio if available
        audio_key = f"audio_{msg_idx}"
        if audio_key in st.session_state and st.session_state[audio_key]:
            st.audio(st.session_state[audio_key], format="audio/wav")


# ════════════════════════════════════════════════════════════
# TYPING INDICATOR
# ════════════════════════════════════════════════════════════
def typing_indicator():
    st.markdown(
'<div style="display:flex;align-items:center;gap:10px;margin:12px 0;padding-left:42px;">'
'<div style="display:flex;gap:5px;align-items:center;">'
'<div style="width:7px;height:7px;border-radius:50%;background:#D4AF37;animation:pulse 1.2s ease infinite;"></div>'
'<div style="width:7px;height:7px;border-radius:50%;background:#D4AF37;animation:pulse 1.2s ease 0.2s infinite;"></div>'
'<div style="width:7px;height:7px;border-radius:50%;background:#D4AF37;animation:pulse 1.2s ease 0.4s infinite;"></div>'
'</div><div style="font-size:12px;color:#444;letter-spacing:1px;">AI is thinking...</div></div>',
        unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════
# LANGUAGE SELECTOR
# ════════════════════════════════════════════════════════════
LANGS = ["English", "Hindi", "Telugu", "Tamil", "Kannada", "Auto-Detect"]

def lang_selector():
    col1, col2, col3 = st.columns([1, 1, 4])
    with col1:
        lang = st.selectbox("Language", LANGS, index=0, label_visibility="collapsed", key="lang_sel")
    with col2:
        if st.button("🗑  Clear Chat", key="clear_btn"):
            call_clear(st.session_state.session_id)
            st.session_state.messages = []
            st.rerun()
    with col3:
        n = len(st.session_state.get("messages", [])) // 2
        st.markdown(
f'<div style="display:flex;align-items:center;gap:8px;padding-top:4px;">'
f'<div style="width:6px;height:6px;border-radius:50%;background:#22C55E;box-shadow:0 0 6px rgba(34,197,94,0.6);"></div>'
f'<div style="font-size:11px;color:#555;letter-spacing:1px;">Session: {st.session_state.get("session_id","")[:8]}... &nbsp;·&nbsp; {n} questions asked</div>'
f'</div>',
            unsafe_allow_html=True)
    return lang


# ════════════════════════════════════════════════════════════
# SIDEBAR
# ════════════════════════════════════════════════════════════
def doc_context_sidebar():
    with st.sidebar:
        st.markdown(
'<div style="padding:20px 0 16px;border-bottom:1px solid rgba(255,255,255,0.06);margin-bottom:16px;">'
'<div style="font-size:9px;color:#FF7722;letter-spacing:3px;text-transform:uppercase;margin-bottom:8px;">Context</div>'
'<div style="font-size:13px;color:#D4AF37;font-family:\'Playfair Display\',serif;">The Virtual Advocate</div>'
'<div style="font-size:11px;color:#555;margin-top:4px;">AI Legal Assistant</div>'
'</div>'
'<div style="font-size:9px;color:#555;letter-spacing:2px;text-transform:uppercase;margin-bottom:10px;">Ask About</div>',
            unsafe_allow_html=True)

        topics = [
            ("📋","Your Uploaded Document"),("💼","Employment Rights"),
            ("🏠","Tenant & Rent Laws"),("🛒","Consumer Protection"),
            ("📄","RTI Applications"),("💻","IT Act & Digital Rights"),
            ("🌸","Women's Rights"),("⚖️","Criminal Law — BNS 2023"),
        ]
        for icon, label in topics:
            st.markdown(
f'<div style="display:flex;align-items:center;gap:10px;padding:8px 10px;border-radius:8px;margin-bottom:4px;background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.04);">'
f'<span style="font-size:14px;">{icon}</span>'
f'<span style="font-size:12px;color:#8E8E93;">{label}</span></div>',
                unsafe_allow_html=True)

        st.markdown(
'<div style="margin-top:20px;padding:14px;background:rgba(212,175,55,0.05);border:1px solid rgba(212,175,55,0.12);border-radius:12px;">'
'<div style="font-size:9px;color:#D4AF37;letter-spacing:2px;text-transform:uppercase;margin-bottom:8px;">Important</div>'
'<div style="font-size:11px;color:#555;line-height:1.8;">Section 66A of IT Act:<br/><span style="color:#EF4444;">STRUCK DOWN 2015</span><br/>Cannot arrest for social media posts.<br/><br/>Emergency: Women 1091<br/>Police 100 · Legal Aid 15100</div>'
'</div>'
'<div style="margin-top:16px;">'
'<div style="font-size:9px;color:#555;letter-spacing:2px;text-transform:uppercase;margin-bottom:8px;">Navigate</div>',
            unsafe_allow_html=True)

        st.page_link("app.py",              label="⚖️  Home")
        st.page_link("pages/2_upload.py",   label="📜  Upload & Analyze")
        st.page_link("pages/4_generator.py",label="📋  Document Forge")
        st.page_link("pages/5_predict.py",  label="🔮  Case Predictor")
        st.markdown('</div>', unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════
# WELCOME SCREEN
# ════════════════════════════════════════════════════════════
def welcome_screen():
    st.markdown(
'<div style="max-width:760px;margin:0 auto;padding:0 0 32px;">'
'<div style="background:linear-gradient(145deg,rgba(18,14,8,0.95),rgba(10,8,4,0.98));border:1px solid rgba(212,175,55,0.15);border-radius:24px;padding:36px;margin-bottom:24px;text-align:center;">'
'<div style="font-size:48px;margin-bottom:16px;animation:flicker 5s infinite;">⚖️</div>'
'<div style="font-family:\'Playfair Display\',serif;font-size:22px;color:#D4AF37;margin-bottom:12px;">Your 24/7 Legal Advisor</div>'
'<div style="font-size:14px;color:#8E8E93;line-height:1.85;max-width:520px;margin:0 auto;">Ask any legal question in your language. Answers from ICA, IDA, RTI, CPA, BNS 2023 and more.<br/><br/><span style="color:#F5F5F7;">No fees. No appointment. No jargon.</span></div>'
'</div>'
'<div style="display:flex;gap:12px;justify-content:center;flex-wrap:wrap;margin-bottom:28px;">'
'<div style="padding:8px 20px;background:rgba(212,175,55,0.07);border:1px solid rgba(212,175,55,0.18);border-radius:50px;font-size:12px;color:#D4AF37;">⚖️ 14 Indian Laws</div>'
'<div style="padding:8px 20px;background:rgba(255,119,34,0.07);border:1px solid rgba(255,119,34,0.18);border-radius:50px;font-size:12px;color:#FF7722;">🗣 5 Languages</div>'
'<div style="padding:8px 20px;background:rgba(34,197,94,0.07);border:1px solid rgba(34,197,94,0.18);border-radius:50px;font-size:12px;color:#22C55E;">🔍 3,593 Law Chunks</div>'
'<div style="padding:8px 20px;background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.08);border-radius:50px;font-size:12px;color:#8E8E93;">💬 Free Always</div>'
'</div></div>',
        unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════
# API
# ════════════════════════════════════════════════════════════
def call_chat(question, session_id, language="English"):
    try:
        r = requests.post(
            f"{API}/chat/ask",
            json={"message": question, "session_id": session_id, "language": language},
            timeout=60,
        )
        r.raise_for_status()
        return r.json()
    except requests.exceptions.ConnectionError:
        return {"answer":"⚠️ Cannot connect to backend. Is uvicorn running on port 8000?","contract_hits":0,"law_hits":0}
    except requests.exceptions.Timeout:
        return {"answer":"⚠️ The AI took too long. Please try again.","contract_hits":0,"law_hits":0}
    except Exception as e:
        return {"answer":f"⚠️ Error: {str(e)}","contract_hits":0,"law_hits":0}

def call_clear(session_id):
    try: requests.post(f"{API}/chat/clear", json={"session_id": session_id}, timeout=10)
    except: pass


# ════════════════════════════════════════════════════════════
# MAIN
# ════════════════════════════════════════════════════════════
def main():
    inject_css()

    if "session_id" not in st.session_state: st.session_state.session_id = str(uuid.uuid4())[:16]
    if "messages"   not in st.session_state: st.session_state.messages   = []
    if "voice_text" not in st.session_state: st.session_state.voice_text = ""

    doc_context_sidebar()
    render_header()

    st.markdown('<div style="max-width:900px;margin:0 auto;padding:0 5% 120px;">', unsafe_allow_html=True)

    lang = lang_selector()
    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    # ── Voice Input Section ────────────────────────────────
    with st.expander("🎤 Voice Input — Speak Your Question", expanded=False):
        st.markdown(
            '<div style="font-size:12px;color:#8E8E93;margin-bottom:12px;">'
            'Record your question in Hindi, Telugu, Tamil, Kannada, or English. '
            'The AI will transcribe and answer.</div>',
            unsafe_allow_html=True
        )
        voice_col1, voice_col2 = st.columns([3, 1])
        with voice_col1:
            audio_input = st.audio_input("Record your question", key="voice_record", label_visibility="collapsed")
        with voice_col2:
            if audio_input:
                if st.button("🎯 Transcribe", key="transcribe_btn", use_container_width=True):
                    with st.spinner("Transcribing..."):
                        audio_bytes = audio_input.read()
                        text = transcribe_audio(audio_bytes, lang)
                        if text:
                            st.session_state.voice_text = text
                            st.success(f"✅ Transcribed: {text[:100]}...")
                        else:
                            st.error("Could not transcribe. Try speaking more clearly.")
        
        if st.session_state.voice_text:
            st.markdown(
                f'<div style="background:rgba(212,175,55,0.1);border:1px solid rgba(212,175,55,0.3);'
                f'border-radius:12px;padding:14px;margin-top:10px;font-size:14px;color:#F5F5F7;">'
                f'📝 <strong>Transcribed:</strong> {st.session_state.voice_text}</div>',
                unsafe_allow_html=True
            )
            if st.button("📤 Send This Question", key="send_voice_btn"):
                question = st.session_state.voice_text
                st.session_state.voice_text = ""
                st.session_state.messages.append({"role":"user","content":question})
                result = call_chat(question, st.session_state.session_id, lang)
                answer = result.get("answer","I could not process your question.")
                ch, lh = result.get("contract_hits",0), result.get("law_hits",0)
                st.session_state.messages.append({"role":"assistant","content":answer,"contract_hits":ch,"law_hits":lh})
                st.rerun()

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    selected_q = quick_questions()
    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

    if not st.session_state.messages:
        welcome_screen()
    else:
        st.markdown(
'<div style="display:flex;align-items:center;gap:16px;margin:8px 0 24px;">'
'<div style="flex:1;height:1px;background:rgba(255,255,255,0.04);"></div>'
'<div style="font-size:10px;color:#333;letter-spacing:2px;">CONVERSATION</div>'
'<div style="flex:1;height:1px;background:rgba(255,255,255,0.04);"></div>'
'</div>',
            unsafe_allow_html=True)

        # Render messages with speaker buttons
        msg_idx = 0
        for i, msg in enumerate(st.session_state.messages):
            if msg["role"] == "user":
                user_bubble(msg["content"])
            else:
                ai_bubble(msg["content"], msg.get("contract_hits",0), msg.get("law_hits",0), msg_idx=msg_idx, lang=lang)
                msg_idx += 1

    prompt   = st.chat_input("Ask your legal question... (Hindi, Telugu, English, Tamil, Kannada)", key="chat_input")
    question = selected_q or prompt

    if question:
        st.session_state.messages.append({"role":"user","content":question})
        user_bubble(question)

        slot = st.empty()
        with slot: typing_indicator()
        result = call_chat(question, st.session_state.session_id, lang)
        slot.empty()

        answer = result.get("answer","I could not process your question. Please try again.")
        ch     = result.get("contract_hits", 0)
        lh     = result.get("law_hits", 0)
        st.session_state.messages.append({"role":"assistant","content":answer,"contract_hits":ch,"law_hits":lh})
        ai_bubble(answer, ch, lh)
        st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown(
'<div style="text-align:center;margin-top:40px;padding:32px;border-top:1px solid rgba(255,255,255,0.04);font-size:11px;color:#333;letter-spacing:3px;text-transform:uppercase;">NYAYA-SETU &nbsp;·&nbsp; VIRTUAL ADVOCATE &nbsp;·&nbsp; INDIA &nbsp;·&nbsp; 2026</div>',
        unsafe_allow_html=True)

main()