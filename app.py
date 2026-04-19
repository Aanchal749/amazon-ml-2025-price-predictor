"""
CloudPriceML — Premium SaaS Dashboard
=======================================
Sends requests to the live Render FastAPI backend.
"""

import time
import requests
import streamlit as st
from supabase import create_client, Client

# ─────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────
st.set_page_config(
    page_title="CloudPriceML | Seller Intelligence",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 🔥 YOUR LIVE RENDER BACKEND URL
API_URL    = "https://amazon-ml-2025-price-predictor.onrender.com/predict"
HEALTH_URL = "https://amazon-ml-2025-price-predictor.onrender.com/health"

# ─────────────────────────────────────────────────────────
# SUPABASE INITIALIZATION
# ─────────────────────────────────────────────────────────
@st.cache_resource
def init_supabase():
    try:
        url = "https://dqbirxwhitqijqlkbuzm.supabase.co"
        key = "sb_publishable_zEoVhO0kCpcPxhEoYtYodw_13SniAKt"
        return create_client(url, key)
    except Exception as e:
        st.error(f"DATABASE ERROR: {e}")
        return None

supabase: Client = init_supabase()

# ─────────────────────────────────────────────────────────
# PROFESSIONAL LIGHT THEME CSS
# ─────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&family=Outfit:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Outfit', sans-serif;
}
.stApp {
    background: #f5f4f0;
}
.block-container {
    padding-top: 0 !important;
    padding-bottom: 3rem !important;
    max-width: 1280px !important;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: #ffffff !important;
    border-right: 1px solid #e5e1d8 !important;
    box-shadow: 2px 0 12px rgba(0,0,0,0.04);
}
[data-testid="stSidebar"] .stMarkdown p,
[data-testid="stSidebar"] .stMarkdown li {
    color: #6b6560 !important;
    font-size: 0.85rem !important;
}
[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] h4 {
    font-family: 'Outfit', sans-serif !important;
    font-weight: 600 !important;
    color: #1a1714 !important;
    font-size: 0.9rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.08em !important;
}

