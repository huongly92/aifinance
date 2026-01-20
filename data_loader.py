"""
Data Loader Module
Load and cache data from Google Drive (cloud) or local files
"""

import streamlit as st
import pandas as pd
import io
import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload


# ============================================
# CONFIGURATION
# ============================================

# TODO: Replace these File IDs with your actual Google Drive File IDs
MARKET_FILE_ID = "1aNNTscWUOew7vnpZV18Y0UhfifejrKEQ"
INDUSTRY_FILE_ID = "18M4_ekSvR4skUl6V9ufDyjXssu-NBLdB"
TICKER_FILE_ID = "1__PIPDg1IoHvauhBgN-SNyVAiNZKRbtD"
MAP_FILE_ID = "1Xl9yKLsNnizAZsEaRWwuCTitxe99JDo5"

# Local file paths (for development)
LOCAL_DATA_DIR = "D:/aifinance_project/data/output"
LOCAL_MAP_PATH = "D:/aifinance_project/data/raw/Map_Complete.xlsx"


# ============================================
# ENVIRONMENT DETECTION
# ============================================

def is_running_on_cloud():
    """
    Check if app is running on cloud or local
    
    Returns:
        bool: True if running on cloud (has secrets), False if local
    """
    try:
        return hasattr(st, 'secrets') and 'gcp_service_account' in st.secrets
    except:
        return False


# ============================================
# GOOGLE DRIVE FUNCTIONS (CLOUD ONLY)
# ============================================

@st.cache_resource
def get_drive_service():
    """
    Create connection to Google Drive API
    ONLY CALL WHEN RUNNING ON CLOUD
    
    Returns:
        Resource: Google Drive API service
    """
    try:
        credentials = service_account.Credentials.from_service_account_info(
            st.secrets["gcp_service_account"],
            scopes=['https://www.googleapis.com/auth/drive.readonly']
        )
        service = build('drive', 'v3', credentials=credentials)
        return service
    except Exception as e:
        st.error(f"Error connecting to Google Drive: {e}")
        st.stop()


@st.cache_data(ttl=3600)  # Cache for 1 hour
def download_file_from_drive(file_id, file_name):
    """
    Download file from Google Drive using File ID
    ONLY CALL WHEN RUNNING ON CLOUD
    
    Args:
        file_id: Google Drive File ID
        file_name: File name (for display)
        
    Returns:
        BytesIO: File buffer
    """
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
        st.stop()


# ============================================
# LOAD DATA - AUTO DETECT LOCAL VS CLOUD
# ============================================

@st.cache_data(ttl=3600)  # Cache for 1 hour
def load_all_data():
    """
    Load all data - AUTO DETECT LOCAL VS CLOUD
    
    - Local: Load from D:/ (or local path)
    - Cloud: Load from Google Drive
    
    Returns:
        tuple: (market_df, industry_df, ticker_df, map_df)
    """
    
    IS_CLOUD = is_running_on_cloud()
    
    if IS_CLOUD:
        # ========== CLOUD MODE: Load from Google Drive ==========
        st.info('Cloud mode - Loading data from Google Drive...')
        
        with st.spinner('Loading data from Google Drive...'):
            try:
                # Download files from Google Drive
                market_buffer = download_file_from_drive(MARKET_FILE_ID, "market_analysis.parquet")
                industry_buffer = download_file_from_drive(INDUSTRY_FILE_ID, "industry_analysis.parquet")
                ticker_buffer = download_file_from_drive(TICKER_FILE_ID, "ticker_analysis.parquet")
                map_buffer = download_file_from_drive(MAP_FILE_ID, "Map_Complete.xlsx")
                
                # Load into pandas DataFrames
                market_df = pd.read_parquet(market_buffer)
                industry_df = pd.read_parquet(industry_buffer)
                ticker_df = pd.read_parquet(ticker_buffer)
                map_df = pd.read_excel(map_buffer)
                
                # Sort by time
                market_df = market_df.sort_values(['YEAR', 'QUARTER'])
                industry_df = industry_df.sort_values(['SYMBOL', 'YEAR', 'QUARTER'])
                ticker_df = ticker_df.sort_values(['SYMBOL', 'YEAR', 'QUARTER'])
                
                st.success('Successfully loaded data from Google Drive!')
                
                return market_df, industry_df, ticker_df, map_df
                
            except Exception as e:
                st.error(f"Error loading data from Google Drive: {e}")
                st.stop()
    
    else:
        # ========== LOCAL MODE: Load from local files ==========
        st.info('Local mode - Loading data from local files...')
        
        try:
            # Construct file paths
            market_file = f"{LOCAL_DATA_DIR}/market_analysis.parquet"
            industry_file = f"{LOCAL_DATA_DIR}/industry_analysis.parquet"
            ticker_file = f"{LOCAL_DATA_DIR}/ticker_analysis.parquet"
            
            # Check if files exist
            if not os.path.exists(market_file):
                st.error(f"File not found: {market_file}")
                st.info(f"Please check path or update LOCAL_DATA_DIR in data_loader.py")
                st.stop()
            
            # Load from local files
            market_df = pd.read_parquet(market_file)
            industry_df = pd.read_parquet(industry_file)
            ticker_df = pd.read_parquet(ticker_file)
            map_df = pd.read_excel(LOCAL_MAP_PATH)
            
            # Sort by time
            market_df = market_df.sort_values(['YEAR', 'QUARTER'])
            industry_df = industry_df.sort_values(['SYMBOL', 'YEAR', 'QUARTER'])
            ticker_df = ticker_df.sort_values(['SYMBOL', 'YEAR', 'QUARTER'])
            
            st.success('Successfully loaded data from local files!')
            
            return market_df, industry_df, ticker_df, map_df
            
        except Exception as e:
            st.error(f"Error loading data from local: {e}")
            st.info(f"""
            Please check:
            - Are the local paths correct?
            - Do the files exist?
            
            Current paths:
            - LOCAL_DATA_DIR: {LOCAL_DATA_DIR}
            - LOCAL_MAP_PATH: {LOCAL_MAP_PATH}
            
            Update in: data_loader.py (lines 17-18)
            """)
            st.stop()


