"""
📊 Báo cáo Tài chính - Clean & Optimized Version

Đặt file này vào: pages/08_📊_Báo_cáo_Tài_chính.py
"""

import streamlit as st
import sys
import pandas as pd
from pathlib import Path

# ============================================
# SETUP
# ============================================

ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

try:
    from components.financial_report_display import (
        display_financial_report,
        FINANCIAL_METRICS,
        detect_cal_group,
        get_available_metrics,
        get_metrics_for_report_type,
        create_export_buttons,
        prepare_financial_data,
        get_streamlit_css
    )
    # from components.financial_report_style_config import get_streamlit_css
except ImportError as e:
    st.error(f'⚠️ Lỗi import module: {str(e)}')
    st.info('Vui lòng đảm bảo các file sau nằm trong folder components/')
    st.info('- financial_report_display.py')
    st.info('- financial_report_style_config.py')
    st.stop()

# ============================================
# PAGE CONFIG
# ============================================

st.set_page_config(
    page_title='Báo cáo Tài chính',
    page_icon='📊',
    layout='wide',
    initial_sidebar_state='expanded'
)

# Apply CSS from config
st.markdown(get_streamlit_css(), unsafe_allow_html=True)

# ============================================
# DATA CHECK
# ============================================

if "industry_df" not in st.session_state:
    st.error("❌ Vui lòng quay lại trang chủ để load dữ liệu!")
    st.stop()

industry_df = st.session_state.industry_df
ticker_df = st.session_state.ticker_df
market_df = st.session_state.market_df

# Initialize session state
if 'data_type' not in st.session_state:
    st.session_state.data_type = 'Cổ phiếu'

# ============================================
# HEADER
# ============================================

col1, col2 = st.columns([4, 1])

with col1:
    st.title('📊 Báo cáo Tài chính')
    st.caption('🎯 Phân tích báo cáo tài chính chuyên nghiệp')

with col2:
    if st.button('🔄 Làm mới', use_container_width=True, type='primary'):
        st.rerun()

st.divider()

# ============================================
# SIDEBAR
# ============================================

with st.sidebar:
    st.header('⚙️ Cấu hình')
    
    # Chọn loại dữ liệu
    data_type = st.radio(
        '📁 Loại dữ liệu',
        ['Thị trường', 'Ngành', 'Cổ phiếu'],
        index=['Thị trường', 'Ngành', 'Cổ phiếu'].index(st.session_state.data_type),
        horizontal=True
    )
    st.session_state.data_type = data_type
    
    # Chọn dataframe
    if data_type == 'Thị trường':
        df = market_df
        data_label = 'Thị trường'
        icon = '🌐'
    elif data_type == 'Ngành':
        df = industry_df
        data_label = 'Ngành'
        icon = '🏭'
    else:
        df = ticker_df
        data_label = 'Cổ phiếu'
        icon = '📈'
    
    st.success(f'{icon} {len(df):,} dòng dữ liệu')
    
    st.divider()
    
    # Chọn mã
    st.subheader('🎯 Chọn mã')
    
    symbols = sorted(df['SYMBOL'].unique().tolist())
    
    if data_type == 'Thị trường':
        selected_symbol = symbols[0] if symbols else 'MARKET'
        st.info(f'**{selected_symbol}**')
    else:
        # Search
        search = st.text_input(
            '🔍 Tìm kiếm',
            placeholder='Nhập mã...',
            label_visibility='collapsed'
        )
        
        if search:
            symbols = [s for s in symbols if search.upper() in s.upper()]
        
        if symbols:
            selected_symbol = st.selectbox(
                'Mã',
                symbols,
                label_visibility='collapsed'
            )
        else:
            st.error('Không tìm thấy')
            selected_symbol = None
    
    st.divider()
    
    # Tùy chọn hiển thị
    st.subheader('📊 Tùy chọn')
    
    show_all = st.toggle('Hiển thị tất cả chỉ số', value=True)
    
    selected_metrics = None
    if not show_all and selected_symbol:
        current_report_type = st.session_state.get('report_type', 'IS')
        cal_group = detect_cal_group(df, selected_symbol)
        metrics_info = get_metrics_for_report_type(cal_group, current_report_type)
        
        available_codes = [m for m in metrics_info.keys() if m in df.columns]
        
        if available_codes:
            options = {code: metrics_info[code]['name'] for code in available_codes}
            selected_names = st.multiselect(
                'Chọn chỉ số',
                list(options.values()),
                label_visibility='collapsed'
            )
            
            if selected_names:
                reverse_map = {v: k for k, v in options.items()}
                selected_metrics = [reverse_map[n] for n in selected_names]

# ============================================
# MAIN CONTENT
# ============================================

if not selected_symbol:
    st.warning('⚠️ Vui lòng chọn mã')
    st.stop()

# Metrics summary
cal_group = detect_cal_group(df, selected_symbol)
num_quarters = len(df[df['SYMBOL'] == selected_symbol])

cal_group_names = {
    'company': '🏢 Công ty',
    'bank': '🏦 Ngân hàng', 
    'security': '📈 Chứng khoán',
    'insurance': '🛡️ Bảo hiểm'
}

col1, col2, col3, col4 = st.columns(4)
col1.metric('🏷️ Loại', data_label)
col2.metric('📋 Mã', selected_symbol)
col3.metric('📅 Số quý', f'{num_quarters}')
col4.metric('🏢 Nhóm', cal_group_names.get(cal_group, cal_group))

if num_quarters == 0:
    st.error('❌ Không có dữ liệu')
    st.stop()

