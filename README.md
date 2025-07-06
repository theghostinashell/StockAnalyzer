# Stock Price Visualizer & Analyzer

A beginner-friendly Python desktop application for stock price analysis with interactive charts, technical indicators, and statistical analysis. Built with Tkinter, yfinance, pandas, and matplotlib.

## Features
- Fetches OHLCV data from Yahoo Finance (via yfinance)
- File-based caching to reduce redundant API calls
- Calculates moving averages (20, 50, 200 days)
- Computes key statistics: mean, median, volatility, returns, drawdown, Sharpe ratio
- Interactive charts (line, candlestick, OHLC) with overlays and volume
- Export charts (PNG/PDF) and data (CSV)
- Modern, intuitive GUI (Tkinter + ttk)

## Setup
1. Clone this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the app:
   ```bash
   python main.py
   ```

## Project Structure
```
stock_analyzer/
├── main.py
├── gui/
│   ├── __init__.py
│   ├── main_window.py
│   ├── chart_widget.py
│   ├── stats_panel.py
│   └── settings_dialog.py
├── data/
│   ├── __init__.py
│   ├── stock_fetcher.py
│   ├── data_processor.py
│   └── cache_manager.py
├── analysis/
│   ├── __init__.py
│   ├── technical_indicators.py
│   ├── statistics.py
│   └── risk_metrics.py
├── utils/
│   ├── __init__.py
│   ├── config.py
│   └── helpers.py
└── requirements.txt
```

## License
MIT 