import streamlit as st
import pandas as pd

# --- 1. PAGE CONFIG ---
st.set_page_config(page_title="PharmaBuddy", page_icon="💊", layout="centered")

# --- 2. ADVANCED CSS (Replicating the Image UI) ---
st.markdown("""
    <style>
    .stApp { background-color: #f8fbff; }
    
    /* Search Bar Styling */
    .stTextInput input {
        border-radius: 12px;
        border: 1px solid #d1d5db;
        padding: 12px;
    }

    /* Category Pill/Chip Styling */
    .chip-container {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin: 15px 0;
    }
    .stButton > button {
        border-radius: 25px;
        border: 1px solid #e5e7eb;
        background-color: white;
        color: #4b5563;
        font-weight: 500;
        padding: 4px 16px;
        transition: 0.2s;
    }
    .stButton > button:hover {
        border-color: #3b82f6;
        color: #3b82f6;
    }

    /* Drug Card (Image UI Match) */
    .drug-card {
        background: white;
        border-radius: 20px;
        padding: 24px;
        margin-bottom: 16px;
        border-left: 6px solid #f97316;
        box-shadow: 0 4px 12px rgba(0,0,0,0.03);
    }
    .savings-badge {
        background-color: #f97316;
        color: white;
        padding: 4px 10px;
        border-radius: 10px;
        font-weight: bold;
        font-size: 14px;
        float: right;
        text-align: center;
    }
    .drug-title { font-size: 22px; font-weight: 800; color: #1e293b; margin-bottom: 4px; }
    .drug-subtitle { color: #64748b; font-size: 15px; margin-bottom: 20px; }
    
    .price-grid { display: flex; gap: 12px; margin-bottom: 20px; }
    .price-box {
        flex: 1;
        padding: 12px;
        border-radius: 12px;
        text-align: left;
    }
    .gen-bg { background-color: #f0fdf4; }
    .brd-bg { background-color: #fef2f2; }
    .price-label { font-size: 11px; font-weight: bold; letter-spacing: 0.5px; margin-bottom: 4px; }
    .price-val { font-size: 20px; font-weight: 800; }

    .tag-container { display: flex; flex-wrap: wrap; gap: 6px; }
    .tag {
        background-color: #fff7ed;
        color: #c2410c;
        border: 1px solid #ffedd5;
        padding: 3px 12px;
        border-radius: 12px;
        font-size: 12px;
        font-weight: 600;
    }
    .mfg-text { color: #94a3b8; font-size: 12px; margin-top: 12px; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. DATA LOADING ---
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("drugs_data.csv", encoding='latin1', on_bad_lines='skip', engine='python', sep=None)
        df.columns = [c.strip() for c in df.columns]
        for col in ['Generic Price (Rs)', 'Brand Price (Rs)', 'Savings (%)']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        return df
    except: return None

# --- 4. RENDERER ---
def render_card(row):
    st.markdown(f"""
    <div class="drug-card">
        <div class="savings-badge">↓{row['Savings (%)']}%<br><small style="font-weight:normal; font-size:9px;">savings</small></div>
        <div class="drug-title">🦠 {row['Brand Name']}</div>
        <div class="drug-subtitle">{row['Generic Name']}</div>
        
        <div class="price-grid">
            <div class="price-box gen-bg">
                <div class="price-label" style="color:#16a34a;">GENERIC</div>
                <div class="price-val" style="color:#16a34a;">₹{row['Generic Price (Rs)']}</div>
            </div>
            <div class="price-box brd-bg">
                <div class="price-label" style="color:#dc2626;">BRAND</div>
                <div class="price-val" style="color:#dc2626;">₹{row['Brand Price (Rs)']}</div>
            </div>
        </div>
        
        <div class="tag-container">
            <span class="tag">{row['Category']}</span>
            <span class="tag">💊 {row['Dosage Form']}</span>
            <span class="tag">{row['Indication']}</span>
        </div>
        <div class="mfg-text">🏢 {row['Company']}</div>
        <hr style="margin: 15px 0; opacity: 0.1;">
        <div style="font-size:13px; color:#475569;">
            <b>Adverse Effects:</b> {row['Adverse Effects']}<br>
            <b>Interaction:</b> {row['Drug Interaction']}
        </div>
    </div>
    """, unsafe_allow_html=True)

# --- 5. MAIN LOGIC ---
df = load_data()

if df is not None:
    # Header Section
    st.title("PharmaBuddy")
    
    # 1. FIXED SEARCH
    search = st.text_input("", placeholder="🔍 Search by brand name, generic, company...")

    # 2. DROPDOWN (Category/Brand Browser)
    browse_mode = st.selectbox(
        "Browse Directory By:",
        ["All Medicines", "All Categories", "All Brands"]
    )

    # 3. CHIP FILTERS (From Image 1)
    # Using session state to track chip selection
    if 'active_chip' not in st.session_state: st.session_state.active_chip = "All"
    
    unique_cats = ["All"] + sorted(df['Category'].unique().tolist())
    
    # Render chips in columns
    st.write("---")
    chip_cols = st.columns(4)
    for i, cat_name in enumerate(unique_cats[:12]): # Showing first 12 for UI cleanliness
        if chip_cols[i % 4].button(cat_name, key=f"chip_{cat_name}"):
            st.session_state.active_chip = cat_name

    # --- FILTERING LOGIC ---
    filtered_df = df

    # Filter by Browse Mode Selection
    if browse_mode == "All Categories":
        sel_cat = st.selectbox("Select Category", sorted(df['Category'].unique()))
        filtered_df = df[df['Category'] == sel_cat]
    elif browse_mode == "All Brands":
        sel_brand = st.selectbox("Select Brand", sorted(df['Brand Name'].unique()))
        filtered_df = df[df['Brand Name'] == sel_brand]
    
    # Apply Chip Filter
    if st.session_state.active_chip != "All":
        filtered_df = filtered_df[filtered_df['Category'] == st.session_state.active_chip]

    # Apply Search (Global Search Priority)
    if search:
        filtered_df = filtered_df[
            filtered_df['Brand Name'].str.contains(search, case=False, na=False) |
            filtered_df['Generic Name'].str.contains(search, case=False, na=False) |
            filtered_df['Category'].str.contains(search, case=False, na=False)
        ]

    # Count Text
    st.caption(f"Showing **{len(filtered_df)}** of {len(df)} drugs")

    # Display Cards
    if not filtered_df.empty:
        for _, row in filtered_df.iterrows():
            render_card(row)
    else:
        st.info("No medications found matching your criteria.")

else:
    st.error("Data Load Error. Ensure 'drugs_data.csv' is on GitHub.")

