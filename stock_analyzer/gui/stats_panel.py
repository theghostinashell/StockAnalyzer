import tkinter as tk
from tkinter import ttk
import textwrap

class StatsPanel(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.labels = {}
        self._build()

    def _build(self):
        # Create scrollable frame
        self.canvas = tk.Canvas(self)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # Pack scrollable elements
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        # Bind mouse wheel
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        
        self._show_placeholder()

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def _show_placeholder(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        placeholder = ttk.Label(self.scrollable_frame, text="No statistics to display.", foreground="gray")
        placeholder.pack(pady=20)

    def update_stats(self, stats_dict, recommendation=None, timeframes_data=None):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        if not stats_dict and not recommendation:
            self._show_placeholder()
            return
        
        # Title
        title = ttk.Label(self.scrollable_frame, text="Stock Analysis", font=("Segoe UI", 16, "bold"))
        title.pack(pady=(10, 15))
        
        # Recommendation Section
        if recommendation:
            self._add_recommendation_section(recommendation)
        
        # Timeframes Section
        if timeframes_data:
            self._add_timeframes_section(timeframes_data)
        
        # Statistics Section
        if stats_dict:
            self._add_statistics_section(stats_dict)

    def _add_recommendation_section(self, recommendation):
        """Add the buy/sell recommendation section."""
        # Recommendation header
        rec_header = ttk.Label(self.scrollable_frame, text="RECOMMENDATION", 
                              font=("Segoe UI", 12, "bold"), foreground="#2E86AB")
        rec_header.pack(pady=(10, 5))
        
        # Recommendation frame
        rec_frame = ttk.Frame(self.scrollable_frame)
        rec_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Recommendation and confidence
        rec_text = f"{recommendation.recommendation}"
        rec_color = "#28A745" if recommendation.recommendation == "BUY" else "#DC3545" if recommendation.recommendation == "SELL" else "#FFC107"
        
        rec_label = ttk.Label(rec_frame, text=rec_text, font=("Segoe UI", 14, "bold"), foreground=rec_color)
        rec_label.pack(side=tk.LEFT, padx=(0, 10))
        
        conf_label = ttk.Label(rec_frame, text=f"Confidence: {recommendation.confidence:.0f}%", 
                              font=("Segoe UI", 10), foreground="#6C757D")
        conf_label.pack(side=tk.LEFT)
        
        # Current price
        price_frame = ttk.Frame(self.scrollable_frame)
        price_frame.pack(fill=tk.X, padx=10, pady=2)
        price_label = ttk.Label(price_frame, text=f"Current Price: ${recommendation.current_price:.2f}", 
                               font=("Segoe UI", 11, "bold"))
        price_label.pack(side=tk.LEFT)
        
        # Entry/Exit/Stop Loss prices
        if recommendation.entry_price and recommendation.exit_price and recommendation.stop_loss:
            prices_frame = ttk.Frame(self.scrollable_frame)
            prices_frame.pack(fill=tk.X, padx=10, pady=5)
            
            # Entry price
            entry_frame = ttk.Frame(prices_frame)
            entry_frame.pack(side=tk.LEFT, padx=(0, 15))
            ttk.Label(entry_frame, text="Entry:", font=("Segoe UI", 9, "bold")).pack()
            ttk.Label(entry_frame, text=f"${recommendation.entry_price:.2f}", 
                     font=("Segoe UI", 10), foreground="#28A745").pack()
            
            # Exit price
            exit_frame = ttk.Frame(prices_frame)
            exit_frame.pack(side=tk.LEFT, padx=(0, 15))
            ttk.Label(exit_frame, text="Target:", font=("Segoe UI", 9, "bold")).pack()
            ttk.Label(exit_frame, text=f"${recommendation.exit_price:.2f}", 
                     font=("Segoe UI", 10), foreground="#007BFF").pack()
            
            # Stop loss
            stop_frame = ttk.Frame(prices_frame)
            stop_frame.pack(side=tk.LEFT)
            ttk.Label(stop_frame, text="Stop Loss:", font=("Segoe UI", 9, "bold")).pack()
            ttk.Label(stop_frame, text=f"${recommendation.stop_loss:.2f}", 
                     font=("Segoe UI", 10), foreground="#DC3545").pack()
        
        # Reasoning
        if recommendation.reasoning:
            reasoning_frame = ttk.Frame(self.scrollable_frame)
            reasoning_frame.pack(fill=tk.X, padx=10, pady=10)
            
            ttk.Label(reasoning_frame, text="Analysis:", font=("Segoe UI", 10, "bold")).pack(anchor=tk.W)
            
            # Wrap long reasoning text
            wrapped_reasoning = textwrap.fill(recommendation.reasoning, width=50)
            reasoning_text = ttk.Label(reasoning_frame, text=wrapped_reasoning, 
                                     font=("Segoe UI", 9), foreground="#495057", justify=tk.LEFT)
            reasoning_text.pack(anchor=tk.W, pady=(2, 0))
        
        # Separator
        separator = ttk.Separator(self.scrollable_frame, orient='horizontal')
        separator.pack(fill=tk.X, padx=10, pady=10)

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