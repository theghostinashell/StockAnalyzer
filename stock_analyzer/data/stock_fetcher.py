try:
    import yfinance as yf
except ImportError:
    raise ImportError("yfinance is not installed. Please install it with 'pip install yfinance'.")
try:
    import pandas as pd
except ImportError:
    raise ImportError("pandas is not installed. Please install it with 'pip install pandas'.")
import requests
import json
import os
from typing import Dict, List, Optional
import time

def fetch_stock_data(symbol, start_date, end_date, currency='USD'):
    """Fetch stock data with currency conversion support."""
    try:
        normalized_symbol = normalize_symbol(symbol)
        ticker = yf.Ticker(normalized_symbol)
        
        # Get data in the stock's native currency first
        df = ticker.history(start=start_date, end=end_date)
        
        if df.empty:
            return None
        
        # Get the stock's native currency
        stock_info = ticker.info
        native_currency = stock_info.get('currency', 'USD')

        # Step 1: Convert to USD if needed
        if native_currency != 'USD':
            try:
                currency_pair = f"{native_currency}USD=X"
                exchange_ticker = yf.Ticker(currency_pair)
                exchange_data = exchange_ticker.history(start=start_date, end=end_date)
                if not exchange_data.empty:
                    latest_rate = exchange_data['Close'].iloc[-1]
                    price_columns = ['Open', 'High', 'Low', 'Close']
                    for col in price_columns:
                        if col in df.columns:
                            df[col] = df[col] * latest_rate
                    print(f"Converted {native_currency} to USD using rate: {latest_rate:.4f}")
                else:
                    print(f"Could not get exchange rate for {currency_pair}, using native currency")
            except Exception as e:
                print(f"Currency conversion error (to USD): {e}, using native currency")

        # Step 2: If user selected a different currency, convert from USD to that currency
        if currency != 'USD':
            try:
                currency_pair = f"USD{currency}=X"
                exchange_ticker = yf.Ticker(currency_pair)
                exchange_data = exchange_ticker.history(start=start_date, end=end_date)
                if not exchange_data.empty:
                    latest_rate = exchange_data['Close'].iloc[-1]
                    price_columns = ['Open', 'High', 'Low', 'Close']
                    for col in price_columns:
                        if col in df.columns:
                            df[col] = df[col] * latest_rate
                    print(f"Converted USD to {currency} using rate: {latest_rate:.4f}")
                else:
                    print(f"Could not get exchange rate for {currency_pair}, using USD")
            except Exception as e:
                print(f"Currency conversion error (to {currency}): {e}, using USD")
        return df
    except Exception as e:
        print(f"Error fetching data for {symbol}: {e}")
        return None

def normalize_symbol(symbol: str) -> str:
    """
    Normalize symbol for different exchanges.
    Handles various exchange suffixes and formats.
    """
    symbol = symbol.upper().strip()
    
    # Exchange-specific symbol mappings
    exchange_mappings = {
        # Indian exchanges
        'NSE': '.NS',  # National Stock Exchange
        'BSE': '.BO',  # Bombay Stock Exchange
        
        # London Stock Exchange
        'LSE': '.L',
        
        # Tokyo Stock Exchange
        'TSE': '.T',
        
        # US exchanges (default, no suffix needed)
        'NYSE': '',
        'NASDAQ': '',
    }
    
    # Check if symbol already has exchange suffix
    if any(symbol.endswith(suffix) for suffix in ['.NS', '.BO', '.L', '.T']):
        return symbol
    
    # For Indian stocks without suffix, default to NSE
    if symbol in get_indian_stocks():
        return symbol + '.NS'
    
    # For London stocks without suffix, add .L
    if symbol in get_london_stocks():
        return symbol + '.L'
    
    # For Tokyo stocks without suffix, add .T
    if symbol in get_tokyo_stocks():
        return symbol + '.T'
    
    # US stocks (default)
    return symbol

