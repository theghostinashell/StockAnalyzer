import os
import pickle
import shutil
from datetime import datetime, timedelta
import pandas as pd

def get_cache_dir():
    cache_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'cache')
    os.makedirs(cache_dir, exist_ok=True)
    return cache_dir

def get_cache_filename(symbol, start_date, end_date, currency=None):
    if currency:
        return f"{symbol}_{start_date}_{end_date}_{currency}.pkl"
    else:
        return f"{symbol}_{start_date}_{end_date}.pkl"

def get_cached_data(symbol, start_date, end_date, currency=None):
    try:
        cache_dir = get_cache_dir()
        filename = get_cache_filename(symbol, start_date, end_date, currency)
        filepath = os.path.join(cache_dir, filename)
        
        if os.path.exists(filepath):
            # Check if cache is less than 1 hour old
            file_time = datetime.fromtimestamp(os.path.getmtime(filepath))
            if datetime.now() - file_time < timedelta(hours=1):
                with open(filepath, 'rb') as f:
                    return pickle.load(f)
    except Exception as e:
        print(f"Error reading cache: {e}")
    return None

def set_cached_data(symbol, start_date, end_date, data, currency=None):
    try:
        cache_dir = get_cache_dir()
        filename = get_cache_filename(symbol, start_date, end_date, currency)
        filepath = os.path.join(cache_dir, filename)
        
        with open(filepath, 'wb') as f:
            pickle.dump(data, f)
    except Exception as e:
        print(f"Error writing cache: {e}")

def clear_cache():
    try:
        cache_dir = get_cache_dir()
        if os.path.exists(cache_dir):
            shutil.rmtree(cache_dir)
            print("Cache cleared successfully")
    except Exception as e:
        print(f"Error clearing cache: {e}")

def get_cache_size():
    try:
        cache_dir = get_cache_dir()
        if not os.path.exists(cache_dir):
            return 0    
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(cache_dir):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                total_size += os.path.getsize(filepath)
        
        return round(total_size / (1024 * 1024), 2)  # Convert to MB
    except Exception as e:
        print(f"Error calculating cache size: {e}")
        return 0

def cleanup_old_cache():
    try:
        cache_dir = get_cache_dir()
        if not os.path.exists(cache_dir):
            return
        
        cutoff_time = datetime.now() - timedelta(hours=24)
        removed_count = 0      
        for filename in os.listdir(cache_dir):
            filepath = os.path.join(cache_dir, filename)
            if os.path.isfile(filepath):
                file_time = datetime.fromtimestamp(os.path.getmtime(filepath))
                if file_time < cutoff_time:
                    os.remove(filepath)
                    removed_count += 1       
        if removed_count > 0:
            print(f"Removed {removed_count} old cache files")
    except Exception as e:
        print(f"Error cleaning up old cache: {e}") 