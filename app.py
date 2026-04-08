import streamlit as st
import pandas as pd
import google.generativeai as genai
import io
import re

# --- GELİŞMİŞ PANEL AYARLARI ---
st.set_page_config(
    page_title="UltraData AI - Akıllı Analiz",
    page_icon="🤖",
    layout="wide"
)

# --- TASARIM VE GÖRÜNÜRLÜK DÜZENLEMELERİ (CSS) ---
st.markdown("""
    <style>
    /* Ana Arka Plan */
    .stApp {
        background-color: #f0f2f6;
    }
    /* Metin Kutusu Düzenleme (Beyaz zemin, Siyah yazı) */
    .stTextArea textarea {
        color: #1e1e1e !important;
        background-color: #ffffff !important;
        font-size: 16px !important;
        border: 2px solid #1a73e8 !important;
        border-radius: 10px !important;
    }
    /* Başlıklar ve Yazılar */
    h1, h2, h3, p, span {
        color: #1e1e1e !important;
    }
    /* Buton Tasarımı */
    .stButton>button {
        width: 100%;
        background-color: #1a73e8 !important;
        color: white !important;
        font-weight: bold !important;
        height: 3.5em !important;
        border-radius: 10px !important;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #0d47a1 !important;
        box-shadow: 0px 4px 15px rgba(0,0,0,0.2);
    }
    /* Tablo Önizleme Alanı */
    .stDataFrame {
        background-color: white;
        padding: 10px;
        border-radius: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- SİSTEM MOTORU (AI YAPILANDIRMASI) ---
def setup_engine():
    try:
        if "GEMINI_API_KEY" in st.secrets:
            api_key = st.secrets["GEMINI_API_KEY"]
            genai.configure(api_key=api_key)
            return genai.GenerativeModel('gemini-1.5-flash')
        else:
            st.error("API Anahtarı bulunamadı! Secrets kısmını kontrol edin.")
            return None
    except Exception as e:
        st.error(f"Bağlantı Hatası: {str(e)}")
        return None

ai_engine = setup_engine()

# --- ARAYÜZ ---
st.title("🤖 UltraData AI: Akıllı Senaryo Analisti")
st.markdown("Metin girişlerini analiz eder, hesaplamaları yapar ve profesyonel Excel raporlarına dönüştürür.")

# Yan yana kolonlar
col1, col2 = st.columns([2, 1])

with col1:
    user_query = st.text_area(
        "Senaryonuzu veya verilerinizi buraya yazın:", 
        height=300,
        placeholder="Örn: Günde 17 liradan 27 ekmek alıyorum. 270 gün boyunca bu ekmeği 19 liradan satıyorum. 10 günde bir de 3 lira indirim yapıyorum. Bunu tablo yap..."
    )

with col2:
    st.markdown("""
    ### 🛠️ Neler Yapabilirim?
    * **Karmaşık Hesaplamalar:** Kar/zarar, stok ve maliyet analizlerini hesaplar.
    * **Senaryo Analizi:** Günlük, haftalık veya aylık periyotlar oluşturur.
    * **Veri Temizleme:** Karışık notları düzenli sütunlara böler.
    * **Excel Çıktısı:** Hazırlanan analizi saniyeler içinde indirmenizi sağlar.
    """)

if st.button("Analiz Et ve Raporu Başlat ✨"):
    if user_query and ai_engine:
        with st.spinner('Yapay zeka senaryoyu hesaplıyor ve tablo oluşturuyor...'):
            try:
                # DAHA GÜÇLÜ PROMPT (Talimat)
                system_instruction = (
                    "Sen profesyonel bir veri analistisin. Kullanıcının verdiği senaryoyu matematiksel olarak hesapla. "
                    "Sonucu SADECE CSV formatında bir tablo olarak ver. Ek açıklama yapma. "
                    "Eğer senaryo uzun bir süreyi (örneğin 270 gün) kapsıyorsa, tabloyu mantıklı aralıklarla veya gün gün özetle. "
                    "Sütun isimleri net ve Türkçe olsun. Yanıtın sadece CSV verisi içermeli: "
                )
                
                response = ai_engine.generate_content(system_instruction + user_query)
                
                # CSV Verisini Temizleme (Markdown kod bloklarını temizle)
                clean_csv = re.sub(r'```csv\n|```', '', response.text).strip()
                
                # DataFrame Oluşturma
                df = pd.read_csv(io.StringIO(clean_csv))
                
                st.success("✅ Analiz başarıyla tamamlandı!")
                st.subheader("📊 Analiz Sonucu (Önizleme)")
                st.dataframe(df, use_container_width=True)
                
                # Excel Dosyası Hazırlama
                excel_data = io.BytesIO()
                with pd.ExcelWriter(excel_data, engine='xlsxwriter') as writer:
                    df.to_excel(writer, index=False, sheet_name='AI_Analiz_Raporu')
                
                st.download_button(
                    label="📥 Profesyonel Excel Raporunu İndir",
                    data=excel_data.getvalue(),
                    file_name="AI_Veri_Analizi.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            except Exception as e:
                st.error("Veri işlenirken bir hata oluştu. Lütfen daha net bir senaryo yazmayı deneyin.")
                st.info("İpucu: 'CSV formatında gün bazlı tablo yap' gibi eklemeler yapabilirsiniz.")
    else:
        st.warning("Lütfen işlem yapmak için bir metin veya senaryo girin.")

st.markdown("---")
st.caption("© 2026 Hikaganatami AI Solutions | Developed for Professional Data Management")
