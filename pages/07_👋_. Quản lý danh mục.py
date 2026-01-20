"""Trang Danh Mục Theo Dõi"""
import streamlit as st
import sys
from pathlib import Path
ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

import config

st.set_page_config(page_title="Danh Mục", page_icon="⭐", layout="wide")
st.title("⭐ Danh Mục Theo Dõi")

if "ticker_df" not in st.session_state:
    st.error("Vui lòng quay lại trang chủ!")
    st.stop()

ticker_df = st.session_state.ticker_df

# Get latest data
latest_year = ticker_df["YEAR"].max()
latest_quarter = ticker_df[ticker_df["YEAR"] == latest_year]["QUARTER"].max()
latest = ticker_df[(ticker_df["YEAR"] == latest_year) & (ticker_df["QUARTER"] == latest_quarter)]

# Initialize watchlist in session state
if "watchlist" not in st.session_state:
    st.session_state.watchlist = []

# Sidebar - Add tickers
st.sidebar.header("➕ Thêm Cổ Phiếu")
tickers = sorted(ticker_df["SYMBOL"].unique())
selected = st.sidebar.selectbox("Chọn mã", [""] + tickers)

if selected and selected not in st.session_state.watchlist:
    if st.sidebar.button("Thêm vào danh mục"):
        st.session_state.watchlist.append(selected)
        st.sidebar.success(f"Đã thêm {selected}")

# Display watchlist
st.header("📋 Danh Mục Của Tôi")

if st.session_state.watchlist:
    watchlist_data = latest[latest["SYMBOL"].isin(st.session_state.watchlist)]
    
    display_cols = ["SYMBOL", "CLOSE_PRICE", "MARKET_CAP_EOQ", "PE_EOQ", "PB_EOQ", "ROAE", "ROAA", "DIVIDEND_YIELD_EOQ"]
    display_cols = [c for c in display_cols if c in watchlist_data.columns]
    
    st.dataframe(watchlist_data[display_cols], use_container_width=True, hide_index=True)
    
    # Remove tickers
    st.subheader("🗑️ Quản Lý")
    to_remove = st.multiselect("Chọn mã để xóa", st.session_state.watchlist)
    if to_remove and st.button("Xóa khỏi danh mục"):
        for ticker in to_remove:
            st.session_state.watchlist.remove(ticker)
        st.success("Đã xóa!")
        st.rerun()
    
    # Clear all
    if st.button("Xóa toàn bộ danh mục"):
        st.session_state.watchlist = []
        st.success("Đã xóa toàn bộ!")
        st.rerun()
else:
    st.info("Danh mục trống. Thêm cổ phiếu từ sidebar.")
