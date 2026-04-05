import streamlit as st
import pandas as pd

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="PharmaBuddy",
    page_icon="💊",
    layout="centered"
)

# --- MODERN UI STYLING ---
st.markdown("""
    <style>
    .stApp { background-color: #fcfdfe; }
    
    /* Category Heading */
    .category-box {
        background-color: #075e54;
        color: white;
        padding: 12px;
        border-radius: 5px;
        margin-top: 25px;
        font-weight: bold;
        font-size: 1.2rem;
    }

    /* Brand Button */
    div.stButton > button {
        width: 100%;
        border: 1px solid #e0e0e0;
        background-color: white;
        color: #333;
        text-align: left !important;
        padding: 15px !important;
        border-radius: 8px;
        font-size: 18px;
        font-weight: 500;
        margin-bottom: -10px;
        transition: 0.3s;
    }
    div.stButton > button:hover {
        border-color: #075e54;
        color: #075e54;
        background-color: #f0fdf4;
    }
    </style>
    """, unsafe_allow_html=True)

# --- DATA LOADING (FIXES THE CSV ERROR) ---
@st.cache_data
def load_data():
    try:
        # on_bad_lines='skip' is the KEY fix for your "Expected 2 fields" error
        # engine='python' helps handle files with mixed formatting
        df = pd.read_csv(
            "drugs_data.csv", 
            encoding='latin1', 
            on_bad_lines='skip', 
            engine='python',
            sep=None # Automatically detects if you used comma or semicolon
        )
        
        # Strip spaces from column names
        df.columns = [c.strip() for c in df.columns]
        
        # Convert prices to numbers, ignoring errors
        cols_to_fix = ['Generic Price (Rs)', 'Brand Price (Rs)', 'Savings (%)']
        for col in cols_to_fix:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
        return df
    except Exception as e:
        st.error(f"Could not load data. Ensure the file is a true CSV. Error: {e}")
        return None

df = load_data()

# --- APP LOGIC ---
if df is not None:
    # Navigation State
    if 'selected_row' not in st.session_state:
        st.session_state.selected_row = None

    # --- DETAIL VIEW ---
    if st.session_state.selected_row is not None:
        row = st.session_state.selected_row
        
        if st.button("⬅ Back to Directory"):
            st.session_state.selected_row = None
            st.rerun()

        st.title(row['Brand Name'])
        st.caption(f"Category: {row['Category']} | Manufacturer: {row['Company']}")
        
        st.divider()

        # Modern Metrics
        c1, c2, c3 = st.columns(3)
        c1.metric("Brand Price", f"₹{row['Brand Price (Rs)']}")
        c2.metric("Generic Price", f"₹{row['Generic Price (Rs)']}")
        c3.metric("Total Savings", f"{row['Savings (%)']}%", delta="Saved")

        # Drug Info Cards
        st.subheader("Medicine Details")
        col_a, col_b = st.columns(2)
        with col_a:
            st.write(f"**Generic Name:** {row['Generic Name']}")
            st.write(f"**Dosage:** {row['Dosage Form']}")
        with col_b:
            st.write(f"**Indication:** {row['Indication']}")

        st.markdown("---")
        st.warning(f"**Adverse Effects:** {row['Adverse Effects']}")
        st.error(f"**Drug Interaction:** {row['Drug Interaction']}")

    # --- HOME VIEW ---
    else:
        st.title("💊 PharmaBuddy")
        
        # Search Box
        search = st.text_input("", placeholder="🔍 Search Brand, Generic, or Category...")

        if search:
            filtered_df = df[
                df['Brand Name'].astype(str).str.contains(search, case=False) |
                df['Generic Name'].astype(str).str.contains(search, case=False) |
                df['Category'].astype(str).str.contains(search, case=False)
            ]
        else:
            filtered_df = df

        # Grouping UI
        if not filtered_df.empty:
            unique_cats = filtered_df['Category'].unique()
            for cat in unique_cats:
                # Display Category Header
                st.markdown(f"<div class='category-box'>{cat}</div>", unsafe_allow_html=True)
                
                # Display all Brands in that Category
                cat_data = filtered_df[filtered_df['Category'] == cat]
                for idx, row in cat_data.iterrows():
                    # Create a unique key for each button
                    if st.button(row['Brand Name'], key=f"btn_{idx}"):
                        st.session_state.selected_row = row
                        st.rerun()
        else:
            st.info("No matching medicines found.")
