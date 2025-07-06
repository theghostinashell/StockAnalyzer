"""
Statistical calculations for stock data.
"""

def mean_price(series):
    """
    Calculate mean price from a pandas Series.
    """
    if series is None or series.empty:
        return None
    return round(series.mean(), 2)

def median_price(series):
    """
    Calculate median price from a pandas Series.
    """
    if series is None or series.empty:
        return None
    return round(series.median(), 2)

def price_volatility(series):
    """
    Calculate price volatility (standard deviation) from a pandas Series.
    """
    if series is None or series.empty:
        return None
    return round(series.std(), 2)

def daily_returns(series):
    """
    Calculate daily returns as percentage change.
    Returns a pandas Series.
    """
    if series is None or series.empty:
        return None
    return series.pct_change().fillna(0) * 100

def cumulative_returns(series):
    """
    Calculate cumulative returns as a percentage.
    Returns a float (total cumulative return in percent).
    """
    if series is None or series.empty:
        return None
    total_return = (series.iloc[-1] / series.iloc[0]) - 1 if len(series) > 1 else 0
    return round(total_return * 100, 2)

def sharpe_ratio(series):
    """
    Calculate the Sharpe ratio (risk-free rate = 0).
    """
    if series is None or series.empty:
        return None
    returns = series.pct_change().dropna()
    if returns.std() == 0:
        return None
    ratio = returns.mean() / returns.std() * (252 ** 0.5)
    return round(ratio, 2) 