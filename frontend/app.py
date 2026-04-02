import streamlit as st
import base64, os

st.set_page_config(
    page_title="Nyaya-Setu | न्याय सेतु",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ════════════════════════════════════════════════════════════
# ASSETS — load logo and background image
# ════════════════════════════════════════════════════════════
LOGO_PATH = os.path.join(os.path.dirname(__file__), "nyayasetu_logo.jpg")
BG_PATH   = os.path.join(os.path.dirname(__file__), "nyaya_setu_bridge.png")

@st.cache_data
def load_asset(path: str) -> str | None:
    """Load file as base64 string. Cached so it only reads disk once."""
    try:
        if not os.path.exists(path):
            return None
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    except (OSError, IOError):
        return None

LOGO = load_asset(LOGO_PATH)
BG   = load_asset(BG_PATH)


# ════════════════════════════════════════════════════════════
# DID YOU KNOW — 8 powerful laws every Indian should know
# Each card has: law, quote, plain meaning in simple words
# ════════════════════════════════════════════════════════════
DID_YOU_KNOW = [
    {
        "law":     "Article 21 — Constitution of India",
        "quote":   "No person shall be deprived of life or personal liberty except according to procedure established by law.",
        "meaning": "No one — not your employer, your landlord, or even the police — can take away your freedom without following the proper legal process. If they do, you can challenge it in any High Court in India today.",
        "tag":     "Fundamental Right",
        "color":   "#D4AF37",
        "num":     "1/8",
    },
    {
        "law":     "Section 25F — Industrial Disputes Act, 1947",
        "quote":   "No worker shall be removed from service unless they have been given one month's written notice AND paid 15 days' wages for every year they worked.",
        "meaning": "Your company CANNOT fire you without giving one month's notice or paying one month's salary. If they fired you without that, it is illegal. You can go to the Labour Court and get your job and back salary restored.",
        "tag":     "Employment Right",
        "color":   "#0EA5E9",
        "num":     "2/8",
    },
    {
        "law":     "Section 106 — Transfer of Property Act, 1882",
        "quote":   "A monthly tenancy can only be ended by giving 15 days' written notice to the other party.",
        "meaning": "Your landlord CANNOT throw you out without warning. They must give 15 days of written notice first. If they try to evict you without notice, it is illegal. You can go to court and stay in your home.",
        "tag":     "Tenant Right",
        "color":   "#22C55E",
        "num":     "3/8",
    },
    {
        "law":     "Section 6 — Right to Information Act, 2005",
        "quote":   "Any person may request information from a Public Information Officer. The officer cannot ask why you want the information.",
        "meaning": "You can ask for ANY information from ANY government office — hospital, police, municipality, ministry — for just ₹10. They must reply within 30 days. You do not need to explain why you are asking. This is YOUR right.",
        "tag":     "Citizen Right",
        "color":   "#D4AF37",
        "num":     "4/8",
    },
    {
        "law":     "Section 2(7) — Consumer Protection Act, 2019",
        "quote":   "Any person who buys goods or services has the right to file a complaint for deficiency in service or defective products.",
        "meaning": "If a company cheats you, sells you a broken product, or refuses your refund — you can file a complaint in the Consumer Forum in your own city. You do NOT need a lawyer. The fee is as low as ₹200. Companies fear consumer forums.",
        "tag":     "Consumer Right",
        "color":   "#A855F7",
        "num":     "5/8",
    },
    {
        "law":     "Section 27 — Indian Contract Act, 1872",
        "quote":   "Every agreement that stops someone from practising their profession or doing their business is completely void.",
        "meaning": "If your job contract says 'you cannot join a competitor for 2 years after leaving' — that line means NOTHING in India. It is legally void. You can join any company the very next day after resigning. Non-compete clauses have no legal power here.",
        "tag":     "Contract Right",
        "color":   "#FF7722",
        "num":     "6/8",
    },
    {
        "law":     "Section 74 — Bharatiya Nyaya Sanhita, 2023",
        "quote":   "Whoever assaults a woman with the intent to outrage her modesty shall be punished with imprisonment of not less than one year.",
        "meaning": "Any physical harassment of a woman at work, on the street, or in public is a criminal offence with at least 1 year in jail. The police MUST file your FIR — they cannot refuse. If they refuse, you can escalate to the Superintendent of Police directly.",
        "tag":     "Women's Right",
        "color":   "#EF4444",
        "num":     "7/8",
    },
    {
        "law":     "Article 39A — Constitution of India",
        "quote":   "The State shall provide free legal aid to ensure justice is not denied to any citizen because of poverty or any other disability.",
        "meaning": "FREE legal help is your constitutional right. If you cannot afford a lawyer, the government MUST give you one for free. Call 15100 — the National Legal Aid helpline. This works for criminal cases, family matters, and much more.",
        "tag":     "Free Legal Aid",
        "color":   "#22C55E",
        "num":     "8/8",
    },
]


# ════════════════════════════════════════════════════════════
# FEATURES — all 7 tools
# ════════════════════════════════════════════════════════════
FEATURES = [
    {
        "icon":    "📄",
        "title":   "The Witness Stand",
        "tagline": "Scan Your Contract",
        "desc":    "Upload any employment or rental contract. We read every line, score the risk out of 10, and show you exactly what is dangerous — in simple words.",
        "color":   "#D4AF37",
        "btn":     "Scan My Document",
        "page":    "pages/2_upload.py",
        "badge":   "Most Used",
    },
    {
        "icon":    "⚖️",
        "title":   "Virtual Advocate",
        "tagline": "Ask a Legal Question",
        "desc":    "Ask anything in Hindi, Telugu, Tamil, Kannada, or English. Get answers from real Indian law — not guesses. Available 24 hours a day, completely free.",
        "color":   "#FF7722",
        "btn":     "Ask a Question",
        "page":    "pages/1_chat.py",
        "badge":   "24/7 Free",
    },
    {
        "icon":    "🔍",
        "title":   "Case Archives",
        "tagline": "Real Court Judgments",
        "desc":    "Search 3 crore real court judgments in plain words. Type your problem — 'landlord won't return deposit' — and see how courts have ruled on the exact same issue.",
        "color":   "#22C55E",
        "btn":     "Search Cases",
        "page":    "pages/3_case_search.py",
        "badge":   "3 Crore+ Cases",
    },
    {
        "icon":    "📜",
        "title":   "Document Forge",
        "tagline": "Create Legal Documents",
        "desc":    "Generate ready-to-use RTI applications, legal notices, rental agreements, consumer complaints, and employment grievance letters. Fill a form, download in seconds.",
        "color":   "#A855F7",
        "btn":     "Create a Document",
        "page":    "pages/4_generator.py",
        "badge":   "5 Templates",
    },
    {
        "icon":    "🔮",
        "title":   "The Oracle",
        "tagline": "Will You Win?",
        "desc":    "Describe your legal situation. We search real court cases and tell you your win probability, which court to go to, how long it will take, and your step-by-step action plan.",
        "color":   "#0EA5E9",
        "btn":     "Check My Chances",
        "page":    "pages/5_predict.py",
        "badge":   "AI + Real Cases",
    },
    {
        "icon":    "📊",
        "title":   "Chamber Records",
        "tagline": "Your Legal History",
        "desc":    "Every document you have ever uploaded — risk scores, clause problems, top concerns — saved safely so you can come back any time and review your legal record.",
        "color":   "#F59E0B",
        "btn":     "View My Records",
        "page":    "pages/6_dashboard.py",
        "badge":   "Saved History",
    },
    {
        "icon":    "🏛️",
        "title":   "Free Legal Aid",
        "tagline": "Your Constitutional Right",
        "desc":    "Under Article 39A, every Indian citizen is entitled to free legal help. Call 15100 to find the nearest Legal Services Authority in your city. This is your right — use it.",
        "color":   "#EF4444",
        "btn":     "Find Free Help Near Me",
        "page":    None,
        "link":    "https://www.google.com/maps/search/District+Legal+Services+Authority",
        "badge":   "Free · Always",
    },
]

LAWS = [
    ("IDA 1947",  "Industrial Disputes Act"),
    ("ICA 1872",  "Indian Contract Act"),
    ("RTI 2005",  "Right to Information"),
    ("CPA 2019",  "Consumer Protection"),
    ("TPA 1882",  "Transfer of Property"),
    ("BNS 2023",  "Bharatiya Nyaya Sanhita"),
    ("BNSS 2023", "Nagarik Suraksha Sanhita"),
    ("PWA 1936",  "Payment of Wages"),
    ("HMA 1955",  "Hindu Marriage Act"),
    ("PWDVA 2005","Domestic Violence Act"),
    ("FA 1948",   "Factories Act"),
    ("MA 1948",   "Minimum Wages Act"),
    ("CrPC 1973", "Criminal Procedure Code"),
    ("IEA 1872",  "Indian Evidence Act"),
]


# ════════════════════════════════════════════════════════════
# HELPER
# ════════════════════════════════════════════════════════════
def _rgb(h: str) -> str:
    h = h.lstrip("#")
    try: return f"{int(h[0:2],16)},{int(h[2:4],16)},{int(h[4:6],16)}"
    except: return "212,175,55"


# ════════════════════════════════════════════════════════════
# CSS + JS — Advanced transitions, particles, counter, ticker
# ════════════════════════════════════════════════════════════
def inject_css():
    bg_rule = (
        f"background-image:linear-gradient(rgba(2,2,6,0.85),rgba(2,2,6,0.97)),"
        f"url('data:image/png;base64,{BG}');"
        f"background-size:cover;background-position:center;background-attachment:fixed;"
    ) if BG else "background:#020206;"

    st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Playfair+Display:ital,wght@0,400;0,700;1,400;1,700&display=swap');

html,body,[data-testid="stAppViewContainer"]{{
{bg_rule}
color:#F0EEE8;font-family:'Plus Jakarta Sans',sans-serif;
}}
[data-testid="block-container"]{{padding:0!important;max-width:100%!important;}}
#MainMenu,header,footer{{display:none!important;}}
.stDeployButton{{display:none!important;}}
[data-testid="stSidebarNav"],[data-testid="stSidebarNavItems"],
nav[data-testid="stSidebarNav"],[data-testid="stSidebarContent"] ul,
[data-testid="stSidebarContent"] nav{{display:none!important;}}
::-webkit-scrollbar{{width:4px;}}
::-webkit-scrollbar-track{{background:#020206;}}
::-webkit-scrollbar-thumb{{background:#D4AF37;border-radius:4px;}}

/* ── BUTTONS ── */
.stButton>button{{
background:transparent!important;
border:1px solid rgba(212,175,55,0.6)!important;
color:#D4AF37!important;
border-radius:50px!important;
padding:11px 28px!important;
font-weight:600!important;
letter-spacing:1px!important;
font-size:13px!important;
width:100%!important;
font-family:'Plus Jakarta Sans',sans-serif!important;
transition:all 0.35s cubic-bezier(0.4,0,0.2,1)!important;
position:relative!important;
overflow:hidden!important;
}}
.stButton>button::before{{
content:'';
position:absolute;
inset:0;
background:linear-gradient(135deg,#D4AF37,#FF7722);
opacity:0;
transition:opacity 0.35s ease;
}}
.stButton>button:hover{{
background:transparent!important;
color:#000!important;
border-color:transparent!important;
transform:translateY(-3px)!important;
box-shadow:0 8px 32px rgba(212,175,55,0.35)!important;
}}
.stButton>button:hover::before{{opacity:1!important;}}
.stButton>button span{{position:relative;z-index:1;}}
.stLinkButton>a{{
background:transparent!important;
border:1px solid rgba(239,68,68,0.5)!important;
color:#EF4444!important;
border-radius:50px!important;
padding:11px 28px!important;
font-weight:600!important;
letter-spacing:1px!important;
font-size:13px!important;
width:100%!important;
display:block!important;
text-align:center!important;
transition:all 0.35s ease!important;
}}
.stLinkButton>a:hover{{
background:#EF4444!important;color:#000!important;
transform:translateY(-3px)!important;
box-shadow:0 8px 32px rgba(239,68,68,0.3)!important;
}}

/* ── KEYFRAMES ── */
@keyframes tricolor{{0%{{background-position:0% 50%;}}100%{{background-position:200% 50%;}}}}
@keyframes floatup{{0%{{transform:translateY(0) rotate(0deg);opacity:0.6;}}100%{{transform:translateY(-120vh) rotate(720deg);opacity:0;}}}}
@keyframes fadein{{from{{opacity:0;transform:translateY(20px);}}to{{opacity:1;transform:translateY(0);}}}}
@keyframes slideInLeft{{from{{opacity:0;transform:translateX(-30px);}}to{{opacity:1;transform:translateX(0);}}}}
@keyframes slideInRight{{from{{opacity:0;transform:translateX(30px);}}to{{opacity:1;transform:translateX(0);}}}}
@keyframes scalein{{from{{opacity:0;transform:scale(0.92);}}to{{opacity:1;transform:scale(1);}}}}
@keyframes glow{{0%,100%{{text-shadow:0 0 30px rgba(212,175,55,0.3);}}50%{{text-shadow:0 0 60px rgba(212,175,55,0.7),0 0 100px rgba(212,175,55,0.3);}}}}
@keyframes pulse{{0%,100%{{transform:scale(1);}}50%{{transform:scale(1.03);}}}}
@keyframes tickerScroll{{0%{{transform:translateX(0);}}100%{{transform:translateX(-50%);}}}}
@keyframes countUp{{from{{opacity:0;transform:translateY(10px);}}to{{opacity:1;transform:translateY(0);}}}}
@keyframes borderGlow{{0%,100%{{border-color:rgba(212,175,55,0.2);}}50%{{border-color:rgba(212,175,55,0.6);}}}}
@keyframes dykFadeIn{{from{{opacity:0;transform:translateX(40px);}}to{{opacity:1;transform:translateX(0);}}}}
@keyframes dykFadeOut{{from{{opacity:1;transform:translateX(0);}}to{{opacity:0;transform:translateX(-40px);}}}}

/* ── PARTICLES ── */
.particle{{
position:fixed;pointer-events:none;z-index:0;
border-radius:50%;background:rgba(212,175,55,0.15);
animation:floatup linear infinite;
}}

/* ── CARD HOVER ── */
.feat-card{{
transition:all 0.4s cubic-bezier(0.4,0,0.2,1)!important;
}}
.feat-card:hover{{
transform:translateY(-8px) scale(1.02)!important;
}}

/* ── HUD STAT COUNTER ── */
.hud-val{{
animation:countUp 0.8s ease both;
}}

/* ── DYK TRANSITION ── */
.dyk-slide{{animation:dykFadeIn 0.5s cubic-bezier(0.4,0,0.2,1) both;}}

/* ── PROGRESS DOT ── */
.dyk-dot{{
display:inline-block;width:8px;height:8px;border-radius:50%;
background:rgba(212,175,55,0.25);margin:0 4px;
transition:all 0.3s ease;cursor:pointer;
}}
.dyk-dot.active{{
background:#D4AF37;width:24px;border-radius:4px;
}}

/* ══════════════════════════════════════════════════════════
   MOBILE RESPONSIVE STYLES
   ══════════════════════════════════════════════════════════ */
@media (max-width: 768px) {{
    /* Global mobile adjustments */
    html, body {{
        font-size: 14px !important;
    }}
    
    /* Hero section */
    h1 {{
        font-size: 32px !important;
        line-height: 1.2 !important;
    }}
    
    /* Feature cards - single column on mobile */
    .feat-card {{
        margin: 12px 8px !important;
        padding: 20px 16px !important;
    }}
    
    /* Buttons - full width on mobile */
    .stButton > button {{
        padding: 14px 20px !important;
        font-size: 14px !important;
        min-height: 48px !important; /* Touch-friendly */
    }}
    
    /* Audio input - larger touch target */
    [data-testid="stAudioInput"] {{
        transform: scale(1.1) !important;
    }}
    
    /* Chat input */
    [data-testid="stChatInput"] {{
        border-radius: 25px !important;
        padding: 8px !important;
    }}
    
    /* File uploader */
    [data-testid="stFileUploader"] {{
        padding: 16px !important;
    }}
    
    /* Selectbox */
    [data-testid="stSelectbox"] > div > div {{
        min-height: 44px !important;
    }}
    
    /* Text area */
    [data-testid="stTextArea"] textarea {{
        min-height: 120px !important;
        font-size: 16px !important; /* Prevents zoom on iOS */
    }}
    
    /* Text input */
    [data-testid="stTextInput"] input {{
        min-height: 44px !important;
        font-size: 16px !important;
    }}
    
    /* Expander */
    [data-testid="stExpander"] {{
        border-radius: 12px !important;
    }}
    
    /* Hide particles on mobile for performance */
    .particle {{
        display: none !important;
    }}
    
    /* Columns stack on mobile */
    [data-testid="column"] {{
        width: 100% !important;
        flex: 1 1 100% !important;
    }}
}}

@media (max-width: 480px) {{
    /* Extra small screens */
    h1 {{
        font-size: 26px !important;
    }}
    
    .stButton > button {{
        padding: 12px 16px !important;
        font-size: 13px !important;
    }}
    
    /* Tighter spacing */
    [data-testid="block-container"] > div {{
        padding-left: 8px !important;
        padding-right: 8px !important;
    }}
}}

/* Touch-friendly improvements */
@media (hover: none) and (pointer: coarse) {{
    /* Remove hover effects on touch devices */
    .feat-card:hover {{
        transform: none !important;
    }}
    
    .stButton > button:hover {{
        transform: none !important;
    }}
    
    /* Larger tap targets */
    .stButton > button {{
        min-height: 52px !important;
    }}
    
    /* Better scrolling */
    [data-testid="stAppViewContainer"] {{
        -webkit-overflow-scrolling: touch !important;
    }}
}}
</style>
""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════
# BACKGROUND PARTICLES — pure CSS floating gold dots
# ════════════════════════════════════════════════════════════
def render_particles():
    PARTICLES = [
        (6,  "8%",  "92%", "18s", "0s"),
        (4,  "22%", "78%", "22s", "3s"),
        (8,  "38%", "88%", "16s", "1s"),
        (3,  "55%", "95%", "25s", "5s"),
        (5,  "72%", "82%", "20s", "2s"),
        (7,  "88%", "90%", "14s", "4s"),
        (4,  "15%", "70%", "28s", "6s"),
        (6,  "45%", "75%", "19s", "1.5s"),
        (3,  "65%", "85%", "24s", "3.5s"),
        (5,  "82%", "68%", "17s", "7s"),
        (9,  "30%", "95%", "21s", "2.5s"),
        (4,  "92%", "72%", "23s", "4.5s"),
    ]
    dots = "".join(
        f'<div class="particle" style="width:{s}px;height:{s}px;left:{l};bottom:{b};'
        f'animation-duration:{d};animation-delay:{dl};"></div>'
        for s, l, b, d, dl in PARTICLES
    )
    st.markdown(
f'<div style="position:fixed;inset:0;pointer-events:none;z-index:0;">{dots}</div>',
        unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════
# HERO
# ════════════════════════════════════════════════════════════
def render_hero():
    logo_html = (
        f'<img src="data:image/jpeg;base64,{LOGO}" '
        f'style="height:96px;width:auto;'
        f'filter:drop-shadow(0 0 32px rgba(212,175,55,0.6));'
        f'animation:pulse 4s ease infinite;"/>'
    ) if LOGO else '<span style="font-size:80px;animation:pulse 4s ease infinite;display:inline-block;">⚖️</span>'

    chips = "".join(
        f'<span style="background:rgba({_rgb(c)},0.1);border:1px solid rgba({_rgb(c)},0.3);'
        f'color:{c};font-size:11px;padding:6px 18px;border-radius:20px;letter-spacing:0.5px;'
        f'transition:all 0.3s ease;">{t}</span>'
        for t, c in [
            ("3,593 Law Chunks",                "#D4AF37"),
            ("14 Indian Acts",                   "#FF7722"),
            ("Hindi · Telugu · Tamil · Kannada", "#22C55E"),
            ("ICA · IDA · RTI · CPA · BNS 2023","#0EA5E9"),
            ("100% Free · No Login Required",    "#A855F7"),
        ]
    )

    st.markdown(
f"""<div style="text-align:center;padding:80px 5% 44px;position:relative;overflow:hidden;z-index:1;">

<!-- Indian flag tricolor strip at top -->
<div style="position:absolute;top:0;left:0;right:0;height:3.5px;
background:linear-gradient(90deg,#FF4500 0%,#FF7722 20%,#FFFFFF 40%,#138808 60%,#138808 80%,#FF7722 90%,#FF4500 100%);
background-size:200% 100%;animation:tricolor 4s linear infinite;
box-shadow:0 0 12px rgba(212,175,55,0.3);"></div>

<!-- Radial glow behind hero -->
<div style="position:absolute;top:0;left:50%;transform:translateX(-50%);
width:900px;height:500px;pointer-events:none;
background:radial-gradient(ellipse at 50% 0%,rgba(212,175,55,0.1) 0%,rgba(212,175,55,0.03) 40%,transparent 70%);"></div>

<!-- Giant watermark scales of justice -->
<div style="position:absolute;right:5%;top:50%;transform:translateY(-50%);
font-size:280px;opacity:0.015;pointer-events:none;user-select:none;
filter:blur(1px);">⚖️</div>

<!-- Logo -->
<div style="margin-bottom:22px;animation:fadein 0.8s ease both;">
{logo_html}
</div>

<!-- Main title -->
<h1 style="font-family:'Playfair Display',serif;
font-size:clamp(56px,8vw,96px);
margin:0;line-height:0.95;
background:linear-gradient(175deg,#FFFFFF 0%,#F0EEE8 30%,#D4AF37 75%,#C9A830 100%);
-webkit-background-clip:text;-webkit-text-fill-color:transparent;
animation:glow 7s ease infinite,fadein 0.8s ease 0.1s both;">Nyaya-Setu</h1>

<!-- Hindi subtitle -->
<div style="font-size:20px;color:#FF7722;letter-spacing:12px;font-weight:300;
margin:10px 0 6px;animation:fadein 0.8s ease 0.2s both;">न्याय सेतु</div>
<div style="font-size:12px;color:#8E8E93;letter-spacing:5px;margin-bottom:28px;
animation:fadein 0.8s ease 0.3s both;">BRIDGE TO JUSTICE · INDIA · 2026</div>

<!-- Main tagline — simpler language -->
<p style="font-family:'Playfair Display',serif;font-size:clamp(16px,2.2vw,22px);
font-style:italic;color:#E2E8F0;max-width:680px;margin:0 auto 32px;
line-height:1.75;animation:fadein 0.8s ease 0.4s both;">
"Every Indian deserves to know their rights — before they sign any paper."
</p>

<!-- Feature chips -->
<div style="display:flex;gap:10px;flex-wrap:wrap;justify-content:center;
animation:fadein 0.8s ease 0.5s both;">
{chips}
</div>

</div>""",
        unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════
# INTELLIGENCE HUD — animated counters
# ════════════════════════════════════════════════════════════
def render_hud():
    stats = [
        ("3,593",   "Law Chunks",        "#D4AF37"),
        ("14+",     "Indian Acts",       "#FF7722"),
        ("5",       "Languages",         "#22C55E"),
        ("3 Crore+","Court Judgments",   "#0EA5E9"),
        ("24 / 7",  "AI Advocate",       "#A855F7"),
    ]

    parts = []
    for i, (val, label, color) in enumerate(stats):
        parts.append(
            f'<div style="text-align:center;padding:0 24px;animation:countUp 0.7s ease {i*0.1:.1f}s both;">'
            f'<div class="hud-val" style="font-size:clamp(18px,2.5vw,26px);font-weight:800;color:{color};'
            f'font-family:\'Playfair Display\',serif;line-height:1;">{val}</div>'
            f'<div style="font-size:10px;color:#8E8E93;letter-spacing:2px;text-transform:uppercase;margin-top:5px;">{label}</div>'
            f'</div>'
        )
        if i < len(stats)-1:
            parts.append('<div style="width:1px;height:36px;background:rgba(212,175,55,0.18);flex-shrink:0;"></div>')

    st.markdown(
f"""<div style="margin:0 5% 44px;background:rgba(255,255,255,0.018);
backdrop-filter:blur(24px);-webkit-backdrop-filter:blur(24px);
border:1px solid rgba(212,175,55,0.18);border-radius:60px;
padding:22px 40px;display:flex;justify-content:center;
align-items:center;flex-wrap:wrap;gap:0;z-index:1;position:relative;
animation:borderGlow 4s ease infinite,fadein 0.8s ease 0.3s both;">
{''.join(parts)}
</div>""",
        unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════
# DID YOU KNOW — JS-powered auto-slide, dot navigation
# No page reload — smooth JS transitions
# ════════════════════════════════════════════════════════════
def render_did_you_know():
    # Build all 8 slides as hidden divs — JS handles showing
    slides_html = ""
    for i, dyk in enumerate(DID_YOU_KNOW):
        tc = dyk["color"]
        vis = "block" if i == 0 else "none"
        slides_html += (
            f'<div class="dyk-slide" id="dyk-{i}" style="display:{vis};">'
            f'<div style="display:flex;align-items:center;gap:12px;margin-bottom:16px;flex-wrap:wrap;">'
            f'<span style="font-size:11px;color:#FF7722;letter-spacing:4px;text-transform:uppercase;font-weight:700;">💡 Did You Know?</span>'
            f'<span style="background:rgba({_rgb(tc)},0.14);border:1px solid rgba({_rgb(tc)},0.35);'
            f'color:{tc};font-size:11px;padding:3px 14px;border-radius:20px;letter-spacing:0.5px;">{dyk["tag"]}</span>'
            f'<span style="font-size:11px;color:#555;margin-left:auto;">{dyk["num"]}</span>'
            f'</div>'
            f'<div style="font-family:\'Playfair Display\',serif;font-size:clamp(15px,2vw,19px);'
            f'font-style:italic;color:#F0EEE8;line-height:1.8;margin-bottom:16px;">'
            f'"{dyk["quote"]}"</div>'
            f'<div style="font-size:11px;color:#FF7722;letter-spacing:2px;text-transform:uppercase;'
            f'margin-bottom:14px;">{dyk["law"]}</div>'
            f'<div style="background:rgba(0,0,0,0.35);border-left:3px solid #22C55E;'
            f'padding:14px 20px;border-radius:0 10px 10px 0;">'
            f'<div style="font-size:13.5px;color:#94A3B8;line-height:1.85;">{dyk["meaning"]}</div>'
            f'</div>'
            f'</div>'
        )

    # Dot indicators
    dots_html = ""
    for i in range(len(DID_YOU_KNOW)):
        active_cls = "active" if i == 0 else ""
        tag_title  = DID_YOU_KNOW[i]["tag"]
        dots_html += (
            f'<div class="dyk-dot {active_cls}" id="dot-{i}" '
            f'onclick="dykGoto({i})" title="{tag_title}"></div>'
        )

    # Progress bar
    progress_html = (
        '<div style="height:2px;background:rgba(212,175,55,0.12);border-radius:2px;margin-top:16px;overflow:hidden;">'
        '<div id="dyk-progress" style="height:100%;background:linear-gradient(90deg,#D4AF37,#FF7722);'
        'border-radius:2px;width:12.5%;transition:width 0.15s ease;"></div>'
        '</div>'
    )

    st.markdown(
f"""<div style="margin:0 5% 44px;position:relative;z-index:1;">
<!-- Section label -->
<div style="text-align:center;margin-bottom:20px;">
<div style="font-size:11px;color:#FF7722;letter-spacing:6px;text-transform:uppercase;margin-bottom:6px;">Know Your Rights</div>
<h2 style="font-family:'Playfair Display',serif;font-size:clamp(24px,3vw,34px);
margin:0;color:#F0EEE8;">Laws That Protect You — Right Now</h2>
</div>

<!-- Main card -->
<div style="background:linear-gradient(140deg,rgba(212,175,55,0.07) 0%,rgba(212,175,55,0.02) 60%,rgba(10,10,22,0.6) 100%);
border-left:4px solid #D4AF37;border-radius:0 24px 24px 0;
padding:32px 44px 24px;position:relative;overflow:hidden;
box-shadow:0 4px 40px rgba(0,0,0,0.4);animation:fadein 0.6s ease both;">

<!-- Giant quote watermark -->
<div style="position:absolute;top:-10px;left:10px;font-family:'Playfair Display',serif;
font-size:140px;color:#D4AF37;opacity:0.04;line-height:1;pointer-events:none;user-select:none;">"</div>

<!-- All slides (JS toggles display) -->
{slides_html}

<!-- Controls row -->
<div style="display:flex;align-items:center;justify-content:space-between;margin-top:20px;flex-wrap:wrap;gap:12px;">
<div style="display:flex;align-items:center;gap:4px;">{dots_html}</div>
<div style="display:flex;gap:8px;">
<button onclick="dykPrev()" style="background:rgba(212,175,55,0.1);border:1px solid rgba(212,175,55,0.3);
color:#D4AF37;border-radius:50px;padding:6px 20px;font-size:12px;cursor:pointer;
font-family:'Plus Jakarta Sans',sans-serif;font-weight:600;letter-spacing:1px;
transition:all 0.3s ease;" onmouseover="this.style.background='rgba(212,175,55,0.25)'" onmouseout="this.style.background='rgba(212,175,55,0.1)'">← Prev</button>
<button onclick="dykNext()" style="background:rgba(212,175,55,0.1);border:1px solid rgba(212,175,55,0.3);
color:#D4AF37;border-radius:50px;padding:6px 20px;font-size:12px;cursor:pointer;
font-family:'Plus Jakarta Sans',sans-serif;font-weight:600;letter-spacing:1px;
transition:all 0.3s ease;" onmouseover="this.style.background='rgba(212,175,55,0.25)'" onmouseout="this.style.background='rgba(212,175,55,0.1)'">Next →</button>
<button onclick="dykToggleAuto()" id="dyk-pause-btn" style="background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.1);
color:#8E8E93;border-radius:50px;padding:6px 16px;font-size:11px;cursor:pointer;
font-family:'Plus Jakarta Sans',sans-serif;transition:all 0.3s ease;" onmouseover="this.style.color='#F0EEE8'" onmouseout="this.style.color='#8E8E93'">⏸ Pause</button>
</div>
</div>

{progress_html}
</div>
</div>

<script>
var _dykIdx = 0;
var _dykTotal = {len(DID_YOU_KNOW)};
var _dykAuto = true;
var _dykTimer = null;
var _dykInterval = 7000;

function dykGoto(n) {{
  var slides = document.querySelectorAll('[id^="dyk-"]');
  var dots = document.querySelectorAll('.dyk-dot');
  if (!slides.length) return;
  slides.forEach(function(s, i) {{
    if (s.id === 'dyk-' + n) {{
      s.style.display = 'block';
      s.style.animation = 'none';
      setTimeout(function() {{ s.style.animation = 'dykFadeIn 0.45s cubic-bezier(0.4,0,0.2,1) both'; }}, 10);
    }} else {{
      s.style.display = 'none';
    }}
  }});
  dots.forEach(function(d, i) {{
    d.classList.toggle('active', i === n);
  }});
  var progress = document.getElementById('dyk-progress');
  if (progress) progress.style.width = ((n + 1) / _dykTotal * 100) + '%';
  _dykIdx = n;
}}

function dykNext() {{
  dykGoto((_dykIdx + 1) % _dykTotal);
  if (_dykAuto) {{ clearInterval(_dykTimer); _dykTimer = setInterval(dykNext, _dykInterval); }}
}}

function dykPrev() {{
  dykGoto((_dykIdx - 1 + _dykTotal) % _dykTotal);
  if (_dykAuto) {{ clearInterval(_dykTimer); _dykTimer = setInterval(dykNext, _dykInterval); }}
}}

function dykToggleAuto() {{
  _dykAuto = !_dykAuto;
  var btn = document.getElementById('dyk-pause-btn');
  if (_dykAuto) {{
    _dykTimer = setInterval(dykNext, _dykInterval);
    if (btn) btn.textContent = '⏸ Pause';
  }} else {{
    clearInterval(_dykTimer);
    if (btn) btn.textContent = '▶ Play';
  }}
}}

if (_dykAuto) {{ _dykTimer = setInterval(dykNext, _dykInterval); }}
</script>
""",
        unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════
# FEATURE CARDS — all 7 tools with hover effects
# ════════════════════════════════════════════════════════════
def render_features():
    st.markdown(
"""<div style="padding:0 5% 20px;text-align:center;z-index:1;position:relative;">
<div style="font-size:11px;color:#FF7722;letter-spacing:6px;text-transform:uppercase;margin-bottom:10px;">Your Complete Legal Toolkit</div>
<h2 style="font-family:'Playfair Display',serif;font-size:clamp(26px,3.5vw,40px);margin:0 0 10px;color:#F0EEE8;">Pick What You Need</h2>
<p style="font-size:14px;color:#8E8E93;margin:0 auto;max-width:500px;">Seven tools — one mission. Making Indian law simple for every Indian.</p>
</div>""",
        unsafe_allow_html=True)

    # Row 1 — 3 cards
    c1 = st.columns(3, gap="small")
    for i, col in enumerate(c1):
        _render_card(col, FEATURES[i], i)

    st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)

    # Row 2 — 3 cards
    c2 = st.columns(3, gap="small")
    for i, col in enumerate(c2):
        _render_card(col, FEATURES[i+3], i+3)

    st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)

    # Row 3 — Free Legal Aid centred
    _, cen, _ = st.columns([1, 2, 1])
    _render_card(cen, FEATURES[6], 6)


def _render_card(col, f, idx):
    c     = f["color"]
    badge = f.get("badge", "")
    delay = f"{idx * 0.06:.2f}s"

    badge_html = (
        f'<div style="position:absolute;top:14px;right:14px;'
        f'background:rgba({_rgb(c)},0.14);border:1px solid rgba({_rgb(c)},0.4);'
        f'color:{c};font-size:10px;padding:3px 10px;border-radius:20px;">{badge}</div>'
    ) if badge else ""

    with col:
        st.markdown(
f"""<div class="feat-card" style="position:relative;
background:rgba(8,8,20,0.88);
backdrop-filter:blur(20px);-webkit-backdrop-filter:blur(20px);
border:1px solid rgba(255,255,255,0.05);
border-top:2px solid rgba({_rgb(c)},0.65);
border-radius:22px;padding:32px 24px 24px;
text-align:center;min-height:270px;
box-shadow:0 2px 20px rgba(0,0,0,0.4);
animation:scalein 0.5s ease {delay} both;
transition:all 0.4s cubic-bezier(0.4,0,0.2,1);">

<!-- Glow on hover via CSS class -->
<div style="position:absolute;inset:0;border-radius:22px;
background:radial-gradient(ellipse at 50% 0%,rgba({_rgb(c)},0.06) 0%,transparent 70%);
pointer-events:none;"></div>

{badge_html}

<div style="font-size:46px;margin-bottom:14px;
animation:fadein 0.5s ease {float(delay[:-1])+0.1:.2f}s both;
display:inline-block;filter:drop-shadow(0 0 10px rgba({_rgb(c)},0.4));">
{f['icon']}</div>

<div style="font-size:10px;color:{c};letter-spacing:3px;text-transform:uppercase;margin-bottom:6px;">{f['tagline']}</div>
<div style="font-family:'Playfair Display',serif;font-size:21px;font-weight:700;color:#F0EEE8;margin-bottom:12px;">{f['title']}</div>
<div style="font-size:13px;color:#8E8E93;line-height:1.8;">{f['desc']}</div>
</div>""",
            unsafe_allow_html=True)

        st.markdown("<div style='margin-top:6px;'></div>", unsafe_allow_html=True)
        if f.get("page"):
            if st.button(f["btn"], key=f"feat_{idx}", use_container_width=True):
                st.switch_page(f["page"])
        else:
            st.link_button(f["btn"], url=f.get("link","https://nalsa.gov.in"), use_container_width=True)


# ════════════════════════════════════════════════════════════
# CONSTITUTION BANNER — pulsing, impactful
# ════════════════════════════════════════════════════════════
def render_constitution_banner():
    st.markdown("<div style='height:40px;'></div>", unsafe_allow_html=True)
    st.markdown(
"""<div style="margin:0 5%;background:linear-gradient(135deg,rgba(12,4,4,0.96),rgba(4,10,4,0.96));
border:1px solid rgba(255,119,34,0.25);border-radius:18px;
padding:28px 44px;display:flex;align-items:center;gap:22px;flex-wrap:wrap;
box-shadow:0 4px 40px rgba(0,0,0,0.5);animation:fadein 0.6s ease both;position:relative;z-index:1;">
<div style="font-size:30px;animation:pulse 3s ease infinite;">🔥</div>
<div style="flex:1;min-width:0;">
<div style="font-size:10px;color:#FF7722;letter-spacing:4px;font-weight:700;margin-bottom:8px;">ARTICLE 39A · CONSTITUTION OF INDIA</div>
<div style="font-family:'Playfair Display',serif;font-size:clamp(13px,1.8vw,16px);font-style:italic;color:#E2E8F0;line-height:1.8;">"The State shall provide free legal aid to ensure that opportunities for securing justice are not denied to any citizen by reason of poverty or any other disability."</div>
</div>
<div style="font-size:30px;animation:pulse 3s ease infinite 1.5s;">🔥</div>
</div>""",
        unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════
# HOW IT WORKS — 4 steps, animated number circles
# ════════════════════════════════════════════════════════════
def render_how_it_works():
    st.markdown("<div style='height:48px;'></div>", unsafe_allow_html=True)
    st.markdown(
"""<div style="padding:0 5% 24px;text-align:center;z-index:1;position:relative;">
<div style="font-size:11px;color:#FF7722;letter-spacing:6px;text-transform:uppercase;margin-bottom:8px;">Getting Started</div>
<h2 style="font-family:'Playfair Display',serif;font-size:clamp(24px,3.5vw,36px);margin:0 0 8px;color:#F0EEE8;">How It Works</h2>
<p style="font-size:14px;color:#8E8E93;">From your problem to your answer in under 2 minutes.</p>
</div>""",
        unsafe_allow_html=True)

    steps = [
        ("1", "Tell Us Your Problem",     "Type in simple, everyday words — 'my boss won't pay me' or 'landlord threw me out.' No legal terms needed. Just describe what happened.",            "#D4AF37"),
        ("2", "AI Reads the Law for You", "We search 14 Indian laws and 3 crore real court judgments instantly. Our AI finds every rule that applies to your specific situation.",              "#FF7722"),
        ("3", "Understand in Plain Words","Every answer is written simply — what the law says, what it means for YOU, and what real courts have decided in cases just like yours.",             "#22C55E"),
        ("4", "Take the Next Step",       "Generate a legal notice, file an RTI application, check your win chances, or get a document ready — all without a lawyer, completely free.",       "#0EA5E9"),
    ]

    cols = st.columns(4, gap="small")
    for i, (num, title, desc, color) in enumerate(steps):
        delay = f"{i * 0.1:.1f}s"
        with cols[i]:
            # Connector line (not on last card)
            connector = (
                f'<div style="position:absolute;top:22px;right:-20px;width:40px;height:2px;'
                f'background:linear-gradient(90deg,rgba({_rgb(color)},0.4),rgba({_rgb(color)},0.05));'
                f'z-index:2;"></div>'
            ) if i < 3 else ""

            st.markdown(
f"""<div style="position:relative;background:rgba(8,8,20,0.88);
border:1px solid rgba(255,255,255,0.05);border-radius:18px;
padding:28px 20px;text-align:center;min-height:200px;
box-shadow:0 2px 20px rgba(0,0,0,0.3);
animation:fadein 0.5s ease {delay} both;
transition:all 0.35s ease;">
{connector}
<div style="width:46px;height:46px;
background:rgba({_rgb(color)},0.12);
border:2px solid rgba({_rgb(color)},0.5);
border-radius:50%;display:flex;align-items:center;justify-content:center;
margin:0 auto 16px;font-size:19px;font-weight:800;color:{color};
box-shadow:0 0 20px rgba({_rgb(color)},0.2);
transition:all 0.35s ease;">{num}</div>
<div style="font-size:14px;font-weight:700;color:#F0EEE8;margin-bottom:10px;">{title}</div>
<div style="font-size:12px;color:#8E8E93;line-height:1.75;">{desc}</div>
</div>""",
                unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════
# LAWS TICKER — auto-scrolling marquee of all 14 laws
# ════════════════════════════════════════════════════════════
def render_laws_ticker():
    st.markdown("<div style='height:40px;'></div>", unsafe_allow_html=True)
    st.markdown(
"""<div style="text-align:center;margin-bottom:14px;z-index:1;position:relative;">
<div style="font-size:11px;color:#8E8E93;letter-spacing:4px;text-transform:uppercase;">Laws & Acts in Our Knowledge Base</div>
</div>""",
        unsafe_allow_html=True)

    # Build ticker items — doubled for seamless loop
    ticker_item = lambda code, name: (
        f'<span style="display:inline-flex;align-items:center;gap:6px;'
        f'background:rgba(212,175,55,0.06);border:1px solid rgba(212,175,55,0.15);'
        f'border-radius:20px;padding:7px 18px;margin:0 8px;white-space:nowrap;flex-shrink:0;">'
        f'<span style="color:#D4AF37;font-size:11px;font-weight:700;">{code}</span>'
        f'<span style="color:#8E8E93;font-size:11px;">{name}</span>'
        f'</span>'
    )

    items_html = "".join(ticker_item(c, n) for c, n in LAWS)
    # Double the items for seamless infinite scroll
    ticker_content = items_html + items_html

    st.markdown(
f"""<div style="overflow:hidden;position:relative;z-index:1;
border-top:1px solid rgba(212,175,55,0.06);
border-bottom:1px solid rgba(212,175,55,0.06);
padding:12px 0;">
<!-- Fade edges -->
<div style="position:absolute;left:0;top:0;bottom:0;width:80px;
background:linear-gradient(90deg,rgba(2,2,6,0.95),transparent);z-index:2;pointer-events:none;"></div>
<div style="position:absolute;right:0;top:0;bottom:0;width:80px;
background:linear-gradient(270deg,rgba(2,2,6,0.95),transparent);z-index:2;pointer-events:none;"></div>
<!-- Scrolling content -->
<div style="display:flex;animation:tickerScroll 40s linear infinite;"
onmouseover="this.style.animationPlayState='paused'"
onmouseout="this.style.animationPlayState='running'">
{ticker_content}
</div>
</div>""",
        unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════
# EMERGENCY HELPLINES — always visible, bold numbers
# ════════════════════════════════════════════════════════════
def render_helplines():
    st.markdown("<div style='height:40px;'></div>", unsafe_allow_html=True)
    st.markdown(
"""<div style="padding:0 5% 16px;text-align:center;z-index:1;position:relative;">
<div style="font-size:11px;color:#EF4444;letter-spacing:6px;text-transform:uppercase;margin-bottom:6px;">Emergency Helplines</div>
<h3 style="font-family:'Playfair Display',serif;font-size:22px;margin:0 0 4px;color:#F0EEE8;">Save These Numbers</h3>
<p style="font-size:13px;color:#8E8E93;">Free. Available 24 hours. Yours by right.</p>
</div>""",
        unsafe_allow_html=True)

    lines = [
        ("👮", "Police",           "100",           "#EF4444"),
        ("🚑", "Ambulance",        "108",           "#22C55E"),
        ("👩", "Women Helpline",   "1091",          "#F59E0B"),
        ("🏛️","Free Legal Aid",   "15100",          "#D4AF37"),
        ("🛒", "Consumer Forum",   "1800-11-4000",  "#A855F7"),
        ("👶", "Child Helpline",   "1098",          "#0EA5E9"),
    ]

    cols = st.columns(6, gap="small")
    for i, (icon, name, num, color) in enumerate(lines):
        delay = f"{i * 0.07:.2f}s"
        with cols[i]:
            st.markdown(
f"""<div style="background:rgba(8,8,20,0.9);
border:1px solid rgba({_rgb(color)},0.2);
border-bottom:3px solid rgba({_rgb(color)},0.5);
border-radius:16px;padding:18px 10px;text-align:center;
box-shadow:0 2px 16px rgba(0,0,0,0.3);
animation:fadein 0.5s ease {delay} both;
transition:all 0.3s ease;" onmouseover="this.style.transform='translateY(-4px)';this.style.boxShadow='0 8px 24px rgba({_rgb(color)},0.2)'" onmouseout="this.style.transform='translateY(0)';this.style.boxShadow='0 2px 16px rgba(0,0,0,0.3)'">
<div style="font-size:26px;margin-bottom:7px;">{icon}</div>
<div style="font-size:10px;color:#8E8E93;margin-bottom:5px;letter-spacing:0.5px;">{name}</div>
<div style="font-size:clamp(16px,2vw,22px);font-weight:800;color:{color};
font-family:'Playfair Display',serif;">{num}</div>
</div>""",
                unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════
# LIVE LEGAL AID FINDER — Google Maps link
# ════════════════════════════════════════════════════════════
def render_legal_aid_finder():
    st.markdown("<div style='height:36px;'></div>", unsafe_allow_html=True)

    left, right = st.columns([7, 5], gap="large")

    with left:
        st.markdown(
"""<div style="background:rgba(212,175,55,0.05);border:1px solid rgba(212,175,55,0.15);
border-radius:20px;padding:36px 40px;height:100%;animation:fadein 0.6s ease both;position:relative;z-index:1;">
<div style="font-size:11px;color:#FF7722;letter-spacing:4px;text-transform:uppercase;margin-bottom:10px;">Article 39A</div>
<h3 style="font-family:'Playfair Display',serif;font-size:clamp(20px,2.5vw,28px);color:#F0EEE8;margin:0 0 14px;line-height:1.3;">Find Free Legal Help<br/>Near Your Home</h3>
<p style="font-size:14px;color:#8E8E93;line-height:1.8;margin-bottom:22px;">If you cannot afford a lawyer, the government must provide one for free. This is guaranteed by the Constitution under Article 39A. The National Legal Services Authority (NALSA) has offices in every district in India.</p>
<a href="https://www.google.com/maps/search/District+Legal+Services+Authority" target="_blank"
style="display:inline-block;background:linear-gradient(135deg,#D4AF37,#FF7722);
color:#000;font-weight:700;padding:13px 30px;border-radius:50px;
text-decoration:none;font-size:13px;letter-spacing:1px;
transition:all 0.3s ease;box-shadow:0 4px 20px rgba(212,175,55,0.3);"
onmouseover="this.style.transform='translateY(-3px)';this.style.boxShadow='0 8px 30px rgba(212,175,55,0.5)'"
onmouseout="this.style.transform='translateY(0)';this.style.boxShadow='0 4px 20px rgba(212,175,55,0.3)'">
📍 Find Legal Aid Office Near Me →
</a>
</div>""",
            unsafe_allow_html=True)

    with right:
        st.markdown(
"""<div style="display:flex;flex-direction:column;gap:12px;animation:fadein 0.6s ease 0.15s both;position:relative;z-index:1;">
<div style="background:rgba(8,8,20,0.88);border:1px solid rgba(255,255,255,0.06);border-radius:16px;padding:18px 22px;">
<div style="font-size:12px;color:#D4AF37;font-weight:700;margin-bottom:4px;">📞 NALSA National Helpline</div>
<div style="font-size:28px;font-weight:800;color:#F0EEE8;font-family:'Playfair Display',serif;">15100</div>
<div style="font-size:12px;color:#8E8E93;margin-top:2px;">Free · 24/7 · All languages</div>
</div>
<div style="background:rgba(8,8,20,0.88);border:1px solid rgba(255,255,255,0.06);border-radius:16px;padding:18px 22px;">
<div style="font-size:12px;color:#22C55E;font-weight:700;margin-bottom:6px;">Who qualifies for free legal aid?</div>
<div style="font-size:12px;color:#8E8E93;line-height:1.75;">
✓ Annual income below ₹1 lakh<br/>
✓ Women (for any case)<br/>
✓ Persons with disabilities<br/>
✓ SC / ST community members<br/>
✓ Industrial workmen<br/>
✓ Victims of trafficking or disasters
</div>
</div>
</div>""",
            unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════
# FOOTER
# ════════════════════════════════════════════════════════════
def render_footer():
    st.markdown("<div style='height:56px;'></div>", unsafe_allow_html=True)
    st.markdown(
"""<div style="text-align:center;padding:36px 5%;border-top:1px solid rgba(212,175,55,0.08);z-index:1;position:relative;">
<div style="font-family:'Playfair Display',serif;font-size:30px;color:#D4AF37;
margin-bottom:6px;animation:glow 7s ease infinite;">Nyaya-Setu</div>
<div style="font-size:12px;color:#8E8E93;letter-spacing:2px;margin-bottom:16px;">न्याय सेतु · Bridge to Justice · India · 2026</div>
<div style="display:flex;gap:20px;justify-content:center;flex-wrap:wrap;margin-bottom:16px;">
<span style="font-size:12px;color:#555;">Built by B.Tech students at CVR College of Engineering</span>
<span style="font-size:12px;color:#444;">·</span>
<span style="font-size:12px;color:#555;">nyayasetu.me</span>
</div>
<div style="font-size:11px;color:#383838;max-width:600px;margin:0 auto;line-height:1.8;">
This platform gives general legal information only — not legal advice. For serious matters, always consult a licensed advocate. Free legal aid is available at 15100.
</div>
</div>""",
        unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════
# MAIN — render in order
# ════════════════════════════════════════════════════════════
inject_css()
render_particles()
render_hero()
render_hud()
render_did_you_know()
render_features()
render_constitution_banner()
render_how_it_works()
render_laws_ticker()
render_helplines()
render_legal_aid_finder()
render_footer()