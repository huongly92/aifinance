"""
Main Application File
Dashboard Phan Tich Chung Khoan Viet Nam
"""

import streamlit as st
import sys
from pathlib import Path

# ========== CLEAR ALL CACHES AT STARTUP ==========
# This fixes cache issues from previous errors
try:
    st.cache_data.clear()
    st.cache_resource.clear()
except:
    pass

# Add root directory to path
ROOT_DIR = Path(__file__).parent
sys.path.insert(0, str(ROOT_DIR))

import config
from data_loader import load_all_data
from excel_helper import get_excel_processor

# ========== PAGE CONFIGURATION ==========
st.set_page_config(
    page_title=config.APP_TITLE,
    page_icon=config.APP_ICON,
    layout=config.LAYOUT,
    initial_sidebar_state=config.INITIAL_SIDEBAR_STATE
)

# ========== CONFIGURATION - GOOGLE DRIVE FILE IDs ==========
MAP_FILE_ID = "1Xl9yKLsNnizAZsEaRWwuCTitxe99JDo5"
LOCAL_MAP_PATH = "D:/aifinance_project/data/raw/Map_Complete.xlsx"

# ========== LOAD DATA ==========
@st.cache_data(ttl=3600, show_spinner=True)
def load_data():
    """
    Load all data from Google Drive with caching
    """
    return load_all_data()

# ========== LOAD EXCEL PROCESSOR ==========
@st.cache_resource
def load_excel_processor():
    """
    Load Excel Processor
    """
    processor = get_excel_processor(
        local_file_path=LOCAL_MAP_PATH,
        gdrive_file_id=MAP_FILE_ID,
        file_name="Map_Complete.xlsx"
    )
    return processor

# ========== INITIALIZE DATA ==========
try:
    # Load parquet data (market, industry, ticker, map)
    market_df, industry_df, ticker_df, map_df = load_data()
    
    # Store in session state
    if 'market_df' not in st.session_state:
        st.session_state.market_df = market_df
    if 'industry_df' not in st.session_state:
        st.session_state.industry_df = industry_df
    if 'ticker_df' not in st.session_state:
        st.session_state.ticker_df = ticker_df
    if 'map_df' not in st.session_state:
        st.session_state.map_df = map_df
        
except Exception as e:
    st.error(f"""
    **Error loading data!**
    
    **If running on Cloud:**
    - Check Streamlit Secrets are configured correctly
    - Verify File IDs in data_loader.py
    - Ensure files are shared with Service Account
    
    **Error details:** {str(e)}
    """)
    
    # Show debug info
    with st.expander("🔍 Debug Information"):
        import traceback
        st.code(traceback.format_exc())
        
        st.markdown("### Troubleshooting:")
        st.markdown("""
        1. Check if files are shared with Service Account
        2. Verify Streamlit Secrets are saved
        3. Try running diagnostic tool (app_diagnostic_v2.py)
        4. Check File IDs are correct
        """)
    
    st.stop()

# ========== SIDEBAR ==========
with st.sidebar:
    st.title(config.APP_ICON + " Dashboard CK")
    st.markdown("---")
    
    # Navigation
    st.markdown("### 📌 Navigation")
    st.markdown("""
    - 🏛️ Market Overview
    - 🏭 Industry Analysis
    - 📊 Stock Analysis
    - ⚖️ Comparison
    - 🔍 Screening
    - ⭐ Watchlist
    """)
    
    st.markdown("---")
    
    # Data info
    st.markdown("### 📈 Data Information")
    st.info(f"""
    **Market**: {len(market_df)} quarters  
    **Industries**: {industry_df['SYMBOL'].nunique()} sectors  
    **Stocks**: {ticker_df['SYMBOL'].nunique()} tickers
    """)
    
    # Latest quarter
    latest_quarter = market_df.iloc[-1]['QUARTER']
    latest_year = market_df.iloc[-1]['YEAR']
    st.success(f"📅 Latest: **{latest_quarter} {latest_year}**")
    
    st.markdown("---")
    st.caption("Dashboard v1.0 | BSC Research")

# ========== MAIN PAGE ==========
st.title("📊 Vietnam Stock Market Analysis Dashboard")

st.markdown("""
### Welcome to Stock Analysis Dashboard! 👋

This dashboard provides comprehensive analysis tools for stock investors:

#### 🎯 Main Features:

1. **🏛️ Market Overview**
   - Track market trends over time
   - Analyze macro indicators (P/E, P/B, ROE, etc.)
   - Assess overall market health

2. **🏭 Industry Analysis**
   - Compare performance across industries
   - Industry rankings by criteria
   - Identify sector rotation trends

3. **📊 Stock Analysis**
   - Deep dive into individual stocks
   - Valuation, profitability, cash flow analysis
   - Risk analysis with Z-Score

4. **⚖️ Comparison**
   - Compare multiple stocks
   - Correlation matrix
   - Comprehensive scoring and ranking

5. **🔍 Screening**
   - Find investment opportunities with multi-criteria filters
   - Pre-built screening strategies
   - Export results

6. **⭐ Watchlist**
   - Manage personal watchlist
   - Track changes
   - Portfolio analysis

---

### 🚀 How to use:

1. **Select page** from left navigation
2. **Customize filters** as needed
3. **Interact with charts**: zoom, pan, hover for details
4. **Export data** when needed

---

### 📊 Data Statistics:
""")

# Display data statistics
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Quarters",
        len(market_df),
        help="Total quarters of market data"
    )

with col2:
    st.metric(
        "Industries",
        industry_df['SYMBOL'].nunique(),
        help="Total industries analyzed"
    )

with col3:
    st.metric(
        "Stocks",
        ticker_df['SYMBOL'].nunique(),
        help="Total stock tickers"
    )

st.markdown("---")

# Quick stats
st.markdown("### 📈 Quick Stats (Latest Quarter)")

latest_market = market_df.iloc[-1]

col1, col2, col3, col4 = st.columns(4)

with col1:
    from utils.formatters import format_billion, format_change
    market_cap = latest_market.get('MARKET_CAP_EOQ', 0)
    market_cap_change = latest_market.get('MARKET_CAP_EOQ_GYOY', 0) if 'MARKET_CAP_EOQ_GYOY' in latest_market else None
    st.metric(
        "Market Cap",
        format_billion(market_cap),
        format_change(market_cap_change) if market_cap_change else None
    )

with col2:
    from utils.formatters import format_ratio
    st.metric(
        "Avg P/E",
        format_ratio(latest_market.get('PE_EOQ', 0)),
        help="Average Price-to-Earnings ratio"
    )

with col3:
    from utils.formatters import format_percent
    st.metric(
        "Avg ROE",
        format_percent(latest_market.get('ROAE', 0)),
        help="Average Return on Equity"
    )

with col4:
    st.metric(
        "Avg P/B",
        format_ratio(latest_market.get('PB_EOQ', 0)),
        help="Average Price-to-Book ratio"
    )

st.markdown("---")

st.info("""
💡 **Tips:**
- Use left sidebar to navigate between pages
- Each page has filters to customize analysis
- Charts are interactive - zoom, pan, and download
- Tables can be sorted and exported
""")

st.markdown("---")
st.caption("© 2024 BSC Research | Dashboard v1.0")

st.success("✅ Data loaded successfully! Select a page from the sidebar to start analyzing.")
