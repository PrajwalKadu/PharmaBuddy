import streamlit as st
import pandas as pd

# Set page config for a professional look
st.set_page_config(
    page_title="MedSave | Drug Information Portal",
    page_icon="💊",
    layout="centered"
)

# Custom CSS for a cleaner UI
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        border-color: #ff4b4b;
        color: #ff4b4b;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .category-header {
        color: #1f77b4;
        margin-top: 2rem;
        padding-bottom: 5px;
        border-bottom: 2px solid #1f77b4;
    }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data
def load_data():
    df = pd.read_csv("drugs_data.csv")
    # Ensure numeric columns are actually numbers
    df['Generic Price (Rs)'] = pd.to_numeric(df['Generic Price (Rs)'], errors='coerce')
    df['Brand Price (Rs)'] = pd.to_numeric(df['Brand Price (Rs)'], errors='coerce')
    return df

try:
    df = load_data()

    if 'view_drug' not in st.session_state:
        st.session_state.view_drug = None

    # --- DETAIL VIEW ---
    if st.session_state.view_drug is not None:
        row = df.iloc[st.session_state.view_drug]
        
        if st.button("⬅ Back to Directory"):
            st.session_state.view_drug = None
            st.rerun()

        st.title(row['Brand Name'])
        st.caption(f"{row['Category']} | {row['Company']}")
        
        # Financial Highlights
        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("Brand Price", f"₹{row['Brand Price (Rs)']}")
        with c2:
            st.metric("Generic Price", f"₹{row['Generic Price (Rs)']}")
        with c3:
            st.metric("Savings", f"{row['Savings (%)']}%", delta="Available", delta_color="normal")

        # Clinical Details
        st.markdown("### Clinical Profile")
        col_left, col_right = st.columns(2)
        
        with col_left:
            st.write(f"**Generic Name:** {row['Generic Name']}")
            st.write(f"**Dosage Form:** {row['Dosage Form']}")
            st.write(f"**Indication:** {row['Indication']}")

        with col_right:
            st.info(f"**Adverse Effects:**\n{row['Adverse Effects']}")
            st.warning(f"**Drug Interaction:**\n{row['Drug Interaction']}")

    # --- MAIN DIRECTORY VIEW ---
    else:
        st.title("💊 MedSave Directory")
        st.subheader("Compare drug prices and information")

        # Modern Search Bar
        search_query = st.text_input("🔍 Search by Brand, Generic Name, or Indication", placeholder="e.g. Paracetamol")

        # Filter Logic
        if search_query:
            mask = (
                df['Brand Name'].str.contains(search_query, case=False, na=False) |
                df['Generic Name'].str.contains(search_query, case=False, na=False) |
                df['Indication'].str.contains(search_query, case=False, na=False)
            )
            filtered_df = df[mask]
        else:
            filtered_df = df

        # Grouping by Category
        categories = filtered_df['Category'].unique()

        for cat in categories:
            st.markdown(f"<h2 class='category-header'>{cat}</h2>", unsafe_allow_html=True)
            
            # Get all drugs in this category
            cat_df = filtered_df[filtered_df['Category'] == cat]
            
            # Create a grid of buttons for brands
            for idx, row in cat_df.iterrows():
                if st.button(row['Brand Name'], key=f"btn_{idx}"):
                    st.session_state.view_drug = idx
                    st.rerun()

except FileNotFoundError:
    st.error("Error: 'drugs_data.csv' not found. Please upload it to your GitHub repository.")
except Exception as e:
    st.error(f"An error occurred: {e}")