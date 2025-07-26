import csv
from datetime import datetime
import os
import streamlit as st

LOG_FILE = "visitor_log.csv"

def log_visit():
    today = datetime.now().strftime("%Y-%m-%d")
    
    if "visit_logged" not in st.session_state:
        st.session_state.visit_logged = False

    if not st.session_state.visit_logged:
        exists = os.path.exists(LOG_FILE)
        with open(LOG_FILE, "a", newline="") as file:
            writer = csv.writer(file)
            if not exists:
                writer.writerow(["date", "count"])
            writer.writerow([today, 1])
        st.session_state.visit_logged = True  # Mark visit as logged

def get_today_count():
    today = datetime.now().strftime("%Y-%m-%d")
    if not os.path.exists(LOG_FILE):
        return 0
    with open(LOG_FILE, "r") as file:
        reader = csv.reader(file)
        next(reader, None)  # Skip header
        count = sum(1 for row in reader if row[0] == today)
        return count