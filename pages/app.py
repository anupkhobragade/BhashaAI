import streamlit as st
import requests
import pdfplumber   
from dotenv import load_dotenv
import os
from utils.groq_api import query_groq

# Load API key
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Streamlit UI setup
st.set_page_config(page_title="BhashaAI App", layout="wide")

# Sidebar Branding
st.sidebar.image("bhasha_logo.png", width=150)
#st.sidebar.markdown("### Navigation")
#st.sidebar.success("App")  # Just a label, not a radio button

# Page Content
st.markdown("""
<div style='text-align: center;'>
    <h2 style='color: #FF671F; margin-bottom: 0;'>Bhasha AI</h2>
    <p style='color: #046A38; font-weight: bold; font-size: 20px; margin-top: 5px;'>भारत का अपना ChatGPT</p>
</div>
""", unsafe_allow_html=True)
st.markdown("Simplify forms, legal docs, and English content in **your preferred Indian language**.")

# Language selection
language = st.selectbox("🗣️ Output Language", [
    "Hindi", "Marathi", "Bengali", "Telugu", "Tamil", 
    "Urdu", "Gujarati", "Malayalam", "Kannada", "Odia"
])

# Input method selection
input_method = st.radio("📥 Choose Input Method", ["Upload PDF", "Paste Text"])

# Function to call Groq API
def query_groq(prompt):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "llama3-70b-8192",
        "messages": [
            {"role": "system", "content": f"You are a helpful assistant who explains content in {language}."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 1000
    }
    response = requests.post(url, headers=headers, json=data)
    return response.json()["choices"][0]["message"]["content"]

# Supported Languages Section
with st.expander("🌐 Supported Indian Languages"):
    st.markdown("""
**Bhasha AI currently supports 10 major Indian languages:**

1. **Hindi** – Northern & Central India  
2. **Bengali** – West Bengal, Assam  
3. **Telugu** – Andhra Pradesh, Telangana  
4. **Marathi** – Maharashtra  
5. **Tamil** – Tamil Nadu, Sri Lanka  
6. **Urdu** – Uttar Pradesh, Telangana  
7. **Gujarati** – Gujarat  
8. **Malayalam** – Kerala  
9. **Kannada** – Karnataka  
10. **Odia** – Odisha

Features include:
- 🗣️ Native script support  
- 🧾 Form simplification  
- 🔁 English ↔️ Indian language translation  
- 🎙️ Voice input/output (coming soon!)
""")

# Extracted or input text
text = ""

# Option 1: PDF Upload
if input_method == "Upload PDF":
    pdf_file = st.file_uploader("Upload a PDF file", type=["pdf"])
    if pdf_file:
        with pdfplumber.open(pdf_file) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text

# Option 2: Paste Text
else:
    text = st.text_area("Paste your content here", height=200)

# Process the text if available
if text.strip():
    if st.button("🧠 Explain in " + language):
        with st.spinner(f"Generating simplified explanation in {language}..."):
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
            lang_in_prompt = language_prompts.get(language, language)

            prompt = f"""
तुम एक सहायक आहात जो भारत के नागरिकों की सहायता करता है। कृपया नीचे दी गई सामग्री को {lang_in_prompt} में समझाओ ताकि सभी लोग उसे आसानी से समझ सकें।

सामग्री:
{text[:3000]}
"""
            try:
                output = query_groq(prompt)
                st.subheader(f"🔍 {language} में व्याख्या:")
                st.write(output)
            except Exception as e:
                st.error("❌ Something went wrong while fetching explanation.")
                st.exception(e)
else:
    st.info("कृपया PDF अपलोड करें या टेक्स्ट पेस्ट करें।")
