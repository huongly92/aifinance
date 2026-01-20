"""
Configuration file for Stock Dashboard
Chứa các constants, cấu hình và settings
"""

# ========== PATH CONFIGURATION ==========
DATA_DIR = "D:/aifinance_project/data/output"
MARKET_DATA_FILE = f"{DATA_DIR}/market_analysis.parquet"
INDUSTRY_DATA_FILE = f"{DATA_DIR}/industry_analysis.parquet"
TICKER_DATA_FILE = f"{DATA_DIR}/ticker_analysis.parquet"

# ========== DASHBOARD CONFIGURATION ==========
APP_TITLE = "📊 Dashboard Phân Tích Chứng Khoán"
APP_ICON = "📈"
LAYOUT = "wide"
INITIAL_SIDEBAR_STATE = "expanded"

# ========== COLOR SCHEME ==========
COLORS = {
    'primary': '#1f77b4',
    'success': '#2ecc71',
    'danger': '#e74c3c',
    'warning': '#f39c12',
    'info': '#3498db',
    'positive': '#00CC96',
    'negative': '#EF553B',
    'neutral': '#636EFA'
}

# ========== CHART CONFIGURATION ==========
CHART_HEIGHT = 400
CHART_TEMPLATE = "plotly_white"

PLOTLY_CONFIG = {
    'displayModeBar': True,
    'displaylogo': False,
    'modeBarButtonsToRemove': ['pan2d', 'lasso2d', 'select2d'],
    'toImageButtonOptions': {
        'format': 'png',
        'filename': 'chart',
        'height': 800,
        'width': 1200,
        'scale': 2
    }
}

# ========== KEY METRICS CONFIGURATION ==========
# Nhóm các chỉ số tài chính quan trọng
VALUATION_METRICS = ['PE_EOQ', 'PB_EOQ', 'EV_EBITDA', 'P_FCF_EOQ', 'P_CFO_EOQ']
PROFITABILITY_METRICS = ['ROAE', 'ROAA', 'ROIC', 'ROCE', 'NET_INCOME_MARGIN_12M', 
                         'OPERATING_MARGIN_12M', 'GROSS_MARGIN_12M']
GROWTH_METRICS = ['MARKET_CAP_EOQ_GYOY', 'MARKET_CAP_EOQ_GQOQ', 
                  'CLOSE_PRICE_GYOY', 'CLOSE_PRICE_GQOQ']
CASHFLOW_METRICS = ['CFO_12M', 'FCF_12M', 'FCFE_12M', 'FCFF_12M', 
                    'FCF_PER_SHARE_12M', 'OCF_PER_SHARE_12M']
LIQUIDITY_METRICS = ['CURRENT_RATIO_Q', 'QUICK_RATIO_Q', 'CASH_PLUS_EQUIVALENTS']
LEVERAGE_METRICS = ['DEBTS_RATIO', 'LEVERAGE', 'INTEREST_COVERAGE_RATIO']
EFFICIENCY_METRICS = ['ASSETS_TURNOVER', 'INVENTORY_TURNOVER', 
                     'ACCOUNTS_RECEIVABLE_TURNOVER', 'ACCOUNTS_PAYABLE_TURNOVER']
RISK_METRICS = ['Z_SCORE', 'Z1', 'Z2', 'Z3', 'Z4', 'Z5']

# Tất cả các nhóm metrics
ALL_METRIC_GROUPS = {
    'Định giá': VALUATION_METRICS,
    'Sinh lời': PROFITABILITY_METRICS,
    'Tăng trưởng': GROWTH_METRICS,
    'Dòng tiền': CASHFLOW_METRICS,
    'Thanh khoản': LIQUIDITY_METRICS,
    'Đòn bẩy': LEVERAGE_METRICS,
    'Hiệu quả': EFFICIENCY_METRICS,
    'Rủi ro': RISK_METRICS
}