@st.cache_data(ttl=3600)
def get_market_data():
    """
    Load market data
    
    Returns:
        DataFrame: Sorted market data
    """
    market_df, _, _, _ = load_all_data()
    return market_df


@st.cache_data(ttl=3600)
def get_industry_data():
    """
    Load industry data
    
    Returns:
        DataFrame: Sorted industry data
    """
    _, industry_df, _, _ = load_all_data()
    return industry_df


@st.cache_data(ttl=3600)
def get_ticker_data():
    """
    Load ticker data
    
    Returns:
        DataFrame: Sorted ticker data
    """
    _, _, ticker_df, _ = load_all_data()
    return ticker_df


@st.cache_data(ttl=3600)
def get_map_data():
    """
    Load mapping data (Map_Complete.xlsx)
    
    Returns:
        DataFrame: Mapping data
    """
    _, _, _, map_df = load_all_data()
    return map_df


# ============================================
# UTILITY FUNCTIONS
# ============================================

def get_available_quarters(df):
    """
    Get list of available quarters
    
    Args:
        df: DataFrame with QUARTER and YEAR columns
        
    Returns:
        list: List of quarters in format 'YYYYQX'
    """
    quarters = df[['YEAR', 'QUARTER']].drop_duplicates()
    quarters['KEY'] = quarters['YEAR'].astype(str) + quarters['QUARTER']
    return sorted(quarters['KEY'].unique())


def get_available_industries(industry_df):
    """
    Get list of available industries
    
    Args:
        industry_df: Industry DataFrame
        
    Returns:
        list: List of industry names
    """
    return sorted(industry_df['SYMBOL'].unique())


def get_available_tickers(ticker_df):
    """
    Get list of available tickers
    
    Args:
        ticker_df: Ticker DataFrame
        
    Returns:
        list: List of ticker symbols
    """
    return sorted(ticker_df['SYMBOL'].unique())


def get_ticker_info(ticker_df, symbol):
    """
    Get detailed information for a ticker
    
    Args:
        ticker_df: Ticker DataFrame
        symbol: Stock symbol
        
    Returns:
        dict: Ticker information or None if not found
    """
    ticker_data = ticker_df[ticker_df['SYMBOL'] == symbol]
    if ticker_data.empty:
        return None
    
    # Get latest quarter data
    latest = ticker_data.iloc[-1]
    
    return {
        'symbol': symbol,
        'industry': latest.get('LEVEL2_NAME_EN', 'N/A'),
        'cal_group': latest.get('CAL_GROUP', 'N/A'),
        'latest_quarter': latest.get('QUARTER', 'N/A'),
        'latest_year': latest.get('YEAR', 'N/A')
    }


def filter_data_by_date_range(df, start_quarter, end_quarter):
    """
    Filter data by date range
    
    Args:
        df: DataFrame
        start_quarter: Start quarter (format: 'YYYYQX')
        end_quarter: End quarter (format: 'YYYYQX')
        
    Returns:
        DataFrame: Filtered data
    """
    start_year = int(start_quarter[:4])
    start_q = int(start_quarter[-1])
    end_year = int(end_quarter[:4])
    end_q = int(end_quarter[-1])
    
    mask = (
        ((df['YEAR'] > start_year) | ((df['YEAR'] == start_year) & (df['QUARTER'].str[-1].astype(int) >= start_q))) &
        ((df['YEAR'] < end_year) | ((df['YEAR'] == end_year) & (df['QUARTER'].str[-1].astype(int) <= end_q)))
    )
    
    return df[mask]


def get_latest_data(df, symbol=None):
    """
    Get latest quarter data
    
    Args:
        df: DataFrame
        symbol: Ticker or industry symbol (optional)
        
    Returns:
        Series or DataFrame: Latest quarter data
    """
    if symbol:
        df = df[df['SYMBOL'] == symbol]
    
    if df.empty:
        return None
    
    # Get latest quarter
    latest_idx = df[['YEAR', 'QUARTER']].apply(lambda x: (x['YEAR'], x['QUARTER']), axis=1).idxmax()
    return df.loc[latest_idx]


def get_metrics_for_tickers(ticker_df, symbols, metrics):
    """
    Get financial metrics for multiple tickers
    
    Args:
        ticker_df: Ticker DataFrame
        symbols: List of stock symbols
        metrics: List of metrics to retrieve
        
    Returns:
        DataFrame: Comparison table of metrics
    """
    result = []
    
    for symbol in symbols:
        latest = get_latest_data(ticker_df, symbol)
        if latest is not None:
            row = {'Symbol': symbol}
            for metric in metrics:
                row[metric] = latest.get(metric, None)
            result.append(row)
    
    return pd.DataFrame(result)


def search_tickers(ticker_df, keyword):
    """
    Search tickers by keyword
    
    Args:
        ticker_df: Ticker DataFrame
        keyword: Search keyword
        
    Returns:
        list: List of matching tickers
    """
    keyword = keyword.upper()
    matching = ticker_df[ticker_df['SYMBOL'].str.contains(keyword, na=False)]['SYMBOL'].unique()
    return sorted(matching)
