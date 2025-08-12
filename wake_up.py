"""
Simple wake-up endpoint for keeping the Streamlit app alive
This can be used by external monitoring services
"""

import streamlit as st
from datetime import datetime
import json

def app():
    st.set_page_config(page_title="BhashaAI Wake-Up", layout="wide")
    
    st.markdown("# 🔄 BhashaAI Wake-Up Service")
    
    current_time = datetime.now()
    
    # Simple health check response
    health_data = {
        "status": "alive",
        "timestamp": current_time.isoformat(),
        "service": "BhashaAI",
        "message": "App is running and responsive"
    }
    
    st.json(health_data)
    
    st.success(f"✅ App is awake at {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    st.markdown("---")
    st.markdown("[← Back to Main App](../app)")

if __name__ == "__main__":
    app()
