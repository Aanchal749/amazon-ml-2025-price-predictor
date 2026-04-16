"""
CloudPriceML — SaaS Frontend Dashboard
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
    page_title="CloudPriceML — E-Commerce Price Predictor",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 🔥 YOUR LIVE RENDER BACKEND URL
API_URL = "https://amazon-ml-2025-price-predictor.onrender.com/predict"

# ─────────────────────────────────────────────────────────
# SUPABASE INITIALIZATION
# ─────────────────────────────────────────────────────────
@st.cache_resource
def init_supabase():
    try:
        url = st.secrets.get("SUPABASE_URL", "https://dqbirxwhitqijqlkbuzm.supabase.co")
        key = st.secrets.get("SUPABASE_KEY", "sb_publishable_zEoVhO0kCpcPxhEoYtYodw_13SniAKt")
        return create_client(url, key)
    except Exception:
        return None

supabase: Client = init_supabase()

# ─────────────────────────────────────────────────────────
# CUSTOM CSS
# ─────────────────────────────────────────────────────────
st.markdown("""
<style>
.main-header {
    background: linear-gradient(135deg, #1B3A6B 0%, #2563EB 100%);
    padding: 2rem 2.5rem;
    border-radius: 12px;
    margin-bottom: 2rem;
    color: white;
}
.main-header h1 { margin: 0; font-size: 2rem; font-weight: 700; }
.main-header p  { margin: 0.4rem 0 0; opacity: 0.85; font-size: 1rem; }
.metric-card { background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 10px; padding: 1.2rem 1.5rem; text-align: center; }
.metric-card .label { font-size: 0.78rem; color: #64748B; text-transform: uppercase; letter-spacing: 0.05em; }
.metric-card .value { font-size: 1.9rem; font-weight: 700; color: #1B3A6B; margin-top: 0.2rem; }
.price-result { background: linear-gradient(135deg, #1B3A6B, #2563EB); border-radius: 14px; padding: 2rem; text-align: center; color: white; margin-top: 1rem; }
.price-result .price-label { font-size: 0.9rem; opacity: 0.8; text-transform: uppercase; letter-spacing: 0.08em; }
.price-result .price-value { font-size: 3.2rem; font-weight: 800; margin: 0.3rem 0; }
.price-result .price-range { font-size: 0.85rem; opacity: 0.75; }
.badge { display: inline-block; padding: 0.25rem 0.75rem; border-radius: 999px; font-size: 0.78rem; font-weight: 600; }
.badge-high   { background: #DCFCE7; color: #15803D; }
.badge-medium { background: #FEF9C3; color: #854D0E; }
.badge-low    { background: #FEE2E2; color: #991B1B; }
.status-ok  { color: #15803D; font-weight: 600; }
.status-err { color: #DC2626; font-weight: 600; }
hr.divider { border: none; border-top: 1px solid #E2E8F0; margin: 1.5rem 0; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────
# CONSTANTS & HELPERS
# ─────────────────────────────────────────────────────────
BRANDS = ["Samsung", "Apple", "Sony", "LG", "Philips", "Bosch", "Havells", "Prestige", "Bajaj", "Whirlpool", "Godrej", "Amul", "Nestle", "Himalaya", "Patanjali", "Britannia", "Other / Unknown"]

def confidence_badge(cv: float) -> str:
    if cv < 0.15: return '<span class="badge badge-high">High Confidence</span>'
    elif cv < 0.30: return '<span class="badge badge-medium">Medium Confidence</span>'
    else: return '<span class="badge badge-low">Low Confidence</span>'

# ─────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ System Status")
    
    if supabase is not None:
        st.markdown('<p class="status-ok">✅ Supabase Connected</p>', unsafe_allow_html=True)
    else:
        st.markdown('<p class="status-err">⚠️ Supabase Offline</p>', unsafe_allow_html=True)

    st.markdown('<p class="status-ok">✅ API Linked: Render Cloud</p>', unsafe_allow_html=True)
    
    st.markdown("---")
    st.caption("CloudPriceML · Aanchal Chauhan · Dr. Pallavi Sapkale")

# ─────────────────────────────────────────────────────────
# MAIN HEADER
# ─────────────────────────────────────────────────────────
st.markdown("""
<div class="main-header">
  <h1>💰 CloudPriceML — E-Commerce Price Predictor</h1>
  <p>Production ML pipeline · Multimodal features · FastAPI Backend</p>
</div>
""", unsafe_allow_html=True)

m1, m2, m3, m4 = st.columns(4)
with m1: st.markdown('<div class="metric-card"><div class="label">OOF SMAPE</div><div class="value">23.4%</div></div>', unsafe_allow_html=True)
with m2: st.markdown('<div class="metric-card"><div class="label">Training Samples</div><div class="value">73.5k</div></div>', unsafe_allow_html=True)
with m3: st.markdown('<div class="metric-card"><div class="label">Feature Dims</div><div class="value">30,422</div></div>', unsafe_allow_html=True)
with m4: st.markdown('<div class="metric-card"><div class="label">Server</div><div class="value">Render</div></div>', unsafe_allow_html=True)

st.markdown("<hr class='divider'>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────
# MAIN LAYOUT — Input (left) | Result (right)
# ─────────────────────────────────────────────────────────
col_input, col_result = st.columns([3, 2], gap="large")

with col_input:
    st.markdown("### 📋 Product Details")
    catalog_content = st.text_area("Catalog Content *", placeholder="Example: Samsung 65-inch 4K QLED...", height=180)

    # ── Real Image Uploader & Storage ─────────────────────
    st.markdown("### 📸 Scan Product")
    uploaded_file = st.file_uploader("Upload product photo to analyze", type=["jpg", "jpeg", "png"])
    
    image_url = "" 
    
    if uploaded_file is not None:
        if supabase is not None:
            with st.spinner("Uploading to secure cloud vault..."):
                try:
                    file_bytes = uploaded_file.getvalue()
                    file_name = f"{int(time.time())}_{uploaded_file.name}"
                    
                    supabase.storage.from_("product_images").upload(
                        file_name, 
                        file_bytes, 
                        {"content-type": uploaded_file.type}
                    )
                    image_url = supabase.storage.from_("product_images").get_public_url(file_name)
                    st.success("Image uploaded successfully!")
                except Exception as e:
                    st.error(f"Upload failed: {e}")
        else:
            st.warning("⚠️ Cannot upload image. Supabase is not connected.")

    with st.expander("➕ Add Structured Hints (optional)"):
        h1, h2 = st.columns(2)
        with h1:
            brand = st.selectbox("Brand", BRANDS, index=16)
        with h2:
            ipq = st.number_input("Item Pack Quantity", min_value=1, value=1)
        hints = [h for h in [brand.lower() if brand != "Other / Unknown" else "", f"pack of {ipq}" if ipq > 1 else ""] if h]
        
        # Combine text before sending to API
        final_catalog_text = catalog_content
        if hints: 
            final_catalog_text += " " + " ".join(hints)

    st.markdown("")
    predict_clicked = st.button("🔮 Predict Price", type="primary", use_container_width=True, disabled=not catalog_content.strip())

# ─────────────────────────────────────────────────────────
# API INFERENCE & RESULT COLUMN
# ─────────────────────────────────────────────────────────
with col_result:
    st.markdown("### 📈 Prediction Result")

    if image_url:
        st.image(image_url, use_container_width=True, caption="Cloud Vision Ready")

    if predict_clicked:
        with st.spinner("Querying Render ML Backend..."):
            try:
                # 1. Prepare data to send to FastAPI
                files = {}
                if uploaded_file:
                    uploaded_file.seek(0)
                    files = {"image_file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                
                payload = {"catalog_content": final_catalog_text}

                # 2. Hit the Render API
                response = requests.post(API_URL, data=payload, files=files)

                # 3. Process the response
                if response.status_code == 200:
                    result = response.json()
                    price = result["predicted_price"]
                    cv = result["confidence_score"]
                    
                    # Ensure price_low and price_high exist or calculate them dynamically
                    price_low = max(0.01, price * 0.85)
                    price_high = price * 1.15
                    
                    st.markdown(f"""
                    <div class="price-result">
                      <div class="price-label">Predicted Price</div>
                      <div class="price-value">₹{price:,.2f}</div>
                      <div class="price-range">Range: ₹{price_low:,.2f} — ₹{price_high:,.2f}</div>
                    </div>
                    <div style="margin-top:0.8rem; text-align:center;">{confidence_badge(cv)}</div>
                    """, unsafe_allow_html=True)
                    
                    # 4. Log to Supabase Database
                    if supabase is not None:
                        try:
                            supabase.table('predictions').insert({
                                "product_details": final_catalog_text[:200], 
                                "predicted_price": price,
                                "confidence": cv,
                                "image_url": image_url
                            }).execute()
                            st.toast('✅ Prediction logged to database!')
                        except Exception as e:
                            st.warning(f"Could not save to database: {e}")
                else:
                    st.error(f"Backend Error [{response.status_code}]: {response.text}")
            
            except requests.exceptions.ConnectionError:
                st.error("🚨 Could not connect to the Render API. Is your backend fully deployed and awake?")
            except Exception as e:
                st.error(f"Prediction failed: {e}")

    elif not image_url:
        st.markdown("""
        <div style="border:2px dashed #CBD5E1; border-radius:12px; padding:3rem 1.5rem; text-align:center; color:#94A3B8;">
          <div style="font-size:2.5rem">💰</div>
          <div style="font-size:1rem; margin-top:0.5rem">Predicted price will appear here</div>
        </div>
        """, unsafe_allow_html=True)