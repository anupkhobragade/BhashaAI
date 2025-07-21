import streamlit as st
from PIL import Image

# Sidebar Navigation
st.sidebar.image("bhasha_logo.png", width=150)

# Page config
st.set_page_config(page_title="BhashaAI – भारत का अपना ChatGPT", layout="centered")

# Title & Tagline
st.title("📘 BhashaAI – भारत का अपना ChatGPT")
st.markdown("🧠 Explain English, Legal, or Govt Docs in your Indian Language")

# Features
st.markdown("✨ Features:")
st.markdown("""
- 📄 Upload PDFs or Paste Text  
- 🌐 Translate to **10 Indian languages**  
- 🔊 Listen to translated text with **Voice Support**  
- 🧾 Perfect for **Forms, Government Notices, Legal Docs**  
- ⚡ Powered by open source AI models  
- ✅ No login or signup needed  
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

# Who it's for
st.markdown("🎯 Ideal Users:")
st.markdown("""
- 👵 Senior Citizens  
- 🧑‍🌾 Farmers  
- 👨‍🎓 Students  
- 🧑‍⚖️ Common citizens with official documents  
- 📑 Anyone wanting **simple explanations**  
""")

# App Access
st.markdown("🚀 Launch the App:")
st.markdown("""
- ▶️ [Try on Streamlit](https://bhashaai.streamlit.app)
- 🌐 [Render Deployment](https://bhashaai.onrender.com)
""")

# Optional Screenshot
# img = Image.open("preview.png")
# st.image(img, use_column_width=True)

# Footer
st.markdown("---")
st.markdown("📬 Contact: [anupkhobragade@gmail.com](mailto:anupkhobragade@gmail.com)  |  Built in Pune 🇮🇳")