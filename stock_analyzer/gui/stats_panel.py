import tkinter as tk
from tkinter import ttk
import textwrap

class StatsPanel(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.labels = {}
        self.current_recommendation = None
        self.current_timeframes_data = None
        self.current_df = None
        self.current_symbol = None
        self.last_timeframe_type = "short_term"  # Store the last selected timeframe
        
        # Setup modern style
        self.setup_modern_style()
        self.create_widgets()

    def setup_modern_style(self):
        """Setup modern Apple-style appearance."""
        style = ttk.Style()
        
        # Define font family with fallbacks
        font_family = ("SF Pro Display", "Segoe UI", "Helvetica", "Arial", "sans-serif")
        
        # Configure modern colors and styles
        style.configure("Stats.TFrame", background="#F5F5F7")
        style.configure("Stats.TLabel", background="#F5F5F7", foreground="#1D1D1F", font=(font_family[1], 10))
        style.configure("StatsTitle.TLabel", background="#F5F5F7", foreground="#1D1D1F", font=(font_family[1], 16, "bold"))
        style.configure("StatsHeader.TLabel", background="#F5F5F7", foreground="#1D1D1F", font=(font_family[1], 12, "bold"))
        style.configure("StatsValue.TLabel", background="#F5F5F7", foreground="#1D1D1F", font=(font_family[1], 11))
        style.configure("StatsSmall.TLabel", background="#F5F5F7", foreground="#86868B", font=(font_family[1], 9))
        
        # Modern combobox style
        style.configure("Stats.TCombobox", 
                       fieldbackground="white", 
                       borderwidth=1, 
                       relief="flat",
                       font=(font_family[1], 10))
        
        # Configure the main frame
        self.configure(style="Stats.TFrame")
        
    def create_widgets(self):
        # Create a canvas with scrollbar
        self.canvas = tk.Canvas(self, bg='#F5F5F7', highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas, style="Stats.TFrame")
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind mouse wheel to scroll
        self.canvas.bind("<MouseWheel>", self._on_mousewheel)
        
        self._show_placeholder()

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

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
                             font=(font_family[1], 18, "bold"), foreground=rec_color)
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
        
        # Current price
        price_frame = ttk.Frame(rec_card, style="Stats.TFrame")
        price_frame.pack(fill=tk.X, pady=5)
        price_label = ttk.Label(price_frame, text=f"${recommendation.current_price:.2f}", 
                               font=(font_family[1], 16, "bold"))
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
        if (recommendation.recommendation in ("BUY", "SELL") and
            recommendation.entry_price is not None and
            recommendation.exit_price is not None and
            recommendation.stop_loss is not None):
            prices_card = ttk.Frame(rec_card, style="Stats.TFrame")
            prices_card.pack(fill=tk.X, pady=10)
            
            # Entry price
            entry_frame = ttk.Frame(prices_card, style="Stats.TFrame")
            entry_frame.pack(side=tk.LEFT, padx=(0, 15))
            ttk.Label(entry_frame, text="Entry", style="StatsSmall.TLabel").pack()
            ttk.Label(entry_frame, text=f"${recommendation.entry_price:.2f}", 
                     font=(font_family[1], 12), foreground="#34C759").pack()
            
            # Exit price
            exit_frame = ttk.Frame(prices_card, style="Stats.TFrame")
            exit_frame.pack(side=tk.LEFT, padx=(0, 15))
            ttk.Label(exit_frame, text="Target", style="StatsSmall.TLabel").pack()
            ttk.Label(exit_frame, text=f"${recommendation.exit_price:.2f}", 
                     font=(font_family[1], 12), foreground="#007AFF").pack()
            
            # Stop loss
            stop_frame = ttk.Frame(prices_card, style="Stats.TFrame")
            stop_frame.pack(side=tk.LEFT)
            ttk.Label(stop_frame, text="Stop Loss", style="StatsSmall.TLabel").pack()
            ttk.Label(stop_frame, text=f"${recommendation.stop_loss:.2f}", 
                     font=(font_family[1], 12), foreground="#FF3B30").pack()
        else:
            # Show a message for HOLD or invalid values
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
        
        # Note: We don't have access to the original stats_dict here, so we skip the statistics section
        # The recommendation and timeframes sections are the most important for timeframe switching

    def _add_timeframes_section(self, timeframes_data):
        """Add the timeframes analysis section."""
        # Timeframes header
        tf_header = ttk.Label(self.scrollable_frame, text="TIMEFRAME ANALYSIS", 
                             font=("Segoe UI", 12, "bold"), foreground="#2E86AB")
        tf_header.pack(pady=(10, 5))
        
        for timeframe, analysis in timeframes_data.items():
            if not analysis:
                continue
                
            # Timeframe frame
            tf_frame = ttk.LabelFrame(self.scrollable_frame, text=timeframe, padding=5)
            tf_frame.pack(fill=tk.X, padx=10, pady=2)
            
            # Price info
            price_info = f"${analysis['current_price']:.2f} ({analysis['price_change']:+.1f}%)"
            price_color = "#28A745" if analysis['price_change'] >= 0 else "#DC3545"
            ttk.Label(tf_frame, text=price_info, font=("Segoe UI", 10, "bold"), 
                     foreground=price_color).pack(anchor=tk.W)
            
            # Technical indicators
            indicators_frame = ttk.Frame(tf_frame)
            indicators_frame.pack(fill=tk.X, pady=(5, 0))
            
            # Left column
            left_col = ttk.Frame(indicators_frame)
            left_col.pack(side=tk.LEFT, fill=tk.X, expand=True)
            
            # Right column
            right_col = ttk.Frame(indicators_frame)
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
            
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.X, pady=1)
        
        ttk.Label(frame, text=f"{label}:", font=("Segoe UI", 8), width=8).pack(side=tk.LEFT)
        
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
        ttk.Label(frame, text=formatted_value, font=("Segoe UI", 8), 
                 foreground=color).pack(side=tk.RIGHT)

    def _add_statistics_section(self, stats_dict):
        """Add the general statistics section."""
        # Statistics header
        stats_header = ttk.Label(self.scrollable_frame, text="GENERAL STATISTICS", 
                                font=("Segoe UI", 12, "bold"), foreground="#2E86AB")
        stats_header.pack(pady=(10, 5))
        
        # Statistics frame
        stats_frame = ttk.Frame(self.scrollable_frame)
        stats_frame.pack(fill=tk.X, padx=10, pady=5)
        
        for key, value in stats_dict.items():
            if value is not None:
                row = ttk.Frame(stats_frame)
                row.pack(fill=tk.X, pady=1)
                
                label = ttk.Label(row, text=f"{key}:", width=20, anchor="w", font=("Segoe UI", 9))
                label.pack(side=tk.LEFT)
                
                # Format value with appropriate suffix
                if isinstance(value, (int, float)):
                    if "Return" in key or "Drawdown" in key:
                        formatted_value = f"{value:.2f}%"
                    elif "Ratio" in key:
                        formatted_value = f"{value:.2f}"
                    elif "Price" in key or "Volatility" in key:
                        formatted_value = f"${value:.2f}"
                    else:
                        formatted_value = f"{value:.2f}"
                else:
                    formatted_value = str(value)
                
                val_label = ttk.Label(row, text=formatted_value, anchor="e", font=("Segoe UI", 9))
                val_label.pack(side=tk.RIGHT)
                
                self.labels[key] = val_label 