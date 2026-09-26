import streamlit as st
import requests

# Clean page configuration using universal arguments
st.set_page_config(page_title="Dermatology App", layout="wide")

st.title("🩺 Equiderma AI: Dermatology Dashboard")
st.write("Query and filter live medical records across the development api server stack.")

# Target the secure backend port
FLASK_API_URL = "http://127.0.0.1:9999/api/conditions"

# Simple search block
search_query = st.text_input("Enter condition name:")

try:
    if search_query:
        response = requests.get(f"{FLASK_API_URL}?q={search_query}")
        raw = response.json()
        data = raw.get("conditions", raw) if isinstance(raw, dict) else raw
    else:
        response = requests.get(FLASK_API_URL)
        raw = response.json()
        data = raw.get("conditions", raw) if isinstance(raw, dict) else raw

    # Generate visual list layout
    if data:
        for item in data:
            st.markdown(f"### {item['condition']} (ID: {item['id']})")
            st.write(f"**Severity:** {item['severity']}")
            st.write(f"**Symptoms:** {item['symptoms']}")
            st.markdown("---")
    else:
        st.warning("No records matched your search query.")

except Exception as err:
    st.error(f"Waiting for backend: {err}")


