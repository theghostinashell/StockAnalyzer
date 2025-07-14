#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from stock_analyzer.analysis.recommendations import (
    analyze_timeframe, generate_recommendation, get_timeframe_data
)
from stock_analyzer.data.stock_fetcher import fetch_stock_data

def test_analysis():
    """Test the analysis functionality with a real stock."""
    print("Testing stock analysis functionality...")
    
    # Fetch some test data
    symbol = "AAPL"
    end_date = datetime.now()
    start_date = end_date - timedelta(days=60)
    
    print(f"Fetching data for {symbol} from {start_date.date()} to {end_date.date()}")
    
    df = fetch_stock_data(symbol, start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"))
    
    if df is None or df.empty:
        print("Failed to fetch data")
        return
    
    print(f"Fetched {len(df)} data points")
    print(f"Date range: {df.index[0]} to {df.index[-1]}")
    # Ensure df['Close'] is a pandas Series for iloc
    close = pd.Series(df['Close'])
    print(f"Current price: ${close.iloc[-1]:.2f}")
    
    # Test timeframes
    timeframes_data = {}
    for timeframe in ["1D", "5D", "15D", "1M"]:
        print(f"\nTesting timeframe: {timeframe}")
        timeframe_df = get_timeframe_data(df, timeframe)
        if timeframe_df is not None:
            print(f"  Got {len(timeframe_df)} data points")
            analysis = analyze_timeframe(timeframe_df, timeframe)
            if analysis:
                print(f"  Analysis successful: {analysis['current_price']}, {analysis['price_change']}%")
                timeframes_data[timeframe] = analysis
            else:
                print(f"  Analysis failed")
        else:
            print(f"  No data for timeframe")
    
    print(f"\nTimeframes with data: {list(timeframes_data.keys())}")
    
    # Print signal strengths for each timeframe
    from stock_analyzer.analysis.recommendations import calculate_signal_strength
    total_score = 0
    timeframe_weights = {'1D': 0.15, '5D': 0.25, '15D': 0.3, '1M': 0.3}
    for timeframe, analysis in timeframes_data.items():
        if analysis:
            weight = timeframe_weights.get(timeframe, 0.25)
            signal_strength = calculate_signal_strength(analysis)
            print(f"Signal strength for {timeframe}: {signal_strength} (weight {weight})")
            total_score += signal_strength * weight
    print(f"Total score: {total_score}")
    
    # Test recommendation
    if timeframes_data:
        # Test both short term and long term
        print("\n--- Testing Short Term Recommendation ---")
        recommendation_short = generate_recommendation(symbol, df, timeframes_data, "short_term")
        if recommendation_short:
            print(f"RECOMMENDATION: {recommendation_short.recommendation}")
            print(f"Confidence: {recommendation_short.confidence:.0f}%")
            print(f"Entry Price: ${recommendation_short.entry_price:.2f}")
            print(f"Exit Price: ${recommendation_short.exit_price:.2f}")
            print(f"Stop Loss: ${recommendation_short.stop_loss:.2f}")
        
        print("\n--- Testing Long Term Recommendation ---")
        recommendation_long = generate_recommendation(symbol, df, timeframes_data, "long_term")
        if recommendation_long:
            print(f"RECOMMENDATION: {recommendation_long.recommendation}")
            print(f"Confidence: {recommendation_long.confidence:.0f}%")
            print(f"Entry Price: ${recommendation_long.entry_price:.2f}")
            print(f"Exit Price: ${recommendation_long.exit_price:.2f}")
            print(f"Stop Loss: ${recommendation_long.stop_loss:.2f}")
        else:
            print("Failed to generate recommendation")
    else:
        print("No timeframe data available for recommendation")

    # Test with a different stock (NVDA)
    print("\n\n--- Testing with NVDA ---")
    symbol = "NVDA"
    end_date = datetime.now()
    start_date = end_date - timedelta(days=60)
    print(f"Fetching data for {symbol} from {start_date.date()} to {end_date.date()}")
    df = fetch_stock_data(symbol, start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"))
    if df is None or df.empty:
        print("Failed to fetch data")
        return
    print(f"Fetched {len(df)} data points")
    print(f"Date range: {df.index[0]} to {df.index[-1]}")
    # Ensure df['Close'] is a pandas Series for iloc
    close = pd.Series(df['Close'])
    print(f"Current price: ${close.iloc[-1]:.2f}")
    timeframes_data = {}
    for timeframe in ["1D", "5D", "15D", "1M"]:
        print(f"\nTesting timeframe: {timeframe}")
        timeframe_df = get_timeframe_data(df, timeframe)
        if timeframe_df is not None:
            print(f"  Got {len(timeframe_df)} data points")
            analysis = analyze_timeframe(timeframe_df, timeframe)
            if analysis:
                print(f"  Analysis successful: {analysis['current_price']}, {analysis['price_change']}%")
                timeframes_data[timeframe] = analysis
            else:
                print(f"  Analysis failed")
        else:
            print(f"  No data for timeframe")
    print(f"\nTimeframes with data: {list(timeframes_data.keys())}")
    total_score = 0
    for timeframe, analysis in timeframes_data.items():
        if analysis:
            weight = timeframe_weights.get(timeframe, 0.25)
            signal_strength = calculate_signal_strength(analysis)
            print(f"Signal strength for {timeframe}: {signal_strength} (weight {weight})")
            total_score += signal_strength * weight
    print(f"Total score: {total_score}")
    if timeframes_data:
        recommendation = generate_recommendation(symbol, df, timeframes_data)
        if recommendation:
            print(f"\nRECOMMENDATION: {recommendation.recommendation}")
            print(f"Confidence: {recommendation.confidence:.0f}%")
            print(f"Current Price: ${recommendation.current_price:.2f}")
            print(f"Entry Price: ${recommendation.entry_price:.2f}")
            print(f"Exit Price: ${recommendation.exit_price:.2f}")
            print(f"Stop Loss: ${recommendation.stop_loss:.2f}")
            print(f"Reasoning: {recommendation.reasoning}")
        else:
            print("Failed to generate recommendation")
    else:
        print("No timeframe data available for recommendation")

    # Try several volatile stocks and print the first BUY/SELL
    print("\n\n--- Searching for a clear BUY or SELL ---")
    stock_list = ["TSLA", "AMZN", "NFLX", "META", "GOOG", "MSFT"]
    found = False
    for symbol in stock_list:
        print(f"\nTesting {symbol}...")
        end_date = datetime.now()
        start_date = end_date - timedelta(days=60)
        df = fetch_stock_data(symbol, start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"))
        if df is None or df.empty:
            print("  Failed to fetch data")
            continue
        close = pd.Series(df['Close'])
        timeframes_data = {}
        for timeframe in ["1D", "5D", "15D", "1M"]:
            timeframe_df = get_timeframe_data(df, timeframe)
            if timeframe_df is not None:
                analysis = analyze_timeframe(timeframe_df, timeframe)
                if analysis:
                    timeframes_data[timeframe] = analysis
        if not timeframes_data:
            print("  No timeframe data available")
            continue
        total_score = 0
        for timeframe, analysis in timeframes_data.items():
            weight = timeframe_weights.get(timeframe, 0.25)
            signal_strength = calculate_signal_strength(analysis)
            total_score += signal_strength * weight
        recommendation = generate_recommendation(symbol, df, timeframes_data)
        print(f"  Recommendation: {recommendation.recommendation} (score: {total_score})")
        if recommendation.recommendation in ["BUY", "SELL"]:
            print(f"  --- Found {recommendation.recommendation} for {symbol}! ---")
            print(f"  Confidence: {recommendation.confidence:.0f}%")
            print(f"  Current Price: ${recommendation.current_price:.2f}")
            print(f"  Entry Price: ${recommendation.entry_price:.2f}")
            print(f"  Exit Price: ${recommendation.exit_price:.2f}")
            print(f"  Stop Loss: ${recommendation.stop_loss:.2f}")
            print(f"  Reasoning: {recommendation.reasoning}")
            found = True
            break
    if not found:
        print("No clear BUY or SELL found in the tested stocks. All results were HOLD.")

if __name__ == "__main__":
    test_analysis() 