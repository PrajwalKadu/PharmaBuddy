import streamlit as st
import pandas as pd

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="PharmaBuddy",
    page_icon="💊",
    layout="centered"
)

# --- 2. PROFESSIONAL UI STYLING ---
st.markdown("""
    <style>
    .stApp { background-color: #f8fafc; }
    
    /* Comparison Card Styling */
    .compare-card {
        background-color: #ffffff;
        padding: 18px;
        border-radius: 12px;
        border-left: 6px solid #10b981;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        margin-bottom: 15px;
    }
    .brand-name { color: #1e40af; font-size: 18px; font-weight: 800; margin-bottom: 2px; }
    .generic-name { color: #059669; font-size: 15px; font-weight: 600; margin-bottom: 10px; }
    .price-label { font-size: 12px; color: #64748b; text-transform: uppercase; letter-spacing: 0.5px; }
    .price-value { font-size: 20px; font-weight: 700; color: #1e293b; }
    .savings-tag {
        background-color: #dcfce7;
        color: #15803d;
        padding: 4px 12px;
        border-radius: 9999px;
        font-weight: 700;
        font-size: 14px;
    }
    
    /* Headers */
    .section-title {
        font-size: 22px;
        font-weight: 800;
        color: #0f172a;
        margin-top: 25px;
        margin-bottom: 15px;
        border-bottom: 2px solid #e2e8f0;
        padding-bottom: 8px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. DATA LOADING (ROBUST ETL LOGIC) ---
@st.cache_data
def load_data():
    try:
        # Fixed encoding and bad line handling for mobile-saved CSVs
        df = pd.read_csv(
            "drugs_data.csv", 
            encoding='latin1', 
            on_bad_lines='skip', 
            engine='python',
            sep=None # Detects comma or semicolon automatically
        )
        # Clean column headers
        df.columns = [c.strip() for c in df.columns]
        
        # Ensure prices and savings are treated as numbers
        for col in ['Generic Price (Rs)', 'Brand Price (Rs)', 'Savings (%)']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        return df
    except Exception as e:
        st.error(f"⚠️ Error reading CSV: {e}")
        return None

# --- 4. HELPER FUNCTION: RENDER COMPARISON CARD ---
def render_drug_card(row):
    """Generates the comparison UI for a single drug row"""
    st.markdown(f"""
        <div class="compare-card">
            <div style="display: flex; justify-content: space-between; align-items: start;">
                <div>
                    <div class="brand-name">{row['Brand Name']}</div>
                    <div class="generic-name">Salt: {row['Generic Name']}</div>
                </div>
                <div class="savings-tag">Save {row['Savings (%)']}%</div>
            </div>
            
            <div style="display: flex; gap: 30px; margin: 15px 0;">
                <div>
                    <div class="price-label">Brand Price</div>
                    <div class="price-value">₹{row['Brand Price (Rs)']}</div>
                </div>
                <div style="border-left: 1px solid #e2e8f0; height: 40px;"></div>
                <div>
                    <div class="price-label">Generic Price</div>
                    <div class="price-value" style="color: #10b981;">₹{row['Generic Price (Rs)']}</div>
                </div>
            </div>
            
            <div style="font-size: 14px; line-height: 1.6; color: #475569; border-top: 1px solid #f1f5f9; pt: 10px;">
                <b>Indication:</b> {row['Indication']}<br>
                <b>Dosage Form:</b> {row['Dosage Form']}<br>
                <span style="color: #b91c1c;"><b>Adverse Effects:</b> {row['Adverse Effects']}</span><br>
                <span style="color: #1e293b;"><b>Interactions:</b> {row['Drug Interaction']}</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

# --- 5. MAIN APP LOGIC ---
df = load_data()

if df is not None:
    st.title("💊 PharmaBuddy")
    st.write("Compare brand medicines with generic equivalents to save money.")

    # A. Global Search
    search_query = st.text_input("🔍 Search Brand, Salt, or Indication", placeholder="e.g. Paracetamol...")

    # B. View Mode Selector
    view_option = st.selectbox(
        "📂 Browse Directory",
        ["Search Results", "All Categories", "All Brands"]
    )

    st.divider()

    # --- LOGIC: ALL CATEGORIES ---
    if view_option == "All Categories":
        st.markdown("<div class='section-title'>Browse by Category</div>", unsafe_allow_html=True)
        categories = sorted(df['Category'].dropna().unique().tolist())
        
        for cat in categories:
            with st.expander(f"📁 {cat}"):
                cat_data = df[df['Category'] == cat]
                for _, row in cat_data.iterrows():
                    render_drug_card(row)

    # --- LOGIC: ALL BRANDS ---
    elif view_option == "All Brands":
        st.markdown("<div class='section-title'>Browse by Brand Name</div>", unsafe_allow_html=True)
        brands = sorted(df['Brand Name'].dropna().unique().tolist())
        
        for brand in brands:
            with st.expander(f"💊 {brand}"):
                brand_data = df[df['Brand Name'] == brand]
                for _, row in brand_data.iterrows():
                    render_drug_card(row)

    # --- LOGIC: SEARCH RESULTS ---
    else:
        if search_query:
            mask = (
                df['Brand Name'].astype(str).str.contains(search_query, case=False, na=False) |
                df['Generic Name'].astype(str).str.contains(search_query, case=False, na=False) |
                df['Indication'].astype(str).str.contains(search_query, case=False, na=False)
            )
            results = df[mask]
            
            if not results.empty:
                st.success(f"Showing {len(results)} results for '{search_query}'")
                for _, row in results.iterrows():
                    render_drug_card(row)
            else:
                st.warning("No medicines found. Try a different keyword.")
        else:
            st.info("Start typing in the search box or select a browse mode from the dropdown.")

else:
    st.error("Missing Data: Please ensure 'drugs_data.csv' is uploaded to your GitHub repository.")

# Footer
st.markdown("---")
st.caption("Developed by Prajwal Kadu | PharmaBuddy v3.0")
