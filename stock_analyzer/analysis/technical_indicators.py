import pandas as pd
import numpy as np
from typing import Tuple, Optional, List

def simple_moving_average(data: pd.Series, period: int) -> Optional[pd.Series]:
    """
    Calculate Simple Moving Average (SMA).
    
    Args:
        data: Price data series
        period: Number of periods for the moving average
    
    Returns:
        SMA series or None if insufficient data
    """
    if len(data) < period:
        return None
    return data.rolling(window=period).mean()

def exponential_moving_average(data: pd.Series, period: int) -> Optional[pd.Series]:
    """
    Calculate Exponential Moving Average (EMA).
    
    Args:
        data: Price data series
        period: Number of periods for the moving average
    
    Returns:
        EMA series or None if insufficient data
    """
    if len(data) < period:
        return None
    return data.ewm(span=period).mean()

def relative_strength_index(data: pd.Series, period: int = 14) -> Optional[pd.Series]:
    """
    Calculate Relative Strength Index (RSI).
    
    Args:
        data: Price data series
        period: Number of periods for RSI calculation
    
    Returns:
        RSI series or None if insufficient data
    """
    if len(data) < period + 1:
        return None
    
    delta = data.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def macd(data: pd.Series, fast_period: int = 12, slow_period: int = 26, signal_period: int = 9) -> Tuple[Optional[pd.Series], Optional[pd.Series]]:
    """
    Calculate MACD (Moving Average Convergence Divergence).
    
    Args:
        data: Price data series
        fast_period: Fast EMA period
        slow_period: Slow EMA period
        signal_period: Signal line period
    
    Returns:
        Tuple of (MACD line, Signal line) or (None, None) if insufficient data
    """
    if len(data) < max(fast_period, slow_period) + signal_period:
        return None, None
    
    ema_fast = exponential_moving_average(data, fast_period)
    ema_slow = exponential_moving_average(data, slow_period)
    
    if ema_fast is None or ema_slow is None:
        return None, None
    
    macd_line = ema_fast - ema_slow
    signal_line = exponential_moving_average(macd_line, signal_period)
    
    return macd_line, signal_line

def bollinger_bands(data: pd.Series, period: int = 20, std_dev: float = 2) -> Tuple[Optional[pd.Series], Optional[pd.Series], Optional[pd.Series]]:
    """
    Calculate Bollinger Bands.
    
    Args:
        data: Price data series
        period: Number of periods for the moving average
        std_dev: Number of standard deviations
    
    Returns:
        Tuple of (Upper band, Middle band, Lower band) or (None, None, None) if insufficient data
    """
    if len(data) < period:
        return None, None, None
    
    middle_band = simple_moving_average(data, period)
    if middle_band is None:
        return None, None, None
    
    std = data.rolling(window=period).std()
    upper_band = middle_band + (std * std_dev)
    lower_band = middle_band - (std * std_dev)
    
    return upper_band, middle_band, lower_band

def support_resistance_levels(data: pd.Series, period: int = 20) -> Optional[Tuple[float, float]]:
    """
    Calculate support and resistance levels.
    
    Args:
        data: Price data series
        period: Number of periods to look back
    
    Returns:
        Tuple of (support, resistance) or None if insufficient data
    """
    if len(data) < period:
        return None
    
    recent_data = data.tail(period)
    support = recent_data.min()
    resistance = recent_data.max()
    
    return support, resistance

def price_momentum(data: pd.Series, period: int = 14) -> Optional[float]:
    """
    Calculate price momentum.
    
    Args:
        data: Price data series
        period: Number of periods to look back
    
    Returns:
        Momentum value or None if insufficient data
    """
    if len(data) < period + 1:
        return None
    
    current_price = data.iloc[-1]
    past_price = data.iloc[-period-1]
    momentum = ((current_price - past_price) / past_price) * 100
    
    return momentum
