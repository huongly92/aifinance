"""
KPI Cards Module
Tạo các KPI cards để hiển thị metrics
"""

import streamlit as st
from utils.formatters import *


def display_kpi_card(label, value, delta=None, format_type='number'):
    """
    Hiển thị một KPI card
    
    Args:
        label: Nhãn
        value: Giá trị
        delta: Thay đổi (optional)
        format_type: Loại format
    """
    formatters = {
        'number': format_number,
        'percent': format_percent,
        'billion': format_billion,
        'price': format_price,
        'ratio': format_ratio
    }
    
    formatter = formatters.get(format_type, format_number)
    formatted_value = formatter(value)
    
    if delta is not None:
        formatted_delta = format_change(delta)
        st.metric(label, formatted_value, formatted_delta)
    else:
        st.metric(label, formatted_value)


def display_kpi_row(kpis):
    """
    Hiển thị một hàng KPIs
    
    Args:
        kpis: List of dict {label, value, delta, format_type}
    """
    cols = st.columns(len(kpis))
    
    for col, kpi in zip(cols, kpis):
        with col:
            display_kpi_card(
                kpi.get('label', ''),
                kpi.get('value'),
                kpi.get('delta'),
                kpi.get('format_type', 'number')
            )


def display_metric_card(title, metrics_dict, format_dict=None):
    """
    Hiển thị card chứa nhiều metrics
    
    Args:
        title: Tiêu đề card
        metrics_dict: Dict {label: value}
        format_dict: Dict {label: format_type}
    """
    st.subheader(title)
    
    if format_dict is None:
        format_dict = {}
    
    # Hiển thị theo grid 2 cột
    items = list(metrics_dict.items())
    for i in range(0, len(items), 2):
        cols = st.columns(2)
        
        for j, col in enumerate(cols):
            if i + j < len(items):
                label, value = items[i + j]
                format_type = format_dict.get(label, 'number')
                
                with col:
                    display_kpi_card(label, value, format_type=format_type)
