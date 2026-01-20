"""
📊 Financial Report Display - Optimized Version
Hiển thị báo cáo tài chính với performance cao và dễ customize
"""

import pandas as pd
import streamlit as st
from typing import Dict, List, Optional, Tuple

# ==================== FINANCIAL METRICS ====================
from components.excel_processor import ExcelProcessorAdvanced
# from excel_processor import ExcelProcessorAdvanced
map_path = "D:/aifinance_project/data/raw/Map_Complete.xlsx"
processor = ExcelProcessorAdvanced(map_path)   

LEVEL_MAP = 3

FINANCIAL_METRICS = processor.to_nested_dict_advanced(
    ['company_map','bank_map', 'security_map', 'insurance_map',\
     'company_ratio', 'bank_ratio', 'security_ratio', 'insurance_ratio'],
    key_hierarchy=['CAL_GROUP', 'CATEGORY', 'COL'],
    value_columns=['VN_NAME', 'ORDER'],
    filters={
        'LEVEL': {'<=':LEVEL_MAP}, 'CATEGORY': {'in':['BS', 'IS', 'CF', 'ratio'] }
    },
)
# print(FINANCIAL_METRICS)

# =================== STYLE CONFIG ====================
# Import style config
try:
    from components.financial_report_style_config import (
        COLORS, FONTS, SPACING, COLUMN_WIDTH,
        get_table_styles, get_cell_properties, get_group_info, get_streamlit_css
    )
except ImportError:
    st.warning("⚠️ Không tìm thấy financial_report_style_config.py, sử dụng style mặc định")
    # Fallback to default
    COLORS = {'negative_number': '#D32F2F'}
    def get_table_styles(): return []
    def get_cell_properties(): return {}
    def get_group_info(): 
        return {
            'company': {'icon': '🏢', 'name': 'Công ty', 'color': '#1976D2'},
            'bank': {'icon': '🏦', 'name': 'Ngân hàng', 'color': '#388E3C'},
            'security': {'icon': '📈', 'name': 'Chứng khoán', 'color': '#F57C00'},
            'insurance': {'icon': '🛡️', 'name': 'Bảo hiểm', 'color': '#7B1FA2'},
        }

# ==================== CACHED HELPER FUNCTIONS ====================

@st.cache_data(show_spinner=False)
def detect_cal_group(df: pd.DataFrame, symbol: str) -> str:
    """Phát hiện CAL_GROUP (cached)"""
    symbol_data = df[df['SYMBOL'] == symbol]
    if symbol_data.empty:
        return 'company'
    
    if 'CAL_GROUP' in symbol_data.columns:
        cal_group = symbol_data['CAL_GROUP'].iloc[0]
        if pd.notna(cal_group):
            cal_group = str(cal_group).lower()
            if cal_group in ['company', 'bank', 'security', 'insurance']:
                return cal_group
    
    return 'company'


def get_metrics_for_report_type(cal_group: str, report_type: str) -> Dict:
    """Lấy metrics cho report type"""
    if cal_group not in FINANCIAL_METRICS:
        cal_group = 'company'
    if report_type not in FINANCIAL_METRICS[cal_group]:
        return {}
    return FINANCIAL_METRICS[cal_group][report_type]


def format_value(val, format_type: str = 'billion'):
    """Format giá trị theo loại"""
    if pd.isna(val) or not isinstance(val, (int, float)):
        return val
    
    if format_type == 'billion':
        return val / 1e9
    elif format_type in ['percent', 'number']:
        return val
    elif format_type == 'vnd':
        return val / 1e9
    else:
        return val / 1e9


