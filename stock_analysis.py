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
