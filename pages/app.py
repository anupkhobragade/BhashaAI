import os
import sys
import textwrap
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
from textwrap import wrap

from utils.groq_api import query_groq
from utils.visitor_tracker import log_visit, get_today_count

# Text preprocessing function
def preprocess_text(text):
    """Clean and preprocess text for better rendering"""
    # Remove problematic characters
    text = text.replace('\u200d', '').replace('\u200c', '')  # Zero-width characters
    text = text.replace('\ufeff', '')  # BOM character
    text = text.replace('â€™', "'").replace('â€œ', '"').replace('â€', '"')  # Encoding fixes
    
    # Normalize whitespace
    text = ' '.join(text.split())
    
    return text

# Font configuration for different languages
def get_font_for_language(language):
    """Return appropriate font settings for different languages"""
    font_configs = {
        "Hindi": {"font": "NotoSansDevanagari-Regular.ttf", "encoding": "utf-8"},
        "Marathi": {"font": "NotoSansDevanagari-Regular.ttf", "encoding": "utf-8"},
        "Bengali": {"font": "NotoSansDevanagari-Regular.ttf", "encoding": "utf-8"},
        "Telugu": {"font": "NotoSansDevanagari-Regular.ttf", "encoding": "utf-8"},
        "Tamil": {"font": "NotoSansDevanagari-Regular.ttf", "encoding": "utf-8"},
        "Urdu": {"font": "NotoSansDevanagari-Regular.ttf", "encoding": "utf-8"},
        "Gujarati": {"font": "NotoSansDevanagari-Regular.ttf", "encoding": "utf-8"},
        "Malayalam": {"font": "NotoSansDevanagari-Regular.ttf", "encoding": "utf-8"},
        "Kannada": {"font": "NotoSansDevanagari-Regular.ttf", "encoding": "utf-8"},
        "Odia": {"font": "NotoSansDevanagari-Regular.ttf", "encoding": "utf-8"}
    }
    return font_configs.get(language, font_configs["Hindi"])

# Streamlit Page Config
st.set_page_config(page_title="BhashaAI", layout="wide")
st.sidebar.image("bhasha_logo.png", width=150)

# Track visits
log_visit()

# Inject PWA meta tags
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

# App Header
st.markdown("""
<div style='text-align: center;'>
    <h2 style='color: #FF671F;'>Bhasha AI</h2>
    <p style='color: #046A38; font-weight: bold; font-size: 20px;'>भारत का अपना ChatGPT</p>
</div>
""", unsafe_allow_html=True)

st.markdown("Simplify forms, legal docs, and English content in **your preferred Indian language**.")
st.sidebar.markdown(f"👁️ **Today's Visitors:** {get_today_count()}")

# Language options
language = st.selectbox("🗣️ Output Language", [
    "Hindi", "Marathi", "Bengali", "Telugu", "Tamil",
    "Urdu", "Gujarati", "Malayalam", "Kannada", "Odia"
])

input_method = st.radio("📥 Choose Input Method", ["Upload PDF", "Paste Text"])
text = ""

# Handle input
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

# Language instructions
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

# Modern FPDF-based PDF Generator (Fixed character scattering)
def generate_pdf(text, language="Hindi"):
    try:
        pdf = FPDF()
        pdf.add_page()
        
        # Add Unicode font
        font_path = os.path.join("assets", "NotoSansDevanagari-Regular.ttf")
        if not os.path.exists(font_path):
            st.error("Font file missing: NotoSansDevanagari-Regular.ttf in assets folder")
            return None
            
        # Use modern FPDF syntax (no 'uni' parameter)
        pdf.add_font("Noto", "", font_path)
        
        # Set margins
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.set_left_margin(15)
        pdf.set_right_margin(15)
        pdf.set_top_margin(20)
        
        # Title
        pdf.set_font("Noto", size=16)
        pdf.cell(0, 15, f"BhashaAI - {language} Output", align="C")
        pdf.ln(20)
        
        # Content font
        pdf.set_font("Noto", size=12)
        
        # Clean and normalize text to prevent character issues
        clean_text = text.replace('\u200d', '').replace('\u200c', '').replace('\ufeff', '')
        clean_text = clean_text.replace('â€™', "'").replace('â€œ', '"').replace('â€', '"')
        clean_text = ' '.join(clean_text.split())  # Normalize all whitespace
        
        # Split text into sentences first, then into manageable chunks
        sentences = clean_text.replace('।', '।|').replace('.', '.|').split('|')
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
                
            # If sentence is too long, split by words
            if len(sentence) > 80:
                words = sentence.split()
                current_chunk = ""
                
                for word in words:
                    test_chunk = current_chunk + " " + word if current_chunk else word
                    if len(test_chunk) <= 70:  # Characters per line
                        current_chunk = test_chunk
                    else:
                        if current_chunk:
                            pdf.multi_cell(0, 8, current_chunk, align="L")
                            pdf.ln(2)
                        current_chunk = word
                
                if current_chunk:
                    pdf.multi_cell(0, 8, current_chunk, align="L")
                    pdf.ln(2)
            else:
                # Short sentence, write directly
                pdf.multi_cell(0, 8, sentence, align="L")
                pdf.ln(2)
        
        # Generate PDF using modern syntax
        output = BytesIO()
        pdf_bytes = pdf.output()  # Modern FPDF returns bytes directly
        output.write(pdf_bytes)
        output.seek(0)
        return output
        
    except Exception as e:
        st.error(f"PDF generation error: {str(e)}")
        # Try fallback method
        return generate_simple_text_pdf(text, language)

# Simple fallback PDF generator
def generate_simple_text_pdf(text, language="Hindi"):
    """Fallback method using basic text handling"""
    try:
        pdf = FPDF()
        pdf.add_page()
        
        font_path = os.path.join("assets", "NotoSansDevanagari-Regular.ttf")
        if os.path.exists(font_path):
            pdf.add_font("Noto", "", font_path)
            pdf.set_font("Noto", size=12)
        else:
            # Use built-in font as last resort
            pdf.set_font("Arial", size=12)
        
        pdf.cell(0, 15, f"BhashaAI - {language} Output", align="C")
        pdf.ln(20)
        
        # Very simple text handling - just write plain text
        clean_text = ' '.join(text.split())
        
        # Break into small chunks
        chunk_size = 60
        for i in range(0, len(clean_text), chunk_size):
            chunk = clean_text[i:i+chunk_size]
            pdf.multi_cell(0, 10, chunk)
            pdf.ln(3)
        
        output = BytesIO()
        pdf_bytes = pdf.output()
        output.write(pdf_bytes)
        output.seek(0)
        return output
        
    except Exception as e:
        st.error(f"Fallback PDF generation error: {str(e)}")
        return None

# Main Logic
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
                # Preprocess the output text
                output = preprocess_text(output)
                
                st.subheader(f"🔍 {language} में व्याख्या:")
                st.write(output)

                # Download PDF
                try:
                    pdf_file = generate_pdf(output, language)
                    st.download_button(
                        label="⬇️ Download as PDF",
                        data=pdf_file,
                        file_name="bhashaai_output.pdf",
                        mime="application/pdf"
                    )
                except Exception as e:
                    st.error("PDF generation failed")
                    st.exception(e)

                # Voice Support
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