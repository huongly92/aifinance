"""
Metrics Module
Tính toán các chỉ số tài chính và thống kê
"""

import pandas as pd
import numpy as np


def calculate_summary_stats(df, column):
    """
    Tính các thống kê tóm tắt cho một cột
    
    Args:
        df: DataFrame
        column: Tên cột
        
    Returns:
        dict: Dictionary chứa các thống kê
    """
    if column not in df.columns:
        return None
    
    data = df[column].dropna()
    
    if len(data) == 0:
        return None
    
    return {
        'mean': data.mean(),
        'median': data.median(),
        'std': data.std(),
        'min': data.min(),
        'max': data.max(),
        'q25': data.quantile(0.25),
        'q75': data.quantile(0.75),
        'count': len(data)
    }


def calculate_growth_rate(df, column, periods=1):
    """
    Tính tốc độ tăng trưởng
    
    Args:
        df: DataFrame (đã sắp xếp theo thời gian)
        column: Tên cột cần tính
        periods: Số kỳ để tính tăng trưởng
        
    Returns:
        Series: Tốc độ tăng trưởng (%)
    """
    if column not in df.columns:
        return None
    
    values = df[column]
    growth = ((values - values.shift(periods)) / values.shift(periods).abs()) * 100
    
    return growth


def calculate_cagr(df, column, start_idx=0, end_idx=-1):
    """
    Tính Compound Annual Growth Rate (CAGR)
    
    Args:
        df: DataFrame
        column: Tên cột
        start_idx: Index bắt đầu
        end_idx: Index kết thúc
        
    Returns:
        float: CAGR (%)
    """
    if column not in df.columns:
        return None
    
    try:
        start_value = df[column].iloc[start_idx]
        end_value = df[column].iloc[end_idx]
        n_periods = abs(end_idx - start_idx)
        
        if start_value <= 0 or end_value <= 0 or n_periods == 0:
            return None
        
        cagr = (((end_value / start_value) ** (1 / n_periods)) - 1) * 100
        return cagr
    except:
        return None


def calculate_percentile(df, column, value):
    """
    Tính percentile của một giá trị trong phân phối
    
    Args:
        df: DataFrame
        column: Tên cột
        value: Giá trị cần tính percentile
        
    Returns:
        float: Percentile (0-100)
    """
    if column not in df.columns:
        return None
    
    data = df[column].dropna()
    
    if len(data) == 0:
        return None
    
    percentile = (data < value).sum() / len(data) * 100
    return percentile


def calculate_z_score_components(row):
    """
    Tính các thành phần của Altman Z-Score
    
    Args:
        row: Series chứa dữ liệu tài chính
        
    Returns:
        dict: Dictionary chứa các thành phần Z-Score
    """
    components = {}
    
    # Z1 = Working Capital / Total Assets
    if pd.notna(row.get('WORKING_CAPITAL_AVG4Q')) and pd.notna(row.get('TOTAL_ASSETS')):
        wc = row.get('WORKING_CAPITAL_AVG4Q', 0)
        ta = row.get('TOTAL_ASSETS', 1)
        components['Z1'] = wc / ta if ta != 0 else 0
    
    # Z2 = Retained Earnings / Total Assets
    if 'Z2' in row:
        components['Z2'] = row['Z2']
    
    # Z3 = EBIT / Total Assets
    if pd.notna(row.get('EBIT_12M')) and pd.notna(row.get('TOTAL_ASSETS')):
        ebit = row.get('EBIT_12M', 0)
        ta = row.get('TOTAL_ASSETS', 1)
        components['Z3'] = ebit / ta if ta != 0 else 0
    
    # Z4 = Market Value of Equity / Book Value of Total Liabilities
    if pd.notna(row.get('MARKET_CAP_EOQ')) and pd.notna(row.get('TOTAL_LIABILITIES')):
        mve = row.get('MARKET_CAP_EOQ', 0)
        tl = row.get('TOTAL_LIABILITIES', 1)
        components['Z4'] = mve / tl if tl != 0 else 0
    
    # Z5 = Sales / Total Assets
    if pd.notna(row.get('NET_SALES_12M')) and pd.notna(row.get('TOTAL_ASSETS')):
        sales = row.get('NET_SALES_12M', 0)
        ta = row.get('TOTAL_ASSETS', 1)
        components['Z5'] = sales / ta if ta != 0 else 0
    
    # Total Z-Score
    if all(k in components for k in ['Z1', 'Z2', 'Z3', 'Z4', 'Z5']):
        components['Z_SCORE'] = (
            1.2 * components['Z1'] +
            1.4 * components['Z2'] +
            3.3 * components['Z3'] +
            0.6 * components['Z4'] +
            1.0 * components['Z5']
        )
    
    return components


def interpret_z_score(z_score):
    """
    Giải thích Z-Score
    
    Args:
        z_score: Giá trị Z-Score
        
    Returns:
        tuple: (category, description, color)
    """
    if pd.isna(z_score):
        return ("N/A", "Không đủ dữ liệu", "#808080")
    
    if z_score > 2.99:
        return ("An toàn", "Khả năng phá sản thấp", "#00CC96")
    elif z_score >= 1.81:
        return ("Vùng xám", "Cần theo dõi", "#FFA15A")
    else:
        return ("Cảnh báo", "Rủi ro cao", "#EF553B")


