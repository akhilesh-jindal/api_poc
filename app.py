import pandas as pd
import streamlit as st
from datetime import date
from main import  run

# --- 2. UI Components ---
st.title("EMA Crossover trades")
st.markdown("Select a date and click the button to view the corresponding data.")

# Create a list of the last 5 days for the dropdown
today = date.today()
last_5_business_days = pd.bdate_range(end=today, periods=5)[::-1]

# Create a selectbox (dropdown) widget
selected_date = st.selectbox('Select a Date', options=last_5_business_days)

# Create a button to trigger the display
if st.button('Display entry-exit'):
    # --- 3. Filter and Display Logic ---
    if selected_date:
        out_df = run(selected_date)
        if not out_df.empty:
            st.dataframe(out_df)
        else:
            st.warning("No data available for this date.")