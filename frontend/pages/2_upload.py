import streamlit as st
import base64, os, time, uuid, requests, math

st.set_page_config(
    page_title="Nyaya-Setu | Witness Stand",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

API = "http://localhost:8000"

LOGO_PATH = os.path.join(os.path.dirname(__file__), "nyayasetu_logo.jpg")
BG_PATH   = os.path.join(os.path.dirname(__file__), "nyaya_setu_bridge.png")

def b64(path):
    try:
        with open(path, "rb") as f: return base64.b64encode(f.read()).decode()
    except: return None

LOGO = b64(LOGO_PATH)
BG   = b64(BG_PATH)


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

# ════════════════════════════════════════════════════════════
# CSS — INJECT ONCE, no f-string interpolation of large data
# ════════════════════════════════════════════════════════════
def inject_css():
    # Background: use CSS variable set separately if bg exists
    bg_rule = (
        f"background-image:linear-gradient(rgba(3,3,5,0.88),rgba(3,3,5,0.97)),"
        f"url('data:image/png;base64,{BG}');"
        f"background-size:cover;background-position:center;background-attachment:fixed;"
    ) if BG else "background-color:#030305;"

    # FIX: Use st.html instead of st.markdown for CSS to avoid markdown parsing issues
    css_content = f"""<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;600;700&family=Playfair+Display:ital,wght@0,400;0,700;1,400&display=swap');

html,body,[data-testid="stAppViewContainer"] {{
    {bg_rule}
    color:#F5F5F7;
    font-family:'Plus Jakarta Sans',sans-serif;
}}
[data-testid="block-container"]{{ padding:0 !important; max-width:100% !important; }}
#MainMenu,header,footer{{ display:none !important; }}
.stDeployButton{{ display:none !important; }}
[data-testid="stSidebarNav"],[data-testid="stSidebarNavItems"],
nav[data-testid="stSidebarNav"],[data-testid="stSidebarContent"] ul,
[data-testid="stSidebarContent"] nav {{ display:none !important; }}

::-webkit-scrollbar{{ width:5px; }}
::-webkit-scrollbar-track{{ background:#030305; }}
::-webkit-scrollbar-thumb{{ background:#D4AF37;border-radius:3px; }}

/* Default button */
.stButton>button{{
    background:transparent !important;
    border:1px solid #D4AF37 !important;
    color:#D4AF37 !important;
    border-radius:50px !important;
    padding:10px 30px !important;
    font-weight:600 !important;
    letter-spacing:1px !important;
    font-size:13px !important;
    transition:0.3s !important;
    width:100% !important;
    font-family:'Plus Jakarta Sans',sans-serif !important;
}}
.stButton>button:hover{{
    background:#D4AF37 !important;
    color:#000 !important;
    box-shadow:0 0 24px rgba(212,175,55,0.45) !important;
}}

/* File uploader */
[data-testid="stFileUploader"]{{
    background:rgba(20,20,30,0.7) !important;
    border:2px dashed rgba(212,175,55,0.35) !important;
    border-radius:20px !important;
    padding:8px !important;
    transition:0.3s !important;
}}
[data-testid="stFileUploader"]:hover{{ border-color:#D4AF37 !important; }}
[data-testid="stCameraInput"]{{ border:2px solid rgba(212,175,55,0.3) !important; border-radius:20px !important; }}
[data-testid="stAudioInput"]{{ transform:scale(1.3); }}

/* Tabs */
.stTabs [data-baseweb="tab-list"]{{ background:transparent !important; border-bottom:1px solid rgba(255,255,255,0.05) !important; gap:2px !important; }}
.stTabs [data-baseweb="tab"]{{ background:transparent !important; color:#8E8E93 !important; border:none !important; padding:10px 22px !important; font-size:13px !important; letter-spacing:1px !important; border-radius:0 !important; }}
.stTabs [aria-selected="true"]{{ color:#D4AF37 !important; border-bottom:2px solid #D4AF37 !important; background:transparent !important; }}

/* Status */
[data-testid="stStatusWidget"]{{ background:rgba(20,20,30,0.9) !important; border:1px solid rgba(212,175,55,0.2) !important; border-radius:16px !important; }}

@keyframes fadein{{ from{{opacity:0;transform:translateY(14px);}} to{{opacity:1;transform:translateY(0);}} }}
@keyframes flicker{{ 0%,100%{{opacity:1;}} 50%{{opacity:0.78;}} }}

/* ══ MOBILE RESPONSIVE ══ */
@media (max-width: 768px) {{
    h1 {{ font-size: 32px !important; }}
    [data-testid="stFileUploader"] {{ padding: 16px !important; border-radius: 16px !important; }}
    [data-testid="stCameraInput"] {{ border-radius: 16px !important; }}
    [data-testid="stAudioInput"] {{ transform: scale(1.1) !important; }}
    .stButton>button {{ padding: 14px 20px !important; min-height: 48px !important; font-size: 14px !important; }}
    .stTabs [data-baseweb="tab"] {{ padding: 10px 14px !important; font-size: 12px !important; }}
    [data-testid="column"] {{ width: 100% !important; flex: 1 1 100% !important; margin-bottom: 16px !important; }}
}}
@media (max-width: 480px) {{
    h1 {{ font-size: 24px !important; }}
}}
</style>"""
    
    # Use st.html for pure HTML/CSS (newer Streamlit versions) or markdown with unsafe_allow_html
    try:
        st.html(css_content)
    except:
        st.markdown(css_content, unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════
# HEADER — logo rendered separately to avoid f-string overflow
# ════════════════════════════════════════════════════════════
def render_header():
    # Top ambient glow + orange label + headline
    st.markdown("""
<div style="text-align:center;padding:56px 5% 0;position:relative;overflow:hidden;">
    <div style="position:absolute;top:0;left:50%;transform:translateX(-50%);
        width:700px;height:300px;pointer-events:none;
        background:radial-gradient(ellipse at 50% 0%,rgba(212,175,55,0.08) 0%,transparent 70%);
    "></div>
</div>
""", unsafe_allow_html=True)

    # Logo — rendered with st.image to avoid huge inline base64 in HTML
    if LOGO:
        _, mid, _ = st.columns([2, 1, 2])
        with mid:
            logo_bytes = base64.b64decode(LOGO)
            st.image(logo_bytes, width=72)
    else:
        st.markdown('<div style="text-align:center;font-size:48px;padding-top:48px;">⚖️</div>',
                    unsafe_allow_html=True)

    # Headline — separate st.markdown, no large data inside
    st.markdown("""
<div style="text-align:center;padding:0 5% 44px;">
    <div style="font-size:11px;color:#FF7722;letter-spacing:6px;
        text-transform:uppercase;margin-bottom:14px;">The Witness Stand</div>
    <h1 style="
        font-family:'Playfair Display',serif;
        font-size:64px;margin:0 0 10px;line-height:1.1;
        background:linear-gradient(to bottom,#FFFFFF 30%,#D4AF37 100%);
        -webkit-background-clip:text;-webkit-text-fill-color:transparent;
    ">Your Contract,<br/>Cross-Examined.</h1>
    <p style="font-size:17px;color:#8E8E93;max-width:620px;
        margin:18px auto 0;line-height:1.75;">
        Upload any legal document — rental agreement, job offer, legal notice, loan paper.
        The AI reads every clause, cites the Indian law it violates,
        and tells you <em style="color:#F5F5F7;">exactly</em> what to change before you sign.
    </p>
</div>
""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════
# INPUT ZONE — 3 columns
# ════════════════════════════════════════════════════════════
def input_zone():
    col1, col2, col3 = st.columns(3, gap="large")

    with col1:
        st.markdown("""
<div style="background:rgba(255,255,255,0.025);backdrop-filter:blur(20px);
    border:1px solid rgba(212,175,55,0.22);border-radius:24px;
    padding:32px 28px 20px;text-align:center;margin-bottom:14px;">
    <div style="font-size:52px;margin-bottom:14px;">📄</div>
    <div style="font-family:'Playfair Display',serif;font-size:24px;
        color:#D4AF37;margin-bottom:8px;">Upload Document</div>
    <div style="font-size:13px;color:#8E8E93;line-height:1.7;">
        Rental agreements, job offers, legal notices, loan papers.
        Supports PDF, JPG, PNG.
    </div>
</div>""", unsafe_allow_html=True)
        uploaded = st.file_uploader("Upload Legal Document",
            type=["pdf","png","jpg","jpeg"],
            label_visibility="collapsed", key="doc_upload")

    with col2:
        st.markdown("""
<div style="background:rgba(255,255,255,0.025);backdrop-filter:blur(20px);
    border:1px solid rgba(212,175,55,0.22);border-radius:24px;
    padding:32px 28px 20px;text-align:center;margin-bottom:14px;">
    <div style="font-size:52px;margin-bottom:14px;">📸</div>
    <div style="font-family:'Playfair Display',serif;font-size:24px;
        color:#D4AF37;margin-bottom:8px;">Scan Evidence</div>
    <div style="font-size:13px;color:#8E8E93;line-height:1.7;">
        Point your camera at any legal document.
        OCR extracts every word automatically.
    </div>
</div>""", unsafe_allow_html=True)
        camera = st.camera_input("Capture Image",
            label_visibility="collapsed", key="cam")

    with col3:
        st.markdown("""
<div style="background:rgba(255,119,34,0.06);backdrop-filter:blur(20px);
    border:1px solid rgba(255,119,34,0.25);border-radius:24px;
    padding:32px 28px 20px;text-align:center;margin-bottom:14px;">
    <div style="font-size:52px;margin-bottom:14px;">🎙️</div>
    <div style="font-family:'Playfair Display',serif;font-size:24px;
        color:#FF7722;margin-bottom:8px;">Voice Statement</div>
    <div style="font-size:13px;color:#8E8E93;line-height:1.7;">
        Explain your legal problem in Hindi, Telugu,
        English, Tamil or Kannada.
        Bhashini AI transcribes and analyzes.
    </div>
</div>""", unsafe_allow_html=True)
        audio = st.audio_input("Record Voice",
            label_visibility="collapsed", key="voice")

    return uploaded, camera, audio


# ════════════════════════════════════════════════════════════
# SVG GAUGE — no f-string with base64, just numbers
# ════════════════════════════════════════════════════════════
def render_gauge(score, level):
    if   score <= 3: col, glow = "#22C55E", "rgba(34,197,94,0.5)"
    elif score <= 6: col, glow = "#F59E0B", "rgba(245,158,11,0.5)"
    elif score <= 8: col, glow = "#EF4444", "rgba(239,68,68,0.5)"
    else:            col, glow = "#991B1B", "rgba(153,27,27,0.6)"

    angle = -90 + (score / 10) * 180
    nx = round(120 + 82 * math.cos(math.radians(angle + 180)), 1)
    ny = round(120 + 82 * math.sin(math.radians(angle + 180)), 1)
    fill = round((score / 10) * 314, 1)

    # FIX: Ensure no leading whitespace in f-string HTML
    gauge_html = f"""<div style="text-align:center;padding:24px 0 16px;">
<div style="width:220px;height:125px;margin:0 auto 16px;position:relative;">
<svg viewBox="0 0 240 130" style="width:100%;height:100%;">
<defs>
<linearGradient id="arcgrad" x1="0%" y1="0%" x2="100%" y2="0%">
<stop offset="0%" stop-color="#22C55E"/>
<stop offset="50%" stop-color="#F59E0B"/>
<stop offset="100%" stop-color="#EF4444"/>
</linearGradient>
</defs>
<path d="M20 120 A100 100 0 0 1 220 120"
fill="none" stroke="rgba(255,255,255,0.05)"
stroke-width="16" stroke-linecap="round"/>
<path d="M20 120 A100 100 0 0 1 220 120"
fill="none" stroke="url(#arcgrad)"
stroke-width="16" stroke-linecap="round"
stroke-dasharray="314"
stroke-dashoffset="{314 - fill}"/>
<line x1="120" y1="120" x2="{nx}" y2="{ny}"
stroke="{col}" stroke-width="3" stroke-linecap="round"
style="filter:drop-shadow(0 0 5px {glow})"/>
<circle cx="120" cy="120" r="5" fill="{col}"
style="filter:drop-shadow(0 0 8px {glow})"/>
<text x="14" y="128" fill="#444" font-size="9" text-anchor="middle">1</text>
<text x="120" y="18" fill="#444" font-size="9" text-anchor="middle">5</text>
<text x="226" y="128" fill="#444" font-size="9" text-anchor="middle">10</text>
</svg>
</div>
<div style="font-family:'Playfair Display',serif;font-size:54px;
font-weight:700;color:{col};line-height:1;
text-shadow:0 0 28px {glow};">{score}</div>
<div style="font-size:10px;color:#555;letter-spacing:3px;
text-transform:uppercase;margin:6px 0 10px;">out of 10</div>
<div style="display:inline-block;border:1px solid {col}55;
color:{col};font-size:12px;font-weight:700;letter-spacing:2px;
text-transform:uppercase;padding:5px 18px;border-radius:50px;
background:rgba(255,255,255,0.03);box-shadow:0 0 12px {glow};">{level}</div>
</div>"""
    
    st.markdown(gauge_html, unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════
# CLAUSE CARD
# ════════════════════════════════════════════════════════════
def clause_card(c):
    rl    = c.get("risk_level", "medium")
    ct    = c.get("clause_type", "").replace("_", " ").title()
    sev   = int(c.get("severity_score", 5))
    text  = c.get("clause_text", "")[:220]
    why   = c.get("why_risky", "")
    legal = c.get("legal_reference", {})
    rec   = c.get("recommendation", "")
    neg   = c.get("negotiable", True)
    flag  = c.get("red_flag", False)
    enf   = legal.get("enforceability", "")

    rl_col  = "#EF4444" if rl == "high" else "#F59E0B" if rl == "medium" else "#22C55E"
    sev_col = "#EF4444" if sev >= 7     else "#F59E0B" if sev >= 4      else "#22C55E"

    flag_html = (
        '<div style="display:inline-block;background:rgba(239,68,68,0.15);'
        'border:1px solid rgba(239,68,68,0.5);color:#EF4444;'
        'font-size:10px;letter-spacing:2px;padding:3px 12px;'
        'border-radius:50px;margin-bottom:10px;">🚩 POTENTIALLY ILLEGAL</div>'
    ) if flag else ""

    neg_chip = (
        '<div style="padding:4px 14px;background:rgba(34,197,94,0.08);'
        'border:1px solid rgba(34,197,94,0.22);border-radius:50px;'
        'font-size:11px;color:#22C55E;">✓ Negotiable</div>'
    ) if neg else (
        '<div style="padding:4px 14px;background:rgba(239,68,68,0.07);'
        'border:1px solid rgba(239,68,68,0.2);border-radius:50px;'
        'font-size:11px;color:#EF4444;">✕ Non-Negotiable</div>'
    )

    enf_row = (
        f'<div style="font-size:11px;color:#555;border-top:1px solid rgba(255,255,255,0.04);'
        f'padding-top:8px;margin-top:8px;">Enforceability: {enf}</div>'
    ) if enf else ""

    # FIX: Build HTML without indentation issues
    card_html = f"""<div style="background:linear-gradient(145deg,rgba(18,14,8,0.92),rgba(10,8,4,0.96));
border:1px solid rgba(255,255,255,0.05);border-left:3px solid {rl_col};
border-radius:20px;padding:28px;margin-bottom:16px;animation:fadein 0.5s ease both;">
<div style="display:flex;justify-content:space-between;align-items:flex-start;
gap:16px;margin-bottom:18px;flex-wrap:wrap;">
<div style="flex:1;">
{flag_html}
<div style="font-family:'Playfair Display',serif;
font-size:20px;color:#D4AF37;margin-bottom:6px;">{ct}</div>
<div style="font-size:12px;color:#444;font-style:italic;
line-height:1.5;max-width:480px;">"{text}..."</div>
</div>
<div style="text-align:center;flex-shrink:0;">
<div style="font-family:'Playfair Display',serif;
font-size:34px;color:{sev_col};line-height:1;
text-shadow:0 0 12px {sev_col}44;">{sev}</div>
<div style="font-size:9px;color:#444;letter-spacing:2px;">SEVERITY</div>
<div style="width:56px;height:3px;background:rgba(255,255,255,0.06);
border-radius:2px;margin:6px auto 0;overflow:hidden;">
<div style="width:{sev * 10}%;height:100%;
background:{sev_col};border-radius:2px;"></div>
</div>
</div>
</div>
<div style="margin-bottom:16px;">
<div style="font-size:10px;color:#FF7722;letter-spacing:2px;
text-transform:uppercase;margin-bottom:8px;">Why This Is Risky</div>
<div style="font-size:14px;color:#B8B8BE;line-height:1.8;">{why}</div>
</div>
<div style="background:rgba(212,175,55,0.05);border:1px solid rgba(212,175,55,0.14);
border-radius:14px;padding:16px 20px;margin-bottom:14px;">
<div style="font-size:10px;color:#D4AF37;letter-spacing:2px;
text-transform:uppercase;margin-bottom:8px;">⚖ Indian Law</div>
<div style="font-size:14px;color:#F5F5F7;font-weight:600;margin-bottom:4px;">
{legal.get("act","Indian Contract Act 1872")}
&nbsp;·&nbsp;
<span style="color:#D4AF37;">{legal.get("section","")}</span>
</div>
<div style="font-size:13px;color:#8E8E93;line-height:1.65;">
{legal.get("summary","")}
</div>
{enf_row}
</div>
<div style="background:rgba(34,197,94,0.04);border:1px solid rgba(34,197,94,0.13);
border-radius:14px;padding:16px 20px;margin-bottom:16px;">
<div style="font-size:10px;color:#22C55E;letter-spacing:2px;
text-transform:uppercase;margin-bottom:8px;">💡 What To Do</div>
<div style="font-size:14px;color:#B8B8BE;line-height:1.8;">{rec}</div>
</div>
<div style="display:flex;gap:8px;flex-wrap:wrap;">
{neg_chip}
<div style="padding:4px 14px;background:rgba(255,255,255,0.03);
border:1px solid rgba(255,255,255,0.07);border-radius:50px;
font-size:11px;color:#555;text-transform:uppercase;letter-spacing:1px;">{rl} risk</div>
</div>
</div>"""
    
    st.markdown(card_html, unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════
# RESULTS — verdict + tabs
# ════════════════════════════════════════════════════════════
def render_results(data):
    risk      = data.get("risk", {})
    clauses   = data.get("clauses", [])
    score     = risk.get("score", 5)
    level     = risk.get("level", "Moderate Risk")
    action    = risk.get("action", "Review all clauses carefully before signing.")
    summary   = risk.get("summary", "")
    concerns  = risk.get("top_concerns", [])
    rb        = risk.get("risk_breakdown", {})
    sb        = risk.get("scoring_breakdown", {})
    explained = risk.get("explained_clauses", [])

    RC = {"Very Safe":"#22C55E","Mostly Fair":"#84CC16",
          "Moderate Risk":"#F59E0B","High Risk":"#EF4444",
          "Very High Risk":"#991B1B"}.get(level, "#F59E0B")

    # Verdict banner + gauge
    col_text, col_gauge = st.columns([2, 1])
    with col_text:
        verdict_html = f"""<div style="background:linear-gradient(145deg,rgba(18,14,6,0.97),rgba(8,6,3,0.99));
border:1px solid {RC}33;border-left:4px solid {RC};
border-radius:22px;padding:32px 36px;
height:100%;animation:fadein 0.7s ease both;">
<div style="font-size:10px;color:{RC};letter-spacing:3px;
text-transform:uppercase;margin-bottom:8px;">Court Verdict</div>
<div style="font-family:'Playfair Display',serif;
font-size:30px;color:#F5F5F7;margin-bottom:12px;">{level}</div>
<div style="font-size:14px;color:#A1A1AA;line-height:1.75;margin-bottom:12px;">
{action}</div>
<div style="font-size:13px;color:#555;line-height:1.7;font-style:italic;">
{summary[:280]}</div>
</div>"""
        st.markdown(verdict_html, unsafe_allow_html=True)

    with col_gauge:
        st.markdown(f"""<div style="background:rgba(255,255,255,0.02);
border:1px solid rgba(255,255,255,0.05);
border-radius:22px;padding:8px;height:100%;">""",
            unsafe_allow_html=True)
        render_gauge(score, level)
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

    # Top concerns
    if concerns:
        items = "".join([
            f'<div style="display:flex;gap:12px;align-items:flex-start;margin-bottom:12px;">'
            f'<div style="min-width:22px;height:22px;border-radius:50%;background:#EF4444;'
            f'display:flex;align-items:center;justify-content:center;'
            f'font-size:11px;font-weight:700;margin-top:1px;">!</div>'
            f'<div style="font-size:14px;color:#E5E5E7;line-height:1.65;">{c}</div>'
            f'</div>'
            for c in concerns
        ])
        concerns_html = f"""<div style="background:rgba(239,68,68,0.05);border:1px solid rgba(239,68,68,0.18);
border-radius:20px;padding:28px 32px;margin-bottom:22px;">
<div style="font-size:10px;color:#EF4444;letter-spacing:3px;
text-transform:uppercase;margin-bottom:18px;">⚠ Top Concerns</div>
{items}
</div>"""
        st.markdown(concerns_html, unsafe_allow_html=True)

    # Breakdown chips
    if rb:
        flag_pill = (
            '<div style="padding:10px 20px;background:rgba(239,68,68,0.12);'
            'border:1px solid rgba(239,68,68,0.4);border-radius:50px;'
            'font-size:13px;color:#EF4444;font-weight:700;">🚩 Potentially Illegal</div>'
        ) if rb.get("red_flag_count", 0) > 0 else ""
        
        chips_html = f"""<div style="display:flex;gap:12px;flex-wrap:wrap;margin-bottom:24px;">
<div style="padding:10px 20px;background:rgba(239,68,68,0.08);
border:1px solid rgba(239,68,68,0.22);border-radius:50px;
font-size:13px;color:#EF4444;font-weight:600;">
🔴 {rb.get("high_risk",0)} High Risk</div>
<div style="padding:10px 20px;background:rgba(245,158,11,0.08);
border:1px solid rgba(245,158,11,0.22);border-radius:50px;
font-size:13px;color:#F59E0B;font-weight:600;">
🟡 {rb.get("medium_risk",0)} Medium</div>
<div style="padding:10px 20px;background:rgba(34,197,94,0.08);
border:1px solid rgba(34,197,94,0.22);border-radius:50px;
font-size:13px;color:#22C55E;font-weight:600;">
🟢 {rb.get("low_risk",0)} Safe</div>
<div style="padding:10px 20px;background:rgba(212,175,55,0.07);
border:1px solid rgba(212,175,55,0.18);border-radius:50px;
font-size:13px;color:#D4AF37;font-weight:600;">
✎ {rb.get("negotiable_count",0)} Negotiable</div>
{flag_pill}
</div>"""
        st.markdown(chips_html, unsafe_allow_html=True)

    # Clause tabs
    high_cl = [c for c in explained if c.get("risk_level") == "high"]
    med_cl  = [c for c in explained if c.get("risk_level") == "medium"]
    low_cl  = [c for c in clauses   if c.get("risk_level") == "low"]

    t1, t2, t3 = st.tabs([
        f"🔴  High Risk  ({len(high_cl)})",
        f"🟡  Medium Risk  ({len(med_cl)})",
        f"🟢  Safe Clauses  ({len(low_cl)})",
    ])
    with t1:
        if high_cl:
            for c in high_cl:
                clause_card(c)
        else:
            st.markdown(
                '<div style="padding:32px;text-align:center;color:#444;">No high-risk clauses found.</div>',
                unsafe_allow_html=True
            )
    with t2:
        if med_cl:
            for c in med_cl:
                clause_card(c)
        else:
            st.markdown(
                '<div style="padding:32px;text-align:center;color:#444;">No medium-risk clauses found.</div>',
                unsafe_allow_html=True
            )
    with t3:
        if low_cl:
            for c in low_cl:
                safe_html = f"""<div style="background:rgba(34,197,94,0.04);border:1px solid rgba(34,197,94,0.12);
border-left:3px solid #22C55E;border-radius:14px;padding:18px 22px;margin-bottom:12px;">
<div style="font-size:14px;color:#22C55E;font-weight:600;margin-bottom:6px;">
✓ {c.get("clause_type","").replace("_"," ").title()}</div>
<div style="font-size:13px;color:#8E8E93;line-height:1.65;">
{c.get("explanation","This clause appears fair and standard.")}</div>
</div>"""
                st.markdown(safe_html, unsafe_allow_html=True)
        else:
            st.markdown(
                '<div style="padding:32px;text-align:center;color:#444;">No safe clauses identified.</div>',
                unsafe_allow_html=True
            )

    # Scoring breakdown
    if sb:
        score_html = f"""<div style="background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.05);
border-radius:18px;padding:24px 32px;margin-top:24px;">
<div style="font-size:10px;color:#444;letter-spacing:3px;
text-transform:uppercase;margin-bottom:18px;">How the Score Was Calculated</div>
<div style="display:flex;gap:24px;flex-wrap:wrap;align-items:center;">
<div>
<div style="font-family:'Playfair Display',serif;
font-size:30px;color:#D4AF37;">{sb.get("rule_score","—")}</div>
<div style="font-size:9px;color:#444;letter-spacing:2px;margin-top:4px;">
RULE SCORE<br/><span style="font-size:10px;color:#333;">clause weights</span></div>
</div>
<div style="font-size:20px;color:#333;">+</div>
<div>
<div style="font-family:'Playfair Display',serif;
font-size:30px;color:#D4AF37;">{sb.get("llm_score","—")}</div>
<div style="font-size:9px;color:#444;letter-spacing:2px;margin-top:4px;">
AI SCORE<br/><span style="font-size:10px;color:#333;">context reasoning</span></div>
</div>
<div style="font-size:20px;color:#333;">=</div>
<div>
<div style="font-family:'Playfair Display',serif;
font-size:40px;color:#F5F5F7;font-weight:700;">{sb.get("final_score","—")}</div>
<div style="font-size:9px;color:#D4AF37;letter-spacing:2px;margin-top:4px;">
FINAL SCORE<br/><span style="font-size:10px;color:#555;">{sb.get("method","hybrid")}</span></div>
</div>
</div>
</div>"""
        st.markdown(score_html, unsafe_allow_html=True)

    # Next steps
    st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("💬  Chat About This Document", key="go_chat"):
            st.switch_page("pages/1_chat.py")
    with c2:
        if st.button("📋  Generate Legal Notice", key="go_gen"):
            st.switch_page("pages/4_generator.py")
    with c3:
        if st.button("🔮  Predict Case Outcome", key="go_pred"):
            st.switch_page("pages/5_predict.py")


# ════════════════════════════════════════════════════════════
# API
# ════════════════════════════════════════════════════════════
def call_api(file_bytes, filename, ctype, session_id):
    try:
        r = requests.post(
            f"{API}/analyze/upload",
            files={"file": (filename, file_bytes, ctype)},
            data={"session_id": session_id},
            timeout=90,
        )
        r.raise_for_status()
        return r.json()
    except requests.exceptions.ConnectionError:
        return {"error": "Cannot connect to backend. Is uvicorn running?"}
    except requests.exceptions.Timeout:
        return {"error": "Backend timeout — large documents may take longer."}
    except Exception as e:
        return {"error": str(e)}


# ════════════════════════════════════════════════════════════
# MAIN
# ════════════════════════════════════════════════════════════
def main():
    inject_css()

    if "sid"    not in st.session_state: st.session_state.sid    = str(uuid.uuid4())[:16]
    if "result" not in st.session_state: st.session_state.result = None

    render_header()

    # ── Input zone ──
    st.markdown('<div style="padding:0 5%;max-width:1200px;margin:0 auto;">', unsafe_allow_html=True)
    uploaded, camera, audio = input_zone()
    st.markdown('</div>', unsafe_allow_html=True)

    # Determine what file to use
    file_bytes = ctype = fname = None
    if uploaded:
        file_bytes = uploaded.read()
        fname      = uploaded.name
        ext        = fname.split(".")[-1].lower()
        ctype      = "application/pdf" if ext == "pdf" else f"image/{ext}"
    elif camera:
        file_bytes = camera.getvalue()
        fname      = "camera_capture.jpg"
        ctype      = "image/jpeg"
    elif audio:
        # Voice transcription with Bhashini
        st.markdown("""
<div style="background:rgba(255,119,34,0.07);border:1px solid rgba(255,119,34,0.25);
border-radius:14px;padding:18px 28px;margin:16px 5%;">
<div style="font-size:14px;color:#FF7722;text-align:center;margin-bottom:12px;">
🎙️ Voice recording received — Bhashini AI will transcribe your legal statement.
</div>
</div>""", unsafe_allow_html=True)
        
        # Language selector for voice
        lang_col1, lang_col2, lang_col3 = st.columns([1, 2, 1])
        with lang_col2:
            voice_lang = st.selectbox(
                "Select your speaking language",
                ["Hindi", "Telugu", "Tamil", "Kannada", "English"],
                key="voice_lang"
            )
            if st.button("🎯 Transcribe Voice", key="transcribe_voice_btn", use_container_width=True):
                with st.spinner("Transcribing with Bhashini AI..."):
                    audio_bytes = audio.read()
                    transcribed = transcribe_audio(audio_bytes, voice_lang)
                    if transcribed:
                        st.session_state["voice_transcription"] = transcribed
                        st.success("✅ Voice transcribed successfully!")
                    else:
                        st.error("Could not transcribe. Please speak clearly and try again.")
        
        # Show transcription if available
        if "voice_transcription" in st.session_state and st.session_state["voice_transcription"]:
            st.markdown(f"""
<div style="background:rgba(34,197,94,0.08);border:1px solid rgba(34,197,94,0.25);
border-radius:14px;padding:18px 28px;margin:16px 5%;">
<div style="font-size:11px;color:#4ADE80;letter-spacing:2px;text-transform:uppercase;margin-bottom:8px;">
📝 Your Voice Statement
</div>
<div style="font-size:15px;color:#F5F5F7;line-height:1.8;">
{st.session_state["voice_transcription"]}
</div>
</div>""", unsafe_allow_html=True)
            st.info("💡 This transcription has been saved. You can now use the Chat page to ask questions about your situation, or upload a related document for full analysis.")

    # ── Analyze button ──
    if file_bytes:
        st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
        _, mid, _ = st.columns([1, 2, 1])
        with mid:
            clicked = st.button("⚖️  Begin Legal Analysis", key="analyze")

        if clicked:
            with st.status("⚖️  AI Court in Session...", expanded=True) as status:
                st.write("📄  Extracting text from document...")
                time.sleep(0.7)
                st.write("🛡️  Removing personal data (Aadhaar, PAN, phone)...")
                time.sleep(0.5)
                st.write("📋  Identifying legal clause types...")
                time.sleep(0.5)
                st.write("⚖️  Cross-referencing Indian statutes...")
                time.sleep(0.5)
                st.write("🔴  Calculating risk score (rule + AI hybrid)...")
                time.sleep(0.5)
                st.write("💡  Generating plain-language explanations...")
                r = call_api(file_bytes, fname, ctype, st.session_state.sid)
                if "error" not in r:
                    st.session_state.result = r
                    st.session_state.sid    = r.get("session_id", st.session_state.sid)
                    status.update(label="✅  The court has reached a verdict.", state="complete")
                else:
                    status.update(label="❌  Analysis failed.", state="error")
                    error_html = f"""<div style="background:rgba(239,68,68,0.08);border:1px solid rgba(239,68,68,0.22);
border-radius:14px;padding:20px 24px;margin:16px 0;">
<div style="color:#EF4444;font-weight:700;margin-bottom:6px;">Connection Error</div>
<div style="color:#A1A1AA;font-size:14px;">{r["error"]}</div>
<div style="color:#555;font-size:12px;margin-top:10px;">
Run: <code style="color:#D4AF37;">uvicorn backend.main:app --reload</code>
</div>
</div>"""
                    st.markdown(error_html, unsafe_allow_html=True)

    # ── Results ──
    if st.session_state.result:
        st.markdown("""
<div style="text-align:center;padding:44px 0 12px;">
<div style="font-size:11px;color:#FF7722;letter-spacing:5px;
text-transform:uppercase;margin-bottom:10px;">Verdict</div>
<div style="font-family:'Playfair Display',serif;font-size:36px;color:#F5F5F7;">
The Court Has Examined Your Document.
</div>
</div>""", unsafe_allow_html=True)
        st.markdown('<div style="padding:0 5%;max-width:1200px;margin:0 auto;">', unsafe_allow_html=True)
        render_results(st.session_state.result)
        st.markdown('</div>', unsafe_allow_html=True)

    elif not file_bytes:
        st.markdown("""
<div style="max-width:680px;margin:36px auto;
background:rgba(212,175,55,0.04);
border:1px solid rgba(212,175,55,0.12);
border-radius:24px;padding:48px;text-align:center;">
<div style="font-size:58px;margin-bottom:18px;animation:flicker 5s infinite;">📜</div>
<div style="font-family:'Playfair Display',serif;font-size:26px;
color:#D4AF37;margin-bottom:12px;">Awaiting Your Document</div>
<div style="font-size:14px;color:#8E8E93;line-height:1.85;margin-bottom:18px;">
Upload a document, take a photo, or record your voice above
to begin the AI cross-examination.<br/><br/>
Every clause checked against Indian law in under 30 seconds.
</div>
<div style="font-size:11px;color:#444;letter-spacing:3px;text-transform:uppercase;">
Rental Agreement &nbsp;·&nbsp; Job Offer &nbsp;·&nbsp; Legal Notice &nbsp;·&nbsp; Loan Paper
</div>
</div>""", unsafe_allow_html=True)

    # Footer
    st.markdown("""
<div style="text-align:center;margin-top:80px;padding:40px;
border-top:1px solid rgba(255,255,255,0.04);
font-size:11px;color:#444;letter-spacing:3px;text-transform:uppercase;">
NYAYA-SETU &nbsp;·&nbsp; MULTI-MODAL JUSTICE SYSTEM &nbsp;·&nbsp; INDIA &nbsp;·&nbsp; 2026
</div>""", unsafe_allow_html=True)

main()