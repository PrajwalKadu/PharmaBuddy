import streamlit as st
import pandas as pd

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="MedSave | Drug Information Portal",
    page_icon="💊",
    layout="centered"
)

# --- CUSTOM MODERN UI STYLING ---
st.markdown("""
    <style>
    /* Main background */
    .stApp {
        background-color: #fcfcfc;
    }
    /* Style for the Brand Buttons */
    div.stButton > button:first-child {
        background-color: #ffffff;
        color: #1f77b4;
        border: 1px solid #e0e0e0;
        border-left: 5px solid #1f77b4;
        width: 100%;
        text-align: left;
        height: 50px;
        font-size: 18px;
        font-weight: 600;
        transition: 0.3s;
    }
    div.stButton > button:hover {
        border-color: #1f77b4;
        background-color: #f0f7ff;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    /* Category Headers */
    .category-title {
        font-size: 24px;
        font-weight: 700;
        color: #2c3e50;
        margin-top: 30px;
        margin-bottom: 10px;
        padding-left: 5px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- DATA LOADING WITH ERROR FIX ---
@st.cache_data
def load_data():
    try:
        # 'latin1' or 'cp1252' fixes the '0xa2' (non-utf8) encoding error
        df = pd.read_csv("drugs_data.csv", encoding='latin1')
        
        # Clean column names (strip whitespace)
        df.columns = [c.strip() for c in df.columns]
        
        # Ensure price columns are numeric for calculations
        df['Generic Price (Rs)'] = pd.to_numeric(df['Generic Price (Rs)'], errors='coerce')
        df['Brand Price (Rs)'] = pd.to_numeric(df['Brand Price (Rs)'], errors='coerce')
        return df
    except FileNotFoundError:
        st.error("Error: 'drugs_data.csv' not found in the project folder.")
        return None
    except Exception as e:
        st.error(f"Data Load Error: {e}")
        return None

df = load_data()

if df is not None:
    # Initialize Session State for Navigation
    if 'selected_idx' not in st.session_state:
        st.session_state.selected_idx = None

    # --- DETAIL VIEW ---
    if st.session_state.selected_idx is not None:
        row = df.iloc[st.session_state.selected_idx]
        
        if st.button("⬅ Back to All Medications"):
            st.session_state.selected_idx = None
            st.rerun()

        st.divider()
        
        # Header Section
        st.title(row['Brand Name'])
        st.markdown(f"**Category:** {row['Category']} | **Company:** {row['Company']}")
        
        # Metrics Row
        m1, m2, m3 = st.columns(3)
        with m1:
            st.metric("Brand Price", f"₹{row['Brand Price (Rs)']}")
        with m2:
            st.metric("Generic Price", f"₹{row['Generic Price (Rs)']}")
        with m3:
            # Highlight savings in green
            st.metric("Savings (%)", f"{row['Savings (%)']}%", delta="Cheaper", delta_color="normal")

        # Information Cards
        st.subheader("Drug Specifications")
        c1, c2 = st.columns(2)
        with c1:
            st.write(f"**Generic Name:** {row['Generic Name']}")
            st.write(f"**Dosage Form:** {row['Dosage Form']}")
            st.write(f"**Indication:** {row['Indication']}")
        
        with c2:
            with st.expander("⚠️ Adverse Effects", expanded=True):
                st.write(row['Adverse Effects'])
            
            with st.expander("🔄 Drug Interaction", expanded=True):
                st.write(row['Drug Interaction'])

    # --- LIST VIEW ---
    else:
        st.title("💊 Medicine Price Comparison")
        st.write("Browse by category or search for specific brands.")

        # Search Box
        search = st.text_input("🔍 Search Brand, Generic, or Category", placeholder="Enter keyword...")

        # Filter Data based on Search
        if search:
            filtered_df = df[
                df['Brand Name'].str.contains(search, case=False, na=False) |
                df['Generic Name'].str.contains(search, case=False, na=False) |
                df['Category'].str.contains(search, case=False, na=False)
            ]
        else:
            filtered_df = df

        # Group by Category and Display
        if not filtered_df.empty:
            categories = filtered_df['Category'].unique()
            
            for cat in categories:
                # Modern Header
                st.markdown(f"<div class='category-title'>{cat}</div>", unsafe_allow_html=True)
                
                cat_items = filtered_df[filtered_df['Category'] == cat]
                
                # Display Brands under Category
                for idx, row in cat_items.iterrows():
                    if st.button(row['Brand Name'], key=f"btn_{idx}"):
                        st.session_state.selected_idx = idx
                        st.rerun()
        else:
            st.warning("No medications found matching your search.")

# --- FOOTER ---
st.markdown("---")
st.caption("Data for informational purposes only. Consult a doctor before changing medication.")
