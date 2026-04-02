import streamlit as st
import base64, os, re, textwrap
from datetime import date

st.set_page_config(
    page_title="Nyaya-Setu | Document Forge",
    page_icon="📜",
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
# EMBEDDED TEMPLATES — no backend files needed
# Placeholders use single braces: {variable_name}
# ════════════════════════════════════════════════════════════
TEMPLATE_BODIES = {

"rti_application": (
"TO,\n"
"The Public Information Officer,\n"
"{department}\n"
"\n"
"SUBJECT: Application for Information under Right to Information Act, 2005\n"
"\n"
"Sir/Madam,\n"
"\n"
"I, {applicant_name}, resident of {applicant_address}, hereby request the following\n"
"information under Section 6(1) of the Right to Information Act, 2005:\n"
"\n"
"INFORMATION SOUGHT:\n"
"{information_sought}\n"
"\n"
"I am willing to pay the prescribed fees applicable under the RTI Act, 2005.\n"
"Kindly provide the requested information within 30 days as mandated under Section 7(1).\n"
"\n"
"If the information pertains to the life or liberty of a person, please provide it within\n"
"48 hours as required under the proviso to Section 7(1).\n"
"\n"
"In case the information is held by another Public Authority, please transfer this\n"
"application under Section 6(3) of the Act and inform me accordingly.\n"
"\n"
"Yours faithfully,\n"
"{applicant_name}\n"
"{applicant_address}\n"
"Date: {date}\n"
"\n"
"-----------------------------------------------------------\n"
"Legal Basis  : RTI Act, 2005 — Sections 6(1), 7(1), 8, 19\n"
"First Appeal : To Appellate Authority within 30 days if no response\n"
"Second Appeal: Central/State Information Commission within 90 days\n"
"Filing Fee   : Rs. 10 (Central Govt.) | varies by state\n"
"-----------------------------------------------------------\n"
),

"legal_notice": (
"LEGAL NOTICE\n"
"\n"
"FROM:\n"
"{sender_name}\n"
"{sender_address}\n"
"\n"
"TO:\n"
"{recipient_name}\n"
"{recipient_address}\n"
"\n"
"Date: {date}\n"
"SUBJECT: {subject}\n"
"\n"
"Sir/Madam,\n"
"\n"
"Under instructions from and on behalf of my client {sender_name}, I hereby serve\n"
"upon you this Legal Notice as under:\n"
"\n"
"1. That my client is {sender_name}, residing at {sender_address}.\n"
"\n"
"2. That you are {recipient_name}, having your address at {recipient_address}.\n"
"\n"
"3. FACTS OF THE MATTER:\n"
"   {details}\n"
"\n"
"4. RELIEF SOUGHT:\n"
"   {relief_sought}\n"
"\n"
"5. My client calls upon you to comply with the above within FIFTEEN (15) DAYS from\n"
"   receipt of this notice, failing which my client shall be constrained to initiate\n"
"   appropriate legal proceedings at your cost and risk.\n"
"\n"
"6. This notice is without prejudice to any other rights or remedies available.\n"
"\n"
"Issued on behalf of:\n"
"{sender_name}\n"
"Date: {date}\n"
"\n"
"-----------------------------------------------------------\n"
"Legal Basis  : Indian Contract Act, 1872 — Sections 73, 74\n"
"               Specific Relief Act, 1963 — Section 38\n"
"               Code of Civil Procedure, 1908 — Order 7 Rule 1\n"
"Note         : Send via Registered Post AD. Retain acknowledgement as proof.\n"
"-----------------------------------------------------------\n"
),

"rental_agreement": (
"RENTAL AGREEMENT\n"
"\n"
"This Rental Agreement is made and entered into on {date}\n"
"\n"
"BETWEEN:\n"
"\n"
"LANDLORD:\n"
"{landlord_name}\n"
"{landlord_address}\n"
"(hereinafter referred to as 'the Landlord')\n"
"\n"
"AND\n"
"\n"
"TENANT:\n"
"{tenant_name}\n"
"{tenant_address}\n"
"(hereinafter referred to as 'the Tenant')\n"
"\n"
"WHEREAS the Landlord is the owner of the property situated at:\n"
"{property_address}\n"
"(hereinafter referred to as 'the Premises')\n"
"\n"
"NOW THEREFORE this Agreement witnesseth as follows:\n"
"\n"
"1. LEASE TERM\n"
"   The tenancy shall commence from {lease_start} and end on {lease_end},\n"
"   unless renewed or terminated earlier per the terms herein.\n"
"\n"
"2. RENT\n"
"   The Tenant agrees to pay monthly rent of Rs. {monthly_rent}/- on or before\n"
"   the 5th day of each calendar month.\n"
"\n"
"3. SECURITY DEPOSIT\n"
"   The Tenant has paid a refundable security deposit of Rs. {security_deposit}/- to\n"
"   the Landlord. This shall be refunded within 30 days of vacating, subject to\n"
"   deductions for damages beyond normal wear and tear.\n"
"\n"
"4. PURPOSE OF USE\n"
"   The Tenant shall use the Premises exclusively for residential purposes only.\n"
"\n"
"5. MAINTENANCE\n"
"   The Tenant shall maintain the Premises in good condition and return it in the same\n"
"   state at the end of the tenancy, fair wear and tear excepted.\n"
"\n"
"6. TERMINATION\n"
"   Either party may terminate this agreement by giving ONE MONTH's written notice.\n"
"\n"
"7. SUBLETTING\n"
"   The Tenant shall not sublet or assign the Premises without prior written consent\n"
"   of the Landlord.\n"
"\n"
"8. UTILITIES\n"
"   The Tenant shall be responsible for electricity, water, and other utility bills.\n"
"\n"
"IN WITNESS WHEREOF, the parties have signed this Agreement on the date written above.\n"
"\n"
"LANDLORD                         TENANT\n"
"{landlord_name}                  {tenant_name}\n"
"\n"
"Witness 1: ________________      Witness 2: ________________\n"
"\n"
"-----------------------------------------------------------\n"
"Legal Basis  : Transfer of Property Act, 1882 — Sections 105-111\n"
"               State Rent Control Act (varies by state)\n"
"Note         : Register if lease exceeds 11 months (Registration Act, 1908)\n"
"Stamp Duty   : Pay applicable stamp duty before registration\n"
"-----------------------------------------------------------\n"
),

"consumer_complaint": (
"CONSUMER COMPLAINT\n"
"\n"
"TO,\n"
"The President/Member,\n"
"District Consumer Disputes Redressal Commission\n"
"\n"
"SUBJECT: Complaint against {company_name} under Consumer Protection Act, 2019\n"
"\n"
"COMPLAINANT:\n"
"{complainant_name}\n"
"{complainant_address}\n"
"\n"
"OPPOSITE PARTY:\n"
"{company_name}\n"
"{company_address}\n"
"\n"
"Date: {date}\n"
"\n"
"COMPLAINT PETITION\n"
"\n"
"Respectfully showeth:\n"
"\n"
"1. IDENTITY OF COMPLAINANT\n"
"   The Complainant, {complainant_name}, is a consumer as defined under Section 2(7)\n"
"   of the Consumer Protection Act, 2019, having purchased/availed:\n"
"\n"
"   Product/Service : {product_service}\n"
"   Amount Paid     : Rs. {amount}/-\n"
"\n"
"2. DETAILS OF GRIEVANCE:\n"
"   {complaint_details}\n"
"\n"
"3. LEGAL GROUNDS:\n"
"   The Opposite Party has committed the following under the CPA 2019:\n"
"   a) Deficiency in service as defined under Section 2(11)\n"
"   b) Unfair trade practice as defined under Section 2(47)\n"
"   c) Manufacturing defect / product liability under Section 2(34)\n"
"\n"
"4. RELIEF SOUGHT:\n"
"   a) Replacement of defective product / full refund of Rs. {amount}/-\n"
"   b) Compensation for mental agony and harassment\n"
"   c) Litigation costs\n"
"   d) Any other relief this Commission deems fit\n"
"\n"
"5. DECLARATION:\n"
"   The matter has not been filed before any other court/commission and the cause of\n"
"   action arose within the jurisdiction of this Commission.\n"
"\n"
"Respectfully submitted,\n"
"{complainant_name}\n"
"Date: {date}\n"
"\n"
"-----------------------------------------------------------\n"
"Legal Basis  : Consumer Protection Act, 2019 — Sections 2(7), 35, 36\n"
"Filing Fee   : Rs. 200 (up to Rs. 5 lakh claim)\n"
"Helpline     : 1800-11-4000 (toll-free)\n"
"Online Portal: consumerhelpline.gov.in\n"
"-----------------------------------------------------------\n"
),

"employment_complaint": (
"EMPLOYMENT GRIEVANCE COMPLAINT\n"
"\n"
"TO,\n"
"The Labour Commissioner / Industrial Relations Officer\n"
"[Jurisdictional Labour Office]\n"
"\n"
"SUBJECT: Formal Complaint against {employer_name}\n"
"DATE: {date}\n"
"\n"
"FROM:\n"
"{employee_name}\n"
"{employee_address}\n"
"Designation : {designation}\n"
"Employer    : {employer_name}, {employer_address}\n"
"\n"
"Sir/Madam,\n"
"\n"
"I, {employee_name}, employed as {designation} at {employer_name}, hereby lodge a\n"
"formal complaint under the provisions of applicable Indian labour laws.\n"
"\n"
"1. DETAILS OF COMPLAINT:\n"
"   {complaint_details}\n"
"\n"
"2. RELEVANT LEGAL PROVISIONS:\n"
"   a) Industrial Disputes Act, 1947 — Section 2A (individual disputes)\n"
"   b) Industrial Disputes Act, 1947 — Section 25F (retrenchment compensation)\n"
"   c) Payment of Wages Act, 1936 — Section 3 (responsibility for payment)\n"
"   d) Code on Wages, 2019 — Section 2(y) (wages definition)\n"
"   e) Factories Act, 1948 — if safety/welfare provisions violated\n"
"\n"
"3. RELIEF SOUGHT:\n"
"   a) Investigate this matter and call employer for conciliation proceedings\n"
"   b) Direct employer to pay all dues within 30 days\n"
"   c) Take appropriate action under relevant labour laws\n"
"   d) Issue certificate of service/dues as applicable\n"
"\n"
"4. DOCUMENTS ATTACHED (please tick applicable):\n"
"   [ ] Appointment letter\n"
"   [ ] Pay slips / salary records\n"
"   [ ] Bank statements showing salary credits\n"
"   [ ] Written communication with employer\n"
"   [ ] Termination letter (if applicable)\n"
"\n"
"Yours faithfully,\n"
"{employee_name}\n"
"Date: {date}\n"
"\n"
"-----------------------------------------------------------\n"
"Legal Basis  : Industrial Disputes Act, 1947 — Sections 2A, 25F, 25G\n"
"               Payment of Wages Act, 1936 — Section 15\n"
"Next Steps   : If no response in 60 days, file before Labour Court\n"
"Labour Helpline: 1800-11-5500 (toll-free)\n"
"-----------------------------------------------------------\n"
),
}


# ════════════════════════════════════════════════════════════
# TEMPLATE CATALOGUE
# ════════════════════════════════════════════════════════════
TEMPLATES = {
    "rti_application": {
        "label":   "RTI Application",
        "icon":    "📋",
        "tagline": "Right to Information Act, 2005",
        "desc":    "Request information from any government office.",
        "color":   "#D4AF37",
        "fields": [
            {"key": "applicant_name",     "label": "Your Full Name",              "type": "text", "placeholder": "e.g. Arjun Kumar"},
            {"key": "applicant_address",  "label": "Your Address",                "type": "area", "placeholder": "Full postal address with pin code"},
            {"key": "department",         "label": "Department / Office",         "type": "text", "placeholder": "e.g. Municipal Corporation, Delhi"},
            {"key": "pio_name",           "label": "PIO Name (optional)",         "type": "text", "placeholder": "e.g. Shri Ramesh Sharma"},
            {"key": "information_sought", "label": "Information You Are Seeking", "type": "area", "placeholder": "Describe clearly what information you need"},
            {"key": "date",               "label": "Date",                        "type": "date", "placeholder": ""},
        ],
    },
    "legal_notice": {
        "label":   "Legal Notice",
        "icon":    "⚖️",
        "tagline": "Indian Contract Act, 1872",
        "desc":    "Send a formal notice before filing a court case.",
        "color":   "#FF7722",
        "fields": [
            {"key": "sender_name",       "label": "Your Full Name",              "type": "text", "placeholder": "e.g. Priya Reddy"},
            {"key": "sender_address",    "label": "Your Address",                "type": "area", "placeholder": "Full postal address"},
            {"key": "recipient_name",    "label": "Recipient's Name",            "type": "text", "placeholder": "e.g. ABC Builders Pvt Ltd"},
            {"key": "recipient_address", "label": "Recipient's Address",         "type": "area", "placeholder": "Full postal address"},
            {"key": "subject",           "label": "Subject / Matter",            "type": "text", "placeholder": "e.g. Non-payment of dues worth Rs. 50,000"},
            {"key": "details",           "label": "Details of Grievance",        "type": "area", "placeholder": "Describe the issue clearly with dates and amounts"},
            {"key": "relief_sought",     "label": "Relief / Action Requested",   "type": "area", "placeholder": "What do you want the recipient to do?"},
            {"key": "date",              "label": "Date",                        "type": "date", "placeholder": ""},
        ],
    },
    "rental_agreement": {
        "label":   "Rental Agreement",
        "icon":    "🏠",
        "tagline": "Transfer of Property Act, 1882",
        "desc":    "Draft a rental agreement between landlord and tenant.",
        "color":   "#22C55E",
        "fields": [
            {"key": "landlord_name",    "label": "Landlord's Full Name",         "type": "text", "placeholder": "e.g. Suresh Patel"},
            {"key": "landlord_address", "label": "Landlord's Address",           "type": "area", "placeholder": "Full postal address"},
            {"key": "tenant_name",      "label": "Tenant's Full Name",           "type": "text", "placeholder": "e.g. Meera Joshi"},
            {"key": "tenant_address",   "label": "Tenant's Permanent Address",   "type": "area", "placeholder": "Permanent address of tenant"},
            {"key": "property_address", "label": "Rental Property Address",      "type": "area", "placeholder": "Full address of the property being rented"},
            {"key": "monthly_rent",     "label": "Monthly Rent (Rs.)",           "type": "text", "placeholder": "e.g. 15000"},
            {"key": "security_deposit", "label": "Security Deposit (Rs.)",       "type": "text", "placeholder": "e.g. 45000"},
            {"key": "lease_start",      "label": "Lease Start Date",             "type": "date", "placeholder": ""},
            {"key": "lease_end",        "label": "Lease End Date",               "type": "date", "placeholder": ""},
            {"key": "date",             "label": "Agreement Date",               "type": "date", "placeholder": ""},
        ],
    },
    "consumer_complaint": {
        "label":   "Consumer Complaint",
        "icon":    "🛒",
        "tagline": "Consumer Protection Act, 2019",
        "desc":    "File a complaint against a company or service.",
        "color":   "#A855F7",
        "fields": [
            {"key": "complainant_name",    "label": "Your Full Name",            "type": "text", "placeholder": "e.g. Kavya Singh"},
            {"key": "complainant_address", "label": "Your Address",              "type": "area", "placeholder": "Full postal address"},
            {"key": "company_name",        "label": "Company / Brand Name",      "type": "text", "placeholder": "e.g. XYZ Electronics"},
            {"key": "company_address",     "label": "Company Address",           "type": "area", "placeholder": "Registered office address"},
            {"key": "product_service",     "label": "Product / Service",         "type": "text", "placeholder": "e.g. Refrigerator Model X200"},
            {"key": "amount",              "label": "Amount Paid (Rs.)",         "type": "text", "placeholder": "e.g. 28500"},
            {"key": "complaint_details",   "label": "Complaint Details",         "type": "area", "placeholder": "Describe the defect/issue clearly with dates"},
            {"key": "date",                "label": "Date",                      "type": "date", "placeholder": ""},
        ],
    },
    "employment_complaint": {
        "label":   "Employment Complaint",
        "icon":    "💼",
        "tagline": "Industrial Disputes Act, 1947",
        "desc":    "Raise a grievance about unfair treatment at work.",
        "color":   "#0EA5E9",
        "fields": [
            {"key": "employee_name",     "label": "Your Full Name",              "type": "text", "placeholder": "e.g. Raj Sharma"},
            {"key": "employee_address",  "label": "Your Address",               "type": "area", "placeholder": "Full postal address"},
            {"key": "employer_name",     "label": "Employer / Company Name",    "type": "text", "placeholder": "e.g. Tech Solutions Pvt Ltd"},
            {"key": "employer_address",  "label": "Employer's Address",         "type": "area", "placeholder": "Office / registered address"},
            {"key": "designation",       "label": "Your Designation / Role",    "type": "text", "placeholder": "e.g. Software Engineer"},
            {"key": "complaint_details", "label": "Details of Your Complaint",  "type": "area", "placeholder": "Describe — unpaid salary, wrongful termination, harassment, etc."},
            {"key": "date",              "label": "Date",                       "type": "date", "placeholder": ""},
        ],
    },
}


# ════════════════════════════════════════════════════════════
# LOCAL DOCUMENT GENERATION — instant, no backend needed
# ════════════════════════════════════════════════════════════
def generate_document_local(tmpl_key: str, values: dict) -> str:
    template = TEMPLATE_BODIES.get(tmpl_key, "")
    doc = template
    for key, val in values.items():
        doc = doc.replace("{" + key + "}", str(val).strip() if val else f"[{key.upper()}]")
    # Replace any remaining unfilled placeholders
    doc = re.sub(r"\{[a-z_]+\}", "[NOT PROVIDED]", doc)
    return doc


# ════════════════════════════════════════════════════════════
# CSS
# ════════════════════════════════════════════════════════════
def inject_css():
    bg_rule = (
        f"background-image:linear-gradient(rgba(3,3,5,0.93),rgba(3,3,5,0.99)),"
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
.stButton>button{{background:transparent!important;border:1px solid #D4AF37!important;color:#D4AF37!important;border-radius:50px!important;padding:10px 24px!important;font-weight:600!important;letter-spacing:1px!important;font-size:13px!important;transition:0.3s!important;font-family:'Plus Jakarta Sans',sans-serif!important;}}
.stButton>button:hover{{background:#D4AF37!important;color:#000!important;box-shadow:0 0 20px rgba(212,175,55,0.4)!important;}}
.stDownloadButton>button{{background:linear-gradient(135deg,#D4AF37,#FF7722)!important;border:none!important;color:#030305!important;border-radius:50px!important;padding:12px 28px!important;font-weight:700!important;letter-spacing:1px!important;font-size:14px!important;width:100%!important;transition:0.3s!important;font-family:'Plus Jakarta Sans',sans-serif!important;}}
.stDownloadButton>button:hover{{transform:scale(1.03)!important;box-shadow:0 0 30px rgba(212,175,55,0.5)!important;}}
[data-testid="stTextInput"]>div>div>input{{background:rgba(18,18,28,0.9)!important;border:1px solid rgba(212,175,55,0.2)!important;border-radius:12px!important;color:#F5F5F7!important;padding:10px 16px!important;font-size:14px!important;}}
[data-testid="stTextInput"]>div>div>input:focus{{border-color:#D4AF37!important;box-shadow:0 0 15px rgba(212,175,55,0.12)!important;}}
[data-testid="stTextArea"]>div>div>textarea{{background:rgba(18,18,28,0.9)!important;border:1px solid rgba(212,175,55,0.2)!important;border-radius:12px!important;color:#F5F5F7!important;font-size:14px!important;}}
[data-testid="stTextArea"]>div>div>textarea:focus{{border-color:#D4AF37!important;box-shadow:0 0 15px rgba(212,175,55,0.12)!important;}}
[data-testid="stDateInput"]>div>div>input{{background:rgba(18,18,28,0.9)!important;border:1px solid rgba(212,175,55,0.2)!important;border-radius:12px!important;color:#F5F5F7!important;}}
@keyframes fadein{{from{{opacity:0;transform:translateY(12px);}}to{{opacity:1;transform:translateY(0);}}}}

/* ══ MOBILE RESPONSIVE ══ */
@media (max-width: 768px) {{
    h1 {{ font-size: 32px !important; }}
    .stButton>button {{ padding: 14px 20px !important; min-height: 48px !important; }}
    .stDownloadButton>button {{ padding: 14px 20px !important; min-height: 48px !important; }}
    [data-testid="stTextInput"]>div>div>input {{ font-size: 16px !important; padding: 12px !important; }}
    [data-testid="stTextArea"]>div>div>textarea {{ font-size: 16px !important; min-height: 120px !important; }}
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
"""<div style="text-align:center;padding:56px 5% 28px;position:relative;overflow:hidden;">
<div style="position:absolute;top:0;left:50%;transform:translateX(-50%);width:700px;height:300px;pointer-events:none;background:radial-gradient(ellipse at 50% 0%,rgba(212,175,55,0.07) 0%,transparent 70%);"></div>
<div style="font-size:11px;color:#FF7722;letter-spacing:6px;text-transform:uppercase;margin-bottom:14px;">The Document Forge</div>
<h1 style="font-family:'Playfair Display',serif;font-size:52px;margin:0 0 10px;line-height:1.1;background:linear-gradient(to bottom,#FFFFFF 30%,#D4AF37 100%);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">Generate Legal Documents.<br/>In Minutes. For Free.</h1>
<p style="font-size:16px;color:#8E8E93;max-width:580px;margin:16px auto 0;line-height:1.75;">Choose a template, fill in your details, download instantly. Grounded in Indian law.</p>
</div>""",
        unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════
# TEMPLATE SELECTOR CARDS
# ════════════════════════════════════════════════════════════
def render_template_selector():
    st.markdown(
"""<div style="padding:0 5% 8px;">
<div style="font-size:11px;color:#D4AF37;letter-spacing:4px;text-transform:uppercase;margin-bottom:20px;">Step 1 — Choose Your Document</div>
</div>""",
        unsafe_allow_html=True)

    cols    = st.columns(5, gap="small")
    selected = st.session_state.get("selected_template", None)

    for i, (key, tmpl) in enumerate(TEMPLATES.items()):
        is_sel = selected == key
        border = f"2px solid {tmpl['color']}" if is_sel else "1px solid rgba(212,175,55,0.15)"
        bg     = "rgba(20,20,30,0.95)" if is_sel else "rgba(12,12,18,0.7)"
        glow   = f"box-shadow:0 0 24px {tmpl['color']}33;" if is_sel else ""
        tick   = f'<div style="position:absolute;top:10px;right:12px;color:{tmpl["color"]};font-size:16px;font-weight:700;">✓</div>' if is_sel else ""
        with cols[i]:
            st.markdown(
f"""<div style="position:relative;background:{bg};border:{border};border-radius:16px;padding:20px 14px 16px;text-align:center;{glow}transition:0.3s;min-height:148px;">
{tick}
<div style="font-size:28px;margin-bottom:10px;">{tmpl['icon']}</div>
<div style="font-size:13px;font-weight:700;color:#F5F5F7;margin-bottom:4px;">{tmpl['label']}</div>
<div style="font-size:10px;color:{tmpl['color']};letter-spacing:0.5px;margin-bottom:8px;">{tmpl['tagline']}</div>
<div style="font-size:11px;color:#8E8E93;line-height:1.5;">{tmpl['desc']}</div>
</div>""",
                unsafe_allow_html=True)
            btn_label = "✓ Selected" if is_sel else "Select"
            if st.button(btn_label, key=f"sel_{key}", use_container_width=True):
                st.session_state["selected_template"] = key
                st.session_state["generated_doc"]     = None
                st.rerun()


# ════════════════════════════════════════════════════════════
# DOCUMENT FORM
# ════════════════════════════════════════════════════════════
def render_form(tmpl_key: str) -> dict:
    tmpl   = TEMPLATES[tmpl_key]
    color  = tmpl["color"]
    fields = tmpl["fields"]

    st.markdown("<div style='height:28px;'></div>", unsafe_allow_html=True)
    st.markdown(
f"""<div style="padding:0 5% 16px;">
<div style="font-size:11px;color:#D4AF37;letter-spacing:4px;text-transform:uppercase;margin-bottom:6px;">Step 2 — Fill In Your Details</div>
<div style="font-size:24px;font-weight:700;color:#F5F5F7;font-family:'Playfair Display',serif;">{tmpl['icon']} {tmpl['label']}</div>
<div style="font-size:12px;color:{color};margin-top:4px;letter-spacing:0.5px;">{tmpl['tagline']}</div>
</div>""",
        unsafe_allow_html=True)
    st.markdown(
f"""<div style="margin:0 5% 28px;height:1px;background:linear-gradient(to right,{color}66,transparent);"></div>""",
        unsafe_allow_html=True)

    half     = len(fields) // 2 + len(fields) % 2
    l_fields = fields[:half]
    r_fields = fields[half:]

    left, _, right = st.columns([5, 1, 5])
    values = {}
    today  = date.today()

    def draw_field(col, f):
        with col:
            st.markdown(
f"<div style='margin-bottom:4px;font-size:12px;color:#A1A1AA;font-weight:600;letter-spacing:0.5px;'>{f['label']}</div>",
                unsafe_allow_html=True)
            wkey = f"fg_{tmpl_key}_{f['key']}"
            if f["type"] == "text":
                val = st.text_input(f["label"], placeholder=f["placeholder"], key=wkey, label_visibility="collapsed")
            elif f["type"] == "area":
                val = st.text_area(f["label"], placeholder=f["placeholder"], key=wkey, height=90, label_visibility="collapsed")
            elif f["type"] == "date":
                d   = st.date_input(f["label"], value=today, key=wkey, label_visibility="collapsed")
                val = str(d)
            else:
                val = ""
            st.markdown("<div style='margin-bottom:14px;'></div>", unsafe_allow_html=True)
        return val

    for f in l_fields:
        values[f["key"]] = draw_field(left, f)
    for f in r_fields:
        values[f["key"]] = draw_field(right, f)

    return values


# ════════════════════════════════════════════════════════════
# GENERATE BUTTON — full width, outside narrow columns
# ════════════════════════════════════════════════════════════
def render_generate_button(tmpl_key: str, values: dict):
    tmpl  = TEMPLATES[tmpl_key]
    color = tmpl["color"]

    st.markdown(
f"""<div style="margin:8px 5% 24px;height:1px;background:linear-gradient(to right,{color}44,transparent);"></div>""",
        unsafe_allow_html=True)
    st.markdown(
"""<div style="padding:0 5%;margin-bottom:16px;">
<div style="font-size:11px;color:#D4AF37;letter-spacing:4px;text-transform:uppercase;">Step 3 — Generate &amp; Download</div>
</div>""",
        unsafe_allow_html=True)

    # Button in a reasonable-width column so it isn't full screen wide
    bcol, _ = st.columns([3, 4])
    with bcol:
        clicked = st.button(f"⚡  Generate {tmpl['label']}", key="gen_btn", use_container_width=True)

    # Handle click OUTSIDE the column — errors/success render full width, visible
    if clicked:
        missing = [
            f["label"] for f in tmpl["fields"]
            if f["type"] in ("text", "area") and not str(values.get(f["key"], "")).strip()
        ]
        if missing:
            st.markdown(
f"""<div style="margin:12px 5%;background:rgba(220,38,38,0.15);border:1px solid rgba(220,38,38,0.4);border-radius:12px;padding:16px 20px;">
<div style="color:#F87171;font-size:14px;font-weight:700;margin-bottom:6px;">⚠️ Please fill in the following fields:</div>
<div style="color:#FCA5A5;font-size:13px;">{' · '.join(missing)}</div>
</div>""",
                unsafe_allow_html=True)
            return

        # ── Generate locally — instant, no backend, never fails ──
        doc = generate_document_local(tmpl_key, values)

        if doc:
            st.session_state["generated_doc"]   = doc
            st.session_state["generated_title"] = tmpl["label"]
            st.session_state["generated_key"]   = tmpl_key
            st.rerun()
        else:
            st.markdown(
"""<div style="margin:12px 5%;background:rgba(220,38,38,0.15);border:1px solid rgba(220,38,38,0.4);border-radius:12px;padding:16px 20px;">
<div style="color:#F87171;font-size:14px;font-weight:700;">Template not found. Please try again.</div>
</div>""",
                unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════
# DOCUMENT VIEWER + DOWNLOAD
# ════════════════════════════════════════════════════════════
def render_document_output():
    doc   = st.session_state.get("generated_doc", "")
    title = st.session_state.get("generated_title", "Legal Document")
    key   = st.session_state.get("generated_key", "")
    if not doc:
        return

    tmpl  = TEMPLATES.get(key, {})
    color = tmpl.get("color", "#D4AF37")
    icon  = tmpl.get("icon", "📄")

    st.markdown("<div style='height:24px;'></div>", unsafe_allow_html=True)

    # ── Success banner ──────────────────────────────────────
    st.markdown(
f"""<div style="margin:0 5% 24px;background:linear-gradient(135deg,rgba(10,25,10,0.95),rgba(8,18,8,0.95));border:1px solid rgba(34,197,94,0.4);border-radius:16px;padding:18px 26px;display:flex;align-items:center;gap:16px;">
<div style="font-size:36px;">{icon}</div>
<div style="flex:1;">
<div style="font-size:15px;font-weight:700;color:#4ADE80;margin-bottom:3px;">Document Generated Successfully</div>
<div style="font-size:12px;color:#8E8E93;">{title} &nbsp;·&nbsp; {len(doc):,} characters &nbsp;·&nbsp; Ready to download</div>
</div>
<div style="font-size:28px;">✅</div>
</div>""",
        unsafe_allow_html=True)

    # ── Download + New — prominent, outside any narrow column ──
    st.markdown(
"""<div style="padding:0 5%;margin-bottom:8px;">
<div style="font-size:11px;color:#D4AF37;letter-spacing:4px;text-transform:uppercase;margin-bottom:14px;">Download Your Document</div>
</div>""",
        unsafe_allow_html=True)

    dl_col, new_col, _ = st.columns([2, 2, 3])
    filename = f"{key}_{date.today().strftime('%Y%m%d')}.txt"

    with dl_col:
        st.download_button(
            label="⬇  Download (.txt)",
            data=doc,
            file_name=filename,
            mime="text/plain",
            use_container_width=True,
            key="dl_btn",
        )
    with new_col:
        if st.button("🔄  New Document", use_container_width=True, key="new_btn"):
            st.session_state["generated_doc"]     = None
            st.session_state["generated_title"]   = None
            st.session_state["selected_template"] = None
            st.rerun()

    st.markdown("<div style='height:24px;'></div>", unsafe_allow_html=True)

    # ── Preview label ───────────────────────────────────────
    st.markdown(
"""<div style="padding:0 5% 10px;">
<div style="font-size:11px;color:#D4AF37;letter-spacing:4px;text-transform:uppercase;">Document Preview</div>
</div>""",
        unsafe_allow_html=True)

    # ── Terminal-style header bar ───────────────────────────
    st.markdown(
"""<div style="margin:0 5%;background:rgba(8,8,16,0.95);border:1px solid rgba(212,175,55,0.2);border-radius:16px 16px 0 0;padding:12px 20px;display:flex;align-items:center;gap:10px;border-bottom:none;">
<div style="width:11px;height:11px;background:#D4AF37;border-radius:50%;"></div>
<div style="width:11px;height:11px;background:rgba(212,175,55,0.4);border-radius:50%;"></div>
<div style="width:11px;height:11px;background:rgba(212,175,55,0.15);border-radius:50%;"></div>
<span style="font-size:11px;color:#8E8E93;margin-left:8px;letter-spacing:2px;text-transform:uppercase;">Document Preview — Review Before Submitting</span>
</div>""",
        unsafe_allow_html=True)

    # st.code = safest renderer — never interprets leading spaces as code blocks
    with st.container():
        st.code(doc, language="")

    st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)
    st.markdown(
"""<div style="margin:0 5%;background:rgba(255,119,34,0.06);border:1px solid rgba(255,119,34,0.2);border-radius:12px;padding:14px 20px;text-align:center;">
<span style="font-size:13px;color:#8E8E93;">⚠️ <strong style="color:#FF7722;">Important:</strong> Review this document carefully before submitting. For complex legal matters, consult a licensed advocate.</span>
</div>""",
        unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════
# EMPTY STATE
# ════════════════════════════════════════════════════════════
def render_empty_state():
    st.markdown(
"""<div style="text-align:center;padding:48px 5%;animation:fadein 0.6s ease;">
<div style="font-size:60px;margin-bottom:20px;">⚒️</div>
<div style="font-size:20px;font-weight:700;color:#F5F5F7;font-family:'Playfair Display',serif;margin-bottom:10px;">Select a template above to begin</div>
<div style="font-size:14px;color:#8E8E93;max-width:420px;margin:0 auto;line-height:1.75;">Each template is pre-filled with the correct Indian legal format. Just fill in your details and download.</div>
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
"""<div style="font-family:'Playfair Display',serif;font-size:20px;color:#D4AF37;margin-bottom:2px;">Nyaya-Setu</div>""",
            unsafe_allow_html=True)
        st.markdown(
"""<div style="font-size:11px;color:#8E8E93;letter-spacing:2px;margin-bottom:24px;">THE DOCUMENT FORGE</div>""",
            unsafe_allow_html=True)
        st.markdown(
"""<div style="font-size:11px;color:#D4AF37;letter-spacing:3px;text-transform:uppercase;margin-bottom:12px;">Templates</div>""",
            unsafe_allow_html=True)
        for k, t in TEMPLATES.items():
            is_sel = st.session_state.get("selected_template") == k
            st.markdown(
f"""<div style="padding:8px 12px;border-radius:8px;margin-bottom:4px;background:{'rgba(20,20,30,0.9)' if is_sel else 'transparent'};border:{'1px solid '+t['color']+'44' if is_sel else '1px solid transparent'};">
<span style="font-size:15px;">{t['icon']}</span>
<span style="font-size:12px;color:{'#F5F5F7' if is_sel else '#8E8E93'};margin-left:8px;">{t['label']}</span>
</div>""",
                unsafe_allow_html=True)
        st.markdown("<div style='height:20px;'></div>", unsafe_allow_html=True)
        st.markdown(
"""<div style="font-size:11px;color:#D4AF37;letter-spacing:3px;text-transform:uppercase;margin-bottom:12px;">Navigate</div>""",
            unsafe_allow_html=True)
        for icon, label, href in [
            ("🏠","Home","/"), ("⚖️","Virtual Advocate","/1_chat"),
            ("📄","Witness Stand","/2_upload"), ("🔍","Case Archives","/3_case_search"),
            ("🔮","The Oracle","/5_predict"), ("📊","Chamber Records","/6_dashboard"),
        ]:
            st.markdown(
f"""<a href="{href}" target="_self" style="text-decoration:none;display:block;padding:7px 12px;border-radius:8px;margin-bottom:3px;color:#8E8E93;font-size:12px;">{icon} {label}</a>""",
                unsafe_allow_html=True)
        st.markdown("<div style='height:20px;'></div>", unsafe_allow_html=True)
        st.markdown(
"""<div style="font-size:11px;color:#D4AF37;letter-spacing:3px;text-transform:uppercase;margin-bottom:10px;">Helplines</div>""",
            unsafe_allow_html=True)
        for name, num in [("Women","1091"),("Police","100"),("Legal Aid","15100"),("Consumer","1800-11-4000")]:
            st.markdown(
f"""<div style="display:flex;justify-content:space-between;padding:5px 8px;margin-bottom:4px;">
<span style="font-size:11px;color:#8E8E93;">{name}</span>
<span style="font-size:12px;color:#D4AF37;font-weight:700;">{num}</span>
</div>""",
                unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════
# FOOTER
# ════════════════════════════════════════════════════════════
def render_footer():
    st.markdown("<div style='height:48px;'></div>", unsafe_allow_html=True)
    st.markdown(
"""<div style="text-align:center;padding:20px;border-top:1px solid rgba(212,175,55,0.1);">
<span style="font-size:11px;color:#333;letter-spacing:2px;">NYAYA-SETU · THE DOCUMENT FORGE · INDIA · 2026</span>
</div>""",
        unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════
# MAIN
# ════════════════════════════════════════════════════════════
inject_css()
render_sidebar()
render_header()
render_template_selector()

selected = st.session_state.get("selected_template")

if st.session_state.get("generated_doc"):
    render_document_output()
elif selected:
    values = render_form(selected)
    render_generate_button(selected, values)
else:
    render_empty_state()

render_footer()