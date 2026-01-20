"""
Tables Module
Tạo các bảng dữ liệu với styling
"""

import streamlit as st
import pandas as pd
from utils.formatters import *
import config


def create_styled_table(df, numeric_formats=None, highlight_cols=None):
    """
    Tạo bảng với styling
    
    Args:
        df: DataFrame
        numeric_formats: Dict {column: format_type}
        highlight_cols: List columns cần highlight
        
    Returns:
        Styled DataFrame
    """
    if numeric_formats:
        styled_df = df.copy()
        for col, fmt in numeric_formats.items():
            if col in styled_df.columns:
                if fmt == 'percent':
                    styled_df[col] = styled_df[col].apply(format_percent)
                elif fmt == 'billion':
                    styled_df[col] = styled_df[col].apply(format_billion)
                elif fmt == 'number':
                    styled_df[col] = styled_df[col].apply(format_number)
                elif fmt == 'ratio':
                    styled_df[col] = styled_df[col].apply(format_ratio)
        return styled_df
    
    return df


def create_comparison_table(df, index_col, value_cols, format_dict=None):
    """
    Tạo bảng so sánh
    
    Args:
        df: DataFrame
        index_col: Cột làm index
        value_cols: List các cột giá trị
        format_dict: Dict format cho từng cột
        
    Returns:
        DataFrame
    """
    result = df[[index_col] + value_cols].copy()
    
    if format_dict:
        result = create_styled_table(result, format_dict)
    
    return result


def create_ranking_table(df, rank_by, ascending=False, top_n=10):
    """
    Tạo bảng xếp hạng
    
    Args:
        df: DataFrame
        rank_by: Cột để xếp hạng
        ascending: Sắp xếp tăng dần
        top_n: Số lượng top
        
    Returns:
        DataFrame
    """
    sorted_df = df.sort_values(rank_by, ascending=ascending).head(top_n).copy()
    sorted_df.insert(0, 'Rank', range(1, len(sorted_df) + 1))
    
    return sorted_df


def display_dataframe(df, height=400, use_container_width=True):
    """
    Hiển thị dataframe với config
    
    Args:
        df: DataFrame
        height: Chiều cao
        use_container_width: Sử dụng full width
    """
    st.dataframe(
        df,
        height=height,
        use_container_width=use_container_width,
        hide_index=True
    )
