import streamlit as st
import pandas as pd
import joblib
import requests
import re
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import time

# ==========================================
# 1. KONFIGURASI HALAMAN & CUSTOM CSS
# ==========================================
st.set_page_config(page_title="SEPHIA Phishing Detector", page_icon="🛡️", layout="wide")

st.markdown("""
    <style>
    div.stButton > button:first-child {
        background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
        color: white !important; border: none; border-radius: 8px; padding: 10px 24px;
        font-size: 18px; font-weight: bold; width: 100%; transition: all 0.3s ease;
    }
    div.stButton > button:first-child:hover { transform: translateY(-2px); box-shadow: 0 6px 12px rgba(0,0,0,0.3); }
    div[data-testid="metric-container"] { 
        border: 1px solid rgba(128, 128, 128, 0.2); padding: 15px; border-radius: 10px; text-align: center; 
    }
    .main-header { text-align: center; font-weight: 800; margin-bottom: -10px; }
    .sub-header { text-align: center; font-size: 18px; margin-bottom: 30px; opacity: 0.8; }
    .veto-box { background-color: #fff3cd; color: #856404; padding: 15px; border-left: 6px solid #ffeeba; border-radius: 5px; margin-top: 15px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. LOGIKA DETEKSI (BACKEND)
# ==========================================
@st.cache_data(show_spinner=False)
def extract_features(url):
    features = {}
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
        
    parsed_url = urlparse(url)
    domain = parsed_url.netloc.lower()
    
    features['url_length'] = len(url)
    ip_pattern = r"(([01]?\d\d?|2[0-4]\d|25[0-5])\.([01]?\d\d?|2[0-4]\d|25[0-5])\.([01]?\d\d?|2[0-4]\d|25[0-5])\.([01]?\d\d?|2[0-4]\d|25[0-5])\/)|"
    features['has_ip'] = 1 if re.search(ip_pattern, url) else 0
    features['count_dash'] = url.count('-')
    features['count_at'] = url.count('@')
    features['is_https'] = 1 if parsed_url.scheme == 'https' else 0
    
    brand_db = {
        'paypal': 'paypal.com', 'google': 'google.com', 'facebook': 'facebook.com',
        'netflix': 'netflix.com', 'bca': 'klikbca.com', 'bri': 'bri.co.id',
        'mandiri': 'bankmandiri.co.id', 'dana': 'dana.id', 'bni': 'bni.co.id'
    }
    
    has_brand = 0; domain_match = 0; detected_brand = None
    
    for brand, official in brand_db.items():
        if brand in url.lower():
            has_brand = 1
            detected_brand = brand
            if domain.endswith(official): domain_match = 1
            else: domain_match = 0 
            break
            
    features['has_brand_name'] = has_brand
    features['domain_match'] = domain_match
    
    status_crawl = "Menunggu..."
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=3)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        links = soup.find_all('a', href=True)
        total = len(links)
        external = 0; null_link = 0
        
        if total > 0:
            for l in links:
                href = l['href']
                if href in ["#", "", "javascript:void(0)"]: null_link += 1
                elif domain not in href and href.startswith('http'): external += 1
            features['external_link_ratio'] = external / total
            features['null_link_ratio'] = null_link / total
        else:
            features['external_link_ratio'] = 0
            features['null_link_ratio'] = 0
            
        pass_field = soup.find_all('input', {'type': 'password'})
        features['has_password_field'] = 1 if len(pass_field) > 0 else 0
        status_crawl = "✅ Sukses (Online Analysis)"
    except:
        features['external_link_ratio'] = 0.85  
        features['null_link_ratio'] = 0.85      
        features['has_password_field'] = 1      
        status_crawl = "⚠️ Gagal (Website Offline / Diblokir - Otomatis Suspect)"

    return features, detected_brand, status_crawl

# ==========================================
# 3. TAMPILAN DASHBOARD (FRONTEND)
# ==========================================
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2092/2092663.png", width=80)
    st.title("SEPHIA (System for Ensemble Phishing & HTML Intelligent Analysis)")
    st.caption("Ver. 1.0 | Thesis Project")
    st.markdown("---")
    st.markdown("**Metode:**\n🔹 Hybrid ML (RF + XGBoost)\n🔹 Behavioral HTML Parsing\n🔹 Brand Override Logic")
    st.markdown("---")
    st.info("💡 **Petunjuk:** Masukkan URL yang mencurigakan ke kolom utama untuk dipindai.")

st.markdown("<h1 class='main-header'>🛡️ SEPHIA Phishing Detector</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-header'>Sistem Deteksi Website Palsu berbasis Kecerdasan Buatan & Analisis Struktur</p>", unsafe_allow_html=True)

try:
    model_data = joblib.load('model_final.pkl')
    model = model_data['model']
    expected_cols = model_data['features']
except:
    st.error("⚠️ Model belum siap! Jalankan `2_train_model.py` terlebih dahulu di terminal.")
    st.stop()

col_space1, col_input, col_space2 = st.columns([1, 4, 1])

with col_input:
    with st.form("scan_form"):
        url_input = st.text_input("URL Website:", placeholder="Tulis atau Paste URL di sini (contoh: http://klikbca-promo-hadiah.net)")
        submit_btn = st.form_submit_button("🚀 PINDAI WEBSITE")

st.markdown("---")

if submit_btn:
    if not url_input:
        st.warning("⚠️ Mohon masukkan URL terlebih dahulu!")
    else:
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        status_text.text("Menghubungi server website...")
        time.sleep(0.5)
        progress_bar.progress(30)
        
        status_text.text("Mengekstraksi DNA dan Struktur HTML...")
        features, brand, status = extract_features(url_input)
        progress_bar.progress(70)
        
        status_text.text("Memasukkan data ke Mesin AI...")
        time.sleep(0.5)
        
        df_input = pd.DataFrame([features])
        df_input = df_input.reindex(columns=expected_cols, fill_value=0)
        pred = model.predict(df_input)[0]
        proba = model.predict_proba(df_input)[0]
        confidence = proba[pred] * 100
        
        override_msg = ""
        is_vetoed = False
        if features['has_brand_name'] == 1 and features['domain_match'] == 0:
            pred = 1 
            confidence = 99.9
            is_vetoed = True
            override_msg = f"🛑 PROTOKOL KEAMANAN AKTIF: URL menggunakan nama '{brand.upper()}' tetapi domain tidak resmi!"

        progress_bar.progress(100)
        status_text.empty()
        progress_bar.empty()

        col_result, col_details = st.columns([1.2, 2])
        
        with col_result:
            st.subheader("🏁 Kesimpulan Akhir")
            if pred == 1:
                st.error("🚨 BERBAHAYA (PHISHING)")
                st.metric("Tingkat Keyakinan AI", f"{confidence:.1f}%", delta="- Risiko Tinggi", delta_color="inverse")
                if is_vetoed:
                    st.markdown(f"<div class='veto-box'>{override_msg}</div>", unsafe_allow_html=True)
            else:
                st.success("✅ AMAN (LEGITIMATE)")
                st.metric("Tingkat Keyakinan AI", f"{confidence:.1f}%", delta="+ Validasi Lolos")

        with col_details:
            st.subheader("📊 Rincian Analisis")
            tab_brand, tab_html, tab_debug = st.tabs(["🔒 Validasi Brand", "🌐 Struktur HTML", "⚙️ Data Jeroan (Debug)"])
            
            with tab_brand:
                if brand:
                    st.write(f"Sistem mendeteksi adanya penggunaan nama entitas: **{brand.upper()}**")
                    if features['domain_match'] == 1:
                        st.success("✔️ Domain ini diakui sebagai properti resmi dari brand tersebut.")
                    else:
                        st.error("❌ Indikasi Penipuan: Domain tidak terdaftar sebagai milik brand tersebut.")
                else:
                    st.info("ℹ️ Tidak ada penggunaan nama brand spesifik yang terdeteksi pada URL.")
                    
                if features['is_https'] == 1:
                    st.write("✔️ Koneksi dienkripsi (HTTPS).")
                else:
                    st.write("❌ Koneksi tidak aman (HTTP).")

            with tab_html:
                st.write(f"**Status Crawling:** {status}")
                colA, colB = st.columns(2)
                colA.metric("Link Keluar (External)", f"{features['external_link_ratio']*100:.1f}%")
                colB.metric("Link Rusak (Null/Dummy)", f"{features['null_link_ratio']*100:.1f}%")
                
                if features['has_password_field'] == 1:
                    st.warning("⚠️ Ditemukan form permintaan password pada halaman ini.")

            with tab_debug:
                st.markdown("*(Data mentah ini diekstrak dan dimasukkan ke dalam algoritma Random Forest & XGBoost)*")
                st.dataframe(df_input, use_container_width=True)