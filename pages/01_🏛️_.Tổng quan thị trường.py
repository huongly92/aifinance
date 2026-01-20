"""Trang Tổng Quan Thị Trường"""
import streamlit as st
import sys
from pathlib import Path
ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

import config
from components.charts import *
from components.kpi_cards import *
from components.filters import *
from utils.formatters import *

st.set_page_config(page_title="Tổng Quan Thị Trường", page_icon="🏛️", layout="wide")
st.title("🏛️ Tổng Quan Thị Trường")

if "market_df" not in st.session_state:
    st.error("Vui lòng quay lại trang chủ để load dữ liệu!")
    st.stop()

market_df = st.session_state.market_df
market_df["QUARTER"] =  market_df["QUARTER"]

# Filters
st.sidebar.header("⚙️ Bộ lọc")
quarters = sorted(market_df["QUARTER"].unique())
start, end = date_range_filter(quarters, "market")

filtered = market_df[(market_df["QUARTER"] >= start) & (market_df["QUARTER"] <= end)]

if len(filtered) > 0:
    latest = filtered.iloc[-1]
    
    # KPIs
    st.header("📊 Chỉ Số Chính")
    kpis = [
        {"label": "Vốn hóa TT", "value": latest.get("MARKET_CAP_EOQ"), "delta": latest.get("MARKET_CAP_EOQ_GYOY"), "format_type": "billion"},
        {"label": "P/E TB", "value": latest.get("PE_EOQ"), "format_type": "ratio"},
        {"label": "P/B TB", "value": latest.get("PB_EOQ"), "format_type": "ratio"},
        {"label": "ROE TB (%)", "value": latest.get("ROAE"), "format_type": "percent"},
    ]
    display_kpi_row(kpis)
    
    # Charts
    st.header("📈 Xu Hướng")
    
    tab1, tab2, tab3 = st.tabs(["Vốn hóa", "Định giá", "Sinh lời"])
    
    with tab1:
        fig = create_line_chart(filtered, "QUARTER", "MARKET_CAP_EOQ", "Vốn hóa thị trường")
        st.plotly_chart(fig, use_container_width=True, config=config.PLOTLY_CONFIG)
    
    with tab2:
        fig = create_line_chart(filtered, "QUARTER", ["PE_EOQ"], "P/E")
        st.plotly_chart(fig, use_container_width=True, config=config.PLOTLY_CONFIG)
        fig = create_line_chart(filtered, "QUARTER", ["PB_EOQ"], "P/B")
        st.plotly_chart(fig, use_container_width=True, config=config.PLOTLY_CONFIG)
    
    with tab3:
        fig = create_line_chart(filtered, "QUARTER", ["ROAE", "ROAA"], "ROE và ROA")
        st.plotly_chart(fig, use_container_width=True, config=config.PLOTLY_CONFIG)
    
    # Top/Bottom performers
    st.header("🏆 Top/Bottom Thị Trường")
    
    create_heatmap(
        df=filtered,       
        title="Biểu đồ nhiệt ROE theo ticker")


    # Data table
    st.header("📋 Dữ Liệu")
    cols = ["QUARTER", "MARKET_CAP_EOQ", "PE_EOQ", "PB_EOQ", "ROAE"]
    cols = [c for c in cols if c in filtered.columns]
    st.dataframe(filtered[cols], use_container_width=True, hide_index=True)
