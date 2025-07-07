"""
Technical indicators for stock analysis (e.g., moving averages, RSI).
"""

import pandas as pd
import numpy as np

def simple_moving_average(series, window):
    """
    Calculate simple moving average for a pandas Series.
    """
    if series is None or series.empty or len(series) < window:
        return None
    return series.rolling(window=window).mean()

def exponential_moving_average(series, window):
    """
    Calculate exponential moving average for a pandas Series.
    """
    if series is None or series.empty or len(series) < window:
        return None
    return series.ewm(span=window).mean()

def relative_strength_index(series, window=14):
    """
    Calculate Relative Strength Index (RSI).
    """
    if series is None or series.empty or len(series) < window + 1:
        return None
    
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def macd(series, fast=12, slow=26, signal=9):
    """
    Calculate MACD (Moving Average Convergence Divergence).
    Returns (macd_line, signal_line, histogram)
    """
    if series is None or series.empty or len(series) < slow:
        return None, None, None
    
    ema_fast = exponential_moving_average(series, fast)
    ema_slow = exponential_moving_average(series, slow)
    
    if ema_fast is None or ema_slow is None:
        return None, None, None
    
    macd_line = ema_fast - ema_slow
    signal_line = exponential_moving_average(macd_line, signal)
    histogram = macd_line - signal_line
    
    return macd_line, signal_line, histogram

def bollinger_bands(series, window=20, num_std=2):
    """
    Calculate Bollinger Bands.
    Returns (upper_band, middle_band, lower_band)
    """
    if series is None or series.empty or len(series) < window:
        return None, None, None
    
    middle_band = simple_moving_average(series, window)
    if middle_band is None:
        return None, None, None
    
    std = series.rolling(window=window).std()
    upper_band = middle_band + (std * num_std)
    lower_band = middle_band - (std * num_std)
    
    return upper_band, middle_band, lower_band

def support_resistance_levels(series, window=20):
    """
    Calculate support and resistance levels using local minima and maxima.
    Returns (support_level, resistance_level)
    """
    if series is None or series.empty or len(series) < window:
        return None, None
    
    # Find local minima (support) and maxima (resistance)
    local_min = series.rolling(window=window, center=True).min()
    local_max = series.rolling(window=window, center=True).max()
    
    # Get recent support and resistance levels
    recent_support = local_min.tail(10).mean()
    recent_resistance = local_max.tail(10).mean()
    
    return recent_support, recent_resistance

def price_momentum(series, window=14):
    """
    Calculate price momentum (rate of change).
    """
    if series is None or series.empty or len(series) < window:
        return None
    
    if len(series) < window:
        window = len(series)
    
    return ((series.iloc[-1] / series.iloc[-window]) - 1) * 100

def volume_weighted_average_price(series, volume_series, window=20):
    """
    Calculate Volume Weighted Average Price (VWAP).
    """
    if series is None or volume_series is None or series.empty or volume_series.empty:
        return None
    
    if len(series) != len(volume_series):
        return None
    
    typical_price = series  # Assuming series is already typical price (High+Low+Close)/3
    vwap = (typical_price * volume_series).rolling(window=window).sum() / volume_series.rolling(window=window).sum()
    return vwap

def stochastic_oscillator(high_series, low_series, close_series, k_window=14, d_window=3):
    """
    Calculate Stochastic Oscillator.
    Returns (%K, %D)
    """
    if any(s is None or s.empty for s in [high_series, low_series, close_series]):
        return None, None
    
    if len(high_series) != len(low_series) != len(close_series):
        return None, None
    
    lowest_low = low_series.rolling(window=k_window).min()
    highest_high = high_series.rolling(window=k_window).max()
    
    k_percent = 100 * ((close_series - lowest_low) / (highest_high - lowest_low))
    d_percent = k_percent.rolling(window=d_window).mean()
    
    return k_percent, d_percent 