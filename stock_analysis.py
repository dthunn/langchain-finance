#%%
import pandas as pd
import yfinance as yf
from datetime import date
import numpy as np
import matplotlib.pyplot as plt
#%%
df = pd.read_csv("data/assets july 7 2025.csv")
df.head()
#%%
df.info()
#%% md
# # FX Rate
#%%
fx_pair = 'USDEUR=X'  # Yahoo Finance symbol for USD to EUR
fx_data = yf.Ticker(fx_pair).history(period="1d")
fx_data
#%%
# Fetch FX rate for USD → EUR
def get_fx_rate(from_currency: str, to_currency: str = 'EUR') -> float:
    """
    Get live FX rate from Yahoo. Returns 1.0 if from/to are the same.
    """
    if from_currency == to_currency:
        return 1.0
    pair = f"{from_currency}{to_currency}=X"
    try:
        data = yf.Ticker(pair).history(period="1d")
        return data["Close"].iloc[-1]
    except Exception as e:
        print(f"Error fetching FX rate: {e}")
        return np.nan
#%%
# test the get_fx_rate
print(get_fx_rate('USD', 'EUR'))
#%%
# Cache FX rates with EUR = 1.0
fx_cache = {}

for ccy in df['Currency Yahoo'].unique():
    if ccy == 'EUR':
        fx_cache[ccy] = 1.0  # no conversion needed
    else:
        fx_cache[ccy] = get_fx_rate(ccy)
print("FX Cache:", fx_cache)
#%%
# Download one price from a ticker for a specific date
yf.Ticker('BTC-USD').history(period="1d")['Close']
#%%
def get_price_eur(row) -> float:
    """
    Fetch Yahoo price in native currency and convert to EUR.
    """
    try:
        price_native = (
            yf.Ticker(row['Ticker'])
            .history(period="1d")['Close']
            .iloc[-1]
        )
        fx_rate = fx_cache.get(row['Currency Yahoo'], 1.0)  # default 1.0
        return price_native * fx_rate
    except Exception as e:
        print(f"Error fetching {row['Ticker']}: {e}")
        return np.nan
#%%
# get the price for all tickers
df.apply(get_price_eur, axis=1)
#%%
# --- CALCULATIONS ---------------------------------------------
today = date.today()

df['Price Today (EUR)'] = df.apply(get_price_eur, axis=1)
df['Value Today (EUR)'] = df['Units'] * df['Price Today (EUR)']

df['Gain € Since Last'] = df['Value Today (EUR)'] - df['Value Last Update']
df['Gain € Since Purchase'] = df['Value Today (EUR)'] - df['Units'] * df['Purchase Price']

df['Gain % Since Last'] = df['Gain € Since Last'] / df['Value Last Update'] * 100
df['Gain % Since Purchase'] = df['Gain € Since Purchase'] / (df['Units'] * df['Purchase Price']) * 100

#%%
df.head()
#%%
# --- Totals Row -----------------------------------------------
totals = {
    'Asset': 'TOTAL',
    'Ticker': '',
    'Gain € Since Last': df['Gain € Since Last'].sum(),
    'Gain % Since Last': df['Gain € Since Last'].sum() / df['Value Last Update'].sum() * 100,
    'Gain € Since Purchase': df['Gain € Since Purchase'].sum(),
    'Gain % Since Purchase': df['Gain € Since Purchase'].sum() / (df['Units'] * df['Purchase Price']).sum() * 100,
}
#%%
# Columns to show
report_cols = [
    'Asset', 'Ticker',
    'Gain € Since Last', 'Gain % Since Last',
    'Gain € Since Purchase', 'Gain % Since Purchase'
]

report = pd.concat([df[report_cols], pd.DataFrame([totals])], ignore_index=True)
report
#%%
# --- Print Report ---------------------------------------------
print(f"\nSnapshot as of {today} (all converted to EUR):\n")
print(report.to_string(index=False, float_format='{:,.2f}'.format))
#%% md
# # Portfolio Updates
#%%
# --- STEP 1: Update existing assets --------------------------------
while True:
    resp = input("\n📥 Were there additional purchases for existing assets? (y/n): ").strip().lower()
    if resp != 'y':
        print("✅ No updates for existing assets.")
        break

    print("\nCurrent portfolio assets:")
    for asset in df['Asset']:
        print(f"- {asset}")

    asset_name = input("\nWhich asset was updated? (type asset name): ").strip()

    # Check if asset exists
    if asset_name not in df['Asset'].values:
        print(f"❌ Asset '{asset_name}' not found in portfolio. Try again.")
        continue

    # Ask for units and price
    try:
        extra_units = float(input("How many new units were bought?: "))
        purchase_price = float(input("What was the purchase price per unit (EUR)?: "))

        # Update units and average purchase price
        idx = df[df['Asset'] == asset_name].index[0]
        old_units = df.at[idx, 'Units']
        old_avg_price = df.at[idx, 'Purchase Price']

        total_cost = (old_units * old_avg_price) + (extra_units * purchase_price)
        total_units = old_units + extra_units
        new_avg_price = total_cost / total_units

        # Update DataFrame
        df.at[idx, 'Units'] = total_units
        df.at[idx, 'Purchase Price'] = new_avg_price

        print(f"✅ Updated {asset_name}: {total_units:.4f} units @ avg price €{new_avg_price:.2f}")

    except Exception as e:
        print("⚠ Error: Please check your input.", e)
#%% md
# # Export
#%%
# --- STEP 2: Add new assets to portfolio --------------------------
while True:
    resp = input("\n➕ Are there new assets to add to the portfolio? (y/n): ").strip().lower()
    if resp != 'y':
        print("✅ No new assets added.")
        break

    try:
        asset_name = input("Asset name: ").strip()
        ticker = input("Ticker (Yahoo Finance): ").strip()
        units = float(input("Units bought: "))
        purchase_price = float(input("Purchase price per unit (EUR): "))
        currency_yahoo = input("Currency in Yahoo Finance (EUR/USD/etc): ").strip().upper()

        # Create new row
        new_row = {
            'Asset': asset_name,
            'Ticker': ticker,
            'Units': units,
            'Purchase Price': purchase_price,
            'Currency Purchase': 'EUR',
            'Currency Yahoo': currency_yahoo,
            'Price Last Update': np.nan,
            'Date Last Update': np.nan,
            'Value Last Update': np.nan,
            'Profit Last Update': np.nan
        }

        # Append to DataFrame
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        print(f"✅ Added {asset_name} to portfolio.")

    except Exception as e:
        print("⚠ Error: Please check your input.", e)

#%%
today = date.today().strftime("%Y-%m-%d")

df.iloc[:, :10].to_csv(f"data/assets-{today}.csv", index=False)
#%%
