import streamlit as st
import pandas as pd

# --- PAGE CONFIG ---
st.set_page_config(page_title="PharmaBuddy", page_icon="💊", layout="centered")

# --- ADVANCED UX STYLING (Kept exactly as your original) ---
st.markdown("""
    <style>
    .stApp { background-color: #f4f7f6; }
    
    /* Comparison Card Styling */
    .compare-card {
        background-color: white;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #e0e0e0;
        margin-bottom: 15px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .brand-text { color: #1e3a8a; font-size: 18px; font-weight: bold; }
    .generic-text { color: #059669; font-size: 16px; font-weight: 600; }
    .price-box { font-size: 20px; font-weight: bold; color: #111827; }
    .savings-badge {
        background-color: #dcfce7;
        color: #166534;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: bold;
        font-size: 14px;
    }
    .vs-text { font-style: italic; color: #6b7280; font-size: 14px; margin: 0 10px; }
    
    /* Category Title */
    .cat-title {
        font-size: 22px;
        font-weight: 800;
        color: #374151;
        margin: 30px 0 15px 0;
        border-left: 5px solid #1e3a8a;
        padding-left: 15px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- DATA ENGINE (Kept exactly as your original) ---
@st.cache_data
def load_data():
    try:
        df = pd.read_csv(
            "drugs_data.csv", 
            encoding='latin1', 
            on_bad_lines='skip', 
            engine='python',
            sep=None 
        )
        df.columns = [c.strip() for c in df.columns]
        for col in ['Generic Price (Rs)', 'Brand Price (Rs)', 'Savings (%)']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        return df
    except Exception as e:
        st.error(f"Data Error: {e}")
        return None

df = load_data()

# --- APP NAVIGATION ---
if df is not None:
    if 'view' not in st.session_state:
        st.session_state.view = "home"
        st.session_state.item = None

    # --- DETAIL VIEW (Kept exactly as your original) ---
    if st.session_state.view == "details":
        row = st.session_state.item
        if st.button("⬅ Back to Comparisons"):
            st.session_state.view = "home"
            st.rerun()
            
        st.title(row['Brand Name'])
        st.subheader(f"Generic: {row['Generic Name']}")
        
        st.divider()
        
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"### Brand\n**{row['Brand Name']}**\n## ₹{row['Brand Price (Rs)']}")
            st.caption(f"Manufacturer: {row['Company']}")
        with c2:
            st.markdown(f"### Generic Equivalent\n**{row['Generic Name']}**\n## ₹{row['Generic Price (Rs)']}")
            st.success(f"**Save {row['Savings (%)']}%**")

        st.markdown("### 📋 Clinical Details")
        st.info(f"**Dosage Form:** {row['Dosage Form']}\n\n**Indication:** {row['Indication']}")
        
        with st.expander("Safety Information"):
            st.warning(f"**Adverse Effects:** {row['Adverse_Effects'] if 'Adverse_Effects' in row else row.get('Adverse Effects', 'N/A')}")
            st.error(f"**Drug Interaction:** {row['Drug Interaction']}")

    # --- HOME VIEW (WITH NEW DROPDOWN LOGIC) ---
    else:
        st.title("💊 PharmaBuddy")
        st.markdown("Compare **Brand vs Generic** prices instantly.")

        # 1. New Dropdown Feature
        browse_option = st.selectbox(
            "Browse Directory By:",
            ["Default / Search", "All Categories", "All Brands"]
        )

        # 2. Filtering Logic based on dropdown
        filtered = df
        
        if browse_option == "All Categories":
            unique_cats = sorted(df['Category'].unique())
            selected_cat = st.selectbox("Select Category", unique_cats)
            filtered = df[df['Category'] == selected_cat]
        
        elif browse_option == "All Brands":
            unique_brands = sorted(df['Brand Name'].unique())
            selected_brand = st.selectbox("Select Brand", unique_brands)
            filtered = df[df['Brand Name'] == selected_brand]
        
        else:
            # DEFAULT MODE: As per your previous code
            search = st.text_input("", placeholder="Search medicine, category or salts...")
            if search:
                mask = (df['Brand Name'].str.contains(search, case=False, na=False) | 
                        df['Generic Name'].str.contains(search, case=False, na=False) |
                        df['Category'].str.contains(search, case=False, na=False))
                filtered = df[mask]

        # 3. Group by Category Display (Kept exactly as your original)
        if not filtered.empty:
            # We group by Category even in search/dropdown modes for consistency
            for cat in filtered['Category'].unique():
                st.markdown(f"<div class='cat-title'>{cat}</div>", unsafe_allow_html=True)
                cat_df = filtered[filtered['Category'] == cat]
                
                for idx, row in cat_df.iterrows():
                    with st.container():
                        st.markdown(f"""
                        <div class="compare-card">
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <div>
                                    <span class="brand-text">{row['Brand Name']}</span>
                                    <span class="vs-text">vs</span>
                                    <span class="generic-text">{row['Generic Name']}</span>
                                </div>
                                <span class="savings-badge">Save {row['Savings (%)']}%</span>
                            </div>
                            <div style="margin-top: 10px; display: flex; gap: 20px;">
                                <div><small>Brand Price</small><br><span class="price-box">₹{row['Brand Price (Rs)']}</span></div>
                                <div><small>Generic Price</small><br><span class="price-box" style="color: #059669;">₹{row['Generic Price (Rs)']}</span></div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        if st.button(f"View Full Details for {row['Brand Name']}", key=f"btn_{idx}"):
                            st.session_state.view = "details"
                            st.session_state.item = row
                            st.rerun()
        else:
            st.info("No medicines found.")

else:
    st.error("Please ensure drugs_data.csv is uploaded.")

