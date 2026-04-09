import streamlit as st
import pandas as pd
import google.generativeai as genai
import io
import re

# --- PANEL AYARLARI ---
st.set_page_config(page_title="UltraData AI", page_icon="🤖", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #f0f2f6; }
    .stTextArea textarea { color: #1e1e1e !important; background-color: #ffffff !important; border: 2px solid #1a73e8 !important; border-radius: 10px !important; }
    .stButton>button { width: 100%; background-color: #1a73e8 !important; color: white !important; font-weight: bold !important; height: 3.5em !important; border-radius: 10px !important; }
    </style>
    """, unsafe_allow_html=True)

# --- AKILLI MODEL SEÇİCİ ---
def get_working_model():
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
        genai.configure(api_key=api_key)
        
        # Mevcut modelleri listele ve en uygun olanı seç
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        
        # Tercih sırası: flash -> pro -> herhangi biri
        preferred = ['models/gemini-1.5-flash', 'models/gemini-1.5-pro', 'models/gemini-1.0-pro']
        
        for p in preferred:
            if p in models:
                return genai.GenerativeModel(p)
        
        # Hiçbiri yoksa listedeki ilk uygun modeli döndür
        if models:
            return genai.GenerativeModel(models[0])
        return None
    except Exception as e:
        st.error(f"Model Listeleme Hatası: {str(e)}")
        return None

ai_engine = get_working_model()

# --- ARAYÜZ ---
st.title("🤖 UltraData AI: Akıllı Analist")

user_query = st.text_area("İşlem yapılacak metni girin:", height=200)

if st.button("Analiz Et ve Raporu Başlat ✨"):
    if user_query and ai_engine:
        with st.spinner(f'Analiz ediliyor... ({ai_engine.model_name})'):
            try:
                prompt = f"Verilen metni analiz et ve sonucu SADECE CSV formatında tablo olarak döndür. Ek açıklama yapma: {user_query}"
                response = ai_engine.generate_content(prompt)
                
                text = response.text
                clean_text = re.sub(r'```csv\n|```', '', text).strip()
                
                df = pd.read_csv(io.StringIO(clean_text))
                st.success("✅ İşlem Başarılı!")
                st.dataframe(df, use_container_width=True)
                
                excel_buffer = io.BytesIO()
                with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
                    df.to_excel(writer, index=False)
                
                st.download_button("📥 Excel İndir", data=excel_buffer.getvalue(), file_name="analiz.xlsx")
                
            except Exception as e:
                st.error(f"İşlem Hatası: {str(e)}")
    else:
        st.warning("Lütfen giriş yapın veya API anahtarınızı kontrol edin.")

st.markdown("---")
st.caption("© 2026 Hikaganatami AI Solutions")
