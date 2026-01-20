"""
Vietnam Stock Market Dashboard - Minimal Version
Guaranteed to work - no complex dependencies
"""

import streamlit as st
import pandas as pd
import io
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

# ========== CLEAR CACHE ==========
try:
    st.cache_data.clear()
    st.cache_resource.clear()
except:
    pass

# ========== PAGE CONFIG ==========
st.set_page_config(
    page_title="Vietnam Stock Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ========== FILE IDS ==========
MARKET_FILE_ID = "1aNNTscWUOew7vnpZV18Y0UhfifejrKEQ"
INDUSTRY_FILE_ID = "18M4_ekSvR4skUl6V9ufDyjXssu-NBLdB"
TICKER_FILE_ID = "1__PIPDg1IoHvauhBgN-SNyVAiNZKRbtD"
MAP_FILE_ID = "1Xl9yKLsNnizAZsEaRWwuCTitxe99JDo5"

# ========== HELPER FUNCTIONS ==========
def is_running_on_cloud():
    """Check if running on Streamlit Cloud"""
    try:
        return hasattr(st, 'secrets') and 'gcp_service_account' in st.secrets
    except:
        return False

@st.cache_resource
def get_drive_service():
    """Get Google Drive service"""
    credentials = service_account.Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=['https://www.googleapis.com/auth/drive.readonly']
    )
    service = build('drive', 'v3', credentials=credentials)
    return service

def download_file(file_id, file_name):
    """Download file from Google Drive"""
    try:
        service = get_drive_service()
        request = service.files().get_media(fileId=file_id)
        
        file_buffer = io.BytesIO()
        downloader = MediaIoBaseDownload(file_buffer, request)
        
        done = False
        while not done:
            status, done = downloader.next_chunk()
        
        file_buffer.seek(0)
        return file_buffer
    except Exception as e:
        st.error(f"Error downloading {file_name}: {e}")
        raise

# ========== LOAD DATA ==========
@st.cache_data(ttl=3600, show_spinner="Loading data from Google Drive...")
def load_all_data():
    """Load all data from Google Drive"""
    try:
        # Download files
        market_buffer = download_file(MARKET_FILE_ID, "market_analysis.parquet")
        industry_buffer = download_file(INDUSTRY_FILE_ID, "industry_analysis.parquet")
        ticker_buffer = download_file(TICKER_FILE_ID, "ticker_analysis.parquet")
        map_buffer = download_file(MAP_FILE_ID, "Map_Complete.xlsx")
        
        # Load into DataFrames
        market_df = pd.read_parquet(market_buffer)
        industry_df = pd.read_parquet(industry_buffer)
        ticker_df = pd.read_parquet(ticker_buffer)
        map_df = pd.read_excel(map_buffer)
        
        # Sort
        market_df = market_df.sort_values(['YEAR', 'QUARTER'])
        industry_df = industry_df.sort_values(['SYMBOL', 'YEAR', 'QUARTER'])
        ticker_df = ticker_df.sort_values(['SYMBOL', 'YEAR', 'QUARTER'])
        
        return market_df, industry_df, ticker_df, map_df
        
    except Exception as e:
        st.error(f"Error loading data: {e}")
        raise

# ========== FORMATTING HELPERS ==========
def format_number(value, decimals=2):
    """Format number with commas"""
    try:
        if value is None:
            return "N/A"
        return f"{value:,.{decimals}f}"
    except:
        return "N/A"

def format_billion(value):
    """Format as billions"""
    try:
        if value is None or value == 0:
            return "0B"
        return f"{value/1_000_000_000:,.2f}B"
    except:
        return "N/A"

def format_percent(value):
    """Format as percentage"""
    try:
        if value is None:
            return "N/A"
        if abs(value) > 1:
            return f"{value:.2f}%"
        else:
            return f"{value*100:.2f}%"
    except:
        return "N/A"

# ========== MAIN APP ==========
def main():
    # Load data
    try:
        market_df, industry_df, ticker_df, map_df = load_all_data()
    except Exception as e:
        st.error(f"""
        **Failed to load data!**
        
        Please check:
        1. Streamlit Secrets are configured correctly
        2. Files are shared with Service Account: aifinance@aifinance-484901.iam.gserviceaccount.com
        3. File IDs are correct
        
        Error: {str(e)}
        """)
        st.stop()
    
    # ========== SIDEBAR ==========
    with st.sidebar:
        st.title("📊 Dashboard")
        st.markdown("---")
        
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
        
        st.markdown("### 📈 Data Info")
        st.info(f"""
        **Market**: {len(market_df)} quarters  
        **Industries**: {industry_df['SYMBOL'].nunique()}  
        **Stocks**: {ticker_df['SYMBOL'].nunique()}
        """)
        
        # Latest quarter
        latest = market_df.iloc[-1]
        st.success(f"📅 Latest: **{latest['QUARTER']} {latest['YEAR']}**")
        
        st.markdown("---")
        st.caption("Dashboard v1.0")
    
    # ========== MAIN CONTENT ==========
    st.title("📊 Vietnam Stock Market Analysis Dashboard")
    
    st.markdown("""
    ### Welcome! 👋
    
    This dashboard provides comprehensive stock market analysis tools.
    
    #### 🎯 Features:
    - 🏛️ **Market Overview** - Track market trends and indicators
    - 🏭 **Industry Analysis** - Compare industry performance
    - 📊 **Stock Analysis** - Deep dive into individual stocks
    - ⚖️ **Comparison** - Compare multiple stocks
    - 🔍 **Screening** - Find investment opportunities
    - ⭐ **Watchlist** - Manage your watchlist
    """)
    
    st.markdown("---")
    st.markdown("### 📊 Data Overview")
    
    # Stats
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Data Quarters", len(market_df))
    
    with col2:
        st.metric("Industries", industry_df['SYMBOL'].nunique())
    
    with col3:
        st.metric("Stock Tickers", ticker_df['SYMBOL'].nunique())
    
    st.markdown("---")
    st.markdown("### 📈 Latest Market Stats")
    
    latest = market_df.iloc[-1]
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        market_cap = latest.get('MARKET_CAP_EOQ', 0)
        st.metric("Market Cap", format_billion(market_cap))
    
    with col2:
        pe = latest.get('PE_EOQ', 0)
        st.metric("Avg P/E", format_number(pe))
    
    with col3:
        roe = latest.get('ROAE', 0)
        st.metric("Avg ROE", format_percent(roe))
    
    with col4:
        pb = latest.get('PB_EOQ', 0)
        st.metric("Avg P/B", format_number(pb))
    
    st.markdown("---")
    
    # Sample data
    with st.expander("📊 View Sample Market Data"):
        st.dataframe(market_df.tail(10))
    
    with st.expander("🏭 View Sample Industry Data"):
        st.dataframe(industry_df.tail(10))
    
    with st.expander("📈 View Sample Ticker Data"):
        st.dataframe(ticker_df.tail(10))
    
    st.markdown("---")
    
    st.success("""
    ✅ **Data loaded successfully!**
    
    Dashboard is ready to use. Use the navigation in the sidebar to explore different analysis tools.
    """)
    
    st.info("""
    💡 **Tips:**
    - Select different pages from the sidebar
    - Charts are interactive - hover, zoom, pan
    - Tables can be sorted by clicking column headers
    - Use expanders above to view raw data
    """)
    
    st.markdown("---")
    st.caption("© 2024 BSC Research | Dashboard v1.0")

# ========== RUN APP ==========
if __name__ == "__main__":
    main()
