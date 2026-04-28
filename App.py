import streamlit as st
import pandas as pd

# --- 1. PAGE SETUP ---
st.set_page_config(page_title="PharmaBuddy", page_icon="💊", layout="centered")

# --- 2. THE UI STYLING (Internal CSS) ---
st.markdown("""
    <style>
    .stApp { background-color: #f1f5f9; }
    
    /* Modern Card Container */
    .med-card {
        background-color: white;
        border-radius: 12px;
        padding: 20px;
        border-top: 5px solid #f97316;
        box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
        margin-bottom: 15px;
    }
    
    /* Price Comparison Box */
    .price-grid {
        display: flex;
        justify-content: space-between;
        margin: 15px 0;
        gap: 10px;
    }
    .price-item {
        flex: 1;
        padding: 10px;
        border-radius: 8px;
        text-align: center;
    }
    .generic-bg { background-color: #f0fdf4; border: 1px solid #bbf7d0; }
    .brand-bg { background-color: #fef2f2; border: 1px solid #fecaca; }
    
    .savings-badge {
        background-color: #f97316;
        color: white;
        padding: 2px 10px;
        border-radius: 20px;
        font-weight: bold;
        font-size: 14px;
        float: right;
    }
    
    .label { color: #64748b; font-size: 12px; font-weight: bold; text-transform: uppercase; }
    .val { font-size: 18px; font-weight: bold; color: #1e293b; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. ROBUST DATA LOADING ---
@st.cache_data
def load_data():
    try:
        # Handling encoding and the "Line 15" comma error
        df = pd.read_csv("drugs_data.csv", encoding='latin1', on_bad_lines='skip', engine='python', sep=None)
        df.columns = [c.strip() for c in df.columns]
        # Data Cleanup
        for col in ['Generic Price (Rs)', 'Brand Price (Rs)', 'Savings (%)']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        return df
    except Exception as e:
        st.error(f"Error loading CSV: {e}")
        return None

# --- 4. CARD RENDERER (Pure HTML/CSS) ---
def display_medicine_card(row):
    card_html = f"""
    <div class="med-card">
        <span class="savings-badge">SAVE {row['Savings (%)']}%</span>
        <div style="font-size: 20px; font-weight: 800; color: #1e40af;">{row['Brand Name']}</div>
        <div style="color: #64748b; font-size: 14px;">Salt: {row['Generic Name']}</div>
        
        <div class="price-grid">
            <div class="price-item generic-bg">
                <div class="label" style="color: #166534;">Generic</div>
                <div class="val" style="color: #166534;">₹{row['Generic Price (Rs)']}</div>
            </div>
            <div class="price-item brand-bg">
                <div class="label" style="color: #991b1b;">Brand</div>
                <div class="val" style="color: #991b1b;">₹{row['Brand Price (Rs)']}</div>
            </div>
        </div>
        
        <div style="font-size: 13px; color: #334155; line-height: 1.5;">
            <b>Indication:</b> {row['Indication']}<br>
            <b>Manufacturer:</b> {row['Company']}<br>
            <b>Dosage:</b> {row['Dosage Form']}<br>
            <hr style="margin: 10px 0; border: 0; border-top: 1px solid #e2e8f0;">
            <b style="color: #b91c1c;">Adverse Effects:</b> {row['Adverse Effects']}<br>
            <b>Interaction:</b> {row['Drug Interaction']}
        </div>
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)

# --- 5. MAIN APP LOGIC ---
df = load_data()

if df is not None:
    st.title("💊 PharmaBuddy")
    
    # SEARCH
    search = st.text_input("", placeholder="🔍 Search medicine, salt or symptoms...")

    # NAVIGATION DROPDOWN
    view_mode = st.selectbox("📂 Browse Directory By:", ["Search Results", "All Categories", "All Brands"])

    # --- MODE: ALL CATEGORIES ---
    if view_mode == "All Categories":
        cats = sorted(df['Category'].unique().tolist())
        selected_cat = st.selectbox("Select a Category", ["-- Choose --"] + cats)
        
        if selected_cat != "-- Choose --":
            st.subheader(f"Medicines in {selected_cat}")
            filtered = df[df['Category'] == selected_cat]
            for _, row in filtered.iterrows():
                # Using expander for clean UX
                with st.expander(f"💊 {row['Brand Name']} (₹{row['Brand Price (Rs)']})"):
                    display_medicine_card(row)

    # --- MODE: ALL BRANDS ---
    elif view_mode == "All Brands":
        brands = sorted(df['Brand Name'].unique().tolist())
        selected_brand = st.selectbox("Select a Brand", ["-- Choose --"] + brands)
        
        if selected_brand != "-- Choose --":
            brand_row = df[df['Brand Name'] == selected_brand].iloc[0]
            display_medicine_card(brand_row)

    # --- MODE: SEARCH ---
    else:
        if search:
            results = df[df['Brand Name'].str.contains(search, case=False, na=False) | 
                         df['Generic Name'].str.contains(search, case=False, na=False) |
                         df['Indication'].str.contains(search, case=False, na=False)]
            
            if not results.empty:
                st.success(f"Found {len(results)} matches")
                for _, row in results.iterrows():
                    with st.expander(f"🔍 {row['Brand Name']} - {row['Generic Name']}"):
                        display_medicine_card(row)
            else:
                st.warning("No medicines found matching that search.")
        else:
            st.info("Use the search bar or select a browse mode above to see drug prices.")

else:
    st.error("Data file not found or empty.")

