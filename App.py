import streamlit as st
import pandas as pd

# Page config
st.set_page_config(page_title="Drug Info Portal", layout="wide")

@st.cache_data
def load_data():
    # Replace 'drugs_data.csv' with your actual filename
    df = pd.read_csv("drugs_data.csv")
    return df

try:
    df = load_data()

    # Session state to handle "navigation" between list and detail view
    if 'selected_drug' not in st.session_state:
        st.session_state.selected_drug = None

    # --- DETAIL PAGE ---
    if st.session_state.selected_drug is not None:
        if st.button("⬅️ Back to List"):
            st.session_state.selected_drug = None
            st.rerun()
        
        row = df.iloc[st.session_state.selected_drug]
        
        st.title(f"Brand: {row['Brand']}")
        st.subheader(f"Category: {row['Category']}")
        
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Generic Name:** {row['Generic']}")
            st.write(f"**Indication:** {row['Indication']}")
            st.write(f"**Manufacturer:** {row['Manufacturer']}")
        
        with col2:
            st.metric("Brand Price (INR)", f"₹{row['Brand_Price_INR']}")
            st.metric("Generic Price (INR)", f"₹{row['Generic_Price_INR']}")

        st.divider()
        st.markdown("### Clinical Information")
        st.warning(f"**Adverse Effects:** {row['Adverse_Effects']}")
        st.error(f"**Drug Interactions:** {row['Drug_Interactions']}")

    # --- MAIN LIST PAGE ---
    else:
        st.title("💊 Drug Information Directory")
        st.write("Click on a Brand name to view detailed information.")
        
        # Search Bar
        search = st.text_input("Search by Brand or Category", "")
        
        filtered_df = df[
            df['Brand'].str.contains(search, case=False) | 
            df['Category'].str.contains(search, case=False)
        ]

        for index, row in filtered_df.iterrows():
            # Create a clickable header using a button styled like a link/header
            if st.button(f"## {row['Brand']}", key=f"btn_{index}"):
                st.session_state.selected_drug = index
                st.rerun()
            st.caption(f"Category: {row['Category']}")
            st.markdown("---")

except Exception as e:
    st.error(f"Please ensure 'drugs_data.csv' is in the folder. Error: {e}")