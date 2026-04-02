import streamlit as st
import base64, os, requests, textwrap

st.set_page_config(
    page_title="Nyaya-Setu | Case Archives",
    page_icon="🔍",
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

def md(html, **kw):
    st.markdown(textwrap.dedent(html), unsafe_allow_html=True, **kw)


# ════════════════════════════════════════════════════════════
# SITUATION TILES — real problems real people face
# query is used directly for IK smart search
# ════════════════════════════════════════════════════════════
SITUATIONS = [
    {"emoji":"💰","title":"Boss didn't pay my salary",     "subtitle":"Wages withheld after work done",             "query":"salary not paid employer withheld wages",          "category":"employment","color":"#0EA5E9"},
    {"emoji":"🔑","title":"Landlord won't return deposit", "subtitle":"Security deposit refused after vacating",     "query":"landlord not returning security deposit tenant",   "category":"property",  "color":"#22C55E"},
    {"emoji":"🚪","title":"Landlord trying to evict me",   "subtitle":"Thrown out without proper notice",            "query":"landlord evicting tenant without notice",          "category":"property",  "color":"#22C55E"},
    {"emoji":"⚡","title":"Wrong electricity or water bill","subtitle":"Inflated or incorrect bill",                 "query":"wrong electricity bill consumer complaint",        "category":"consumer",  "color":"#A855F7"},
    {"emoji":"📦","title":"Company refused to refund money","subtitle":"Product defective, refund denied",           "query":"company refused refund defective product",         "category":"consumer",  "color":"#A855F7"},
    {"emoji":"🔥","title":"Fired from job without notice", "subtitle":"Terminated, no notice or pay given",          "query":"fired from job without notice pay",                "category":"employment","color":"#0EA5E9"},
    {"emoji":"📋","title":"Government ignoring my RTI",    "subtitle":"Information request rejected or unanswered",  "query":"RTI application ignored no response government",   "category":"rti",       "color":"#D4AF37"},
    {"emoji":"💔","title":"Need divorce or maintenance",   "subtitle":"Separation, alimony, monthly support",        "query":"divorce maintenance alimony spouse family court",  "category":"family",    "color":"#F59E0B"},
    {"emoji":"🤝","title":"Someone cheated or defrauded",  "subtitle":"Money taken through deception",               "query":"cheated defrauded money taken criminal",           "category":"criminal",  "color":"#EF4444"},
    {"emoji":"👮","title":"False case filed against me",   "subtitle":"Fabricated FIR or wrongful arrest",           "query":"false FIR filed against me wrongful arrest",       "category":"criminal",  "color":"#EF4444"},
    {"emoji":"🏥","title":"Hospital or doctor negligence", "subtitle":"Wrong treatment or medical mistake",           "query":"doctor hospital medical negligence wrong treatment","category":"consumer",  "color":"#A855F7"},
    {"emoji":"⏰","title":"Overtime work not paid",         "subtitle":"Extra hours done, extra pay denied",          "query":"overtime worked not paid employer extra hours",    "category":"employment","color":"#0EA5E9"},
]

CAT_LABELS = {
    "all":"All Topics", "employment":"💼 Employment",
    "consumer":"🛒 Consumer", "property":"🏠 Property",
    "criminal":"⚖️ Criminal","family":"👨‍👩‍👧 Family","rti":"📋 RTI / Govt",
}
CAT_COLORS = {
    "all":"#D4AF37","employment":"#0EA5E9","consumer":"#A855F7",
    "property":"#22C55E","criminal":"#EF4444","family":"#F59E0B","rti":"#D4AF37",
}


# ════════════════════════════════════════════════════════════
# SCORE COLOUR + LABEL
# ════════════════════════════════════════════════════════════
def score_style(score: int):
    if score >= 85: return "#22C55E", "Highly Relevant"
    if score >= 70: return "#D4AF37", "Relevant"
    return "#F59E0B", "Somewhat Relevant"


def _rgb(hex_color: str) -> str:
    h = hex_color.lstrip("#")
    return f"{int(h[0:2],16)},{int(h[2:4],16)},{int(h[4:6],16)}"


# ════════════════════════════════════════════════════════════
# CSS
# ════════════════════════════════════════════════════════════
def inject_css():
    bg_rule = (
        f"background-image:linear-gradient(rgba(3,3,5,0.93),rgba(3,3,5,0.98)),"
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
.stButton>button{{background:transparent!important;border:1px solid rgba(212,175,55,0.35)!important;color:#D4AF37!important;border-radius:50px!important;padding:8px 20px!important;font-weight:600!important;letter-spacing:1px!important;font-size:12px!important;transition:0.3s!important;font-family:'Plus Jakarta Sans',sans-serif!important;}}
.stButton>button:hover{{background:#D4AF37!important;color:#000!important;box-shadow:0 0 20px rgba(212,175,55,0.4)!important;}}
[data-testid="stTextInput"]>div>div>input{{background:rgba(8,8,18,0.97)!important;border:2px solid rgba(212,175,55,0.3)!important;border-radius:50px!important;color:#F5F5F7!important;font-size:15px!important;padding:14px 26px!important;}}
[data-testid="stTextInput"]>div>div>input:focus{{border-color:#D4AF37!important;box-shadow:0 0 28px rgba(212,175,55,0.14)!important;}}
[data-testid="stTextInput"]>div>div>input::placeholder{{color:#444!important;}}
@keyframes fadein{{from{{opacity:0;transform:translateY(14px);}}to{{opacity:1;transform:translateY(0);}}}}
@keyframes scoreGlow{{0%,100%{{opacity:0.8;}}50%{{opacity:1;}}}}

/* ══ MOBILE RESPONSIVE ══ */
@media (max-width: 768px) {{
    h1 {{ font-size: 32px !important; }}
    [data-testid="stTextInput"]>div>div>input {{ padding: 12px 18px !important; font-size: 16px !important; border-radius: 25px !important; }}
    .stButton>button {{ padding: 14px 20px !important; min-height: 48px !important; }}
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
"""<div style="text-align:center;padding:52px 5% 20px;position:relative;overflow:hidden;">
<div style="position:absolute;top:0;left:50%;transform:translateX(-50%);width:900px;height:340px;pointer-events:none;background:radial-gradient(ellipse at 50% 0%,rgba(212,175,55,0.06) 0%,transparent 70%);"></div>
<div style="font-size:11px;color:#FF7722;letter-spacing:6px;text-transform:uppercase;margin-bottom:14px;">The Case Archives</div>
<h1 style="font-family:'Playfair Display',serif;font-size:50px;margin:0 0 12px;line-height:1.15;background:linear-gradient(to bottom,#FFFFFF 20%,#D4AF37 100%);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">3 Crore Indian Court Judgments.<br/>Explained in Plain Language.</h1>
<p style="font-size:16px;color:#8E8E93;max-width:600px;margin:0 auto 20px;line-height:1.8;">Describe your problem in simple words. We search only for cases that actually match your situation — and explain exactly what they mean for you.</p>
<div style="display:flex;gap:10px;justify-content:center;flex-wrap:wrap;">
<span style="background:rgba(212,175,55,0.08);border:1px solid rgba(212,175,55,0.22);color:#D4AF37;font-size:11px;padding:4px 14px;border-radius:20px;letter-spacing:1px;">Powered by Indian Kanoon</span>
<span style="background:rgba(34,197,94,0.07);border:1px solid rgba(34,197,94,0.18);color:#4ADE80;font-size:11px;padding:4px 14px;border-radius:20px;letter-spacing:1px;">AI Relevance Scoring</span>
<span style="background:rgba(168,85,247,0.07);border:1px solid rgba(168,85,247,0.18);color:#C084FC;font-size:11px;padding:4px 14px;border-radius:20px;letter-spacing:1px;">Only Highly Relevant Cases Shown</span>
</div>
</div>""",
        unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════
# SEARCH BAR
# ════════════════════════════════════════════════════════════
def render_search_bar():
    st.markdown(
"""<div style="padding:0 5% 4px;text-align:center;">
<div style="font-size:13px;color:#8E8E93;margin-bottom:10px;">Type your problem in plain words — no legal knowledge needed</div>
</div>""",
        unsafe_allow_html=True)

    inp_col, btn_col = st.columns([8, 1])
    with inp_col:
        query = st.text_input(
            "Search",
            placeholder='e.g.  "my landlord is not returning my security deposit"  or  "fired without notice"  or  "company refused refund"',
            key="search_query",
            label_visibility="collapsed",
        )
    with btn_col:
        search_clicked = st.button("🔍 Search", key="search_btn", use_container_width=True)

    category = st.session_state.get("active_category", "all")
    if category == "all":
        category = "general"

    if search_clicked and query.strip():
        return query.strip(), category
    return None, None


# ════════════════════════════════════════════════════════════
# CATEGORY TABS
# ════════════════════════════════════════════════════════════
def render_category_tabs():
    st.markdown(
"""<div style="padding:18px 5% 6px;">
<div style="font-size:11px;color:#D4AF37;letter-spacing:4px;text-transform:uppercase;margin-bottom:12px;">Filter by Topic</div>
</div>""",
        unsafe_allow_html=True)

    active = st.session_state.get("active_category", "all")
    cols   = st.columns(7, gap="small")
    for i, (key, label) in enumerate(CAT_LABELS.items()):
        color  = CAT_COLORS[key]
        is_sel = active == key
        with cols[i]:
            if st.button(label, key=f"cat_{key}", use_container_width=True):
                st.session_state["active_category"] = key
                st.session_state["search_results"]  = None
                st.rerun()


# ════════════════════════════════════════════════════════════
# SITUATION TILES
# ════════════════════════════════════════════════════════════
def render_situations():
    active = st.session_state.get("active_category", "all")
    shown  = [s for s in SITUATIONS if active == "all" or s["category"] == active]
    if not shown:
        return

    st.markdown(
"""<div style="padding:10px 5% 6px;">
<div style="font-size:11px;color:#D4AF37;letter-spacing:4px;text-transform:uppercase;margin-bottom:14px;">Or Click Your Situation Directly</div>
</div>""",
        unsafe_allow_html=True)

    cols = st.columns(4, gap="small")
    for i, sit in enumerate(shown):
        c = sit["color"]
        with cols[i % 4]:
            st.markdown(
f"""<div style="background:rgba(10,10,20,0.88);border:1px solid rgba(255,255,255,0.07);border-radius:16px;padding:18px 15px;margin-bottom:6px;min-height:108px;">
<div style="font-size:26px;margin-bottom:8px;">{sit['emoji']}</div>
<div style="font-size:13px;font-weight:700;color:#F5F5F7;line-height:1.4;margin-bottom:3px;">{sit['title']}</div>
<div style="font-size:11px;color:#8E8E93;line-height:1.5;">{sit['subtitle']}</div>
</div>""",
                unsafe_allow_html=True)
            if st.button("Find Cases →", key=f"sit_{i}", use_container_width=True):
                st.session_state["pending_sit"] = {
                    "query":    sit["query"],
                    "category": sit["category"],
                }
                st.rerun()


# ════════════════════════════════════════════════════════════
# HOW IT WORKS — 3 steps for first-time visitors
# ════════════════════════════════════════════════════════════
def render_how_it_works():
    st.markdown(
"""<div style="margin:8px 5% 28px;display:grid;grid-template-columns:1fr 1fr 1fr;gap:12px;">
<div style="background:rgba(212,175,55,0.04);border:1px solid rgba(212,175,55,0.13);border-radius:14px;padding:18px 16px;text-align:center;">
<div style="font-size:28px;margin-bottom:10px;">1️⃣</div>
<div style="font-size:13px;font-weight:700;color:#F5F5F7;margin-bottom:6px;">Describe Your Problem</div>
<div style="font-size:12px;color:#8E8E93;line-height:1.7;">Type in simple words — like how you'd tell a friend. No legal terms needed at all.</div>
</div>
<div style="background:rgba(212,175,55,0.04);border:1px solid rgba(212,175,55,0.13);border-radius:14px;padding:18px 16px;text-align:center;">
<div style="font-size:28px;margin-bottom:10px;">2️⃣</div>
<div style="font-size:13px;font-weight:700;color:#F5F5F7;margin-bottom:6px;">AI Filters for Relevance</div>
<div style="font-size:12px;color:#8E8E93;line-height:1.7;">We only show cases that actually match your situation. Irrelevant cases are automatically removed.</div>
</div>
<div style="background:rgba(212,175,55,0.04);border:1px solid rgba(212,175,55,0.13);border-radius:14px;padding:18px 16px;text-align:center;">
<div style="font-size:28px;margin-bottom:10px;">3️⃣</div>
<div style="font-size:13px;font-weight:700;color:#F5F5F7;margin-bottom:6px;">Understand in Plain Words</div>
<div style="font-size:12px;color:#8E8E93;line-height:1.7;">Every case shows what the court decided — and what it means specifically for your situation.</div>
</div>
</div>""",
        unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════
# RESULTS — the heart of the page
# Shows match score, match reasons, plain decision, means for you
# ════════════════════════════════════════════════════════════
def render_results(results: list, query: str, is_live: bool):
    count = len(results)

    # ── Results quality header ──────────────────────────────
    source_text = "🟢 Live from Indian Kanoon" if is_live else "📚 Verified Landmark Cases"
    source_color = "#4ADE80" if is_live else "#D4AF37"

    st.markdown(
f"""<div style="padding:4px 5% 20px;">
<div style="display:flex;align-items:center;gap:12px;flex-wrap:wrap;margin-bottom:6px;">
<span style="font-size:20px;font-weight:700;color:#F5F5F7;font-family:'Playfair Display',serif;">Showing {count} Highly Relevant Case{'s' if count != 1 else ''}</span>
<span style="font-size:11px;color:{source_color};background:rgba({_rgb(source_color)},0.1);border:1px solid rgba({_rgb(source_color)},0.3);padding:3px 12px;border-radius:20px;">{source_text}</span>
</div>
<div style="font-size:12px;color:#8E8E93;">For: &ldquo;{query[:70]}{'...' if len(query)>70 else ''}&rdquo;</div>
<div style="margin-top:10px;background:rgba(34,197,94,0.05);border:1px solid rgba(34,197,94,0.15);border-radius:8px;padding:8px 14px;display:inline-block;">
<span style="font-size:12px;color:#4ADE80;">✓ AI filtered for relevance — only cases that actually match your situation are shown</span>
</div>
</div>""",
        unsafe_allow_html=True)

    # ── Each case card ──────────────────────────────────────
    for i, case in enumerate(results):
        title          = case.get("title", "Court Judgment")
        court          = case.get("court", "Indian Court")
        raw_date       = case.get("date", "")
        year           = raw_date[:4] if raw_date else ""
        url            = case.get("url", "https://indiankanoon.org")
        is_fallback    = case.get("fallback", False)
        score          = case.get("relevance_score", 70)
        match_reasons  = case.get("match_reasons", [])
        plain_decision = case.get("plain_decision", "")
        means_for_you  = case.get("means_for_you", "")

        sc_color, sc_label = score_style(score)

        # Year colour
        try:
            yr_c = "#4ADE80" if int(year) >= 2015 else "#D4AF37" if int(year) >= 2000 else "#8E8E93"
        except Exception:
            yr_c = "#8E8E93"

        # Source badge
        source_badge = (
            f'<span style="font-size:10px;color:#4ADE80;background:rgba(34,197,94,0.07);'
            f'border:1px solid rgba(34,197,94,0.2);padding:2px 10px;border-radius:12px;margin-left:8px;">🟢 Indian Kanoon</span>'
            if not is_fallback else
            f'<span style="font-size:10px;color:#8E8E93;background:rgba(255,255,255,0.04);'
            f'border:1px solid rgba(255,255,255,0.08);padding:2px 10px;border-radius:12px;margin-left:8px;">Landmark Case</span>'
        )

        # Match reasons block
        reasons_html = ""
        if match_reasons:
            items = "".join(
                f'<div style="display:flex;gap:8px;align-items:flex-start;margin-bottom:6px;">'
                f'<span style="color:#D4AF37;flex-shrink:0;font-size:13px;">✔</span>'
                f'<span style="font-size:12px;color:#CBD5E1;line-height:1.6;">{r}</span>'
                f'</div>'
                for r in match_reasons
            )
            reasons_html = (
                f'<div style="margin-top:14px;background:rgba(212,175,55,0.04);'
                f'border:1px solid rgba(212,175,55,0.15);border-radius:10px;padding:12px 16px;">'
                f'<div style="font-size:10px;color:#D4AF37;font-weight:700;letter-spacing:2px;margin-bottom:8px;">WHY THIS CASE MATCHES YOUR SITUATION</div>'
                f'{items}'
                f'</div>'
            )

        # Plain decision block
        decision_html = ""
        if plain_decision:
            decision_html = (
                f'<div style="margin-top:10px;background:rgba(99,102,241,0.06);'
                f'border-left:3px solid rgba(99,102,241,0.5);border-radius:0 10px 10px 0;padding:12px 16px;">'
                f'<div style="font-size:10px;color:#818CF8;font-weight:700;letter-spacing:2px;margin-bottom:5px;">⚖️ WHAT THE COURT DECIDED</div>'
                f'<div style="font-size:13px;color:#E2E8F0;line-height:1.75;">{plain_decision}</div>'
                f'</div>'
            )

        # Means for you block
        meaning_html = ""
        if means_for_you:
            meaning_html = (
                f'<div style="margin-top:10px;background:rgba(34,197,94,0.05);'
                f'border-left:3px solid rgba(34,197,94,0.45);border-radius:0 10px 10px 0;padding:12px 16px;">'
                f'<div style="font-size:10px;color:#4ADE80;font-weight:700;letter-spacing:2px;margin-bottom:5px;">💡 WHAT THIS MEANS FOR YOU</div>'
                f'<div style="font-size:13px;color:#E2E8F0;line-height:1.75;">{means_for_you}</div>'
                f'</div>'
            )

        # Full card
        delay = f"{i * 0.1:.1f}s"
        st.markdown(
f"""<div style="margin:0 5% 18px;background:rgba(8,8,18,0.94);border:1px solid rgba(255,255,255,0.07);border-radius:18px;padding:22px 26px;animation:fadein 0.4s ease both;animation-delay:{delay};">
<div style="display:flex;justify-content:space-between;align-items:flex-start;gap:16px;flex-wrap:wrap;">
<div style="flex:1;min-width:0;">
<div style="display:flex;align-items:flex-start;gap:8px;flex-wrap:wrap;margin-bottom:6px;">
<span style="font-size:18px;font-weight:800;color:#F5F5F7;font-family:'Playfair Display',serif;line-height:1.35;">{title}</span>
{source_badge}
</div>
<div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap;">
<span style="font-size:12px;color:#8E8E93;">{court}</span>
{f'<span style="font-size:12px;font-weight:700;color:{yr_c};">{year}</span>' if year else ''}
</div>
</div>
<div style="display:flex;flex-direction:column;align-items:flex-end;gap:8px;flex-shrink:0;">
<div style="text-align:center;background:rgba({_rgb(sc_color)},0.1);border:1px solid rgba({_rgb(sc_color)},0.35);border-radius:12px;padding:8px 16px;min-width:90px;">
<div style="font-size:22px;font-weight:800;color:{sc_color};line-height:1;">{score}%</div>
<div style="font-size:10px;color:{sc_color};letter-spacing:0.5px;margin-top:2px;">{sc_label}</div>
</div>
<a href="{url}" target="_blank" style="text-decoration:none;">
<div style="background:rgba(212,175,55,0.08);border:1px solid rgba(212,175,55,0.3);border-radius:10px;padding:7px 14px;text-align:center;">
<div style="font-size:11px;color:#D4AF37;font-weight:700;">Read Full</div>
<div style="font-size:10px;color:#8E8E93;">Judgment ↗</div>
</div>
</a>
</div>
</div>
{reasons_html}
{decision_html}
{meaning_html}
</div>""",
            unsafe_allow_html=True)

    # IK Attribution — required by their terms
    st.markdown(
"""<div style="margin:16px 5% 0;padding:12px 20px;background:rgba(212,175,55,0.03);border:1px solid rgba(212,175,55,0.1);border-radius:12px;display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:8px;">
<span style="font-size:12px;color:#555;">Case law from India's largest legal database</span>
<a href="https://indiankanoon.org" target="_blank" style="text-decoration:none;">
<span style="font-size:12px;color:#D4AF37;font-weight:600;">Powered by IndianKanoon.org ↗</span>
</a>
</div>""",
        unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════
# EMPTY STATE
# ════════════════════════════════════════════════════════════
def render_empty_state():
    st.markdown(
"""<div style="text-align:center;padding:36px 5% 16px;">
<div style="font-size:52px;margin-bottom:16px;">⚖️</div>
<div style="font-size:18px;font-weight:700;color:#F5F5F7;font-family:'Playfair Display',serif;margin-bottom:8px;">Every judgment. In plain words.</div>
<div style="font-size:14px;color:#8E8E93;max-width:480px;margin:0 auto;line-height:1.8;">Type your situation above or click a problem below. We find the most relevant real court cases — and explain exactly what they mean for you.</div>
</div>""",
        unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════
# RUN SEARCH
# ════════════════════════════════════════════════════════════
def run_search(query: str, category: str) -> dict | None:
    try:
        with st.spinner("🔍 Searching and scoring relevance — this takes about 15 seconds..."):
            resp = requests.post(
                f"{API}/search/cases",
                json={"query": query, "category": category, "top_k": 3, "explain": True},
                timeout=50,
            )
            return resp.json()
    except requests.exceptions.ConnectionError:
        st.markdown(
"""<div style="margin:12px 5%;background:rgba(220,38,38,0.1);border:1px solid rgba(220,38,38,0.3);border-radius:12px;padding:16px 20px;">
<div style="color:#F87171;font-size:14px;font-weight:700;">⚠️ Cannot connect to backend.</div>
<div style="color:#FCA5A5;font-size:13px;margin-top:4px;">Run: <code>uvicorn backend.main:app --reload</code></div>
</div>""",
            unsafe_allow_html=True)
        return None
    except Exception as e:
        st.error(f"Error: {e}")
        return None


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
"<div style='font-size:11px;color:#8E8E93;letter-spacing:2px;margin-bottom:24px;'>THE CASE ARCHIVES</div>",
            unsafe_allow_html=True)
        history = st.session_state.get("search_history", [])
        if history:
            st.markdown(
"<div style='font-size:11px;color:#D4AF37;letter-spacing:3px;text-transform:uppercase;margin-bottom:10px;'>Recent Searches</div>",
                unsafe_allow_html=True)
            for h in history[-5:]:
                st.markdown(
f"<div style='font-size:12px;color:#8E8E93;padding:5px 8px;margin-bottom:3px;'>🔍 {h[:34]}{'...' if len(h)>34 else ''}</div>",
                    unsafe_allow_html=True)
            st.markdown("<div style='height:14px;'></div>", unsafe_allow_html=True)
        st.markdown(
"<div style='font-size:11px;color:#D4AF37;letter-spacing:3px;text-transform:uppercase;margin-bottom:12px;'>Navigate</div>",
            unsafe_allow_html=True)
        for icon, label, href in [
            ("🏠","Home","/"),("⚖️","Virtual Advocate","/1_chat"),
            ("📄","Witness Stand","/2_upload"),("📜","Document Forge","/4_generator"),
            ("🔮","The Oracle","/5_predict"),("📊","Chamber Records","/6_dashboard"),
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
<span style="font-size:11px;color:#333;letter-spacing:2px;">NYAYA-SETU · THE CASE ARCHIVES · INDIA · 2026 &nbsp;·&nbsp; </span>
<a href="https://indiankanoon.org" target="_blank" style="font-size:11px;color:#555;text-decoration:none;letter-spacing:2px;">POWERED BY INDIANKANOON</a>
</div>""",
        unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════
# MAIN
# ════════════════════════════════════════════════════════════
inject_css()
render_sidebar()
render_header()

# Init state
for k, v in [("active_category","all"),("search_results",None),("last_query",""),("search_history",[])]:
    if k not in st.session_state:
        st.session_state[k] = v

# Inputs
manual_query, manual_cat = render_search_bar()
st.markdown("<div style='height:6px;'></div>", unsafe_allow_html=True)
render_category_tabs()

# Handle situation tile click
pending = st.session_state.pop("pending_sit", None)

# Determine what to search
search_query = search_cat = None
if manual_query:
    search_query = manual_query
    search_cat   = manual_cat or "general"
elif pending:
    search_query = pending["query"]
    search_cat   = pending.get("category", "general")

# Run search
if search_query:
    data = run_search(search_query, search_cat)
    if data and data.get("success"):
        st.session_state["search_results"] = data
        st.session_state["last_query"]     = search_query
        h = st.session_state["search_history"]
        if search_query not in h:
            h.append(search_query)
        st.session_state["search_history"] = h[-10:]
        st.rerun()
    elif data:
        st.markdown(
f"""<div style="margin:12px 5%;background:rgba(212,175,55,0.06);border:1px solid rgba(212,175,55,0.2);border-radius:12px;padding:16px 20px;">
<div style="color:#D4AF37;font-size:14px;font-weight:600;">No relevant cases found for this search.</div>
<div style="color:#8E8E93;font-size:13px;margin-top:4px;">Try different words or click one of the situations below.</div>
</div>""",
            unsafe_allow_html=True)

# Show results or empty state
data = st.session_state.get("search_results")
if data and data.get("results"):
    render_results(data["results"], st.session_state.get("last_query",""), data.get("ik_live", False))
    st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)
    _, mid, _ = st.columns([3, 2, 3])
    with mid:
        if st.button("🔍 Search Again", key="new_search", use_container_width=True):
            st.session_state["search_results"] = None
            st.session_state["last_query"]     = ""
            st.rerun()
else:
    render_empty_state()
    render_how_it_works()
    render_situations()

render_footer()