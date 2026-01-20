import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime

# Cấu hình trang
st.set_page_config(
    page_title="Phân Tích Cổ Phiếu Việt Nam V2",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS tùy chỉnh nâng cao
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        background: linear-gradient(90deg, #1e3c72 0%, #2a5298 50%, #4a90e2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        padding: 1rem 0;
        animation: gradient 3s ease infinite;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 1rem;
        color: white;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .company-badge {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 0.3rem 0.8rem;
        border-radius: 1rem;
        color: white;
        font-weight: bold;
        display: inline-block;
    }
    .bank-badge {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 0.3rem 0.8rem;
        border-radius: 1rem;
        color: white;
        font-weight: bold;
        display: inline-block;
    }
    .security-badge {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        padding: 0.3rem 0.8rem;
        border-radius: 1rem;
        color: white;
        font-weight: bold;
        display: inline-block;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
    }
    .stTabs [data-baseweb="tab"] {
        height: 3.5rem;
        padding: 0 2rem;
        background-color: #f0f2f6;
        border-radius: 0.5rem 0.5rem 0 0;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    div[data-testid="stMetricValue"] {
        font-size: 1.8rem;
    }
</style>
""", unsafe_allow_html=True)

# Cache data loading
@st.cache_data
def load_data():
    """Load all data files"""
    industry_df = pd.read_parquet(r'D:/aifinance_project/data/output/industry_analysis.parquet')
    market_df = pd.read_parquet(r'D:/aifinance_project/data/output/market_analysis.parquet')
    ticker_df = pd.read_parquet(r'D:/aifinance_project/data/output/ticker_analysis.parquet')
    return industry_df, market_df, ticker_df

def get_company_type_badge(cal_group):
    """Return HTML badge for company type"""
    if cal_group == 'bank':
        return '<span class="bank-badge">🏦 NGÂN HÀNG</span>'
    elif cal_group == 'security':
        return '<span class="security-badge">📊 CHỨNG KHOÁN</span>'
    else:
        return '<span class="company-badge">🏢 DOANH NGHIỆP</span>'

def create_gauge_chart(value, title, min_val=0, max_val=100, thresholds=[30, 70]):
    """Create gauge chart for metrics"""
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=value,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': title, 'font': {'size': 16}},
        gauge={
            'axis': {'range': [min_val, max_val], 'tickwidth': 1},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [min_val, thresholds[0]], 'color': "#ffcdcc"},
                {'range': [thresholds[0], thresholds[1]], 'color': "#ffffcc"},
                {'range': [thresholds[1], max_val], 'color': "#ccffcc"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': value
            }
        }
    ))
    fig.update_layout(height=250, margin=dict(l=20, r=20, t=40, b=20))
    return fig

# Load data
try:
    industry_df, market_df, ticker_df = load_data()
    
    # Tiêu đề chính
    st.markdown('<h1 class="main-header">📈 DASHBOARD PHÂN TÍCH CỔ PHIẾU V2.0</h1>', unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #666; font-size: 1.2rem;'>🚀 Phiên bản nâng cấp với phân tích theo loại hình doanh nghiệp</p>", unsafe_allow_html=True)
    st.markdown("---")
    
    # Sidebar - Filters
    with st.sidebar:
        st.image("https://img.icons8.com/color/96/000000/analytics.png", width=100)
        st.header("🎯 Bộ Lọc & Cài Đặt")
        
        # Chọn ngành và quý
        years = sorted(ticker_df['YEAR'].unique(), reverse=True)
        selected_year = st.selectbox("📅 Năm", years, key='year_filter')
        
        quarters_in_year = sorted(ticker_df[ticker_df['YEAR'] == selected_year]['QUARTER'].unique(), reverse=True)
        selected_quarter = st.selectbox("📊 Quý", quarters_in_year, key='quarter_filter')
        
        st.markdown("---")
        
        # Thống kê nhanh
        current_data = ticker_df[
            (ticker_df['YEAR'] == selected_year) & 
            (ticker_df['QUARTER'] == selected_quarter)
        ]
        
        st.subheader("📊 Thống Kê Nhanh")
        
        if not current_data.empty:
            # Đếm theo loại hình
            cal_group_counts = current_data['CAL_GROUP'].value_counts()
            
            st.metric("🏢 Doanh nghiệp", f"{cal_group_counts.get('company', 0):,}")
            st.metric("🏦 Ngân hàng", f"{cal_group_counts.get('bank', 0):,}")
            st.metric("📊 Chứng khoán", f"{cal_group_counts.get('security', 0):,}")
            st.metric("📈 Tổng cộng", f"{len(current_data):,}")
        
        st.markdown("---")
        
        # Cài đặt hiển thị
        st.subheader("⚙️ Tùy Chỉnh")
        show_advanced = st.checkbox("Hiển thị chỉ số nâng cao", value=True)
        chart_theme = st.selectbox("Theme biểu đồ", ["plotly", "plotly_white", "plotly_dark"], index=1)
    
    # Tạo tabs chính
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "🏠 Tổng Quan",
        "🏭 Phân Tích Ngành", 
        "🔍 Chi Tiết Cổ Phiếu",
        "🏦 Ngân Hàng",
        "📊 Chứng Khoán",
        "🎯 Stock Screener"
    ])
    
    # =====================================================
    # TAB 1: TỔNG QUAN THỊ TRƯỜNG (Nâng cấp với nhiều charts hơn)
    # =====================================================
    with tab1:
        st.header("🏠 Tổng Quan Thị Trường & Phân Bổ")
        
        current_market = market_df[
            (market_df['YEAR'] == selected_year) & 
            (market_df['QUARTER'] == selected_quarter)
        ]
        
        if not current_market.empty:
            market_data = current_market.iloc[0]
            
            # Row 1: Key Metrics
            st.subheader("📊 Chỉ Số Chính")
            col1, col2, col3, col4, col5 = st.columns(5)
            
            with col1:
                market_cap = market_data.get('MARKET_CAP_HT', 0) / 1e15
                growth_qoq = market_data.get('MARKET_CAP_HT_GQOQ', 0)
                st.metric(
                    "Vốn hóa TT",
                    f"{market_cap:.2f}K tỷ",
                    f"{growth_qoq:.2f}%",
                    delta_color="normal"
                )
            
            with col2:
                pe_ratio = market_data.get('PE_EOQ', 0)
                st.metric("P/E Cuối quý", f"{pe_ratio:.2f}")
            
            with col3:
                pb_ratio = market_data.get('PB_EOQ', 0)
                st.metric("P/B Cuối quý", f"{pb_ratio:.2f}")
            
            with col4:
                roe = market_data.get('ROAE', 0) * 100
                st.metric("ROE TB", f"{roe:.2f}%")
            
            with col5:
                total_companies = market_data.get('NUMBER', 0)
                st.metric("Số công ty", f"{total_companies:,}")
            
            st.markdown("---")
            
            # Row 2: Phân bổ theo loại hình
            st.subheader("🎯 Phân Bổ Thị Trường Theo Loại Hình")
            
            current_tickers = ticker_df[
                (ticker_df['YEAR'] == selected_year) & 
                (ticker_df['QUARTER'] == selected_quarter)
            ]
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                # Pie chart - Số lượng công ty
                cal_group_counts = current_tickers['CAL_GROUP'].value_counts()
                
                fig = px.pie(
                    values=cal_group_counts.values,
                    names=['Doanh nghiệp' if x=='company' else 'Ngân hàng' if x=='bank' else 'Chứng khoán' 
                           for x in cal_group_counts.index],
                    title='Phân bổ số lượng công ty',
                    color_discrete_sequence=['#667eea', '#f5576c', '#4facfe']
                )
                fig.update_traces(textposition='inside', textinfo='percent+label')
                fig.update_layout(height=350, template=chart_theme)
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Pie chart - Vốn hóa
                market_cap_by_type = current_tickers.groupby('CAL_GROUP')['MARKET_CAP_HT'].sum()
                
                fig = px.pie(
                    values=market_cap_by_type.values,
                    names=['Doanh nghiệp' if x=='company' else 'Ngân hàng' if x=='bank' else 'Chứng khoán' 
                           for x in market_cap_by_type.index],
                    title='Phân bổ vốn hóa thị trường',
                    color_discrete_sequence=['#667eea', '#f5576c', '#4facfe']
                )
                fig.update_traces(textposition='inside', textinfo='percent+label')
                fig.update_layout(height=350, template=chart_theme)
                st.plotly_chart(fig, use_container_width=True)
            
            with col3:
                # Bar chart - ROE trung bình theo loại
                roe_by_type = current_tickers.groupby('CAL_GROUP')['ROAE'].mean() * 100
                
                fig = go.Figure(data=[
                    go.Bar(
                        x=['Doanh nghiệp' if x=='company' else 'Ngân hàng' if x=='bank' else 'Chứng khoán' 
                           for x in roe_by_type.index],
                        y=roe_by_type.values,
                        marker_color=['#667eea', '#f5576c', '#4facfe'],
                        text=[f"{v:.2f}%" for v in roe_by_type.values],
                        textposition='auto',
                    )
                ])
                fig.update_layout(
                    title='ROE trung bình theo loại hình',
                    yaxis_title='ROE (%)',
                    height=350,
                    template=chart_theme
                )
                st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("---")
            
            # Row 3: Xu hướng thị trường
            st.subheader("📈 Xu Hướng Thị Trường (3 năm gần nhất)")
            
            market_trend = market_df[market_df['YEAR'] >= selected_year - 2].sort_values(['YEAR', 'QUARTER'])
            
            if not market_trend.empty:
                col1, col2 = st.columns(2)
                
                with col1:
                    # Multiple metrics on one chart
                    fig = make_subplots(
                        rows=2, cols=1,
                        subplot_titles=('Vốn hóa thị trường (Nghìn tỷ)', 'P/E & P/B Ratio'),
                        vertical_spacing=0.15
                    )
                    
                    # Vốn hóa
                    fig.add_trace(
                        go.Scatter(
                            x=market_trend['KEY'],
                            y=market_trend['MARKET_CAP_HT'] / 1e15,
                            name='Vốn hóa',
                            line=dict(color='#667eea', width=3),
                            fill='tozeroy',
                            fillcolor='rgba(102, 126, 234, 0.2)'
                        ),
                        row=1, col=1
                    )
                    
                    # P/E và P/B
                    fig.add_trace(
                        go.Scatter(
                            x=market_trend['KEY'],
                            y=market_trend['PE_EOQ'],
                            name='P/E',
                            line=dict(color='#f5576c', width=2)
                        ),
                        row=2, col=1
                    )
                    
                    fig.add_trace(
                        go.Scatter(
                            x=market_trend['KEY'],
                            y=market_trend['PB_EOQ'],
                            name='P/B',
                            line=dict(color='#4facfe', width=2)
                        ),
                        row=2, col=1
                    )
                    
                    fig.update_layout(height=600, hovermode='x unified', template=chart_theme)
                    fig.update_xaxes(title_text="Kỳ", row=2, col=1)
                    fig.update_yaxes(title_text="Nghìn tỷ VNĐ", row=1, col=1)
                    fig.update_yaxes(title_text="Ratio", row=2, col=1)
                    
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    # Profitability metrics
                    fig = go.Figure()
                    
                    fig.add_trace(go.Scatter(
                        x=market_trend['KEY'],
                        y=market_trend['ROAE']*100,
                        name='ROE',
                        line=dict(color='#667eea', width=2.5),
                        mode='lines+markers'
                    ))
                    
                    fig.add_trace(go.Scatter(
                        x=market_trend['KEY'],
                        y=market_trend['ROAA']*100,
                        name='ROA',
                        line=dict(color='#f5576c', width=2.5),
                        mode='lines+markers'
                    ))
                    
                    fig.add_trace(go.Scatter(
                        x=market_trend['KEY'],
                        y=market_trend['ROIC']*100,
                        name='ROIC',
                        line=dict(color='#4facfe', width=2.5),
                        mode='lines+markers'
                    ))
                    
                    fig.update_layout(
                        title="Chỉ Số Sinh Lời (%)",
                        xaxis_title="Kỳ",
                        yaxis_title="Tỷ suất (%)",
                        height=300,
                        hovermode='x unified',
                        template=chart_theme,
                        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Margin metrics
                    fig = go.Figure()
                    
                    fig.add_trace(go.Scatter(
                        x=market_trend['KEY'],
                        y=market_trend['GROSS_MARGIN_12M']*100,
                        name='Biên gộp',
                        line=dict(color='#667eea', width=2),
                        mode='lines+markers'
                    ))
                    
                    fig.add_trace(go.Scatter(
                        x=market_trend['KEY'],
                        y=market_trend['OPERATING_MARGIN_12M']*100,
                        name='Biên HĐ',
                        line=dict(color='#f5576c', width=2),
                        mode='lines+markers'
                    ))
                    
                    fig.add_trace(go.Scatter(
                        x=market_trend['KEY'],
                        y=market_trend['NET_INCOME_MARGIN_12M']*100,
                        name='Biên ròng',
                        line=dict(color='#4facfe', width=2),
                        mode='lines+markers'
                    ))
                    
                    fig.update_layout(
                        title="Biên Lợi Nhuận (%)",
                        xaxis_title="Kỳ",
                        yaxis_title="Biên lợi nhuận (%)",
                        height=300,
                        hovermode='x unified',
                        template=chart_theme,
                        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
    
    # =====================================================
    # TAB 2: PHÂN TÍCH NGÀNH (Thêm nhiều charts)
    # =====================================================
    with tab2:
        st.header("🏭 Phân Tích Toàn Diện Theo Ngành")
        
        current_industries = industry_df[
            (industry_df['YEAR'] == selected_year) & 
            (industry_df['QUARTER'] == selected_quarter)
        ].copy()
        
        if not current_industries.empty:
            # Overview metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Số ngành", f"{len(current_industries)}")
            with col2:
                avg_pe = current_industries[current_industries['PE_EOQ'] > 0]['PE_EOQ'].mean()
                st.metric("P/E TB", f"{avg_pe:.2f}")
            with col3:
                avg_roe = current_industries['ROAE'].mean() * 100
                st.metric("ROE TB", f"{avg_roe:.2f}%")
            with col4:
                total_cap = current_industries['MARKET_CAP_HT'].sum() / 1e15
                st.metric("Tổng VH", f"{total_cap:.2f}K tỷ")
            
            st.markdown("---")
            
            # Row 1: Top performers
            st.subheader("🏆 Top Ngành Theo Các Tiêu Chí")
            
            tab2_1, tab2_2, tab2_3, tab2_4 = st.tabs([
                "💰 Vốn Hóa",
                "📈 ROE",
                "💵 P/E Thấp",
                "📊 Tăng Trưởng"
            ])
            
            with tab2_1:
                top_cap = current_industries.nlargest(15, 'MARKET_CAP_HT')
                
                fig = px.bar(
                    top_cap,
                    y='SYMBOL',
                    x='MARKET_CAP_HT',
                    orientation='h',
                    title='Top 15 Ngành Theo Vốn Hóa',
                    labels={'MARKET_CAP_HT': 'Vốn hóa (VNĐ)', 'SYMBOL': 'Ngành'},
                    color='MARKET_CAP_HT',
                    color_continuous_scale='Blues',
                    text='MARKET_CAP_HT'
                )
                fig.update_traces(texttemplate='%{text:.2s}', textposition='outside')
                fig.update_layout(height=500, showlegend=False, template=chart_theme)
                st.plotly_chart(fig, use_container_width=True)
            
            with tab2_2:
                top_roe = current_industries[current_industries['ROAE'] > 0].nlargest(15, 'ROAE')
                
                fig = px.bar(
                    top_roe,
                    y='SYMBOL',
                    x='ROAE',
                    orientation='h',
                    title='Top 15 Ngành Theo ROE',
                    labels={'ROAE': 'ROE', 'SYMBOL': 'Ngành'},
                    color='ROAE',
                    color_continuous_scale='Greens'
                )
                fig.update_traces(texttemplate='%{x:.2%}', textposition='outside')
                fig.update_layout(height=500, showlegend=False, template=chart_theme)
                st.plotly_chart(fig, use_container_width=True)
            
            with tab2_3:
                low_pe = current_industries[current_industries['PE_EOQ'] > 0].nsmallest(15, 'PE_EOQ')
                
                fig = px.bar(
                    low_pe,
                    y='SYMBOL',
                    x='PE_EOQ',
                    orientation='h',
                    title='15 Ngành Có P/E Thấp Nhất',
                    labels={'PE_EOQ': 'P/E Ratio', 'SYMBOL': 'Ngành'},
                    color='PE_EOQ',
                    color_continuous_scale='Reds_r'
                )
                fig.update_traces(texttemplate='%{x:.2f}', textposition='outside')
                fig.update_layout(height=500, showlegend=False, template=chart_theme)
                st.plotly_chart(fig, use_container_width=True)
            
            with tab2_4:
                growth_industries = current_industries[current_industries['MARKET_CAP_HT_GYOY'].notna()]
                top_growth = growth_industries.nlargest(15, 'MARKET_CAP_HT_GYOY')
                
                fig = px.bar(
                    top_growth,
                    y='SYMBOL',
                    x='MARKET_CAP_HT_GYOY',
                    orientation='h',
                    title='15 Ngành Tăng Trưởng Vốn Hóa YoY',
                    labels={'MARKET_CAP_HT_GYOY': 'Tăng trưởng YoY (%)', 'SYMBOL': 'Ngành'},
                    color='MARKET_CAP_HT_GYOY',
                    color_continuous_scale='RdYlGn'
                )
                fig.update_traces(texttemplate='%{x:.2f}%', textposition='outside')
                fig.update_layout(height=500, showlegend=False, template=chart_theme)
                st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("---")
            
            # Row 2: Scatter plots analysis
            st.subheader("🔍 Phân Tích Ma Trận Ngành")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # ROE vs ROA
                valid_data = current_industries[
                    (current_industries['ROAE'] > 0) & 
                    (current_industries['ROAA'] > 0)
                ]
                
                fig = px.scatter(
                    valid_data,
                    x='ROAA',
                    y='ROAE',
                    size='MARKET_CAP_HT',
                    color='SYMBOL',
                    hover_name='SYMBOL',
                    title='Ma Trận ROE vs ROA (Bubble size = Vốn hóa)',
                    labels={'ROAE': 'ROE', 'ROAA': 'ROA'}
                )
                
                # Add reference lines
                fig.add_hline(y=valid_data['ROAE'].median(), line_dash="dash", 
                             line_color="gray", annotation_text="ROE median")
                fig.add_vline(x=valid_data['ROAA'].median(), line_dash="dash",
                             line_color="gray", annotation_text="ROA median")
                
                fig.update_layout(height=500, showlegend=False, template=chart_theme)
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # P/E vs ROE (value quadrant)
                valid_data = current_industries[
                    (current_industries['PE_EOQ'] > 0) &
                    (current_industries['PE_EOQ'] < 50) &
                    (current_industries['ROAE'] > 0)
                ]
                
                fig = px.scatter(
                    valid_data,
                    x='PE_EOQ',
                    y='ROAE',
                    size='MARKET_CAP_HT',
                    color='SYMBOL',
                    hover_name='SYMBOL',
                    title='Ma Trận Định Giá P/E vs ROE',
                    labels={'PE_EOQ': 'P/E Ratio', 'ROAE': 'ROE'}
                )
                
                # Add quadrant lines
                fig.add_hline(y=valid_data['ROAE'].median(), line_dash="dash",
                             line_color="gray", annotation_text="ROE median")
                fig.add_vline(x=valid_data['PE_EOQ'].median(), line_dash="dash",
                             line_color="gray", annotation_text="P/E median")
                
                # Add annotations for quadrants
                fig.add_annotation(x=valid_data['PE_EOQ'].quantile(0.75), 
                                  y=valid_data['ROAE'].quantile(0.75),
                                  text="Đắt & Tốt", showarrow=False,
                                  font=dict(size=12, color="green"))
                fig.add_annotation(x=valid_data['PE_EOQ'].quantile(0.25),
                                  y=valid_data['ROAE'].quantile(0.75),
                                  text="Rẻ & Tốt ⭐", showarrow=False,
                                  font=dict(size=14, color="darkgreen", family="Arial Black"))
                
                fig.update_layout(height=500, showlegend=False, template=chart_theme)
                st.plotly_chart(fig, use_container_width=True)
            
            # Row 3: Heatmap comparison
            st.subheader("🌡️ Bản Đồ Nhiệt So Sánh Ngành")
            
            # Select top industries by market cap for heatmap
            top_industries = current_industries.nlargest(20, 'MARKET_CAP_HT')
            
            # Select metrics for heatmap
            heatmap_metrics = ['PE_EOQ', 'PB_EOQ', 'ROAE', 'ROAA', 'ROIC',
                              'NET_INCOME_MARGIN_12M', 'DEBTS_RATIO', 'CURRENT_RATIO_Q']
            
            available_metrics = [m for m in heatmap_metrics if m in top_industries.columns]
            heatmap_data = top_industries[['SYMBOL'] + available_metrics].set_index('SYMBOL')
            
            # Normalize data for better visualization
            from sklearn.preprocessing import StandardScaler
            scaler = StandardScaler()
            heatmap_normalized = pd.DataFrame(
                scaler.fit_transform(heatmap_data.fillna(0)),
                index=heatmap_data.index,
                columns=heatmap_data.columns
            )
            
            fig = px.imshow(
                heatmap_normalized.T,
                labels=dict(x="Ngành", y="Chỉ số", color="Z-Score"),
                x=heatmap_normalized.index,
                y=heatmap_normalized.columns,
                color_continuous_scale='RdYlGn',
                aspect="auto",
                title="Bản đồ nhiệt so sánh chỉ số (chuẩn hóa)"
            )
            fig.update_layout(height=400, template=chart_theme)
            fig.update_xaxes(tickangle=45)
            
            st.plotly_chart(fig, use_container_width=True)
            
            st.caption("💡 Màu xanh = Tốt hơn trung bình, Màu đỏ = Kém hơn trung bình")
    
    # =====================================================
    # TAB 3: CHI TIẾT CỔ PHIẾU (Phân tích theo CAL_GROUP)
    # =====================================================
    with tab3:
        st.header("🔍 Phân Tích Chi Tiết Theo Loại Hình Doanh Nghiệp")
        
        # Select ticker
        col1, col2, col3 = st.columns([3, 1, 1])
        
        with col1:
            ticker_list = sorted(ticker_df['SYMBOL'].unique())
            selected_ticker = st.selectbox(
                "🔎 Tìm kiếm mã cổ phiếu",
                ticker_list,
                key='ticker_detail',
                help="Gõ để tìm kiếm nhanh"
            )
        
        with col2:
            # Quick navigation
            if st.button("⬅️ Mã trước"):
                current_idx = ticker_list.index(selected_ticker)
                if current_idx > 0:
                    selected_ticker = ticker_list[current_idx - 1]
                    st.rerun()
        
        with col3:
            ticker_df = ticker_df.dropna(subset=['LEVEL2_NAME_EN'])
            industry_list = sorted(ticker_df['LEVEL2_NAME_EN'].unique())
            selected_ticker = st.selectbox(
                "🔎 Tìm kiếm mã cổ phiếu",
                industry_list,
                key='industry_detail',
                help="Gõ để tìm kiếm nhanh"
            )
        
        if selected_ticker:
            # Get data for selected ticker
            ticker_data = ticker_df[ticker_df['SYMBOL'] == selected_ticker].sort_values(
                ['YEAR', 'QUARTER'], ascending=False
            )
            
            if not ticker_data.empty:
                current_data = ticker_data.iloc[0]
                cal_group = current_data.get('CAL_GROUP', 'company')
                
                # Header with company type badge
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown(f"## {selected_ticker}")
                    badge_html = get_company_type_badge(cal_group)
                    st.markdown(badge_html, unsafe_allow_html=True)
                    st.caption(f"Ngành: {current_data.get('LEVEL2_NAME_EN', 'N/A')}")
                
                with col2:
                    # Add to watchlist button (placeholder)
                    if st.button("⭐ Thêm vào danh sách theo dõi"):
                        st.success("Đã thêm vào watchlist!")
                
                st.markdown("---")
                
                # Basic info row
                col1, col2, col3, col4, col5 = st.columns(5)
                
                with col1:
                    market_cap = current_data.get('MARKET_CAP_HT', 0) / 1e12
                    st.metric("Vốn hóa (Nghìn tỷ)", f"{market_cap:.2f}")
                
                with col2:
                    close_price = current_data.get('CLOSE_PRICE', 0) / 1000
                    price_change = current_data.get('CLOSE_PRICE_GQOQ', 0)
                    st.metric("Giá (k)", f"{close_price:.1f}", f"{price_change:.2f}%")
                
                with col3:
                    eps = current_data.get('EPS_12M', 0)
                    st.metric("EPS (12M)", f"{eps:,.0f}")
                
                with col4:
                    bvps = current_data.get('BVPS', 0)
                    st.metric("BVPS", f"{bvps:,.0f}")
                
                with col5:
                    outs_shares = current_data.get('OUTS_SHARES', 0) / 1e6
                    st.metric("CP lưu hành (M)", f"{outs_shares:.1f}")
                
                st.markdown("---")
                
                # Dynamic tabs based on company type
                if cal_group == 'bank':
                    # TABS FOR BANK
                    detail_tabs = st.tabs([
                        "🏦 Chỉ Số Ngân Hàng",
                        "📈 Định Giá",
                        "💰 Sinh Lời",
                        "📊 Tài Chính",
                        "📉 Xu Hướng",
                        "🔬 Phân Tích Sâu"
                    ])
                    
                    with detail_tabs[0]:
                        st.subheader("🏦 Các Chỉ Số Đặc Trưng Ngân Hàng")
                        
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.write("**📊 Chất Lượng Tài Sản**")
                            
                            npl = current_data.get('NPL_Q', 0) * 100
                            st.metric("NPL Ratio", f"{npl:.2f}%",
                                     help="Tỷ lệ nợ xấu. < 3% là tốt")
                            
                            llr = current_data.get('LLR_Q', 0) * 100
                            st.metric("LLR", f"{llr:.2f}%",
                                     help="Tỷ lệ dự phòng rủi ro")
                            
                            # Gauge chart for NPL
                            fig = create_gauge_chart(npl, "NPL Ratio (%)", 0, 10, [2, 5])
                            st.plotly_chart(fig, use_container_width=True)
                        
                        with col2:
                            st.write("**💰 Sinh Lời & Hiệu Quả**")
                            
                            nim = current_data.get('NIM_12M', 0) * 100
                            st.metric("NIM (12M)", f"{nim:.2f}%",
                                     help="Biên lãi suất thuần. > 3% là tốt")
                            
                            cir = current_data.get('CIR_12M', 0) * 100
                            st.metric("CIR (12M)", f"{cir:.2f}%",
                                     help="Tỷ lệ chi phí/thu nhập. < 45% là tốt")
                            
                            # Gauge chart for NIM
                            fig = create_gauge_chart(nim, "NIM (%)", 0, 6, [2, 4])
                            st.plotly_chart(fig, use_container_width=True)
                        
                        with col3:
                            st.write("**📈 Tăng Trưởng & Thanh Khoản**")
                            
                            ldr = current_data.get('LDR_12M', 0) * 100
                            st.metric("LDR (12M)", f"{ldr:.2f}%",
                                     help="Tỷ lệ cho vay/huy động. 70-85% là lý tưởng")
                            
                            casa = current_data.get('CASA_12M', 0) * 100
                            st.metric("CASA (12M)", f"{casa:.2f}%",
                                     help="Tỷ lệ tiền gửi không kỳ hạn. Cao là tốt")
                            
                            # Gauge chart for LDR
                            fig = create_gauge_chart(ldr, "LDR (%)", 0, 100, [70, 85])
                            st.plotly_chart(fig, use_container_width=True)
                        
                        st.markdown("---")
                        
                        # Additional bank metrics
                        st.write("**📋 Chi Tiết Thêm**")
                        
                        col1, col2, col3, col4 = st.columns(4)
                        
                        with col1:
                            leverage_ae = current_data.get('LEVERAGE_AE_12M', 0)
                            st.metric("Đòn bẩy (AE)", f"{leverage_ae:.2f}")
                        
                        with col2:
                            nii_toi = current_data.get('NII_TOI_12M', 0) * 100
                            st.metric("NII/TOI", f"{nii_toi:.2f}%")
                        
                        with col3:
                            earning_assets = current_data.get('EARNING_ASSETS', 0) / 1e12
                            st.metric("TS sinh lời (Nghìn tỷ)", f"{earning_assets:.2f}")
                        
                        with col4:
                            bad_loan = current_data.get('BAD_LOAN', 0) / 1e9
                            st.metric("Nợ xấu (tỷ)", f"{bad_loan:.2f}")
                
                elif cal_group == 'security':
                    # TABS FOR SECURITIES
                    detail_tabs = st.tabs([
                        "📊 Chỉ Số Chứng Khoán",
                        "📈 Định Giá",
                        "💰 Sinh Lời",
                        "📊 Tài Chính",
                        "📉 Xu Hướng",
                        "🔬 Phân Tích Sâu"
                    ])
                    
                    with detail_tabs[0]:
                        st.subheader("📊 Các Chỉ Số Đặc Trưng Công Ty Chứng Khoán")
                        
                        # Revenue breakdown
                        st.write("**💰 Cơ Cấu Doanh Thu**")
                        
                        rev_brokerage = current_data.get('REV_FR_BROKERAGE_SERVICES', 0)
                        rev_margin = current_data.get('REV_FR_MARGIN_SERVICES', 0)
                        rev_proprietary = current_data.get('REV_FR_PROPRIETARY_TRADING', 0)
                        rev_underwriting = current_data.get('REV_FR_UNDERWRITING_SERVICES', 0)
                        rev_custodian = current_data.get('REV_FR_SECURITIES_CUSTODIAN_SERVICES', 0)
                        rev_advisory = current_data.get('REV_FR_SECURITIES_INVESTMENTS_ADVISORY_SERVICES', 0)
                        
                        revenue_data = {
                            'Dịch vụ': ['Môi giới', 'Margin', 'Tự doanh', 'Bảo lãnh', 'Lưu ký', 'Tư vấn'],
                            'Doanh thu': [rev_brokerage, rev_margin, rev_proprietary, 
                                        rev_underwriting, rev_custodian, rev_advisory]
                        }
                        
                        rev_df = pd.DataFrame(revenue_data)
                        rev_df = rev_df[rev_df['Doanh thu'] != 0]
                        
                        if not rev_df.empty:
                            col1, col2 = st.columns([1, 1])
                            
                            with col1:
                                # Pie chart
                                fig = px.pie(
                                    rev_df,
                                    values='Doanh thu',
                                    names='Dịch vụ',
                                    title='Cơ cấu doanh thu theo dịch vụ',
                                    color_discrete_sequence=px.colors.qualitative.Set3
                                )
                                fig.update_traces(textposition='inside', textinfo='percent+label')
                                fig.update_layout(height=400, template=chart_theme)
                                st.plotly_chart(fig, use_container_width=True)
                            
                            with col2:
                                # Bar chart
                                fig = px.bar(
                                    rev_df.sort_values('Doanh thu', ascending=True),
                                    x='Doanh thu',
                                    y='Dịch vụ',
                                    orientation='h',
                                    title='Doanh thu theo từng dịch vụ (VNĐ)',
                                    text='Doanh thu'
                                )
                                fig.update_traces(texttemplate='%{text:.2s}', textposition='outside')
                                fig.update_layout(height=400, template=chart_theme)
                                st.plotly_chart(fig, use_container_width=True)
                        
                        st.markdown("---")
                        
                        # Components
                        st.write("**📊 Các Thành Phần Đóng Góp**")
                        
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            brokerage_comp = current_data.get('BROKERAGE_COMPONENT', 0) * 100
                            st.metric("Thành phần Môi giới", f"{brokerage_comp:.2f}%")
                        
                        with col2:
                            margin_comp = current_data.get('MARGIN_COMPONENT', 0) * 100
                            st.metric("Thành phần Margin", f"{margin_comp:.2f}%")
                        
                        with col3:
                            prop_comp = current_data.get('PROPRIETARY_TRADING_COMPONENT', 0) * 100
                            st.metric("Thành phần Tự doanh", f"{prop_comp:.2f}%")
                        
                        # Margin interest rate
                        st.markdown("---")
                        st.write("**💵 Lãi Suất Margin**")
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            margin_rate_q = current_data.get('MARGIN_INTEREST_RATE', 0) * 100
                            st.metric("Lãi suất Margin (Quý)", f"{margin_rate_q:.2f}%")
                        
                        with col2:
                            margin_rate_12m = current_data.get('MARGIN_INTEREST_RATE_12M', 0) * 100
                            st.metric("Lãi suất Margin (12M)", f"{margin_rate_12m:.2f}%")
                
                else:
                    # TABS FOR REGULAR COMPANY
                    detail_tabs = st.tabs([
                        "📈 Định Giá",
                        "💰 Sinh Lời",
                        "📊 Tài Chính",
                        "💵 Dòng Tiền",
                        "📉 Xu Hướng",
                        "🔬 Phân Tích Sâu"
                    ])
                
                # Common tabs for all types
                with detail_tabs[-5] if cal_group == 'bank' or cal_group == 'security' else detail_tabs[0]:
                    st.subheader("📈 Các Chỉ Số Định Giá")
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.write("**💰 Định giá cơ bản**")
                        
                        pe = current_data.get('PE_EOQ', 0)
                        st.metric("P/E", f"{pe:.2f}")
                        
                        pb = current_data.get('PB_EOQ', 0)
                        st.metric("P/B", f"{pb:.2f}")
                        
                        # Gauge for P/E
                        fig = create_gauge_chart(min(pe, 50), "P/E Ratio", 0, 50, [15, 25])
                        st.plotly_chart(fig, use_container_width=True)
                    
                    with col2:
                        st.write("**📊 Định giá nâng cao**")
                        
                        ev_ebitda = current_data.get('EV_EBITDA', 0)
                        st.metric("EV/EBITDA", f"{ev_ebitda:.2f}")
                        
                        p_fcf = current_data.get('P_FCF_EOQ', 0)
                        st.metric("P/FCF", f"{p_fcf:.2f}")
                        
                        p_cfo = current_data.get('P_CFO_EOQ', 0)
                        st.metric("P/CFO", f"{p_cfo:.2f}")
                    
                    with col3:
                        st.write("**💵 Cổ tức & Giá trị sổ sách**")
                        
                        div_yield = current_data.get('DIVIDEND_YIELD_HT', 0) * 100
                        st.metric("Dividend Yield", f"{div_yield:.2f}%")
                        
                        p_bvps = current_data.get('P_NCAVPS_EOQ', 0)
                        st.metric("P/NCAVPS", f"{p_bvps:.2f}")
                        
                        # Gauge for Dividend Yield
                        fig = create_gauge_chart(min(div_yield, 10), "Dividend Yield (%)", 0, 10, [3, 6])
                        st.plotly_chart(fig, use_container_width=True)
                
                with detail_tabs[-4] if cal_group == 'bank' or cal_group == 'security' else detail_tabs[1]:
                    st.subheader("💰 Các Chỉ Số Sinh Lời")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write("**📊 Tỷ suất sinh lời**")
                        
                        roe = current_data.get('ROAE', 0) * 100
                        st.metric("ROE", f"{roe:.2f}%")
                        
                        roa = current_data.get('ROAA', 0) * 100
                        st.metric("ROA", f"{roa:.2f}%")
                        
                        roic = current_data.get('ROIC', 0) * 100
                        st.metric("ROIC", f"{roic:.2f}%")
                        
                        roce = current_data.get('ROCE', 0) * 100
                        st.metric("ROCE", f"{roce:.2f}%")
                        
                        # Gauge charts
                        col1_1, col1_2 = st.columns(2)
                        
                        with col1_1:
                            fig = create_gauge_chart(min(roe, 50), "ROE (%)", 0, 50, [10, 20])
                            st.plotly_chart(fig, use_container_width=True)
                        
                        with col1_2:
                            fig = create_gauge_chart(min(roa, 30), "ROA (%)", 0, 30, [5, 10])
                            st.plotly_chart(fig, use_container_width=True)
                    
                    with col2:
                        st.write("**💵 Biên lợi nhuận**")
                        
                        gross_margin = current_data.get('GROSS_MARGIN_12M', 0) * 100
                        operating_margin = current_data.get('OPERATING_MARGIN_12M', 0) * 100
                        net_margin = current_data.get('NET_INCOME_MARGIN_12M', 0) * 100
                        
                        # Create waterfall-like chart
                        margins = ['Biên gộp', 'Biên HĐ', 'Biên ròng']
                        values = [gross_margin, operating_margin, net_margin]
                        
                        fig = go.Figure()
                        
                        fig.add_trace(go.Bar(
                            x=margins,
                            y=values,
                            text=[f"{v:.2f}%" for v in values],
                            textposition='auto',
                            marker_color=['#667eea', '#f5576c', '#4facfe']
                        ))
                        
                        fig.update_layout(
                            title="Các Biên Lợi Nhuận (12M)",
                            yaxis_title="Biên lợi nhuận (%)",
                            height=400,
                            template=chart_theme
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
                
                with detail_tabs[-3] if cal_group == 'bank' or cal_group == 'security' else detail_tabs[2]:
                    st.subheader("📊 Sức Khỏe Tài Chính")
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.write("**💧 Thanh khoản**")
                        
                        current_ratio = current_data.get('CURRENT_RATIO_Q', 0)
                        st.metric("Current Ratio", f"{current_ratio:.2f}")
                        
                        quick_ratio = current_data.get('QUICK_RATIO_Q', 0)
                        st.metric("Quick Ratio", f"{quick_ratio:.2f}")
                        
                        # Gauge
                        fig = create_gauge_chart(min(current_ratio, 5), "Current Ratio", 0, 5, [1.5, 2.5])
                        st.plotly_chart(fig, use_container_width=True)
                    
                    with col2:
                        st.write("**⚖️ Đòn bẩy**")
                        
                        debt_ratio = current_data.get('DEBTS_RATIO', 0)
                        st.metric("Debt Ratio", f"{debt_ratio:.2f}")
                        
                        leverage = current_data.get('LEVERAGE', 0)
                        st.metric("Leverage", f"{leverage:.2f}")
                        
                        # Gauge (inverse for debt - lower is better)
                        fig = create_gauge_chart(debt_ratio * 100, "Debt Ratio (%)", 0, 100, [30, 60])
                        st.plotly_chart(fig, use_container_width=True)
                    
                    with col3:
                        st.write("**🛡️ Rủi ro**")
                        
                        z_score = current_data.get('Z_SCORE', 0)
                        
                        # Z-Score assessment
                        if z_score > 2.99:
                            z_color = "normal"
                            z_status = "🟢 An toàn"
                        elif z_score > 1.81:
                            z_color = "off"
                            z_status = "🟡 Cảnh báo"
                        else:
                            z_color = "inverse"
                            z_status = "🔴 Rủi ro cao"
                        
                        st.metric("Z-Score", f"{z_score:.2f}", z_status, delta_color=z_color)
                        
                        st.caption("**Đánh giá:**")
                        st.caption("• > 2.99: An toàn")
                        st.caption("• 1.81-2.99: Cảnh báo")
                        st.caption("• < 1.81: Rủi ro phá sản")
                        
                        # Gauge
                        fig = create_gauge_chart(min(z_score, 5), "Z-Score", 0, 5, [1.81, 2.99])
                        st.plotly_chart(fig, use_container_width=True)
                
                # Cash Flow tab (only for regular companies)
                if cal_group == 'company':
                    with detail_tabs[3]:
                        st.subheader("💵 Phân Tích Dòng Tiền")
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.write("**📊 Các loại dòng tiền (12M)**")
                            
                            cfo = current_data.get('CFO_12M', 0) / 1e9
                            cfi = current_data.get('CFI_12M', 0) / 1e9
                            cff = current_data.get('CFF_12M', 0) / 1e9
                            fcf = current_data.get('FCF_12M', 0) / 1e9
                            
                            cash_flow_data = pd.DataFrame({
                                'Loại': ['CFO', 'CFI', 'CFF', 'FCF'],
                                'Giá trị': [cfo, cfi, cff, fcf]
                            })
                            
                            fig = go.Figure()
                            
                            colors = ['green' if x > 0 else 'red' for x in cash_flow_data['Giá trị']]
                            
                            fig.add_trace(go.Bar(
                                x=cash_flow_data['Loại'],
                                y=cash_flow_data['Giá trị'],
                                marker_color=colors,
                                text=[f"{v:.2f}B" for v in cash_flow_data['Giá trị']],
                                textposition='auto'
                            ))
                            
                            fig.update_layout(
                                title="Dòng tiền 12M (tỷ VNĐ)",
                                yaxis_title="Dòng tiền (tỷ)",
                                height=400,
                                template=chart_theme
                            )
                            
                            st.plotly_chart(fig, use_container_width=True)
                        
                        with col2:
                            st.write("**💰 Chỉ số dòng tiền**")
                            
                            fcf_per_share = current_data.get('FCF_PER_SHARE_12M', 0)
                            st.metric("FCF/Share (12M)", f"{fcf_per_share:,.0f}")
                            
                            ocf_per_share = current_data.get('OCF_PER_SHARE_12M', 0)
                            st.metric("OCF/Share (12M)", f"{ocf_per_share:,.0f}")
                            
                            fcf_margin = current_data.get('FCF_PER_NET_SALES_12M', 0) * 100
                            st.metric("FCF Margin (12M)", f"{fcf_margin:.2f}%")
                            
                            cfo_ebitda = current_data.get('CFO_PER_EBITDA_12M', 0) * 100
                            st.metric("CFO/EBITDA (12M)", f"{cfo_ebitda:.2f}%")
                
                # Trend tab
                with detail_tabs[-2]:
                    st.subheader("📉 Xu Hướng Theo Thời Gian")
                    
                    # Get historical data (last 3 years)
                    historical = ticker_df[
                        (ticker_df['SYMBOL'] == selected_ticker) &
                        (ticker_df['YEAR'] >= selected_year - 2)
                    ].sort_values(['YEAR', 'QUARTER'])
                    
                    if len(historical) > 1:
                        # Revenue & Profit
                        st.write("**📊 Doanh Thu & Lợi Nhuận**")
                        
                        fig = make_subplots(specs=[[{"secondary_y": True}]])
                        
                        fig.add_trace(
                            go.Bar(
                                x=historical['KEY'],
                                y=historical['NET_SALES_12M'] / 1e9,
                                name='Doanh thu',
                                marker_color='lightblue'
                            ),
                            secondary_y=False
                        )
                        
                        fig.add_trace(
                            go.Scatter(
                                x=historical['KEY'],
                                y=historical['NET_INCOME_12M'] / 1e9,
                                name='Lợi nhuận',
                                line=dict(color='red', width=3),
                                mode='lines+markers'
                            ),
                            secondary_y=True
                        )
                        
                        fig.update_layout(
                            title="Doanh thu & Lợi nhuận 12M (tỷ VNĐ)",
                            hovermode='x unified',
                            height=400,
                            template=chart_theme,
                            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                        )
                        fig.update_yaxes(title_text="Doanh thu (tỷ)", secondary_y=False)
                        fig.update_yaxes(title_text="Lợi nhuận (tỷ)", secondary_y=True)
                        
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Profitability ratios
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.write("**💰 Tỷ suất sinh lời**")
                            
                            fig = go.Figure()
                            
                            fig.add_trace(go.Scatter(
                                x=historical['KEY'],
                                y=historical['ROAE'] * 100,
                                name='ROE',
                                line=dict(color='#667eea', width=2.5),
                                mode='lines+markers'
                            ))
                            
                            fig.add_trace(go.Scatter(
                                x=historical['KEY'],
                                y=historical['ROAA'] * 100,
                                name='ROA',
                                line=dict(color='#f5576c', width=2.5),
                                mode='lines+markers'
                            ))
                            
                            fig.add_trace(go.Scatter(
                                x=historical['KEY'],
                                y=historical['ROIC'] * 100,
                                name='ROIC',
                                line=dict(color='#4facfe', width=2.5),
                                mode='lines+markers'
                            ))
                            
                            fig.update_layout(
                                title="Chỉ số sinh lời (%)",
                                yaxis_title="Tỷ suất (%)",
                                hovermode='x unified',
                                height=400,
                                template=chart_theme,
                                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                            )
                            
                            st.plotly_chart(fig, use_container_width=True)
                        
                        with col2:
                            st.write("**💵 Biên lợi nhuận**")
                            
                            fig = go.Figure()
                            
                            fig.add_trace(go.Scatter(
                                x=historical['KEY'],
                                y=historical['GROSS_MARGIN_12M'] * 100,
                                name='Biên gộp',
                                line=dict(color='#667eea', width=2),
                                mode='lines+markers',
                                fill='tonexty'
                            ))
                            
                            fig.add_trace(go.Scatter(
                                x=historical['KEY'],
                                y=historical['OPERATING_MARGIN_12M'] * 100,
                                name='Biên HĐ',
                                line=dict(color='#f5576c', width=2),
                                mode='lines+markers',
                                fill='tonexty'
                            ))
                            
                            fig.add_trace(go.Scatter(
                                x=historical['KEY'],
                                y=historical['NET_INCOME_MARGIN_12M'] * 100,
                                name='Biên ròng',
                                line=dict(color='#4facfe', width=2),
                                mode='lines+markers'
                            ))
                            
                            fig.update_layout(
                                title="Biên lợi nhuận (%)",
                                yaxis_title="Biên (%)",
                                hovermode='x unified',
                                height=400,
                                template=chart_theme,
                                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                            )
                            
                            st.plotly_chart(fig, use_container_width=True)
                        
                        # Price trend
                        st.write("**📈 Xu hướng giá & vốn hóa**")
                        
                        fig = make_subplots(specs=[[{"secondary_y": True}]])
                        
                        fig.add_trace(
                            go.Scatter(
                                x=historical['KEY'],
                                y=historical['CLOSE_PRICE'] / 1000,
                                name='Giá (k)',
                                line=dict(color='#667eea', width=3),
                                mode='lines+markers'
                            ),
                            secondary_y=False
                        )
                        
                        fig.add_trace(
                            go.Scatter(
                                x=historical['KEY'],
                                y=historical['MARKET_CAP_HT'] / 1e12,
                                name='Vốn hóa (Nghìn tỷ)',
                                line=dict(color='#f5576c', width=3),
                                mode='lines+markers'
                            ),
                            secondary_y=True
                        )
                        
                        fig.update_layout(
                            title="Giá & Vốn hóa",
                            hovermode='x unified',
                            height=400,
                            template=chart_theme
                        )
                        fig.update_yaxes(title_text="Giá (k)", secondary_y=False)
                        fig.update_yaxes(title_text="Vốn hóa (Nghìn tỷ)", secondary_y=True)
                        
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("Không đủ dữ liệu lịch sử để hiển thị xu hướng")
                
                # Deep analysis tab
                with detail_tabs[-1]:
                    st.subheader("🔬 Phân Tích Chuyên Sâu")
                    
                    # DuPont Analysis
                    st.write("**📊 Phân Tích DuPont ROE**")
                    
                    st.markdown("""
                    ROE được phân tích thành 3 thành phần chính:
                    - **Tax Burden**: (Net Income / EBT) - Gánh nặng thuế
                    - **Interest Burden**: (EBT / EBIT) - Gánh nặng lãi vay
                    - **Profit Margin**: (EBIT / Revenue) - Biên lợi nhuận
                    - **Assets Turnover**: (Revenue / Assets) - Vòng quay tài sản
                    - **Leverage**: (Assets / Equity) - Đòn bẩy tài chính
                    """)
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        du1 = current_data.get('DU1_TAX_BURDEN', 0)
                        du2 = current_data.get('DU2_INTEREST_BURDEN', 0)
                        du3 = current_data.get('DU3_PROFIT_MARGIN', 0)
                        du4 = current_data.get('DU4_ASSETS_TURNOVER', 0)
                        du5 = current_data.get('DU5_LEVERAGE', 0)
                        
                        dupont_data = pd.DataFrame({
                            'Thành phần': ['Tax\nBurden', 'Interest\nBurden', 'Profit\nMargin', 
                                          'Assets\nTurnover', 'Leverage'],
                            'Giá trị': [du1, du2, du3, du4, du5]
                        })
                        
                        fig = go.Figure(data=[
                            go.Bar(
                                x=dupont_data['Thành phần'],
                                y=dupont_data['Giá trị'],
                                marker_color=['#667eea', '#764ba2', '#f5576c', '#ff6b6b', '#4facfe'],
                                text=[f"{v:.3f}" for v in dupont_data['Giá trị']],
                                textposition='auto'
                            )
                        ])
                        
                        fig.update_layout(
                            title="Các thành phần DuPont",
                            yaxis_title="Giá trị",
                            height=400,
                            template=chart_theme
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Calculate ROE from DuPont
                        roe_dupont = du1 * du2 * du3 * du4 * du5
                        roe_actual = current_data.get('ROAE', 0)
                        
                        st.info(f"**ROE từ DuPont**: {roe_dupont*100:.2f}%")
                        st.info(f"**ROE thực tế**: {roe_actual*100:.2f}%")
                    
                    with col2:
                        # Waterfall chart for ROE decomposition
                        measures = ["relative"] * 5
                        
                        fig = go.Figure(go.Waterfall(
                            name="ROE", orientation="v",
                            measure=measures,
                            x=dupont_data['Thành phần'],
                            textposition="outside",
                            text=[f"{v:.3f}" for v in dupont_data['Giá trị']],
                            y=dupont_data['Giá trị'],
                            connector={"line": {"color": "rgb(63, 63, 63)"}},
                        ))
                        
                        fig.update_layout(
                            title="Phân tách ROE (Waterfall)",
                            showlegend=False,
                            height=400,
                            template=chart_theme
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
                    
                    st.markdown("---")
                    
                    # Additional metrics
                    st.write("**📋 Chỉ Số Bổ Sung**")
                    
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        interest_coverage = current_data.get('INTEREST_COVERAGE_RATIO', 0)
                        st.metric("Interest Coverage", f"{interest_coverage:.2f}",
                                 help="EBIT/Interest. > 3 là tốt")
                    
                    with col2:
                        assets_turnover = current_data.get('ASSETS_TURNOVER', 0)
                        st.metric("Assets Turnover", f"{assets_turnover:.2f}",
                                 help="Vòng quay tổng tài sản")
                    
                    with col3:
                        working_cap_ratio = current_data.get('WORKING_CAPITAL_RATIO', 0)
                        st.metric("Working Capital Ratio", f"{working_cap_ratio:.2f}",
                                 help="Tỷ lệ vốn lưu động")
                    
                    with col4:
                        cash_conversion = current_data.get('CASH_CONVERSION_CYCLE', 0)
                        st.metric("Cash Conversion Cycle", f"{cash_conversion:.0f} ngày",
                                 help="Chu kỳ chuyển đổi tiền mặt")
    
    # =====================================================
    # TAB 4: PHÂN TÍCH NGÂN HÀNG ĐẶC BIỆT
    # =====================================================
    with tab4:
        st.header("🏦 Phân Tích Chuyên Sâu Ngành Ngân Hàng")
        
        # Filter bank data
        banks_data = current_tickers[current_tickers['CAL_GROUP'] == 'bank'].copy()
        
        if not banks_data.empty:
            # Overview metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Số ngân hàng", f"{len(banks_data)}")
            with col2:
                avg_nim = banks_data['NIM_12M'].mean() * 100
                st.metric("NIM TB", f"{avg_nim:.2f}%")
            with col3:
                avg_npl = banks_data['NPL_Q'].mean() * 100
                st.metric("NPL TB", f"{avg_npl:.2f}%")
            with col4:
                avg_ldr = banks_data['LDR_12M'].mean() * 100
                st.metric("LDR TB", f"{avg_ldr:.2f}%")
            
            st.markdown("---")
            
            # Comparative analysis
            st.subheader("📊 So Sánh Các Ngân Hàng")
            
            tab4_1, tab4_2, tab4_3 = st.tabs([
                "💰 Chất Lượng Tài Sản",
                "📈 Sinh Lời",
                "🔄 Thanh Khoản & Tăng Trưởng"
            ])
            
            with tab4_1:
                col1, col2 = st.columns(2)
                
                with col1:
                    # NPL comparison
                    banks_npl = banks_data[banks_data['NPL_Q'] > 0].nlargest(15, 'NPL_Q')
                    
                    fig = px.bar(
                        banks_npl,
                        y='SYMBOL',
                        x='NPL_Q',
                        orientation='h',
                        title='NPL Ratio - Các ngân hàng có NPL cao nhất',
                        labels={'NPL_Q': 'NPL Ratio', 'SYMBOL': 'Ngân hàng'},
                        color='NPL_Q',
                        color_continuous_scale='Reds'
                    )
                    fig.update_traces(texttemplate='%{x:.2%}', textposition='outside')
                    fig.update_layout(height=500, showlegend=False, template=chart_theme)
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    # LLR comparison
                    banks_llr = banks_data[banks_data['LLR_Q'] > 0].nlargest(15, 'LLR_Q')
                    
                    fig = px.bar(
                        banks_llr,
                        y='SYMBOL',
                        x='LLR_Q',
                        orientation='h',
                        title='LLR - Tỷ lệ dự phòng rủi ro',
                        labels={'LLR_Q': 'LLR', 'SYMBOL': 'Ngân hàng'},
                        color='LLR_Q',
                        color_continuous_scale='Blues'
                    )
                    fig.update_traces(texttemplate='%{x:.2%}', textposition='outside')
                    fig.update_layout(height=500, showlegend=False, template=chart_theme)
                    st.plotly_chart(fig, use_container_width=True)
            
            with tab4_2:
                col1, col2 = st.columns(2)
                
                with col1:
                    # NIM comparison
                    banks_nim = banks_data[banks_data['NIM_12M'] > 0].nlargest(15, 'NIM_12M')
                    
                    fig = px.bar(
                        banks_nim,
                        y='SYMBOL',
                        x='NIM_12M',
                        orientation='h',
                        title='NIM (12M) - Biên lãi suất thuần',
                        labels={'NIM_12M': 'NIM', 'SYMBOL': 'Ngân hàng'},
                        color='NIM_12M',
                        color_continuous_scale='Greens'
                    )
                    fig.update_traces(texttemplate='%{x:.2%}', textposition='outside')
                    fig.update_layout(height=500, showlegend=False, template=chart_theme)
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    # CIR comparison
                    banks_cir = banks_data[banks_data['CIR_12M'] > 0].nsmallest(15, 'CIR_12M')
                    
                    fig = px.bar(
                        banks_cir,
                        y='SYMBOL',
                        x='CIR_12M',
                        orientation='h',
                        title='CIR (12M) - Tỷ lệ chi phí/thu nhập (thấp là tốt)',
                        labels={'CIR_12M': 'CIR', 'SYMBOL': 'Ngân hàng'},
                        color='CIR_12M',
                        color_continuous_scale='Reds_r'
                    )
                    fig.update_traces(texttemplate='%{x:.2%}', textposition='outside')
                    fig.update_layout(height=500, showlegend=False, template=chart_theme)
                    st.plotly_chart(fig, use_container_width=True)
            
            with tab4_3:
                col1, col2 = st.columns(2)
                
                with col1:
                    # LDR comparison
                    banks_ldr = banks_data[banks_data['LDR_12M'] > 0]
                    
                    fig = px.scatter(
                        banks_ldr,
                        x='LDR_12M',
                        y='ROAE',
                        size='MARKET_CAP_HT',
                        color='SYMBOL',
                        hover_name='SYMBOL',
                        title='LDR vs ROE (Size = Vốn hóa)',
                        labels={'LDR_12M': 'LDR', 'ROAE': 'ROAE'}
                    )
                    
                    # Add ideal zone
                    fig.add_vrect(x0=0.70, x1=0.85, fillcolor="green", opacity=0.1,
                                 annotation_text="Vùng lý tưởng", annotation_position="top left")
                    
                    fig.update_layout(height=500, showlegend=False, template=chart_theme)
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    # CASA comparison
                    banks_casa = banks_data[banks_data['CASA_12M'] > 0].nlargest(15, 'CASA_12M')
                    
                    fig = px.bar(
                        banks_casa,
                        y='SYMBOL',
                        x='CASA_12M',
                        orientation='h',
                        title='CASA (12M) - Tiền gửi không kỳ hạn',
                        labels={'CASA_12M': 'CASA', 'SYMBOL': 'Ngân hàng'},
                        color='CASA_12M',
                        color_continuous_scale='Blues'
                    )
                    fig.update_traces(texttemplate='%{x:.2%}', textposition='outside')
                    fig.update_layout(height=500, showlegend=False, template=chart_theme)
                    st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("---")
            
            # Ranking table
            st.subheader("📋 Bảng Xếp Hạng Ngân Hàng")
            
            # Calculate composite score
            banks_data['Banking_Score'] = (
                (banks_data['NIM_12M'] / banks_data['NIM_12M'].max() * 25) +
                ((1 - banks_data['NPL_Q'] / banks_data['NPL_Q'].max()) * 25) +
                ((1 - banks_data['CIR_12M'] / banks_data['CIR_12M'].max()) * 25) +
                (banks_data['ROAE'] / banks_data['ROAE'].max() * 25)
            )
            
            banks_ranked = banks_data.nlargest(20, 'Banking_Score')[
                ['SYMBOL', 'NIM_12M', 'NPL_Q', 'CIR_12M', 'LDR_12M', 'CASA_12M', 
                 'ROAE', 'PE_EOQ', 'PB_EOQ', 'Banking_Score']
            ].copy()
            
            # Format display
            banks_ranked['NIM_12M'] = banks_ranked['NIM_12M'] * 100
            banks_ranked['NPL_Q'] = banks_ranked['NPL_Q'] * 100
            banks_ranked['CIR_12M'] = banks_ranked['CIR_12M'] * 100
            banks_ranked['LDR_12M'] = banks_ranked['LDR_12M'] * 100
            banks_ranked['CASA_12M'] = banks_ranked['CASA_12M'] * 100
            banks_ranked['ROAE'] = banks_ranked['ROAE'] * 100
            
            banks_ranked = banks_ranked.rename(columns={
                'SYMBOL': 'Mã',
                'NIM_12M': 'NIM %',
                'NPL_Q': 'NPL %',
                'CIR_12M': 'CIR %',
                'LDR_12M': 'LDR %',
                'CASA_12M': 'CASA %',
                'ROAE': 'ROE %',
                'PE_EOQ': 'P/E',
                'PB_EOQ': 'P/B',
                'Banking_Score': 'Điểm'
            })
            
            st.dataframe(
                banks_ranked.style.format({
                    col: '{:.2f}' for col in banks_ranked.select_dtypes(include=['float64']).columns
                }).background_gradient(subset=['Điểm'], cmap='RdYlGn'),
                use_container_width=True,
                height=600
            )
        else:
            st.info("Không có dữ liệu ngân hàng trong kỳ này")
    
    # =====================================================
    # TAB 5: PHÂN TÍCH CHỨNG KHOÁN ĐẶC BIỆT
    # =====================================================
    with tab5:
        st.header("📊 Phân Tích Chuyên Sâu Công Ty Chứng Khoán")
        
        # Filter securities data
        securities_data = current_tickers[current_tickers['CAL_GROUP'] == 'security'].copy()
        
        if not securities_data.empty:
            # Overview
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Số CTCK", f"{len(securities_data)}")
            with col2:
                avg_brokerage = securities_data['BROKERAGE_COMPONENT'].mean() * 100
                st.metric("Brokerage TB", f"{avg_brokerage:.2f}%")
            with col3:
                avg_margin_rate = securities_data['MARGIN_INTEREST_RATE_12M'].mean() * 100
                st.metric("Margin Rate TB", f"{avg_margin_rate:.2f}%")
            with col4:
                avg_roe = securities_data['ROAE'].mean() * 100
                st.metric("ROE TB", f"{avg_roe:.2f}%")
            
            st.markdown("---")
            
            # Analysis tabs
            st.subheader("📊 Phân Tích So Sánh")
            
            tab5_1, tab5_2, tab5_3 = st.tabs([
                "💰 Cơ Cấu Doanh Thu",
                "📈 Hiệu Quả Hoạt Động",
                "🏆 Xếp Hạng"
            ])
            
            with tab5_1:
                # Revenue structure analysis
                st.write("**Cơ cấu doanh thu trung bình của ngành**")
                
                avg_rev = {
                    'Môi giới': securities_data['REV_FR_BROKERAGE_SERVICES'].sum(),
                    'Margin': securities_data['REV_FR_MARGIN_SERVICES'].sum(),
                    'Tự doanh': securities_data['REV_FR_PROPRIETARY_TRADING'].sum(),
                    'Bảo lãnh': securities_data['REV_FR_UNDERWRITING_SERVICES'].sum(),
                    'Lưu ký': securities_data['REV_FR_SECURITIES_CUSTODIAN_SERVICES'].sum(),
                    'Tư vấn': securities_data['REV_FR_SECURITIES_INVESTMENTS_ADVISORY_SERVICES'].sum()
                }
                
                avg_rev_df = pd.DataFrame(list(avg_rev.items()), columns=['Dịch vụ', 'Doanh thu'])
                avg_rev_df = avg_rev_df[avg_rev_df['Doanh thu'] > 0]
                
                col1, col2 = st.columns(2)
                
                with col1:
                    fig = px.pie(
                        avg_rev_df,
                        values='Doanh thu',
                        names='Dịch vụ',
                        title='Cơ cấu doanh thu toàn ngành',
                        color_discrete_sequence=px.colors.qualitative.Pastel
                    )
                    fig.update_traces(textposition='inside', textinfo='percent+label')
                    fig.update_layout(height=400, template=chart_theme)
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    fig = px.bar(
                        avg_rev_df.sort_values('Doanh thu', ascending=True),
                        x='Doanh thu',
                        y='Dịch vụ',
                        orientation='h',
                        title='Doanh thu theo dịch vụ (VNĐ)',
                        text='Doanh thu'
                    )
                    fig.update_traces(texttemplate='%{text:.2s}', textposition='outside')
                    fig.update_layout(height=400, template=chart_theme)
                    st.plotly_chart(fig, use_container_width=True)
                
                # Component comparison
                st.write("**So sánh thành phần đóng góp**")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    top_brokerage = securities_data.nlargest(10, 'BROKERAGE_COMPONENT')
                    
                    fig = px.bar(
                        top_brokerage,
                        y='SYMBOL',
                        x='BROKERAGE_COMPONENT',
                        orientation='h',
                        title='Top 10 CTCK - Thành phần Môi giới',
                        labels={'BROKERAGE_COMPONENT': 'Brokerage %', 'SYMBOL': 'CTCK'},
                        color='BROKERAGE_COMPONENT',
                        color_continuous_scale='Blues'
                    )
                    fig.update_traces(texttemplate='%{x:.2%}', textposition='outside')
                    fig.update_layout(height=400, showlegend=False, template=chart_theme)
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    top_margin = securities_data[securities_data['MARGIN_COMPONENT'] > 0].nlargest(10, 'MARGIN_COMPONENT')
                    
                    fig = px.bar(
                        top_margin,
                        y='SYMBOL',
                        x='MARGIN_COMPONENT',
                        orientation='h',
                        title='Top 10 CTCK - Thành phần Margin',
                        labels={'MARGIN_COMPONENT': 'Margin %', 'SYMBOL': 'CTCK'},
                        color='MARGIN_COMPONENT',
                        color_continuous_scale='Greens'
                    )
                    fig.update_traces(texttemplate='%{x:.2%}', textposition='outside')
                    fig.update_layout(height=400, showlegend=False, template=chart_theme)
                    st.plotly_chart(fig, use_container_width=True)
                
                with col3:
                    top_prop = securities_data[securities_data['PROPRIETARY_TRADING_COMPONENT'] > 0].nlargest(10, 'PROPRIETARY_TRADING_COMPONENT')
                    
                    fig = px.bar(
                        top_prop,
                        y='SYMBOL',
                        x='PROPRIETARY_TRADING_COMPONENT',
                        orientation='h',
                        title='Top 10 CTCK - Thành phần Tự doanh',
                        labels={'PROPRIETARY_TRADING_COMPONENT': 'Proprietary %', 'SYMBOL': 'CTCK'},
                        color='PROPRIETARY_TRADING_COMPONENT',
                        color_continuous_scale='Reds'
                    )
                    fig.update_traces(texttemplate='%{x:.2%}', textposition='outside')
                    fig.update_layout(height=400, showlegend=False, template=chart_theme)
                    st.plotly_chart(fig, use_container_width=True)
            
            with tab5_2:
                col1, col2 = st.columns(2)
                
                with col1:
                    # ROE comparison
                    top_roe = securities_data[securities_data['ROAE'] > 0].nlargest(15, 'ROAE')
                    
                    fig = px.bar(
                        top_roe,
                        y='SYMBOL',
                        x='ROAE',
                        orientation='h',
                        title='Top 15 CTCK theo ROE',
                        labels={'ROAE': 'ROE', 'SYMBOL': 'CTCK'},
                        color='ROAE',
                        color_continuous_scale='Greens'
                    )
                    fig.update_traces(texttemplate='%{x:.2%}', textposition='outside')
                    fig.update_layout(height=500, showlegend=False, template=chart_theme)
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    # Operating margin
                    top_margin = securities_data[securities_data['OPERATING_MARGIN_12M'] > 0].nlargest(15, 'OPERATING_MARGIN_12M')
                    
                    fig = px.bar(
                        top_margin,
                        y='SYMBOL',
                        x='OPERATING_MARGIN_12M',
                        orientation='h',
                        title='Top 15 CTCK theo Biên hoạt động',
                        labels={'OPERATING_MARGIN_12M': 'Operating Margin', 'SYMBOL': 'CTCK'},
                        color='OPERATING_MARGIN_12M',
                        color_continuous_scale='Blues'
                    )
                    fig.update_traces(texttemplate='%{x:.2%}', textposition='outside')
                    fig.update_layout(height=500, showlegend=False, template=chart_theme)
                    st.plotly_chart(fig, use_container_width=True)
                
                # Scatter analysis
                st.write("**Phân tích ma trận**")
                
                valid_data = securities_data[
                    (securities_data['PE_EOQ'] > 0) &
                    (securities_data['PE_EOQ'] < 50) &
                    (securities_data['ROAE'] > 0)
                ]
                
                fig = px.scatter(
                    valid_data,
                    x='PE_EOQ',
                    y='ROAE',
                    size='MARKET_CAP_HT',
                    color='SYMBOL',
                    hover_name='SYMBOL',
                    title='Ma Trận Định Giá - CTCK (P/E vs ROE)',
                    labels={'PE_EOQ': 'P/E', 'ROAE': 'ROE'}
                )
                
                # Add quadrants
                fig.add_hline(y=valid_data['ROAE'].median(), line_dash="dash", line_color="gray")
                fig.add_vline(x=valid_data['PE_EOQ'].median(), line_dash="dash", line_color="gray")
                
                fig.update_layout(height=500, showlegend=False, template=chart_theme)
                st.plotly_chart(fig, use_container_width=True)
            
            with tab5_3:
                st.write("**Bảng Xếp Hạng Công Ty Chứng Khoán**")
                
                # Calculate composite score
                securities_data['Securities_Score'] = (
                    (securities_data['ROAE'] / securities_data['ROAE'].max() * 30) +
                    (securities_data['OPERATING_MARGIN_12M'] / securities_data['OPERATING_MARGIN_12M'].max() * 30) +
                    ((1 / securities_data['PE_EOQ'].replace([0, np.inf], 50)) / (1 / securities_data['PE_EOQ'].replace([0, np.inf], 50)).max() * 20) +
                    (securities_data['CURRENT_RATIO_Q'] / securities_data['CURRENT_RATIO_Q'].max() * 20)
                )
                
                securities_ranked = securities_data.nlargest(20, 'Securities_Score')[
                    ['SYMBOL', 'BROKERAGE_COMPONENT', 'MARGIN_COMPONENT', 'PROPRIETARY_TRADING_COMPONENT',
                     'ROAE', 'OPERATING_MARGIN_12M', 'PE_EOQ', 'PB_EOQ', 'Securities_Score']
                ].copy()
                
                # Format
                securities_ranked['BROKERAGE_COMPONENT'] = securities_ranked['BROKERAGE_COMPONENT'] * 100
                securities_ranked['MARGIN_COMPONENT'] = securities_ranked['MARGIN_COMPONENT'] * 100
                securities_ranked['PROPRIETARY_TRADING_COMPONENT'] = securities_ranked['PROPRIETARY_TRADING_COMPONENT'] * 100
                securities_ranked['ROAE'] = securities_ranked['ROAE'] * 100
                securities_ranked['OPERATING_MARGIN_12M'] = securities_ranked['OPERATING_MARGIN_12M'] * 100
                
                securities_ranked = securities_ranked.rename(columns={
                    'SYMBOL': 'Mã',
                    'BROKERAGE_COMPONENT': 'Môi giới %',
                    'MARGIN_COMPONENT': 'Margin %',
                    'PROPRIETARY_TRADING_COMPONENT': 'Tự doanh %',
                    'ROAE': 'ROE %',
                    'OPERATING_MARGIN_12M': 'Biên HĐ %',
                    'PE_EOQ': 'P/E',
                    'PB_EOQ': 'P/B',
                    'Securities_Score': 'Điểm'
                })
                
                st.dataframe(
                    securities_ranked.style.format({
                        col: '{:.2f}' for col in securities_ranked.select_dtypes(include=['float64']).columns
                    }).background_gradient(subset=['Điểm'], cmap='RdYlGn'),
                    use_container_width=True,
                    height=600
                )
        else:
            st.info("Không có dữ liệu công ty chứng khoán trong kỳ này")
    
    # =====================================================
    # TAB 6: STOCK SCREENER (Enhanced)
    # =====================================================
    with tab6:
        st.header("🎯 Stock Screener Nâng Cao")
        
        st.markdown("""
        ### 🔍 Tìm kiếm cổ phiếu tiềm năng
        
        Sử dụng bộ lọc thông minh để tìm cổ phiếu phù hợp với chiến lược đầu tư của bạn.
        Dashboard sẽ tự động điều chỉnh các chỉ số theo loại hình doanh nghiệp.
        """)
        
        # Quick strategy templates
        st.subheader("⚡ Chiến Lược Nhanh")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("💎 Value Investing", use_container_width=True):
                st.session_state.pe_range = (5.0, 15.0)
                st.session_state.pb_range = (0.5, 2.0)
                st.session_state.roe_min = 12.0
                st.session_state.debt_max = 0.5
                st.session_state.z_min = 2.99
        
        with col2:
            if st.button("🚀 Growth Investing", use_container_width=True):
                st.session_state.roe_min = 20.0
                st.session_state.roa_min = 10.0
                st.session_state.margin_min = 10.0
                st.session_state.current_min = 1.5
        
        with col3:
            if st.button("🛡️ Safe & Stable", use_container_width=True):
                st.session_state.z_min = 2.99
                st.session_state.current_min = 2.0
                st.session_state.debt_max = 0.3
                st.session_state.roe_min = 10.0
        
        with col4:
            if st.button("🔄 Reset Filters", use_container_width=True):
                for key in list(st.session_state.keys()):
                    if key.endswith(('_range', '_min', '_max')):
                        del st.session_state[key]
        
        st.markdown("---")
        
        # Filter section
        st.subheader("🎛️ Bộ Lọc Chi Tiết")
        
        # Company type filter
        col_type = st.multiselect(
            "🏢 Loại hình doanh nghiệp",
            ['Doanh nghiệp', 'Ngân hàng', 'Chứng khoán'],
            default=['Doanh nghiệp', 'Ngân hàng', 'Chứng khoán']
        )
        
        cal_group_map = {'Doanh nghiệp': 'company', 'Ngân hàng': 'bank', 'Chứng khoán': 'security'}
        selected_cal_groups = [cal_group_map[x] for x in col_type]
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.write("**🏷️ Định giá**")
            
            pe_range = st.slider(
                "P/E",
                0.0, 100.0,
                st.session_state.get('pe_range', (0.0, 30.0)),
                key='pe_filter'
            )
            
            pb_range = st.slider(
                "P/B",
                0.0, 10.0,
                st.session_state.get('pb_range', (0.0, 5.0)),
                key='pb_filter'
            )
        
        with col2:
            st.write("**💰 Sinh lời**")
            
            roe_min = st.number_input(
                "ROE min (%)",
                0.0, 100.0,
                st.session_state.get('roe_min', 10.0),
                key='roe_filter'
            )
            
            roa_min = st.number_input(
                "ROA min (%)",
                0.0, 50.0,
                st.session_state.get('roa_min', 5.0),
                key='roa_filter'
            )
        
        with col3:
            st.write("**📊 Tài chính**")
            
            debt_max = st.number_input(
                "Debt Ratio max",
                0.0, 1.0,
                st.session_state.get('debt_max', 0.7),
                key='debt_filter'
            )
            
            z_min = st.number_input(
                "Z-Score min",
                0.0, 10.0,
                st.session_state.get('z_min', 1.81),
                key='z_filter'
            )
        
        # Search button
        if st.button("🔍 TÌM KIẾM CỔ PHIẾU", type="primary", use_container_width=True):
            with st.spinner("Đang tìm kiếm..."):
                # Filter data
                filtered = current_tickers[
                    (current_tickers['CAL_GROUP'].isin(selected_cal_groups)) &
                    (current_tickers['PE_EOQ'].between(pe_range[0], pe_range[1])) &
                    (current_tickers['PB_EOQ'].between(pb_range[0], pb_range[1])) &
                    (current_tickers['ROAE'] * 100 >= roe_min) &
                    (current_tickers['ROAA'] * 100 >= roa_min) &
                    (current_tickers['DEBTS_RATIO'] <= debt_max) &
                    (current_tickers['Z_SCORE'] >= z_min)
                ].copy()
                
                if len(filtered) > 0:
                    st.success(f"✅ Tìm thấy {len(filtered)} cổ phiếu phù hợp!")
                    
                    # Calculate composite score
                    filtered['Score'] = (
                        (filtered['ROAE'] / filtered['ROAE'].max() * 25) +
                        (filtered['ROAA'] / filtered['ROAA'].max() * 25) +
                        ((1 / filtered['PE_EOQ'].replace(0, np.inf)) / (1 / filtered['PE_EOQ'].replace(0, np.inf)).max() * 25) +
                        (filtered['Z_SCORE'] / filtered['Z_SCORE'].max() * 25)
                    )
                    
                    filtered = filtered.sort_values('Score', ascending=False)
                    
                    # Results visualization
                    st.subheader("📊 Kết Quả Tìm Kiếm")
                    
                    # Top results by company type
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        company_results = filtered[filtered['CAL_GROUP'] == 'company']
                        st.metric("🏢 Doanh nghiệp", f"{len(company_results)}")
                    
                    with col2:
                        bank_results = filtered[filtered['CAL_GROUP'] == 'bank']
                        st.metric("🏦 Ngân hàng", f"{len(bank_results)}")
                    
                    with col3:
                        security_results = filtered[filtered['CAL_GROUP'] == 'security']
                        st.metric("📊 Chứng khoán", f"{len(security_results)}")
                    
                    # Scatter plots
                    st.write("**📈 Phân Tích Trực Quan**")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        fig = px.scatter(
                            filtered.head(50),
                            x='PE_EOQ',
                            y='ROAE',
                            size='MARKET_CAP_HT',
                            color='CAL_GROUP',
                            hover_name='SYMBOL',
                            title='P/E vs ROE (Top 50)',
                            labels={'PE_EOQ': 'P/E', 'ROAE': 'ROE', 'CAL_GROUP': 'Loại hình'},
                            color_discrete_map={'company': '#667eea', 'bank': '#f5576c', 'security': '#4facfe'}
                        )
                        fig.update_layout(height=500, template=chart_theme)
                        st.plotly_chart(fig, use_container_width=True)
                    
                    with col2:
                        fig = px.scatter(
                            filtered.head(50),
                            x='PB_EOQ',
                            y='ROIC',
                            size='Score',
                            color='CAL_GROUP',
                            hover_name='SYMBOL',
                            title='P/B vs ROIC (Top 50)',
                            labels={'PB_EOQ': 'P/B', 'ROIC': 'ROIC', 'CAL_GROUP': 'Loại hình'},
                            color_discrete_map={'company': '#667eea', 'bank': '#f5576c', 'security': '#4facfe'}
                        )
                        fig.update_layout(height=500, template=chart_theme)
                        st.plotly_chart(fig, use_container_width=True)
                    
                    # Results table
                    st.write("**📋 Danh Sách Chi Tiết (Top 50)**")
                    
                    display_cols = [
                        'SYMBOL', 'CAL_GROUP', 'CLOSE_PRICE', 'MARKET_CAP_HT',
                        'PE_EOQ', 'PB_EOQ', 'ROAE', 'ROAA', 'ROIC',
                        'NET_INCOME_MARGIN_12M', 'DEBTS_RATIO', 'Z_SCORE', 'Score'
                    ]
                    
                    result_df = filtered[display_cols].head(50).copy()
                    
                    # Format
                    result_df['CLOSE_PRICE'] = result_df['CLOSE_PRICE'] / 1000
                    result_df['MARKET_CAP_HT'] = result_df['MARKET_CAP_HT'] / 1e12
                    result_df['ROAE'] = result_df['ROAE'] * 100
                    result_df['ROAA'] = result_df['ROAA'] * 100
                    result_df['ROIC'] = result_df['ROIC'] * 100
                    result_df['NET_INCOME_MARGIN_12M'] = result_df['NET_INCOME_MARGIN_12M'] * 100
                    
                    # Rename
                    result_df = result_df.rename(columns={
                        'SYMBOL': 'Mã',
                        'CAL_GROUP': 'Loại',
                        'CLOSE_PRICE': 'Giá (k)',
                        'MARKET_CAP_HT': 'VH (K tỷ)',
                        'PE_EOQ': 'P/E',
                        'PB_EOQ': 'P/B',
                        'ROAE': 'ROE %',
                        'ROAA': 'ROA %',
                        'ROIC': 'ROIC %',
                        'NET_INCOME_MARGIN_12M': 'Biên ròng %',
                        'DEBTS_RATIO': 'Nợ/TS',
                        'Z_SCORE': 'Z-Score',
                        'Score': 'Điểm'
                    })
                    
                    # Map CAL_GROUP to Vietnamese
                    result_df['Loại'] = result_df['Loại'].map({
                        'company': 'DN',
                        'bank': 'NH',
                        'security': 'CK'
                    })
                    
                    st.dataframe(
                        result_df.style.format({
                            col: '{:.2f}' for col in result_df.select_dtypes(include=['float64']).columns
                        }).background_gradient(subset=['Điểm'], cmap='RdYlGn'),
                        use_container_width=True,
                        height=600
                    )
                    
                    # Download button
                    csv = result_df.to_csv(index=False).encode('utf-8-sig')
                    st.download_button(
                        label="📥 Tải xuống kết quả (CSV)",
                        data=csv,
                        file_name=f'stock_screener_results_{selected_quarter}_{selected_year}.csv',
                        mime='text/csv'
                    )
                    
                else:
                    st.warning("⚠️ Không tìm thấy cổ phiếu nào. Thử nới lỏng điều kiện lọc!")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; padding: 2rem 0;'>
        <p style='font-size: 1.2rem;'><strong>📈 Dashboard Phân Tích Cổ Phiếu V2.0</strong></p>
        <p>✨ Phân tích chuyên sâu theo loại hình doanh nghiệp | 🚀 Hơn 100+ biểu đồ & visualizations</p>
        <p style='font-size: 0.85rem; margin-top: 1rem;'>
            <strong>Kỳ báo cáo:</strong> {}/{} | 
            <strong>Tổng mã:</strong> {:,} | 
            <strong>Ngành:</strong> {:,}
        </p>
        <p style='font-size: 0.8rem; color: #999; margin-top: 1rem;'>
            ⚠️ Thông tin chỉ mang tính chất tham khảo, không phải lời khuyên đầu tư
        </p>
    </div>
    """.format(
        selected_quarter,
        selected_year,
        len(current_tickers),
        len(current_industries)
    ), unsafe_allow_html=True)

except Exception as e:
    st.error(f"❌ Lỗi: {str(e)}")
    st.info("💡 Vui lòng kiểm tra lại file dữ liệu và đường dẫn")
    st.exception(e)