"""Trang Phân Tích Cổ Phiếu"""
import streamlit as st
import sys
from pathlib import Path
ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

import config
from components.charts import *
from components.kpi_cards import *
from utils.formatters import *
from utils.metrics import *

st.set_page_config(page_title="Phân Tích Cổ Phiếu", page_icon="📊", layout="wide")
st.title("📊 Phân Tích Cổ Phiếu Chi Tiết")

if "ticker_df" not in st.session_state:
    st.error("Vui lòng quay lại trang chủ!")
    st.stop()

ticker_df = st.session_state.ticker_df

# Ticker selector
st.sidebar.header("⚙️ Chọn Cổ Phiếu")
tickers = sorted(ticker_df["SYMBOL"].unique())
selected_ticker = st.sidebar.selectbox("Mã cổ phiếu", tickers)

if selected_ticker:
    ticker_data = ticker_df[ticker_df["SYMBOL"] == selected_ticker].sort_values(["YEAR", "QUARTER"])
    ticker_data["QUARTER_KEY"] = ticker_data["YEAR"].astype(str) + ticker_data["QUARTER"]
    
    if len(ticker_data) > 0:
        latest = ticker_data.iloc[-1]
        
        # Header
        st.header(f"📈 {selected_ticker}")
        
        industry = latest.get("LEVEL2_NAME_EN", "N/A")
        st.info(f"**Ngành:** {industry} | **Quý gần nhất:** {latest.get('QUARTER')} {latest.get('YEAR')}")
        
        # KPIs
        st.subheader("💎 Chỉ Số Chính")
        kpis = [
            {"label": "Giá", "value": latest.get("CLOSE_PRICE"), "delta": latest.get("CLOSE_PRICE_GYOY"), "format_type": "price"},
            {"label": "Vốn hóa", "value": latest.get("MARKET_CAP_EOQ"), "format_type": "billion"},
            {"label": "P/E", "value": latest.get("PE_EOQ"), "format_type": "ratio"},
            {"label": "P/B", "value": latest.get("PB_EOQ"), "format_type": "ratio"},
        ]
        display_kpi_row(kpis)
        
        kpis2 = [
            {"label": "ROE (%)", "value": latest.get("ROAE"), "format_type": "percent"},
            {"label": "ROA (%)", "value": latest.get("ROAA"), "format_type": "percent"},
            {"label": "EPS", "value": latest.get("EPS_12M"), "format_type": "number"},
            {"label": "BVPS", "value": latest.get("BVPS"), "format_type": "number"},
        ]
        display_kpi_row(kpis2)
        
        # Charts
        st.header("📈 Phân Tích")
        
        tab1, tab2, tab3, tab4 = st.tabs(["Định giá", "Sinh lời", "Dòng tiền", "Rủi ro"])
        
        with tab1:
            st.subheader("Lịch sử định giá")
            if "PE_EOQ" in ticker_data.columns:
                fig = create_line_chart(ticker_data, "QUARTER_KEY", ["PE_EOQ", "PB_EOQ"], "P/E và P/B theo thời gian")
                st.plotly_chart(fig, use_container_width=True, config=config.PLOTLY_CONFIG)
        
        with tab2:
            st.subheader("Chỉ số sinh lời")
            if all(c in ticker_data.columns for c in ["ROAE", "ROAA"]):
                fig = create_line_chart(ticker_data, "QUARTER_KEY", ["ROAE", "ROAA", "ROIC"], "ROE, ROA, ROIC")
                st.plotly_chart(fig, use_container_width=True, config=config.PLOTLY_CONFIG)
            
            if all(c in ticker_data.columns for c in ["GROSS_MARGIN_12M", "OPERATING_MARGIN_12M", "NET_INCOME_MARGIN_12M"]):
                fig = create_line_chart(ticker_data, "QUARTER_KEY", ["GROSS_MARGIN_12M", "OPERATING_MARGIN_12M", "NET_INCOME_MARGIN_12M"], "Biên lợi nhuận")
                st.plotly_chart(fig, use_container_width=True, config=config.PLOTLY_CONFIG)
        
        with tab3:
            st.subheader("Dòng tiền")
            if "CFO_12M" in ticker_data.columns:
                fig = create_line_chart(ticker_data, "QUARTER_KEY", ["CFO_12M", "FCF_12M"], "CFO và FCF")
                st.plotly_chart(fig, use_container_width=True, config=config.PLOTLY_CONFIG)
        
        with tab4:
            st.subheader("Đánh giá rủi ro")
            
            z_score = latest.get("Z_SCORE")
            if z_score:
                category, description, color = interpret_z_score(z_score)
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Z-Score", format_number(z_score))
                with col2:
                    st.metric("Phân loại", category)
                with col3:
                    st.metric("Đánh giá", description)
                
                if "Z_SCORE" in ticker_data.columns:
                    fig = create_line_chart(ticker_data, "QUARTER_KEY", "Z_SCORE", "Lịch sử Z-Score")
                    st.plotly_chart(fig, use_container_width=True, config=config.PLOTLY_CONFIG)
        
        # Data table
        st.header("📋 Dữ Liệu Chi Tiết")
        cols = ["QUARTER_KEY", "CLOSE_PRICE", "MARKET_CAP_EOQ", "PE_EOQ", "PB_EOQ", "ROAE", "EPS_12M"]
        cols = [c for c in cols if c in ticker_data.columns]
        st.dataframe(ticker_data[cols], use_container_width=True, hide_index=True)
