# utils/groq_api.py
import os
from dotenv import load_dotenv
import requests

# Load from .env
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def query_groq(prompt, language="Hindi"):
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
    
    # Safe access with error handling
    try:
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        print("❌ Error parsing Groq response:", response.text)
        raise e
