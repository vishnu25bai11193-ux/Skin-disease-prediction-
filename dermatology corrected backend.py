# 2. Corrected target backend link
BASE_API_URL = "http://127.0.0"

# Search box input field
search_query = st.text_input("Enter condition name:")

data = []  # Initialize an empty list to prevent crashes

try:
    # 3. Fetch data dynamically based on your search input
    if search_query:
        response = requests.get(f"{BASE_API_URL}/search?q={search_query}")
        if response.status_code == 200:
            data = response.json()
    else:
        response = requests.get(BASE_API_URL)
        if response.status_code == 200:
            data = response.json()
except requests.exceptions.ConnectionError:
    st.warning("⚠️ Waiting for backend server... Please ensure your Flask Backend terminal is running on Port 9999.")


for i in range(0,11)
    st.write(f"### Record #{i+1}")
    st.write(f"Condition: {data[i]['condition']}")
    st.write(f"Description: {data[i]['description']}")
    st.write(f"Severity: {data[i]['severity']}")
    st.write("---")

# 5. Display the fetched data in the dashboard
 try 
     if search_query
         response = requests.get(f"{BASE_API_URL}/search?q={search_query}")

        