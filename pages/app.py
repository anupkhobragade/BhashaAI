import os
os.environ["STREAMLIT_WATCH_FILE_SYSTEM"] = "false"
import streamlit as st
import requests
import pdfplumber
import sys
from io import BytesIO
from gtts import gTTS
from fpdf import FPDF

# Fix path issues when deploying
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from utils.groq_api import query_groq
from utils.visitor_tracker import log_visit, get_today_count

# Log and show visitor count
log_visit()
st.set_page_config(page_title="BhashaAI", layout="wide")
st.sidebar.image("bhasha_logo.png", width=150)
st.sidebar.success(f"👁️ Today's Visitors: {get_today_count()}")

# Inject PWA manifest and icons
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

# Branding
st.markdown("""
<div style='text-align: center;'>
    <h2 style='color: #FF671F;'>Bhasha AI</h2>
    <p style='color: #046A38; font-weight: bold; font-size: 20px;'>भारत का अपना ChatGPT</p>
</div>
""", unsafe_allow_html=True)

st.markdown("Simplify forms, legal docs, and English content in **your preferred Indian language**.")

# Language selection
language = st.selectbox("🗣️ Output Language", [
    "Hindi", "Marathi", "Bengali", "Telugu", "Tamil", 
    "Urdu", "Gujarati", "Malayalam", "Kannada", "Odia"
])

# Input method
input_method = st.radio("📥 Choose Input Method", ["Upload PDF", "Paste Text"])
text = ""

# Handle input
if input_method == "Upload PDF":
    pdf_file = st.file_uploader("Upload a PDF file", type=["pdf"])
    if pdf_file:
        with pdfplumber.open(pdf_file) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text
else:
    text = st.text_area("Paste your content here", height=200)

# Language prompt map
language_prompts = {
    "Hindi": "सरल और आसान हिंदी",
    "Marathi": "सोप्या आणि समजण्यासारख्य मराठीत",
    "Bengali": "সহজ এবং বোধগম্য বাংলা",
    "Telugu": "సులభంగా అర్థమయ్య తెలుగు",
    "Tamil": "எளிமையான மற்றும் புரிந்துகோள்ள தமிழ்",
    "Urdu": "سادہ اور قابل فہم اردو",
    "Gujarati": "સરળ અને સમજમા આવતી ગુજરાતી",
    "Malayalam": "എളുപ്പും മനസ്സിലാകുന്നതായ മലയാളം",
    "Kannada": "ಸರಳ ಮತ್ತು ಅರ್ಥವಾಗುವ ಕನ್ನಡ",
    "Odia": "ସହଜ ଓ ବୁଝିପାରିବା ଓଡ଼ିଆ"
}

lang_codes = {
    "Hindi": "hi", "Marathi": "mr", "Bengali": "bn", "Telugu": "te", "Tamil": "ta",
    "Urdu": "ur", "Gujarati": "gu", "Malayalam": "ml", "Kannada": "kn", "Odia": "or"
}

def generate_pdf(text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    for line in text.split('\n'):
        pdf.multi_cell(0, 10, line)
    output = BytesIO()
    pdf.output(output)
    output.seek(0)
    return output

if text.strip():
    if st.button("🧠 Explain in " + language):
        with st.spinner(f"Generating explanation in {language}..."):
            lang_prompt = language_prompts.get(language, language)
            prompt = f"""
तुम एक सहायक हो जो भारत के नागरिकों की सहायता करता है। कृपया नीचे दी गई सामग्री को {lang_prompt} में समझाओ ताकि सभी लोग उसे आसानी से समझ सकें।\n\nसामग्री:\n{text[:3000]}
"""
            output = query_groq(prompt, language)
            if output:
                st.subheader(f"🔍 {language} में व्याख्या:")
                st.write(output)

                # --- Download as PDF ---
                pdf_file = generate_pdf(output)
                st.download_button(
                    label="⬇️ Download as PDF",
                    data=pdf_file,
                    file_name="bhashaai_output.pdf",
                    mime="application/pdf"
                )

                # --- TTS Voice Support ---
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