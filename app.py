import streamlit as st
import pandas as pd

# --- 1. MOCK DATABASE: BASE PRICES (Estimates in SGD) ---
# In a real app, this would be scraped daily from a live source.
base_prices = {
    "95": {"SPC": 2.79, "Esso": 2.80, "Caltex": 2.80, "Shell": 2.85, "Sinopec": 2.79},
    "98": {"SPC": 3.28, "Esso": 3.29, "Caltex": 3.29, "Shell": 3.34, "Sinopec": 3.28},
    "Diesel": {"SPC": 2.61, "Esso": 2.62, "Caltex": 2.62, "Shell": 2.63, "Sinopec": 2.61}
}

# --- 2. MOCK DATABASE: CREDIT CARD DISCOUNTS ---
# Format: {"Card Name": {"Brand": Total Effective Discount %}}
# Note: These are simplified effective discounts for demonstration.
card_discounts = {
    "No Card / Cash": {"SPC": 0.0, "Esso": 0.0, "Caltex": 0.0, "Shell": 0.0, "Sinopec": 0.0},
    "POSB Everyday Card": {"SPC": 0.201, "Esso": 0.05, "Caltex": 0.05, "Shell": 0.05, "Sinopec": 0.05},
    "UOB One Card": {"SPC": 0.05, "Esso": 0.05, "Caltex": 0.05, "Shell": 0.2115, "Sinopec": 0.24},
    "Trust Card": {"SPC": 0.05, "Esso": 0.05, "Caltex": 0.20, "Shell": 0.05, "Sinopec": 0.05},
    "Citi Cash Back": {"SPC": 0.05, "Esso": 0.2088, "Caltex": 0.05, "Shell": 0.2088, "Sinopec": 0.05},
    "OCBC 365": {"SPC": 0.05, "Esso": 0.05, "Caltex": 0.221, "Shell": 0.05, "Sinopec": 0.268}
}

# --- APP UI START ---
st.set_page_config(page_title="SG Petrol Saver", page_icon="⛽")

st.title("⛽ SG Petrol Price Finder")
st.write("Find the cheapest petrol based on **your** credit cards.")

# --- SIDEBAR: USER INPUTS ---
st.sidebar.header("Your Details")

# 1. Select Fuel Type
fuel_type = st.sidebar.selectbox("Select Fuel Grade", ["95", "98", "Diesel"])

# 2. Select Credit Cards
available_cards = list(card_discounts.keys())
available_cards.remove("No Card / Cash") # Remove default from options
selected_cards = st.sidebar.multiselect(
    "Which credit cards do you have?", 
    available_cards,
    default=["POSB Everyday Card"]
)

# Always include "No Card" as a baseline fallback
if not selected_cards:
    selected_cards = ["No Card / Cash"]
else:
    selected_cards.append("No Card / Cash")

# --- DISCOUNT ENGINE LOGIC ---
st.subheader(f"Current Prices for {fuel_type} Octane")

results = []

# Loop through every petrol brand
for brand, base_price in base_prices[fuel_type].items():
    best_discount_rate = 0.0
    best_card = "No Card / Cash"
    
    # Check all user's cards to find the best discount for this brand
    for card in selected_cards:
        discount = card_discounts[card].get(brand, 0.0)
        if discount >= best_discount_rate:
            best_discount_rate = discount
            best_card = card if discount > 0 else "No Card / Cash"
            
    # Calculate effective price
    net_price = base_price * (1 - best_discount_rate)
    
    results.append({
        "Petrol Station": brand,
        "Base Price": f"${base_price:.2f}",
        "Best Card to Use": best_card,
        "Discount %": f"{best_discount_rate * 100:.1f}%",
        "Effective Price (Per Litre)": net_price
    })

# Convert results to a Dataframe and sort by Cheapest Effective Price
df = pd.DataFrame(results)
df = df.sort_values(by="Effective Price (Per Litre)")

# Format the Effective Price for display after sorting
df["Effective Price (Per Litre)"] = df["Effective Price (Per Litre)"].apply(lambda x: f"${x:.3f}")

# --- DISPLAY RESULTS ---
# Show the #1 Best Deal prominently
cheapest_brand = df.iloc[0]["Petrol Station"]
cheapest_price = df.iloc[0]["Effective Price (Per Litre)"]
cheapest_card = df.iloc[0]["Best Card to Use"]

st.success(f"🏆 **Best Deal:** Go to **{cheapest_brand}**. Pay **{cheapest_price}**/litre using your **{cheapest_card}**.")

# Show the full comparison table
st.markdown("### Comparison Board")
# Hide the row index for a cleaner look
st.dataframe(df, hide_index=True, use_container_width=True)

st.caption("Disclaimer: Prices and discounts are estimated for demonstration purposes. Bank T&Cs apply (e.g., minimum monthly spend).")