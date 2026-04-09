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

# --- MODEL SEÇİCİ ---
def get_working_model():
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
        genai.configure(api_key=api_key)
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        preferred = ['models/gemini-1.5-flash', 'models/gemini-1.5-pro', 'models/gemini-1.0-pro']
        for p in preferred:
            if p in models: return genai.GenerativeModel(p)
        return genai.GenerativeModel(models[0]) if models else None
    except: return None

ai_engine = get_working_model()

# --- ARAYÜZ ---
st.title("🤖 UltraData AI: Akıllı Analist")
user_query = st.text_area("İşlem yapılacak metni girin:", height=200, placeholder="Örn: 10 günlük kar tablosu yap...")

if st.button("Analiz Et ve Raporu Başlat ✨"):
    if user_query and ai_engine:
        with st.spinner('Analiz ediliyor...'):
            try:
                # Prompt: AI'ya CSV yapısını bozmaması için kesin talimat veriyoruz
                prompt = f"Verilen metni analiz et. Sonucu sadece virgülle ayrılmış (CSV) tablo olarak ver. Sütun sayısı her satırda aynı olsun. Ek açıklama yapma. Senaryo: {user_query}"
                response = ai_engine.generate_content(prompt)
                
                # Temizleme
                text = response.text
                clean_text = re.sub(r'```csv\n|```', '', text).strip()
                
                # HATA ÇÖZÜCÜ OKUMA: Eğer standart okuma hata verirse, boşluklara göre böl
                try:
                    df = pd.read_csv(io.StringIO(clean_text), sep=None, engine='python', on_bad_lines='skip')
                except:
                    # En kötü durumda veriyi satır satır bölüp zorla tablo yap
                    lines = [l.split(',') for l in clean_text.split('\n') if ',' in l]
                    df = pd.DataFrame(lines[1:], columns=lines[0])

                if not df.empty:
                    st.success("✅ İşlem Başarılı!")
                    st.dataframe(df, use_container_width=True)
                    
                    excel_buffer = io.BytesIO()
                    with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
                        df.to_excel(writer, index=False)
                    
                    st.download_button("📥 Excel İndir", data=excel_buffer.getvalue(), file_name="analiz.xlsx")
                else:
                    st.error("Veri tabloya dönüştürülemedi.")
                
            except Exception as e:
                st.error(f"İşlem Hatası: {str(e)}")
    else:
        st.warning("Lütfen giriş yapın.")

st.markdown("---")
st.caption("© 2026 Hikaganatami AI Solutions")