def calculate_dupont_analysis(row):
    """
    Phân tích DuPont cho ROE
    
    Args:
        row: Series chứa dữ liệu tài chính
        
    Returns:
        dict: Các thành phần DuPont
    """
    components = {}
    
    # Tax Burden = Net Income / PBT
    if 'DU1_TAX_BURDEN' in row:
        components['tax_burden'] = row['DU1_TAX_BURDEN']
    
    # Interest Burden = PBT / EBIT
    if 'DU2_INTEREST_BURDEN' in row:
        components['interest_burden'] = row['DU2_INTEREST_BURDEN']
    
    # Profit Margin = EBIT / Sales
    if 'DU3_PROFIT_MARGIN' in row:
        components['profit_margin'] = row['DU3_PROFIT_MARGIN']
    
    # Asset Turnover = Sales / Assets
    if 'DU4_ASSETS_TURNOVER' in row:
        components['asset_turnover'] = row['DU4_ASSETS_TURNOVER']
    
    # Leverage = Assets / Equity
    if 'DU5_LEVERAGE' in row:
        components['leverage'] = row['DU5_LEVERAGE']
    
    # ROE
    if all(k in components for k in ['tax_burden', 'interest_burden', 'profit_margin', 'asset_turnover', 'leverage']):
        components['roe'] = (
            components['tax_burden'] *
            components['interest_burden'] *
            components['profit_margin'] *
            components['asset_turnover'] *
            components['leverage']
        )
    
    return components


def calculate_liquidity_score(row):
    """
    Tính điểm thanh khoản
    
    Args:
        row: Series chứa dữ liệu tài chính
        
    Returns:
        float: Điểm thanh khoản (0-100)
    """
    score = 0
    count = 0
    
    # Current Ratio (ideal: > 2)
    if pd.notna(row.get('CURRENT_RATIO_Q')):
        cr = row.get('CURRENT_RATIO_Q', 0)
        if cr >= 2:
            score += 30
        elif cr >= 1.5:
            score += 20
        elif cr >= 1:
            score += 10
        count += 30
    
    # Quick Ratio (ideal: > 1)
    if pd.notna(row.get('QUICK_RATIO_Q')):
        qr = row.get('QUICK_RATIO_Q', 0)
        if qr >= 1:
            score += 25
        elif qr >= 0.8:
            score += 15
        elif qr >= 0.5:
            score += 5
        count += 25
    
    # Cash Ratio (ideal: > 0.5)
    if pd.notna(row.get('CASH_PLUS_EQUIVALENTS')) and pd.notna(row.get('CURRENT_LIABILITIES')):
        cash = row.get('CASH_PLUS_EQUIVALENTS', 0)
        cl = row.get('CURRENT_LIABILITIES', 1)
        cash_ratio = cash / cl if cl != 0 else 0
        if cash_ratio >= 0.5:
            score += 25
        elif cash_ratio >= 0.3:
            score += 15
        elif cash_ratio >= 0.1:
            score += 5
        count += 25
    
    # Working Capital positive
    if pd.notna(row.get('WORKING_CAPITAL_AVG4Q')):
        wc = row.get('WORKING_CAPITAL_AVG4Q', 0)
        if wc > 0:
            score += 20
        count += 20
    
    return (score / count * 100) if count > 0 else 0


def calculate_profitability_score(row):
    """
    Tính điểm sinh lời
    
    Args:
        row: Series chứa dữ liệu tài chính
        
    Returns:
        float: Điểm sinh lời (0-100)
    """
    score = 0
    count = 0
    
    # ROE (ideal: > 15%)
    if pd.notna(row.get('ROAE')):
        roe = row.get('ROAE', 0)
        if roe >= 20:
            score += 30
        elif roe >= 15:
            score += 20
        elif roe >= 10:
            score += 10
        count += 30
    
    # ROA (ideal: > 5%)
    if pd.notna(row.get('ROAA')):
        roa = row.get('ROAA', 0)
        if roa >= 8:
            score += 25
        elif roa >= 5:
            score += 15
        elif roa >= 3:
            score += 5
        count += 25
    
    # Net Margin (ideal: > 10%)
    if pd.notna(row.get('NET_INCOME_MARGIN_12M')):
        margin = row.get('NET_INCOME_MARGIN_12M', 0)
        if margin >= 15:
            score += 25
        elif margin >= 10:
            score += 15
        elif margin >= 5:
            score += 5
        count += 25
    
    # ROIC (ideal: > 10%)
    if pd.notna(row.get('ROIC')):
        roic = row.get('ROIC', 0)
        if roic >= 15:
            score += 20
        elif roic >= 10:
            score += 10
        elif roic >= 5:
            score += 5
        count += 20
    
    return (score / count * 100) if count > 0 else 0


def screen_stocks(df, criteria):
    """
    Lọc cổ phiếu theo tiêu chí
    
    Args:
        df: DataFrame ticker
        criteria: Dict chứa các tiêu chí {column: (min, max)}
        
    Returns:
        DataFrame: Cổ phiếu đã lọc
    """
    result = df.copy()
    
    for column, (min_val, max_val) in criteria.items():
        if column in result.columns:
            if min_val is not None:
                result = result[result[column] >= min_val]
            if max_val is not None:
                result = result[result[column] <= max_val]
    
    return result
