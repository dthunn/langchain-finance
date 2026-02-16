import pandas as pd
import streamlit as st


st.set_page_config(page_title="Stock Analysis", page_icon=":chart_with_upwards_trend:")
st.title("Financial Performance Analysis")


# Explain what the app does
st.markdown("This app allows you to upload a CSV with your financial "
            "assets and view gains, stock performance and get AI based recommendations.")


# Upload a CSV file
st.markdown("### 🗂️ Upload CSV")
uploaded_file = st.file_uploader("Upload your portfolio CSV", type=["csv"])


# Check if the file is uploaded
if 'data_loaded' not in st.session_state:
    st.session_state.data_loaded = False


# Save the uploaded file as df and continue analysis
if uploaded_file and st.session_state.data_loaded is False:
    st.session_state.df = pd.read_csv(uploaded_file)
    st.session_state.data_loaded = True