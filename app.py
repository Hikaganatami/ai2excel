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

# --- AI MOTORU YAPILANDIRMASI (HATA DÜZELTİLDİ) ---
def get_engine():
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
        genai.configure(api_key=api_key)
        # Sürüm çakışmasını önlemek için model ismini en yalın haliyle kullanıyoruz
        return genai.GenerativeModel('gemini-1.5-flash')
    except Exception as e:
        return None

ai_engine = get_engine()

# Arayüz
st.title("🤖 UltraData AI: Akıllı Analist")
st.write("Verilerinizi profesyonel Excel raporlarına dönüştürün.")

user_query = st.text_area("İşlem yapılacak metni girin:", height=200, placeholder="Örn: 27 günlük maliyet tablosu yap...")

if st.button("Analiz Et ve Raporu Başlat ✨"):
    if user_query and ai_engine:
        with st.spinner('Yapay zeka analiz ediyor...'):
            try:
                # Talimat
                prompt = f"Sen bir veri analistisin. Verilen metni analiz et ve sonucu SADECE CSV formatında tablo olarak döndür. Ek açıklama yapma: {user_query}"
                
                # İçerik Üretimi (Eski sürüm hatalarını önlemek için doğrudan çağrım)
                response = ai_engine.generate_content(prompt)
                
                # Metni temizleme
                text = response.text
                
                # Gelişmiş CSV Ayıklama (Satır başlarını ve virgülleri arar)
                csv_pattern = r'([a-zA-Z0-9_,.\s\nğüşıöçĞÜŞİÖÇ]+,[a-zA-Z0-9_,.\s\nğüşıöçĞÜŞİÖÇ]+)'
                csv_match = re.search(csv_data_pattern if 'csv_data_pattern' in locals() else r'((?:[^,]+,)+[^,\n]+\n(?:[^,]+,)+[^,\n]+)', text, re.DOTALL)
                
                if csv_match:
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
                    # Alternatif temizleme: Markdown bloklarını sil
                    clean_text = re.sub(r'```csv\n|```', '', text).strip()
                    df = pd.read_csv(io.StringIO(clean_text))
                    st.success("✅ Veri Başarıyla Çözümlendi!")
                    st.dataframe(df, use_container_width=True)
            except Exception as e:
                # Eğer hala 404 verirse, kütüphane versiyonu hatasıdır
                st.error(f"Sistem Hatası: {str(e)}")
                st.info("İpucu: Eğer 404 alıyorsanız, lütfen Streamlit panelinden uygulamayı 'Reboot' edin.")
    else:
        st.warning("Lütfen bir giriş yapın.")

st.markdown("---")
st.caption("© 2026 Hikaganatami AI Solutions")