st.divider()

# ============================================
# TABS
# ============================================

tab1, tab2, tab3, tab4 = st.tabs([
    '📈 Kết quả Kinh doanh',
    '💰 Cân đối Kế toán',
    '💵 Lưu chuyển Tiền tệ',
    '📊 Chỉ số Phân tích'
])

with tab1:
    st.session_state.report_type = 'IS'
    try:
        display_financial_report(df, selected_symbol, 'IS', selected_metrics)

        # Thêm nút export
        st.markdown('---')
        st.subheader('📥 Export dữ liệu')
        df_export, _, _ = prepare_financial_data(df, selected_symbol, 'IS', selected_metrics)
        if not df_export.empty:
            create_export_buttons(df_export, selected_symbol, 'IS')
    except Exception as e:
        st.error(f'❌ Lỗi: {str(e)}')

with tab2:
    st.session_state.report_type = 'BS'
    try:
        display_financial_report(df, selected_symbol, 'BS', selected_metrics)

        # Thêm nút export
        st.markdown('---')
        st.subheader('📥 Export dữ liệu')
        df_export, _, _ = prepare_financial_data(df, selected_symbol, 'BS', selected_metrics)
        if not df_export.empty:
            create_export_buttons(df_export, selected_symbol, 'BS')
    except Exception as e:
        st.error(f'❌ Lỗi: {str(e)}')

with tab3:
    st.session_state.report_type = 'CF'
    try:
        display_financial_report(df, selected_symbol, 'CF', selected_metrics)

        # Thêm nút export
        st.markdown('---')
        st.subheader('📥 Export dữ liệu')
        df_export, _, _ = prepare_financial_data(df, selected_symbol, 'CF', selected_metrics)
        if not df_export.empty:
            create_export_buttons(df_export, selected_symbol, 'CF')
    except Exception as e:
        st.error(f'❌ Lỗi: {str(e)}')

with tab4:
    st.session_state.report_type = 'ratio'
    try:
        display_financial_report(df, selected_symbol, 'ratio', selected_metrics)
        
        # Thêm nút export
        st.markdown('---')
        st.subheader('📥 Export dữ liệu')
        df_export, _, _ = prepare_financial_data(df, selected_symbol, 'ratio', selected_metrics)
        if not df_export.empty:
            create_export_buttons(df_export, selected_symbol, 'ratio')
    except Exception as e:
        st.error(f'❌ Lỗi: {str(e)}')

# ============================================
# FOOTER - QUICK INSIGHTS
# ============================================

st.divider()

with st.expander('💡 Thông tin & Phân tích nhanh'):
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        #### 📖 Hướng dẫn
        
        **Chức năng chính:**
        - 🔄 Chuyển đổi giữa 4 loại báo cáo
        - 🎯 Xem theo Thị trường/Ngành/Cổ phiếu
        - 📊 Lọc chỉ số cần thiết
        
        **Đơn vị:**
        - Tài chính: **Tỷ VNĐ**
        - Ratio: **%, lần, tỷ lệ**
        
        **Màu sắc:**
        - 🟣 Header: Gradient tím
        - 🔴 Header chỉ số: Gradient đỏ
        - ⚪ Dòng chẵn: Nền xám nhạt
        - 🔵 Hover: Nền xanh nhạt
        """)
    
    with col2:
        st.markdown('#### 📈 Phân tích nhanh')
        
        try:
            df_symbol = df[df['SYMBOL'] == selected_symbol].copy()
            
            if len(df_symbol) >= 2:
                latest = df_symbol.iloc[-1]
                prev = df_symbol.iloc[-2]
                
                metrics_to_show = []
                
                # Revenue growth
                if 'NET_SALES' in df_symbol.columns:
                    if prev['NET_SALES'] != 0 and pd.notna(prev['NET_SALES']) and pd.notna(latest['NET_SALES']):
                        growth = ((latest['NET_SALES'] - prev['NET_SALES']) / abs(prev['NET_SALES'])) * 100
                        metrics_to_show.append(('Tăng trưởng DT', f'{growth:.1f}%', growth))
                
                # Profit growth
                if 'NPATMI' in df_symbol.columns:
                    if prev['NPATMI'] != 0 and pd.notna(prev['NPATMI']) and pd.notna(latest['NPATMI']):
                        growth = ((latest['NPATMI'] - prev['NPATMI']) / abs(prev['NPATMI'])) * 100
                        metrics_to_show.append(('Tăng trưởng LN', f'{growth:.1f}%', growth))
                
                # Display
                if metrics_to_show:
                    for name, val, delta in metrics_to_show:
                        st.metric(name, val, f'{delta:.1f}%')
                
                # Key ratios
                st.markdown('**Chỉ số chính:**')
                ratio_cols = st.columns(2)
                
                if 'ROAE' in latest and pd.notna(latest['ROAE']):
                    ratio_cols[0].metric('ROE', f"{latest['ROAE']*100:.1f}%")
                
                if 'PE_EOQ' in latest and pd.notna(latest['PE_EOQ']):
                    ratio_cols[1].metric('P/E', f"{latest['PE_EOQ']:.1f}")
                    
            else:
                st.info('Cần ít nhất 2 quý để phân tích')
                
        except Exception as e:
            st.info('Không thể phân tích')

# Footer
st.markdown("""
<div style='text-align: center; color: #666; padding: 20px;'>
    📊 <b>Báo cáo Tài chính</b> | Powered by Streamlit
</div>
""", unsafe_allow_html=True)