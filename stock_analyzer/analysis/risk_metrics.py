"""
Risk analysis functions for stock data.
"""

def max_drawdown(series):
    """
    Calculate the maximum drawdown for a price series.
    Returns:
        float: Maximum drawdown as a percentage (negative value)
    """
    if series is None or series.empty:
        return None
    roll_max = series.cummax()
    drawdown = (series - roll_max) / roll_max
    max_dd = drawdown.min()
    return round(max_dd * 100, 2) 