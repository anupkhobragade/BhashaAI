import os
import sys
os.environ["STREAMLIT_WATCH_FILE_SYSTEM"] = "false"

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import csv
from datetime import datetime
from io import BytesIO
from fpdf import FPDF
import streamlit as st
import requests
import pdfplumber
from gtts import gTTS

# Fix path issues when deploying

from utils.groq_api import query_groq
from utils.visitor_tracker import log_visit, get_today_count

# Set Streamlit config
st.set_page_config(page_title="BhashaAI", layout="wide")
st.sidebar.image("bhasha_logo.png", width=150)

# Log visitor
log_visit()

# Inject PWA metadata
st.markdown("""
<link rel="manifest" href="/manifest.json">
<link rel="icon" href="/icon-192.png">
<meta name="theme-color" content="#0b5cd1">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-title" content="BhashaAI">
<meta name="apple-mobile-web-app-status-bar-style" content="default">
<link rel="apple-touch-icon" href="/icon-192.png">
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div style='text-align: center;'>
    <h2 style='color: #FF671F;'>Bhasha AI</h2>
    <p style='color: #046A38; font-weight: bold; font-size: 20px;'>भारत का अपना ChatGPT</p>
</div>
""", unsafe_allow_html=True)

st.markdown("Simplify forms, legal docs, and English content in **your preferred Indian language**.")

st.sidebar.markdown(f"👁️ **Today's Visitors:** {get_today_count()}")

# Language Options
language = st.selectbox("🗣️ Output Language", [
    "Hindi", "Marathi", "Bengali", "Telugu", "Tamil",
    "Urdu", "Gujarati", "Malayalam", "Kannada", "Odia"
])

input_method = st.radio("📥 Choose Input Method", ["Upload PDF", "Paste Text"])
text = ""

# Handle Input
if input_method == "Upload PDF":
    pdf_file = st.file_uploader("Upload a PDF file", type=["pdf"])
    if pdf_file:
        try:
            with pdfplumber.open(pdf_file) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text
        except Exception as e:
            st.error("⚠️ Error reading PDF.")
            st.exception(e)
else:
    text = st.text_area("Paste your content here", height=200)

# Language prompt map
language_prompts = {
    "Hindi": "सरल और आसान हिंदी",
    "Marathi": "सोप्या आणि समजण्यासारख्या मराठीत",
    "Bengali": "সহজ এবং বোধগম্য বাংলা",
    "Telugu": "సులభంగా అర్థమయ్యే తెలుగు",
    "Tamil": "எளிமையான மற்றும் புரிந்துகொள்ளக்கூடிய தமிழ்",
    "Urdu": "سادہ اور قابل فہم اردو",
    "Gujarati": "સરળ અને સમજમાં આવતી ગુજરાતી",
    "Malayalam": "എളുപ്പവും മനസ്സിലാകുന്നതുമായ മലയാളം",
    "Kannada": "ಸರಳ ಮತ್ತು ಅರ್ಥವಾಗುವ ಕನ್ನಡ",
    "Odia": "ସହଜ ଓ ବୁଝିପାରିବା ଓଡ଼ିଆ"
}

lang_codes = {
    "Hindi": "hi", "Marathi": "mr", "Bengali": "bn", "Telugu": "te", "Tamil": "ta",
    "Urdu": "ur", "Gujarati": "gu", "Malayalam": "ml", "Kannada": "kn", "Odia": "or"
}

# PDF Generator
class UnicodePDF(FPDF):
    def header(self):
        self.set_font("Noto", size=12)

    def footer(self):
        self.set_y(-15)
        self.set_font("Noto", size=8)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")

def generate_pdf(text):
    pdf = UnicodePDF()

    font_path = os.path.join("assets", "NotoSansDevanagari-Regular.ttf")
    if not os.path.exists(font_path):
        raise FileNotFoundError("Font file missing. Please ensure 'NotoSansDevanagari-Regular.ttf' is in the assets/ folder.")

    pdf.add_font("Noto", "", font_path, uni=True)
    pdf.set_font("Noto", size=12)

    pdf.add_page()

    for line in text.split('\n'):
        pdf.multi_cell(0, 10, line)

    output = BytesIO()
    pdf.output(output)
    output.seek(0)
    return output

# Process translation
if text.strip():
    if st.button(f"🧠 Explain in {language}"):
        with st.spinner(f"Generating explanation in {language}..."):
            lang_prompt = language_prompts.get(language, language)
            prompt = f"""
तुम एक सहायक हो जो भारत के नागरिकों की सहायता करता है। कृपया नीचे दी गई सामग्री को {lang_prompt} में समझाओ ताकि सभी लोग उसे आसानी से समझ सकें।

सामग्री:
{text[:3000]}
"""
            output = query_groq(prompt, language)
            if output:
                st.subheader(f"🔍 {language} में व्याख्या:")
                st.write(output)

                # Download PDF
                try:
                    pdf_file = generate_pdf(output)
                    st.download_button(
                        label="⬇️ Download as PDF",
                        data=pdf_file,
                        file_name="bhashaai_output.pdf",
                        mime="application/pdf"
                    )
                except Exception as e:
                    st.error("PDF generation failed")
                    st.exception(e)

                # TTS
                try:
                    lang_code = lang_codes.get(language, "hi")
                    tts = gTTS(output, lang=lang_code)
                    audio_bytes = BytesIO()
                    tts.write_to_fp(audio_bytes)
                    audio_bytes.seek(0)
                    st.audio(audio_bytes, format="audio/mp3")
                    st.success("🎧 Voice generated successfully!")
                except Exception as e:
                    st.warning("⚠️ Could not generate voice output.")
                    st.exception(e)
else:
    st.info("कृपया PDF अपलोड करें या टेक्स्ट पेस्ट करें।")