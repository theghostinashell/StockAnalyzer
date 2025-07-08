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
        self.current_recommendation = recommendation
        self.current_timeframes_data = timeframes_data
        self.current_df = df
        self.current_symbol = symbol
        
        # Title
        title = ttk.Label(self.scrollable_frame, text="Analysis", style="StatsTitle.TLabel")
        title.pack(pady=(10, 20))
        
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
        
        self.timeframe_var = tk.StringVar(value="Short Term")
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
        
        # Entry/Exit/Stop Loss prices in a modern card layout
        if recommendation.entry_price and recommendation.exit_price and recommendation.stop_loss:
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
        
        timeframe_type = "short_term" if self.timeframe_var.get() == "Short Term" else "long_term"
        new_recommendation = generate_recommendation(
            self.current_symbol, 
            self.current_df, 
            self.current_timeframes_data, 
            timeframe_type
        )
        
        if new_recommendation:
            # Update the recommendation section
            self._update_recommendation_display(new_recommendation)

    def _update_recommendation_display(self, recommendation):
        """Update the recommendation display with new values."""
        # Find and update the recommendation label
        for widget in self.scrollable_frame.winfo_children():
            if isinstance(widget, ttk.Frame):
                for child in widget.winfo_children():
                    if isinstance(child, ttk.Label) and child.cget("font") == ("SF Pro Display", 18, "bold"):
                        rec_color = "#34C759" if recommendation.recommendation == "BUY" else "#FF3B30" if recommendation.recommendation == "SELL" else "#FF9500"
                        child.config(text=recommendation.recommendation, foreground=rec_color)
                        break
                # Update confidence
                for child in widget.winfo_children():
                    if isinstance(child, ttk.Label) and "confidence" in child.cget("text"):
                        child.config(text=f"{recommendation.confidence:.0f}% confidence")
                        break
                # Update price labels
                for child in widget.winfo_children():
                    if isinstance(child, ttk.Frame):
                        for grandchild in child.winfo_children():
                            if isinstance(grandchild, ttk.Label) and "Current Price:" in grandchild.cget("text"):
                                grandchild.config(text=f"${recommendation.current_price:.2f}")
                                break
                        # Update entry/exit/stop loss
                        for grandchild in child.winfo_children():
                            if isinstance(grandchild, ttk.Frame):
                                for great_grandchild in grandchild.winfo_children():
                                    if isinstance(great_grandchild, ttk.Label) and great_grandchild.cget("text").startswith("$"):
                                        if "Entry" in [sibling.cget("text") for sibling in grandchild.winfo_children() if isinstance(sibling, ttk.Label) and "Entry" in sibling.cget("text")]:
                                            great_grandchild.config(text=f"${recommendation.entry_price:.2f}")
                                        elif "Target" in [sibling.cget("text") for sibling in grandchild.winfo_children() if isinstance(sibling, ttk.Label) and "Target" in sibling.cget("text")]:
                                            great_grandchild.config(text=f"${recommendation.exit_price:.2f}")
                                        elif "Stop Loss" in [sibling.cget("text") for sibling in grandchild.winfo_children() if isinstance(sibling, ttk.Label) and "Stop Loss" in sibling.cget("text")]:
                                            great_grandchild.config(text=f"${recommendation.stop_loss:.2f}")
                                        break

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