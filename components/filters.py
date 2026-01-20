"""
Filters Module
Tạo các bộ lọc và controls
"""

import streamlit as st
import pandas as pd


def date_range_filter(quarters, key_prefix="date"):
    """
    Bộ lọc khoảng thời gian
    
    Args:
        quarters: List các quarter
        key_prefix: Prefix cho key
        
    Returns:
        tuple: (start_quarter, end_quarter)
    """
    col1, col2 = st.columns(2)
    
    with col1:
        start = st.selectbox(
            "Từ quý",
            quarters,
            key=f"{key_prefix}_start"
        )
    
    with col2:
        end = st.selectbox(
            "Đến quý",
            quarters,
            index=len(quarters)-1,
            key=f"{key_prefix}_end"
        )
    
    return start, end


def multi_select_filter(label, options, default=None, key=None):
    """
    Bộ lọc multi-select
    
    Args:
        label: Nhãn
        options: List options
        default: Giá trị mặc định
        key: Key cho widget
        
    Returns:
        list: Các giá trị đã chọn
    """
    return st.multiselect(
        label,
        options,
        default=default,
        key=key
    )


def metric_selector(metric_groups, key_prefix="metric"):
    """
    Bộ chọn metrics theo nhóm
    
    Args:
        metric_groups: Dict {group_name: [metrics]}
        key_prefix: Prefix cho key
        
    Returns:
        list: Các metrics đã chọn
    """
    selected_group = st.selectbox(
        "Chọn nhóm chỉ số",
        list(metric_groups.keys()),
        key=f"{key_prefix}_group"
    )
    
    selected_metrics = st.multiselect(
        "Chọn chỉ số cụ thể",
        metric_groups[selected_group],
        default=metric_groups[selected_group][:3] if len(metric_groups[selected_group]) >= 3 else metric_groups[selected_group],
        key=f"{key_prefix}_items"
    )
    
    return selected_metrics


def number_range_filter(label, min_val=0, max_val=100, default_range=None, key=None):
    """
    Bộ lọc khoảng số
    
    Args:
        label: Nhãn
        min_val: Giá trị min
        max_val: Giá trị max
        default_range: Khoảng mặc định
        key: Key cho widget
        
    Returns:
        tuple: (min_selected, max_selected)
    """
    if default_range is None:
        default_range = (min_val, max_val)
    
    return st.slider(
        label,
        min_value=float(min_val),
        max_value=float(max_val),
        value=default_range,
        key=key
    )
