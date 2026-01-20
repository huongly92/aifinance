"""
Data Loader Module
Load và cache dữ liệu từ Google Drive (cloud) hoặc local files
"""

import streamlit as st
import pandas as pd
import io
import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload


# ============================================
# PHẦN 1: CONFIGURATION
# ============================================

# ⚠️ TODO: THAY THẾ 4 FILE IDs BÊN DƯỚI BẰNG FILE IDs THỰC CỦA BẠN (từ Bước 3.3)
MARKET_FILE_ID = "1aNNTscWUOew7vnpZV18Y0UhfifejrKEQ"
INDUSTRY_FILE_ID = "18M4_ekSvR4skUl6V9ufDyjXssu-NBLdB"
TICKER_FILE_ID = "1__PIPDg1IoHvauhBgN-SNyVAiNZKRbtD"
MAP_FILE_ID = "1Xl9yKLsNnizAZsEaRWwuCTitxe99JDo5"

# Local file paths (dùng khi develop)
LOCAL_DATA_DIR = "D:/aifinance_project/data/output"
LOCAL_MAP_PATH = "D:/aifinance_project/data/raw/Map_Complete.xlsx"


# ============================================
# PHẦN 2: DETECT ENVIRONMENT
# ============================================

def is_running_on_cloud():
    """
    Kiểm tra xem app đang chạy trên cloud hay local
    
    Returns:
        bool: True nếu đang chạy trên cloud (có secrets), False nếu local
    """
    try:
        # Kiểm tra xem có st.secrets và gcp_service_account không
        return hasattr(st, 'secrets') and 'gcp_service_account' in st.secrets
    except:
        return False


# ============================================
# PHẦN 3: GOOGLE DRIVE FUNCTIONS (CLOUD ONLY)
# ============================================

@st.cache_resource
def get_drive_service():
    """
    Tạo kết nối với Google Drive API
    CHỈ GỌI KHI CHẠY TRÊN CLOUD
    
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
        st.error(f"❌ Lỗi khi kết nối Google Drive: {e}")
        st.stop()


@st.cache_data(ttl=3600)  # Cache 1 giờ
def download_file_from_drive(file_id, file_name):
    """
    Download file từ Google Drive bằng File ID
    CHỈ GỌI KHI CHẠY TRÊN CLOUD
    
    Args:
        file_id: Google Drive File ID
        file_name: Tên file (để hiển thị thông báo)
        
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
        st.error(f"❌ Lỗi khi download {file_name}: {e}")
        st.stop()


# ============================================
# PHẦN 4: LOAD DATA - AUTO DETECT LOCAL VS CLOUD
# ============================================

@st.cache_data(ttl=3600)  # Cache 1 giờ
def load_all_data():
    """
    Load tất cả dữ liệu - TỰ ĐỘNG DETECT LOCAL VS CLOUD
    
    - Local: Load từ D:/ (hoặc đường dẫn local)
    - Cloud: Load từ Google Drive
    
    Returns:
        tuple: (market_df, industry_df, ticker_df, map_df)
    """
    
    IS_CLOUD = is_running_on_cloud()
    
    if IS_CLOUD:
        # ========== CLOUD MODE: Load từ Google Drive ==========
        st.info('🌐 Chạy trên Cloud - Đang tải dữ liệu từ Google Drive...')
        
        with st.spinner('🔄 Đang tải dữ liệu từ Google Drive...'):
            try:
                # Download files từ Google Drive
                market_buffer = download_file_from_drive(MARKET_FILE_ID, "market_analysis.parquet")
                industry_buffer = download_file_from_drive(INDUSTRY_FILE_ID, "industry_analysis.parquet")
                ticker_buffer = download_file_from_drive(TICKER_FILE_ID, "ticker_analysis.parquet")
                map_buffer = download_file_from_drive(MAP_FILE_ID, "Map_Complete.xlsx")
                
                # Load vào pandas DataFrames
                market_df = pd.read_parquet(market_buffer)
                industry_df = pd.read_parquet(industry_buffer)
                ticker_df = pd.read_parquet(ticker_buffer)
                map_df = pd.read_excel(map_buffer)
                
                # Sắp xếp theo thời gian
                market_df = market_df.sort_values(['YEAR', 'QUARTER'])
                industry_df = industry_df.sort_values(['SYMBOL', 'YEAR', 'QUARTER'])
                ticker_df = ticker_df.sort_values(['SYMBOL', 'YEAR', 'QUARTER'])
                
                st.success('✅ Đã tải xong dữ liệu từ Google Drive!')
                
                return market_df, industry_df, ticker_df, map_df
                
            except Exception as e:
                st.error(f"❌ Lỗi khi load dữ liệu từ Google Drive: {e}")
                st.stop()
    
    else:
        # ========== LOCAL MODE: Load từ local files ==========
        st.info('💻 Chạy Local - Đang tải dữ liệu từ local files...')
        
        try:
            # Construct file paths
            market_file = f"{LOCAL_DATA_DIR}/market_analysis.parquet"
            industry_file = f"{LOCAL_DATA_DIR}/industry_analysis.parquet"
            ticker_file = f"{LOCAL_DATA_DIR}/ticker_analysis.parquet"
            
            # Kiểm tra files tồn tại
            if not os.path.exists(market_file):
                st.error(f"❌ File không tồn tại: {market_file}")
                st.info(f"💡 Vui lòng kiểm tra đường dẫn hoặc cập nhật LOCAL_DATA_DIR trong utils/data_loader.py")
                st.stop()
            
            # Load từ local files
            market_df = pd.read_parquet(market_file)
            industry_df = pd.read_parquet(industry_file)
            ticker_df = pd.read_parquet(ticker_file)
            map_df = pd.read_excel(LOCAL_MAP_PATH)
            
            # Sắp xếp theo thời gian
            market_df = market_df.sort_values(['YEAR', 'QUARTER'])
            industry_df = industry_df.sort_values(['SYMBOL', 'YEAR', 'QUARTER'])
            ticker_df = ticker_df.sort_values(['SYMBOL', 'YEAR', 'QUARTER'])
            
            st.success('✅ Đã tải xong dữ liệu từ local files!')
            
            return market_df, industry_df, ticker_df, map_df
            
        except Exception as e:
            st.error(f"❌ Lỗi khi load dữ liệu từ local: {e}")
            st.info(f"""
            **Vui lòng kiểm tra:**
            - Đường dẫn local có đúng không?
            - Files có tồn tại không?
            
            **Đường dẫn hiện tại:**
            - LOCAL_DATA_DIR: {LOCAL_DATA_DIR}
            - LOCAL_MAP_PATH: {LOCAL_MAP_PATH}
            
            **Cập nhật trong:** utils/data_loader.py (dòng 17-18)
            """)
            st.stop()


