"""
Main Application File
Dashboard Phân Tích Chứng Khoán Việt Nam
"""

import streamlit as st
import sys
from pathlib import Path

# Add root directory to path
ROOT_DIR = Path(__file__).parent
sys.path.insert(0, str(ROOT_DIR))

import config
from utils.data_loader import load_all_data
from excel_helper import get_excel_processor

# ========== PAGE CONFIGURATION ==========
st.set_page_config(
    page_title=config.APP_TITLE,
    page_icon=config.APP_ICON,
    layout=config.LAYOUT,
    initial_sidebar_state=config.INITIAL_SIDEBAR_STATE
)

# ========== CONFIGURATION - GOOGLE DRIVE FILE IDs ==========
# TODO: Thay thế các FILE IDs bên dưới bằng File IDs thực từ Google Drive của bạn
# (Đã setup ở Bước 3.3)

# Map File ID (cho Excel processor)
MAP_FILE_ID = "1Xl9yKLsNnizAZsEaRWwuCTitxe99JDo5"  # ← File ID từ file app.py cũ của bạn

# Đường dẫn local (dùng khi develop)
LOCAL_MAP_PATH = "D:/aifinance_project/data/raw/Map_Complete.xlsx"

# ========== LOAD DATA ==========
@st.cache_data(ttl=3600)
def load_data():
    """
    Load tất cả dữ liệu từ Google Drive và cache
    Tự động load từ Google Drive khi deploy, hoặc từ local khi develop
    """
    return load_all_data()

# ========== LOAD EXCEL PROCESSOR ==========
@st.cache_resource
def load_excel_processor():
    """
    Load Excel Processor để xử lý Map_Complete.xlsx
    Tự động detect local vs cloud
    """
    processor = get_excel_processor(
        local_file_path=LOCAL_MAP_PATH,
        gdrive_file_id=MAP_FILE_ID,
        file_name="Map_Complete.xlsx"
    )
    return processor

# ========== INITIALIZE DATA ==========
# Load data globally
try:
    # Load parquet data (market, industry, ticker, map)
    market_df, industry_df, ticker_df, map_df = load_data()
    
    # Load Excel processor (nếu cần xử lý Map_Complete.xlsx)
    # Uncomment dòng dưới nếu bạn cần dùng processor
    # processor = load_excel_processor()
    
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
    ❌ **Lỗi khi load dữ liệu!**
    
    **Nếu đang chạy LOCAL:**
    - Vui lòng đảm bảo các file dữ liệu tồn tại ở ổ D:
    - Hoặc đã cài đặt Google Drive credentials (xem Bước 6)
    
    **Nếu đang deploy lên Cloud:**
    - Đảm bảo đã setup Streamlit Secrets (xem Bước 6)
    - Đã thay thế đúng FILE IDs ở dòng 24-25
    
    Chi tiết lỗi: {str(e)}
    """)
    st.stop()

# ========== SIDEBAR ==========
with st.sidebar:
    st.title(config.APP_ICON + " Dashboard CK")
    st.markdown("---")
    
    # Navigation
    st.markdown("### 📌 Điều hướng")
    st.markdown("""
    - 🏛️ Tổng Quan Thị Trường
    - 🏭 Phân Tích Ngành
    - 📊 Phân Tích Cổ Phiếu
    - ⚖️ So Sánh & Đối Chiếu
    - 🔍 Sàng Lọc & Tìm Kiếm
    - ⭐ Danh Mục Theo Dõi             
    """)
    
    st.markdown("---")
    
    # Data info
    st.markdown("### 📈 Thông tin dữ liệu")
    st.info(f"""
    **Thị trường**: {len(market_df)} quý  
    **Ngành**: {industry_df['SYMBOL'].nunique()} ngành  
    **Cổ phiếu**: {ticker_df['SYMBOL'].nunique()} mã
    """)
    
    # Latest quarter
    latest_quarter = market_df.iloc[-1]['QUARTER']
    latest_year = market_df.iloc[-1]['YEAR']
    st.success(f"📅 Quý mới nhất: **{latest_quarter} {latest_year}**")
    
    st.markdown("---")
    st.caption("Dashboard v1.0 | BSC Research")

# ========== MAIN PAGE ==========
st.title("📊 Dashboard Phân Tích Chứng Khoán Việt Nam")

st.markdown("""
### Chào mừng đến với Dashboard Phân Tích Chứng Khoán! 👋

Dashboard này cung cấp công cụ phân tích toàn diện cho đầu tư chứng khoán với:

#### 🎯 Các tính năng chính:

