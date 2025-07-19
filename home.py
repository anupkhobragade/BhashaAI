import streamlit as st
from PIL import Image

# Sidebar Navigation
st.sidebar.image("bhasha_logo.png", width=150)

# Page config
st.set_page_config(page_title="BhashaAI App – भारत का अपना ChatGPT", layout="centered")

# Title & Tagline
st.title("BhashaAI – भारत का Apna ChatGPT")
st.markdown("🧠 Simplifying English, Legal & Government Docs into your regional language")

# Features
st.markdown("✨ Key Features:")
st.markdown("""
- 📄 Accepts **PDFs or Pasted Text**
- 🌐 Converts to **10 different Indian languages**
- 🧾 Perfect for **Forms, Government Notices, Legal Docs**
- ⚡ Powered by fast, free **Open Source LLMs**
- 📲 **No login or signup** needed
""")

# Supported Languages
st.markdown("🌐 Supported Languages:")
st.markdown("""
- 💎Hindi  
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
st.markdown("🎯 Who is this for?")
st.markdown("""
- 👵 Senior Citizens struggling with English forms  
- 🧑‍🌾 Farmers receiving government letters  
- 👨‍💻 Students dealing with academic PDFs  
- 🧑‍⚖️ Common citizens reading legal/official documents  
- 📑 Anyone who wants **simple explanations**  
""")

# Screenshot or Try Now
st.markdown("🚀 Try the App")
st.markdown("[👉 Launch Now](https://bhashaai.streamlit.app)")

# Optional Screenshot
# img = Image.open("preview.png")
# st.image(img, use_column_width=True)
# Footer
st.markdown("---")
#st.markdown("📬 Contact: [anupkhobragade@gmail.com](mailto:anupkhobragade@gmail.com)  |  Built in Pune, MH | भारत")