def get_company_name(symbol):
    """Get company name with enhanced multi-exchange support."""
    try:
        normalized_symbol = normalize_symbol(symbol)
        ticker = yf.Ticker(normalized_symbol)
        info = ticker.info
        
        # Try different name fields
        name = info.get('longName') or info.get('shortName') or info.get('name')
        if name:
            return name
        
        # Fallback to symbol
        return symbol.upper()
    except Exception as e:
        print(f"Error getting company name for {symbol}: {e}")
        return symbol.upper()

def get_available_currencies():
    """Get available currencies for different exchanges."""
    return {
        'USD': {'name': 'US Dollar', 'symbol': '$'},
        'GBP': {'name': 'British Pound', 'symbol': '£'},
        'JPY': {'name': 'Japanese Yen', 'symbol': '¥'},
        'INR': {'name': 'Indian Rupee', 'symbol': '₹'},
        'EUR': {'name': 'Euro', 'symbol': '€'}
    }

def get_currency_symbol(currency_code):
    """Get currency symbol."""
    return {
        'USD': '$', 'GBP': '£', 'JPY': '¥',
        'INR': '₹', 'EUR': '€'
    }.get(currency_code, '$')

def get_exchange_for_symbol(symbol: str) -> str:
    """Determine which exchange a symbol belongs to."""
    symbol = symbol.upper().strip()
    
    # Check for exchange suffixes
    if symbol.endswith('.NS') or symbol.endswith('.BO'):
        return 'NSE' if symbol.endswith('.NS') else 'BSE'
    elif symbol.endswith('.L'):
        return 'LSE'
    elif symbol.endswith('.T'):
        return 'TSE'
    else:
        # Check against known stock lists
        if symbol in get_us_stocks():
            return 'NYSE' if symbol in get_nyse_stocks() else 'NASDAQ'
        elif symbol in get_indian_stocks():
            return 'NSE'
        elif symbol in get_london_stocks():
            return 'LSE'
        elif symbol in get_tokyo_stocks():
            return 'TSE'
        else:
            return 'NYSE'  # Default to NYSE

def get_us_stocks() -> List[str]:
    """Get major US stocks."""
    return [
        # NYSE
        "AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NVDA", "BRK-B", "JPM", "JNJ",
        "V", "PG", "UNH", "HD", "MA", "DIS", "PYPL", "BAC", "CRM", "NFLX", "CMCSA", 
        "PFE", "ABT", "KO", "PEP", "TMO", "AVGO", "T", "ABBV", "WMT", "COST", "LLY",
        # NASDAQ
        "INTC", "AMD", "CSCO", "QCOM", "INTU", "ORCL", "TXN", "MU", "ADP", "ISRG", 
        "REGN", "GILD", "VRTX", "MDLZ", "KLAC", "SNPS", "MELI", "ZM", "PTON", "BYND"
    ]

def get_nyse_stocks() -> List[str]:
    """Get major NYSE stocks."""
    return [
        "AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NVDA", "BRK-B", "JPM", "JNJ",
        "V", "PG", "UNH", "HD", "MA", "DIS", "PYPL", "BAC", "CRM", "NFLX", "CMCSA", 
        "PFE", "ABT", "KO", "PEP", "TMO", "AVGO", "T", "ABBV", "WMT", "COST", "LLY"
    ]

def get_indian_stocks() -> List[str]:
    """Get major Indian stocks (NSE)."""
    return [
        "RELIANCE", "TCS", "HDFCBANK", "INFY", "ICICIBANK", "HINDUNILVR", "ITC", "SBIN", 
        "BHARTIARTL", "KOTAKBANK", "AXISBANK", "ASIANPAINT", "MARUTI", "HCLTECH", 
        "SUNPHARMA", "TATAMOTORS", "WIPRO", "ULTRACEMCO", "TITAN", "BAJFINANCE",
        "NESTLEIND", "POWERGRID", "BAJAJFINSV", "NTPC", "ONGC", "COALINDIA", 
        "JSWSTEEL", "TECHM", "ADANIENT", "HINDALCO", "ADANIPORTS", "TATASTEEL",
        "BRITANNIA", "SHREECEM", "HEROMOTOCO", "INDUSINDBK", "DIVISLAB", "EICHERMOT",
        "DRREDDY", "CIPLA", "BPCL", "HCLTECH", "TATACONSUM", "VEDL", "GRASIM"
    ]

