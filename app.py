import streamlit as st
import pandas as pd
import google.generativeai as genai
import io
import re

# --- PANEL AYARLARI ---
st.set_page_config(page_title="UltraData AI", page_icon="🤖", layout="wide")

# Tasarım (CSS)
st.markdown("""
    <style>
    .stApp { background-color: #f0f2f6; }
    .stTextArea textarea { color: #1e1e1e !important; background-color: #ffffff !important; border: 2px solid #1a73e8 !important; border-radius: 10px !important; }
    .stButton>button { width: 100%; background-color: #1a73e8 !important; color: white !important; font-weight: bold !important; height: 3.5em !important; border-radius: 10px !important; }
    </style>
    """, unsafe_allow_html=True)

# AI Motoru
def get_engine():
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        return genai.GenerativeModel('gemini-1.5-flash')
    except:
        return None

ai_engine = get_engine()

# Arayüz
st.title("🤖 UltraData AI: Akıllı Analist")
user_query = st.text_area("Senaryonuzu yazın:", height=200, placeholder="Örn: 270 günlük ekmek alım satım tablosu yap...")

if st.button("Analiz Et ve Raporu Başlat ✨"):
    if user_query and ai_engine:
        with st.spinner('AI analiz ediyor...'):
            try:
                # Geliştirilmiş Prompt
                prompt = f"""
                Sen bir veri analistisin. Verilen senaryoyu analiz et ve sonucu sadece CSV formatında döndür.
                Ek açıklama veya giriş cümlesi kurma, sadece tabloyu ver.
                Senaryo: {user_query}
                """
                response = ai_engine.generate_content(prompt)
                
                # Temizleme Algoritması
                text = response.text
                # Markdown'dan arındır ve sadece tabloyu bul
                csv_data = re.search(r'((?:[^,]+,)+[^,\n]+\n(?:[^,]+,)+[^,\n]+)', text, re.DOTALL)
                
                if csv_data:
                    df = pd.read_csv(io.StringIO(csv_data.group(0