@st.cache_data(show_spinner=False)
def prepare_financial_data(
    df: pd.DataFrame,
    symbol: str,
    report_type: str = 'IS',
    metrics: List[str] = None
) -> Tuple[pd.DataFrame, str, Dict]:
    """Chuẩn bị dữ liệu tài chính (cached)"""
    
    # Lọc dữ liệu
    df_filtered = df[df['SYMBOL'] == symbol].copy()
    if df_filtered.empty:
        return pd.DataFrame(), 'company', {}
    
    # Phát hiện CAL_GROUP
    cal_group = detect_cal_group(df, symbol)
    
    # Lấy metrics info
    metrics_info = get_metrics_for_report_type(cal_group, report_type)
    
    # Lấy metrics
    if metrics is None:
        metrics = list(metrics_info.keys())
    
    # Chỉ giữ metrics có trong data
    available_metrics = [m for m in metrics if m in df_filtered.columns]
    if not available_metrics:
        return pd.DataFrame(), cal_group, {}
    
    # Tạo Quarter_Year
    df_filtered['QUARTER_YEAR'] = df_filtered['QUARTER'].astype(str)
    
    # Pivot data
    columns_to_keep = ['QUARTER_YEAR'] + available_metrics
    df_pivoted = df_filtered[columns_to_keep].copy()
    df_pivoted = df_pivoted.set_index('QUARTER_YEAR').T
    df_pivoted.columns.name = None  # Xóa tên column index
    
    # Thêm tên chỉ số
    df_pivoted['Chỉ số'] = df_pivoted.index.map(
        lambda x: metrics_info.get(x, {}).get('name', x)
    )
    
    # Thêm cột _code để tham chiếu
    df_pivoted['_code'] = df_pivoted.index
    
    # Sắp xếp
    quarter_cols = [col for col in df_pivoted.columns if col not in ['Chỉ số', '_code']]
    df_pivoted = df_pivoted[['_code', 'Chỉ số'] + sorted(quarter_cols, reverse=True)]
    
    # Sort theo order
    df_pivoted['_ORDER'] = df_pivoted['_code'].map(
        lambda x: metrics_info.get(x, {}).get('ORDER', 999)
    )
    df_pivoted = df_pivoted.sort_values('_ORDER').drop('_ORDER', axis=1)

    # Đặt 'Chỉ số' làm index
    df_pivoted = df_pivoted.set_index('Chỉ số')
    
    return df_pivoted, cal_group, metrics_info


