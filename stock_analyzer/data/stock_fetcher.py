"""
Fetches OHLCV stock data from Yahoo Finance using yfinance.
"""
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import requests
import time

def get_company_name(symbol):
    """
    Get company name for a given ticker symbol.
    Uses multiple fallback methods to ensure we get the name.
    """
    try:
        # Method 1: Try yfinance first (most reliable)
        ticker = yf.Ticker(symbol)
        info = ticker.info
        if 'longName' in info and info['longName']:
            return info['longName']
        elif 'shortName' in info and info['shortName']:
            return info['shortName']
        
        # Method 2: Try Alpha Vantage API (free tier)
        # Note: This requires an API key, but we'll use a fallback
        try:
            # Using a free stock info API
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                if 'chart' in data and 'result' in data['chart'] and data['chart']['result']:
                    result = data['chart']['result'][0]
                    if 'meta' in result and 'shortName' in result['meta']:
                        return result['meta']['shortName']
        except:
            pass
        
        # Method 3: Common company name mapping for major stocks
        company_names = {
            'AAPL': 'Apple Inc.',
            'MSFT': 'Microsoft Corporation',
            'GOOGL': 'Alphabet Inc.',
            'AMZN': 'Amazon.com Inc.',
            'TSLA': 'Tesla Inc.',
            'NVDA': 'NVIDIA Corporation',
            'META': 'Meta Platforms Inc.',
            'BRK-B': 'Berkshire Hathaway Inc.',
            'BRK.B': 'Berkshire Hathaway Inc.',
            'JPM': 'JPMorgan Chase & Co.',
            'JNJ': 'Johnson & Johnson',
            'V': 'Visa Inc.',
            'PG': 'Procter & Gamble Co.',
            'HD': 'Home Depot Inc.',
            'MA': 'Mastercard Inc.',
            'DIS': 'Walt Disney Co.',
            'PYPL': 'PayPal Holdings Inc.',
            'ADBE': 'Adobe Inc.',
            'CRM': 'Salesforce Inc.',
            'NFLX': 'Netflix Inc.',
            'INTC': 'Intel Corporation',
            'VZ': 'Verizon Communications Inc.',
            'KO': 'Coca-Cola Co.',
            'PFE': 'Pfizer Inc.',
            'TMO': 'Thermo Fisher Scientific Inc.',
            'ABT': 'Abbott Laboratories',
            'WMT': 'Walmart Inc.',
            'MRK': 'Merck & Co. Inc.',
            'BAC': 'Bank of America Corp.',
            'XOM': 'Exxon Mobil Corporation',
            'CVX': 'Chevron Corporation',
            'LLY': 'Eli Lilly and Company',
            'AVGO': 'Broadcom Inc.',
            'PEP': 'PepsiCo Inc.',
            'COST': 'Costco Wholesale Corporation',
            'ABBV': 'AbbVie Inc.',
            'TXN': 'Texas Instruments Inc.',
            'ACN': 'Accenture plc',
            'DHR': 'Danaher Corporation',
            'VRTX': 'Vertex Pharmaceuticals Inc.',
            'WFC': 'Wells Fargo & Company',
            'NEE': 'NextEra Energy Inc.',
            'PM': 'Philip Morris International Inc.',
            'RTX': 'Raytheon Technologies Corporation',
            'T': 'AT&T Inc.',
            'QCOM': 'QUALCOMM Incorporated',
            'UNH': 'UnitedHealth Group Incorporated',
            'LOW': 'Lowe\'s Companies Inc.',
            'BMY': 'Bristol-Myers Squibb Company',
            'SPGI': 'S&P Global Inc.',
            'HON': 'Honeywell International Inc.',
            'AMGN': 'Amgen Inc.',
            'ISRG': 'Intuitive Surgical Inc.',
            'PLD': 'Prologis Inc.',
            'ADI': 'Analog Devices Inc.',
            'GILD': 'Gilead Sciences Inc.',
            'REGN': 'Regeneron Pharmaceuticals Inc.',
            'MDLZ': 'Mondelez International Inc.',
            'CMCSA': 'Comcast Corporation',
            'KLAC': 'KLA Corporation',
            'PANW': 'Palo Alto Networks Inc.',
            'CHTR': 'Charter Communications Inc.',
            'MAR': 'Marriott International Inc.',
            'ORCL': 'Oracle Corporation',
            'MNST': 'Monster Beverage Corporation',
            'SNPS': 'Synopsys Inc.',
            'CDNS': 'Cadence Design Systems Inc.',
            'CPRT': 'Copart Inc.',
            'PAYX': 'Paychex Inc.',
            'MELI': 'MercadoLibre Inc.',
            'CTAS': 'Cintas Corporation',
            'ADP': 'Automatic Data Processing Inc.',
            'ODFL': 'Old Dominion Freight Line Inc.',
            'ROST': 'Ross Stores Inc.',
            'BIIB': 'Biogen Inc.',
            'DXCM': 'DexCom Inc.',
            'EXC': 'Exelon Corporation',
            'AEP': 'American Electric Power Company Inc.',
            'SO': 'Southern Company',
            'DUK': 'Duke Energy Corporation',
            'D': 'Dominion Energy Inc.',
            'SRE': 'Sempra Energy',
            'XEL': 'Xcel Energy Inc.',
            'WEC': 'WEC Energy Group Inc.',
            'DTE': 'DTE Energy Company',
            'AEE': 'Ameren Corporation',
            'CMS': 'CMS Energy Corporation',
            'PEG': 'Public Service Enterprise Group Inc.',
            'ED': 'Consolidated Edison Inc.',
            'EIX': 'Edison International',
            'PCG': 'PG&E Corporation',
            'NEE': 'NextEra Energy Inc.',
            'D': 'Dominion Energy Inc.',
            'SO': 'Southern Company',
            'DUK': 'Duke Energy Corporation',
            'AEP': 'American Electric Power Company Inc.',
            'EXC': 'Exelon Corporation',
            'SRE': 'Sempra Energy',
            'XEL': 'Xcel Energy Inc.',
            'WEC': 'WEC Energy Group Inc.',
            'DTE': 'DTE Energy Company',
            'AEE': 'Ameren Corporation',
            'CMS': 'CMS Energy Corporation',
            'PEG': 'Public Service Enterprise Group Inc.',
            'ED': 'Consolidated Edison Inc.',
            'EIX': 'Edison International',
            'PCG': 'PG&E Corporation'
        }
        
        # Handle BRK.B -> BRK-B conversion for yfinance
        if symbol == 'BRK.B':
            symbol = 'BRK-B'
        
        if symbol in company_names:
            return company_names[symbol]
        
        # Fallback: return the symbol itself
        return symbol.upper()
        
    except Exception as e:
        # If all methods fail, return the symbol
        return symbol.upper()

def fetch_stock_data(symbol, start_date, end_date):
    """
    Fetch OHLCV data for the given stock symbol and date range.
    Args:
        symbol (str): Stock ticker symbol
        start_date (str): Start date (YYYY-MM-DD)
        end_date (str): End date (YYYY-MM-DD)
    Returns:
        pandas.DataFrame: OHLCV data indexed by date, or None on error
    """
    try:
        # Handle BRK.B -> BRK-B conversion for yfinance
        if symbol == 'BRK.B':
            symbol = 'BRK-B'
        
        ticker = yf.Ticker(symbol)
        df = ticker.history(start=start_date, end=end_date, auto_adjust=False)
        if df.empty:
            return None
        df = df[['Open', 'High', 'Low', 'Close', 'Volume']]
        df.index = pd.to_datetime(df.index)
        return df
    except Exception as e:
        print(f"Error fetching data for {symbol}: {e}")
        return None 