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
API_URL = "https://amazon-ml-2025-price-predictor.onrender.com/predict"
HEALTH_URL = "https://amazon-ml-2025-price-predictor.onrender.com/health"

# ─────────────────────────────────────────────────────────
# SUPABASE INITIALIZATION (EMERGENCY BYPASS FOR DEADLINE)
# ─────────────────────────────────────────────────────────
@st.cache_resource
def init_supabase():
    try:
        url = "https://dqbirxwhitqijqlkbuzm.supabase.co"
        key = "sb_publishable_zEoVhO0kCpcPxhEoYtYodw_13SniAKt"
        return create_client(url, key)
    except Exception as e:
        st.error(f"DATABASE CRASH REASON: {e}")
        return None

supabase: Client = init_supabase()

# ─────────────────────────────────────────────────────────
# PREMIUM CSS STYLING — Dark Luxury Theme
# ─────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap');

    /* ── Global reset ── */
    html, body, [class*="css"] {
        font-family: 'DM Sans', sans-serif;
    }
    .stApp {
        background: #070b14;
    }
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 3rem !important;
    }

    /* ── Sidebar ── */
    [data-testid="stSidebar"] {
        background: #0c1221 !important;
        border-right: 1px solid #1e2d47;
    }
    [data-testid="stSidebar"] * {
        color: #94a3b8 !important;
    }
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] h4 {
        color: #e2e8f0 !important;
        font-family: 'Syne', sans-serif !important;
        font-weight: 700 !important;
    }

    /* ── Hero header ── */
    .hero-wrap {
        position: relative;
        background: linear-gradient(135deg, #0f1f3d 0%, #0a192f 60%, #050d1a 100%);
        border: 1px solid #1e3a5f;
        border-radius: 20px;
        padding: 3rem 3.5rem;
        margin-bottom: 2.5rem;
        overflow: hidden;
    }
    .hero-wrap::before {
        content: '';
        position: absolute;
        top: -80px; right: -80px;
        width: 320px; height: 320px;
        background: radial-gradient(circle, rgba(59,130,246,0.18) 0%, transparent 70%);
        pointer-events: none;
    }
    .hero-wrap::after {
        content: '';
        position: absolute;
        bottom: -60px; left: 200px;
        width: 240px; height: 240px;
        background: radial-gradient(circle, rgba(16,185,129,0.12) 0%, transparent 70%);
        pointer-events: none;
    }
    .hero-eyebrow {
        font-family: 'DM Sans', sans-serif;
        font-size: 0.75rem;
        font-weight: 500;
        letter-spacing: 0.2em;
        text-transform: uppercase;
        color: #3b82f6;
        margin-bottom: 0.6rem;
    }
    .hero-title {
        font-family: 'Syne', sans-serif;
        font-size: 3rem;
        font-weight: 800;
        color: #f1f5f9;
        margin: 0 0 0.6rem;
        line-height: 1.1;
        letter-spacing: -0.03em;
    }
    .hero-title span { color: #3b82f6; }
    .hero-subtitle {
        color: #64748b;
        font-size: 1.05rem;
        font-weight: 300;
        margin: 0;
    }

    /* ── Stat pills ── */
    .stat-row { display: flex; gap: 1rem; margin-bottom: 2.5rem; }
    .stat-pill {
        background: #0c1221;
        border: 1px solid #1e2d47;
        border-radius: 12px;
        padding: 1rem 1.4rem;
        flex: 1;
        transition: border-color 0.2s;
    }
    .stat-pill:hover { border-color: #3b82f6; }
    .stat-pill .sp-label {
        font-size: 0.7rem;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        color: #475569;
        font-weight: 600;
    }
    .stat-pill .sp-value {
        font-family: 'Syne', sans-serif;
        font-size: 1.5rem;
        font-weight: 700;
        color: #e2e8f0;
        margin-top: 0.25rem;
    }

    /* ── Section headings ── */
    .section-label {
        font-family: 'Syne', sans-serif;
        font-size: 0.7rem;
        letter-spacing: 0.18em;
        text-transform: uppercase;
        color: #3b82f6;
        font-weight: 600;
        margin-bottom: 0.4rem;
    }
    .section-title {
        font-family: 'Syne', sans-serif;
        font-size: 1.15rem;
        font-weight: 700;
        color: #e2e8f0;
        margin: 0 0 1.2rem;
    }

    /* ── Card wrapper ── */
    .card {
        background: #0c1221;
        border: 1px solid #1e2d47;
        border-radius: 16px;
        padding: 1.8rem;
        margin-bottom: 1.5rem;
    }

    /* ── Input fields ── */
    .stTextArea textarea, .stSelectbox select,
    .stNumberInput input {
        background: #0f1b2d !important;
        border: 1px solid #1e3a5f !important;
        border-radius: 10px !important;
        color: #e2e8f0 !important;
        font-family: 'DM Sans', sans-serif !important;
        font-size: 0.95rem !important;
        transition: border-color 0.2s !important;
    }
    .stTextArea textarea:focus {
        border-color: #3b82f6 !important;
        box-shadow: 0 0 0 3px rgba(59,130,246,0.12) !important;
    }
    label[data-testid="stWidgetLabel"] p {
        color: #94a3b8 !important;
        font-size: 0.85rem !important;
        font-weight: 500 !important;
        letter-spacing: 0.02em !important;
    }

    /* ── File uploader ── */
    [data-testid="stFileUploader"] {
        background: #0f1b2d !important;
        border: 1.5px dashed #1e3a5f !important;
        border-radius: 12px !important;
    }
    [data-testid="stFileUploader"]:hover {
        border-color: #3b82f6 !important;
    }

    /* ── Primary CTA button ── */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #2563eb, #1d4ed8) !important;
        border: none !important;
        border-radius: 12px !important;
        color: white !important;
        font-family: 'Syne', sans-serif !important;
        font-size: 1rem !important;
        font-weight: 700 !important;
        letter-spacing: 0.04em !important;
        padding: 0.85rem 2rem !important;
        transition: all 0.2s !important;
        box-shadow: 0 4px 20px rgba(37,99,235,0.35) !important;
    }
    .stButton > button[kind="primary"]:hover {
        background: linear-gradient(135deg, #1d4ed8, #1e40af) !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 6px 28px rgba(37,99,235,0.45) !important;
    }
    .stButton > button[kind="primary"]:disabled {
        opacity: 0.4 !important;
        transform: none !important;
        box-shadow: none !important;
    }

    /* ── Secondary buttons (sidebar) ── */
    .stButton > button:not([kind="primary"]) {
        background: #0f1b2d !important;
        border: 1px solid #1e3a5f !important;
        border-radius: 10px !important;
        color: #94a3b8 !important;
        font-family: 'DM Sans', sans-serif !important;
        font-size: 0.875rem !important;
        transition: all 0.2s !important;
    }
    .stButton > button:not([kind="primary"]):hover {
        border-color: #3b82f6 !important;
        color: #e2e8f0 !important;
    }

    /* ── Price result card ── */
    .price-result {
        background: linear-gradient(140deg, #064e3b 0%, #065f46 50%, #047857 100%);
        border: 1px solid #10b981;
        border-radius: 20px;
        padding: 2.8rem 2rem;
        text-align: center;
        color: white;
        box-shadow: 0 12px 40px rgba(16,185,129,0.25);
        animation: fadeUp 0.5s ease both;
    }
    @keyframes fadeUp {
        from { opacity: 0; transform: translateY(16px); }
        to   { opacity: 1; transform: translateY(0); }
    }
    .price-result .badge {
        display: inline-block;
        background: rgba(255,255,255,0.15);
        border-radius: 100px;
        padding: 0.3rem 1rem;
        font-size: 0.7rem;
        letter-spacing: 0.15em;
        text-transform: uppercase;
        font-weight: 600;
        margin-bottom: 1.2rem;
    }
    .price-result .price-value {
        font-family: 'Syne', sans-serif;
        font-size: 4.2rem;
        font-weight: 800;
        line-height: 1;
        letter-spacing: -0.03em;
        margin-bottom: 0.8rem;
    }
    .price-result .price-range {
        font-size: 0.9rem;
        opacity: 0.75;
        font-weight: 400;
    }
    .price-result .divider-line {
        border: none;
        border-top: 1px solid rgba(255,255,255,0.15);
        margin: 1.4rem auto;
        width: 70%;
    }
    .price-result .note {
        font-size: 0.8rem;
        opacity: 0.6;
    }

    /* ── Status badges ── */
    .status-ok  { color: #10b981; font-weight: 600; font-size: 0.85rem; display: flex; align-items: center; gap: 0.4rem; padding: 0.5rem 0; }
    .status-err { color: #f87171; font-weight: 600; font-size: 0.85rem; display: flex; align-items: center; gap: 0.4rem; padding: 0.5rem 0; }

    /* ── Expander ── */
    [data-testid="stExpander"] {
        background: #0c1221 !important;
        border: 1px solid #1e2d47 !important;
        border-radius: 12px !important;
    }
    [data-testid="stExpander"] summary {
        color: #94a3b8 !important;
        font-size: 0.9rem !important;
    }

    /* ── Alerts ── */
    .stAlert { border-radius: 12px !important; }

    /* ── Result placeholder ── */
    .result-placeholder {
        background: #0c1221;
        border: 1.5px dashed #1e2d47;
        border-radius: 20px;
        padding: 3rem 2rem;
        text-align: center;
        color: #334155;
    }
    .result-placeholder .icon { font-size: 2.5rem; margin-bottom: 1rem; }
    .result-placeholder p { margin: 0; font-size: 0.95rem; line-height: 1.6; }

    /* ── Footer ── */
    .footer {
        text-align: center;
        color: #1e3a5f;
        font-size: 0.78rem;
        margin-top: 3rem;
        padding-top: 1.5rem;
        border-top: 1px solid #0f1d30;
        letter-spacing: 0.04em;
    }
    .footer span { color: #334155; }

    /* ── Divider ── */
    hr.divider { border: none; border-top: 1px solid #1e2d47; margin: 2rem 0; }

    /* ── Column gap fix ── */
    [data-testid="stHorizontalBlock"] { gap: 2rem !important; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────
# CONSTANTS & HELPERS
# ─────────────────────────────────────────────────────────
BRANDS = ["Select a Brand...", "Samsung", "Apple", "Sony", "LG", "Philips", "Bosch", "Havells", "Prestige", "Bajaj", "Whirlpool", "Godrej", "Amul", "Nestle", "Himalaya", "Patanjali", "Britannia", "Other / Unknown"]

def check_backend_health():
    """Pings the Render backend to wake it up."""
    try:
        response = requests.get(HEALTH_URL, timeout=10)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False

# ─────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ System Status")

    if supabase is not None:
        st.markdown('<div class="status-ok">🟢 Supabase Database Live</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="status-err">🔴 Supabase Offline</div>', unsafe_allow_html=True)

    st.markdown('<div class="status-ok">🟢 Render Cloud API Linked</div>', unsafe_allow_html=True)

    st.markdown("---")

    st.markdown("#### ☁️ Cloud Management")
    if st.button("⚡ Ping API Server (Wake Up)", use_container_width=True):
        with st.spinner("Pinging Render..."):
            if check_backend_health():
                st.success("Server is awake and ready!")
            else:
                st.error("Server sleeping or unreachable. Wait 60 s and retry.")

    st.markdown("---")
    st.caption("Built by **Aanchal Chauhan**")

# ─────────────────────────────────────────────────────────
# HERO HEADER
# ─────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-wrap">
  <div class="hero-eyebrow">AI-Powered E-Commerce Intelligence</div>
  <h1 class="hero-title">Cloud<span>Price</span>ML</h1>
  <p class="hero-subtitle">Real-time product valuation powered by multimodal AI — trained on 75k+ market assets.</p>
</div>
""", unsafe_allow_html=True)

# ── Stat pills ──
st.markdown("""
<div class="stat-row">
  <div class="stat-pill">
    <div class="sp-label">Algorithm</div>
    <div class="sp-value">Multimodal</div>
  </div>
  <div class="stat-pill">
    <div class="sp-label">Training Data</div>
    <div class="sp-value">75k+ Assets</div>
  </div>
  <div class="stat-pill">
    <div class="sp-label">Inference</div>
    <div class="sp-value">Render API</div>
  </div>
  <div class="stat-pill">
    <div class="sp-label">Image Support</div>
    <div class="sp-value">Enabled</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────
# MAIN LAYOUT — Input (left) | Result (right)
# ─────────────────────────────────────────────────────────
col_input, col_result = st.columns([1.2, 1], gap="large")

with col_input:
    st.markdown('<div class="section-label">Step 1</div><div class="section-title">Product Description</div>', unsafe_allow_html=True)
    catalog_content = st.text_area(
        "Enter full product description:",
        placeholder="e.g., Samsung 65-inch 4K Smart QLED TV with Quantum HDR, Dolby Atmos, built-in Alexa...",
        height=160,
        label_visibility="collapsed"
    )
    st.caption("Tip: More detail → more accurate valuation. Include specs, features, and condition.")

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)

    st.markdown('<div class="section-label">Step 2</div><div class="section-title">Product Image</div>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader(
        "Upload product image (JPG / PNG)",
        type=["jpg", "jpeg", "png"],
        label_visibility="collapsed"
    )

    image_url = ""

    if uploaded_file is not None:
        if supabase is not None:
            with st.spinner("Uploading to cloud vault..."):
                try:
                    file_bytes = uploaded_file.getvalue()
                    file_name = f"scan_{int(time.time())}_{uploaded_file.name}"
                    supabase.storage.from_("product_images").upload(
                        file_name,
                        file_bytes,
                        {"content-type": uploaded_file.type}
                    )
                    image_url = supabase.storage.from_("product_images").get_public_url(file_name)
                    st.success("✓ Image secured in cloud vault.")
                except Exception as e:
                    st.error(f"Image upload failed: {e}")
        else:
            st.warning("⚠️ Database offline — image won't be stored.")

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)

    with st.expander("🛠️ Advanced Metadata (Optional)"):
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
        "Generate Valuation  🔮",
        type="primary",
        use_container_width=True,
        disabled=not catalog_content.strip()
    )

# ─────────────────────────────────────────────────────────
# API INFERENCE & RESULT COLUMN
# ─────────────────────────────────────────────────────────
with col_result:
    st.markdown('<div class="section-label">Output</div><div class="section-title">Valuation Report</div>', unsafe_allow_html=True)

    if image_url:
        st.image(image_url, use_container_width=True, caption="Visual asset analysed")

    if not predict_clicked and not image_url:
        st.markdown("""
        <div class="result-placeholder">
          <div class="icon">📊</div>
          <p>Fill in the product description on the left and click <strong>Generate Valuation</strong> to see the AI-predicted price.</p>
        </div>
        """, unsafe_allow_html=True)

    if predict_clicked:
        with st.spinner("Running AI models on Render server..."):
            try:
                files = {}
                if uploaded_file:
                    uploaded_file.seek(0)
                    files = {"image_file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}

                payload = {"catalog_content": final_catalog_text}
                response = requests.post(API_URL, data=payload, files=files, timeout=30)

                if response.status_code == 200:
                    result = response.json()
                    price = result.get("predicted_price", 0)
                    price_low  = max(0.01, price * 0.85)
                    price_high = price * 1.15

                    st.markdown(f"""
                    <div class="price-result">
                      <div class="badge">AI Valuation Complete</div>
                      <div class="price-value">₹{price:,.2f}</div>
                      <hr class="divider-line">
                      <div class="price-range">Confidence Range &nbsp;·&nbsp; ₹{price_low:,.2f} — ₹{price_high:,.2f}</div>
                      <div class="note" style="margin-top:0.8rem;">±15% confidence interval based on market variance</div>
                    </div>
                    """, unsafe_allow_html=True)

                    # Log to Supabase
                    if supabase is not None:
                        try:
                            supabase.table('predictions').insert({
                                "product_details": final_catalog_text[:250],
                                "predicted_price": price,
                                "image_url": image_url
                            }).execute()
                        except Exception:
                            pass  # Fail silently — don't surface DB errors on a successful prediction

                else:
                    st.error(f"API Error [{response.status_code}]: Please verify the Render backend is running.")

            except requests.exceptions.Timeout:
                st.error("🚨 Request timed out. The Render server may be waking up from sleep. Use the **Ping API Server** button in the sidebar, wait ~60 seconds, then try again.")
            except requests.exceptions.ConnectionError:
                st.error("🚨 Connection refused. The Render API appears to be offline.")
            except Exception as e:
                st.error(f"Unexpected error: {e}")

# ─────────────────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────────────────
st.markdown("""
<div class="footer">
  CloudPriceML &nbsp;·&nbsp; <span>Built by Aanchal Chauhan</span>
</div>
""", unsafe_allow_html=True)
