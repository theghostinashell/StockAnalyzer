#!/usr/bin/env python3
"""
Test script to debug the stock analysis functionality.
"""

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
    print(f"Current price: ${df['Close'].iloc[-1]:.2f}")
    
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
    
    # Test recommendation
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

if __name__ == "__main__":
    test_analysis() 