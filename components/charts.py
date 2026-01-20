"""
Charts Module
Tạo các biểu đồ Plotly cho dashboard
"""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
import config

def create_line_chart(df, x_col, y_cols, title="", labels=None, height=400, 
                      show_mean=False, show_std=False, std_fill=False):
    """
    Tạo biểu đồ đường
    
    Args:
        df: DataFrame
        x_col: Cột trục X
        y_cols: Cột hoặc list cột trục Y
        title: Tiêu đề
        labels: Dict mapping column -> label
        height: Chiều cao
        show_mean: Hiển thị đường trung bình
        show_std: Hiển thị đường ±1 standard deviation
        std_fill: Tô vùng giữa ±1σ thay vì vẽ đường
        
    Returns:
        Figure: Plotly figure
    """
    fig = go.Figure()
    
    if not isinstance(y_cols, list):
        y_cols = [y_cols]
    
    colors = px.colors.qualitative.Plotly
    annotations = []
    x_data = df[x_col]
    x_last = x_data.iloc[-1]
    
    def add_horizontal_line(y_value, name, color, dash='dash', width=1.5, opacity=1.0):
        """Helper: Thêm đường ngang"""
        fig.add_trace(go.Scatter(
            x=x_data,
            y=[y_value] * len(df),
            mode='lines',
            name=name,
            line=dict(width=width, dash=dash, color=color),
            opacity=opacity,
            showlegend=True
        ))
    
    def add_annotation(y_value, text, color, font_size=10):
        """Helper: Thêm annotation"""
        annotations.append(dict(
            x=x_last,
            y=y_value,
            text=text,
            showarrow=False,
            xanchor='left',
            xshift=10,
            font=dict(size=font_size, color=color),
            bgcolor='rgba(255,255,255,0.8)',
            borderpad=2
        ))
    
    for idx, col in enumerate(y_cols):
        if col not in df.columns:
            continue
            
        label = labels.get(col, col) if labels else col
        color = colors[idx % len(colors)]
        y_data = df[col]
        
        # Vẽ đường dữ liệu
        fig.add_trace(go.Scatter(
            x=x_data,
            y=y_data,
            mode='lines+markers',
            name=label,
            line=dict(width=2, color=color),
            marker=dict(size=6, color=color)
        ))
        
        # Tính toán statistics
        mean_val = y_data.mean()
        std_val = y_data.std()
        upper_bound = mean_val + std_val
        lower_bound = mean_val - std_val
        
        # Đường trung bình
        if show_mean:
            add_horizontal_line(mean_val, f'{label} (TB)', color, 'dash', 1.5)
            add_annotation(mean_val, f'{mean_val:.2f}', color)
        
        # Standard deviation
        if show_std:
            if std_fill:
                # Tô vùng giữa ±1σ
                upper_list = [upper_bound] * len(df)
                lower_list = [lower_bound] * len(df)
                
                fig.add_trace(go.Scatter(
                    x=list(x_data) + list(x_data)[::-1],
                    y=upper_list + lower_list[::-1],  # Sửa chỗ này
                    fill='toself',
                    fillcolor=f'rgba{tuple(list(px.colors.hex_to_rgb(color)) + [0.15])}',
                    line=dict(width=0),
                    name=f'{label} (±1σ)',
                    showlegend=True,
                    hoverinfo='skip'
                ))
            else:
                # Vẽ 2 đường riêng biệt
                add_horizontal_line(upper_bound, f'{label} (+1σ)', color, 'dot', 1, 0.6)
                add_horizontal_line(lower_bound, f'{label} (-1σ)', color, 'dot', 1, 0.6)
            
            # Annotations cho ±1σ
            add_annotation(upper_bound, f'{upper_bound:.2f}', color, 9)
            add_annotation(lower_bound, f'{lower_bound:.2f}', color, 9)
    
    fig.update_layout(
        title=title,
        xaxis_title=labels.get(x_col, x_col) if labels else x_col,
        template=config.CHART_TEMPLATE,
        height=height,
        hovermode='x unified',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        annotations=annotations
    )
    
    return fig


