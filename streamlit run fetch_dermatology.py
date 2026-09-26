import streamlit as st
import requests

# 1. Clean page layout configuration
st.set_page_config(page_title="Equiderma AI Dashboard", layout="wide")

st.title("🩺 Equiderma AI dashboard  \
 AI: Dermatology Dashboard")
st.write("Query and filter live medical records across the development API server stack.")


FLASK_API_URL = "http://127.0.0.1:9999"


search_query = st.text_input("Enter condition name:")

# 4. Fetch data dynamically based on your search input safely
try:
    if search_query:
        response = requests.get(f"{FLASK_API_URL}/search?q={search_query}")
    else:
        response = requests.get(FLASK_API_URL)
        
    # Check if the API request returned a successful status code
    if response.status_code == 200:
        data = response.json()
        
        # --- YOUR DASHBOARD GENERATION CODE GOES HERE ---
        # (Add your st.write(data), st.dataframe, or charts below this line)
        st.success("Data successfully fetched from Equiderma API backend!")
        st.json(data) 
        
    else:
        st.error(f"Backend returned an error status code: {response.status_code}")

except requests.exceptions.ConnectionError:
    st.error(f"Could not connect to the Equiderma backend at {FLASK_API_URL}. Please ensure your Flask app is running on port 9999!")




  