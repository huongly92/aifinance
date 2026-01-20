"""Trang Phân Tích Ngành"""
import streamlit as st
import sys
from pathlib import Path
ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

import config
from components.charts import *
from components.tables import *
from utils.formatters import *
import pandas as pd

st.set_page_config(page_title="Phân Tích Ngành", page_icon="🏭", layout="wide")
st.title("🏭 Phân Tích Ngành")

if "industry_df" not in st.session_state:
    st.error("Vui lòng quay lại trang chủ!")
    st.stop()

industry_df = st.session_state.industry_df
ticker_df = st.session_state.ticker_df
# Get latest data
latest_year = industry_df["YEAR"].max()
latest_quarter = industry_df[industry_df["YEAR"] == latest_year]["QUARTER"].max()
latest = industry_df[(industry_df["YEAR"] == latest_year) & (industry_df["QUARTER"] == latest_quarter)]

# Filters
st.sidebar.header("⚙️ Bộ lọc")
industries = sorted(industry_df["SYMBOL"].unique())
selected = st.sidebar.multiselect("Chọn ngành", industries, default=industries[:5] if len(industries) >= 5 else industries)

if selected:
    filtered = latest[latest["SYMBOL"].isin(selected)]
    # Phân phối ngành
    st.header("📊 Phân Phối Ngành")

    # ========== BỘ LỌC & TÙY CHỈNH ==========
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        # Chọn quý
        quarters = sorted(ticker_df['QUARTER'].dropna().unique())
        selected_quarter = st.selectbox("Quý:", quarters,index=quarters.index(latest_quarter))

    with col2:
        # Chọn cột phân tích
        numeric_columns = ['PE_EOQ', 'PB_EOQ', 'ROAE', 'ROAA', 'NPATMI_12M_GYOY']
        selected_column = st.selectbox("Chỉ số:", numeric_columns)

    with col3:
        # Giá trị min
        min_value = st.number_input("Min:", value=0.0)

    with col4:
        # Giá trị max
        max_value = st.number_input("Max:", value=50.0)

    # ========== LỌC DỮ LIỆU ==========
    filtered_df = ticker_df[ticker_df['QUARTER'] == selected_quarter]

    # ========== VẼ BIỂU ĐỒ ==========
    fig = plot_distribution_by_industry(
        filtered_df,
        y_column=selected_column,  # ← Dùng giá trị đã chọn
        title=f'Phân phối {selected_column} theo ngành',
        y_label=selected_column,
        x_column='LEVEL2_NAME_EN',
        x_label='Ngành',
        filter_outliers=True,
        min_value=min_value,
        max_value=max_value, 
        multiply_by=1,
        height=600,
        theme='plotly_white',
        show_chart=True
    )
    # Summary table
    st.header("📊 So Sánh Ngành")
    
    compare_cols = ["SYMBOL", "MARKET_CAP_EOQ", "PE_EOQ", "PE_HT", "PB_EOQ" , "PB_HT" , "ROAE", "ROAA"]
    compare_cols = [c for c in compare_cols if c in filtered.columns]
    
    display_df = filtered[compare_cols].copy()
    st.dataframe(display_df, use_container_width=True, hide_index=True)
    
    # Charts
    st.header("📈 Biểu Đồ So Sánh")
    
    tab1, tab2, tab3 = st.tabs(["Sinh lời", "Định giá", "Vốn hóa"])
    
    with tab1:
        if all(c in filtered.columns for c in ["SYMBOL", "ROAE", "ROAA"]):
            fig = create_grouped_bar_chart(filtered, "SYMBOL", ["ROAE", "ROAA"], "ROE và ROA theo ngành")
            st.plotly_chart(fig, use_container_width=True, config=config.PLOTLY_CONFIG)
    
    with tab2:
        if all(c in filtered.columns for c in ["SYMBOL", "PE_EOQ"]):
            fig = create_bar_chart(filtered, "SYMBOL", "PE_EOQ", "P/E theo ngành")
            st.plotly_chart(fig, use_container_width=True, config=config.PLOTLY_CONFIG)
    
    with tab3:
        if all(c in filtered.columns for c in ["SYMBOL", "MARKET_CAP_EOQ"]):
            fig = create_bar_chart(filtered, "SYMBOL", "MARKET_CAP_EOQ", "Vốn hóa theo ngành")
            st.plotly_chart(fig, use_container_width=True, config=config.PLOTLY_CONFIG)
    
    # Top performers
    st.header("⭐ Top Performers")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Top 5 ROE cao nhất")
        if "ROAE" in filtered.columns:
            top_roe = filtered.nlargest(5, "ROAE")[["SYMBOL", "ROAE"]]
            st.dataframe(top_roe, use_container_width=True, hide_index=True)
    
    with col2:
        st.subheader("Top 5 P/E thấp nhất")
        if "PE_EOQ" in filtered.columns:
            top_pe = filtered[filtered["PE_EOQ"] > 0].nsmallest(5, "PE_EOQ")[["SYMBOL", "PE_EOQ"]]
            st.dataframe(top_pe, use_container_width=True, hide_index=True)
