from stock_analyzer.data.stock_fetcher import fetch_stock_data
from stock_analyzer.analysis.recommendations import generate_recommendation, get_timeframe_data, analyze_timeframe

# Fetch JPM data
df = fetch_stock_data('JPM', '2024-01-01', '2025-01-01')
print(f"Data range: {df.index[0]} to {df.index[-1]}")
print(f"Current price: {df['Close'].iloc[-1]:.2f}")

# Test short term
timeframes = {tf: analyze_timeframe(get_timeframe_data(df, tf), tf) for tf in ['1D', '5D', '15D', '1M']}
rec_short = generate_recommendation('JPM', df, timeframes, 'short_term')
print(f"\nSHORT TERM:")
print(f"Recommendation: {rec_short.recommendation}")
print(f"Entry: {rec_short.entry_price}")
print(f"Exit: {rec_short.exit_price}")
print(f"Stop Loss: {rec_short.stop_loss}")

# Test long term
rec_long = generate_recommendation('JPM', df, timeframes, 'long_term')
print(f"\nLONG TERM:")
print(f"Recommendation: {rec_long.recommendation}")
print(f"Entry: {rec_long.entry_price}")
print(f"Exit: {rec_long.exit_price}")
print(f"Stop Loss: {rec_long.stop_loss}") 