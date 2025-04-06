import streamlit as st

st.set_page_config(page_title="Market Pulse", layout="wide")
st.title("📊 Welcome to MarketPulse Dashboard")

st.write("""
Real-Time Market Intelligence, Simplified.
""")

# Navigation shortcuts (optional, opens sidebar page links in new tabs)
st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    st.page_link("pages/Correlation-Heatmap.py", label="📈 Correlation Heatmap", icon="📊")
    st.page_link("pages/COT_Asset_Data.py", label="📁 COT Asset Data", icon="📂")
    st.page_link("pages/COT_Data_History.py", label="📜 COT Data History", icon="🕰️")

with col2:
    st.page_link("pages/NSE_Financial_Dashboard.py", label="🏦 NSE Financial Dashboard", icon="📉")
    st.page_link("pages/NSE_Mutual_Funds_Dashboard.py", label="💼 NSE Mutual Funds Dashboard", icon="📋")


