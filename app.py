import pandas as pd
import numpy as np
from datetime import date
import streamlit as st
import yfinance as yf
from utils import get_fx_rate, get_price_eur


st.set_page_config(page_title="Stock Analysis", page_icon=":chart_with_upwards_trend:")
st.title("📊 Financial Performance Analysis")


# Explain what the app does
st.markdown("This app allows you to upload a CSV with your financial "
            "assets and view gains, stock performance and get AI based recommendations.")


# Upload a CSV file
st.markdown("### 🗂️ Upload CSV")
uploaded_file = st.file_uploader("Upload your portfolio CSV", type=["csv"])


# Check if the file is uploaded
if 'data_loaded' not in st.session_state:
    st.session_state.data_loaded = False
if 'flag' not in st.session_state:
    st.session_state.flag = False


# Save the uploaded file as df and continue analysis
if uploaded_file and st.session_state.data_loaded is False:
    st.session_state.df = pd.read_csv(uploaded_file)
    st.session_state.data_loaded = True


# Start the analysis
if st.session_state.data_loaded:
    tab1, tab2, tab3 = st.tabs(["💰 Gains", "🔄 Stock Updates", "📥 Export Data"])

    df = st.session_state.df
    fx_cache = {}

    for ccy in df['Currency Yahoo'].unique():
        if ccy == 'EUR':
            fx_cache[ccy] = 1.0  # no conversion needed
        else:
            fx_cache[ccy] = get_fx_rate(ccy)

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

    with tab1:
        today = date.today().strftime("%Y-%m-%d")
        st.markdown(f"### 📈 Snapshot of the financial performance {today}:")
        numeric_cols = report.select_dtypes(include='number').columns
        st.dataframe(report.style.format("{:.2f}", subset=numeric_cols))

        st.session_state.flag = True

    # Tab 2
    with tab2:
        # Ask if there are any updates
        update = st.radio("Do you have any updates to your portfolio?", ('Yes', 'No'), horizontal=True)

        if update == 'Yes':
            st.write("### 📦 Stack Asset Details")
            selected_asset = st.selectbox("Select an asset", df['Asset'].tolist())

            extra_units = st.number_input("How many units did you buy?", min_value=None, step=.000001)
            new_purchase_price = st.number_input("What was the purchase price per unit (EUR)?", min_value=0.00, step=.01)

            if st.button("✅ Update Asset"):
                if selected_asset and extra_units != 0 and new_purchase_price > 0:
                    # Update units and average purchase price
                    idx = df[df['Asset'] == selected_asset].index[0]
                    old_units = df.at[idx, 'Units']
                    old_avg_price = df.at[idx, 'Purchase Price']

                    total_cost = (old_units * old_avg_price) + (extra_units * new_purchase_price)
                    total_units = old_units + extra_units
                    new_avg_price = total_cost / total_units

                    # Update DataFrame
                    df.at[idx, 'Units'] = total_units
                    df.at[idx, 'Purchase Price'] = new_avg_price

                    st.session_state.df = df
                    st.success(f"Updated {selected_asset}: {total_units:.4f} units @ avg price €{new_avg_price:.2f}")
                    # st.rerun()
                else:
                    st.warning("Please enter valid units and purchase price.")

            new_asset = st.radio("Did you add a new asset?", ('No', 'Yes'), horizontal=True)

            if new_asset == 'Yes':
                st.markdown("### ✨ New Asset Details")

                asset_name = st.text_input("Asset name: ").strip()
                ticker = st.text_input("Ticker (Yahoo Finance): ").strip()
                currency = st.selectbox("Currency (EUR or USD): ", ('EUR', 'USD'))
                units = st.number_input("Number of units: ", min_value=0.0, step=.000001, key="new_units")
                purchase_price = st.number_input("Purchase price: ", min_value=0.00, step=.01, key="new_price")

                if st.button("➕ Add Asset"):
                    if asset_name and ticker and units > 0 and purchase_price > 0:
                        stock = yf.Ticker(ticker)
                        info = stock.info

                        if "shortName" in info:
                            # Create the new row
                            new_row = {
                                'Asset': asset_name,
                                'Ticker': ticker,
                                'Units': units,
                                'Purchase Price': purchase_price,
                                'Currency Purchase': 'EUR',
                                'Currency Yahoo': currency,
                                'Price Last Update': np.nan,
                                'Date Last Update': np.nan,
                                'Value Last Update': units * purchase_price,
                                'Profit Last Update': 0.0
                            }

                            # Append to DataFrame
                            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)

                            st.session_state.df = df
                            st.success(f"Added {asset_name} to portfolio.")
                        else:
                            st.error("Invalid ticker. Please try again.")
                    else:
                        st.error("Please enter valid asset details.")


    with tab3:
        if st.session_state.flag:
            df["Price Last Update"] = df["Price Today (EUR)"]
            df["Date Last Update"] = today

            csv = df.iloc[:, :10].to_csv(index=False).encode('utf-8')

            # Export the CSV
            st.download_button(label="Download updated CSV", data=csv, file_name=f"assets-{today}.csv", mime="text/csv")

            st.session_state.flag = True