def create_bar_chart(df, x_col, y_col, title="", orientation='v', color_col=None, height=400):
    """
    Tạo biểu đồ cột
    
    Args:
        df: DataFrame
        x_col: Cột trục X
        y_col: Cột trục Y
        title: Tiêu đề
        orientation: 'v' (vertical) hoặc 'h' (horizontal)
        color_col: Cột để tô màu
        height: Chiều cao
        
    Returns:
        Figure: Plotly figure
    """
    if orientation == 'v':
        fig = px.bar(df, x=x_col, y=y_col, title=title, color=color_col)
    else:
        fig = px.bar(df, x=y_col, y=x_col, title=title, 
                    orientation='h', color=color_col)
    
    fig.update_layout(
        template=config.CHART_TEMPLATE,
        height=height,
        showlegend=True if color_col else False
    )
    
    return fig


def create_grouped_bar_chart(df, x_col, y_cols, title="", labels=None, height=400):
    """
    Tạo biểu đồ cột nhóm
    
    Args:
        df: DataFrame
        x_col: Cột trục X
        y_cols: List cột trục Y
        title: Tiêu đề
        labels: Dict mapping column -> label
        height: Chiều cao
        
    Returns:
        Figure: Plotly figure
    """
    fig = go.Figure()
    
    for col in y_cols:
        if col in df.columns:
            label = labels.get(col, col) if labels else col
            fig.add_trace(go.Bar(
                x=df[x_col],
                y=df[col],
                name=label
            ))
    
    fig.update_layout(
        title=title,
        barmode='group',
        template=config.CHART_TEMPLATE,
        height=height,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    return fig


def create_scatter_chart(df, x_col, y_col, title="", color_col=None, size_col=None, 
                        text_col=None, height=400):
    """
    Tạo biểu đồ phân tán
    
    Args:
        df: DataFrame
        x_col: Cột trục X
        y_col: Cột trục Y
        title: Tiêu đề
        color_col: Cột để tô màu
        size_col: Cột để quy định kích thước
        text_col: Cột để hiển thị text
        height: Chiều cao
        
    Returns:
        Figure: Plotly figure
    """
    fig = px.scatter(
        df, 
        x=x_col, 
        y=y_col, 
        color=color_col,
        size=size_col,
        text=text_col,
        title=title
    )
    
    fig.update_traces(textposition='top center')
    
    fig.update_layout(
        template=config.CHART_TEMPLATE,
        height=height
    )
    
    return fig


def create_pie_chart(df, names_col, values_col, title="", height=400):
    """
    Tạo biểu đồ tròn
    
    Args:
        df: DataFrame
        names_col: Cột tên
        values_col: Cột giá trị
        title: Tiêu đề
        height: Chiều cao
        
    Returns:
        Figure: Plotly figure
    """
    fig = px.pie(
        df, 
        names=names_col, 
        values=values_col,
        title=title
    )
    
    fig.update_traces(
        textposition='inside',
        textinfo='percent+label'
    )
    
    fig.update_layout(
        template=config.CHART_TEMPLATE,
        height=height
    )
    
    return fig


def create_heatmap(df, title="", height=400, colorscale='RdYlGn'):
    """
    Tạo heatmap
    
    Args:
        df: DataFrame (dạng ma trận)
        title: Tiêu đề
        height: Chiều cao
        colorscale: Bảng màu
        
    Returns:
        Figure: Plotly figure
    """
    fig = go.Figure(data=go.Heatmap(
        z=df.values,
        x=df.columns,
        y=df.index,
        colorscale=colorscale,
        text=df.values,
        texttemplate='%{text:.2f}',
        textfont={"size": 10},
        colorbar=dict(title="")
    ))
    
    fig.update_layout(
        title=title,
        template=config.CHART_TEMPLATE,
        height=height
    )
    
    return fig


def create_waterfall_chart(categories, values, title="", height=400):
    """
    Tạo biểu đồ waterfall
    
    Args:
        categories: List tên các mục
        values: List giá trị
        title: Tiêu đề
        height: Chiều cao
        
    Returns:
        Figure: Plotly figure
    """
    fig = go.Figure(go.Waterfall(
        name="",
        orientation="v",
        x=categories,
        y=values,
        connector={"line": {"color": "rgb(63, 63, 63)"}},
    ))
    
    fig.update_layout(
        title=title,
        template=config.CHART_TEMPLATE,
        height=height
    )
    
    return fig


def create_radar_chart(df, categories, title="", height=400):
    """
    Tạo biểu đồ radar
    
    Args:
        df: DataFrame với các cột là metrics
        categories: List tên metrics
        title: Tiêu đề
        height: Chiều cao
        
    Returns:
        Figure: Plotly figure
    """
    fig = go.Figure()
    
    for idx, row in df.iterrows():
        fig.add_trace(go.Scatterpolar(
            r=[row[cat] for cat in categories if cat in row],
            theta=categories,
            fill='toself',
            name=str(idx)
        ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100]
            )),
        showlegend=True,
        title=title,
        template=config.CHART_TEMPLATE,
        height=height
    )
    
    return fig


