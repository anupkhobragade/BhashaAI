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

# Robust PDF Generator with comprehensive error handling
def generate_pdf(text, language="Hindi"):
    """Generate PDF with multiple fallback strategies"""
    
    # Strategy 1: Try ReportLab first (if available)
    try:
        return generate_pdf_reportlab(text, language)
    except ImportError:
        pass  # ReportLab not available
    except Exception as e:
        st.warning(f"ReportLab method failed: {str(e)}")
    
    # Strategy 2: Try FPDF with Unicode support
    try:
        return generate_pdf_fpdf_safe(text, language)
    except Exception as e:
        st.warning(f"FPDF method failed: {str(e)}")
    
    # Strategy 3: ASCII-only PDF as last resort
    try:
        return generate_ascii_only_pdf(text, language)
    except Exception as e:
        st.warning(f"ASCII fallback failed: {str(e)}")
    
    # Strategy 4: Error PDF (never fails)
    return create_error_pdf(language, "All PDF generation methods failed")

# ASCII-only fallback PDF generator
def generate_ascii_only_pdf(text, language="Hindi"):
    """Generate PDF with ASCII-only content as ultimate fallback"""
    
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=14)
    
    # ASCII-safe title
    pdf.cell(0, 15, "BhashaAI - Output", align="C")
    pdf.ln(20)
    
    pdf.set_font("Arial", size=12)
    
    # Convert text to ASCII-safe version
    ascii_text = ""
    for char in text:
        if ord(char) < 128:
            ascii_text += char
        elif char in 'नमस्तेकमैंहूसरकारभारतीयहिंदीमराठीबंगालीतमिलतेलुगुगुजरातीमलयालमकन्नडओडिया':
            ascii_text += "?"  # Replace Indian chars with ?
        else:
            ascii_text += " "
    
    # Clean up the text
    ascii_text = ' '.join(ascii_text.split())
    
    if not ascii_text or len(ascii_text.strip()) < 5:
        ascii_text = "Original content contained non-ASCII characters that cannot be displayed in this PDF format. Please try a different approach or contact support."
    
    # Write in small chunks
    chunk_size = 80
    for i in range(0, len(ascii_text), chunk_size):
        chunk = ascii_text[i:i+chunk_size]
        try:
            pdf.multi_cell(0, 8, chunk)
            pdf.ln(3)
        except:
            pass  # Skip problematic chunks
    
    # Generate PDF
    output = BytesIO()
    pdf_bytes = pdf.output()
    output.write(pdf_bytes)
    output.seek(0)
    return output

# Safe FPDF generator with robust encoding handling
def generate_pdf_fpdf_safe(text, language="Hindi"):
    """Generate PDF using FPDF with safe encoding handling"""
    
    pdf = FPDF()
    pdf.add_page()
    
    # Always use Arial as fallback to avoid font issues
    try:
        font_path = os.path.join("assets", "NotoSansDevanagari-Regular.ttf")
        if os.path.exists(font_path):
            pdf.add_font("Noto", "", font_path)
            pdf.set_font("Noto", size=16)
            font_name = "Noto"
        else:
            raise Exception("Font not found")
    except Exception as e:
        # Use Arial as fallback
        pdf.set_font("Arial", size=16)
        font_name = "Arial"
    
    # Title - Convert to ASCII for safety
    try:
        title = f"BhashaAI - {language} Output"
        # Try with Unicode font first
        if font_name == "Noto":
            pdf.cell(0, 15, title, align="C")
        else:
            # ASCII fallback
            pdf.cell(0, 15, "BhashaAI - Output", align="C")
    except:
        pdf.cell(0, 15, "BhashaAI - Output", align="C")
    
    pdf.ln(20)
    
    # Content font
    try:
        pdf.set_font(font_name, size=12)
    except:
        pdf.set_font("Arial", size=12)
    
    # Aggressive text preprocessing for encoding safety
    processed_text = preprocess_text_for_pdf_safe(text)
    
    # If no valid text after processing, create error message
    if not processed_text or len(processed_text.strip()) < 5:
        processed_text = "Content could not be processed for PDF generation."
    
    # Write text with maximum safety
    try:
        write_text_to_pdf_safe(pdf, processed_text, font_name)
    except Exception as e:
        # Ultimate fallback - ASCII only
        ascii_text = ''.join(c for c in processed_text if ord(c) < 128)
        if not ascii_text:
            ascii_text = "Content contains characters that cannot be displayed in PDF format."
        pdf.set_font("Arial", size=12)
        pdf.multi_cell(0, 10, ascii_text)
    
    # Generate PDF with encoding safety
    output = BytesIO()
    try:
        pdf_bytes = pdf.output()
        output.write(pdf_bytes)
        output.seek(0)
        return output
    except Exception as e:
        raise Exception(f"PDF output generation failed: {e}")

