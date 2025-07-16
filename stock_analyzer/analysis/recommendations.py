

class StockRecommendation:
    def __init__(self, symbol, current_price, recommendation, confidence, reasoning, entry_price, exit_price, stop_loss):
        self.symbol = symbol
        self.current_price = current_price
        self.recommendation = recommendation
        self.confidence = confidence
        self.reasoning = reasoning
        self.entry_price = entry_price
        self.exit_price = exit_price
        self.stop_loss = stop_loss

def analyze_timeframe(df, timeframe_name):
    if df is None or df.empty:
        return None
    close = df['Close']
    price_change = round(((close.iloc[-1] / close.iloc[0]) - 1) * 100, 2) if len(close) > 1 else 0.0
    return {
        'timeframe': timeframe_name,
        'current_price': round(close.iloc[-1], 2),
        'price_change': price_change
    }

def generate_recommendation(symbol, df, timeframes_data, timeframe_type="short_term"):
    if df is None or df.empty:
        return None
    current_price = df['Close'].iloc[-1]
    return StockRecommendation(
        symbol=symbol,
        current_price=current_price,
        recommendation="HOLD",
        confidence=50,
        reasoning="Insufficient data",
        entry_price=current_price,
        exit_price=current_price,
        stop_loss=current_price
    )

def get_timeframe_data(df, timeframe):
    if df is None or df.empty:
        return None
    end_date = df.index[-1]
    if timeframe == "1D":
        timeframe_df = df.tail(1)
    elif timeframe == "5D":
        timeframe_df = df.tail(5)
    elif timeframe == "15D":
        timeframe_df = df.tail(15)
    elif timeframe == "1M":
        timeframe_df = df.tail(22)
    else:
        return None
    if len(timeframe_df) < 2:
        return None
    return timeframe_df
