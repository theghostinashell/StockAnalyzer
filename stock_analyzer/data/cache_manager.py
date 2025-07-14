import os
import pickle
try:
    import pandas as pd
except ImportError as e:
    print("Required package not found:", e)
    print("Please install dependencies with: pip install -r requirements.txt")
    raise

CACHE_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'cache')
os.makedirs(CACHE_DIR, exist_ok=True)

def _cache_filename(symbol, start, end):
    return os.path.join(CACHE_DIR, f"{symbol}_{start}_{end}.pkl")

def get_cached_data(symbol, start, end):
    fname = _cache_filename(symbol, start, end)
    if os.path.exists(fname):
        try:
            with open(fname, 'rb') as f:
                df = pickle.load(f)
            if isinstance(df, pd.DataFrame):
                return df
        except Exception as e:
            print(f"Error reading cache: {e}")
    return None

def set_cached_data(symbol, start, end, data):
    fname = _cache_filename(symbol, start, end)
    try:
        with open(fname, 'wb') as f:
            pickle.dump(data, f)
    except Exception as e:
        print(f"Error writing cache: {e}") 