def preprocess_text_for_pdf_safe(text):
    """Ultra-safe text preprocessing for PDF compatibility"""
    if not text:
        return ""
    
    # Remove ALL problematic Unicode characters
    safe_chars = []
    for char in text:
        try:
            # Test if character is safe
            char_code = ord(char)
            
            # Keep basic Latin, extended Latin, and Devanagari ranges
            if (
                (0x0020 <= char_code <= 0x007E) or  # Basic Latin
                (0x00A0 <= char_code <= 0x00FF) or  # Latin-1 Supplement
                (0x0900 <= char_code <= 0x097F) or  # Devanagari
                char in ' \n\r\t।'  # Safe whitespace and punctuation
            ):
                safe_chars.append(char)
            else:
                safe_chars.append(' ')  # Replace with space
        except:
            safe_chars.append(' ')
    
    text = ''.join(safe_chars)
    
    # Fix common encoding issues
    replacements = {
        'â€™': "'", 'â€œ': '"', 'â€': '"', 'â€˜': "'",
        'Ã¡': 'á', 'Ã©': 'é', 'Ã­': 'í', 'Ã³': 'ó', 'Ãº': 'ú'
    }
    
    for old, new in replacements.items():
        text = text.replace(old, new)
    
    # Normalize whitespace
    text = ' '.join(text.split())
    
    return text.strip()

def write_text_to_pdf_safe(pdf, text, font_name):
    """Write text to PDF with maximum safety"""
    if not text:
        return
    
    # Split into small, manageable chunks
    max_chunk_size = 50  # Very conservative
    
    # Split by sentences first
    sentences = text.replace('।', '।\n').replace('.', '.\n').split('\n')
    
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
        
        # Break long sentences into smaller chunks
        words = sentence.split()
        current_chunk = ""
        
        for word in words:
            test_chunk = current_chunk + " " + word if current_chunk else word
            
            if len(test_chunk) <= max_chunk_size:
                current_chunk = test_chunk
            else:
                # Write current chunk
                if current_chunk:
                    try:
                        if font_name == "Noto":
                            pdf.multi_cell(0, 8, current_chunk.strip())
                        else:
                            # For Arial, ensure ASCII only
                            ascii_chunk = ''.join(c for c in current_chunk if ord(c) < 128)
                            if ascii_chunk:
                                pdf.multi_cell(0, 8, ascii_chunk.strip())
                        pdf.ln(2)
                    except Exception as e:
                        # Skip problematic chunks
                        pass
                current_chunk = word
        
        # Write remaining chunk
        if current_chunk:
            try:
                if font_name == "Noto":
                    pdf.multi_cell(0, 8, current_chunk.strip())
                else:
                    ascii_chunk = ''.join(c for c in current_chunk if ord(c) < 128)
                    if ascii_chunk:
                        pdf.multi_cell(0, 8, ascii_chunk.strip())
                pdf.ln(2)
            except:
                pass

# ReportLab PDF generator (better Unicode support)
def generate_pdf_reportlab(text, language="Hindi"):
    """Generate PDF using ReportLab for better Unicode support"""
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    
    # Register font
    font_path = os.path.join("assets", "NotoSansDevanagari-Regular.ttf")
    if not os.path.exists(font_path):
        raise FileNotFoundError("Font file missing")
        
    pdfmetrics.registerFont(TTFont('Noto', font_path))
    
    # Set position and font
    y_position = height - 80
    margin = 50
    line_height = 18
    
    # Title - Fix the method name
    p.setFont("Noto", 16)
    title_text = f"BhashaAI - {language} Output"
    title_width = p.stringWidth(title_text, "Noto", 16)
    p.drawString((width - title_width) / 2, y_position, title_text)  # Center manually
    y_position -= 40
    
    # Content
    p.setFont("Noto", 12)
    
    # Clean text
    clean_text = text.replace('\u200d', '').replace('\u200c', '').replace('\ufeff', '')
    clean_text = ' '.join(clean_text.split())
    
    # Split into lines
    max_chars_per_line = 70
    words = clean_text.split(' ')
    lines = []
    current_line = ""
    
    for word in words:
        if len(current_line + " " + word) <= max_chars_per_line:
            current_line = current_line + " " + word if current_line else word
        else:
            if current_line:
                lines.append(current_line)
            current_line = word
    
    if current_line:
        lines.append(current_line)
    
    # Draw lines
    for line in lines:
        if y_position < 50:
            p.showPage()
            p.setFont("Noto", 12)
            y_position = height - 50
        
        try:
            p.drawString(margin, y_position, line)
            y_position -= line_height
        except:
            # Skip problematic lines
            y_position -= line_height
    
    p.save()
    buffer.seek(0)
    return buffer