def create_histogram(df, column, title="", bins=30, height=400):
    """
    Tạo histogram
    
    Args:
        df: DataFrame
        column: Cột cần vẽ
        title: Tiêu đề
        bins: Số bins
        height: Chiều cao
        
    Returns:
        Figure: Plotly figure
    """
    fig = px.histogram(
        df, 
        x=column,
        nbins=bins,
        title=title
    )
    
    fig.update_layout(
        template=config.CHART_TEMPLATE,
        height=height,
        showlegend=False
    )
    
    return fig


def create_box_plot(df, y_col, x_col=None, title="", height=400):
    """
    Tạo box plot
    
    Args:
        df: DataFrame
        y_col: Cột giá trị
        x_col: Cột nhóm (optional)
        title: Tiêu đề
        height: Chiều cao
        
    Returns:
        Figure: Plotly figure
    """
    fig = px.box(
        df,
        y=y_col,
        x=x_col,
        title=title
    )
    
    fig.update_layout(
        template=config.CHART_TEMPLATE,
        height=height
    )
    
    return fig


def create_area_chart(df, x_col, y_cols, title="", labels=None, height=400):
    """
    Tạo biểu đồ vùng xếp chồng
    
    Args:
        df: DataFrame
        x_col: Cột trục X
        y_cols: List cột trục Y
        title: Tiêu đề
        labels: Dict mapping column -> label
        height: Chiều cao
        
    Returns:
        Figure: Plotly figure
    """
    fig = go.Figure()
    
    for col in y_cols:
        if col in df.columns:
            label = labels.get(col, col) if labels else col
            fig.add_trace(go.Scatter(
                x=df[x_col],
                y=df[col],
                name=label,
                mode='lines',
                stackgroup='one',
                fillcolor=None
            ))
    
    fig.update_layout(
        title=title,
        template=config.CHART_TEMPLATE,
        height=height,
        hovermode='x unified'
    )
    
    return fig


def create_gauge_chart(value, title="", min_val=0, max_val=100, 
                      thresholds=None, height=300):
    """
    Tạo biểu đồ gauge (đồng hồ)
    
    Args:
        value: Giá trị hiện tại
        title: Tiêu đề
        min_val: Giá trị min
        max_val: Giá trị max
        thresholds: Dict {threshold: color}
        height: Chiều cao
        
    Returns:
        Figure: Plotly figure
    """
    # Default thresholds
    if thresholds is None:
        thresholds = {
            max_val * 0.33: 'red',
            max_val * 0.67: 'yellow',
            max_val: 'green'
        }
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=value,
        title={'text': title},
        gauge={
            'axis': {'range': [min_val, max_val]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [min_val, list(thresholds.keys())[0]], 
                 'color': list(thresholds.values())[0]},
                {'range': [list(thresholds.keys())[0], list(thresholds.keys())[1]], 
                 'color': list(thresholds.values())[1]},
                {'range': [list(thresholds.keys())[1], max_val], 
                 'color': list(thresholds.values())[2]}
            ],
        }
    ))
    
    fig.update_layout(
        template=config.CHART_TEMPLATE,
        height=height
    )
    
    return fig

