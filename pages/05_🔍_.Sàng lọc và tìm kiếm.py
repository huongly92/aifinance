"""Trang Sàng Lọc & Tìm Kiếm"""
import streamlit as st
import sys
from pathlib import Path
ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

import config
from utils.metrics import screen_stocks

st.set_page_config(page_title="Sàng Lọc", page_icon="🔍", layout="wide")
st.title("🔍 Sàng Lọc & Tìm Kiếm")

if "ticker_df" not in st.session_state:
    st.error("Vui lòng quay lại trang chủ!")
    st.stop()

ticker_df = st.session_state.ticker_df

# Get latest data
latest_year = ticker_df["YEAR"].max()
latest_quarter = ticker_df[ticker_df["YEAR"] == latest_year]["QUARTER"].max()
latest = ticker_df[(ticker_df["YEAR"] == latest_year) & (ticker_df["QUARTER"] == latest_quarter)]

# Sidebar filters
st.sidebar.header("⚙️ Tiêu Chí Lọc")

# Preset strategies
preset = st.sidebar.selectbox("Chiến lược có sẵn", ["Custom", "Value Investing", "Growth Investing", "Dividend Stocks", "Quality Stocks"])

criteria = {}

if preset != "Custom" and preset in config.SCREENING_PRESETS:
    criteria = config.SCREENING_PRESETS[preset]
    st.sidebar.success(f"Đã áp dụng chiến lược: {preset}")
else:
    st.sidebar.subheader("Định giá")
    if "PE_EOQ" in latest.columns:
        pe_range = st.sidebar.slider("P/E", 0.0, 50.0, (0.0, 20.0))
        criteria["PE_EOQ"] = pe_range
    
    if "PB_EOQ" in latest.columns:
        pb_range = st.sidebar.slider("P/B", 0.0, 10.0, (0.0, 3.0))
        criteria["PB_EOQ"] = pb_range
    
    st.sidebar.subheader("Sinh lời")
    if "ROAE" in latest.columns:
        roe_range = st.sidebar.slider("ROE (%)", 0.0, 100.0, (10.0, 100.0))
        criteria["ROAE"] = roe_range

# Screen
st.header("📊 Kết Quả Lọc")

if criteria:
    result = screen_stocks(latest, criteria)
    
    st.info(f"Tìm thấy **{len(result)}** cổ phiếu thỏa mãn tiêu chí")
    
    if len(result) > 0:
        display_cols = ["SYMBOL", "CLOSE_PRICE", "MARKET_CAP_EOQ", "PE_EOQ", "PB_EOQ", "ROAE", "ROAA"]
        display_cols = [c for c in display_cols if c in result.columns]
        
        st.dataframe(result[display_cols], use_container_width=True, hide_index=True)
        
        # Export
        csv = result[display_cols].to_csv(index=False).encode("utf-8")
        st.download_button("📥 Tải xuống kết quả", csv, f"screening_{preset}.csv", "text/csv")
    else:
        st.warning("Không tìm thấy cổ phiếu nào!")
else:
    st.info("Chọn tiêu chí lọc từ sidebar")
