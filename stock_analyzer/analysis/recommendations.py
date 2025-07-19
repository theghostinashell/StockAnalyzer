
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from stock_analyzer.analysis.technical_indicators import (
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
    Calculate signal strength based on professional technical analysis.
    Returns a score from -100 (strong sell) to +100 (strong buy).
    Based on institutional trading strategies and research.
    """
    if not analysis:
        return 0
    
    score = 0
    current_price = analysis['current_price']
    
    # 1. TREND ANALYSIS (35% weight) - Most important for professional analysis
    trend_score = 0
    
    # Moving Average Trend Analysis
    if analysis['sma_20'] and analysis['sma_50']:
        # Golden Cross/Death Cross (strong signals)
        if current_price > analysis['sma_20'] > analysis['sma_50']:
            trend_score += 30  # Strong uptrend
        elif current_price < analysis['sma_20'] < analysis['sma_50']:
            trend_score -= 30  # Strong downtrend
        # Price vs MA analysis
        elif current_price > analysis['sma_20']:
            trend_score += 20  # Above short-term MA
        else:
            trend_score -= 20  # Below short-term MA
    
    # EMA Trend Analysis
    if analysis['ema_12'] and analysis['ema_26']:
        if analysis['ema_12'] > analysis['ema_26']:
            trend_score += 15  # Bullish EMA alignment
        else:
            trend_score -= 15  # Bearish EMA alignment
    
    score += trend_score * 0.35  # 35% weight for trend
    
    # 2. MOMENTUM ANALYSIS (30% weight)
    momentum_score = 0
    
    # RSI Analysis - Professional levels
    if analysis['rsi']:
        if analysis['rsi'] < 20:  # Extreme oversold
            momentum_score += 35
        elif analysis['rsi'] > 80:  # Extreme overbought
            momentum_score -= 35
        elif analysis['rsi'] < 30:  # Oversold
            momentum_score += 25
        elif analysis['rsi'] > 70:  # Overbought
            momentum_score -= 25
        elif analysis['rsi'] < 40:  # Slightly oversold
            momentum_score += 15
        elif analysis['rsi'] > 60:  # Slightly overbought
            momentum_score -= 15
    
    # Price Momentum
    if analysis['momentum']:
        if analysis['momentum'] > 8:  # Strong positive momentum
            momentum_score += 25
        elif analysis['momentum'] < -8:  # Strong negative momentum
            momentum_score -= 25
        elif analysis['momentum'] > 4:
            momentum_score += 15
        elif analysis['momentum'] < -4:
            momentum_score -= 15
    
    score += momentum_score * 0.30  # 30% weight for momentum
    
    # 3. VOLATILITY ANALYSIS (20% weight)
    volatility_score = 0
    
    # Bollinger Bands Analysis
    if analysis['bollinger_bands']:
        upper, middle, lower = analysis['bollinger_bands']
        if upper is not None and lower is not None:
            if isinstance(upper, pd.Series) and isinstance(lower, pd.Series):
                bb_position = (current_price - lower.iloc[-1]) / (upper.iloc[-1] - lower.iloc[-1])
                if bb_position < 0.2:  # Near lower band
                    volatility_score += 25
                elif bb_position > 0.8:  # Near upper band
                    volatility_score -= 25
                elif bb_position < 0.3:  # Below middle
                    volatility_score += 15
                elif bb_position > 0.7:  # Above middle
                    volatility_score -= 15
    
    score += volatility_score * 0.20  # 20% weight for volatility
    
    # 4. MACD ANALYSIS (15% weight)
    macd_score = 0
    
    if analysis['macd'][0] is not None and analysis['macd'][1] is not None:
        macd_line, signal_line = analysis['macd'][0], analysis['macd'][1]
        if isinstance(macd_line, pd.Series) and isinstance(signal_line, pd.Series) and len(macd_line) >= 2:
            # MACD Crossover signals
            if macd_line.iloc[-1] > signal_line.iloc[-1] and macd_line.iloc[-2] <= signal_line.iloc[-2]:
                macd_score += 30  # Bullish crossover
            elif macd_line.iloc[-1] < signal_line.iloc[-1] and macd_line.iloc[-2] >= signal_line.iloc[-2]:
                macd_score -= 30  # Bearish crossover
            # MACD position
            elif macd_line.iloc[-1] > signal_line.iloc[-1]:
                macd_score += 20
            else:
                macd_score -= 20
    
    score += macd_score * 0.15  # 15% weight for MACD
    
    return max(-100, min(100, score))

def generate_recommendation(symbol, df, timeframes_data, timeframe_type="short_term"):
    """
    Generate professional buy/sell recommendation based on multiple timeframes.
    Uses institutional-grade analysis with proper risk management.
    """
    if df is None or df.empty:
        return None
    
    current_price = df['Close'].iloc[-1]
    
    # Professional timeframe weighting based on investment horizon
    if timeframe_type == "short_term":
        # Short-term trading (days to weeks)
        timeframe_weights = {'1D': 0.20, '5D': 0.35, '15D': 0.30, '1M': 0.15}
        buy_threshold = 3     # Lower threshold for more actionable signals
        sell_threshold = -3   # Lower threshold for more actionable signals
    else:
        # Long-term investing (months to years)
        timeframe_weights = {'1D': 0.10, '5D': 0.20, '15D': 0.30, '1M': 0.40}
        buy_threshold = 5     # Higher threshold for long-term conviction
        sell_threshold = -5   # Higher threshold for long-term conviction
    
    # Calculate weighted signal strength
    total_score = 0
    timeframe_scores = {}
    
    for timeframe, analysis in timeframes_data.items():
        if analysis:
            weight = timeframe_weights.get(timeframe, 0.25)
            signal_strength = calculate_signal_strength(analysis)
            weighted_score = signal_strength * weight
            total_score += weighted_score
            timeframe_scores[timeframe] = signal_strength
    
    # Professional signal confirmation
    signal_consistency = 0
    positive_signals = sum(1 for score in timeframe_scores.values() if score > 3)
    negative_signals = sum(1 for score in timeframe_scores.values() if score < -3)
    
    if positive_signals >= 3:  # Strong bullish consensus
        signal_consistency = 8
    elif negative_signals >= 3:  # Strong bearish consensus
        signal_consistency = -8
    
    total_score += signal_consistency
    
    # Professional recommendation logic
    if total_score >= buy_threshold:
        recommendation = "BUY"
        confidence = min(85, 65 + abs(total_score))
    elif total_score <= sell_threshold:
        recommendation = "SELL"
        confidence = min(85, 65 + abs(total_score))
    else:
        recommendation = "HOLD"
        confidence = max(40, 50 - abs(total_score))
    
    reasoning = generate_professional_reasoning(timeframes_data, total_score, timeframe_scores)
    entry_price, exit_price, stop_loss = calculate_professional_price_targets(df, recommendation, total_score, timeframe_type)
    
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

def generate_professional_reasoning(timeframes_data, total_score, timeframe_scores):
    """
    Generate professional-grade reasoning for the recommendation.
    """
    reasoning_parts = []
    
    # Overall assessment
    if total_score >= 15:
        overall = "BULLISH: Multiple technical indicators showing strong upward momentum"
    elif total_score >= 5:
        overall = "BULLISH: Technical analysis suggests upward potential"
    elif total_score <= -15:
        overall = "BEARISH: Multiple technical indicators showing strong downward pressure"
    elif total_score <= -5:
        overall = "BEARISH: Technical analysis suggests downward potential"
    else:
        overall = "NEUTRAL: Mixed signals suggest waiting for clearer direction"
    
    reasoning_parts.append(overall)
    
    # Key technical insights
    key_insights = []
    
    # Check for strong signals across timeframes
    for timeframe, analysis in timeframes_data.items():
        if not analysis:
            continue
        
        timeframe_insights = []
        score = timeframe_scores.get(timeframe, 0)
        
        # RSI insights
        if analysis['rsi']:
            if analysis['rsi'] < 25:
                timeframe_insights.append(f"Extreme oversold (RSI: {analysis['rsi']:.1f})")
            elif analysis['rsi'] > 75:
                timeframe_insights.append(f"Extreme overbought (RSI: {analysis['rsi']:.1f})")
            elif analysis['rsi'] < 35:
                timeframe_insights.append(f"Oversold (RSI: {analysis['rsi']:.1f})")
            elif analysis['rsi'] > 65:
                timeframe_insights.append(f"Overbought (RSI: {analysis['rsi']:.1f})")
        
        # Trend insights
        if analysis['sma_20'] and analysis['sma_50']:
            if analysis['sma_20'] > analysis['sma_50']:
                timeframe_insights.append("Bullish trend (SMA alignment)")
            else:
                timeframe_insights.append("Bearish trend (SMA alignment)")
        
        # Momentum insights
        if analysis['momentum']:
            if abs(analysis['momentum']) > 6:
                timeframe_insights.append(f"Strong momentum ({analysis['momentum']:+.1f}%)")
        
        if timeframe_insights:
            key_insights.append(f"{timeframe}: {', '.join(timeframe_insights)}")
    
    if key_insights:
        reasoning_parts.extend(key_insights)
    
    # Risk assessment
    if abs(total_score) > 15:
        risk_level = "HIGH" if abs(total_score) > 25 else "MEDIUM"
        reasoning_parts.append(f"Risk Level: {risk_level} - Strong directional signals")
    else:
        reasoning_parts.append("Risk Level: LOW - Weak directional signals")
    
    return " | ".join(reasoning_parts)

def calculate_professional_price_targets(df, recommendation, signal_strength, timeframe_type="short_term"):
    """
    Calculate professional entry, exit, and stop loss prices.
    ALWAYS based on buying the stock at entry price, regardless of recommendation.
    """
    if df is None or df.empty:
        return None, None, None
    
    current_price = df['Close'].iloc[-1]
    
    # Calculate volatility for dynamic targets
    returns = df['Close'].pct_change().dropna()
    volatility = returns.std() * np.sqrt(252)  # Annualized volatility
    
    # Professional risk-reward ratios
    if timeframe_type == "short_term":
        # Short-term: 1:2 risk-reward ratio
        risk_percentage = 0.02  # 2% risk
        reward_percentage = 0.04  # 4% reward
    else:
        # Long-term: 1:3 risk-reward ratio
        risk_percentage = 0.05  # 5% risk
        reward_percentage = 0.15  # 15% reward
    
    # Adjust for volatility
    volatility_adjustment = min(2.0, max(0.5, volatility / 0.2))  # Normalize to 20% volatility
    risk_percentage *= volatility_adjustment
    reward_percentage *= volatility_adjustment
    
    # Entry price: current price (or slightly better for strong signals)
    if signal_strength > 15:
        entry_price = current_price * 0.995  # 0.5% below for strong buy signals
    elif signal_strength < -15:
        entry_price = current_price * 0.995  # Still 0.5% below for consistency
    else:
        entry_price = current_price
    
    # Exit price: ALWAYS above entry (profit target for buying)
    exit_price = entry_price * (1 + reward_percentage)
    
    # Stop loss: ALWAYS below entry (risk management for buying)
    stop_loss = entry_price * (1 - risk_percentage)
    
    return (round(entry_price, 2) if entry_price is not None else None,
            round(exit_price, 2) if exit_price is not None else None,
            round(stop_loss, 2) if stop_loss is not None else None)

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