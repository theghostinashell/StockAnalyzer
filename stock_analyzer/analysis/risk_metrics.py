

def max_drawdown(series):
    if series is None or series.empty:
        return None
    roll_max = series.cummax()
    drawdown = (series - roll_max) / roll_max
    max_dd = drawdown.min()
    return round(max_dd * 100, 2)