def get_london_stocks() -> List[str]:
    """Get major London Stock Exchange stocks."""
    return [
        "HSBA", "GSK", "ULVR", "BHP", "RIO", "REL", "LSEG", "CRH", "PRU", "MB",
        "SHEL", "BP", "VOD", "BT-A", "BARC", "LLOY", "RKT", "WPP", "AAL", "GE",
        "CNA", "SGE", "IMB", "RKT", "WPP", "AAL", "SGE", "CNA", "RKT", "WPP"
    ]

def get_tokyo_stocks() -> List[str]:
    """Get major Tokyo Stock Exchange stocks."""
    return [
        "7203", "6758", "6861", "9984", "7974", "6954", "836", "9433", "4502",
        "4519", "6501", "6594", "7733", "4911", "7269", "6098", "4063", "4568",
        "4661", "4755", "4689", "474", "4543", "4578", "4689", "474", "4543"
    ]

def get_exchange_stocks(exchange: str) -> List[str]:
    """Get stocks for a specific exchange."""
    exchange_stocks = {
        "NYSE": get_nyse_stocks(),
        "NASDAQ": [stock for stock in get_us_stocks() if stock not in get_nyse_stocks()],
        "LSE": get_london_stocks(),
        "TSE": get_tokyo_stocks(),
        "NSE": get_indian_stocks(),
        "BSE": get_indian_stocks()  # Same stocks, different exchange
    }
    return exchange_stocks.get(exchange, [])

def validate_symbol(symbol: str) -> bool:
    """Validate if a symbol exists and has data."""
    try:
        normalized_symbol = normalize_symbol(symbol)
        ticker = yf.Ticker(normalized_symbol)
        info = ticker.info
        
        # Check if we can get basic info
        return info.get('regularMarketPrice') is not None or info.get('currentPrice') is not None
    except Exception as e:
        print(f"Validation error for {symbol}: {e}")
        return False

def get_all_exchange_stocks() -> Dict[str, List[str]]:
    """Get stocks from all major exchanges."""
    exchanges = ["NYSE", "NASDAQ", "LSE", "TSE", "NSE"]
    all_stocks = {}
    
    for exchange in exchanges:
        print(f"Getting {exchange} stocks...")
        stocks = get_exchange_stocks(exchange)
        all_stocks[exchange] = stocks
    
    return all_stocks

def get_stock_info(symbol: str) -> Dict:
    """Get comprehensive stock information."""
    try:
        normalized_symbol = normalize_symbol(symbol)
        ticker = yf.Ticker(normalized_symbol)
        info = ticker.info
        
        return {
            'symbol': symbol,
            'name': info.get('longName') or info.get('shortName') or symbol.upper(),
            'exchange': get_exchange_for_symbol(symbol),
            'currency': info.get('currency', 'USD'),
            'current_price': info.get('regularMarketPrice') or info.get('currentPrice'),
            'market_cap': info.get('marketCap'),
            'volume': info.get('volume'),
            'pe_ratio': info.get('trailingPE'),
            'dividend_yield': info.get('dividendYield'),
            'sector': info.get('sector'),
            'industry': info.get('industry')
        }
    except Exception as e:
        print(f"Error getting stock info for {symbol}: {e}")
        return {
            'symbol': symbol,
            'name': symbol.upper(),
            'exchange': get_exchange_for_symbol(symbol),
            'currency': 'USD',
            'current_price': None,
            'market_cap': None,
            'volume': None,
            'pe_ratio': None,
            'dividend_yield': None,
            'sector': None,
            'industry': None
        }

def get_usd_to_currency_rate(currency_code):
    """
    Fetch the latest USD to selected currency rate using yfinance.
    Returns 1.0 if currency_code is USD or on error.
    """
    if currency_code == 'USD':
        return 1.0
    try:
        currency_pair = f"USD{currency_code}=X"
        ticker = yf.Ticker(currency_pair)
        data = ticker.history(period="1d")
        if not data.empty:
            return float(data['Close'].iloc[-1])
    except Exception as e:
        print(f"Error fetching USD to {currency_code} rate: {e}")
    return 1.0
