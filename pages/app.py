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
import easyocr
import cv2
import numpy as np
from PIL import Image
import tempfile
try:
    from pdf2image import convert_from_bytes
    PDF2IMAGE_AVAILABLE = True
except ImportError:
    PDF2IMAGE_AVAILABLE = False
try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False

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

# Initialize OCR reader (cached to avoid reloading)
@st.cache_resource
def get_ocr_reader():
    """Initialize and cache OCR reader"""
    try:
        # Support only English and Hindi for maximum compatibility
        reader = easyocr.Reader(['en', 'hi'], gpu=False)
        return reader
    except Exception as e:
        st.error(f"Failed to initialize OCR reader: {str(e)}")
        return None

def extract_text_from_image(image, reader):
    """Extract text from image using OCR"""
    try:
        if reader is None:
            return "OCR reader not available"
        
        # Convert PIL image to numpy array if needed
        if isinstance(image, Image.Image):
            image_array = np.array(image)
        else:
            image_array = image
        
        # Show processing message for images
        processing_placeholder = st.empty()
        # processing_placeholder.info("⏳ Extracting text from image...")
        
        # Perform OCR silently
        results = reader.readtext(image_array, detail=0)
        extracted_text = ' '.join(results)
        
        # Clear processing message
        processing_placeholder.empty()
        
        return extracted_text.strip()
    except Exception as e:
        # Clear processing message on error
        if 'processing_placeholder' in locals():
            processing_placeholder.empty()
        st.error(f"Error extracting text from image: {str(e)}")
        return ""

def extract_text_from_image_pdf(pdf_bytes, reader):
    """Extract text from image-based PDF using OCR"""
    try:
        if reader is None:
            return "OCR reader not available"
        
        extracted_text = ""
        
        # Show processing message
        processing_placeholder = st.empty()
        processing_placeholder.info("⏳ Please wait, PDF is processing...")
        
        # Try pdf2image first, then PyMuPDF as fallback
        images = []
        
        if PDF2IMAGE_AVAILABLE:
            try:
                images = convert_from_bytes(pdf_bytes, dpi=200)
            except Exception as e:
                images = []
        
        # Fallback to PyMuPDF
        if not images and PYMUPDF_AVAILABLE:
            try:
                images = convert_pdf_pymupdf(pdf_bytes)
            except Exception as e:
                processing_placeholder.empty()
                return ""
        
        # If no conversion method worked
        if not images:
            processing_placeholder.empty()
            st.error("Unable to process PDF. Please try a different file.")
            return ""
        
        # Update progress message
        if len(images) > 1:
            processing_placeholder.info(f"⏳ Processing {len(images)} pages, please wait...")
        
        # Process each page silently
        for i, image in enumerate(images):
            # Update progress for multi-page documents
            if len(images) > 3:  # Only show page progress for longer documents
                processing_placeholder.info(f"⏳ Processing page {i+1} of {len(images)}...")
            
            # Convert PIL image to numpy array if needed
            if isinstance(image, Image.Image):
                image_array = np.array(image)
            else:
                image_array = image
            
            # Extract text from this page
            page_text = extract_text_from_image(image_array, reader)
            if page_text:
                extracted_text += f"\n--- Page {i+1} ---\n{page_text}\n"
        
        # Clear processing message
        processing_placeholder.empty()
        
        return extracted_text.strip()
    except Exception as e:
        # Clear processing message on error
        if 'processing_placeholder' in locals():
            processing_placeholder.empty()
        st.error(f"Error processing PDF: {str(e)}")
        return ""

def convert_pdf_pymupdf(pdf_bytes):
    """Convert PDF to images using PyMuPDF (fitz)"""
    try:
        # Open PDF from bytes
        pdf_document = fitz.open(stream=pdf_bytes, filetype="pdf")
        images = []
        
        for page_num in range(len(pdf_document)):
            # Get page
            page = pdf_document[page_num]
            
            # Convert page to image
            # Higher matrix values = higher resolution
            mat = fitz.Matrix(2.0, 2.0)  # 2x zoom for better quality
            pix = page.get_pixmap(matrix=mat)
            
            # Convert to PIL Image
            img_data = pix.tobytes("ppm")
            img = Image.open(BytesIO(img_data))
            images.append(img)
        
        pdf_document.close()
        return images
        
    except Exception as e:
        raise Exception(f"PyMuPDF conversion failed: {str(e)}")

