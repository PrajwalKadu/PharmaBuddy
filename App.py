import streamlit as st
import pandas as pd

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="PharmaBuddy",
    page_icon="💊",
    layout="centered"
)

# --- 2. CSS STYLING (Themed UI) ---
st.markdown("""
    <style>
    .stApp { background-color: #f8fafc; }
    
    /* The Medicine Card Container */
    .med-card {
        background-color: #ffffff;
        padding: 22px;
        border-radius: 12px;
        border-top: 6px solid #f97316;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.08);
        margin-bottom: 20px;
    }
    
    /* Pricing Comparison Grid */
    .price-row {
        display: flex;
        justify-content: space-between;
        gap: 15px;
        margin: 18px 0;
    }
    .price-card {
        flex: 1;
        padding: 12px;
        border-radius: 8px;
        text-align: center;
    }
    .gen-bg { background-color: #f0fdf4; border: 1px solid #bbf7d0; color: #166534; }
    .brd-bg { background-color: #fef2f2; border: 1px solid #fecaca; color: #991b1b; }
    
    .savings-badge {
        background-color: #f97316;
        color: white;
        padding: 4px 14px;
        border-radius: 20px;
        font-weight: bold;
        float: right;
        font-size: 14px;
    }
    
    .med-title { font-size: 22px; font-weight: 800; color: #1e3a8a; margin-bottom: 2px; }
    .med-salt { font-size: 14px; color: #64748b; margin-bottom: 15px; }
    .label-small { font-size: 11px; font-weight: bold; text-transform: uppercase; opacity: 0.8; }
    .price-big { font-size: 22px; font-weight: 800; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. DATA LOADING (Robust Engine) ---
@st.cache_data
def load_data():
    try:
        # Handles potential encoding issues and bad formatting in the CSV
        df = pd.read_csv(
            "drugs_data.csv", 
            encoding='latin1', 
            on_bad_lines='skip', 
            engine='python', 
            sep=None
        )
        df.columns = [c.strip() for c in df.columns]
        
        # Numeric cleanup
        for col in ['Generic Price (Rs)', 'Brand Price (Rs)', 'Savings (%)']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        return df
    except Exception as e:
        st.error(f"Data Load Error: {e}")
        return None

# --- 4. CARD RENDERER ---
def display_drug_card(row):
    """Renders the HTML card for a single drug entry"""
    card_content = f"""
    <div class="med-card">
        <span class="savings-badge">SAVE {row['Savings (%)']}%</span>
        <div class="med-title">{row['Brand Name']}</div>
        <div class="med-salt">Salt: {row['Generic Name']}</div>
        
        <div class="price-row">
            <div class="price-card gen-bg">
                <div class="label-small">GENERIC</div>
                <div class="price-big">₹{row['Generic Price (Rs)']}</div>
            </div>
            <div class="price-card brd-bg">
                <div class="label-small">BRAND</div>
                <div class="price-big">₹{row['Brand Price (Rs)']}</div>
            </div>
        </div>
        
        <div style="font-size: 14px; color: #334155; line-height: 1.6;">
            <b>Indication:</b> {row['Indication']}<br>
            <b>Manufacturer:</b> {row['Company']}<br>
            <b>Dosage:</b> {row['Dosage Form']}<br>
            <hr style="margin: 12px 0; border: 0; border-top: 1px solid #f1f5f9;">
            <span style="color: #dc2626;"><b>Adverse Effects:</b> {row['Adverse Effects']}</span><br>
            <b>Interactions:</b> {row['Drug Interaction']}
        </div>
    </div>
    """
    st.markdown(card_content, unsafe_allow_html=True)

# --- 5. MAIN APP INTERFACE ---
df = load_data()

if df is not None:
    st.title("💊 PharmaBuddy")
    
    # Global Search
    search = st.text_input("", placeholder="🔍 Search medicine, salt or symptoms...")

    # Dropdown Navigation
    view_mode = st.selectbox(
        "📂 Browse Directory By:", 
        ["All Medicines", "All Categories", "All Brands"]
    )

    st.divider()

    # --- LOGIC: ALL CATEGORIES ---
    if view_mode == "All Categories":
        unique_cats = sorted(df['Category'].unique().tolist())
        selected_cat = st.selectbox("Select a Category", ["-- Select Category --"] + unique_cats)
        
        if selected_cat != "-- Select Category --":
            st.subheader(f"Results for {selected_cat}")
            filtered = df[df['Category'] == selected_cat]
            for _, row in filtered.iterrows():
                with st.expander(f"💊 {row['Brand Name']} (₹{row['Brand Price (Rs)']})"):
                    display_drug_card(row)
        else:
            st.info("Please select a category above to browse medicines.")

    # --- LOGIC: ALL BRANDS ---
    elif view_mode == "All Brands":
        unique_brands = sorted(df['Brand Name'].unique().tolist())
        selected_brand = st.selectbox("Select a Brand", ["-- Select Brand --"] + unique_brands)
        
        if selected_brand != "-- Select Brand --":
            brand_data = df[df['Brand Name'] == selected_brand].iloc[0]
            display_drug_card(brand_data)
        else:
            st.info("Please select a specific brand name to see details.")

    # --- LOGIC: ALL MEDICINES (The Fallback Mode) ---
    else:
        # If user searches, filter the main list
        if search:
            mask = (
                df['Brand Name'].astype(str).str.contains(search, case=False, na=False) | 
                df['Generic Name'].astype(str).str.contains(search, case=False, na=False) |
                df['Indication'].astype(str).str.contains(search, case=False, na=False)
            )
            display_df = df[mask]
            st.caption(f"Found {len(display_df)} matches")
        else:
            # If no search, show everything
            display_df = df
            st.caption(f"Showing all {len(display_df)} medicines in directory")

        # Render list
        for _, row in display_df.iterrows():
            with st.expander(f"💊 {row['Brand Name']} - {row['Generic Name']}"):
                display_drug_card(row)

else:
    st.error("Data Load Error: Please ensure 'drugs_data.csv' is correctly formatted and uploaded.")

# Footer
st.markdown("---")
st.caption("PharmaBuddy v3.1 | Medicine Price Comparison Tool")