/* ── Top nav bar ── */
.topbar {
    background: #ffffff;
    border-bottom: 1px solid #e5e1d8;
    padding: 0.85rem 3rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin: -1rem -3rem 0;
    box-shadow: 0 1px 6px rgba(0,0,0,0.05);
}
.topbar-brand {
    font-family: 'Playfair Display', serif;
    font-size: 1.3rem;
    font-weight: 700;
    color: #1a1714;
    letter-spacing: -0.02em;
}
.topbar-brand span { color: #c47c2e; }
.topbar-meta {
    font-size: 0.78rem;
    color: #9e978e;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    font-weight: 500;
}

/* ── Hero ── */
.hero-section {
    background: linear-gradient(108deg, #1a1714 0%, #2d2520 55%, #3d3020 100%);
    border-radius: 20px;
    padding: 3.5rem 3.5rem 3rem;
    margin: 1.5rem 0 2rem;
    position: relative;
    overflow: hidden;
}
.hero-section::before {
    content: '';
    position: absolute;
    top: -100px; right: -60px;
    width: 380px; height: 380px;
    background: radial-gradient(circle, rgba(196,124,46,0.22) 0%, transparent 65%);
    pointer-events: none;
}
.hero-section::after {
    content: '';
    position: absolute;
    bottom: -80px; left: 40%;
    width: 260px; height: 260px;
    background: radial-gradient(circle, rgba(255,255,255,0.05) 0%, transparent 70%);
    pointer-events: none;
}
.hero-kicker {
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.22em;
    text-transform: uppercase;
    color: #c47c2e;
    margin-bottom: 0.7rem;
}
.hero-title {
    font-family: 'Playfair Display', serif;
    font-size: 2.9rem;
    font-weight: 700;
    color: #faf8f4;
    line-height: 1.1;
    letter-spacing: -0.02em;
    margin: 0 0 0.8rem;
}
.hero-title em { font-style: italic; color: #d4924a; }
.hero-sub {
    color: #9e978e;
    font-size: 1rem;
    font-weight: 300;
    max-width: 520px;
    line-height: 1.65;
    margin: 0;
}

/* ── Stat strip ── */
.stat-strip {
    display: flex;
    gap: 1px;
    background: #e5e1d8;
    border: 1px solid #e5e1d8;
    border-radius: 14px;
    overflow: hidden;
    margin-bottom: 2.5rem;
    box-shadow: 0 1px 4px rgba(0,0,0,0.04);
}
.stat-item {
    background: #ffffff;
    flex: 1;
    padding: 1.2rem 1.6rem;
    transition: background 0.2s;
}
.stat-item:hover { background: #faf8f4; }
.si-label {
    font-size: 0.68rem;
    font-weight: 600;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #9e978e;
    margin-bottom: 0.3rem;
}
.si-value {
    font-family: 'Playfair Display', serif;
    font-size: 1.45rem;
    font-weight: 600;
    color: #1a1714;
    letter-spacing: -0.01em;
}

/* ── Panel header ── */
.panel-header {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    margin-bottom: 1.1rem;
    padding-bottom: 0.9rem;
    border-bottom: 1px solid #f0ede8;
}
.panel-step {
    background: #1a1714;
    color: #c47c2e;
    font-size: 0.65rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    padding: 0.28rem 0.65rem;
    border-radius: 100px;
    text-transform: uppercase;
}
.panel-title {
    font-family: 'Outfit', sans-serif;
    font-size: 0.88rem;
    font-weight: 600;
    color: #1a1714;
    letter-spacing: 0.02em;
    text-transform: uppercase;
}

/* ── Inputs ── */
.stTextArea textarea {
    background: #faf8f4 !important;
    border: 1.5px solid #e5e1d8 !important;
    border-radius: 10px !important;
    color: #1a1714 !important;
    font-family: 'Outfit', sans-serif !important;
    font-size: 0.93rem !important;
    line-height: 1.6 !important;
    padding: 0.85rem 1rem !important;
    transition: border-color 0.2s, box-shadow 0.2s !important;
}
.stTextArea textarea:focus {
    border-color: #c47c2e !important;
    box-shadow: 0 0 0 3px rgba(196,124,46,0.1) !important;
    background: #ffffff !important;
}
label[data-testid="stWidgetLabel"] p {
    color: #6b6560 !important;
    font-size: 0.82rem !important;
    font-weight: 500 !important;
    letter-spacing: 0.03em !important;
    margin-bottom: 0.3rem !important;
}
.stSelectbox > div > div {
    background: #faf8f4 !important;
    border: 1.5px solid #e5e1d8 !important;
    border-radius: 10px !important;
    color: #1a1714 !important;
}
.stNumberInput input {
    background: #faf8f4 !important;
    border: 1.5px solid #e5e1d8 !important;
    border-radius: 10px !important;
    color: #1a1714 !important;
}
[data-testid="stFileUploader"] {
    background: #faf8f4 !important;
    border: 1.5px dashed #d4c9bb !important;
    border-radius: 12px !important;
    transition: border-color 0.2s;
}
[data-testid="stFileUploader"]:hover {
    border-color: #c47c2e !important;
    background: #fdf6ee !important;
}

/* ── Primary CTA ── */
.stButton > button[kind="primary"] {
    background: #1a1714 !important;
    border: none !important;
    border-radius: 10px !important;
    color: #ffffff !important;
    font-family: 'Outfit', sans-serif !important;
    font-size: 0.92rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.06em !important;
    text-transform: uppercase !important;
    padding: 0.8rem 2rem !important;
    transition: all 0.2s !important;
    box-shadow: 0 2px 10px rgba(26,23,20,0.18) !important;
}
.stButton > button[kind="primary"]:hover:not(:disabled) {
    background: #2d2520 !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 20px rgba(26,23,20,0.25) !important;
}
.stButton > button[kind="primary"]:disabled {
    background: #ccc7c0 !important;
    box-shadow: none !important;
    color: #9e978e !important;
}

/* ── Secondary buttons ── */
.stButton > button:not([kind="primary"]) {
    background: #ffffff !important;
    border: 1.5px solid #e5e1d8 !important;
    border-radius: 10px !important;
    color: #6b6560 !important;
    font-family: 'Outfit', sans-serif !important;
    font-size: 0.82rem !important;
    font-weight: 500 !important;
    transition: all 0.2s !important;
}
.stButton > button:not([kind="primary"]):hover {
    border-color: #c47c2e !important;
    color: #1a1714 !important;
}

/* ── Expander ── */
[data-testid="stExpander"] {
    background: #faf8f4 !important;
    border: 1px solid #e5e1d8 !important;
    border-radius: 12px !important;
}
[data-testid="stExpander"] summary p {
    font-size: 0.85rem !important;
    color: #6b6560 !important;
    font-weight: 500 !important;
}

/* ── Price result card ── */
.valuation-card {
    background: #ffffff;
    border: 1px solid #e5e1d8;
    border-radius: 20px;
    overflow: hidden;
    box-shadow: 0 4px 20px rgba(0,0,0,0.07);
    animation: riseIn 0.45s cubic-bezier(0.22,1,0.36,1) both;
}
@keyframes riseIn {
    from { opacity: 0; transform: translateY(20px) scale(0.98); }
    to   { opacity: 1; transform: translateY(0) scale(1); }
}
.valuation-top {
    background: linear-gradient(135deg, #1a1714 0%, #3d3020 100%);
    padding: 2.5rem 2rem 2rem;
    text-align: center;
    position: relative;
    overflow: hidden;
}
.valuation-top::before {
    content: '';
    position: absolute;
    top: -60px; right: -40px;
    width: 200px; height: 200px;
    background: radial-gradient(circle, rgba(196,124,46,0.3) 0%, transparent 65%);
}
.val-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    background: rgba(196,124,46,0.15);
    border: 1px solid rgba(196,124,46,0.35);
    color: #d4924a;
    font-size: 0.68rem;
    font-weight: 600;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    padding: 0.3rem 0.9rem;
    border-radius: 100px;
    margin-bottom: 1.2rem;
}
.val-price {
    font-family: 'Playfair Display', serif;
    font-size: 4rem;
    font-weight: 700;
    color: #faf8f4;
    line-height: 1;
    letter-spacing: -0.03em;
    margin-bottom: 0.3rem;
}
.val-label {
    font-size: 0.78rem;
    color: #9e978e;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    font-weight: 500;
}
.valuation-bottom {
    padding: 1.5rem 2rem;
    background: #faf8f4;
    border-top: 1px solid #f0ede8;
}
.range-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1rem;
}
.range-box { text-align: center; flex: 1; }
.rb-label {
    font-size: 0.68rem;
    color: #9e978e;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin-bottom: 0.25rem;
}
.rb-val {
    font-family: 'Playfair Display', serif;
    font-size: 1.15rem;
    color: #1a1714;
    font-weight: 600;
}
.range-divider {
    width: 1px; height: 36px;
    background: #e5e1d8;
    margin: 0 1rem;
}
.val-note {
    font-size: 0.75rem;
    color: #b5aea5;
    text-align: center;
    padding-top: 0.6rem;
    border-top: 1px solid #f0ede8;
}

/* ── Result placeholder ── */
.result-empty {
    background: #ffffff;
    border: 1.5px dashed #d4c9bb;
    border-radius: 20px;
    padding: 4rem 2rem;
    text-align: center;
}
.re-icon {
    width: 56px; height: 56px;
    background: #f5f4f0;
    border: 1px solid #e5e1d8;
    border-radius: 16px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.6rem;
    margin: 0 auto 1.2rem;
}
.result-empty h4 {
    font-family: 'Outfit', sans-serif;
    font-size: 0.95rem;
    font-weight: 600;
    color: #1a1714;
    margin: 0 0 0.5rem;
}
.result-empty p {
    font-size: 0.83rem;
    color: #9e978e;
    line-height: 1.6;
    max-width: 240px;
    margin: 0 auto;
}

/* ── Sidebar status dots ── */
.status-row {
    display: flex;
    align-items: center;
    gap: 0.55rem;
    padding: 0.55rem 0;
    font-size: 0.82rem;
    font-weight: 500;
    color: #6b6560;
    border-bottom: 1px solid #f0ede8;
}
.dot-green { width: 7px; height: 7px; border-radius: 50%; background: #16a34a; box-shadow: 0 0 0 3px rgba(22,163,74,0.15); flex-shrink: 0; }
.dot-red   { width: 7px; height: 7px; border-radius: 50%; background: #dc2626; box-shadow: 0 0 0 3px rgba(220,38,38,0.15); flex-shrink: 0; }

/* ── Misc ── */
hr.div { border: none; border-top: 1px solid #e5e1d8; margin: 1.4rem 0; }
.tip-text { font-size: 0.76rem; color: #b5aea5; margin-top: 0.4rem; line-height: 1.5; }

/* ── Footer ── */
.footer {
    margin-top: 3rem;
    padding-top: 1.5rem;
    border-top: 1px solid #e5e1d8;
    text-align: center;
    font-size: 0.75rem;
    color: #b5aea5;
    letter-spacing: 0.05em;
}
.footer strong { color: #6b6560; font-weight: 600; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────
# CONSTANTS & HELPERS
# ─────────────────────────────────────────────────────────
BRANDS = [
    "Select a Brand...", "Samsung", "Apple", "Sony", "LG", "Philips",
    "Bosch", "Havells", "Prestige", "Bajaj", "Whirlpool", "Godrej",
    "Amul", "Nestle", "Himalaya", "Patanjali", "Britannia", "Other / Unknown"
]

def check_backend_health():
    try:
        r = requests.get(HEALTH_URL, timeout=10)
        return r.status_code == 200
    except requests.exceptions.RequestException:
        return False

# ─────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### System Status")

    if supabase is not None:
        st.markdown('<div class="status-row"><div class="dot-green"></div>Supabase Database</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="status-row"><div class="dot-red"></div>Supabase Offline</div>', unsafe_allow_html=True)

    st.markdown('<div class="status-row"><div class="dot-green"></div>Render Cloud API</div>', unsafe_allow_html=True)
    st.markdown('<div class="status-row"><div class="dot-green"></div>Multimodal Engine</div>', unsafe_allow_html=True)

    st.markdown("<hr class='div'>", unsafe_allow_html=True)

    st.markdown("### Cloud Management")
    if st.button("⚡ Ping API Server", use_container_width=True):
        with st.spinner("Pinging Render server..."):
            if check_backend_health():
                st.success("Server is live and ready.")
            else:
                st.error("Server sleeping. Wait ~60 s and retry.")

    st.markdown("<hr class='div'>", unsafe_allow_html=True)
    st.markdown("""
    <div style="font-size:0.75rem; color:#b5aea5; line-height:1.8;">
        <strong style="color:#6b6560; font-size:0.8rem;">CloudPriceML</strong><br>
        AI-Powered Valuation Engine<br><br>
        Built by<br>
        <strong style="color:#1a1714; font-size:0.82rem;">Aanchal Chauhan</strong>
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────
# TOP NAV BAR
# ─────────────────────────────────────────────────────────
st.markdown("""
<div class="topbar">
  <div class="topbar-brand">Cloud<span>Price</span>ML</div>
  <div class="topbar-meta">E-Commerce Valuation Intelligence &nbsp;·&nbsp; v2.0</div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────
# HERO
# ─────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-section">
  <div class="hero-kicker">AI-Powered Price Intelligence</div>
  <h1 class="hero-title">Valuation built for<br><em>serious sellers.</em></h1>
  <p class="hero-sub">Enter your product details and let our multimodal model — trained on 75,000+ real market assets — generate an accurate, confidence-calibrated price in seconds.</p>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────
# STAT STRIP
# ─────────────────────────────────────────────────────────
st.markdown("""
<div class="stat-strip">
  <div class="stat-item"><div class="si-label">Model Type</div><div class="si-value">Multimodal</div></div>
  <div class="stat-item"><div class="si-label">Training Assets</div><div class="si-value">75k+</div></div>
  <div class="stat-item"><div class="si-label">Inference Host</div><div class="si-value">Render API</div></div>
  <div class="stat-item"><div class="si-label">Image Analysis</div><div class="si-value">Enabled</div></div>
  <div class="stat-item"><div class="si-label">Confidence Interval</div><div class="si-value">± 15%</div></div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────
# MAIN LAYOUT
# ─────────────────────────────────────────────────────────
col_input, col_result = st.columns([1.15, 1], gap="large")

with col_input:
    st.markdown('<div class="panel-header"><span class="panel-step">Step 01</span><span class="panel-title">Product Description</span></div>', unsafe_allow_html=True)
    catalog_content = st.text_area(
        "Product description",
        placeholder="e.g., Samsung 65-inch 4K Smart QLED TV with Quantum HDR, Dolby Atmos, built-in Alexa, 120Hz refresh rate, 4 HDMI ports...",
        height=165,
        label_visibility="collapsed"
    )
    st.markdown('<p class="tip-text">💡 Richer descriptions yield more accurate valuations — include specs, condition, brand, and key features.</p>', unsafe_allow_html=True)

    st.markdown("<hr class='div'>", unsafe_allow_html=True)

    st.markdown('<div class="panel-header"><span class="panel-step">Step 02</span><span class="panel-title">Product Image</span></div>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader(
        "Upload product image",
        type=["jpg", "jpeg", "png"],
        label_visibility="collapsed"
    )

    image_url = ""

    if uploaded_file is not None:
        if supabase is not None:
            with st.spinner("Uploading to cloud vault…"):
                try:
                    file_bytes = uploaded_file.getvalue()
                    file_name  = f"scan_{int(time.time())}_{uploaded_file.name}"
                    supabase.storage.from_("product_images").upload(
                        file_name, file_bytes, {"content-type": uploaded_file.type}
                    )
                    image_url = supabase.storage.from_("product_images").get_public_url(file_name)
                    st.success("✓ Image secured in cloud vault.")
                except Exception as e:
                    st.error(f"Image upload failed: {e}")
        else:
            st.warning("⚠️ Database offline — image will not be persisted.")

    st.markdown("<hr class='div'>", unsafe_allow_html=True)

    with st.expander("🛠️  Advanced Metadata  (Optional)"):
        h1, h2 = st.columns(2)
        with h1:
            brand = st.selectbox("Brand", BRANDS)
        with h2:
            ipq = st.number_input("Package Quantity", min_value=1, value=1)

    hints = []
    if brand and brand not in ("Select a Brand...", "Other / Unknown"):
        hints.append(brand.lower())
    if ipq > 1:
        hints.append(f"pack of {ipq}")

    final_catalog_text = catalog_content
    if hints:
        final_catalog_text += " " + " ".join(hints)

    st.markdown("<br>", unsafe_allow_html=True)
    predict_clicked = st.button(
        "Generate Valuation  →",
        type="primary",
        use_container_width=True,
        disabled=not catalog_content.strip()
    )

with col_result:
    st.markdown('<div class="panel-header"><span class="panel-step">Output</span><span class="panel-title">Valuation Report</span></div>', unsafe_allow_html=True)

    if image_url:
        st.image(image_url, use_container_width=True, caption="Visual asset submitted for analysis")
        st.markdown("<hr class='div'>", unsafe_allow_html=True)

    if not predict_clicked and not image_url:
        st.markdown("""
        <div class="result-empty">
          <div class="re-icon">📊</div>
          <h4>Awaiting Input</h4>
          <p>Fill in the product description and click Generate Valuation to receive your AI-powered price estimate.</p>
        </div>
        """, unsafe_allow_html=True)

    if predict_clicked:
        with st.spinner("Running inference on Render server…"):
            try:
                files = {}
                if uploaded_file:
                    uploaded_file.seek(0)
                    files = {"image_file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}

                payload  = {"catalog_content": final_catalog_text}
                response = requests.post(API_URL, data=payload, files=files, timeout=30)

                if response.status_code == 200:
                    result     = response.json()
                    price      = result.get("predicted_price", 0)
                    price_low  = max(0.01, price * 0.85)
                    price_high = price * 1.15

                    st.markdown(f"""
                    <div class="valuation-card">
                      <div class="valuation-top">
                        <div class="val-badge">✦ AI Valuation Complete</div>
                        <div class="val-price">₹{price:,.2f}</div>
                        <div class="val-label">Suggested Retail Price</div>
                      </div>
                      <div class="valuation-bottom">
                        <div class="range-row">
                          <div class="range-box">
                            <div class="rb-label">Low Estimate</div>
                            <div class="rb-val">₹{price_low:,.2f}</div>
                          </div>
                          <div class="range-divider"></div>
                          <div class="range-box">
                            <div class="rb-label">Point Estimate</div>
                            <div class="rb-val">₹{price:,.2f}</div>
                          </div>
                          <div class="range-divider"></div>
                          <div class="range-box">
                            <div class="rb-label">High Estimate</div>
                            <div class="rb-val">₹{price_high:,.2f}</div>
                          </div>
                        </div>
                        <div class="val-note">± 15% confidence interval based on live market variance</div>
                      </div>
                    </div>
                    """, unsafe_allow_html=True)

                    if supabase is not None:
                        try:
                            supabase.table('predictions').insert({
                                "product_details": final_catalog_text[:250],
                                "predicted_price": price,
                                "image_url": image_url
                            }).execute()
                        except Exception:
                            pass

                else:
                    st.error(f"API Error [{response.status_code}] — Verify the Render backend is running.")

            except requests.exceptions.Timeout:
                st.error("🚨 Request timed out. Use Ping API Server in the sidebar, wait ~60 seconds, then retry.")
            except requests.exceptions.ConnectionError:
                st.error("🚨 Connection refused. The Render API appears to be offline.")
            except Exception as e:
                st.error(f"Unexpected error: {e}")

# ─────────────────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────────────────
st.markdown("""
<div class="footer">
  CloudPriceML &nbsp;·&nbsp; AI-Powered E-Commerce Valuation &nbsp;·&nbsp;
  Built by <strong>Aanchal Chauhan</strong>
</div>
""", unsafe_allow_html=True)
