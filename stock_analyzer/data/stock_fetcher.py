"""
Fetches OHLCV stock data from Yahoo Finance using yfinance.
"""
try:
    import yfinance as yf
    import pandas as pd
except ImportError as e:
    print("Required package not found:", e)
    print("Please install dependencies with: pip install -r requirements.txt")
    raise

def get_company_name(symbol):
    """
    Get company name from ticker symbol using yfinance.
    Args:
        symbol (str): Stock ticker symbol
    Returns:
        str: Company name, or symbol if not found
    """
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        company_name = info.get('longName', symbol)
        return company_name
    except Exception as e:
        print(f"Error fetching company name for {symbol}: {e}")
        return symbol

def fetch_stock_data(symbol, start, end):
    """
    Fetch OHLCV data for the given stock symbol and date range.
    Args:
        symbol (str): Stock ticker symbol
        start (str): Start date (YYYY-MM-DD)
        end (str): End date (YYYY-MM-DD)
    Returns:
        pandas.DataFrame: OHLCV data indexed by date, or None on error
    """
    try:
        ticker = yf.Ticker(symbol)
        df = ticker.history(start=start, end=end, auto_adjust=False)
        if df.empty:
            return None
        df = df[['Open', 'High', 'Low', 'Close', 'Volume']]
        df.index = pd.to_datetime(df.index)
        return df
    except Exception as e:
        print(f"Error fetching data for {symbol}: {e}")
        return None 