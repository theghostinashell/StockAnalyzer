from stock_analyzer.data.stock_fetcher import fetch_stock_data
from stock_analyzer.analysis.recommendations import generate_recommendation, get_timeframe_data, analyze_timeframe

stocks = ['JPM', 'AAPL', 'GOOGL', 'MSFT', 'TSLA', 'NVDA']

for symbol in stocks:
    print(f"\n{'='*50}")
    print(f"TESTING {symbol}")
    print(f"{'='*50}")
    
    try:
        # Fetch data
        df = fetch_stock_data(symbol, '2024-01-01', '2025-01-01')
        current_price = df['Close'].iloc[-1]
        print(f"Current Price: ${current_price:.2f}")
        
        # Test both timeframes
        timeframes = {tf: analyze_timeframe(get_timeframe_data(df, tf), tf) for tf in ['1D', '5D', '15D', '1M']}
        
        for timeframe_type in ['short_term', 'long_term']:
            rec = generate_recommendation(symbol, df, timeframes, timeframe_type)
            print(f"\n{timeframe_type.upper()}:")
            print(f"  Recommendation: {rec.recommendation}")
            print(f"  Entry: ${rec.entry_price:.2f}")
            print(f"  Exit/Target: ${rec.exit_price:.2f}")
            print(f"  Stop Loss: ${rec.stop_loss:.2f}")
            
            # Check for logical errors
            if rec.recommendation == "BUY":
                if rec.stop_loss >= rec.entry_price:
                    print(f"  ❌ ERROR: Stop loss (${rec.stop_loss:.2f}) >= Entry (${rec.entry_price:.2f})")
                if rec.exit_price <= rec.entry_price:
                    print(f"  ❌ ERROR: Exit (${rec.exit_price:.2f}) <= Entry (${rec.entry_price:.2f})")
                else:
                    print(f"  ✅ BUY logic correct")
                    
            elif rec.recommendation == "SELL":
                if rec.stop_loss <= rec.entry_price:
                    print(f"  ❌ ERROR: Stop loss (${rec.stop_loss:.2f}) <= Entry (${rec.entry_price:.2f})")
                if rec.exit_price >= rec.entry_price:
                    print(f"  ❌ ERROR: Exit (${rec.exit_price:.2f}) >= Entry (${rec.entry_price:.2f})")
                else:
                    print(f"  ✅ SELL logic correct")
                    
    except Exception as e:
        print(f"Error testing {symbol}: {e}") 