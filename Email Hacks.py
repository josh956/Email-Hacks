import streamlit as st
import requests
import json
import os
import pandas as pd

# Streamlit UI
st.title("🔍 Email Breach Search")
st.write("Enter your email address below to check if it has been exposed in any data breaches.")

# User Input
email = st.text_input("📧 Enter your email:", placeholder="your-email@example.com")

# Secure API key from environment variable or Streamlit secrets
API_KEY = os.getenv("RapidAPI")
if not API_KEY:
    st.error("⚠️ API key is missing! Please set the RAPIDAPI_KEY environment variable.")
    st.stop()
    
API_HOST = "email-breach-search.p.rapidapi.com"

# Function to fetch breach data
@st.cache_data
def fetch_breach_data(email):
    url = f"https://{API_HOST}/rapidapi/search-email/{email}"
    headers = {
        "x-rapidapi-key": API_KEY,
        "x-rapidapi-host": API_HOST
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        st.error(f"⚠️ Error fetching data: {e}")
        return None

# Fetch and display results
if email:
    if "@" in email:
        data = fetch_breach_data(email)

        if data:
            st.subheader("📂 Breach Details")

            # Display as a table
            df = pd.DataFrame(data)
            st.dataframe(df[["id", "name", "breach_date", "upload_date", "rows"]])

            # Expanders for detailed breach info
            for breach in data:
                with st.expander(f"📁 {breach['name']}"):
                    st.write(f"**ID**: {breach.get('id', 'N/A')}")
                    st.write(f"**Breach Date**: {breach.get('breach_date', 'N/A')}")
                    st.write(f"**Upload Date**: {breach.get('upload_date', 'N/A')}")
                    st.write(f"**Exposed Rows**: {breach.get('rows', 'N/A')}")
                    if "summary" in breach:
                        st.write(f"**Summary**: {breach['summary']}")
                    if "icon" in breach:
                        st.image(breach['icon'], width=100)

            # JSON Export
            st.subheader("📥 Export Data")
            formatted_json = json.dumps(data, indent=4)
            st.download_button(
                label="Download Breaches as JSON",
                data=formatted_json,
                file_name="breaches.json",
                mime="application/json"
            )
        else:
            st.info("✅ No breaches found for this email.")
    else:
        st.warning("⚠️ Please enter a valid email address.")
