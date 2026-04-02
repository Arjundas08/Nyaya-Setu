import streamlit as st
import base64, os, math, requests, textwrap

st.set_page_config(
    page_title="Nyaya-Setu | Chamber Records",
    page_icon="📊",
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
# RISK HELPERS
# ════════════════════════════════════════════════════════════
def risk_color(score):
    if score is None: return "#8E8E93"
    s = float(score)
    if s >= 7: return "#EF4444"
    if s >= 4: return "#F59E0B"
    return "#22C55E"

def risk_label(score):
    if score is None: return "Unknown"
    s = float(score)
    if s >= 7: return "High Risk"
    if s >= 4: return "Medium Risk"
    return "Low Risk"

def risk_bg(score):
    if score is None: return "rgba(142,142,147,0.1)"
    s = float(score)
    if s >= 7: return "rgba(239,68,68,0.08)"
    if s >= 4: return "rgba(245,158,11,0.08)"
    return "rgba(34,197,94,0.08)"

def risk_border(score):
    if score is None: return "rgba(142,142,147,0.2)"
    s = float(score)
    if s >= 7: return "rgba(239,68,68,0.3)"
    if s >= 4: return "rgba(245,158,11,0.3)"
    return "rgba(34,197,94,0.3)"


# ════════════════════════════════════════════════════════════
# MINI GAUGE SVG — compact version for history cards
# ════════════════════════════════════════════════════════════
def mini_gauge(score: float) -> str:
    r      = 34
    cx, cy = 44, 44
    semi   = round(math.pi * r, 2)
    clamped = max(0, min(10, float(score)))
    fill   = round(semi * clamped / 10, 2)
    offset = round(semi - fill, 2)
    color  = risk_color(score)
    lx, ly = cx - r, cy
    rx, ry = cx + r, cy
    return (
        f'<svg width="88" height="52" viewBox="0 0 88 52" xmlns="http://www.w3.org/2000/svg">'
        f'<path d="M {lx},{ly} A {r},{r} 0 0 1 {rx},{ry}" fill="none" '
        f'stroke="rgba(255,255,255,0.06)" stroke-width="8" stroke-linecap="round"/>'
        f'<path d="M {lx},{ly} A {r},{r} 0 0 1 {rx},{ry}" fill="none" '
        f'stroke="{color}" stroke-width="8" stroke-linecap="round" '
        f'stroke-dasharray="{semi} {semi}" stroke-dashoffset="{offset}"/>'
        f'<text x="{cx}" y="{cy - 2}" text-anchor="middle" fill="{color}" '
        f'font-size="14" font-weight="800" font-family="Plus Jakarta Sans,sans-serif">{clamped:.1f}</text>'
        f'<text x="{cx}" y="{cy + 12}" text-anchor="middle" fill="#8E8E93" '
        f'font-size="7" letter-spacing="1" font-family="Plus Jakarta Sans,sans-serif">/ 10</text>'
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
.stButton>button{{background:transparent!important;border:1px solid rgba(212,175,55,0.35)!important;color:#D4AF37!important;border-radius:50px!important;padding:8px 22px!important;font-weight:600!important;letter-spacing:1px!important;font-size:12px!important;transition:0.3s!important;font-family:'Plus Jakarta Sans',sans-serif!important;}}
.stButton>button:hover{{background:#D4AF37!important;color:#000!important;box-shadow:0 0 20px rgba(212,175,55,0.4)!important;}}
@keyframes fadein{{from{{opacity:0;transform:translateY(14px);}}to{{opacity:1;transform:translateY(0);}}}}
@keyframes countup{{from{{opacity:0;transform:scale(0.8);}}to{{opacity:1;transform:scale(1);}}}}

/* ══ MOBILE RESPONSIVE ══ */
@media (max-width: 768px) {{
    h1 {{ font-size: 32px !important; }}
    .stButton>button {{ padding: 14px 20px !important; min-height: 48px !important; }}
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
"""<div style="text-align:center;padding:52px 5% 24px;position:relative;overflow:hidden;">
<div style="position:absolute;top:0;left:50%;transform:translateX(-50%);width:800px;height:320px;pointer-events:none;background:radial-gradient(ellipse at 50% 0%,rgba(212,175,55,0.07) 0%,transparent 70%);"></div>
<div style="font-size:11px;color:#FF7722;letter-spacing:6px;text-transform:uppercase;margin-bottom:14px;">Chamber Records</div>
<h1 style="font-family:'Playfair Display',serif;font-size:50px;margin:0 0 10px;line-height:1.1;background:linear-gradient(to bottom,#FFFFFF 20%,#D4AF37 100%);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">Your Legal History.<br/>Every Document. Every Analysis.</h1>
<p style="font-size:15px;color:#8E8E93;max-width:560px;margin:16px auto 0;line-height:1.8;">All your past document analyses — risk scores, clause breakdowns, and action history — saved permanently so you never lose your legal record.</p>
</div>""",
        unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════
# GLOBAL STATS CARDS — top 4 numbers
# ════════════════════════════════════════════════════════════
def render_stats_cards(stats: dict, history: list):
    total     = stats.get("total_analyses", len(history))
    high_risk = stats.get("high_risk_count", sum(1 for a in history if float(a.get("risk_score") or 0) >= 7))
    avg_score = stats.get("avg_risk_score", 0)
    if not avg_score and history:
        scores    = [float(a.get("risk_score") or 0) for a in history if a.get("risk_score")]
        avg_score = round(sum(scores) / len(scores), 1) if scores else 0

    # Safe documents
    safe = total - high_risk

    cards = [
        {
            "value":    str(total),
            "label":    "Documents Analysed",
            "sub":      "Total contracts reviewed",
            "icon":     "📄",
            "color":    "#D4AF37",
        },
        {
            "value":    str(high_risk),
            "label":    "High Risk Found",
            "sub":      "Documents scored 7+/10",
            "icon":     "⚠️",
            "color":    "#EF4444",
        },
        {
            "value":    str(safe),
            "label":    "Low / Safe",
            "sub":      "Documents under risk score 4",
            "icon":     "✅",
            "color":    "#22C55E",
        },
        {
            "value":    f"{avg_score}/10",
            "label":    "Average Risk Score",
            "sub":      "Across all your documents",
            "icon":     "📊",
            "color":    risk_color(avg_score),
        },
    ]

    st.markdown(
"""<div style="padding:0 5% 8px;">
<div style="font-size:11px;color:#D4AF37;letter-spacing:4px;text-transform:uppercase;margin-bottom:16px;">Your Legal Stats</div>
</div>""",
        unsafe_allow_html=True)

    cols = st.columns(4, gap="small")
    for i, card in enumerate(cards):
        c = card["color"]
        with cols[i]:
            st.markdown(
f"""<div style="background:rgba(10,10,20,0.92);border:1px solid rgba({_rgb(c)},0.25);border-radius:18px;padding:22px 20px;text-align:center;animation:fadein 0.4s ease {i*0.08:.2f}s both;">
<div style="font-size:28px;margin-bottom:10px;">{card['icon']}</div>
<div style="font-size:32px;font-weight:800;color:{c};font-family:'Playfair Display',serif;line-height:1;margin-bottom:6px;animation:countup 0.5s ease both;">{card['value']}</div>
<div style="font-size:13px;font-weight:700;color:#F5F5F7;margin-bottom:4px;">{card['label']}</div>
<div style="font-size:11px;color:#8E8E93;">{card['sub']}</div>
</div>""",
                unsafe_allow_html=True)


def _rgb(hex_color: str) -> str:
    h = hex_color.lstrip("#")
    try:
        return f"{int(h[0:2],16)},{int(h[2:4],16)},{int(h[4:6],16)}"
    except Exception:
        return "212,175,55"


# ════════════════════════════════════════════════════════════
# RISK DISTRIBUTION BAR — visual breakdown
# ════════════════════════════════════════════════════════════
def render_risk_distribution(history: list):
    if not history:
        return

    high   = sum(1 for a in history if float(a.get("risk_score") or 0) >= 7)
    medium = sum(1 for a in history if 4 <= float(a.get("risk_score") or 0) < 7)
    low    = sum(1 for a in history if float(a.get("risk_score") or 0) < 4)
    total  = len(history)
    if not total:
        return

    hp = round(high   / total * 100)
    mp = round(medium / total * 100)
    lp = round(low    / total * 100)

    st.markdown("<div style='height:20px;'></div>", unsafe_allow_html=True)
    st.markdown(
"""<div style="padding:0 5% 8px;">
<div style="font-size:11px;color:#D4AF37;letter-spacing:4px;text-transform:uppercase;margin-bottom:16px;">Risk Distribution</div>
</div>""",
        unsafe_allow_html=True)

    # Build bar segments only for non-zero values
    segments = ""
    if hp:
        segments += f'<div style="width:{hp}%;background:#EF4444;height:100%;border-radius:{"8px 0 0 8px" if not mp and not lp else "8px 0 0 8px" if not segments else "0"};"></div>'
    if mp:
        r = "0 8px 8px 0" if not lp else "0"
        l = "8px 0 0 8px" if not hp else "0"
        segments += f'<div style="width:{mp}%;background:#F59E0B;height:100%;border-radius:{l if not hp else "0"} {r};"></div>'
    if lp:
        l = "8px 0 0 8px" if not hp and not mp else "0"
        segments += f'<div style="width:{lp}%;background:#22C55E;height:100%;border-radius:{l} 8px 8px 0;"></div>'

    st.markdown(
f"""<div style="margin:0 5% 20px;">
<div style="display:flex;height:16px;border-radius:8px;overflow:hidden;background:rgba(255,255,255,0.05);gap:2px;">
{segments if segments else '<div style="width:100%;background:rgba(255,255,255,0.05);border-radius:8px;"></div>'}
</div>
<div style="display:flex;gap:20px;margin-top:10px;flex-wrap:wrap;">
<span style="font-size:12px;color:#EF4444;">■ High Risk: {high} ({hp}%)</span>
<span style="font-size:12px;color:#F59E0B;">■ Medium Risk: {medium} ({mp}%)</span>
<span style="font-size:12px;color:#22C55E;">■ Low Risk / Safe: {low} ({lp}%)</span>
</div>
</div>""",
        unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════
# ANALYSIS HISTORY CARDS
# ════════════════════════════════════════════════════════════
def render_history(history: list, selected_session: str | None):
    if not history:
        st.markdown(
"""<div style="margin:0 5%;background:rgba(212,175,55,0.04);border:1px solid rgba(212,175,55,0.15);border-radius:16px;padding:40px;text-align:center;">
<div style="font-size:40px;margin-bottom:16px;">📭</div>
<div style="font-size:16px;font-weight:700;color:#F5F5F7;font-family:'Playfair Display',serif;margin-bottom:8px;">No analyses yet</div>
<div style="font-size:13px;color:#8E8E93;max-width:360px;margin:0 auto 20px;line-height:1.7;">Upload a contract on the Witness Stand page to start building your legal record.</div>
</div>""",
            unsafe_allow_html=True)
        _, mid, _ = st.columns([2, 2, 2])
        with mid:
            if st.button("📄  Analyse a Document", key="go_upload", use_container_width=True):
                st.switch_page("pages/2_upload.py")
        return

    st.markdown(
"""<div style="padding:0 5% 16px;">
<div style="font-size:11px;color:#D4AF37;letter-spacing:4px;text-transform:uppercase;margin-bottom:4px;">Analysis History</div>
<div style="font-size:12px;color:#8E8E93;">Click any document to view its full analysis</div>
</div>""",
        unsafe_allow_html=True)

    for i, a in enumerate(history):
        sid        = a.get("session_id", "")
        filename   = a.get("filename",  "Unknown Document")
        ftype      = a.get("file_type", "").upper()
        score      = a.get("risk_score")
        level      = a.get("risk_level", "Unknown")
        n_clauses  = a.get("clause_count", 0)
        n_high     = a.get("high_risk_count", 0)
        concerns   = a.get("top_concerns", [])
        created    = a.get("created_at", "")[:16].replace("T", " ") if a.get("created_at") else "—"
        is_sel     = selected_session == sid

        rc   = risk_color(score)
        rbg  = risk_bg(score)
        rb   = risk_border(score)
        rlbl = risk_label(score)
        gauge_html = mini_gauge(float(score)) if score is not None else ""

        # Top concerns as chips
        concern_chips = ""
        for c in concerns[:2]:
            concern_chips += (
                f'<span style="display:inline-block;background:rgba(239,68,68,0.08);'
                f'border:1px solid rgba(239,68,68,0.2);color:#FCA5A5;font-size:11px;'
                f'padding:3px 10px;border-radius:20px;margin:2px;">{str(c)[:50]}</span>'
            )

        border    = f"2px solid {rc}" if is_sel else "1px solid rgba(255,255,255,0.07)"
        bg        = "rgba(15,15,28,0.97)" if is_sel else "rgba(8,8,18,0.92)"
        sel_glow  = f"box-shadow:0 0 24px rgba({_rgb(rc)},0.2);" if is_sel else ""
        delay     = f"{i * 0.07:.2f}s"

        st.markdown(
f"""<div style="margin:0 5% 14px;background:{bg};border:{border};border-radius:18px;padding:20px 24px;{sel_glow}animation:fadein 0.4s ease {delay} both;cursor:pointer;">
<div style="display:flex;justify-content:space-between;align-items:flex-start;gap:16px;flex-wrap:wrap;">
<div style="flex:1;min-width:0;">
<div style="display:flex;align-items:center;gap:10px;margin-bottom:6px;flex-wrap:wrap;">
<span style="font-size:16px;font-weight:700;color:#F5F5F7;">{filename}</span>
{f'<span style="font-size:10px;color:#8E8E93;background:rgba(255,255,255,0.06);padding:2px 8px;border-radius:10px;">{ftype}</span>' if ftype else ''}
</div>
<div style="display:flex;align-items:center;gap:12px;flex-wrap:wrap;margin-bottom:8px;">
<span style="font-size:12px;color:#8E8E93;">🕐 {created}</span>
<span style="font-size:12px;color:#8E8E93;">📋 {n_clauses} clauses</span>
{f'<span style="font-size:12px;color:#F87171;">⚠️ {n_high} high risk</span>' if n_high else ''}
</div>
{f'<div style="margin-top:4px;">{concern_chips}</div>' if concern_chips else ''}
</div>
<div style="display:flex;flex-direction:column;align-items:center;flex-shrink:0;">
{gauge_html}
<div style="font-size:11px;color:{rc};font-weight:700;margin-top:2px;">{rlbl}</div>
</div>
</div>
</div>""",
            unsafe_allow_html=True)

        # Expand button
        btn_col, _ = st.columns([2, 5])
        with btn_col:
            btn_label = "▼ Hide Details" if is_sel else "▶ View Full Analysis"
            if st.button(btn_label, key=f"expand_{sid}_{i}", use_container_width=True):
                if is_sel:
                    st.session_state["selected_session"] = None
                else:
                    st.session_state["selected_session"] = sid
                st.rerun()

        # Expanded details
        if is_sel:
            _render_expanded(sid, a)


# ════════════════════════════════════════════════════════════
# EXPANDED SESSION DETAIL
# ════════════════════════════════════════════════════════════
def _render_expanded(session_id: str, summary: dict):
    """
    Load full session data from backend and display inline.
    """
    try:
        resp = requests.get(f"{API}/dashboard/{session_id}", timeout=10)
        data = resp.json()
    except Exception:
        data = {}

    has_data = data.get("has_data", False)

    if not has_data:
        # Use summary data we already have
        score    = summary.get("risk_score")
        level    = summary.get("risk_level", "Unknown")
        concerns = summary.get("top_concerns", [])
        n_high   = summary.get("high_risk_count", 0)
        n_total  = summary.get("clause_count", 0)
        data = {
            "risk_summary": {
                "score":        score,
                "level":        level,
                "top_concerns": concerns,
            },
            "clauses": {
                "total":     n_total,
                "high_risk": n_high,
            },
        }

    risk    = data.get("risk_summary", {})
    clauses = data.get("clauses", {})
    score   = risk.get("score", summary.get("risk_score", 0))
    level   = risk.get("level", "Unknown")
    concerns = risk.get("top_concerns", [])
    high_details   = clauses.get("high_details", [])
    medium_details = clauses.get("medium_details", [])
    explained      = risk.get("explained_clauses", [])

    rc = risk_color(score)

    # Top concerns
    concerns_html = ""
    if concerns:
        items = "".join(
            f'<div style="display:flex;gap:8px;margin-bottom:8px;align-items:flex-start;">'
            f'<span style="color:#EF4444;flex-shrink:0;">⚠️</span>'
            f'<span style="font-size:13px;color:#E2E8F0;line-height:1.6;">{c}</span>'
            f'</div>'
            for c in concerns
        )
        concerns_html = (
            f'<div style="background:rgba(239,68,68,0.06);border:1px solid rgba(239,68,68,0.2);'
            f'border-radius:12px;padding:16px 18px;margin-bottom:12px;">'
            f'<div style="font-size:10px;color:#EF4444;font-weight:700;letter-spacing:2px;margin-bottom:10px;">TOP CONCERNS IDENTIFIED</div>'
            f'{items}</div>'
        )

    # High risk clauses
    clause_html = ""
    for clause in (high_details + medium_details)[:6]:
        ctype  = clause.get("clause_type", "clause").replace("_", " ").title()
        clevel = clause.get("risk_level", "medium")
        ctext  = clause.get("text", "")[:120]
        cc     = "#EF4444" if clevel == "high" else "#F59E0B"
        clause_html += (
            f'<div style="background:rgba({_rgb(cc)},0.05);border:1px solid rgba({_rgb(cc)},0.15);'
            f'border-radius:10px;padding:10px 14px;margin-bottom:8px;">'
            f'<div style="display:flex;justify-content:space-between;margin-bottom:4px;">'
            f'<span style="font-size:12px;font-weight:700;color:{cc};">{ctype}</span>'
            f'<span style="font-size:10px;color:{cc};background:rgba({_rgb(cc)},0.12);'
            f'padding:2px 8px;border-radius:10px;">{clevel.upper()}</span>'
            f'</div>'
            f'{"<div style=&quot;font-size:11px;color:#94A3B8;line-height:1.6;&quot;>" + ctext + "...</div>" if ctext else ""}'
            f'</div>'
        )

    # Explained clauses (Upgrade 2)
    explained_html = ""
    for ec in explained[:3]:
        etype  = ec.get("clause_type", "").replace("_", " ").title()
        law    = ec.get("law_citation", "")
        why    = ec.get("why_risky", "")
        rec    = ec.get("recommendation", "")
        sev    = ec.get("severity", 5)
        sev_c  = "#EF4444" if sev >= 8 else "#F59E0B" if sev >= 5 else "#22C55E"
        if etype:
            explained_html += (
                f'<div style="background:rgba(212,175,55,0.04);border:1px solid rgba(212,175,55,0.15);'
                f'border-radius:10px;padding:12px 16px;margin-bottom:8px;">'
                f'<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;">'
                f'<span style="font-size:13px;font-weight:700;color:#F5F5F7;">{etype}</span>'
                f'<span style="font-size:11px;color:{sev_c};font-weight:700;">Severity {sev}/10</span>'
                f'</div>'
                f'{"<div style=&quot;font-size:11px;color:#D4AF37;margin-bottom:4px;&quot;>⚖️ " + law + "</div>" if law else ""}'
                f'{"<div style=&quot;font-size:12px;color:#94A3B8;line-height:1.6;margin-bottom:4px;&quot;>" + why + "</div>" if why else ""}'
                f'{"<div style=&quot;font-size:12px;color:#4ADE80;line-height:1.6;&quot;>💡 " + rec + "</div>" if rec else ""}'
                f'</div>'
            )

    st.markdown(
f"""<div style="margin:0 5% 20px 5%;background:rgba(5,5,15,0.97);border:1px solid rgba(212,175,55,0.15);border-radius:0 0 16px 16px;padding:20px 24px;">
<div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:16px;">
<div style="background:rgba(212,175,55,0.06);border:1px solid rgba(212,175,55,0.15);border-radius:12px;padding:14px 18px;">
<div style="font-size:10px;color:#D4AF37;font-weight:700;letter-spacing:2px;margin-bottom:6px;">RISK SCORE</div>
<div style="font-size:28px;font-weight:800;color:{rc};">{score}/10</div>
<div style="font-size:12px;color:{rc};margin-top:2px;">{level}</div>
</div>
<div style="background:rgba(212,175,55,0.06);border:1px solid rgba(212,175,55,0.15);border-radius:12px;padding:14px 18px;">
<div style="font-size:10px;color:#D4AF37;font-weight:700;letter-spacing:2px;margin-bottom:6px;">CLAUSE BREAKDOWN</div>
<div style="font-size:13px;color:#F5F5F7;">Total: <strong>{clauses.get('total',0)}</strong></div>
<div style="font-size:13px;color:#EF4444;">High Risk: <strong>{clauses.get('high_risk',0)}</strong></div>
<div style="font-size:13px;color:#F59E0B;">Medium Risk: <strong>{clauses.get('medium_risk',0)}</strong></div>
</div>
</div>
{concerns_html}
{"<div style='font-size:10px;color:#D4AF37;font-weight:700;letter-spacing:2px;margin-bottom:10px;'>HIGH RISK CLAUSES</div>" + clause_html if clause_html else ""}
{"<div style='font-size:10px;color:#D4AF37;font-weight:700;letter-spacing:2px;margin-top:12px;margin-bottom:10px;'>EXPLAINED CLAUSES (AI Analysis)</div>" + explained_html if explained_html else ""}
</div>""",
        unsafe_allow_html=True)

    # Action buttons
    c1, c2, c3, _ = st.columns([2, 2, 2, 1])
    with c1:
        if st.button("⚖️  Ask About This Doc", key=f"chat_{session_id}", use_container_width=True):
            st.session_state["session_id"] = session_id
            st.switch_page("pages/1_chat.py")
    with c2:
        if st.button("🔮  Predict Outcome", key=f"predict_{session_id}", use_container_width=True):
            st.switch_page("pages/5_predict.py")
    with c3:
        if st.button("📜  Generate Notice", key=f"gen_{session_id}", use_container_width=True):
            st.switch_page("pages/4_generator.py")


# ════════════════════════════════════════════════════════════
# CURRENT SESSION PANEL
# ════════════════════════════════════════════════════════════
def render_current_session():
    session_id = st.session_state.get("session_id", "default")
    try:
        resp = requests.get(f"{API}/dashboard/{session_id}", timeout=8)
        data = resp.json()
    except Exception:
        return

    if not data.get("has_data"):
        return

    doc   = data.get("document", {})
    risk  = data.get("risk_summary", {})
    score = risk.get("score", 0)
    rc    = risk_color(score)

    st.markdown(
"""<div style="padding:0 5% 8px;">
<div style="font-size:11px;color:#D4AF37;letter-spacing:4px;text-transform:uppercase;margin-bottom:14px;">Current Session</div>
</div>""",
        unsafe_allow_html=True)

    st.markdown(
f"""<div style="margin:0 5% 20px;background:linear-gradient(135deg,rgba(212,175,55,0.08),rgba(212,175,55,0.03));border:1px solid rgba(212,175,55,0.25);border-radius:18px;padding:20px 26px;display:flex;align-items:center;gap:20px;flex-wrap:wrap;">
<div style="font-size:36px;">📄</div>
<div style="flex:1;">
<div style="font-size:16px;font-weight:700;color:#F5F5F7;margin-bottom:4px;">{doc.get('filename','Unknown')}</div>
<div style="font-size:12px;color:#8E8E93;">Uploaded {doc.get('uploaded_at','')[:10]} · {doc.get('char_count',0):,} characters</div>
</div>
<div style="text-align:center;">
<div style="font-size:32px;font-weight:800;color:{rc};">{score}/10</div>
<div style="font-size:12px;color:{rc};font-weight:700;">{risk.get('level','')}</div>
</div>
</div>""",
        unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════
# EMPTY STATE — no MongoDB data
# ════════════════════════════════════════════════════════════
def render_no_mongodb():
    st.markdown(
"""<div style="margin:12px 5% 20px;background:rgba(212,175,55,0.04);border:1px solid rgba(212,175,55,0.15);border-radius:14px;padding:16px 20px;display:flex;align-items:center;gap:12px;">
<span style="font-size:20px;">💾</span>
<div>
<div style="font-size:13px;font-weight:700;color:#D4AF37;margin-bottom:3px;">MongoDB not connected</div>
<div style="font-size:12px;color:#8E8E93;">Add MONGO_URI to your .env file to save analyses permanently across sessions.</div>
</div>
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
"<div style='font-size:11px;color:#8E8E93;letter-spacing:2px;margin-bottom:24px;'>CHAMBER RECORDS</div>",
            unsafe_allow_html=True)
        st.markdown(
"<div style='font-size:11px;color:#D4AF37;letter-spacing:3px;text-transform:uppercase;margin-bottom:12px;'>Navigate</div>",
            unsafe_allow_html=True)
        for icon, label, href in [
            ("🏠","Home","/"),("⚖️","Virtual Advocate","/1_chat"),
            ("📄","Witness Stand","/2_upload"),("🔍","Case Archives","/3_case_search"),
            ("📜","Document Forge","/4_generator"),("🔮","The Oracle","/5_predict"),
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
<span style="font-size:11px;color:#333;letter-spacing:2px;">NYAYA-SETU · CHAMBER RECORDS · INDIA · 2026</span>
</div>""",
        unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════
# MAIN
# ════════════════════════════════════════════════════════════
inject_css()
render_sidebar()
render_header()

# Init state
if "selected_session" not in st.session_state:
    st.session_state["selected_session"] = None

# ── Load data from backend ───────────────────────────────────
history = []
stats   = {}
mongo_ok = False

try:
    r1 = requests.get(f"{API}/dashboard/history/all",  timeout=8)
    r2 = requests.get(f"{API}/dashboard/stats/global", timeout=8)
    h  = r1.json()
    s  = r2.json()
    if h.get("success"):
        history  = h.get("analyses", [])
        mongo_ok = True
    if s.get("success"):
        stats = s
except Exception:
    pass

# ── Refresh button ───────────────────────────────────────────
_, ref_col = st.columns([5, 1])
with ref_col:
    if st.button("🔄 Refresh", key="refresh_btn", use_container_width=True):
        st.rerun()

# ── Current session (if available) ──────────────────────────
render_current_session()

# ── Stats cards ──────────────────────────────────────────────
render_stats_cards(stats, history)

st.markdown("<div style='height:20px;'></div>", unsafe_allow_html=True)

# ── Risk distribution bar ────────────────────────────────────
render_risk_distribution(history)

# ── MongoDB status notice ────────────────────────────────────
if not mongo_ok:
    render_no_mongodb()

# ── History cards ────────────────────────────────────────────
render_history(history, st.session_state.get("selected_session"))

# ── Quick action if no data ──────────────────────────────────
if not history:
    st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)
    c1, c2, _ = st.columns([2, 2, 3])
    with c1:
        if st.button("📄  Upload Document", key="up_btn", use_container_width=True):
            st.switch_page("pages/2_upload.py")
    with c2:
        if st.button("⚖️  Ask a Question", key="chat_btn", use_container_width=True):
            st.switch_page("pages/1_chat.py")

render_footer()