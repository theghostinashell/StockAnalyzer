import tkinter as tk
from tkinter import ttk
import textwrap

# Try different import approaches for currency symbol
try:
    from ..data.stock_fetcher import get_currency_symbol
except ImportError:
    try:
        from stock_analyzer.data.stock_fetcher import get_currency_symbol
    except ImportError:
        # Fallback: define a simple function that returns the symbol
        def get_currency_symbol(currency_code):
            return '$'

class StatsPanel(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.labels = {}
        self.current_recommendation = None
        self.current_timeframes_data = None
        self.current_df = None
        self.current_symbol = None
        self.current_currency = 'USD'
        self.last_timeframe_type = "short_term"  # Store the last selected timeframe
        
        # Setup modern style
        self.setup_modern_style()
        self.create_widgets()

    def setup_modern_style(self):
        """Setup modern Apple-style appearance."""
        self.style = ttk.Style()
        
        # Define font family with fallbacks
        self.font_family = ("SF Pro Display", "Segoe UI", "Helvetica", "Arial", "sans-serif")
        
        # Initialize theme mode
        self.theme_mode = "light"
        
        # Apply theme
        self.apply_theme()
        
        # Configure the main frame
        self.configure(style="Stats.TFrame")

    def apply_theme(self):
        """Apply light or dark theme."""
        if self.theme_mode == "dark":
            self._setup_dark_theme()
        else:
            self._setup_light_theme()

    def _setup_light_theme(self):
        """Setup light theme colors."""
        # Configure modern light colors and styles
        self.style.configure("Stats.TFrame", background="#F5F5F7")
        self.style.configure("Stats.TLabel", background="#F5F5F7", foreground="#1D1D1F", font=(self.font_family[1], 10))
        self.style.configure("StatsTitle.TLabel", background="#F5F5F7", foreground="#1D1D1F", font=(self.font_family[1], 16, "bold"))
        self.style.configure("StatsHeader.TLabel", background="#F5F5F7", foreground="#1D1D1F", font=(self.font_family[1], 12, "bold"))
        self.style.configure("StatsValue.TLabel", background="#F5F5F7", foreground="#1D1D1F", font=(self.font_family[1], 11))
        self.style.configure("StatsSmall.TLabel", background="#F5F5F7", foreground="#86868B", font=(self.font_family[1], 9))
        
        # Modern combobox style
        self.style.configure("Stats.TCombobox", 
                           fieldbackground="white", 
                           borderwidth=1, 
                           relief="flat",
                           font=(self.font_family[1], 10))
        
        # Modern entry style
        self.style.configure("Stats.TEntry", 
                           fieldbackground="white", 
                           borderwidth=1, 
                           relief="flat",
                           font=(self.font_family[1], 10))

    def _setup_dark_theme(self):
        """Setup dark theme colors."""
        # Configure modern dark colors and styles
        self.style.configure("Stats.TFrame", background="#1C1C1E")
        self.style.configure("Stats.TLabel", background="#1C1C1E", foreground="#FFFFFF", font=(self.font_family[1], 10))
        self.style.configure("StatsTitle.TLabel", background="#1C1C1E", foreground="#FFFFFF", font=(self.font_family[1], 16, "bold"))
        self.style.configure("StatsHeader.TLabel", background="#1C1C1E", foreground="#FFFFFF", font=(self.font_family[1], 12, "bold"))
        self.style.configure("StatsValue.TLabel", background="#1C1C1E", foreground="#FFFFFF", font=(self.font_family[1], 11))
        self.style.configure("StatsSmall.TLabel", background="#1C1C1E", foreground="#8E8E93", font=(self.font_family[1], 9))
        
        # Modern combobox style
        self.style.configure("Stats.TCombobox", 
                           fieldbackground="#2C2C2E", 
                           borderwidth=1, 
                           relief="flat",
                           font=(self.font_family[1], 10))
        
        # Modern entry style
        self.style.configure("Stats.TEntry", 
                           fieldbackground="#2C2C2E", 
                           borderwidth=1, 
                           relief="flat",
                           font=(self.font_family[1], 10))

    def _update_scrollbar_colors(self):
        """Update scrollbar colors to match current theme."""
        if not hasattr(self, 'scrollbar'):
            return
            
        if self.theme_mode == "dark":
            # Dark theme - blue scrollbar matching chart line
            self.scrollbar.configure(
                background="#0A84FF",      # Blue slider (same as chart line)
                troughcolor="#2C2C2E",     # Dark background
                activebackground="#0056CC", # Darker blue when active
                width=12
            )
        else:
            # Light theme - light gray scrollbar
            self.scrollbar.configure(
                background="#E5E5E7",      # Light gray slider
                troughcolor="#F5F5F7",     # Very light background
                activebackground="#D1D1D6", # Darker gray when active
                width=12
            )

    def set_theme(self, theme_mode):
        """Set the stats panel theme (light or dark)."""
        self.theme_mode = theme_mode
        self.apply_theme()
        self._update_widget_colors()
        if hasattr(self, 'current_df') and self.current_df is not None:
            self._rebuild_stats_display()

    def set_currency(self, currency_code):
        """Set the currency for price display."""
        self.current_currency = currency_code
        if hasattr(self, 'current_df') and self.current_df is not None:
            self._rebuild_stats_display()

    def _update_widget_colors(self):
        """Update widget colors to match current theme."""
        if self.theme_mode == "dark":
            bg_color = "#1C1C1E"
            text_color = "#FFFFFF"
        else:
            bg_color = "#F5F5F7"
            text_color = "#1D1D1F"
        
        # Update canvas background
        if hasattr(self, 'canvas'):
            self.canvas.configure(bg=bg_color)
        
        # Update scrollbar colors
        self._update_scrollbar_colors()

    def create_widgets(self):
        # Create a canvas with scrollbar
        self.canvas = tk.Canvas(self, bg='#F5F5F7', highlightthickness=0)
        scrollbar = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas, style="Stats.TFrame")
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind mouse wheel to scroll on the entire stats panel
        self.bind("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind("<MouseWheel>", self._on_mousewheel)
        self.scrollable_frame.bind("<MouseWheel>", self._on_mousewheel)
        
        # Store scrollbar reference for styling
        self.scrollbar = scrollbar
        
        # Apply initial scrollbar styling
        self._update_scrollbar_colors()
        
        self._show_placeholder()

    def _on_mousewheel(self, event):
        """Handle mouse wheel scrolling with improved sensitivity."""
        # Get the current scroll position
        current_pos = self.canvas.yview()
        
        # Calculate scroll amount (more sensitive scrolling)
        scroll_amount = int(-1 * (event.delta / 120)) * 3  # 3x more sensitive
        
        # Apply scrolling
        self.canvas.yview_scroll(scroll_amount, "units")
        
        # Prevent event propagation to avoid conflicts
        return "break"

    def _show_placeholder(self):
        """Show placeholder when no data is available."""
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        placeholder = ttk.Label(self.scrollable_frame, 
                               text="Enter a stock symbol and click Analyze\nto view analysis and recommendations",
                               style="Stats.TLabel",
                               justify=tk.CENTER)
        placeholder.pack(expand=True, fill=tk.BOTH, pady=50)

    def update_stats(self, stats_dict, recommendation=None, timeframes_data=None, df=None, symbol=None):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        if not stats_dict and not recommendation:
            self._show_placeholder()
            return
        
        # Store current data for timeframe changes
        self.current_df = df
        self.current_symbol = symbol
        self.current_timeframes_data = timeframes_data
        self.last_stats_dict = stats_dict  # <--- Store the stats dict
        
        # Generate recommendation based on last selected timeframe
        if timeframes_data and symbol and df is not None:
            try:
                from ..analysis.recommendations import generate_recommendation
            except ImportError:
                try:
                    from stock_analyzer.analysis.recommendations import generate_recommendation
                except ImportError:
                    # If import fails, use the provided recommendation
                    self.current_recommendation = recommendation
                else:
                    self.current_recommendation = generate_recommendation(symbol, df, timeframes_data, self.last_timeframe_type)
            else:
                self.current_recommendation = generate_recommendation(symbol, df, timeframes_data, self.last_timeframe_type)
        else:
            self.current_recommendation = recommendation
        
        # Title
        title = ttk.Label(self.scrollable_frame, text="Analysis", style="StatsTitle.TLabel")
        title.pack(pady=(10, 20))
        
        # Recommendation Section
        if self.current_recommendation:
            self._add_recommendation_section(self.current_recommendation)
        
        # Timeframes Section
        if timeframes_data:
            self._add_timeframes_section(timeframes_data)
        
        # Statistics Section
        if stats_dict:
            self._add_statistics_section(stats_dict)

    def _add_recommendation_section(self, recommendation):
        """Add the buy/sell recommendation section with modern design."""
        # Recommendation header
        rec_header = ttk.Label(self.scrollable_frame, text="RECOMMENDATION", 
                              style="StatsHeader.TLabel")
        rec_header.pack(pady=(10, 10))
        
        # Recommendation card with modern design
        rec_card = ttk.Frame(self.scrollable_frame, style="Stats.TFrame")
        rec_card.pack(fill=tk.X, padx=10, pady=5)
        
        # Top row: Recommendation and timeframe dropdown
        top_row = ttk.Frame(rec_card, style="Stats.TFrame")
        top_row.pack(fill=tk.X, pady=(10, 5))
        
        # Left side: Recommendation and confidence
        left_frame = ttk.Frame(top_row, style="Stats.TFrame")
        left_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Define font family with fallbacks
        font_family = ("SF Pro Display", "Segoe UI", "Helvetica", "Arial", "sans-serif")
        
        rec_text = f"{recommendation.recommendation}"
        rec_color = "#34C759" if recommendation.recommendation == "BUY" else "#FF3B30" if recommendation.recommendation == "SELL" else "#FF9500"
        
        rec_label = ttk.Label(left_frame, text=rec_text, 
                             font=(font_family[1], 18, "bold"), foreground=rec_color, style="Stats.TLabel")
        rec_label.pack(side=tk.LEFT, padx=(0, 10))
        
        conf_label = ttk.Label(left_frame, text=f"{recommendation.confidence:.0f}% confidence", 
                              style="StatsSmall.TLabel")
        conf_label.pack(side=tk.LEFT)
        
        # Right side: Timeframe dropdown
        right_frame = ttk.Frame(top_row, style="Stats.TFrame")
        right_frame.pack(side=tk.RIGHT)
        
        ttk.Label(right_frame, text="Timeframe", style="StatsSmall.TLabel").pack(side=tk.LEFT, padx=(0, 5))
        
        # Set dropdown value based on last selected timeframe
        dropdown_value = "Short Term" if self.last_timeframe_type == "short_term" else "Long Term"
        self.timeframe_var = tk.StringVar(value=dropdown_value)
        timeframe_combo = ttk.Combobox(right_frame, textvariable=self.timeframe_var, 
                                      values=["Short Term", "Long Term"], 
                                      state="readonly", width=10, style="Stats.TCombobox")
        timeframe_combo.pack(side=tk.LEFT)
        timeframe_combo.bind("<<ComboboxSelected>>", self._on_timeframe_changed)
        
        # Get currency symbol
        currency_symbol = get_currency_symbol(self.current_currency)
        
        # Current price
        price_frame = ttk.Frame(rec_card, style="Stats.TFrame")
        price_frame.pack(fill=tk.X, pady=5)
        price_label = ttk.Label(price_frame, text=f"{currency_symbol}{recommendation.current_price:.2f}", 
                               font=(font_family[1], 16, "bold"), style="Stats.TLabel")
        price_label.pack(side=tk.LEFT)
        
        # User input for "Price you bought at"
        bought_price_frame = ttk.Frame(rec_card, style="Stats.TFrame")
        bought_price_frame.pack(fill=tk.X, pady=(10, 5))
        
        # Label
        ttk.Label(bought_price_frame, text="Price you bought at:", 
                 style="StatsSmall.TLabel").pack(side=tk.LEFT, padx=(0, 10))
        
        # Input field
        self.bought_price_var = tk.StringVar()
        bought_price_entry = ttk.Entry(bought_price_frame, textvariable=self.bought_price_var, 
                                      width=10, style="Stats.TEntry")
        bought_price_entry.pack(side=tk.LEFT, padx=(0, 5))
        bought_price_entry.bind('<KeyRelease>', self._on_bought_price_changed)
        
        # Clear button (red X)
        clear_btn = tk.Button(bought_price_frame, text="✕", width=2, height=1,
                             bg="#FF3B30", fg="white", font=(font_family[1], 8, "bold"),
                             relief="flat", bd=0, cursor="hand2",
                             command=self._clear_bought_price)
        clear_btn.pack(side=tk.LEFT)
        
        # Updated recommendation based on bought price
        self.bought_price_recommendation = ttk.Label(bought_price_frame, text="", 
                                                    style="StatsSmall.TLabel", foreground="#007AFF")
        self.bought_price_recommendation.pack(side=tk.RIGHT)
        
        # Entry/Exit/Stop Loss prices in a modern card layout
        if (recommendation.entry_price is not None and
            recommendation.exit_price is not None and
            recommendation.stop_loss is not None):
            prices_card = ttk.Frame(rec_card, style="Stats.TFrame")
            prices_card.pack(fill=tk.X, pady=10)
            
            # Entry price
            entry_frame = ttk.Frame(prices_card, style="Stats.TFrame")
            entry_frame.pack(side=tk.LEFT, padx=(0, 15))
            ttk.Label(entry_frame, text="Entry", style="StatsSmall.TLabel").pack()
            ttk.Label(entry_frame, text=f"{currency_symbol}{recommendation.entry_price:.2f}", 
                     font=(font_family[1], 12), foreground="#34C759", style="Stats.TLabel").pack()
            
            # Exit price
            exit_frame = ttk.Frame(prices_card, style="Stats.TFrame")
            exit_frame.pack(side=tk.LEFT, padx=(0, 15))
            ttk.Label(exit_frame, text="Target", style="StatsSmall.TLabel").pack()
            ttk.Label(exit_frame, text=f"{currency_symbol}{recommendation.exit_price:.2f}", 
                     font=(font_family[1], 12), foreground="#007AFF", style="Stats.TLabel").pack()
            
            # Stop loss
            stop_frame = ttk.Frame(prices_card, style="Stats.TFrame")
            stop_frame.pack(side=tk.LEFT)
            ttk.Label(stop_frame, text="Stop Loss", style="StatsSmall.TLabel").pack()
            ttk.Label(stop_frame, text=f"{currency_symbol}{recommendation.stop_loss:.2f}", 
                     font=(font_family[1], 12), foreground="#FF3B30", style="Stats.TLabel").pack()
        else:
            # Show a message for invalid values
            msg = ttk.Label(rec_card, text="No actionable trade setup for this stock and timeframe.",
                             style="StatsValue.TLabel", foreground="#888888", font=(font_family[1], 11, "italic"))
            msg.pack(pady=10)
        
        # Reasoning
        if recommendation.reasoning:
            reasoning_frame = ttk.Frame(rec_card, style="Stats.TFrame")
            reasoning_frame.pack(fill=tk.X, pady=10)
            
            ttk.Label(reasoning_frame, text="Analysis", style="StatsHeader.TLabel").pack(anchor=tk.W, pady=(0, 5))
            
            # Wrap long reasoning text
            wrapped_reasoning = textwrap.fill(recommendation.reasoning, width=40)
            reasoning_text = ttk.Label(reasoning_frame, text=wrapped_reasoning, 
                                     style="StatsValue.TLabel", justify=tk.LEFT)
            reasoning_text.pack(anchor=tk.W)
        
        # Separator
        separator = ttk.Separator(self.scrollable_frame, orient='horizontal')
        separator.pack(fill=tk.X, padx=10, pady=15)

    def _on_timeframe_changed(self, event=None):
        """Handle timeframe dropdown change."""
        if not (self.current_df is not None and not self.current_df.empty and 
                self.current_symbol and self.current_timeframes_data):
            return
            
        # Try different import approaches
        try:
            from ..analysis.recommendations import generate_recommendation
        except ImportError:
            try:
                from stock_analyzer.analysis.recommendations import generate_recommendation
            except ImportError:
                # If all imports fail, just return
                return
        
        # Update the stored timeframe type
        self.last_timeframe_type = "short_term" if self.timeframe_var.get() == "Short Term" else "long_term"
        
        # Generate new recommendation with the selected timeframe
        new_recommendation = generate_recommendation(
            self.current_symbol, 
            self.current_df, 
            self.current_timeframes_data, 
            self.last_timeframe_type
        )
        
        if new_recommendation:
            # Store the new recommendation
            self.current_recommendation = new_recommendation
            # Rebuild the entire stats display with the new recommendation
            self._rebuild_stats_display()
            
            # Update bought price recommendation if there's a value
            if hasattr(self, 'bought_price_var') and self.bought_price_var.get().strip():
                self._on_bought_price_changed()

    def _rebuild_stats_display(self):
        """Rebuild the entire stats display with current data."""
        # Store current bought price value if it exists
        current_bought_price = ""
        if hasattr(self, 'bought_price_var'):
            current_bought_price = self.bought_price_var.get()
        
        # Clear all widgets
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        # Rebuild the display with current data
        if not (self.current_recommendation or self.current_timeframes_data):
            self._show_placeholder()
            return
        
        # Title
        title = ttk.Label(self.scrollable_frame, text="Analysis", style="StatsTitle.TLabel")
        title.pack(pady=(10, 20))
        
        # Recommendation Section
        if self.current_recommendation:
            self._add_recommendation_section(self.current_recommendation)
            # Restore bought price value if it existed
            if current_bought_price and hasattr(self, 'bought_price_var'):
                self.bought_price_var.set(current_bought_price)
                self._on_bought_price_changed()
        
        # Timeframes Section
        if self.current_timeframes_data:
            self._add_timeframes_section(self.current_timeframes_data)
        
        # Statistics Section (fix: always show if available)
        if hasattr(self, 'last_stats_dict') and self.last_stats_dict:
            self._add_statistics_section(self.last_stats_dict)

    def _add_timeframes_section(self, timeframes_data):
        """Add the timeframes analysis section."""
        # Timeframes header
        tf_header = ttk.Label(self.scrollable_frame, text="TIMEFRAME ANALYSIS", 
                             style="StatsHeader.TLabel")
        tf_header.pack(pady=(10, 5))
        
        for timeframe, analysis in timeframes_data.items():
            if not analysis:
                continue
                
            # Timeframe frame
            tf_frame = ttk.Frame(self.scrollable_frame, style="Stats.TFrame")
            tf_frame.pack(fill=tk.X, padx=10, pady=2)
            
            # Timeframe title
            ttk.Label(tf_frame, text=timeframe, style="StatsHeader.TLabel").pack(anchor=tk.W, pady=(5, 5))
            
            # Price info
            currency_symbol = get_currency_symbol(self.current_currency)
            price_info = f"{currency_symbol}{analysis['current_price']:.2f} ({analysis['price_change']:+.1f}%)"
            price_color = "#34C759" if analysis['price_change'] >= 0 else "#FF3B30"
            ttk.Label(tf_frame, text=price_info, style="StatsValue.TLabel", 
                     foreground=price_color).pack(anchor=tk.W)
            
            # Technical indicators
            indicators_frame = ttk.Frame(tf_frame, style="Stats.TFrame")
            indicators_frame.pack(fill=tk.X, pady=(5, 0))
            
            # Left column
            left_col = ttk.Frame(indicators_frame, style="Stats.TFrame")
            left_col.pack(side=tk.LEFT, fill=tk.X, expand=True)
            
            # Right column
            right_col = ttk.Frame(indicators_frame, style="Stats.TFrame")
            right_col.pack(side=tk.RIGHT, fill=tk.X, expand=True)
            
            # Add indicators
            self._add_indicator(left_col, "RSI", analysis.get('rsi'), 
                               good_range=(30, 70), reverse=True)
            self._add_indicator(left_col, "SMA20", analysis.get('sma_20'))
            self._add_indicator(left_col, "EMA12", analysis.get('ema_12'))
            
            self._add_indicator(right_col, "Momentum", analysis.get('momentum'), 
                               good_range=(-5, 5), format_str="{:.1f}%")
            self._add_indicator(right_col, "SMA50", analysis.get('sma_50'))
            self._add_indicator(right_col, "EMA26", analysis.get('ema_26'))

    def _clear_bought_price(self):
        """Clear the bought price input and reset recommendation."""
        self.bought_price_var.set("")
        if hasattr(self, 'bought_price_recommendation'):
            self.bought_price_recommendation.config(text="")

    def _on_bought_price_changed(self, event=None):
        """Handle bought price input change and update recommendation."""
        if not self.current_recommendation:
            return
            
        try:
            bought_price = float(self.bought_price_var.get())
            current_price = self.current_recommendation.current_price
            
            # Calculate percentage change
            pct_change = ((current_price - bought_price) / bought_price) * 100
            
            # Get current timeframe type
            timeframe_type = self.last_timeframe_type if hasattr(self, 'last_timeframe_type') else "short_term"
            
            # Professional thresholds based on research:
            # Short term: 5% profit target, 10% stop loss
            # Long term: 15% profit target, 20% stop loss
            if timeframe_type == "short_term":
                profit_threshold = 5.0   # 5% profit to sell
                loss_threshold = -10.0   # 10% loss to cut
            else:  # long_term
                profit_threshold = 15.0  # 15% profit to sell
                loss_threshold = -20.0   # 20% loss to cut
            
            # Determine recommendation based on bought price vs current price
            if pct_change >= profit_threshold:
                rec_text = f"SELL (Take profit: +{pct_change:.1f}%)"
                rec_color = "#FF3B30"
            elif pct_change <= loss_threshold:
                rec_text = f"SELL (Cut loss: {pct_change:.1f}%)"
                rec_color = "#FF3B30"
            elif pct_change > 0:
                rec_text = f"HOLD (Profit: +{pct_change:.1f}%)"
                rec_color = "#FF9500"
            elif pct_change > loss_threshold:
                rec_text = f"HOLD (Loss: {pct_change:.1f}%)"
                rec_color = "#007AFF"
            else:
                rec_text = f"HOLD (Neutral: {pct_change:+.1f}%)"
                rec_color = "#007AFF"
                
            self.bought_price_recommendation.config(text=rec_text, foreground=rec_color)
            
        except ValueError:
            # Invalid input, clear the recommendation
            self.bought_price_recommendation.config(text="")

    def _add_indicator(self, parent, label, value, good_range=None, reverse=False, format_str="{:.2f}"):
        """Add a technical indicator with color coding."""
        if value is None:
            return
            
        frame = ttk.Frame(parent, style="Stats.TFrame")
        frame.pack(fill=tk.X, pady=1)
        
        ttk.Label(frame, text=f"{label}:", style="StatsSmall.TLabel", width=8).pack(side=tk.LEFT)
        
        # Color coding
        color = "#495057"  # Default gray
        if good_range and value is not None:
            if reverse:
                if value < good_range[0] or value > good_range[1]:
                    color = "#28A745"  # Green for oversold/overbought
            else:
                if good_range[0] <= value <= good_range[1]:
                    color = "#28A745"  # Green for good range
                elif value < good_range[0]:
                    color = "#DC3545"  # Red for low
                else:
                    color = "#FFC107"  # Yellow for high
        
        formatted_value = format_str.format(value)
        ttk.Label(frame, text=formatted_value, style="StatsSmall.TLabel", 
                 foreground=color).pack(side=tk.RIGHT)

    def _add_statistics_section(self, stats_dict):
        """Add the general statistics section."""
        # Statistics header
        stats_header = ttk.Label(self.scrollable_frame, text="GENERAL STATISTICS", 
                                style="StatsHeader.TLabel")
        stats_header.pack(pady=(10, 5))
        
        # Statistics frame
        stats_frame = ttk.Frame(self.scrollable_frame, style="Stats.TFrame")
        stats_frame.pack(fill=tk.X, padx=10, pady=5)
        
        for key, value in stats_dict.items():
            if value is not None:
                row = ttk.Frame(stats_frame, style="Stats.TFrame")
                row.pack(fill=tk.X, pady=1)
                
                label = ttk.Label(row, text=f"{key}:", width=20, anchor="w", style="StatsValue.TLabel")
                label.pack(side=tk.LEFT)
                
                # Format value with appropriate suffix
                if isinstance(value, (int, float)):
                    if "Return" in key or "Drawdown" in key:
                        formatted_value = f"{value:.2f}%"
                    elif "Ratio" in key:
                        formatted_value = f"{value:.2f}"
                    elif "Price" in key or "Volatility" in key:
                        currency_symbol = get_currency_symbol(self.current_currency)
                        formatted_value = f"{currency_symbol}{value:.2f}"
                    else:
                        formatted_value = f"{value:.2f}"
                else:
                    formatted_value = str(value)
                
                val_label = ttk.Label(row, text=formatted_value, anchor="e", style="StatsValue.TLabel")
                val_label.pack(side=tk.RIGHT)
                
                self.labels[key] = val_label 