def display_financial_report(
    df: pd.DataFrame,
    symbol: str,
    report_type: str = 'IS',
    metrics: List[str] = None
):
    """Hiển thị báo cáo tài chính"""
    
    # Chuẩn bị dữ liệu (cached)
    df_display, cal_group, metrics_info = prepare_financial_data(
        df, symbol, report_type, metrics
    )
    
    if df_display.empty:
        st.warning(f'⚠️ Không tìm thấy dữ liệu cho {symbol}')
        return
    
    # Get group info
    group_info = get_group_info()
    info = group_info.get(cal_group, group_info['company'])
    
    # Header với màu sắc
    st.markdown(f"""
        <div style='background: linear-gradient(90deg, {info['color']}15 0%, {info['color']}05 100%); 
                    padding: 15px; border-radius: 10px; border-left: 4px solid {info['color']}; margin-bottom: 10px;'>
            <h4 style='margin: 0; color: {info['color']};'>
                {info['icon']} {info['name']} - {symbol}
            </h4>
        </div>
    """, unsafe_allow_html=True)
    
    # Đơn vị
    unit_text = '📊 Đơn vị: Tỷ lệ, %, lần, VNĐ' if report_type == 'ratio' else '💰 Đơn vị: Tỷ VNĐ'
    st.caption(unit_text)
    
    # Format dữ liệu
    df_styled = df_display.copy()
    
    if report_type == 'ratio':
        # Format theo từng metric
        for idx, row in df_styled.iterrows():
            code = row.get('_code', '')
            if code in metrics_info:
                fmt = metrics_info[code].get('format', 'number')
                for col in df_styled.columns:
                    if col != '_code':
                        df_styled.at[idx, col] = format_value(row[col], fmt)
    else:
        # Format tất cả sang tỷ
        for col in df_styled.columns:
            if col != '_code':
                df_styled[col] = df_styled[col].apply(lambda x: format_value(x, 'billion'))
    
    # Highlight số âm
    def highlight_negative(val):
        try:
            if isinstance(val, (int, float)) and val < 0:
                return f'color: {COLORS["negative_number"]}; font-weight: 600'
            return ''
        except:
            return ''
    
    # Remove _code column và reset index để "Chỉ số" thành cột thường
    df_to_display = df_styled.drop(columns=['_code']).reset_index()
    
    # Apply styling
    styled_df = df_to_display.style\
        .hide(axis='index')\
        .applymap(highlight_negative, subset=[col for col in df_to_display.columns if col != 'Chỉ số'])\
        .format('{:,.2f}', subset=[col for col in df_to_display.columns if col != 'Chỉ số'], na_rep='-')\
        .set_properties(**{
            'text-align': 'right',
            'font-size': '13px',
            'padding': '8px'
        }, subset=[col for col in df_to_display.columns if col != 'Chỉ số'])\
        .set_properties(**{
            'text-align': 'left',
            'font-weight': '600',
            'font-size': '13px',
            'padding': '8px',
            'background-color': '#FFF9C4',
            'min-width': '250px',
            'width': '250px'
        }, subset=['Chỉ số'])\
        .set_table_styles(get_table_styles())
    
    # Hiển thị bảng (index=False vì "Chỉ số" đã là cột thường)
    st.write(styled_df.to_html(escape=False, index=False), unsafe_allow_html=True)
    
    # Footer
    st.markdown('<br>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    
    report_names = {
        'IS': 'Kết quả Kinh doanh',
        'BS': 'Cân đối Kế toán',
        'CF': 'Lưu chuyển Tiền tệ',
        'ratio': 'Chỉ số Phân tích'
    }
    
    with col1:
        st.metric('📊 Số chỉ số', len(df_to_display))
    with col2:
        st.metric('📅 Số quý', len(df_to_display.columns))
    with col3:
        st.metric('📋 Loại', report_names.get(report_type, report_type))


@st.cache_data(show_spinner=False)
def get_available_metrics(df: pd.DataFrame, symbol: str, report_type: str) -> List[str]:
    """Lấy danh sách metrics có sẵn (cached)"""
    symbol_data = df[df['SYMBOL'] == symbol]
    if symbol_data.empty:
        return []
    
    cal_group = detect_cal_group(df, symbol)
    metrics_info = get_metrics_for_report_type(cal_group, report_type)
    
    return [m for m in metrics_info.keys() if m in symbol_data.columns]


def export_to_excel(df: pd.DataFrame, symbol: str, report_type: str) -> bytes:
    """
    Export dữ liệu ra file Excel
    Returns: bytes data của file Excel
    """
    from io import BytesIO
    
    output = BytesIO()
    
    # Tạo Excel writer
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name=report_type, index=True)
    
    output.seek(0)
    return output.getvalue()


def export_to_csv(df: pd.DataFrame) -> str:
    """
    Export dữ liệu ra CSV
    Returns: CSV string
    """
    return df.to_csv(index=True).encode('utf-8')


def create_export_buttons(df: pd.DataFrame, symbol: str, report_type: str):
    """
    Tạo các nút export cho báo cáo
    
    Args:
        df: DataFrame cần export (đã format)
        symbol: Mã chứng khoán
        report_type: Loại báo cáo
    """
    report_names = {
        'IS': 'Ket_qua_KD',
        'BS': 'Can_doi_KT',
        'CF': 'Luu_chuyen_TT',
        'ratio': 'Chi_so'
    }
    
    file_name = f"{symbol}_{report_names.get(report_type, report_type)}"
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Export Excel
        excel_data = export_to_excel(df, symbol, report_type)
        st.download_button(
            label="📥 Export Excel",
            data=excel_data,
            file_name=f"{file_name}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
    
    with col2:
        # Export CSV
        csv_data = export_to_csv(df)
        st.download_button(
            label="📥 Export CSV",
            data=csv_data,
            file_name=f"{file_name}.csv",
            mime="text/csv",
            use_container_width=True
        )


# ==================== EXPORT ====================

__all__ = [
    'FINANCIAL_METRICS',
    'detect_cal_group',
    'get_metrics_for_report_type',
    'format_value',
    'prepare_financial_data',
    'display_financial_report',
    'get_available_metrics',
    'create_export_buttons'
]