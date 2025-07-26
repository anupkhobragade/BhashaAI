import os
os.environ["STREAMLIT_WATCH_FILE_SYSTEM"] = "false"
import streamlit as st
from PIL import Image

# Sidebar Navigation
st.sidebar.image("bhasha_logo.png", width=150)

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
**BhashaAI** is your local Indian language AI assistant. It explains English content and government/legal documents in **Hindi, Marathi, Bengali, Tamil, Telugu, Kannada, and more**, so that every citizen can understand them with ease.
""")

# Who it's for
st.markdown("""
#### 🎯 Who is it for?
- 👵 Senior Citizens struggling with English  
- 👨‍🌾 Farmers receiving government letters  
- 🧑‍🎓 Students dealing with academic PDFs  
- 🧾 Anyone confused by legal or official forms  
""")

# New Features
st.markdown("""
#### 🔈 New Features:
- 📄 PDF + Text input supported  
- 🌐 Translates to **10 different Indian languages**  
- 🔊 Includes **Text-to-Speech** output
- 🖨️ Save translated Hindi/Marathi output as **PDF**  
- ✅ 100 percent Free and No Login Needed  
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
# Footer
st.markdown("""---""")
st.markdown(
    "<div style='text-align: center; font-size: 14px; color: grey;'>"
    "📬 Contact: <a href='mailto:anupkhobragade@gmail.com'>anupkhobragade@gmail.com</a>  |  Built in Pune 🇮🇳<br>"
    "Made with ❤️ using Streamlit & OpenAI"
    "</div>",
    unsafe_allow_html=True
)