# Simple fallback PDF generator with better error handling
def generate_simple_text_pdf(text, language="Hindi"):
    """Fallback method using basic text handling"""
    try:
        pdf = FPDF()
        pdf.add_page()
        
        font_path = os.path.join("assets", "NotoSansDevanagari-Regular.ttf")
        if os.path.exists(font_path):
            try:
                pdf.add_font("Noto", "", font_path)
                pdf.set_font("Noto", size=12)
            except:
                # If font fails, use Arial
                pdf.set_font("Arial", size=12)
        else:
            # Use built-in font as last resort
            pdf.set_font("Arial", size=12)
        
        pdf.cell(0, 15, f"BhashaAI - {language} Output", align="C")
        pdf.ln(20)
        
        # Very simple text handling - convert to ASCII-safe format
        try:
            # Remove non-ASCII characters for fallback
            clean_text = ''.join(c for c in text if ord(c) < 128)
            if not clean_text:
                clean_text = "Content could not be converted to PDF format."
        except:
            clean_text = "Content could not be converted to PDF format."
        
        # Break into small chunks
        chunk_size = 60
        for i in range(0, len(clean_text), chunk_size):
            chunk = clean_text[i:i+chunk_size]
            try:
                pdf.multi_cell(0, 10, chunk)
                pdf.ln(3)
            except:
                pass
        
        output = BytesIO()
        pdf_bytes = pdf.output()
        output.write(pdf_bytes)
        output.seek(0)
        return output
        
    except Exception as e:
        st.error(f"Fallback PDF generation error: {str(e)}")
        # Return a minimal PDF instead of None
        return create_error_pdf(language)

# Create error PDF when all else fails
def create_error_pdf(language="Hindi", error_msg="Unknown error"):
    """Create a minimal PDF when generation fails"""
    try:
        pdf = FPDF()
        pdf.add_page()
        
        # Use only ASCII-safe content for error PDF
        pdf.set_font("Arial", size=14)
        pdf.cell(0, 15, "BhashaAI - PDF Generation Error", align="C")
        pdf.ln(25)
        
        pdf.set_font("Arial", size=12)
        pdf.multi_cell(0, 10, "Sorry, there was an issue generating the PDF.")
        pdf.ln(10)
        
        # Only include ASCII-safe error message
        safe_error = ''.join(c for c in str(error_msg) if ord(c) < 128)
        if safe_error:
            pdf.multi_cell(0, 10, f"Error: {safe_error[:100]}")
        pdf.ln(10)
        
        pdf.multi_cell(0, 10, "Suggestions:")
        pdf.ln(5)
        pdf.multi_cell(0, 10, "• Try using shorter text")
        pdf.ln(5)
        pdf.multi_cell(0, 10, "• Use simpler language")
        pdf.ln(5)
        pdf.multi_cell(0, 10, "• Contact support if issue persists")
        
        output = BytesIO()
        pdf_bytes = pdf.output()
        output.write(pdf_bytes)
        output.seek(0)
        return output
        
    except Exception as e:
        # Ultimate fallback - return None and let UI handle gracefully
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

                # PDF Download - Only for Hindi and Marathi (Devanagari script supported)
                if language in ["Hindi", "Marathi"]:
                    pdf_file = generate_pdf(output, language)
                    if pdf_file is not None:
                        st.download_button(
                            label="⬇️ Download as PDF",
                            data=pdf_file,
                            file_name="bhashaai_output.pdf",
                            mime="application/pdf"
                        )
                    else:
                        st.error("⚠️ Could not generate PDF. Please try again.")
                else:
                    # Show info for non-Devanagari languages
                    st.info(f"💡 PDF download is currently available only for Hindi and Marathi. {language} content is displayed above with voice support.")

                # Voice Support (available for all languages)
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

# Fixed Footer
footer_html = """
<style>
.footer {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    background-color: white;
    padding: 10px;
    text-align: center;
    font-size: 14px;
    color: #444;
    border-top: 1px solid #ccc;
    z-index: 100;
}
</style>
<div class="footer">
    📬 Contact: <a href='mailto:anupkhobragade@gmail.com'>anupkhobragade@gmail.com</a> | Built in Pune 🇮🇳<br>
    © 2025 BhashaAI. All rights reserved. 
</div>
"""

st.markdown(footer_html, unsafe_allow_html=True)