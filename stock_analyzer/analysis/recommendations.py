"""
Buy/Sell recommendations and analysis for stocks.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from .technical_indicators import (
    simple_moving_average, exponential_moving_average, relative_strength_index,
    macd, bollinger_bands, support_resistance_levels, price_momentum
)

class StockRecommendation:
    def __init__(self, symbol, current_price, recommendation, confidence, reasoning, entry_price, exit_price, stop_loss):
        self.symbol = symbol
        self.current_price = current_price
        self.recommendation = recommendation  # "BUY", "SELL", "HOLD"
        self.confidence = confidence  # 0-100
        self.reasoning = reasoning
        self.entry_price = entry_price
        self.exit_price = exit_price
        self.stop_loss = stop_loss
        self.timestamp = datetime.now()

def analyze_timeframe(df, timeframe_name):
    """
    Analyze a specific timeframe and return technical indicators.
    """
    if df is None or df.empty:
        return None
    
    close = df['Close']
    high = df['High'] if 'High' in df.columns else close
    low = df['Low'] if 'Low' in df.columns else close
    volume = df['Volume'] if 'Volume' in df.columns else None
    
    # Calculate price change
    if len(close) > 1:
        price_change = round(((close.iloc[-1] / close.iloc[0]) - 1) * 100, 2)
    else:
        price_change = 0.0
    
    analysis = {
        'timeframe': timeframe_name,
        'current_price': round(close.iloc[-1], 2),
        'price_change': price_change,
        'sma_20': simple_moving_average(close, min(20, len(close))),
        'sma_50': simple_moving_average(close, min(50, len(close))),
        'ema_12': exponential_moving_average(close, min(12, len(close))),
        'ema_26': exponential_moving_average(close, min(26, len(close))),
        'rsi': relative_strength_index(close, min(14, len(close)-1)),
        'momentum': price_momentum(close, min(14, len(close))),
        'support_resistance': support_resistance_levels(close, min(20, len(close))),
        'bollinger_bands': bollinger_bands(close, min(20, len(close)), 2),
        'macd': macd(close, min(12, len(close)), min(26, len(close)), min(9, len(close)))
    }
    
    # Get latest values
    for key in ['sma_20', 'sma_50', 'ema_12', 'ema_26', 'rsi', 'momentum']:
        if analysis[key] is not None:
            if isinstance(analysis[key], pd.Series):
                analysis[key] = round(analysis[key].iloc[-1], 2)
    
    return analysis

def calculate_signal_strength(analysis):
    """
    Calculate signal strength based on technical indicators.
    Returns a score from -100 (strong sell) to +100 (strong buy).
    """
    if not analysis:
        return 0
    
    score = 0
    current_price = analysis['current_price']
    
    # Moving Average signals
    if analysis['sma_20'] and analysis['sma_50']:
        if current_price > analysis['sma_20'] > analysis['sma_50']:
            score += 15  # Golden cross
        elif current_price < analysis['sma_20'] < analysis['sma_50']:
            score -= 15  # Death cross
        elif current_price > analysis['sma_20']:
            score += 5
        else:
            score -= 5
    
    # EMA signals
    if analysis['ema_12'] and analysis['ema_26']:
        if analysis['ema_12'] > analysis['ema_26']:
            score += 10
        else:
            score -= 10
    
    # RSI signals
    if analysis['rsi']:
        if analysis['rsi'] < 30:
            score += 20  # Oversold
        elif analysis['rsi'] > 70:
            score -= 20  # Overbought
        elif analysis['rsi'] < 40:
            score += 10
        elif analysis['rsi'] > 60:
            score -= 10
    
    # Momentum signals
    if analysis['momentum']:
        if analysis['momentum'] > 5:
            score += 15
        elif analysis['momentum'] < -5:
            score -= 15
    
    # Bollinger Bands signals
    if analysis['bollinger_bands']:
        upper, middle, lower = analysis['bollinger_bands']
        if upper is not None and lower is not None:
            if isinstance(upper, pd.Series) and isinstance(lower, pd.Series):
                if current_price <= lower.iloc[-1]:
                    score += 15  # Near lower band (oversold)
                elif current_price >= upper.iloc[-1]:
                    score -= 15  # Near upper band (overbought)
    
    # MACD signals
    if analysis['macd'][0] is not None and analysis['macd'][1] is not None:
        macd_line, signal_line = analysis['macd'][0], analysis['macd'][1]
        if isinstance(macd_line, pd.Series) and isinstance(signal_line, pd.Series) and len(macd_line) >= 2:
            if macd_line.iloc[-1] > signal_line.iloc[-1] and macd_line.iloc[-2] <= signal_line.iloc[-2]:
                score += 20  # Bullish crossover
            elif macd_line.iloc[-1] < signal_line.iloc[-1] and macd_line.iloc[-2] >= signal_line.iloc[-2]:
                score -= 20  # Bearish crossover
    
    return max(-100, min(100, score))

def generate_recommendation(symbol, df, timeframes_data):
    """
    Generate comprehensive buy/sell recommendation based on multiple timeframes.
    """
    if df is None or df.empty:
        return None
    
    current_price = df['Close'].iloc[-1]
    
    # Calculate overall signal strength
    total_score = 0
    timeframe_weights = {'1D': 0.1, '5D': 0.2, '15D': 0.3, '1M': 0.4}
    
    for timeframe, analysis in timeframes_data.items():
        if analysis:
            weight = timeframe_weights.get(timeframe, 0.25)
            signal_strength = calculate_signal_strength(analysis)
            total_score += signal_strength * weight
    

    if total_score >= 15:  # Lowered from 30
        recommendation = "BUY"
        confidence = min(95, 50 + abs(total_score))
    elif total_score <= -15:  # Lowered from -30
        recommendation = "SELL"
        confidence = min(95, 50 + abs(total_score))
    else:
        recommendation = "HOLD"
        confidence = 50 - abs(total_score)

    reasoning = generate_reasoning(timeframes_data, total_score)
    
    # Calculate entry/exit prices
    entry_price, exit_price, stop_loss = calculate_price_targets(df, recommendation, total_score)
    
    return StockRecommendation(
        symbol=symbol,
        current_price=current_price,
        recommendation=recommendation,
        confidence=confidence,
        reasoning=reasoning,
        entry_price=entry_price,
        exit_price=exit_price,
        stop_loss=stop_loss
    )

def generate_reasoning(timeframes_data, total_score):
    """
    Generate detailed reasoning for the recommendation.
    """
    reasoning_parts = []
    
    for timeframe, analysis in timeframes_data.items():
        if not analysis:
            continue
            
        timeframe_reasoning = []
        
        # RSI analysis
        if analysis['rsi']:
            if analysis['rsi'] < 30:
                timeframe_reasoning.append(f"RSI oversold ({analysis['rsi']:.1f})")
            elif analysis['rsi'] > 70:
                timeframe_reasoning.append(f"RSI overbought ({analysis['rsi']:.1f})")
        
        # Moving average analysis
        if analysis['sma_20'] and analysis['sma_50']:
            if analysis['sma_20'] > analysis['sma_50']:
                timeframe_reasoning.append("SMA bullish alignment")
            else:
                timeframe_reasoning.append("SMA bearish alignment")
        
        # Momentum analysis
        if analysis['momentum']:
            if analysis['momentum'] > 5:
                timeframe_reasoning.append(f"Strong momentum (+{analysis['momentum']:.1f}%)")
            elif analysis['momentum'] < -5:
                timeframe_reasoning.append(f"Weak momentum ({analysis['momentum']:.1f}%)")
        
        if timeframe_reasoning:
            reasoning_parts.append(f"{timeframe}: {', '.join(timeframe_reasoning)}")
    
    if total_score >= 30:
        overall = "Overall bullish signals across timeframes"
    elif total_score <= -30:
        overall = "Overall bearish signals across timeframes"
    else:
        overall = "Mixed signals, neutral stance recommended"
    
    reasoning_parts.insert(0, overall)
    return " | ".join(reasoning_parts)

def calculate_price_targets(df, recommendation, signal_strength):
    """
    Calculate entry, exit, and stop loss prices.
    """
    if df is None or df.empty:
        return None, None, None
    
    current_price = df['Close'].iloc[-1]
    volatility = df['Close'].pct_change().std() * np.sqrt(252)  # Annualized volatility
    
    # Calculate support and resistance levels
    support, resistance = support_resistance_levels(df['Close'], 20)
    
    if recommendation == "BUY":
        # Entry price: slightly above current price or at support
        entry_price = min(current_price * 1.02, support if support else current_price * 1.01)
        
        # Exit price: target resistance or 10-20% above entry
        if resistance and resistance > entry_price * 1.1:
            exit_price = resistance
        else:
            exit_price = entry_price * (1.15 + abs(signal_strength) / 100)
        
        # Stop loss: below support or 5-10% below entry
        stop_loss = max(entry_price * 0.92, support * 0.95 if support else entry_price * 0.90)
        
    elif recommendation == "SELL":
        # Entry price: slightly below current price or at resistance
        entry_price = max(current_price * 0.98, resistance if resistance else current_price * 0.99)
        
        # Exit price: target support or 10-20% below entry
        if support and support < entry_price * 0.9:
            exit_price = support
        else:
            exit_price = entry_price * (0.85 - abs(signal_strength) / 100)
        
        # Stop loss: above resistance or 5-10% above entry
        stop_loss = min(entry_price * 1.08, resistance * 1.05 if resistance else entry_price * 1.10)
        
    else: 

        entry_price = current_price
        exit_price = resistance if resistance else current_price
        stop_loss = support if support else current_price
    
    return round(entry_price, 2), round(exit_price, 2), round(stop_loss, 2)

def get_timeframe_data(df, timeframe):
    """
    Get data for a specific timeframe from the main dataframe.
    """
    if df is None or df.empty:
        return None
    
    end_date = df.index[-1]
    
    if timeframe == "1D":
        # Last trading day - get just the last day's data
        timeframe_df = df.tail(1)  # Get the last row
    elif timeframe == "5D":
        # Last 5 trading days
        start_date = end_date - pd.Timedelta(days=7)  # Account for weekends
        timeframe_df = df[df.index >= start_date]
    elif timeframe == "15D":
        # Last 15 trading days
        start_date = end_date - pd.Timedelta(days=21)  # Account for weekends
        timeframe_df = df[df.index >= start_date]
    elif timeframe == "1M":
        # Last month
        start_date = end_date - pd.Timedelta(days=30)
        timeframe_df = df[df.index >= start_date]
    else:
        return None
    
    if len(timeframe_df) < 2:  # Need minimum data points
        return None
    
    return timeframe_df 