import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from stock_analyzer.main import main

if __name__ == "__main__":
    main() 