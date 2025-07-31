import os
os.environ["STREAMLIT_WATCH_FILE_SYSTEM"] = "false"
import streamlit as st
from PIL import Image

# Sidebar Navigation
st.sidebar.markdown("""
<div style="text-align: center;">
    <img src="data:image/gif;base64,{}" width="180">
</div>
""".format(
    __import__('base64').b64encode(open("bhasha_logo.gif", "rb").read()).decode()
), unsafe_allow_html=True)

# Page config
st.set_page_config(page_title="BhashaAI – भारत का अपना ChatGPT", layout="centered")

# Title & Tagline with reduced spacing
st.markdown("""
<div style='text-align: center; margin-top: -10px; margin-bottom: 5px;'>
    <h2 style='color: #FF671F; margin: 0;'>📘 BhashaAI – भारत का अपना ChatGPT</h2>
    <p style='font-size: 16px; color: #046A38; font-weight: bold; margin: 4px 0;'>
        🧠 Explain English, Legal, or Govt complex Docs in your regional Indian Language
    </p>
</div>
""", unsafe_allow_html=True)

# About Section
st.markdown("""
#### ℹ️ About BhashaAI  
**BhashaAI** is your local Indian language AI assistant. It explains English content, government/legal documents, and **extracts text from images and PDFs** in **Hindi, Marathi, Bengali, Tamil, Telugu, Kannada, and more**, so that every citizen can understand them with ease.
""")

# Who it's for
st.markdown("""
#### 🎯 Who is it for?
- 👵 Senior Citizens struggling with English  
- 👨‍🌾 Farmers receiving government letters or scanned documents
- 🧑‍🎓 Students dealing with academic PDFs and image-based content
- 🧾 Anyone confused by legal or official forms
- 📱 Users with image-based documents that need translation
""")

# New Features
st.markdown("""
#### ✨ Key Features:
- 📄 **Smart PDF Processing**: Handles both text-based and image-based PDFs automatically
- 🖼️ **OCR Technology**: Extract text from images (JPG, PNG, BMP) with advanced recognition
- 🌐 **10 Indian Languages**: Translates to Hindi, Marathi, Bengali, Tamil, Telugu, and more
- 🔊 **Text-to-Speech**: Listen to translations in your preferred language
- 🖨️ **PDF Export**: Save Hindi/Marathi translations as downloadable PDFs
- ⚡ **Auto-Processing**: Instant translation for uploaded files
- ✅ **100% Free**: No login required, completely free to use
""")

# Supported languages (compact 2-column layout)
st.markdown("🌍 **Supported Languages:**")
col1, col2 = st.columns(2)
with col1:
    st.markdown("💎 Hindi")
    st.markdown("🌸 Marathi")
    st.markdown("🏵️ Bengali")
    st.markdown("🌿 Telugu")
    st.markdown("🎶 Tamil")
with col2:
    st.markdown("✨ Urdu")
    st.markdown("💎 Gujarati")
    st.markdown("🌴 Malayalam")
    st.markdown("🌊 Kannada")
    st.markdown("🦁 Odia")

# App Access
st.markdown("""
### 🚀 Launch the App:
-  🌐 [Try on Streamlit](https://bhashaai.streamlit.app/app)    
""")

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