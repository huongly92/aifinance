"""Trang So Sánh & Đối Chiếu"""
import streamlit as st
import sys
from pathlib import Path
ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

import config
from components.charts import *
from components.tables import *

st.set_page_config(page_title="So Sánh", page_icon="⚖️", layout="wide")
st.title("⚖️ So Sánh & Đối Chiếu")

if "ticker_df" not in st.session_state:
    st.error("Vui lòng quay lại trang chủ!")
    st.stop()

ticker_df = st.session_state.ticker_df

# Get latest data
latest_year = ticker_df["YEAR"].max()
latest_quarter = ticker_df[ticker_df["YEAR"] == latest_year]["QUARTER"].max()
latest = ticker_df[(ticker_df["YEAR"] == latest_year) & (ticker_df["QUARTER"] == latest_quarter)]

# Ticker selector
st.sidebar.header("⚙️ Chọn Cổ Phiếu So Sánh")
tickers = sorted(ticker_df["SYMBOL"].unique())
selected = st.sidebar.multiselect("Chọn 2-10 mã", tickers, default=tickers[:3] if len(tickers) >= 3 else tickers, max_selections=10)

if len(selected) >= 2:
    compare_data = latest[latest["SYMBOL"].isin(selected)]
    
    # Comparison table
    st.header("📊 Bảng So Sánh")
    
    compare_cols = ["SYMBOL", "CLOSE_PRICE", "MARKET_CAP_EOQ", "PE_EOQ", "PB_EOQ", "ROAE", "ROAA", "EPS_12M", "BVPS"]
    compare_cols = [c for c in compare_cols if c in compare_data.columns]
    
    st.dataframe(compare_data[compare_cols], use_container_width=True, hide_index=True)
    
    # Charts
    st.header("📈 Biểu Đồ So Sánh")
    
    tab1, tab2, tab3 = st.tabs(["Định giá", "Sinh lời", "Scatter"])
    
    with tab1:
        if all(c in compare_data.columns for c in ["SYMBOL", "PE_EOQ", "PB_EOQ"]):
            fig = create_grouped_bar_chart(compare_data, "SYMBOL", ["PE_EOQ", "PB_EOQ"], "P/E và P/B")
            st.plotly_chart(fig, use_container_width=True, config=config.PLOTLY_CONFIG)
    
    with tab2:
        if all(c in compare_data.columns for c in ["SYMBOL", "ROAE", "ROAA"]):
            fig = create_grouped_bar_chart(compare_data, "SYMBOL", ["ROAE", "ROAA"], "ROE và ROA")
            st.plotly_chart(fig, use_container_width=True, config=config.PLOTLY_CONFIG)
    
    with tab3:
        if all(c in compare_data.columns for c in ["PE_EOQ", "ROAE", "SYMBOL"]):
            fig = create_scatter_chart(compare_data, "PE_EOQ", "ROAE", "P/E vs ROE", text_col="SYMBOL")
            st.plotly_chart(fig, use_container_width=True, config=config.PLOTLY_CONFIG)

elif len(selected) == 1:
    st.warning("Vui lòng chọn ít nhất 2 mã để so sánh")
else:
    st.info("Chọn các mã cổ phiếu từ sidebar để bắt đầu so sánh")