def plot_distribution_by_industry(
    data,
    y_column,
    title,
    y_label,
    x_column='LEVEL2_NAME_EN',
    x_label='Ngành',
    filter_outliers=True,
    min_value=None,
    max_value=None,
    multiply_by=1,
    height=600,
    theme='plotly_white',
    show_chart=True
):
    """
    Vẽ biểu đồ phân phối (box plot) theo ngành với nhiều tùy chọn
    
    Parameters:
    -----------
    data : DataFrame
        Dữ liệu đầu vào
    y_column : str
        Tên cột dữ liệu trục Y
    title : str
        Tiêu đề biểu đồ
    y_label : str
        Nhãn trục Y
    x_column : str
        Tên cột nhóm (mặc định là LEVEL2_NAME_EN)
    x_label : str
        Nhãn trục X
    filter_outliers : bool
        Có lọc outliers không (mặc định True)
    min_value : float
        Giá trị tối thiểu (None = không giới hạn)
    max_value : float
        Giá trị tối đa (None = không giới hạn)
    multiply_by : float
        Nhân giá trị với số này (VD: 100 để chuyển sang %)
    height : int
        Chiều cao biểu đồ (pixels)
    theme : str
        Theme của biểu đồ
    show_chart : bool
        Hiển thị biểu đồ ngay hay chỉ trả về figure
    
    Returns:
    --------
    fig : plotly.graph_objects.Figure
        Figure object (nếu show_chart=False)
    """
    import plotly.express as px
    import streamlit as st
    
    # Kiểm tra cột tồn tại
    if y_column not in data.columns:
        st.error(f"❌ Cột '{y_column}' không tồn tại trong dữ liệu!")
        return None
    
    if x_column not in data.columns:
        st.error(f"❌ Cột '{x_column}' không tồn tại trong dữ liệu!")
        return None
    
    # Copy data để không ảnh hưởng data gốc
    plot_data = data.copy()
    
    # Lọc outliers
    if filter_outliers:
        if min_value is not None:
            plot_data = plot_data[plot_data[y_column] >= min_value]
        if max_value is not None:
            plot_data = plot_data[plot_data[y_column] <= max_value]
    
    # Kiểm tra data sau khi lọc
    if len(plot_data) == 0:
        st.warning("⚠️ Không có dữ liệu sau khi lọc!")
        return None
    
    # Chuyển đổi giá trị (VD: nhân 100 cho %)
    if multiply_by != 1:
        plot_column = f"{y_column}_transformed"
        plot_data[plot_column] = plot_data[y_column] * multiply_by
    else:
        plot_column = y_column
    
    # Vẽ biểu đồ
    fig = px.box(
        plot_data,
        x=x_column,
        y=plot_column,
        title=title,
        labels={x_column: x_label, plot_column: y_label}
    )
    
    # Cập nhật layout
    fig.update_layout(
        height=height,
        template=theme,
        xaxis_tickangle=-45,
        showlegend=False
    )
    
    # Hiển thị hoặc trả về
    if show_chart:
        st.plotly_chart(fig, use_container_width=True)
        
        # Thống kê bổ sung         
        with st.expander("📊 Thống kê chi tiết", expanded=False):
            # PHẦN 1: Thống kê tổng quan
            st.markdown("### 📈 Thống Kê Tổng Quan")
            col1, col2, col3, col4, col5 = st.columns(5)
            
            with col1:
                st.metric("Tổng số mã", len(plot_data))
            with col2:
                st.metric("Số ngành", plot_data[x_column].nunique())
            with col3:
                st.metric("Trung bình", f"{plot_data[plot_column].mean():.2f}")
            with col4:
                st.metric("Trung vị", f"{plot_data[plot_column].median():.2f}")
            with col5:
                st.metric("Độ lệch chuẩn", f"{plot_data[plot_column].std():.2f}")
            
            st.markdown("---")
            
            # PHẦN 2: Thống kê theo ngành
            st.markdown(f"### 📋 Thống Kê {y_label} Theo Ngành")
            
            # Tạo bảng thống kê
            stats_by_industry = plot_data.groupby(x_column)[plot_column].agg([
                ('Số lượng', 'count'),
                ('Trung bình', 'mean'),
                ('Trung vị', 'median'),
                ('Độ lệch chuẩn', 'std'),
                ('Min', 'min'),
                ('Q1', lambda x: x.quantile(0.25)),
                ('Q3', lambda x: x.quantile(0.75)),
                ('Max', 'max')
            ]).reset_index()
            
            # Đổi tên cột x_column
            stats_by_industry.rename(columns={x_column: x_label}, inplace=True)
            
            # Sắp xếp
            stats_by_industry = stats_by_industry.sort_values('Trung bình', ascending=False)
            # Đặt tên cho index
            stats_by_industry.index.name = 'STT'
            stats_by_industry.index = range(1, len(stats_by_industry) + 1)

            # Hiển thị bảng với styling
            st.dataframe(
                stats_by_industry.style.format({
                    'Trung bình': '{:.2f}',
                    'Trung vị': '{:.2f}',
                    'Độ lệch chuẩn': '{:.2f}',
                    'Min': '{:.2f}',
                    'Q1': '{:.2f}',
                    'Q3': '{:.2f}',
                    'Max': '{:.2f}'
                }).background_gradient(subset=['Trung bình'], cmap='RdYlGn'),
                use_container_width=True,
                height=700
            )
            # Nút download
            csv = stats_by_industry.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Tải xuống bảng thống kê (CSV)",
                data=csv,
                file_name=f"stats_{y_column}_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime='text/csv'
            )
    else:
        return fig