1. **🏛️ Tổng Quan Thị Trường**
   - Theo dõi xu hướng thị trường theo thời gian
   - Phân tích các chỉ số vĩ mô (P/E, P/B, ROE, etc.)
   - Đánh giá sức khỏe tổng thể thị trường

2. **🏭 Phân Tích Ngành**
   - So sánh hiệu suất giữa các ngành
   - Xếp hạng ngành theo các tiêu chí
   - Phát hiện xu hướng chuyển dịch vốn

3. **📊 Phân Tích Cổ Phiếu**
   - Phân tích sâu từng mã cổ phiếu
   - Đánh giá định giá, sinh lời, dòng tiền
   - Phân tích rủi ro với Z-Score

4. **⚖️ So Sánh & Đối Chiếu**
   - So sánh nhiều cổ phiếu cùng lúc
   - Ma trận tương quan
   - Scoring và xếp hạng tổng hợp

5. **🔍 Sàng Lọc & Tìm Kiếm**
   - Tìm cơ hội đầu tư với bộ lọc đa tiêu chí
   - Các chiến lược lọc có sẵn
   - Export kết quả

6. **⭐ Danh Mục Theo Dõi**
   - Quản lý watchlist cá nhân
   - Theo dõi thay đổi
   - Phân tích danh mục

---

### 🚀 Hướng dẫn sử dụng:

1. **Chọn trang** từ thanh điều hướng bên trái
2. **Tùy chỉnh bộ lọc** theo nhu cầu phân tích
3. **Tương tác với biểu đồ**: zoom, pan, hover để xem chi tiết
4. **Export dữ liệu** khi cần thiết

---

### 📊 Thống kê dữ liệu:
""")

# Display data statistics
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Số quý dữ liệu",
        len(market_df),
        help="Tổng số quý có dữ liệu thị trường"
    )

with col2:
    st.metric(
        "Số ngành",
        industry_df['SYMBOL'].nunique(),
        help="Tổng số ngành được phân tích"
    )

with col3:
    st.metric(
        "Số mã CK",
        ticker_df['SYMBOL'].nunique(),
        help="Tổng số mã cổ phiếu có dữ liệu"
    )

st.markdown("---")

# Quick stats
st.markdown("### 📈 Thống kê nhanh (Quý gần nhất)")

latest_market = market_df.iloc[-1]

col1, col2, col3, col4 = st.columns(4)

with col1:
    from utils.formatters import format_billion 
    from utils.formatters import format_change
    st.metric(
        "Vốn hóa TT",
        format_billion(latest_market.get('MARKET_CAP_EOQ', 0)),
        format_change(latest_market.get('MARKET_CAP_EOQ_GYOY', 0)) if 'MARKET_CAP_EOQ_GYOY' in latest_market else None
    )

with col2:
    from utils.formatters import format_ratio
    st.metric(
        "P/E Trung bình",
        format_ratio(latest_market.get('PE_EOQ', 0)),
        help="Price-to-Earnings ratio trung bình thị trường"
    )

with col3:
    from utils.formatters import format_percent
    st.metric(
        "ROE Trung bình",
        format_percent(latest_market.get('ROAE', 0)),
        help="Return on Equity trung bình thị trường"
    )

with col4:
    st.metric(
        "P/B Trung bình",
        format_ratio(latest_market.get('PB_EOQ', 0)),
        help="Price-to-Book ratio trung bình thị trường"
    )

st.markdown("---")

st.info("""
💡 **Mẹo sử dụng:**
- Sử dụng thanh bên trái để điều hướng giữa các trang
- Mỗi trang có bộ lọc riêng để tùy chỉnh phân tích
- Biểu đồ có thể zoom, pan và tải xuống
- Bảng dữ liệu có thể sắp xếp và export
""")

st.markdown("---")
st.caption("© 2024 BSC Research | Dashboard v1.0")


# ========== EXAMPLE: SỬ DỤNG EXCEL PROCESSOR (NẾU CẦN) ==========
# Uncomment phần này nếu bạn cần xử lý Map_Complete.xlsx
"""
# Load processor
processor = load_excel_processor()

# Ví dụ: Tạo nested dict từ Excel
result = processor.to_nested_dict(
    sheet_name=['company_map', 'bank_map'],
    key_hierarchy=['CAL_GROUP', 'COL'],
    value_columns='RULE'
)

# Hoặc dùng advanced features
result_advanced = processor.to_nested_dict_advanced(
    sheet_name=['company_map'],
    key_hierarchy=['CAL_GROUP', 'COL'],
    value_columns='ALGO',
    filters={'LEVEL': {'<=': 1}},
    drop_duplicates=True
)

# Sử dụng kết quả
st.write(result)
"""