@st.cache_data(ttl=3600)
def get_market_data():
    """
    Load dữ liệu thị trường
    
    Returns:
        DataFrame: Dữ liệu thị trường đã sắp xếp
    """
    market_df, _, _, _ = load_all_data()
    return market_df


@st.cache_data(ttl=3600)
def get_industry_data():
    """
    Load dữ liệu ngành
    
    Returns:
        DataFrame: Dữ liệu ngành đã sắp xếp
    """
    _, industry_df, _, _ = load_all_data()
    return industry_df


@st.cache_data(ttl=3600)
def get_ticker_data():
    """
    Load dữ liệu ticker
    
    Returns:
        DataFrame: Dữ liệu ticker đã sắp xếp
    """
    _, _, ticker_df, _ = load_all_data()
    return ticker_df


@st.cache_data(ttl=3600)
def get_map_data():
    """
    Load dữ liệu mapping (Map_Complete.xlsx)
    
    Returns:
        DataFrame: Dữ liệu mapping
    """
    _, _, _, map_df = load_all_data()
    return map_df


# ============================================
# PHẦN 5: UTILITY FUNCTIONS (GIỮ NGUYÊN)
# ============================================

def get_available_quarters(df):
    """
    Lấy danh sách các quarter có sẵn
    
    Args:
        df: DataFrame chứa cột QUARTER và YEAR
        
    Returns:
        list: Danh sách các quarter theo format 'YYYYQX'
    """
    quarters = df[['YEAR', 'QUARTER']].drop_duplicates()
    quarters['KEY'] = quarters['YEAR'].astype(str) + quarters['QUARTER']
    return sorted(quarters['KEY'].unique())


def get_available_industries(industry_df):
    """
    Lấy danh sách các ngành có sẵn
    
    Args:
        industry_df: DataFrame ngành
        
    Returns:
        list: Danh sách tên ngành
    """
    return sorted(industry_df['SYMBOL'].unique())


def get_available_tickers(ticker_df):
    """
    Lấy danh sách các ticker có sẵn
    
    Args:
        ticker_df: DataFrame ticker
        
    Returns:
        list: Danh sách ticker symbols
    """
    return sorted(ticker_df['SYMBOL'].unique())


def get_ticker_info(ticker_df, symbol):
    """
    Lấy thông tin chi tiết của một ticker
    
    Args:
        ticker_df: DataFrame ticker
        symbol: Mã cổ phiếu
        
    Returns:
        dict: Thông tin ticker hoặc None nếu không tìm thấy
    """
    ticker_data = ticker_df[ticker_df['SYMBOL'] == symbol]
    if ticker_data.empty:
        return None
    
    # Lấy dữ liệu quý gần nhất
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
    Lọc dữ liệu theo khoảng thời gian
    
    Args:
        df: DataFrame
        start_quarter: Quarter bắt đầu (format: 'YYYYQX')
        end_quarter: Quarter kết thúc (format: 'YYYYQX')
        
    Returns:
        DataFrame: Dữ liệu đã được lọc
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
    Lấy dữ liệu quý gần nhất
    
    Args:
        df: DataFrame
        symbol: Mã ticker hoặc ngành (optional)
        
    Returns:
        Series hoặc DataFrame: Dữ liệu quý gần nhất
    """
    if symbol:
        df = df[df['SYMBOL'] == symbol]
    
    if df.empty:
        return None
    
    # Lấy quý gần nhất
    latest_idx = df[['YEAR', 'QUARTER']].apply(lambda x: (x['YEAR'], x['QUARTER']), axis=1).idxmax()
    return df.loc[latest_idx]


def get_metrics_for_tickers(ticker_df, symbols, metrics):
    """
    Lấy các chỉ số tài chính cho nhiều ticker
    
    Args:
        ticker_df: DataFrame ticker
        symbols: List các mã cổ phiếu
        metrics: List các chỉ số cần lấy
        
    Returns:
        DataFrame: Bảng so sánh các chỉ số
    """
    result = []
    
    for symbol in symbols:
        latest = get_latest_data(ticker_df, symbol)
        if latest is not None:
            row = {'Mã CK': symbol}
            for metric in metrics:
                row[metric] = latest.get(metric, None)
            result.append(row)
    
    return pd.DataFrame(result)


def search_tickers(ticker_df, keyword):
    """
    Tìm kiếm ticker theo từ khóa
    
    Args:
        ticker_df: DataFrame ticker
        keyword: Từ khóa tìm kiếm
        
    Returns:
        list: Danh sách ticker phù hợp
    """
    keyword = keyword.upper()
    matching = ticker_df[ticker_df['SYMBOL'].str.contains(keyword, na=False)]['SYMBOL'].unique()
    return sorted(matching)
