"""
📊 Financial Report Style Configuration
Chứa toàn bộ config về màu sắc, font, spacing cho báo cáo tài chính
Dễ dàng customize theo ý muốn!
"""

# ==================== COLOR SCHEME ====================

COLORS = {
    # Gradient colors cho header
    'header_gradient_start': '#667eea',
    'header_gradient_end': '#764ba2',
    
    # Gradient colors cho cột "Chỉ số"
    'index_gradient_start': '#f093fb',
    'index_gradient_end': '#f5576c',
    
    # Background colors
    'index_bg_odd': '#FFF9C4',      # Màu nền cột chỉ số - dòng lẻ
    'index_bg_even': '#FFF59D',     # Màu nền cột chỉ số - dòng chẵn
    'row_bg_even': '#f8f9fa',       # Màu nền dòng chẵn
    'row_hover': '#e3f2fd',         # Màu khi hover
    
    # Text colors
    'negative_number': '#D32F2F',   # Màu số âm
    'text_primary': '#212121',      # Màu text chính
    'text_white': 'white',
    
    # Group colors
    'company': '#1976D2',           # Công ty
    'bank': '#388E3C',              # Ngân hàng
    'security': '#F57C00',          # Chứng khoán
    'insurance': '#7B1FA2',         # Bảo hiểm
}

# ==================== FONT SETTINGS ====================

FONTS = {
    'family': "'Source Sans Pro', sans-serif",
    'size_header': '14px',
    'size_body': '13px',
    'size_index': '13px',
    'weight_bold': '600',
    'weight_normal': 'normal',
}

# ==================== SPACING ====================

SPACING = {
    'cell_padding': '8px',
    'header_padding': '12px 8px',
    'table_border_radius': '10px',
    'table_shadow': '0 2px 8px rgba(0,0,0,0.1)',
}

# ==================== COLUMN WIDTH ====================

COLUMN_WIDTH = {
    'index_min_width': '200px',     # Độ rộng tối thiểu cột "Chỉ số"
    'index_width': '200px',         # Độ rộng cố định cột "Chỉ số"
    'quarter_min_width': '80px',    # Độ rộng tối thiểu cột quý
}

# ==================== TABLE STYLES GENERATOR ====================

def get_table_styles():
    """
    Tạo table styles cho pandas DataFrame
    Dễ dàng customize bằng cách thay đổi COLORS, FONTS, SPACING
    """
    return [
        # Header chính (tất cả các cột bao gồm "Chỉ số")
        {
            'selector': 'thead th',
            'props': [
                ('background', f'linear-gradient(135deg, {COLORS["header_gradient_start"]} 0%, {COLORS["header_gradient_end"]} 100%)'),
                ('color', COLORS['text_white']),
                ('font-weight', FONTS['weight_bold']),
                ('font-size', FONTS['size_header']),
                ('text-align', 'center'),
                ('padding', SPACING['header_padding']),
                ('border', 'none'),
            ]
        },
        # Header cột đầu tiên ("Chỉ số")
        {
            'selector': 'thead th:first-child',
            'props': [
                ('background', f'linear-gradient(135deg, {COLORS["index_gradient_start"]} 0%, {COLORS["index_gradient_end"]} 100%)'),
                ('text-align', 'left'),
                ('min-width', COLUMN_WIDTH['index_min_width']),
                ('width', COLUMN_WIDTH['index_width']),
            ]
        },
        # Dòng chẵn
        {
            'selector': 'tbody tr:nth-child(even)',
            'props': [('background-color', COLORS['row_bg_even'])]
        },
        # Hover effect
        {
            'selector': 'tbody tr:hover',
            'props': [
                ('background-color', COLORS['row_hover']),
                ('transition', 'background-color 0.2s'),
            ]
        },
        # Cột đầu tiên trong body (cột "Chỉ số")
        {
            'selector': 'tbody td:first-child',
            'props': [
                ('background-color', COLORS['index_bg_odd']),
                ('font-weight', FONTS['weight_bold']),
                ('text-align', 'left'),
                ('font-size', FONTS['size_index']),
                ('padding', SPACING['cell_padding']),
                ('min-width', COLUMN_WIDTH['index_min_width']),
                ('width', COLUMN_WIDTH['index_width']),
            ]
        },
        # Cột đầu tiên dòng chẵn
        {
            'selector': 'tbody tr:nth-child(even) td:first-child',
            'props': [('background-color', COLORS['index_bg_even'])]
        },
        # Table general
        {
            'selector': 'table',
            'props': [
                ('border-collapse', 'collapse'),
                ('width', '100%'),
                ('box-shadow', SPACING['table_shadow']),
                ('border-radius', SPACING['table_border_radius']),
                ('overflow', 'hidden'),
                ('font-family', FONTS['family']),
            ]
        },
    ]