def is_pdf_image_based(pdf_bytes):
    """Check if PDF is image-based (scanned) or text-based"""
    try:
        with pdfplumber.open(BytesIO(pdf_bytes)) as pdf:
            text_content = ""
            # Check first few pages for text content
            pages_to_check = min(3, len(pdf.pages))
            
            for i in range(pages_to_check):
                page_text = pdf.pages[i].extract_text()
                if page_text:
                    text_content += page_text.strip()
            
            # If very little text found, likely image-based
            return len(text_content.strip()) < 50
    except:
        return True  # Assume image-based if can't read normally

# Streamlit Page Config
st.set_page_config(page_title="BhashaAI", layout="wide")

# Track visits
log_visit()

# Sidebar Layout
st.sidebar.markdown("""
<div style="text-align:  center;">
    <img src="data:image/gif;base64,{}" width="180">
</div>
""".format(
    __import__('base64').b64encode(open("bhasha_logo.gif", "rb").read()).decode()
), unsafe_allow_html=True)

st.sidebar.markdown("### 🎯 Supported Formats")
st.sidebar.markdown("**PDFs:** Text & Image-based")
st.sidebar.markdown("**Images:** JPG, PNG, BMP")  
st.sidebar.markdown("**Languages:** English + Indian languages")

st.sidebar.markdown("---")
st.sidebar.markdown(f"**Today's Visitors:** {get_today_count()}")

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
<div style='text-align: center; margin-top: -50px; margin-bottom: -20px;'>
    <h2 style='color: #FF671F; margin: 0; padding: 0;'>Bhasha AI</h2>
    <p style='color: #046A38; font-weight: bold; font-size: 20px; margin: 5px 0;'>भारत का अपना ChatGPT</p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div style='text-align: center; margin-bottom: 20px;'>
    <p style='margin: 5px 0; font-size: 16px;'>Simplify forms, legal docs, and English content in <strong>your preferred Indian language</strong>.</p>
