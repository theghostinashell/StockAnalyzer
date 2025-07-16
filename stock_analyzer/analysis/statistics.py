

def mean_price(series):
    if series is None or series.empty:
        return None
    return round(series.mean(), 2)

def median_price(series):
    if series is None or series.empty:
        return None
    return round(series.median(), 2)

def price_volatility(series):
    if series is None or series.empty:
        return None
    return round(series.std(), 2)

def daily_returns(series):
    if series is None or series.empty:
        return None
    return series.pct_change().fillna(0) * 100

def cumulative_returns(series):
    if series is None or series.empty:
        return None
    total_return = (series.iloc[-1] / series.iloc[0]) - 1 if len(series) > 1 else 0
    return round(total_return * 100, 2)

def sharpe_ratio(series):
    if series is None or series.empty:
        return None
    returns = series.pct_change().dropna()
    if returns.std() == 0:
        return None
    ratio = returns.mean() / returns.std() * (252 ** 0.5)
    return round(ratio, 2)

def beta_ratio(series, market_series):
    if series is None or market_series is None or series.empty or market_series.empty:
        return None
    if len(series) != len(market_series):
        return None
    returns = series.pct_change().dropna()
    market_returns = market_series.pct_change().dropna()
    common_index = returns.index.intersection(market_returns.index)
    if len(common_index) < 2:
        return None
    returns = returns[common_index]
    market_returns = market_returns[common_index]
    covariance = returns.cov(market_returns)
    market_variance = market_returns.var()
    if market_variance == 0:
        return None
    beta = covariance / market_variance
    return round(beta, 2)

def alpha_ratio(series, market_series, risk_free_rate=0.02):
    if series is None or market_series is None or series.empty or market_series.empty:
        return None
    beta_val = beta_ratio(series, market_series)
    if beta_val is None:
        return None
    returns = series.pct_change().dropna()
    market_returns = market_series.pct_change().dropna()
    common_index = returns.index.intersection(market_returns.index)
    if len(common_index) < 2:
        return None
    returns = returns[common_index]
    market_returns = market_returns[common_index]
    avg_return = returns.mean() * 252
    avg_market_return = market_returns.mean() * 252
    alpha = avg_return - (risk_free_rate + beta_val * (avg_market_return - risk_free_rate))
    return round(alpha * 100, 2)

def value_at_risk(series, confidence_level=0.05):
    if series is None or series.empty:
        return None
    returns = series.pct_change().dropna()
    if returns.empty:
        return None
    var = returns.quantile(confidence_level)
    return round(var * 100, 2)

def price_to_earnings_ratio(current_price, earnings_per_share):
    if current_price is None or earnings_per_share is None or earnings_per_share <= 0:
        return None
    return round(current_price / earnings_per_share, 2)

def price_to_book_ratio(current_price, book_value_per_share):
    if current_price is None or book_value_per_share is None or book_value_per_share <= 0:
        return None
    return round(current_price / book_value_per_share, 2)

def dividend_yield(current_price, annual_dividend):
    if current_price is None or annual_dividend is None or current_price <= 0:
        return None
    return round((annual_dividend / current_price) * 100, 2)
