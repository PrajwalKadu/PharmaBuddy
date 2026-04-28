import streamlit as st
import pandas as pd

# --- 1. PAGE CONFIG ---
st.set_page_config(page_title="PharmaBuddy", page_icon="💊", layout="centered")

# --- 2. ADVANCED CSS (Matching your images) ---
st.markdown("""
    <style>
    .stApp { background-color: #f0f7ff; }
    
    /* Category Chips Styling */
    .stButton > button {
        border-radius: 20px;
        border: 1px solid #e0e0e0;
        background-color: white;
        color: #555;
        font-size: 14px;
        padding: 5px 15px;
        margin-bottom: 5px;
    }
    .stButton > button:hover {
        border-color: #ff4b4b;
        color: #ff4b4b;
    }
    
    /* Medicine Card Styling (Matching Image 2) */
    .med-card {
        background-color: white;
        border-radius: 15px;
        padding: 20px;
        border-left: 8px solid #ff7043;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        margin-bottom: 20px;
        position: relative;
    }
    .brand-title { font-size: 22px; font-weight: 800; color: #2c3e50; }
    .generic-sub { color: #7f8c8d; font-size: 15px; margin-bottom: 15px; }
    
    .savings-badge {
        background-color: #e67e22;
        color: white;
        padding: 5px 12px;
        border-radius: 10px;
        font-weight: bold;
        float: right;
    }
    
    .price-container { display: flex; gap: 15px; margin: 15px 0; }
    .price-box-generic {
        background-color: #e8f5e9;
        padding: 10px;
        border-radius: 10px;
        flex: 1;
        text-align: center;
    }
    .price-box-brand {
        background-color: #fff5f5;
        padding: 10px;
        border-radius: 10px;
        flex: 1;
        text-align: center;
    }
    .price-val { font-size: 20px; font-weight: bold; }
    
    .tag {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 15px;
        font-size: 12px;
        margin-right: 5px;
        background-color: #fdf2f2;
        color: #e67e22;
        border: 1px solid #fee2e2;
    }
    .mfg { font-size: 13px; color: #95a5a6; margin-top: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. ROBUST DATA LOADING ---
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("drugs_data.csv", encoding='latin1', on_bad_lines='skip', engine='python', sep=None)
        df.columns = [c.strip() for c in df.columns]
        for col in ['Generic Price (Rs)', 'Brand Price (Rs)', 'Savings (%)']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        return df
    except Exception: return None

# --- 4. RENDER FUNCTION (The "Image 2" Card) ---
def render_drug_card(row):
    html_card = f"""
    <div class="med-card">
        <div class="savings-badge">↓{row['Savings (%)']}%<br><small style="font-weight:normal; font-size:10px;">savings</small></div>
        <div class="brand-title">🦠 {row['Brand Name']}</div>
        <div class="generic-sub">{row['Generic Name']}</div>
        
        <div class="price-container">
            <div class="price-box-generic">
                <small style="color: #2e7d32; font-weight:bold;">GENERIC</small><br>
                <span class="price-val" style="color: #2e7d32;">₹{row['Generic Price (Rs)']}</span>
            </div>
            <div class="price-box-brand">
                <small style="color: #c62828; font-weight:bold;">BRAND</small><br>
                <span class="price-val" style="color: #c62828;">₹{row['Brand Price (Rs)']}</span>
            </div>
        </div>
        
        <div>
            <span class="tag">{row['Category']}</span>
            <span class="tag">💊 {row['Dosage Form']}</span>
            <span class="tag">{row['Indication']}</span>
        </div>
        <div class="mfg">🏢 {row['Company']}</div>
        <hr style="margin: 10px 0; opacity: 0.1;">
        <div style="font-size:12px; color:#555;">
            <b>Adverse Effects:</b> {row['Adverse Effects']}<br>
            <b>Interactions:</b> {row['Drug Interaction']}
        </div>
    </div>
    """
    st.markdown(html_card, unsafe_allow_html=True)

df = load_data()

if df is not None:
    # Top Search Section
    search_query = st.text_input("", placeholder="🔍 Search by brand name, generic, company...")
    
    # 1st Dropdown fix: Only show if explicitly browsing
    unique_cats = sorted(df['Category'].unique().tolist())
    browse_cat = st.selectbox(f"All Categories ({len(df)})", ["-- Select Category --"] + unique_cats)

    # Category Chips (Matching Image 1)
    st.write("---")
    cols = st.columns(3)
    if cols[0].button("🔵 All"):
        st.session_state.filter = "All"
    
    # Initialize Filter State
    if 'filter' not in st.session_state: st.session_state.filter = "All"

    # MAIN LOGIC
    filtered_df = df
    
    # Priority 1: Search
    if search_query:
        filtered_df = df[df['Brand Name'].str.contains(search_query, case=False) | df['Generic Name'].str.contains(search_query, case=False)]
    # Priority 2: Dropdown
    elif browse_cat != "-- Select Category --":
        filtered_df = df[df['Category'] == browse_cat]
    # Priority 3: Categorized Browse (If any chip selected)
    elif st.session_state.filter != "All":
        filtered_df = df[df['Category'] == st.session_state.filter]

    # Show Count
    st.caption(f"Showing **{len(filtered_df)}** of {len(df)} drugs")

    # DISPLAY CARDS
    if not filtered_df.empty:
        for _, row in filtered_df.iterrows():
            render_drug_card(row)
    else:
        st.info("No medications found. Try a different search.")

else:
    st.error("Please upload 'drugs_data.csv' to your GitHub.")