</div>
""", unsafe_allow_html=True)

# Language options
language = st.selectbox("🗣️ Output Language", [
    "Hindi", "Marathi", "Bengali", "Telugu", "Tamil",
    "Urdu", "Gujarati", "Malayalam", "Kannada", "Odia"
])

input_method = st.radio("📥 Choose Input Method", ["Upload PDF or Image", "Paste Text"])
text = ""

# Initialize OCR reader
ocr_reader = None
if input_method == "Upload PDF or Image":
    ocr_reader = get_ocr_reader()

# Handle input
if input_method == "Upload PDF or Image":
    uploaded_file = st.file_uploader("Upload a PDF or Image file", type=["pdf", "jpg", "jpeg", "png", "bmp", "tiff"])
    if uploaded_file:
        file_type = uploaded_file.type
        
        if file_type == "application/pdf":
            # Handle PDF file
            pdf_bytes = uploaded_file.read()
            
            # Check if PDF is image-based or text-based
            if is_pdf_image_based(pdf_bytes):
                text = extract_text_from_image_pdf(pdf_bytes, ocr_reader)
            else:
                try:
                    with pdfplumber.open(BytesIO(pdf_bytes)) as pdf:
                        for page in pdf.pages:
                            page_text = page.extract_text()
                            if page_text:
                                text += page_text
                except Exception as e:
                    text = extract_text_from_image_pdf(pdf_bytes, ocr_reader)
        
        else:
            # Handle image file
            try:
                # Display a small thumbnail of the uploaded image
                image = Image.open(uploaded_file)
                
                # Create a small thumbnail
                thumbnail = image.copy()
                thumbnail.thumbnail((150, 150))  # Max 150x150 pixels
                
                # Show thumbnail with filename
                col1, col2 = st.columns([1, 4])
                with col1:
                    st.image(thumbnail, caption=f"📎 {uploaded_file.name}", width=150)
                with col2:
                    st.write(f"**File:** {uploaded_file.name}")
                    st.write(f"**Type:** {uploaded_file.type}")
                
                # Show processing message
                st.info("⏳ Image is processing, please wait...")
                
                # Extract text from image using OCR
                text = extract_text_from_image(image, ocr_reader)
                
                if text:
                    st.success(f"✅ Extracted {len(text)} characters from image")
                    with st.expander("📝 Extracted Text Preview"):
                        st.text_area("Extracted text:", text, height=150, disabled=True)
                else:
                    st.warning("⚠️ No text found in the image")
                    
            except Exception as e:
                st.error("⚠️ Error processing image.")
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
    "Urdu": "ur", "Gujarati": "gu", "Malayalam": "ml", "Kannada": "kn", "Odia": "hi"  # Odia not supported by gTTS, fallback to Hindi
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

# Process and generate output automatically when text is available
def process_and_generate_output(text, language):
    """Process text and generate output automatically"""
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
                # Special handling for Odia
                if language == "Odia":
                    st.info("🔊 Voice output for Odia will be in Hindi due to technical limitations.")
                
                tts = gTTS(output, lang=lang_code)
                audio_bytes = BytesIO()
                tts.write_to_fp(audio_bytes)
                audio_bytes.seek(0)
                st.audio(audio_bytes, format="audio/mp3")
            except Exception as e:
                st.warning("⚠️ Could not generate voice output for this language.")
                # Don't show the full exception to users, just log it
                print(f"Voice generation error: {e}")

# Main Logic
if input_method == "Upload PDF or Image":
    # For upload method
    if uploaded_file and text.strip():
        # File uploaded and text extracted - automatically process
        process_and_generate_output(text, language)
    elif not uploaded_file:
        # No file uploaded yet
        st.info("📁 कृपया PDF या इमेज फ़ाइल अपलोड करें।")
    elif uploaded_file and not text.strip():
        # File uploaded but no text extracted
        st.warning("⚠️ फ़ाइल से कोई टेक्स्ट नहीं मिला। कृपया दूसरी फ़ाइल का प्रयास करें।")
        
elif input_method == "Paste Text":
    # For paste text method - always show enabled button for better UX
    if st.button(f"🧠 Explain in {language}"):
        if text.strip():
            # Text is available - process it
            process_and_generate_output(text, language)
        else:
            # No text entered - show error message
            st.error("⚠️ कृपया पहले टेक्स्ट बॉक्स में कुछ लिखें या पेस्ट करें।")
    
    # Show helper text when no text is entered
    if not text.strip():
        st.info("✏️ कृपया ऊपर के बॉक्स में अपना टेक्स्ट लिखें या पेस्ट करें, फिर 'Explain' बटन दबाएं।")

footer_html = """
<style>
.footer {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    background-color: white;
    padding: 10px 15px;
    text-align: center;
    font-size: 13px;
    color: #333;
    border-top: 1px solid #ccc;
    z-index: 1000;
}

.footer a {
    color: #0b5cd1;
    text-decoration: none;
    margin: 0 8px;
}

.footer a:hover {
    text-decoration: underline;
}
</style>

<div class="footer">
    📬 Contact: <a href='mailto:anupkhobragade@gmail.com'>anupkhobragade@gmail.com</a> |
    <a href="https://twitter.com/anupkhobragade" target="_blank">Twitter</a> |
    <a href="https://www.linkedin.com/in/anup-khobragade" target="_blank">LinkedIn</a><br>
    Proudly developed in Pune, India 🇮🇳  |  © 2025 BhashaAI. All rights reserved.
</div>
"""
st.markdown(footer_html, unsafe_allow_html=True)