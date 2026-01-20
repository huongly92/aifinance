"""
MINIMAL TEST APP - Debug deployment
"""

import streamlit as st
import pandas as pd
import sys

st.set_page_config(
    page_title="Debug Test",
    page_icon="🔍",
    layout="wide"
)

st.title("🔍 Debug Test App")

# Test 1: Basic Streamlit
st.success("✅ Streamlit đang hoạt động!")

# Test 2: Check Python version
st.info(f"🐍 Python version: {sys.version}")

# Test 3: Check Streamlit Secrets
st.markdown("### 🔐 Kiểm tra Secrets")
try:
    if hasattr(st, 'secrets'):
        if 'gcp_service_account' in st.secrets:
            st.success("✅ Đã tìm thấy gcp_service_account trong secrets")
            st.write("Keys:", list(st.secrets['gcp_service_account'].keys()))
        else:
            st.error("❌ KHÔNG tìm thấy 'gcp_service_account' trong secrets")
            st.write("Available secrets:", list(st.secrets.keys()) if st.secrets else "None")
    else:
        st.warning("⚠️ Không có st.secrets (đang chạy local)")
except Exception as e:
    st.error(f"❌ Lỗi khi check secrets: {e}")

# Test 4: Import data_loader
st.markdown("### 📦 Kiểm tra imports")
try:
    # Import from uploaded files
    sys.path.insert(0, '/mnt/user-data/uploads')
    from data_loader import is_running_on_cloud
    
    st.success("✅ Import data_loader thành công!")
    
    # Check environment
    is_cloud = is_running_on_cloud()
    if is_cloud:
        st.info("🌐 Đang chạy trên CLOUD")
    else:
        st.info("💻 Đang chạy LOCAL")
        
except Exception as e:
    st.error(f"❌ Lỗi import data_loader: {e}")
    import traceback
    st.code(traceback.format_exc())

# Test 5: Try loading data
st.markdown("### 📊 Kiểm tra load data")
try:
    from data_loader import load_all_data
    
    with st.spinner('Đang load data...'):
        market_df, industry_df, ticker_df, map_df = load_all_data()
    
    st.success("✅ Load data thành công!")
    
    # Show stats
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Market rows", len(market_df))
    with col2:
        st.metric("Industry rows", len(industry_df))
    with col3:
        st.metric("Ticker rows", len(ticker_df))
    with col4:
        st.metric("Map rows", len(map_df))
    
    # Show sample
    st.markdown("#### Market data sample:")
    st.dataframe(market_df.head())
    
except Exception as e:
    st.error(f"❌ Lỗi khi load data: {e}")
    import traceback
    st.code(traceback.format_exc())

st.markdown("---")
st.caption("Debug Test v1.0")
