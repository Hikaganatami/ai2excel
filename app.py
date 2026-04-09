import streamlit as st
import pandas as pd
import google.generativeai as genai
import io
import re

# Page Config
st.set_page_config(page_title="UltraData AI Premium", page_icon="💎", layout="wide")

# Elite UI Design (Dark & Neon Theme)
st.markdown("""
    <style>
    /* Ana Arka Plan */
    .stApp {
        background: radial-gradient(circle, #1a1a2e 0%, #16213e 100%);
        color: #e94560;
    }
    
    /* Üst Başlık Stili */
    h1 {
        font-family: 'Inter', sans-serif;
        font-weight: 800;
        letter-spacing: -1px;
        color: #00d2ff !important;
        text-shadow: 0px 0px 15px rgba(0, 210, 255, 0.4);
    }

    /* Input Alanı (Glassmorphism) */
    .stTextArea textarea {
        color: #ffffff !important;
        background-color: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(0, 210, 255, 0.3) !important;
        border-radius: 15px !important;
        font-size: 16px !important;
        backdrop-filter: blur(10px);
        selection-background-color: #00d2ff;
    }

    /* Buton Tasarımı */
    .stButton>button {
        width: 100%;
        background: linear-gradient(90deg, #00d2ff 0%, #3a7bd5 100%) !important;
        color: white !important;
        font-weight: 700 !important;
        text-transform: uppercase;
        letter-spacing: 1px;
        border: none !important;
        border-radius: 12px !important;
        padding: 15px !important;
        transition: all 0.3s ease-in-out !important;
    }

    .stButton>button:hover {
        transform: translateY(-3px);
        box-shadow: 0px 10px 20px rgba(0, 210, 255, 0.4);
    }

    /* Analiz Yazıları ve Spinner */
    .stSpinner > div > div {
        border-top-color: #00d2ff !important;
    }
    
    div[data-testid="stMarkdownContainer"] p {
        color: #ffffff !important;
        opacity: 0.9;
    }

    /* Tablo Görünümü */
    [data-testid="stDataFrame"] {
        background-color: rgba(255, 255, 255, 0.02);
        border-radius: 15px;
        padding: 10px;
    }
    
    /* Başarı Mesajı */
    .stAlert {
        background-color: rgba(0, 210, 255, 0.1) !important;
        color: #00d2ff !important;
        border: 1px solid #00d2ff !important;
    }
    </style>
    """, unsafe_allow_html=True)

def initialize_engine():
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        priority = ['models/gemini-1.5-flash', 'models/gemini-1.5-pro']
        for p in priority:
            if p in models: return genai.GenerativeModel(p)
        return genai.GenerativeModel(models[0]) if models else None
    except: return None

engine = initialize_engine()

# UI Layout
st.title("💎 UltraData AI Premium")
st.markdown("##### Next-generation financial analysis and data conversion framework.")

query = st.text_area("", height=250, placeholder="Paste your data or scenario here. Example: '270-day profit analysis with 82% inflation...'")

if st.button("EXECUTE ANALYSIS"):
    if query and engine:
        with st.spinner('Synchronizing with AI Neural Network...'):
            try:
                instruction = "Act as a senior data analyst. Process the following data and return ONLY a valid CSV. No conversational text."
                response = engine.generate_content(f"{instruction}\n\nData: {query}")
                
                output = response.text
                clean_csv = re.sub(r'```csv\n|```', '', output).strip()
                
                try:
                    df = pd.read_csv(io.StringIO(clean_csv), sep=None, engine='python', on_bad_lines='skip')
                except:
                    lines = [l.split(',') for l in clean_csv.split('\n') if ',' in l]
                    df = pd.DataFrame(lines[1:], columns=lines[0])

                if not df.empty:
                    st.success("COMPUTATION SUCCESSFUL")
                    st.dataframe(df, use_container_width=True)
                    
                    buf = io.BytesIO()
                    with pd.ExcelWriter(buf, engine='xlsxwriter') as writer:
                        df.to_excel(writer, index=False)
                    
                    st.download_button("EXPORT TO EXCEL (.XLSX)", data=buf.getvalue(), file_name="ai_analysis_report.xlsx")
                else:
                    st.error("Engine failed to parse the data structure.")
            except Exception as e:
                st.error(f"System Error: {str(e)}")
    else:
        st.warning("Action required: Please provide input data.")

st.markdown("---")
st.caption("Hikaganatami AI Framework | Licensed under MIT | v3.0 Premium Edition")
