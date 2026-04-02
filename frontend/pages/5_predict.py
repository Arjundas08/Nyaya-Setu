import streamlit as st
import base64, os, time, math, requests, textwrap

st.set_page_config(
    page_title="Nyaya-Setu | The Oracle",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="collapsed",
)

API       = "http://localhost:8000"
BG_PATH   = os.path.join(os.path.dirname(__file__), "nyaya_setu_bridge.png")
LOGO_PATH = os.path.join(os.path.dirname(__file__), "nyayasetu_logo.jpg")

def b64(path):
    try:
        with open(path, "rb") as f: return base64.b64encode(f.read()).decode()
    except: return None

BG   = b64(BG_PATH)
LOGO = b64(LOGO_PATH)

# ── safe markdown helper — strips leading indent ──────────
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


# ════════════════════════════════════════════════════════════
# WIN PROBABILITY GAUGE — SVG arc using stroke-dasharray
# ════════════════════════════════════════════════════════════
def gauge_svg(prob: int) -> str:
    r      = 88
    cx, cy = 130, 120
    semi   = round(math.pi * r, 2)          # semicircle length ≈ 276.46
    fill   = round(semi * prob / 100, 2)
    offset = round(semi - fill, 2)

    if prob >= 68:
        color, label, glow = "#22C55E", "STRONG CASE",      "#22C55E44"
    elif prob >= 45:
        color, label, glow = "#F59E0B", "MODERATE CASE",    "#F59E0B44"
    elif prob >= 25:
        color, label, glow = "#EF4444", "CHALLENGING",      "#EF444444"
    else:
        color, label, glow = "#A855F7", "HIGH RISK",        "#A855F744"

    # d="M left A r,r 0 0 1 right" draws the top semicircle
    lx, ly = cx - r, cy
    rx, ry = cx + r, cy

    return (
        f'<svg width="260" height="150" viewBox="0 0 260 150" xmlns="http://www.w3.org/2000/svg">'
        f'<defs>'
        f'<filter id="glow"><feGaussianBlur stdDeviation="4" result="blur"/>'
        f'<feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge></filter>'
        f'</defs>'
        f'<path d="M {lx},{ly} A {r},{r} 0 0 1 {rx},{ry}" fill="none" '
        f'stroke="rgba(255,255,255,0.06)" stroke-width="20" stroke-linecap="round"/>'
        f'<path d="M {lx},{ly} A {r},{r} 0 0 1 {rx},{ry}" fill="none" '
        f'stroke="{color}" stroke-width="20" stroke-linecap="round" filter="url(#glow)" '
        f'stroke-dasharray="{semi} {semi}" stroke-dashoffset="{offset}"/>'
        f'<text x="{cx}" y="{cy - 8}" text-anchor="middle" fill="{color}" '
        f'font-size="36" font-weight="800" font-family="Plus Jakarta Sans,sans-serif">{prob}%</text>'
        f'<text x="{cx}" y="{cy + 18}" text-anchor="middle" fill="#8E8E93" '
        f'font-size="10" letter-spacing="2" font-family="Plus Jakarta Sans,sans-serif">{label}</text>'
        f'</svg>'
    )