# ========== METRIC LABELS (Vietnamese) ==========
METRIC_LABELS = {
    # Valuation
    'PE_EOQ': 'P/E',
    'PB_EOQ': 'P/B',
    'EV_EBITDA': 'EV/EBITDA',
    'P_FCF_EOQ': 'P/FCF',
    'P_CFO_EOQ': 'P/CFO',
    
    # Profitability
    'ROAE': 'ROE (%)',
    'ROAA': 'ROA (%)',
    'ROIC': 'ROIC (%)',
    'ROCE': 'ROCE (%)',
    'NET_INCOME_MARGIN_12M': 'Biên lợi nhuận ròng (%)',
    'OPERATING_MARGIN_12M': 'Biên EBIT (%)',
    'GROSS_MARGIN_12M': 'Biên gộp (%)',
    
    # Growth
    'MARKET_CAP_EOQ_GYOY': 'Tăng trưởng vốn hóa YoY (%)',
    'MARKET_CAP_EOQ_GQOQ': 'Tăng trưởng vốn hóa QoQ (%)',
    'CLOSE_PRICE_GYOY': 'Tăng giá YoY (%)',
    'CLOSE_PRICE_GQOQ': 'Tăng giá QoQ (%)',
    
    # Cashflow
    'CFO_12M': 'Dòng tiền hoạt động (12M)',
    'FCF_12M': 'Dòng tiền tự do (12M)',
    'FCFE_12M': 'FCFE (12M)',
    'FCFF_12M': 'FCFF (12M)',
    'FCF_PER_SHARE_12M': 'FCF/CP',
    'OCF_PER_SHARE_12M': 'OCF/CP',
    
    # Liquidity
    'CURRENT_RATIO_Q': 'Tỷ số thanh toán hiện hành',
    'QUICK_RATIO_Q': 'Tỷ số thanh toán nhanh',
    'CASH_PLUS_EQUIVALENTS': 'Tiền và tương đương',
    
    # Leverage
    'DEBTS_RATIO': 'Tỷ lệ nợ (%)',
    'LEVERAGE': 'Đòn bẩy',
    'INTEREST_COVERAGE_RATIO': 'Khả năng trả lãi',
    
    # Risk
    'Z_SCORE': 'Z-Score',
    
    # Other important metrics
    'MARKET_CAP_EOQ': 'Vốn hóa',
    'CLOSE_PRICE': 'Giá đóng cửa',
    'EPS_12M': 'EPS (12M)',
    'BVPS': 'BVPS',
    'DPS': 'DPS',
    'DIVIDEND_YIELD_EOQ': 'Tỷ suất cổ tức (%)',
    'NET_SALES_12M': 'Doanh thu (12M)',
    'NET_INCOME_12M': 'Lợi nhuận ròng (12M)',
    'NPATMI_12M': 'Lợi nhuận sau thuế (12M)',
    'EBITDA_12M': 'EBITDA (12M)',
    'TOTAL_ASSETS': 'Tổng tài sản',
    'TOTAL_EQUITY': 'Vốn chủ sở hữu',
    'TOTAL_DEBTS': 'Tổng nợ',
}

# ========== SCREENING PRESETS ==========
SCREENING_PRESETS = {
    'Value Investing': {
        'PE_EOQ': (0, 15),
        'PB_EOQ': (0, 1.5),
        'ROAE': (12, 100),
        'DEBTS_RATIO': (0, 0.6)
    },
    'Growth Investing': {
        'MARKET_CAP_EOQ_GYOY': (15, 100),
        'ROAE': (15, 100),
        'NET_INCOME_MARGIN_12M': (10, 100)
    },
    'Dividend Stocks': {
        'DIVIDEND_YIELD_EOQ': (4, 100),
        'ROAE': (10, 100),
        'DIVIDEND_PAYOUT': (0, 70)
    },
    'Quality Stocks': {
        'ROAE': (20, 100),
        'ROIC': (15, 100),
        'DEBTS_RATIO': (0, 0.5),
        'Z_SCORE': (3, 100)
    }
}

# ========== NUMBER FORMATTING ==========
def get_number_format(column_name):
    """Lấy định dạng số phù hợp cho từng cột"""
    if any(x in column_name.upper() for x in ['RATIO', 'MARGIN', 'YIELD', 'ROA', 'ROE', 'ROIC', 'ROCE', 'GROWTH', 'GQOQ', 'GYOY', 'DEBTS_RATIO']):
        return 'percent'
    elif any(x in column_name.upper() for x in ['MARKET_CAP', 'SALES', 'INCOME', 'ASSETS', 'EQUITY', 'DEBTS', 'CF', 'FCF', 'EBITDA', 'REVENUE']):
        return 'billion'
    elif 'PRICE' in column_name.upper():
        return 'price'
    elif any(x in column_name.upper() for x in ['PE_', 'PB_', 'EV_', 'P_']):
        return 'ratio'
    else:
        return 'number'

# ========== QUARTER UTILITIES ==========
def get_quarter_key(year, quarter):
    """Tạo key cho quarter (e.g., '2024Q1')"""
    return f"{year}Q{quarter}"

def parse_quarter_key(quarter_str):
    """Parse quarter string (e.g., '2024Q1') thành (year, quarter)"""
    year = int(quarter_str[:4])
    quarter = int(quarter_str[-1])
    return year, quarter
