from stock_analyzer.data.stock_fetcher import fetch_stock_data
from stock_analyzer.analysis.recommendations import generate_recommendation, get_timeframe_data, analyze_timeframe

# Test JPM specifically
df = fetch_stock_data('JPM', '2024-01-01', '2025-01-01')
current_price = df['Close'].iloc[-1]
print(f"JPM Current Price: ${current_price:.2f}")
print(f"Current Price (exact): {current_price}")

timeframes = {tf: analyze_timeframe(get_timeframe_data(df, tf), tf) for tf in ['1D', '5D', '15D', '1M']}

# Test long term specifically
rec = generate_recommendation('JPM', df, timeframes, 'long_term')
print(f"\nJPM LONG TERM:")
print(f"Recommendation: {rec.recommendation}")
print(f"Entry: ${rec.entry_price:.2f}")
print(f"Entry (exact): {rec.entry_price}")
print(f"Target: ${rec.exit_price:.2f}")
print(f"Stop Loss: ${rec.stop_loss:.2f}")

# Check if the values make sense
if rec.recommendation == "SELL":
    print(f"\nSELL Logic Check:")
    print(f"Entry should be current price: {rec.entry_price == current_price}")
    print(f"Entry vs Current (diff): {abs(rec.entry_price - current_price)}")
    print(f"Target should be below entry: {rec.exit_price < rec.entry_price}")
    print(f"Stop loss should be above entry: {rec.stop_loss > rec.entry_price}")
    
    if rec.stop_loss <= rec.entry_price:
        print("❌ ERROR: Stop loss should be ABOVE entry for SELL")
    if rec.exit_price >= rec.entry_price:
        print("❌ ERROR: Target should be BELOW entry for SELL") 