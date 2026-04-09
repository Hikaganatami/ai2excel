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
        api_key = st.secrets["GEMINI_API_KEY"]
        genai.configure(api_key=api_key)
        # Sürüm hatasını aşmak için en temel model ismini kullanıyoruz
        return genai.GenerativeModel('gemini-1.5-flash')
    except:
        return None

ai_engine = get_engine()

# Arayüz
st.title("🤖 UltraData AI: Akıllı Analist")

user_query = st.text_area("İşlem yapılacak metni girin:", height=200)

if st.button("Analiz Et ve Raporu Başlat ✨"):
    if user_query and ai_engine:
        with st.spinner('Yapay zeka analiz ediyor...'):
            try:
                prompt = f"Sen bir veri analistisin. Verilen metni analiz et ve sonucu SADECE CSV formatında tablo olarak döndür. Ek açıklama yapma: {user_query}"
                
                # API ÇAĞRISI
                response = ai_engine.generate_content(prompt)
                
                # Yanıtı işle
                text = response.text
                clean_text = re.sub(r'```csv\n|```', '', text).strip()
                
                # Eğer yanıt boş değilse tabloya çevir
                df = pd.read_csv(io.StringIO(clean_text))
                st.success("✅ İşlem Başarılı!")
                st.dataframe(df, use_container_width=True)
                
                # Excel
                excel_buffer = io.BytesIO()
                with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
                    df.to_excel(writer, index=False)
                
                st.download_button("📥 Excel İndir", data=excel_buffer.getvalue(), file_name="analiz.xlsx")
                
            except Exception as e:
                st.error(f"Sistem Hatası: {str(e)}")
                st.info("Eğer 404 hatası alıyorsanız, lütfen sağ alttan Reboot App yapın.")
    else:
        st.warning("Giriş yapın.")
