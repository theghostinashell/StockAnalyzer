import tkinter as tk
from tkinter import ttk
from .chart_widget import ChartWidget
from .stats_panel import StatsPanel
from .settings_dialog import SettingsDialog
from data.stock_fetcher import fetch_stock_data
from data.cache_manager import get_cached_data, set_cached_data
from utils.helpers import load_config
import threading
import datetime
from analysis.statistics import mean_price, median_price, price_volatility, daily_returns, cumulative_returns, sharpe_ratio
from analysis.risk_metrics import max_drawdown

class MainWindow(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.configure(padding=0)
        
        # Load configuration
        self.config = load_config()
        
        self.create_widgets()
        
        # Apply initial chart type
        self.apply_chart_type()

    def create_widgets(self):
        # Header
        header = ttk.Frame(self, height=80)
        header.grid(row=0, column=0, columnspan=2, sticky="nsew")
        header.grid_propagate(False)
        title = ttk.Label(header, text="Stock Price Visualizer & Analyzer", font=("Segoe UI", 18, "bold"))
        title.pack(side=tk.LEFT, padx=20)

        # Stock symbol entry
        symbol_label = ttk.Label(header, text="Symbol:")
        symbol_label.pack(side=tk.LEFT, padx=(40, 5))
        self.symbol_var = tk.StringVar()
        symbol_entry = ttk.Entry(header, textvariable=self.symbol_var, width=12)
        symbol_entry.pack(side=tk.LEFT)

        # Date range picker (preset dropdown)
        range_label = ttk.Label(header, text="Range:")
        range_label.pack(side=tk.LEFT, padx=(30, 5))
        self.range_var = tk.StringVar(value=self.config.get("default_date_range", "6M"))
        range_options = ["1M", "3M", "6M", "1Y", "2Y", "5Y"]
        range_menu = ttk.Combobox(header, textvariable=self.range_var, values=range_options, width=5, state="readonly")
        range_menu.pack(side=tk.LEFT)

        # Analyze button
        self.analyze_btn = ttk.Button(header, text="Analyze", command=self.on_analyze)
        self.analyze_btn.pack(side=tk.LEFT, padx=(30, 5))

        # Loading indicator
        self.loading_var = tk.StringVar(value="")
        self.loading_label = ttk.Label(header, textvariable=self.loading_var, foreground="#007bff")
        self.loading_label.pack(side=tk.LEFT, padx=(10, 0))

        # Settings icon (gear)
        settings_btn = ttk.Button(header, text="⚙", width=3, command=self.on_settings)
        settings_btn.pack(side=tk.LEFT, padx=(10, 0))

        # Content
        content = ttk.Frame(self)
        content.grid(row=1, column=0, columnspan=2, sticky="nsew")
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=7)
        self.grid_columnconfigure(1, weight=3)

        # Chart Panel (70%)
        self.chart_panel = ChartWidget(content)
        self.chart_panel.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        content.grid_columnconfigure(0, weight=7)

        # Stats Panel (30%)
        self.stats_panel = StatsPanel(content)
        self.stats_panel.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        content.grid_columnconfigure(1, weight=3)

        # Footer
        footer = ttk.Frame(self, height=30)
        footer.grid(row=2, column=0, columnspan=2, sticky="nsew")
        footer.grid_propagate(False)
        self.source = ttk.Label(footer, text="Data source: Yahoo Finance", font=("Segoe UI", 9))
        self.source.pack(side=tk.LEFT, padx=10)
        self.updated = ttk.Label(footer, text="Last updated: --", font=("Segoe UI", 9))
        self.updated.pack(side=tk.LEFT, padx=20)
        self.status = ttk.Label(footer, text="Status: Disconnected", font=("Segoe UI", 9))
        self.status.pack(side=tk.RIGHT, padx=10)

    def apply_chart_type(self):
        """Apply current chart type to the chart."""
        chart_type = self.config.get("chart_type", "line")
        self.chart_panel.set_chart_type(chart_type)

    def on_settings_changed(self, new_config):
        """Handle settings changes from the settings dialog."""
        self.config = new_config
        
        # Apply new chart type
        self.apply_chart_type()
        
        # Update date range if changed
        if self.range_var.get() != new_config.get("default_date_range", "6M"):
            self.range_var.set(new_config.get("default_date_range", "6M"))

    def on_analyze(self):
        symbol = self.symbol_var.get().strip().upper()
        range_str = self.range_var.get()
        if not symbol:
            self.loading_var.set("Enter a symbol.")
            return
        self.loading_var.set("Loading...")
        self.analyze_btn.config(state=tk.DISABLED)
        self.status.config(text="Status: Connecting...")
        # Run data fetch in a thread to avoid blocking UI
        threading.Thread(target=self._fetch_and_update, args=(symbol, range_str), daemon=True).start()

    def _fetch_and_update(self, symbol, range_str):
        # Map range_str to start/end dates
        end = datetime.date.today()
        if range_str == "1M":
            start = end - datetime.timedelta(days=30)
        elif range_str == "3M":
            start = end - datetime.timedelta(days=90)
        elif range_str == "6M":
            start = end - datetime.timedelta(days=182)
        elif range_str == "1Y":
            start = end - datetime.timedelta(days=365)
        elif range_str == "2Y":
            start = end - datetime.timedelta(days=730)
        elif range_str == "5Y":
            start = end - datetime.timedelta(days=1825)
        else:
            start = end - datetime.timedelta(days=182)
        start_str = start.strftime("%Y-%m-%d")
        end_str = end.strftime("%Y-%m-%d")
        # Try cache first
        df = get_cached_data(symbol, start_str, end_str)
        if df is None:
            df = fetch_stock_data(symbol, start_str, end_str)
            if df is not None:
                set_cached_data(symbol, start_str, end_str, df)
        # Update UI in main thread
        self.after(0, self._update_ui_after_fetch, symbol, df, end_str)

    def _update_ui_after_fetch(self, symbol, df, end_str):
        if df is not None and not df.empty:
            self.chart_panel.plot_line_chart(df, symbol)
            self.loading_var.set("")
            self.status.config(text="Status: Connected")
            self.updated.config(text=f"Last updated: {end_str}")
            # Compute statistics
            close = df['Close']
            daily_ret = daily_returns(close)
            stats = {
                "Mean Price": mean_price(close),
                "Median Price": median_price(close),
                "Volatility (Std)": price_volatility(close),
                "Max Drawdown (%)": max_drawdown(close),
                "Min Price": round(close.min(), 2) if not close.empty else None,
                "Max Price": round(close.max(), 2) if not close.empty else None,
                "Cumulative Return (%)": cumulative_returns(close),
                "Avg Daily Return (%)": round(daily_ret.mean(), 2) if daily_ret is not None else None,
                "Sharpe Ratio": sharpe_ratio(close),
            }
            self.stats_panel.update_stats(stats)
        else:
            self.chart_panel.plot_placeholder()
            self.loading_var.set("No data found.")
            self.status.config(text="Status: Error")
            self.stats_panel.update_stats({})
        self.analyze_btn.config(state=tk.NORMAL)

    def on_settings(self):
        """Open settings dialog."""
        settings_dialog = SettingsDialog(self, on_settings_changed=self.on_settings_changed)
        settings_dialog.focus_set() 