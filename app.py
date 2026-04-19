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
        # We are bypassing secrets and hardcoding the values so it connects instantly!
        url = "https://dqbirxwhitqijqlkbuzm.supabase.co"
        key = "sb_publishable_zEoVhO0kCpcPxhEoYtYodw_13SniAKt"
        return create_client(url, key)
    except Exception as e:
        st.error(f"DATABASE CRASH REASON: {e}")
        return None

supabase: Client = init_supabase()

# ─────────────────────────────────────────────────────────
# PREMIUM CSS STYLING
# ─────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #0f172a 0%, #3b82f6 100%);
        padding: 2.5rem;
        border-radius: 16px;
        margin-bottom: 2rem;
        color: white;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    .main-header h1 { margin: 0; font-size: 2.5rem; font-weight: 800; letter-spacing: -0.02em; }
    .main-header p  { margin: 0.5rem 0 0; opacity: 0.9; font-size: 1.1rem; font-weight: 300; }
    .metric-card { background: white; border: 1px solid #e2e8f0; border-radius: 12px; padding: 1.5rem; text-align: center; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
    .metric-card .label { font-size: 0.8rem; color: #64748b; text-transform: uppercase; letter-spacing: 0.05em; font-weight: 600; }
    .metric-card .value { font-size: 2rem; font-weight: 800; color: #0f172a; margin-top: 0.5rem; }
    .price-result { background: linear-gradient(135deg, #10b981, #059669); border-radius: 16px; padding: 2.5rem; text-align: center; color: white; margin-top: 1rem; box-shadow: 0 10px 15px -3px rgba(16, 185, 129, 0.3); }
    .price-result .price-label { font-size: 1rem; opacity: 0.9; text-transform: uppercase; letter-spacing: 0.1em; font-weight: 600; }
    .price-result .price-value { font-size: 4rem; font-weight: 900; margin: 0.5rem 0; line-height: 1; }
    .price-result .price-range { font-size: 1rem; opacity: 0.85; font-weight: 500; }
    .status-ok  { color: #10b981; font-weight: 600; display: flex; align-items: center; gap: 0.5rem; }
    .status-err { color: #ef4444; font-weight: 600; display: flex; align-items: center; gap: 0.5rem; }
    hr.divider { border: none; border-top: 1px solid #e2e8f0; margin: 2rem 0; }
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

    st.markdown('<div class="status-ok">🟢 API: Render Cloud Linked</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Server Wake-Up Button
    st.markdown("#### Cloud Management")
    if st.button("⚡ Ping API Server (Wake Up)"):
        with st.spinner("Pinging Render..."):
            if check_backend_health():
                st.success("Server is awake and ready!")
            else:
                st.error("Server is sleeping or unreachable. Give it 60 seconds and try again.")
    
    st.markdown("---")
    st.caption("Built by Aanchal Chauhan & Team | Guided by Dr. Pallavi Sapkale")

# ─────────────────────────────────────────────────────────
# MAIN HEADER
# ─────────────────────────────────────────────────────────
st.markdown("""
<div class="main-header">
  <h1>CloudPriceML</h1>
  <p>AI-Powered E-Commerce Valuation Engine</p>
</div>
""", unsafe_allow_html=True)

m1, m2, m3 = st.columns(3)
with m1: st.markdown('<div class="metric-card"><div class="label">Algorithm</div><div class="value">Multimodal</div></div>', unsafe_allow_html=True)
with m2: st.markdown('<div class="metric-card"><div class="label">Training Data</div><div class="value">75k+ Assets</div></div>', unsafe_allow_html=True)
with m3: st.markdown('<div class="metric-card"><div class="label">Server</div><div class="value">Render API</div></div>', unsafe_allow_html=True)

st.markdown("<hr class='divider'>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────
# MAIN LAYOUT — Input (left) | Result (right)
# ─────────────────────────────────────────────────────────
col_input, col_result = st.columns([1.2, 1], gap="large")

with col_input:
    st.markdown("### 1. Product Details")
    catalog_content = st.text_area("Enter full product description:", placeholder="e.g., Samsung 65-inch 4K Smart QLED TV with Quantum HDR...", height=150)

    st.markdown("### 2. Product Image")
    uploaded_file = st.file_uploader("Upload an image for visual analysis", type=["jpg", "jpeg", "png"])
    
    image_url = "" 
    
    if uploaded_file is not None:
        if supabase is not None:
            with st.spinner("Securing image in cloud vault..."):
                try:
                    file_bytes = uploaded_file.getvalue()
                    file_name = f"scan_{int(time.time())}_{uploaded_file.name}"
                    
                    supabase.storage.from_("product_images").upload(
                        file_name, 
                        file_bytes, 
                        {"content-type": uploaded_file.type}
                    )
                    image_url = supabase.storage.from_("product_images").get_public_url(file_name)
                    st.success("Image secured!")
                except Exception as e:
                    st.error(f"Could not upload image. Supabase Error: {e}")
        else:
            st.warning("⚠️ Database disconnected. Image won't be saved.")

    with st.expander("🛠️ Advanced Metadata (Optional)"):
        h1, h2 = st.columns(2)
        with h1:
            brand = st.selectbox("Brand Name", BRANDS)
        with h2:
            ipq = st.number_input("Package Quantity", min_value=1, value=1)
        
        hints = []
        if brand and brand != "Select a Brand..." and brand != "Other / Unknown":
            hints.append(brand.lower())
        if ipq > 1:
            hints.append(f"pack of {ipq}")
            
        final_catalog_text = catalog_content
        if hints: 
            final_catalog_text += " " + " ".join(hints)

    st.markdown("<br>", unsafe_allow_html=True)
    predict_clicked = st.button("Generate Valuation 🔮", type="primary", use_container_width=True, disabled=not catalog_content.strip())

# ─────────────────────────────────────────────────────────
# API INFERENCE & RESULT COLUMN
# ─────────────────────────────────────────────────────────
with col_result:
    st.markdown("### Valuation Report")

    if not predict_clicked and not image_url:
        st.info("👈 Fill out the product details and click Generate Valuation to see results.")

    if image_url:
        st.image(image_url, use_container_width=True, caption="Visual Asset Analyzed")

    if predict_clicked:
        with st.spinner("Running AI models on Render server..."):
            try:
                # 1. Prepare data
                files = {}
                if uploaded_file:
                    uploaded_file.seek(0)
                    files = {"image_file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                
                payload = {"catalog_content": final_catalog_text}

                # 2. Hit the Render API (with a 30-second timeout)
                response = requests.post(API_URL, data=payload, files=files, timeout=30)

                # 3. Process the response
                if response.status_code == 200:
                    result = response.json()
                    price = result.get("predicted_price", 0)
                    
                    price_low = max(0.01, price * 0.85)
                    price_high = price * 1.15
                    
                    st.markdown(f"""
                    <div class="price-result">
                      <div class="price-label">Suggested Retail Price</div>
                      <div class="price-value">₹{price:,.2f}</div>
                      <div class="price-range">Confidence Range: ₹{price_low:,.2f} — ₹{price_high:,.2f}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # 4. Log to Supabase Database
                    if supabase is not None:
                        try:
                            supabase.table('predictions').insert({
                                "product_details": final_catalog_text[:250], 
                                "predicted_price": price,
                                "image_url": image_url
                            }).execute()
                        except Exception:
                            pass # Fail silently for the user, no need to show DB errors on success
                else:
                    st.error(f"API Error [{response.status_code}]: Please check if the Render backend is running.")
            
            except requests.exceptions.Timeout:
                st.error("🚨 Request timed out. The Render server might be waking up from sleep. Click the 'Ping API Server' button in the sidebar and try again in 1 minute.")
            except requests.exceptions.ConnectionError:
                st.error("🚨 Connection Refused. The Render API is currently offline.")
            except Exception as e:
                st.error(f"An unexpected error occurred: {e}")
