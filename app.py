import streamlit as st
import pandas as pd
import google.generativeai as genai
import io

# --- PANEL AYARLARI ---
st.set_page_config(
    page_title="Veri Yönetim Sistemi",
    page_icon="📊",
    layout="wide"
)

# Profesyonel Görünüm İçin Stil
st.markdown("""
    <style>
    .stButton>button {
        width: 100%;
        background-color: #1a73e8;
        color: white;
        height: 3em;
        font-weight: bold;
    }
    .stTextArea textarea {
        background-color: #f8f9fa;
    }
    </style>
    """, unsafe_allow_html=True)

# --- SİSTEM MOTORU ---
def başlat():
    try:
        # Anahtar güvenli alandan çekiliyor
        anahtar = st.secrets["GEMINI_API_KEY"]
        genai.configure(api_key=anahtar)
        return genai.GenerativeModel('gemini-1.5-flash')
    except:
        st.error("Sistem yapılandırma hatası. Lütfen yöneticiye başvurun.")
        return None

motor = başlat()

# --- ARAYÜZ ---
st.title("📊 Profesyonel Veri Dönüştürücü")
st.info("Karmaşık metin girişlerini analiz ederek saniyeler içinde düzenli raporlar oluşturur.")

giriş_metni = st.text_area(
    "Analiz edilecek veriyi buraya girin:", 
    height=250,
    placeholder="Örnek: Bugün 10 adet ürün A satıldı birim fiyat 100 TL, dün ise 5 adet ürün B iade edildi..."
)

if st.button("Veriyi Analiz Et ve Tabloyu Hazırla"):
    if giriş_metni and motor:
        with st.spinner('Veri yapısı çözümleniyor...'):
            try:
                # Veri işleme komutu
                komut = "Aşağıdaki metni analiz et ve sadece CSV formatında tablo verisi döndür. Başka hiçbir açıklama ekleme: "
                yanıt = motor.generate_content(komut + giriş_metni)
                
                # Çıktı temizleme
                temiz_veri = yanıt.text.replace("```csv", "").replace("```", "").strip()
                df = pd.read_csv(io.StringIO(temiz_veri))
                
                st.success("✅ Veri başarıyla işlendi.")
                st.dataframe(df, use_container_width=True)
                
                # Excel oluşturma (Bellekte)
                excel_yolu = io.BytesIO()
                with pd.ExcelWriter(excel_yolu, engine='xlsxwriter') as writer:
                    df.to_excel(writer, index=False, sheet_name='AnalizRaporu')
                
                # İndirme Butonu
                st.download_button(
                    label="📥 Hazırlanan Excel Dosyasını İndir",
                    data=excel_yolu.getvalue(),
                    file_name="analiz_raporu.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            except:
                st.warning("Veri işlenirken bir sorun oluştu. Lütfen metni daha net yazmayı deneyin.")
    else:
        st.warning("Lütfen işlem yapmak için bir veri girişi yapın.")

st.markdown("---")
st.caption("© 2026 Hikaganatami Veri Çözümleri - Tüm hakları saklıdır.")
