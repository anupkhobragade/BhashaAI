import streamlit as st
from PIL import Image

# Set page config
st.set_page_config(page_title="BhashaAI – भारत का अपना ChatGPT", layout="centered")

# Sidebar
st.sidebar.image("bhasha_logo.png", width=150)

# Title & Tagline
st.title("📘 BhashaAI – भारत का अपना ChatGPT")
st.markdown("🧠 Explain English, Legal, or Govt Docs in your Indian Language")

# About Section
st.markdown("---")
st.header("ℹ️ About BhashaAI")
st.markdown("""
**BhashaAI** is your local Indian language AI assistant. It explains English content and government/legal documents in **Hindi, Marathi, Bengali, Tamil, Telugu, Kannada, and more**, so that every citizen can understand them with ease.

#### 🎯 Who is it for?
- 👵 Senior Citizens struggling with English  
- 👨‍🌾 Farmers receiving government letters  
- 🧑‍🎓 Students dealing with academic PDFs  
- 🧾 Anyone who confused by legal or official complex forms
""")

# Features
st.markdown("---")
st.header("✨ Key Features")
st.markdown("""
- 📄 Upload PDFs or Paste Text  
- 🌐 Translate to **10 Indian languages**  
- 🔊 Listen to translated text with **Voice Support**  
- 🧾 Perfect for **Forms, Government Notices, Legal Docs**  
- ⚡ Powered by open source AI models  
- ✅ 100% Free and No Login Needed
""")

# Supported Languages
st.markdown("🌍 Supported Languages:")
st.markdown("""
- 💎 Hindi  
- 🌸 Marathi  
- 🏵️ Bengali  
- 🌿 Telugu  
- 🎶 Tamil  
- ✨ Urdu  
- 💎 Gujarati  
- 🌴 Malayalam  
- 🌊 Kannada  
- 🌞 Odia  
""")

# App Access
st.markdown("---")
st.header("🚀 Launch the App")
st.markdown("""
- 🌐 [Try on Streamlit](https://bhashaai.streamlit.app/app)  
- 🌐 [Render Deployment](https://bhashaai.onrender.com)
""")

# Optional Screenshot Preview
# img = Image.open("preview.png")
# st.image(img, use_column_width=True)

# Footer
st.markdown("---")
st.markdown("📬 Contact: [anupkhobragade@gmail.com](mailto:anupkhobragade@gmail.com)  |  Built with 💖 in Pune, IN")