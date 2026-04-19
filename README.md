# 💰 CloudPriceML: AI-Powered E-Commerce Valuation Engine

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-Frontend-FF4B4B.svg)](https://streamlit.io/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688.svg)](https://fastapi.tiangolo.com/)
[![Supabase](https://img.shields.io/badge/Supabase-Database-3ECF8E.svg)](https://supabase.io/)
[![Render](https://img.shields.io/badge/Render-Cloud_Deployed-000000.svg)](https://render.com/)

> **An enterprise-grade multimodal AI pipeline that predicts real-time market retail prices for e-commerce assets using visual and textual analysis.**

### 📸 Output Screenshot
![ML Output - Samsung TV](https://github.com/Aanchal749/amazon-ml-2025-price-predictor/blob/72faede1fb7cd99d4b72d44c3c0be181a4fb4586/output_imes/ml%20output%20sumsung%20tv.png)

---

## 🎯 Problem Statement
In the hyper-competitive e-commerce landscape, sellers struggle to price items optimally. Static rule-based pricing fails to account for asset condition, subtle brand variations, and current market trends. **CloudPriceML** bridges this gap by leveraging a Multimodal AI architecture (Vision + Text) trained on 75,000+ market data points to generate highly accurate, confidence-calibrated retail valuations instantly.

---

## ✨ Key Features
* **Multimodal Inference:** Analyzes both product catalog descriptions and visual assets (images) simultaneously for maximum context.
* **Neobrutalist Enterprise UI:** A high-contrast, responsive dashboard designed for professional sellers and analysts.
* **Cloud-Native Architecture:** Fully decoupled FastAPI backend and Streamlit frontend.
* **Zero-Downtime CI/CD:** Integrated Continuous Deployment pipeline pushing updates from GitHub directly to Render and Streamlit Cloud.
* **Secure Data Vault:** Live integration with Supabase for secure image hosting and prediction logging.

---

## 📸 System Output & Screenshots

## 📊 Project Visuals

### 1. 🖥️ The Dashboard  
![Dashboard Interface](https://raw.githubusercontent.com/Aanchal749/amazon-ml-2025-price-predictor/4a148d616caf4bc084bb2d71c6302739604208d9/output_imes/dashboard.png)  
*The main pricing intelligence interface featuring advanced metadata tuning.*

---

### 2. 🤖 AI Valuation Result  
*Generating a confidence-calibrated point estimate with market highs and lows.*

| CatBoost | XGBoost |
|----------|--------|
| ![](https://raw.githubusercontent.com/Aanchal749/amazon-ml-2025-price-predictor/4a148d616caf4bc084bb2d71c6302739604208d9/output_imes/CatBoost.png) | ![](https://raw.githubusercontent.com/Aanchal749/amazon-ml-2025-price-predictor/4a148d616caf4bc084bb2d71c6302739604208d9/output_imes/XGBoost.png) |

| LightGBM | Ensemble |
|----------|----------|
| ![](https://raw.githubusercontent.com/Aanchal749/amazon-ml-2025-price-predictor/4a148d616caf4bc084bb2d71c6302739604208d9/output_imes/lightGBM.png) | ![](https://raw.githubusercontent.com/Aanchal749/amazon-ml-2025-price-predictor/4a148d616caf4bc084bb2d71c6302739604208d9/output_imes/EnsembleWeight.png) |

---

### 📌 Additional Outputs

| Result 1 | Result 2 |
|----------|----------|
| ![](https://raw.githubusercontent.com/Aanchal749/amazon-ml-2025-price-predictor/4a148d616caf4bc084bb2d71c6302739604208d9/output_imes/Screenshot%202026-04-14%20113505.png) | ![](https://raw.githubusercontent.com/Aanchal749/amazon-ml-2025-price-predictor/4a148d616caf4bc084bb2d71c6302739604208d9/output_imes/Screenshot%202026-04-14%20113709.png) |

---

### 3. 🧩 Architecture Flow  
[View Architecture Diagram](https://drive.google.com/file/d/1-8gO2UkOI7zPR7fVjk9xln3Q_LGA1BLQ/view?usp=sharing)

## 🛠️ Tech Stack & Infrastructure
* **Frontend:** Streamlit, Custom CSS
* **Backend:** FastAPI, Python, Requests
* **AI Engine:** Google Gemini 1.5 Vision AI (Multimodal)
* **Cloud Database & Storage:** Supabase (PostgreSQL)
* **Hosting & CI/CD:** Render (Backend), Streamlit Cloud (Frontend)

---

## 🚀 Local Installation & Setup

If you wish to run this project on your local machine:

### 1️⃣ Clone the repository
```bash
git clone https://github.com/Aanchal749/amazon-ml-2025-price-predictor.git
cd amazon-ml-2025-price-predictor