# ==================== CELL PROPERTIES ====================

def get_cell_properties():
    """Properties cho các cells trong bảng"""
    return {
        'text-align': 'right',
        'font-size': FONTS['size_body'],
        'padding': SPACING['cell_padding'],
    }

# ==================== GROUP INFO ====================

def get_group_info():
    """Thông tin icons và màu sắc cho từng nhóm"""
    return {
        'company': {'icon': '🏢', 'name': 'Công ty', 'color': COLORS['company']},
        'bank': {'icon': '🏦', 'name': 'Ngân hàng', 'color': COLORS['bank']},
        'security': {'icon': '📈', 'name': 'Chứng khoán', 'color': COLORS['security']},
        'insurance': {'icon': '🛡️', 'name': 'Bảo hiểm', 'color': COLORS['insurance']},
    }

# ==================== STREAMLIT PAGE CSS ====================

def get_streamlit_css():
    """
    CSS cho Streamlit page
    Đặt trong st.markdown(..., unsafe_allow_html=True)
    """
    return f"""
    <style>
        /* Clean header */
        .main h1 {{
            color: {COLORS['company']};
            font-weight: {FONTS['weight_bold']};
            margin-bottom: 0.5rem;
        }}
        
        /* Metrics cards */
        div[data-testid="metric-container"] {{
            background: linear-gradient(135deg, {COLORS['header_gradient_start']} 0%, {COLORS['header_gradient_end']} 100%);
            padding: 1rem;
            border-radius: {SPACING['table_border_radius']};
            color: white;
        }}
        
        div[data-testid="metric-container"] label {{
            color: rgba(255,255,255,0.9) !important;
            font-size: 0.9rem;
        }}
        
        div[data-testid="metric-container"] [data-testid="stMetricValue"] {{
            color: white;
            font-size: 1.8rem;
            font-weight: {FONTS['weight_bold']};
        }}
        
        /* Tabs gradient */
        .stTabs [data-baseweb="tab-list"] {{
            gap: 8px;
            background: transparent;
        }}
        
        .stTabs [data-baseweb="tab"] {{
            padding: 12px 24px;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            border-radius: 10px 10px 0 0;
            font-weight: {FONTS['weight_bold']};
            border: none;
            transition: all 0.3s;
        }}
        
        .stTabs [data-baseweb="tab"]:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }}
        
        .stTabs [aria-selected="true"] {{
            background: linear-gradient(135deg, {COLORS['header_gradient_start']} 0%, {COLORS['header_gradient_end']} 100%);
            color: white;
        }}
        
        /* Sidebar clean */
        section[data-testid="stSidebar"] {{
            background: linear-gradient(180deg, #f8f9fa 0%, #ffffff 100%);
        }}
        
        /* Info boxes */
        .stAlert {{
            border-radius: {SPACING['table_border_radius']};
            border: none;
        }}
    </style>
    """

# ==================== CUSTOMIZATION TIPS ====================
"""
💡 HƯỚNG DẪN CUSTOMIZE:

1. Thay đổi màu sắc:
   - Sửa trong dict COLORS
   - VD: COLORS['header_gradient_start'] = '#ff6b6b'

2. Thay đổi font:
   - Sửa trong dict FONTS
   - VD: FONTS['size_body'] = '15px'

3. Thay đổi spacing:
   - Sửa trong dict SPACING
   - VD: SPACING['cell_padding'] = '12px'

4. Thay đổi độ rộng cột:
   - Sửa trong dict COLUMN_WIDTH
   - VD: COLUMN_WIDTH['index_width'] = '300px'

5. Áp dụng ngay lập tức:
   - Save file này
   - Refresh Streamlit app
   - Không cần sửa code logic!
"""