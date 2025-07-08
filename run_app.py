#!/usr/bin/env python3
"""
Launcher script for Stock Price Visualizer.
This script ensures proper Python path setup and launches the application.
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import and run the main application
from stock_analyzer.main import main

if __name__ == "__main__":
    main() 