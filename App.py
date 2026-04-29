import streamlit as st
import pandas as pd

# --- 1. PAGE SETUP ---
st.set_page_config(page_title="PharmaBuddy", page_icon="💊", layout="centered")

# --- 2. THE MODERN UI CSS (Matching your images) ---
st.markdown("""
    <style>
    /* Main Background */
    .stApp { background-color: #f8fbff; }
    
    /* Top Search & Dropdown Container */
    .search-container {
        background-color: white;
        padding: 30px;
        border-radius: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        margin-bottom: 25px;
    }

    /* Category Chips/Pills */
    .stButton > button {
        border-radius: 30px !important;
        border: 1px solid #e2e8f0 !important;
        background-color: white !important;
        color: #475569 !important;
        padding: 6px 18px !important;
        font-weight: 500 !important;
        margin-bottom: 5px !important;
        transition: 0.3s !important;
    }
    .stButton > button:hover {
        border-color: #3b82f6 !important;
        color: #3b82f6 !important;
        background-color: #eff6ff !important;
    }
    /* Style for active filter (if possible with Streamlit) */
    div[data-testid="stHorizontalBlock"] button {
        font-size: 13px !important;
    }

    /* THE DRUG CARD (Exact match to Image 2) */
    .drug-card {
        background: white;
        border-radius: 20px;
        padding: 25px;
        margin-bottom: 20px;
        border-left: 6px solid #f97316; /* Orange Border */
        box-shadow: 0 4px 12px rgba(0,0,0,0.04);
        position: relative;
    }
    
    /* Savings Badge */
    .savings-badge {
        position: absolute;
        top: 20px;
        right: 20px;
        background-color: #f97316;
        color: white;
        padding: 5px 12px;
        border-radius: 12px;
        font-weight: 800;
        text-align: center;
        line-height: 1;
    }
    .savings-text { font-size: 9px; font-weight: normal; text-transform: uppercase; }

    .brand-title { font-size: 22px; font-weight: 800; color: #1e293b; margin-bottom: 2px; }
    .generic-subtitle { color: #94a3b8; font-size: 15px; margin-bottom: 20px; }

    /* Price Boxes */
    .price-row { display: flex; gap: 15px; margin-bottom: 20px; }
    .price-box {
        flex: 1;
        padding: 12px 15px;
        border-radius: 15px;
    }
    .gen-bg { background-color: #f0fdf4; border: 1px solid #dcfce7; }
    .brd-bg { background-color: #fef2f2; border: 1px solid #fee2e2; }
    
    .price-lbl { font-size: 10px; font-weight: 800; letter-spacing: 0.5px; margin-bottom: 4px; }
    .price-amt { font-size: 19px; font-weight: 800; }

    /* Bottom Tags */
    .tag-row { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 15px; }
    .pill-tag {
        background-color: #fff7ed;
        color: #c2410c;
        border: 1px solid #ffedd5;
        padding: 4px 14px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
    }
    .company-name { font-size: 12px; color: #94a3b8; margin-top: 15px; font-weight: 500; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. ROBUST DATA ENGINE ---
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

# --- 4. CARD RENDERER ---
def render_drug_card(row):
    st.markdown(f"""
    <div class="drug-card">
        <div class="savings-badge">
            ↓{row['Savings (%)']}%<br><span class="savings-text">savings</span>
        </div>
        <div class="brand-title">🦠 {row['Brand Name']}</div>
        <div class="generic-subtitle">{row['Generic Name']}</div>
        
        <div class="price-row">
            <div class="price-box gen-bg">
                <div class="price-lbl" style="color:#16a34a;">GENERIC</div>
                <div class="price-amt" style="color:#16a34a;">₹{row['Generic Price (Rs)']}</div>
            </div>
            <div class="price-box brd-bg">
                <div class="price-lbl" style="color:#dc2626;">BRAND</div>
                <div class="price-amt" style="color:#dc2626;">₹{row['Brand Price (Rs)']}</div>
            </div>
        </div>
        
        <div class="tag-row">
            <span class="pill-tag">{row['Category']}</span>
            <span class="pill-tag">💊 {row['Dosage Form']}</span>
            <span class="pill-tag">{row['Indication']}</span>
        </div>
        <div class="company-name">🏢 {row['Company']}</div>
        
        <hr style="margin: 20px 0; border:0; border-top: 1px solid #f1f5f9;">
        <div style="font-size: 13px; color: #64748b; line-height: 1.6;">
            <b>Adverse Effects:</b> {row['Adverse Effects']}<br>
            <b>Interaction:</b> {row['Drug Interaction']}
        </div>
    </div>
    """, unsafe_allow_html=True)

# --- 5. APP LOGIC ---
df = load_data()

if df is not None:
    st.title("PharmaBuddy")
    
    # Session state for filters
    if 'active_cat' not in st.session_state: st.session_state.active_cat = "All"

    # White Container for Search & Dropdown (Image 1 top part)
    with st.container():
        st.markdown('<div class="search-container">', unsafe_allow_html=True)
        search = st.text_input("", placeholder="🔍 Search by brand name, generic, company...")
        
        unique_cats = sorted(df['Category'].unique().tolist())
        sel_dropdown = st.selectbox(f"All Categories ({len(df)})", ["Show All"] + unique_cats)
        
        st.caption(f"Showing medicines based on your selection")
        st.markdown('</div>', unsafe_allow_html=True)

    # Category Chips (Image 1 bottom part)
    st.markdown('<div class="chip-container">', unsafe_allow_html=True)
    chip_cols = st.columns(4)
    if chip_cols[0].button("🔵 All"): st.session_state.active_cat = "All"
    
    # Display a few common category chips for the "Vibe"
    for i, cat in enumerate(unique_cats[:7]):
        if chip_cols[(i+1)%4].button(cat):
            st.session_state.active_cat = cat

    # --- FILTERING ENGINE ---
    filtered = df

    # Priority 1: Dropdown
    if sel_dropdown != "Show All":
        filtered = df[df['Category'] == sel_dropdown]
    # Priority 2: Chip Filter
    elif st.session_state.active_cat != "All":
        filtered = df[df['Category'] == st.session_state.active_cat]
    
    # Priority 3: Search (Global)
    if search:
        filtered = filtered[
            filtered['Brand Name'].str.contains(search, case=False, na=False) |
            filtered['Generic Name'].str.contains(search, case=False, na=False) |
            filtered['Company'].str.contains(search, case=False, na=False)
        ]

    # Display Cards
    if not filtered.empty:
        for _, row in filtered.iterrows():
            render_drug_card(row)
    else:
        st.info("No medicines found matching your criteria.")

else:
    st.error("Please ensure drugs_data.csv is uploaded to GitHub.")

