import pandas as pd
from datetime import date
import streamlit as st
from utils import get_fx_rate, get_price_eur


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


# Start the analysis
if st.session_state.data_loaded:
    tab1, tab2, tab3 = st.tabs(["Gains", "Stock Updates", "Export Data"])

    df = st.session_state.df
    fx_cache = {}

    for ccy in df['Currency Yahoo'].unique():
        if ccy == 'EUR':
            fx_cache[ccy] = 1.0  # no conversion needed
        else:
            fx_cache[ccy] = get_fx_rate(ccy)

    df.apply(get_price_eur, axis=1, fx_cache=fx_cache)

    df['Price Today (EUR)'] = df.apply(get_price_eur, axis=1, fx_cache=fx_cache)
    df['Value Today (EUR)'] = df['Units'] * df['Price Today (EUR)']

    df['Gain € Since Last'] = df['Value Today (EUR)'] - df['Value Last Update']
    df['Gain € Since Purchase'] = df['Value Today (EUR)'] - df['Units'] * df['Purchase Price']

    df['Gain % Since Last'] = df['Gain € Since Last'] / df['Value Last Update'] * 100
    df['Gain % Since Purchase'] = df['Gain € Since Purchase'] / (df['Units'] * df['Purchase Price']) * 100

    totals = {
        'Asset': 'TOTAL',
        'Ticker': '',
        'Gain € Since Last': df['Gain € Since Last'].sum(),
        'Gain % Since Last': df['Gain € Since Last'].sum() / df['Value Last Update'].sum() * 100,
        'Gain € Since Purchase': df['Gain € Since Purchase'].sum(),
        'Gain % Since Purchase': df['Gain € Since Purchase'].sum() / (df['Units'] * df['Purchase Price']).sum() * 100,
    }
    # %%
    # Columns to show
    report_cols = [
        'Asset', 'Ticker',
        'Gain € Since Last', 'Gain % Since Last',
        'Gain € Since Purchase', 'Gain % Since Purchase'
    ]

    report = pd.concat([df[report_cols], pd.DataFrame([totals])], ignore_index=True)

    pd.options.display.float_format = '{:,.2f}'.format

    today = date.today().strftime("%Y-%m-%d")
    st.markdown(f"### Snapshot of the financial performance {today}:")
    numeric_cols = report.select_dtypes(include='number').columns
    st.dataframe(report.style.format("{:.2f}", subset=numeric_cols))