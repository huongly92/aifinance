"""
Formatters Module
Format dữ liệu để hiển thị đẹp và dễ đọc
"""

import pandas as pd
import numpy as np


def format_number(value, decimals=2):
    """
    Format số thông thường
    
    Args:
        value: Giá trị cần format
        decimals: Số chữ số thập phân
        
    Returns:
        str: Số đã được format
    """
    if pd.isna(value):
        return "N/A"
    
    try:
        value = float(value)
        if abs(value) >= 1e9:
            return f"{value/1e9:,.{decimals}f}B"
        elif abs(value) >= 1e6:
            return f"{value/1e6:,.{decimals}f}M"
        elif abs(value) >= 1e3:
            return f"{value/1e3:,.{decimals}f}K"
        else:
            return f"{value:,.{decimals}f}"
    except (ValueError, TypeError):
        return "N/A"


def format_percent(value, decimals=2):
    """
    Format phần trăm
    
    Args:
        value: Giá trị (đã là %, không cần nhân 100)
        decimals: Số chữ số thập phân
        
    Returns:
        str: Phần trăm đã được format
    """
    if pd.isna(value):
        return "N/A"
    
    try:
        value = float(value)
        return f"{value:,.{decimals}f}%"
    except (ValueError, TypeError):
        return "N/A"


def format_billion(value, decimals=2):
    """
    Format số lớn theo đơn vị tỷ
    
    Args:
        value: Giá trị
        decimals: Số chữ số thập phân
        
    Returns:
        str: Số đã format theo tỷ
    """
    if pd.isna(value):
        return "N/A"
    
    try:
        value = float(value)
        return f"{value/1e9:,.{decimals}f} tỷ"
    except (ValueError, TypeError):
        return "N/A"


def format_price(value, decimals=2):
    """
    Format giá cổ phiếu
    
    Args:
        value: Giá
        decimals: Số chữ số thập phân
        
    Returns:
        str: Giá đã format
    """
    if pd.isna(value):
        return "N/A"
    
    try:
        value = float(value)
        return f"{value:,.{decimals}f}"
    except (ValueError, TypeError):
        return "N/A"


def format_change(value, decimals=2, show_sign=True):
    """
    Format thay đổi (với màu sắc)
    
    Args:
        value: Giá trị thay đổi
        decimals: Số chữ số thập phân
        show_sign: Hiển thị dấu +/-
        
    Returns:
        str: Thay đổi đã format
    """
    if pd.isna(value):
        return "N/A"
    
    try:
        value = float(value)
        sign = "+" if value > 0 and show_sign else ""
        return f"{sign}{value:,.{decimals}f}%"
    except (ValueError, TypeError):
        return "N/A"


def format_ratio(value, decimals=2):
    """
    Format tỷ lệ (P/E, P/B, etc.)
    
    Args:
        value: Giá trị tỷ lệ
        decimals: Số chữ số thập phân
        
    Returns:
        str: Tỷ lệ đã format
    """
    if pd.isna(value):
        return "N/A"
    
    try:
        value = float(value)
        if value < 0:
            return "N/A"
        return f"{value:,.{decimals}f}"
    except (ValueError, TypeError):
        return "N/A"


def format_currency(value, decimals=0):
    """
    Format tiền tệ (VND)
    
    Args:
        value: Giá trị
        decimals: Số chữ số thập phân
        
    Returns:
        str: Tiền tệ đã format
    """
    if pd.isna(value):
        return "N/A"
    
    try:
        value = float(value)
        if abs(value) >= 1e12:
            return f"{value/1e12:,.{decimals}f} nghìn tỷ"
        elif abs(value) >= 1e9:
            return f"{value/1e9:,.{decimals}f} tỷ"
        elif abs(value) >= 1e6:
            return f"{value/1e6:,.{decimals}f} triệu"
        else:
            return f"{value:,.{decimals}f}"
    except (ValueError, TypeError):
        return "N/A"


def apply_conditional_formatting(df, column, format_type='number'):
    """
    Áp dụng format cho một cột trong DataFrame
    
    Args:
        df: DataFrame
        column: Tên cột
        format_type: Loại format ('number', 'percent', 'billion', 'price', 'ratio')
        
    Returns:
        Series: Cột đã được format
    """
    if column not in df.columns:
        return df[column] if column in df.columns else None
    
    formatters = {
        'number': format_number,
        'percent': format_percent,
        'billion': format_billion,
        'price': format_price,
        'ratio': format_ratio,
        'currency': format_currency
    }
    
    formatter = formatters.get(format_type, format_number)
    return df[column].apply(formatter)


def get_color_for_value(value, metric_type='growth'):
    """
    Lấy màu cho giá trị dựa trên loại metric
    
    Args:
        value: Giá trị
        metric_type: Loại metric ('growth', 'ratio', 'margin')
        
    Returns:
        str: Mã màu hex
    """
    if pd.isna(value):
        return '#808080'  # Gray for N/A
    
    try:
        value = float(value)
        
        if metric_type == 'growth':
            if value > 0:
                return '#00CC96'  # Green for positive
            elif value < 0:
                return '#EF553B'  # Red for negative
            else:
                return '#636EFA'  # Blue for neutral
        
        elif metric_type == 'ratio':
            # For ratios like P/E, lower is often better
            if value < 15:
                return '#00CC96'  # Green for attractive
            elif value > 25:
                return '#EF553B'  # Red for expensive
            else:
                return '#FFA15A'  # Orange for moderate
        
        elif metric_type == 'margin':
            # For margins, higher is better
            if value > 15:
                return '#00CC96'  # Green for high
            elif value < 5:
                return '#EF553B'  # Red for low
            else:
                return '#FFA15A'  # Orange for moderate
        
    except (ValueError, TypeError):
        pass
    
    return '#808080'  # Gray for invalid


def create_styled_dataframe(df, numeric_columns=None):
    """
    Tạo DataFrame với styling
    
    Args:
        df: DataFrame gốc
        numeric_columns: Dict mapping column -> format_type
        
    Returns:
        Styled DataFrame
    """
    if numeric_columns is None:
        return df
    
    styled_df = df.copy()
    
    for col, format_type in numeric_columns.items():
        if col in styled_df.columns:
            styled_df[col] = apply_conditional_formatting(styled_df, col, format_type)
    
    return styled_df


def format_quarter_display(quarter_str):
    """
    Format quarter để hiển thị
    
    Args:
        quarter_str: Quarter string (e.g., '2024Q1')
        
    Returns:
        str: Quarter đã format (e.g., 'Q1 2024')
    """
    try:
        year = quarter_str[:4]
        quarter = quarter_str[-1]
        return f"Q{quarter} {year}"
    except:
        return quarter_str
