import streamlit as st
import requests
import os
import pandas as pd
import io
import matplotlib.pyplot as plt

# App Title & Description
st.set_page_config(page_title="Email Breach Search", page_icon="🔍", layout="wide")
st.title("🔍 Email Breach Search")
st.write("Enter your email address below to check if it has been exposed in data breaches.")

# 📖 Sidebar: How to Use
st.sidebar.title("ℹ️ How to Use")
st.sidebar.markdown(
    """
    **1️⃣ Enter your email** in the field below and press `Enter`.  
    **2️⃣ View the results** – see which breaches your email was found in.  
    **3️⃣ Use the search bar** to filter specific breaches.  
    **4️⃣ Click "Download Breaches as Excel"** to save your data.  

    ---
    ### 📌 Understanding the Data:
    - **Breach Date** 📅 → When the breach occurred.  
    - **Exposed Rows** 🔢 → Number of records leaked.  
    - **Risk Score** ⚠️  
      - 🟢 **Low** → Less than 10,000 records.  
      - 🟡 **Medium** → 10,000 - 1,000,000 records.  
      - 🔴 **High** → More than 1,000,000 records.  
    ---
    """
)

# User Input for Single Email
email = st.text_input("📧 Enter your email:", placeholder="your-email@example.com")

# Secure API key from environment variable
API_KEY = os.getenv("RapidAPI")
API_HOST = "email-breach-search.p.rapidapi.com"

if not API_KEY:
    st.error("⚠️ API key is missing! Please set the RAPIDAPI_KEY environment variable.")
    st.stop()

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
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"⚠️ Error fetching data for {email}: {e}")
        return None

# Search Breach Data
if email and "@" in email:
    with st.status("🔍 Searching for breaches..."):
        data = fetch_breach_data(email)

    if data:
        st.subheader("📂 Breach Details")

        # Convert data to DataFrame
        df = pd.DataFrame(data)

        # Risk Level Based on Breach Data Size
        def assign_risk(rows):
            if rows > 1_000_000:
                return "🔴 High"
            elif rows > 10_000:
                return "🟡 Medium"
            return "🟢 Low"

        df["Risk Level"] = df["rows"].apply(assign_risk)

        # Rename headers to user-friendly terms
        df = df.rename(
            columns={
                "name": "Breach Name",
                "breach_date": "Breach Date",
                "rows": "Exposed Rows"
            }
        )

        # Remove 'Upload Date' column
        table_data = df[["Breach Name", "Breach Date", "Exposed Rows", "Risk Level"]]

        # Search & Filter Option
        search_query = st.text_input("🔍 Search breaches:", placeholder="Type breach name...")
        if search_query:
            table_data = table_data[table_data["Breach Name"].str.contains(search_query, case=False, na=False)]

        # 📊 Layout for Table & Chart
        col1, col2 = st.columns([4, 3], gap="large")

        with col1:
            st.write("### 📋 Breach Details Table")
            st.dataframe(table_data)

        with col2:
            # Bar Chart: Breaches Over Time
            st.write("### 📊 Breaches by Year")
            df["Breach Date"] = pd.to_datetime(df["Breach Date"], errors="coerce")
            df["Year"] = df["Breach Date"].dt.year
            year_counts = df["Year"].value_counts().sort_index()

            # Plot the bar chart
            plt.figure(figsize=(8, 6))  # Larger chart
            plt.bar(year_counts.index, year_counts.values, color="blue")
            plt.xlabel("Year")
            plt.ylabel("Number of Breaches")
            plt.xticks(rotation=45, fontsize=10)
            plt.grid(axis="y", linestyle="--", alpha=0.7)
            st.pyplot(plt)

        # 📥 Excel Export
        st.subheader("📥 Export Data")

        # Convert DataFrame to Excel
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            table_data.to_excel(writer, index=False, sheet_name="Breach Data")
            writer.close()

        st.download_button(
            label="📂 Download Breaches as Excel",
            data=output.getvalue(),
            file_name="breaches.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        # 🔽 Expandable List of Breaches
        st.subheader("🔎 Detailed Breach Information")
        for _, breach in df.iterrows():
            with st.expander(f"{breach['Breach Name']} - Risk: {breach['Risk Level']}"):
                st.write(f"**Breach Date**: {breach['Breach Date']}")
                st.write(f"**Exposed Rows**: {breach['Exposed Rows']}")
                if "summary" in breach:
                    st.write(f"**Summary**: {breach['summary']}")
                if "icon" in breach:
                    st.image(breach["icon"], width=100)

    else:
        st.info("✅ No breaches found for this email.")
else:
    st.warning("⚠️ Please enter a valid email address.")

# Footer
st.markdown(
    """
    <hr>
    <p style="text-align: center;">
    <b>2025 Email Hack App</b> &copy; 2025<br>
    Developed by <a href="https://www.linkedin.com/in/josh-poresky956/" target="_blank">Josh Poresky</a><br><br>
    </p>
    """,
    unsafe_allow_html=True
)
