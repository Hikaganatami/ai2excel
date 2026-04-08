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
    h1 { color: #1a73e8 !important; }
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
st.write("Senaryonuzu yazın, profesyonel Excel raporunuzu saniyeler içinde alın.")

user_query = st.text_area("İşlem yapılacak metni veya senaryoyu girin:", height=200, placeholder="Örn: 270 günlük kar maliyet tablosu yap...")

if st.button("Analiz Et ve Raporu Başlat ✨"):
    if user_query and ai_engine:
        with st.spinner('Yapay zeka verileri hesaplıyor...'):
            try:
                # Geliştirilmiş Prompt
                prompt = f"Sen bir veri analistisin. Verilen senaryoyu analiz et ve sonucu SADECE CSV formatında döndür. Ek açıklama yapma: {user_query}"
                response = ai_engine.generate_content(prompt)
                
                # Temizleme ve Tablo Oluşturma
                text = response.text
                csv_match = re.search(r'((?:[^,]+,)+[^,\n]+\n(?:[^,]+,)+[^,\n]+)', text, re.DOTALL)
                
                if csv_match:
                    # BURASI DÜZELTİLDİ: Parantezler tek tek kapatıldı.
                    clean_data = csv_match.group(0).strip()
                    df = pd.read_csv(io.StringIO(clean_data))
                    
                    st.success("✅ Veri Başarıyla Çözümlendi!")
                    st.dataframe(df, use_container_width=True)
                    
                    # Excel Çıktısı
                    excel_buffer = io.BytesIO()
                    with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
                        df.to_excel(writer, index=False)
                    
                    st.download_button(
                        label="📥 Excel Raporunu İndir",
                        data=excel_buffer.getvalue(),
                        file_name="AI_Analiz_Raporu.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                else:
                    st.error("AI tablo formatı oluşturamadı. Lütfen senaryoyu daha net yazın.")
            except Exception as e:
                st.error(f"Hata oluştu: {str(e)}")
    else:
        st.warning("Lütfen bir giriş yapın.")

st.markdown("---")
st.caption("© 2026 Hikaganatami AI Solutions")
