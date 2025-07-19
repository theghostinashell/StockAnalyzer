import tkinter as tk
from tkinter import ttk
from stock_analyzer.gui.chart_widget import ChartWidget
from stock_analyzer.gui.stats_panel import StatsPanel
from stock_analyzer.gui.settings_dialog import SettingsDialog
from stock_analyzer.data.stock_fetcher import fetch_stock_data, get_company_name, get_available_currencies, get_currency_symbol
from stock_analyzer.data.cache_manager import get_cached_data, set_cached_data
from stock_analyzer.utils.helpers import load_config
import threading
import datetime
from stock_analyzer.analysis.statistics import (
    mean_price, median_price, price_volatility, daily_returns, cumulative_returns, 
    sharpe_ratio, value_at_risk
)
from stock_analyzer.analysis.risk_metrics import max_drawdown
from stock_analyzer.analysis.recommendations import analyze_timeframe, generate_recommendation, get_timeframe_data

class MainWindow(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.configure(padding=0)
        
        # Load configuration
        self.config = load_config()
        
        # Initialize currency
        self.current_currency = 'USD'
        
        # Configure modern style
        self.setup_modern_style()
        
        # Fix title bar theme
        self.fix_title_bar_theme()
        
        self.create_widgets()
        
        # Apply initial chart type
        self.apply_chart_type()

    def fix_title_bar_theme(self):
        """Fix the title bar theme to match the current mode."""
        try:
            # Get the root window
            root = self.winfo_toplevel()
            
            # Set title bar colors based on theme
            if self.theme_mode == "dark":
                # Dark theme title bar
                root.configure(bg='#1C1C1E')
                # For Windows, we can try to set the title bar color
                try:
                    root.attributes('-alpha', 0.99)  # Force redraw
                    root.attributes('-alpha', 1.0)
                except:
                    pass
            else:
                # Light theme title bar
                root.configure(bg='#F5F5F7')
                try:
                    root.attributes('-alpha', 0.99)  # Force redraw
                    root.attributes('-alpha', 1.0)
                except:
                    pass
        except Exception as e:
            print(f"Could not fix title bar theme: {e}")

    def setup_modern_style(self):
        """Setup modern Apple-style appearance."""
        self.style = ttk.Style()
        
        # Define font family with fallbacks
        self.font_family = ("SF Pro Display", "Segoe UI", "Helvetica", "Arial", "sans-serif")
        
        # Initialize theme mode
        self.theme_mode = self.config.get("theme_mode", "light")
        
        # Apply theme
        self.apply_theme()
        
        # Configure the main frame
        self.configure(style="Modern.TFrame")

    def apply_theme(self):
        """Apply light or dark theme."""
        if self.theme_mode == "dark":
            self._setup_dark_theme()
        else:
            self._setup_light_theme()
        
        # Update input widget colors
        self._update_input_widget_colors()
        
        # Fix title bar theme
        self.fix_title_bar_theme()

    def _setup_light_theme(self):
        """Setup light theme colors."""
        # Configure modern light colors
        self.style.configure("Modern.TFrame", background="#F5F5F7")
        self.style.configure("Modern.TLabel", background="#F5F5F7", foreground="#1D1D1F", font=(self.font_family[1], 10))
        self.style.configure("Title.TLabel", background="#F5F5F7", foreground="#1D1D1F", font=(self.font_family[1], 24, "bold"))
        self.style.configure("Header.TLabel", background="#F5F5F7", foreground="#1D1D1F", font=(self.font_family[1], 14, "bold"))
        
        # Modern button style
        self.style.configure("Modern.TButton", 
                           background="#007AFF", 
                           foreground="white", 
                           font=(self.font_family[1], 11, "bold"),
                           borderwidth=0,
                           focuscolor="none")
        self.style.map("Modern.TButton",
                     background=[("active", "#0056CC"), ("pressed", "#0056CC")])
        
        # Modern entry style
        self.style.configure("Modern.TEntry", 
                           fieldbackground="white", 
                           borderwidth=1, 
                           relief="flat",
                           font=(self.font_family[1], 11))
        
        # Modern combobox style
        self.style.configure("Modern.TCombobox", 
                           fieldbackground="white", 
                           borderwidth=1, 
                           relief="flat",
                           font=(self.font_family[1], 11))
        
        # Settings button style
        self.style.configure("Settings.TButton", 
                           background="#007AFF", 
                           foreground="white", 
                           font=(self.font_family[1], 11, "bold"),
                           borderwidth=0,
                           focuscolor="none")
        self.style.map("Settings.TButton",
                     background=[("active", "#0056CC"), ("pressed", "#0056CC")])

    def _setup_dark_theme(self):
        """Setup dark theme colors."""
        # Configure modern dark colors
        self.style.configure("Modern.TFrame", background="#1C1C1E")
        self.style.configure("Modern.TLabel", background="#1C1C1E", foreground="#FFFFFF", font=(self.font_family[1], 10))
        self.style.configure("Title.TLabel", background="#1C1C1E", foreground="#FFFFFF", font=(self.font_family[1], 24, "bold"))
        self.style.configure("Header.TLabel", background="#1C1C1E", foreground="#FFFFFF", font=(self.font_family[1], 14, "bold"))
        
        # Modern button style
        self.style.configure("Modern.TButton", 
                           background="#0A84FF", 
                           foreground="white", 
                           font=(self.font_family[1], 11, "bold"),
                           borderwidth=0,
                           focuscolor="none")
        self.style.map("Modern.TButton",
                     background=[("active", "#0056CC"), ("pressed", "#0056CC")])
        
        # Modern entry style
        self.style.configure("Modern.TEntry", 
                           fieldbackground="#2C2C2E", 
                           borderwidth=1, 
                           relief="flat",
                           font=(self.font_family[1], 11))
        
        # Modern combobox style
        self.style.configure("Modern.TCombobox", 
                           fieldbackground="#2C2C2E", 
                           borderwidth=1, 
                           relief="flat",
                           font=(self.font_family[1], 11))
        
        # Settings button style
        self.style.configure("Settings.TButton", 
                           background="#0A84FF", 
                           foreground="white", 
                           font=(self.font_family[1], 11, "bold"),
                           borderwidth=0,
                           focuscolor="none")
        self.style.map("Settings.TButton",
                     background=[("active", "#0056CC"), ("pressed", "#0056CC")])

    def create_widgets(self):
        # Define font family with fallbacks
        font_family = ("SF Pro Display", "Segoe UI", "Helvetica", "Arial", "sans-serif")
        # Main container with padding
        main_container = ttk.Frame(self, style="Modern.TFrame", padding=20)
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Header with modern design
        header = ttk.Frame(main_container, style="Modern.TFrame")
        header.pack(fill=tk.X, pady=(0, 20))
        
        # Title
        title = ttk.Label(header, text="Stock Analyzer", style="Title.TLabel")
        title.pack(anchor=tk.W, pady=(0, 20))
        
        # Control panel with modern design
        control_panel = ttk.Frame(header, style="Modern.TFrame")
        control_panel.pack(fill=tk.X)

        # Stock symbol entry with modern styling
        symbol_frame = ttk.Frame(control_panel, style="Modern.TFrame")
        symbol_frame.pack(side=tk.LEFT, padx=(0, 15))
        
        symbol_label = ttk.Label(symbol_frame, text="Symbol", style="Modern.TLabel")
        symbol_label.pack(anchor=tk.W, pady=(0, 5))
        
        self.symbol_var = tk.StringVar()
        self.symbol_entry = ttk.Entry(symbol_frame, textvariable=self.symbol_var, width=15, style="Modern.TEntry")
        self.symbol_entry.pack(fill=tk.X)
        
        # Bind Enter key to analyze function
        self.symbol_entry.bind('<Return>', lambda event: self.on_analyze())


        
        # Currency dropdown
        currency_frame = ttk.Frame(control_panel, style="Modern.TFrame")
        currency_frame.pack(side=tk.LEFT, padx=(0, 15))
        
        currency_label = ttk.Label(currency_frame, text="Currency", style="Modern.TLabel")
        currency_label.pack(anchor=tk.W, pady=(0, 5))
        
        self.currency_var = tk.StringVar(value=self.current_currency)
        currencies = get_available_currencies()
        currency_options = [f"{code} - {currencies[code]['name']}" for code in currencies.keys()]
        self.currency_menu = ttk.Combobox(currency_frame, textvariable=self.currency_var, 
                                        values=currency_options, width=15, state="readonly", style="Modern.TCombobox")
        self.currency_menu.pack(fill=tk.X)
        
        # Bind currency change to automatic update
        self.currency_menu.bind('<<ComboboxSelected>>', self.on_currency_changed)

        # Date range picker with modern styling
        range_frame = ttk.Frame(control_panel, style="Modern.TFrame")
        range_frame.pack(side=tk.LEFT, padx=(0, 15))
        
        range_label = ttk.Label(range_frame, text="Time Range", style="Modern.TLabel")
        range_label.pack(anchor=tk.W, pady=(0, 5))
        
        self.range_var = tk.StringVar(value=self.config.get("default_date_range", "6M"))
        range_options = ["1M", "3M", "6M", "1Y", "2Y", "5Y"]
        self.range_menu = ttk.Combobox(range_frame, textvariable=self.range_var, 
                                 values=range_options, width=8, state="readonly", style="Modern.TCombobox")
        self.range_menu.pack(fill=tk.X)
        
        # Bind timeframe change to automatic analysis
        self.range_menu.bind('<<ComboboxSelected>>', self.on_timeframe_changed)
        
        # Analyze button with modern styling
        button_frame = ttk.Frame(control_panel, style="Modern.TFrame")
        button_frame.pack(side=tk.LEFT, padx=(0, 15))

        button_label = ttk.Label(button_frame, text="", style="Modern.TLabel")
        button_label.pack(anchor=tk.W, pady=(0, 5))
        
        # Set initial button colors based on theme
        if self.theme_mode == "dark":
            btn_bg = "#2C2C2E"
            btn_fg = "#0A84FF"
            btn_active_bg = "#1C1C1E"
            btn_active_fg = "#0056CC"
        else:
            btn_bg = "white"
            btn_fg = "#007AFF"
            btn_active_bg = "#F5F5F7"
            btn_active_fg = "#0056CC"
        
        self.analyze_btn = tk.Button(button_frame, text="Analyze", command=self.on_analyze, 
                                    bg=btn_bg, fg=btn_fg, activebackground=btn_active_bg, activeforeground=btn_active_fg, 
                                    font=(font_family[1], 11, "bold"), relief="flat", bd=0, padx=16, pady=6, cursor="hand2")
        self.analyze_btn.pack()
        
        # Loading indicator with modern styling
        loading_frame = ttk.Frame(control_panel, style="Modern.TFrame")
        loading_frame.pack(side=tk.LEFT, padx=(0, 15))

        loading_label = ttk.Label(loading_frame, text="", style="Modern.TLabel")
        loading_label.pack(anchor=tk.W, pady=(0, 5))
        
        self.loading_var = tk.StringVar(value="")
        self.loading_label = ttk.Label(loading_frame, textvariable=self.loading_var, 
                                     style="Modern.TLabel", foreground="#007AFF")
        self.loading_label.pack()
        
        # Theme toggle button with modern styling
        theme_frame = ttk.Frame(control_panel, style="Modern.TFrame")
        theme_frame.pack(side=tk.RIGHT, padx=(0, 10))
        
        theme_label = ttk.Label(theme_frame, text="", style="Modern.TLabel")
        theme_label.pack(anchor=tk.W, pady=(0, 5))

        # Set initial theme button text and colors
        theme_icon = "☀️" if self.theme_mode == "dark" else "🌙"
        self.theme_btn = tk.Button(theme_frame, text=theme_icon, width=3, command=self.toggle_theme, 
                                  bg=btn_bg, fg=btn_fg, activebackground=btn_active_bg, activeforeground=btn_active_fg, 
                                  font=(font_family[1], 11, "bold"), relief="flat", bd=0, padx=8, pady=4, cursor="hand2")
        self.theme_btn.pack(anchor=tk.CENTER)

        # Chart type toggle button (replaces settings)
        chart_frame = ttk.Frame(control_panel, style="Modern.TFrame")
        chart_frame.pack(side=tk.RIGHT, padx=(0, 10))
        
        chart_label = ttk.Label(chart_frame, text="", style="Modern.TLabel")
        chart_label.pack(anchor=tk.W, pady=(0, 5))
        
        # Initialize chart type
        self.current_chart_type = self.config.get("chart_type", "line")
        chart_icon = "📊" if self.current_chart_type == "line" else "🕯️"
        self.chart_btn = tk.Button(chart_frame, text=chart_icon, width=3, command=self.toggle_chart_type, 
                                  bg=btn_bg, fg=btn_fg, activebackground=btn_active_bg, activeforeground=btn_active_fg, 
                                  font=(font_family[1], 11, "bold"), relief="flat", bd=0, padx=8, pady=4, cursor="hand2")
        self.chart_btn.pack(anchor=tk.CENTER)

        # Content area with modern design
        content = ttk.Frame(main_container, style="Modern.TFrame")
        content.pack(fill=tk.BOTH, expand=True)

        # Chart Panel (70%) with modern styling
        chart_container = ttk.Frame(content, style="Modern.TFrame")
        chart_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        self.chart_label = ttk.Label(chart_container, text="Price Chart", style="Header.TLabel")
        self.chart_label.pack(anchor=tk.W, pady=(0, 10))
        
        self.chart_panel = ChartWidget(chart_container)
        self.chart_panel.pack(fill=tk.BOTH, expand=True)

        # Stats Panel (30%) with modern styling
        stats_container = ttk.Frame(content, style="Modern.TFrame")
        stats_container.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(10, 0))
        
        self.stats_panel = StatsPanel(stats_container)
        self.stats_panel.pack(fill=tk.BOTH, expand=True)

        # Footer with modern design
        footer = ttk.Frame(main_container, style="Modern.TFrame")
        footer.pack(fill=tk.X, pady=(20, 0))
        
        # Footer content
        footer_content = ttk.Frame(footer, style="Modern.TFrame")
        footer_content.pack(fill=tk.X)
        
        self.source = ttk.Label(footer_content, text="Data source: Yahoo Finance", 
                               style="Modern.TLabel", font=(font_family[1], 9))
        self.source.pack(side=tk.LEFT)
        
        self.updated = ttk.Label(footer_content, text="Last updated: --", 
                                style="Modern.TLabel", font=(font_family[1], 9))
        self.updated.pack(side=tk.LEFT, padx=(20, 0))
        
        self.status = ttk.Label(footer_content, text="Status: Ready", 
                               style="Modern.TLabel", font=(font_family[1], 9))
        self.status.pack(side=tk.RIGHT)

    def toggle_chart_type(self):
        """Toggle between line and candlestick chart types."""
        if self.current_chart_type == "line":
            self.current_chart_type = "candlestick"
            self.chart_btn.config(text="🕯️")
        else:
            self.current_chart_type = "line"
            self.chart_btn.config(text="📊")
        
        # Update config
        self.config["chart_type"] = self.current_chart_type
        
        # Apply new chart type
        self.apply_chart_type()

    def apply_chart_type(self):
        """Apply current chart type to the chart."""
        self.chart_panel.set_chart_type(self.current_chart_type)

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
        
        # Get selected currency
        currency_selection = self.currency_var.get()
        self.current_currency = currency_selection.split(' - ')[0] if ' - ' in currency_selection else 'USD'
        
        if not symbol:
            self.loading_var.set("Enter a symbol.")
            return
        self.loading_var.set("Loading...")
        self.analyze_btn.config(state=tk.DISABLED)
        self.status.config(text="Status: Connecting...")
        # Run data fetch in a thread to avoid blocking UI
        threading.Thread(target=self._fetch_and_update, args=(symbol, range_str), daemon=True).start()

    def on_timeframe_changed(self, event=None):
        """Handle timeframe change - automatically analyze if symbol is entered."""
        symbol = self.symbol_var.get().strip().upper()
        if symbol:
            # Only auto-analyze if there's already a symbol entered
            self.on_analyze()

    def on_currency_changed(self, event=None):
        """Handle currency change - update display immediately if data is available."""
        currency_selection = self.currency_var.get()
        self.current_currency = currency_selection.split(' - ')[0] if ' - ' in currency_selection else 'USD'
        
        # Update chart currency
        self.chart_panel.set_currency(self.current_currency)
        
        # Update stats panel currency
        self.stats_panel.set_currency(self.current_currency)

    def _fetch_and_update(self, symbol, range_str):
        try:
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
                df = fetch_stock_data(symbol, start_str, end_str, self.current_currency)
                if df is not None:
                    set_cached_data(symbol, start_str, end_str, df)
            # Update UI in main thread
            self.after(0, self._update_ui_after_fetch, symbol, df, end_str)
        except Exception as e:
            # Handle any exceptions and re-enable the button
            self.after(0, self._handle_fetch_error, str(e))
    
    def _handle_fetch_error(self, error_message):
        """Handle fetch errors and re-enable the analyze button."""
        self.analyze_btn.config(state=tk.NORMAL)
        self.loading_var.set(f"Error: {error_message}")
        self.status.config(text="Status: Error")

    def _calculate_statistics(self, df):
        """Calculate basic statistics for the stock data."""
        if df is None or df.empty:
            return {}
        
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
            "Value at Risk (5%)": value_at_risk(close, 0.05),
            "Current Price": round(close.iloc[-1], 2),
            "52-Week High": round(close.max(), 2) if not close.empty else None,
            "52-Week Low": round(close.min(), 2) if not close.empty else None,
        }
        return stats

    def _update_ui_after_fetch(self, symbol, df, end_str):
        """Update UI with fetched data."""
        # Always re-enable the analyze button
        self.analyze_btn.config(state=tk.NORMAL)
        
        if df is None or df.empty:
            self.loading_var.set("Error: No data found")
            self.status.config(text="Status: Error")
            return
        
        # Get company name
        company_name = get_company_name(symbol)
        
        # Update chart label with company name
        self.chart_label.config(text=f"{company_name} Price Chart")
        
        # Set currency for chart
        self.chart_panel.set_currency(self.current_currency)
        
        # Update chart
        self.chart_panel.plot_data(df, symbol)
        
        # Calculate statistics
        stats_dict = self._calculate_statistics(df)
        
        # Generate recommendations for both timeframes
        timeframes_data = {}
        for timeframe in ['1D', '5D', '15D', '1M']:
            timeframe_df = get_timeframe_data(df, timeframe)
            if timeframe_df is not None:
                timeframes_data[timeframe] = analyze_timeframe(timeframe_df, timeframe)
        
        # Get short-term recommendation by default
        recommendation = generate_recommendation(symbol, df, timeframes_data, "short_term")
        
        # Update stats panel
        self.stats_panel.update_stats(stats_dict, recommendation, timeframes_data, df, symbol)
        
        # Update footer
        self.updated.config(text=f"Last updated: {end_str}")
        self.loading_var.set("")
        self.status.config(text="Status: Connected")

    def toggle_theme(self):
        """Toggle between light and dark theme."""
        if self.theme_mode == "light":
            self.theme_mode = "dark"
            self.theme_btn.config(text="☀️")
        else:
            self.theme_mode = "light"
            self.theme_btn.config(text="🌙")
        
        # Update config
        self.config["theme_mode"] = self.theme_mode
        
        # Apply new theme
        self.apply_theme()
        
        # Update button colors to match theme
        self._update_button_colors()
        
        # Update chart theme
        self.chart_panel.set_theme(self.theme_mode)
        
        # Update stats panel theme
        self.stats_panel.set_theme(self.theme_mode)

    def _update_input_widget_colors(self):
        """Update input widget colors to match current theme."""
        if self.theme_mode == "dark":
            # Dark theme colors
            entry_bg = "#2C2C2E"
            entry_fg = "#FFFFFF"
            combo_bg = "#2C2C2E"
            combo_fg = "#FFFFFF"
        else:
            # Light theme colors
            entry_bg = "white"
            entry_fg = "#1D1D1F"
            combo_bg = "white"
            combo_fg = "#1D1D1F"
        
        # Update symbol entry colors
        if hasattr(self, 'symbol_entry'):
            self.symbol_entry.configure(style="Modern.TEntry")
        
        # Update range menu colors
        if hasattr(self, 'range_menu'):
            self.range_menu.configure(style="Modern.TCombobox")
        
        # Update currency menu
        if hasattr(self, 'currency_menu'):
            self.currency_menu.configure(style="Modern.TCombobox")

    def _update_button_colors(self):
        """Update button colors to match current theme."""
        if self.theme_mode == "dark":
            # Dark theme button colors
            self.analyze_btn.config(bg="#2C2C2E", fg="#0A84FF", activebackground="#1C1C1E", activeforeground="#0056CC")
            self.theme_btn.config(bg="#2C2C2E", fg="#0A84FF", activebackground="#1C1C1E", activeforeground="#0056CC")
            self.chart_btn.config(bg="#2C2C2E", fg="#0A84FF", activebackground="#1C1C1E", activeforeground="#0056CC")
        else:
            # Light theme button colors
            self.analyze_btn.config(bg="white", fg="#007AFF", activebackground="#F5F5F7", activeforeground="#0056CC")
            self.theme_btn.config(bg="white", fg="#007AFF", activebackground="#F5F5F7", activeforeground="#0056CC")
            self.chart_btn.config(bg="white", fg="#007AFF", activebackground="#F5F5F7", activeforeground="#0056CC") 