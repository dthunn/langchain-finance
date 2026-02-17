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


#%% md
# # Export
#%%
# --- STEP 2: Add new assets to portfolio --------------------------

#%%
today = date.today().strftime("%Y-%m-%d")

df.iloc[:, :10].to_csv(f"data/assets-{today}.csv", index=False)
#%%
