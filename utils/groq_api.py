import os
import requests
import streamlit as st
from dotenv import load_dotenv

# Load from .env if present (for local use)
load_dotenv()

# First priority: .env, fallback to Streamlit/Render secrets
GROQ_API_KEY = os.getenv("GROQ_API_KEY") or st.secrets.get("GROQ_API_KEY", None)

if not GROQ_API_KEY:
    raise ValueError("🚨 GROQ_API_KEY not found! Please set it in .env or Render secrets.")

def query_groq(prompt, language="Hindi"):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": f"You are a helpful assistant who explains content in {language}."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 1000
    }

    response = requests.post(url, headers=headers, json=data)

    try:
        res_json = response.json()
        if "choices" in res_json:
            return res_json["choices"][0]["message"]["content"]
        elif "error" in res_json:
            st.error(f"Groq API Error: {res_json['error'].get('message', 'Unknown error')}")
        else:
            st.error("Invalid response format from Groq API.")
        return None
    except Exception as e:
        st.error("❌ Failed to parse Groq API response.")
        st.text(response.text)
        return None