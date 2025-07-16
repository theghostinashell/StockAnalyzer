import yfinance as yf
import pandas as pd

def fetch_stock_data(symbol, start_date, end_date, currency='USD'):
    try:
        ticker = yf.Ticker(symbol)
        df = ticker.history(start=start_date, end=end_date, auto_adjust=False)
        if df.empty:
            return None
        df = df[['Open', 'High', 'Low', 'Close', 'Volume']]
        df.index = pd.to_datetime(df.index)
        return df
    except Exception:
        return None

def get_company_name(symbol):
    return symbol.upper()

def get_available_currencies():
    return {'USD': {'name': 'US Dollar', 'symbol': '$'}}

def get_currency_symbol(currency_code):
    return {'USD': '$'}.get(currency_code, '$')