# ════════════════════════════════════════════════════════════
# CSS
# ════════════════════════════════════════════════════════════
def inject_css():
    bg_rule = (
        f"background-image:linear-gradient(rgba(3,3,5,0.94),rgba(3,3,5,0.99)),"
        f"url('data:image/png;base64,{BG}');"
        f"background-size:cover;background-position:center;background-attachment:fixed;"
    ) if BG else "background-color:#030305;"

    st.markdown(f"""<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;600;700&family=Playfair+Display:ital,wght@0,400;0,700;1,400&display=swap');
html,body,[data-testid="stAppViewContainer"]{{ {bg_rule} color:#F5F5F7;font-family:'Plus Jakarta Sans',sans-serif; }}
[data-testid="block-container"]{{padding:0!important;max-width:100%!important;}}
#MainMenu,header,footer{{display:none!important;}}
.stDeployButton{{display:none!important;}}
[data-testid="stSidebarNav"],[data-testid="stSidebarNavItems"],
nav[data-testid="stSidebarNav"],[data-testid="stSidebarContent"] ul,
[data-testid="stSidebarContent"] nav{{display:none!important;}}
::-webkit-scrollbar{{width:5px;}}
::-webkit-scrollbar-track{{background:#030305;}}
::-webkit-scrollbar-thumb{{background:#D4AF37;border-radius:3px;}}
.stButton>button{{background:transparent!important;border:1px solid #D4AF37!important;color:#D4AF37!important;border-radius:50px!important;padding:10px 28px!important;font-weight:600!important;letter-spacing:1px!important;font-size:13px!important;transition:0.3s!important;font-family:'Plus Jakarta Sans',sans-serif!important;}}
.stButton>button:hover{{background:#D4AF37!important;color:#000!important;box-shadow:0 0 20px rgba(212,175,55,0.4)!important;}}
[data-testid="stTextArea"]>div>div>textarea{{background:rgba(15,15,25,0.9)!important;border:1px solid rgba(212,175,55,0.25)!important;border-radius:14px!important;color:#F5F5F7!important;font-size:14px!important;line-height:1.7!important;padding:14px!important;}}
[data-testid="stTextArea"]>div>div>textarea:focus{{border-color:#D4AF37!important;box-shadow:0 0 20px rgba(212,175,55,0.12)!important;}}
[data-testid="stSelectbox"]>div>div{{background:rgba(15,15,25,0.9)!important;border:1px solid rgba(212,175,55,0.2)!important;border-radius:12px!important;color:#F5F5F7!important;}}
[data-testid="stTextInput"]>div>div>input{{background:rgba(15,15,25,0.9)!important;border:1px solid rgba(212,175,55,0.2)!important;border-radius:12px!important;color:#F5F5F7!important;font-size:14px!important;padding:10px 16px!important;}}
[data-testid="stTextInput"]>div>div>input:focus{{border-color:#D4AF37!important;box-shadow:0 0 15px rgba(212,175,55,0.1)!important;}}
[data-testid="stStatusWidget"]{{background:rgba(15,15,25,0.95)!important;border:1px solid rgba(212,175,55,0.2)!important;border-radius:14px!important;}}
@keyframes fadein{{from{{opacity:0;transform:translateY(14px);}}to{{opacity:1;transform:translateY(0);}}}}
@keyframes pulse{{0%,100%{{opacity:1;}}50%{{opacity:0.5;}}}}
.oracle-section{{animation:fadein 0.5s ease both;}}

/* ══ MOBILE RESPONSIVE ══ */
@media (max-width: 768px) {{
    h1 {{ font-size: 32px !important; }}
    .stButton>button {{ padding: 14px 20px !important; min-height: 48px !important; }}
    [data-testid="stTextArea"]>div>div>textarea {{ font-size: 16px !important; min-height: 140px !important; }}
    [data-testid="stTextInput"]>div>div>input {{ font-size: 16px !important; }}
    [data-testid="stAudioInput"] {{ transform: scale(1.1) !important; }}
    [data-testid="column"] {{ width: 100% !important; flex: 1 1 100% !important; }}
}}
@media (max-width: 480px) {{
    h1 {{ font-size: 24px !important; }}
}}
</style>""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════
# HEADER
# ════════════════════════════════════════════════════════════
def render_header():
    st.markdown(
"""<div style="text-align:center;padding:56px 5% 24px;position:relative;overflow:hidden;">
<div style="position:absolute;top:0;left:50%;transform:translateX(-50%);width:800px;height:320px;pointer-events:none;background:radial-gradient(ellipse at 50% 0%,rgba(168,85,247,0.06) 0%,rgba(212,175,55,0.04) 50%,transparent 70%);"></div>
<div style="font-size:11px;color:#A855F7;letter-spacing:6px;text-transform:uppercase;margin-bottom:14px;">The Oracle</div>
<h1 style="font-family:'Playfair Display',serif;font-size:52px;margin:0 0 10px;line-height:1.1;background:linear-gradient(to bottom,#FFFFFF 20%,#D4AF37 80%,#A855F7 100%);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">Know Your Odds.<br/>Before You Fight.</h1>
<p style="font-size:16px;color:#8E8E93;max-width:560px;margin:16px auto 0;line-height:1.75;">Describe your legal situation. The Oracle searches real Indian court judgments and predicts your likely outcome — with specific law citations and your action roadmap.</p>
<div style="display:flex;gap:12px;justify-content:center;margin-top:20px;flex-wrap:wrap;">
<span style="background:rgba(168,85,247,0.12);border:1px solid rgba(168,85,247,0.3);color:#C084FC;font-size:11px;padding:4px 14px;border-radius:20px;letter-spacing:1px;">Powered by Indian Kanoon</span>
<span style="background:rgba(212,175,55,0.1);border:1px solid rgba(212,175,55,0.25);color:#D4AF37;font-size:11px;padding:4px 14px;border-radius:20px;letter-spacing:1px;">3 Crore+ Judgments</span>
<span style="background:rgba(34,197,94,0.1);border:1px solid rgba(34,197,94,0.25);color:#4ADE80;font-size:11px;padding:4px 14px;border-radius:20px;letter-spacing:1px;">IDA · CPA · RTI · BNS 2023</span>
</div>
</div>""",
        unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════
# CASE TYPE CARDS
# ════════════════════════════════════════════════════════════
CASE_TYPES = {
    "employment":  ("💼", "Employment",  "#0EA5E9"),
    "consumer":    ("🛒", "Consumer",    "#A855F7"),
    "property":    ("🏠", "Property",    "#22C55E"),
    "criminal":    ("⚖️", "Criminal",   "#EF4444"),
    "family":      ("👨‍👩‍👧", "Family",     "#F59E0B"),
    "rti":         ("📋", "RTI",        "#D4AF37"),
}

def render_case_type_selector():
    st.markdown(
"""<div style="padding:0 5% 8px;">
<div style="font-size:11px;color:#D4AF37;letter-spacing:4px;text-transform:uppercase;margin-bottom:18px;">Step 1 — What Type of Case Is This?</div>
</div>""",
        unsafe_allow_html=True)

    cols     = st.columns(6, gap="small")
    selected = st.session_state.get("oracle_case_type", "employment")

    for i, (key, (icon, label, color)) in enumerate(CASE_TYPES.items()):
        is_sel = selected == key
        border = f"2px solid {color}" if is_sel else "1px solid rgba(212,175,55,0.12)"
        bg     = f"rgba(20,20,35,0.95)" if is_sel else "rgba(10,10,18,0.6)"
        glow   = f"box-shadow:0 0 20px {color}33;" if is_sel else ""
        with cols[i]:
            st.markdown(
f"""<div style="background:{bg};border:{border};border-radius:14px;padding:16px 8px;text-align:center;{glow}transition:0.25s;min-height:80px;cursor:pointer;">
<div style="font-size:24px;margin-bottom:6px;">{icon}</div>
<div style="font-size:12px;font-weight:700;color:{'#F5F5F7' if is_sel else '#8E8E93'};">{label}</div>
</div>""",
                unsafe_allow_html=True)
            if st.button(label, key=f"ct_{key}", use_container_width=True):
                st.session_state["oracle_case_type"] = key
                st.rerun()


# ════════════════════════════════════════════════════════════
# ORACLE FORM
# ════════════════════════════════════════════════════════════
def render_form() -> dict | None:
    case_type = st.session_state.get("oracle_case_type", "employment")
    _, color, _ = list(CASE_TYPES.values())[list(CASE_TYPES.keys()).index(case_type)]
    icon, label, color = CASE_TYPES[case_type]

    st.markdown("<div style='height:24px;'></div>", unsafe_allow_html=True)
    st.markdown(
"""<div style="padding:0 5% 8px;">
<div style="font-size:11px;color:#D4AF37;letter-spacing:4px;text-transform:uppercase;margin-bottom:16px;">Step 2 — Describe Your Situation</div>
</div>""",
        unsafe_allow_html=True)

    left, gap, right = st.columns([5, 1, 5])

    with left:
        # Situation description — most important input
        st.markdown(
"<div style='font-size:12px;color:#A1A1AA;font-weight:600;letter-spacing:0.5px;margin-bottom:4px;'>Describe Your Situation in Detail *</div>",
            unsafe_allow_html=True)
        
        # Voice input option
        with st.expander("🎤 Or speak your situation", expanded=False):
            voice_lang = st.selectbox(
                "Speaking language",
                ["Hindi", "Telugu", "Tamil", "Kannada", "English"],
                key="oracle_voice_lang",
                label_visibility="collapsed"
            )
            voice_audio = st.audio_input("Record your situation", key="oracle_voice", label_visibility="collapsed")
            if voice_audio:
                if st.button("🎯 Transcribe", key="oracle_transcribe_btn"):
                    with st.spinner("Transcribing with Bhashini AI..."):
                        audio_bytes = voice_audio.read()
                        transcribed = transcribe_audio(audio_bytes, voice_lang)
                        if transcribed:
                            st.session_state["oracle_voice_text"] = transcribed
                            st.success("✅ Transcribed! Text added below.")
                        else:
                            st.error("Could not transcribe. Try speaking more clearly.")
        
        # Pre-fill with voice transcription if available
        default_desc = st.session_state.get("oracle_voice_text", "")
        description = st.text_area(
            "Situation",
            value=default_desc,
            placeholder=(
                "Example: My employer terminated me on 15th January 2026 without any notice "
                "or notice pay. I had worked there for 3 years as a software engineer. "
                "They have also not paid my last 2 months salary totaling Rs. 1,20,000. "
                "No misconduct was alleged — they said it was cost cutting."
            ),
            height=160,
            key="oracle_desc",
            label_visibility="collapsed",
        )
        st.markdown("<div style='margin-bottom:16px;'></div>", unsafe_allow_html=True)

        st.markdown(
"<div style='font-size:12px;color:#A1A1AA;font-weight:600;letter-spacing:0.5px;margin-bottom:4px;'>Which State Are You In?</div>",
            unsafe_allow_html=True)
        jurisdiction = st.selectbox(
            "State",
            options=[
                "Andhra Pradesh", "Telangana", "Karnataka", "Tamil Nadu", "Kerala",
                "Maharashtra", "Delhi", "Gujarat", "Rajasthan", "Uttar Pradesh",
                "West Bengal", "Madhya Pradesh", "Punjab", "Haryana", "Bihar",
                "Odisha", "Assam", "Jharkhand", "Uttarakhand", "Other / All India",
            ],
            key="oracle_state",
            label_visibility="collapsed",
        )
        st.markdown("<div style='margin-bottom:16px;'></div>", unsafe_allow_html=True)

        st.markdown(
"<div style='font-size:12px;color:#A1A1AA;font-weight:600;letter-spacing:0.5px;margin-bottom:4px;'>You Are The:</div>",
            unsafe_allow_html=True)
        user_side = st.selectbox(
            "Side",
            options=["Complainant (Victim / Affected Party)", "Respondent (Accused / Opposite Party)"],
            key="oracle_side",
            label_visibility="collapsed",
        )

    with right:
        st.markdown(
"<div style='font-size:12px;color:#A1A1AA;font-weight:600;letter-spacing:0.5px;margin-bottom:4px;'>Amount Involved (₹) — if applicable</div>",
            unsafe_allow_html=True)
        amount = st.text_input(
            "Amount",
            placeholder="e.g. 120000 (leave blank if not applicable)",
            key="oracle_amount",
            label_visibility="collapsed",
        )
        st.markdown("<div style='margin-bottom:16px;'></div>", unsafe_allow_html=True)

        st.markdown(
"<div style='font-size:12px;color:#A1A1AA;font-weight:600;letter-spacing:0.5px;margin-bottom:4px;'>Urgency Level</div>",
            unsafe_allow_html=True)
        urgency_map = {
            "Normal — I have time to do this properly": "normal",
            "Urgent — Need to act within 2 weeks":     "urgent",
            "Emergency — Immediate action required":   "emergency",
        }
        urgency_label = st.selectbox(
            "Urgency",
            options=list(urgency_map.keys()),
            key="oracle_urgency",
            label_visibility="collapsed",
        )
        st.markdown("<div style='margin-bottom:16px;'></div>", unsafe_allow_html=True)

        # Quick tips
        st.markdown(
f"""<div style="background:rgba(168,85,247,0.06);border:1px solid rgba(168,85,247,0.2);border-radius:12px;padding:16px;">
<div style="font-size:11px;color:#A855F7;font-weight:700;letter-spacing:2px;margin-bottom:10px;">TIPS FOR BETTER RESULTS</div>
<div style="font-size:12px;color:#8E8E93;line-height:1.8;">
✦ Include <strong style="color:#F5F5F7;">dates</strong> — when it happened<br>
✦ Include <strong style="color:#F5F5F7;">amounts</strong> — salary, dues, deposit<br>
✦ Mention <strong style="color:#F5F5F7;">duration</strong> — how long you've worked/lived there<br>
✦ Note any <strong style="color:#F5F5F7;">documents</strong> you have — contract, pay slips
</div>
</div>""",
            unsafe_allow_html=True)

    # ── Submit button ───────────────────────────────────────
    st.markdown("<div style='height:20px;'></div>", unsafe_allow_html=True)
    st.markdown(
"""<div style="margin:0 5% 16px;height:1px;background:linear-gradient(to right,rgba(168,85,247,0.4),rgba(212,175,55,0.2),transparent);"></div>""",
        unsafe_allow_html=True)

    bcol, _ = st.columns([3, 4])
    with bcol:
        clicked = st.button("🔮  Consult The Oracle", key="oracle_btn", use_container_width=True)

    if clicked:
        if not description or not description.strip():
            st.markdown(
"""<div style="margin:12px 5%;background:rgba(220,38,38,0.12);border:1px solid rgba(220,38,38,0.35);border-radius:12px;padding:14px 20px;">
<span style="color:#F87171;font-size:14px;font-weight:600;">⚠️ Please describe your situation first — the more detail, the more accurate the prediction.</span>
</div>""",
                unsafe_allow_html=True)
            return None

        return {
            "case_description": description.strip(),
            "case_type":        case_type,
            "jurisdiction":     jurisdiction,
            "user_side":        "complainant" if "Complainant" in user_side else "respondent",
            "amount_involved":  amount.strip(),
            "urgency":          urgency_map.get(urgency_label, "normal"),
        }

    return None


# ════════════════════════════════════════════════════════════
# PROCESSING — animated steps while API call runs
# ════════════════════════════════════════════════════════════
def run_oracle(form_data: dict) -> dict | None:
    result = None
    with st.status("🔮 The Oracle is consulting the archives...", expanded=True) as status:
        st.write("📖 Understanding your legal situation...")
        time.sleep(0.6)

        st.write("🔍 Searching Indian Kanoon — 3 crore+ judgments...")
        time.sleep(0.4)

        # ── Actual API call ─────────────────────────────────
        try:
            resp = requests.post(
                f"{API}/predict/outcome",
                json=form_data,
                timeout=45,     # IK + Groq can take up to 30s total
            )
            result = resp.json()
        except requests.exceptions.ConnectionError:
            st.error("Cannot connect to backend. Make sure the server is running.")
            return None
        except requests.exceptions.Timeout:
            st.error("Request timed out. Please try again.")
            return None
        except Exception as e:
            st.error(f"Error: {e}")
            return None

        st.write("⚖️ Analyzing relevant precedents and legal provisions...")
        time.sleep(0.5)

        st.write("📊 Calculating outcome probability and action plan...")
        time.sleep(0.4)

        ik_count = len(result.get("ik_cases", []))
        if ik_count > 0:
            st.write(f"✅ Found {ik_count} relevant Indian court judgments")
        else:
            st.write("✅ Analysis complete — using AI legal knowledge")
        time.sleep(0.3)

        status.update(label="🔮 The Oracle has spoken.", state="complete")

    return result


# ════════════════════════════════════════════════════════════
# VERDICT RENDERER — the main output screen
# ════════════════════════════════════════════════════════════
def render_verdict(result: dict):
    prob    = result.get("win_probability", 50)
    vlabel  = result.get("verdict_label", "Moderate Case")
    vsummary = result.get("verdict_summary", "")
    forum   = result.get("recommended_forum", "—")
    timeline = result.get("timeline", "—")
    strengths  = result.get("strengths", [])
    weaknesses = result.get("weaknesses", [])
    action_steps = result.get("action_steps", [])
    laws    = result.get("applicable_laws", [])
    ik_cases = result.get("ik_cases", [])
    settle  = result.get("settlement_advice")

    # Probability color
    if prob >= 68:   pcolor = "#22C55E"
    elif prob >= 45: pcolor = "#F59E0B"
    elif prob >= 25: pcolor = "#EF4444"
    else:            pcolor = "#A855F7"

    st.markdown("<div style='height:20px;'></div>", unsafe_allow_html=True)

    # ── Oracle header banner ────────────────────────────────
    st.markdown(
f"""<div style="margin:0 5% 28px;background:linear-gradient(135deg,rgba(10,8,20,0.97),rgba(15,10,30,0.97));border:1px solid rgba(168,85,247,0.3);border-radius:20px;padding:24px 32px;position:relative;overflow:hidden;">
<div style="position:absolute;top:0;right:0;width:300px;height:100%;background:radial-gradient(ellipse at 100% 50%,rgba(168,85,247,0.06),transparent 70%);pointer-events:none;"></div>
<div style="font-size:11px;color:#A855F7;letter-spacing:5px;text-transform:uppercase;margin-bottom:8px;">The Oracle Has Spoken</div>
<div style="font-size:20px;font-weight:700;color:#F5F5F7;font-family:'Playfair Display',serif;max-width:700px;line-height:1.5;">{vsummary}</div>
</div>""",
        unsafe_allow_html=True)

    # ── Row 1: Gauge + 3 stat chips ────────────────────────
    g_col, s_col = st.columns([3, 4], gap="large")

    with g_col:
        st.markdown(
"""<div style="padding:0 5%;margin-bottom:4px;">
<div style="font-size:11px;color:#D4AF37;letter-spacing:4px;text-transform:uppercase;margin-bottom:12px;">Win Probability</div>
</div>""",
            unsafe_allow_html=True)
        gauge_html = gauge_svg(prob)
        st.markdown(
f"<div style='padding:0 5%;text-align:center;'>{gauge_html}</div>",
            unsafe_allow_html=True)

    with s_col:
        st.markdown(
"""<div style="font-size:11px;color:#D4AF37;letter-spacing:4px;text-transform:uppercase;margin-bottom:16px;margin-top:4px;">Key Numbers</div>""",
            unsafe_allow_html=True)
        st.markdown(
f"""<div style="display:flex;flex-direction:column;gap:12px;">
<div style="background:rgba(15,15,25,0.9);border:1px solid rgba(212,175,55,0.2);border-radius:14px;padding:14px 20px;display:flex;justify-content:space-between;align-items:center;">
<span style="font-size:12px;color:#8E8E93;letter-spacing:1px;">RECOMMENDED FORUM</span>
<span style="font-size:13px;font-weight:700;color:#D4AF37;text-align:right;max-width:220px;">{forum}</span>
</div>
<div style="background:rgba(15,15,25,0.9);border:1px solid rgba(212,175,55,0.2);border-radius:14px;padding:14px 20px;display:flex;justify-content:space-between;align-items:center;">
<span style="font-size:12px;color:#8E8E93;letter-spacing:1px;">EXPECTED TIMELINE</span>
<span style="font-size:13px;font-weight:700;color:#F5F5F7;">{timeline}</span>
</div>
<div style="background:rgba(15,15,25,0.9);border:1px solid rgba({pcolor.lstrip('#')[:2]},{''.join(hex(int(pcolor.lstrip('#')[i:i+2],16)) for i in (0,2,4) if False) or f'{int(pcolor[1:3],16)},{int(pcolor[3:5],16)},{int(pcolor[5:7],16)}'},{0.2});border-radius:14px;padding:14px 20px;display:flex;justify-content:space-between;align-items:center;">
<span style="font-size:12px;color:#8E8E93;letter-spacing:1px;">VERDICT</span>
<span style="font-size:13px;font-weight:700;color:{pcolor};">{vlabel}</span>
</div>
</div>""",
            unsafe_allow_html=True)

    st.markdown("<div style='height:24px;'></div>", unsafe_allow_html=True)

    # ── Settlement advice ───────────────────────────────────
    if settle:
        st.markdown(
f"""<div style="margin:0 5% 20px;background:rgba(212,175,55,0.07);border:1px solid rgba(212,175,55,0.25);border-left:4px solid #D4AF37;border-radius:0 12px 12px 0;padding:14px 20px;">
<span style="font-size:12px;color:#D4AF37;font-weight:700;letter-spacing:1px;">💡 SETTLEMENT OPTION &nbsp;</span>
<span style="font-size:13px;color:#F5F5F7;">{settle}</span>
</div>""",
            unsafe_allow_html=True)

    # ── Strengths + Weaknesses ──────────────────────────────
    sw_left, sw_gap, sw_right = st.columns([5, 1, 5])

    with sw_left:
        items_html = "".join(
            f'<div style="display:flex;gap:10px;margin-bottom:10px;align-items:flex-start;">'
            f'<span style="color:#22C55E;font-size:16px;flex-shrink:0;">✅</span>'
            f'<span style="font-size:13px;color:#E2E8F0;line-height:1.6;">{s}</span></div>'
            for s in strengths
        ) if strengths else '<div style="color:#8E8E93;font-size:13px;">No strengths identified.</div>'

        st.markdown(
f"""<div style="background:rgba(10,22,10,0.85);border:1px solid rgba(34,197,94,0.25);border-radius:16px;padding:20px 22px;height:100%;">
<div style="font-size:11px;color:#22C55E;letter-spacing:3px;font-weight:700;margin-bottom:14px;">YOUR STRONGEST ARGUMENTS</div>
{items_html}
</div>""",
            unsafe_allow_html=True)

    with sw_right:
        items_html = "".join(
            f'<div style="display:flex;gap:10px;margin-bottom:10px;align-items:flex-start;">'
            f'<span style="color:#F59E0B;font-size:16px;flex-shrink:0;">⚠️</span>'
            f'<span style="font-size:13px;color:#E2E8F0;line-height:1.6;">{w}</span></div>'
            for w in weaknesses
        ) if weaknesses else '<div style="color:#8E8E93;font-size:13px;">No major risks identified.</div>'

        st.markdown(
f"""<div style="background:rgba(22,14,5,0.85);border:1px solid rgba(245,158,11,0.25);border-radius:16px;padding:20px 22px;height:100%;">
<div style="font-size:11px;color:#F59E0B;letter-spacing:3px;font-weight:700;margin-bottom:14px;">RISKS &amp; COUNTER-ARGUMENTS</div>
{items_html}
</div>""",
            unsafe_allow_html=True)

    st.markdown("<div style='height:24px;'></div>", unsafe_allow_html=True)

    # ── Action Roadmap ──────────────────────────────────────
    st.markdown(
"""<div style="padding:0 5% 16px;">
<div style="font-size:11px;color:#D4AF37;letter-spacing:4px;text-transform:uppercase;">Your Action Roadmap</div>
</div>""",
        unsafe_allow_html=True)

    PAGE_LINKS = {
        "legal_notice": ("📜", "Generate Notice", "/4_generator"),
        "chat":         ("⚖️", "Ask The Advocate", "/1_chat"),
    }

    steps_html = ""
    for i, step in enumerate(action_steps):
        tf     = step.get("timeframe", f"Step {i+1}")
        action = step.get("action", "")
        page   = step.get("page")
        link_html = ""
        if page and page in PAGE_LINKS:
            p_icon, p_label, p_href = PAGE_LINKS[page]
            link_html = (
                f'<a href="{p_href}" target="_self" style="display:inline-block;margin-top:8px;'
                f'background:rgba(212,175,55,0.1);border:1px solid rgba(212,175,55,0.3);'
                f'color:#D4AF37;font-size:11px;padding:4px 12px;border-radius:20px;'
                f'text-decoration:none;letter-spacing:0.5px;">{p_icon} {p_label} →</a>'
            )
        is_last = i == len(action_steps) - 1
        connector = "" if is_last else (
            '<div style="width:2px;height:20px;background:rgba(212,175,55,0.2);'
            'margin:4px 0 4px 22px;"></div>'
        )
        steps_html += (
            f'<div style="display:flex;gap:16px;align-items:flex-start;">'
            f'<div style="width:44px;height:44px;background:rgba(212,175,55,0.1);'
            f'border:1px solid rgba(212,175,55,0.35);border-radius:50%;display:flex;'
            f'align-items:center;justify-content:center;flex-shrink:0;">'
            f'<span style="font-size:13px;font-weight:800;color:#D4AF37;">{i+1}</span></div>'
            f'<div style="flex:1;padding-top:4px;">'
            f'<div style="font-size:11px;color:#D4AF37;letter-spacing:1px;margin-bottom:3px;">{tf.upper()}</div>'
            f'<div style="font-size:14px;color:#F5F5F7;line-height:1.6;">{action}</div>'
            f'{link_html}</div></div>'
            f'{connector}'
        )

    st.markdown(
f"""<div style="margin:0 5%;background:rgba(12,12,22,0.9);border:1px solid rgba(212,175,55,0.15);border-radius:18px;padding:24px 28px;">
{steps_html if steps_html else '<div style="color:#8E8E93;font-size:13px;">No action steps available.</div>'}
</div>""",
        unsafe_allow_html=True)

    st.markdown("<div style='height:24px;'></div>", unsafe_allow_html=True)

    # ── Indian Kanoon Cases ─────────────────────────────────
    st.markdown(
"""<div style="padding:0 5% 8px;display:flex;align-items:center;justify-content:space-between;">
<div style="font-size:11px;color:#D4AF37;letter-spacing:4px;text-transform:uppercase;">Similar Cases from Indian Kanoon</div>
<a href="https://indiankanoon.org" target="_blank" style="text-decoration:none;">
<span style="font-size:10px;color:#8E8E93;border:1px solid rgba(255,255,255,0.1);padding:3px 10px;border-radius:20px;">Powered by IndianKanoon ↗</span>
</a>
</div>""",
        unsafe_allow_html=True)

    if ik_cases:
        cases_html = ""
        for case in ik_cases[:4]:
            title    = case.get("title", "Judgment")[:80]
            court    = case.get("court", "Court")[:50]
            cdate    = case.get("date", "")[:10]
            snippet  = case.get("snippet", "")[:180]
            fragment = case.get("fragment", "")[:200]
            url      = case.get("url", "https://indiankanoon.org")
            excerpt  = fragment if fragment else snippet
            year     = cdate[:4] if cdate else ""

            cases_html += (
                f'<div style="background:rgba(10,10,20,0.9);border:1px solid rgba(255,255,255,0.08);'
                f'border-radius:14px;padding:16px 20px;margin-bottom:12px;">'
                f'<div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:8px;">'
                f'<div style="flex:1;">'
                f'<div style="font-size:14px;font-weight:700;color:#F5F5F7;line-height:1.4;margin-bottom:4px;">{title}</div>'
                f'<div style="font-size:11px;color:#8E8E93;">{court}'
                f'{"&nbsp;·&nbsp;" + year if year else ""}</div>'
                f'</div>'
                f'<a href="{url}" target="_blank" style="text-decoration:none;flex-shrink:0;margin-left:16px;">'
                f'<span style="background:rgba(212,175,55,0.1);border:1px solid rgba(212,175,55,0.3);'
                f'color:#D4AF37;font-size:11px;padding:5px 12px;border-radius:20px;white-space:nowrap;">'
                f'Read Judgment ↗</span></a>'
                f'</div>'
                f'{"<div style=&quot;font-size:12px;color:#94A3B8;line-height:1.7;font-style:italic;border-left:2px solid rgba(212,175,55,0.2);padding-left:12px;&quot;>&quot;" + excerpt + "...&quot;</div>" if excerpt else ""}'
                f'</div>'
            )
        st.markdown(
f'<div style="margin:0 5%;">{cases_html}</div>',
            unsafe_allow_html=True)
    else:
        st.markdown(
"""<div style="margin:0 5%;background:rgba(212,175,55,0.04);border:1px solid rgba(212,175,55,0.15);border-radius:14px;padding:20px 24px;">
<div style="font-size:12px;color:#D4AF37;font-weight:700;letter-spacing:2px;margin-bottom:6px;">⚖️ AI LEGAL KNOWLEDGE BASE</div>
<div style="font-size:13px;color:#8E8E93;line-height:1.7;">Case law is being retrieved. The analysis above is based on established Indian legal principles and precedents from the AI's knowledge of Indian court judgments.</div>
<a href="https://indiankanoon.org" target="_blank" style="display:inline-block;margin-top:10px;background:rgba(212,175,55,0.1);border:1px solid rgba(212,175,55,0.3);color:#D4AF37;font-size:12px;padding:6px 16px;border-radius:20px;text-decoration:none;letter-spacing:0.5px;">Search on IndianKanoon.org ↗</a>
</div>""",
            unsafe_allow_html=True)

    st.markdown("<div style='height:24px;'></div>", unsafe_allow_html=True)

    # ── Applicable Laws — with full expanded names ───────────
    if laws:
        # Expand short codes to full law names
        LAW_EXPAND = {
            "IDA 1947 Section 25F":  "Industrial Disputes Act, 1947 – Section 25F",
            "IDA 1947 Section 25G":  "Industrial Disputes Act, 1947 – Section 25G",
            "IDA 1947 Section 25H":  "Industrial Disputes Act, 1947 – Section 25H",
            "IDA 1947 Section 2A":   "Industrial Disputes Act, 1947 – Section 2A",
            "IDA 1947":              "Industrial Disputes Act, 1947",
            "IDA Section":           "Industrial Disputes Act, 1947 –",
            "ICA Section 27":        "Indian Contract Act, 1872 – Section 27",
            "ICA Section 73":        "Indian Contract Act, 1872 – Section 73",
            "ICA Section 74":        "Indian Contract Act, 1872 – Section 74",
            "ICA 1872":              "Indian Contract Act, 1872",
            "CPA 2019":              "Consumer Protection Act, 2019",
            "CPA Section":           "Consumer Protection Act, 2019 –",
            "TPA 1882":              "Transfer of Property Act, 1882",
            "TPA Section":           "Transfer of Property Act, 1882 –",
            "RTI Act":               "Right to Information Act, 2005",
            "PWA 1936":              "Payment of Wages Act, 1936",
            "HMA 1955":              "Hindu Marriage Act, 1955",
            "IPC Section":           "Indian Penal Code, 1860 –",
            "BNS Section":           "Bharatiya Nyaya Sanhita, 2023 –",
            "PWDVA":                 "Protection of Women from Domestic Violence Act, 2005",
        }

        def expand_law(raw):
            for code, full in sorted(LAW_EXPAND.items(), key=lambda x: -len(x[0])):
                if code in raw:
                    return raw.replace(code, full)
            return raw

        expanded_laws = [expand_law(law) for law in laws]

        st.markdown(
"""<div style="padding:0 5% 12px;">
<div style="font-size:11px;color:#D4AF37;letter-spacing:4px;text-transform:uppercase;margin-bottom:12px;">Applicable Laws &amp; Provisions</div>
</div>""",
            unsafe_allow_html=True)
        chips = "".join(
            f'<span style="display:inline-block;background:rgba(212,175,55,0.08);'
            f'border:1px solid rgba(212,175,55,0.22);color:#D4AF37;font-size:12px;'
            f'padding:6px 16px;border-radius:20px;margin:4px 4px 4px 0;">{law}</span>'
            for law in expanded_laws
        )
        st.markdown(
f'<div style="padding:0 5%;">{chips}</div>',
            unsafe_allow_html=True)
        st.markdown("<div style='height:20px;'></div>", unsafe_allow_html=True)

    # ── CTA Buttons ─────────────────────────────────────────
    st.markdown(
"""<div style="margin:0 5% 20px;height:1px;background:linear-gradient(to right,rgba(212,175,55,0.3),transparent);"></div>""",
        unsafe_allow_html=True)

    c1, c2, c3, _ = st.columns([2, 2, 2, 1])
    with c1:
        if st.button("📜  Generate Legal Notice", use_container_width=True, key="to_gen"):
            st.switch_page("pages/4_generator.py")
    with c2:
        if st.button("⚖️  Ask The Advocate", use_container_width=True, key="to_chat"):
            st.switch_page("pages/1_chat.py")
    with c3:
        if st.button("🔄  New Prediction", use_container_width=True, key="new_pred"):
            for k in ["oracle_result", "oracle_form", "oracle_processing"]:
                st.session_state.pop(k, None)
            st.rerun()

    # ── Disclaimer ──────────────────────────────────────────
    st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)
    st.markdown(
"""<div style="margin:0 5%;background:rgba(168,85,247,0.05);border:1px solid rgba(168,85,247,0.15);border-radius:12px;padding:14px 20px;text-align:center;">
<span style="font-size:12px;color:#8E8E93;">🔮 <strong style="color:#C084FC;">Disclaimer:</strong> This is an AI-generated estimate based on similar Indian court cases. Actual outcomes depend on specific facts, evidence, and the presiding judge. <strong style="color:#F5F5F7;">Always consult a licensed advocate before taking legal action.</strong> Verify case citations at <a href="https://indiankanoon.org" target="_blank" style="color:#D4AF37;">indiankanoon.org</a>.</span>
</div>""",
        unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════
# SIDEBAR
# ════════════════════════════════════════════════════════════
def render_sidebar():
    with st.sidebar:
        if LOGO:
            st.image(base64.b64decode(LOGO), width=56)
        st.markdown(
"<div style=\"font-family:'Playfair Display',serif;font-size:20px;color:#D4AF37;margin-bottom:2px;\">Nyaya-Setu</div>",
            unsafe_allow_html=True)
        st.markdown(
"<div style='font-size:11px;color:#8E8E93;letter-spacing:2px;margin-bottom:24px;'>THE ORACLE</div>",
            unsafe_allow_html=True)
        st.markdown(
"<div style='font-size:11px;color:#D4AF37;letter-spacing:3px;text-transform:uppercase;margin-bottom:12px;'>Case Types</div>",
            unsafe_allow_html=True)
        for key, (icon, label, color) in CASE_TYPES.items():
            is_sel = st.session_state.get("oracle_case_type") == key
            st.markdown(
f"<div style='padding:7px 12px;border-radius:8px;margin-bottom:3px;background:{'rgba(20,20,35,0.9)' if is_sel else 'transparent'};border:{'1px solid '+color+'44' if is_sel else '1px solid transparent'};'><span style='font-size:14px;'>{icon}</span><span style='font-size:12px;color:{'#F5F5F7' if is_sel else '#8E8E93'};margin-left:8px;'>{label}</span></div>",
                unsafe_allow_html=True)
        st.markdown("<div style='height:20px;'></div>", unsafe_allow_html=True)
        st.markdown(
"<div style='font-size:11px;color:#D4AF37;letter-spacing:3px;text-transform:uppercase;margin-bottom:12px;'>Navigate</div>",
            unsafe_allow_html=True)
        for icon, label, href in [
            ("🏠","Home","/"), ("⚖️","Virtual Advocate","/1_chat"),
            ("📄","Witness Stand","/2_upload"), ("🔍","Case Archives","/3_case_search"),
            ("📜","Document Forge","/4_generator"), ("📊","Chamber Records","/6_dashboard"),
        ]:
            st.markdown(
f"<a href='{href}' target='_self' style='text-decoration:none;display:block;padding:7px 12px;border-radius:8px;margin-bottom:3px;color:#8E8E93;font-size:12px;'>{icon} {label}</a>",
                unsafe_allow_html=True)
        st.markdown("<div style='height:20px;'></div>", unsafe_allow_html=True)
        st.markdown(
"<div style='font-size:11px;color:#D4AF37;letter-spacing:3px;text-transform:uppercase;margin-bottom:10px;'>Helplines</div>",
            unsafe_allow_html=True)
        for name, num in [("Women","1091"),("Police","100"),("Legal Aid","15100"),("Consumer","1800-11-4000")]:
            st.markdown(
f"<div style='display:flex;justify-content:space-between;padding:5px 8px;margin-bottom:4px;'><span style='font-size:11px;color:#8E8E93;'>{name}</span><span style='font-size:12px;color:#D4AF37;font-weight:700;'>{num}</span></div>",
                unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════
# FOOTER
# ════════════════════════════════════════════════════════════
def render_footer():
    st.markdown("<div style='height:48px;'></div>", unsafe_allow_html=True)
    st.markdown(
"""<div style="text-align:center;padding:20px;border-top:1px solid rgba(212,175,55,0.1);">
<span style="font-size:11px;color:#333;letter-spacing:2px;">NYAYA-SETU · THE ORACLE · INDIA · 2026 &nbsp;·&nbsp; </span>
<a href="https://indiankanoon.org" target="_blank" style="font-size:11px;color:#555;letter-spacing:2px;text-decoration:none;">POWERED BY INDIANKANOON</a>
</div>""",
        unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════
# MAIN
# ════════════════════════════════════════════════════════════
inject_css()
render_sidebar()
render_header()

# Initialise default case type
if "oracle_case_type" not in st.session_state:
    st.session_state["oracle_case_type"] = "employment"

# ── RESULT SCREEN ───────────────────────────────────────────
if st.session_state.get("oracle_result"):
    render_verdict(st.session_state["oracle_result"])
    render_footer()

# ── PROCESSING STATE ─────────────────────────────────────────
elif st.session_state.get("oracle_processing"):
    form_data = st.session_state.get("oracle_form", {})
    result    = run_oracle(form_data)
    if result:
        st.session_state["oracle_result"]     = result
        st.session_state["oracle_processing"] = False
        st.rerun()
    else:
        st.session_state["oracle_processing"] = False

# ── FORM SCREEN ───────────────────────────────────────────────
else:
    render_case_type_selector()
    form_data = render_form()
    if form_data:
        st.session_state["oracle_form"]       = form_data
        st.session_state["oracle_processing"] = True
        st.rerun()
    render_footer()