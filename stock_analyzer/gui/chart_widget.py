import tkinter as tk
from tkinter import ttk
try:
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    from matplotlib.patches import Rectangle
    import numpy as np
except ImportError as e:
    print("Required package not found:", e)
    print("Please install dependencies with: pip install -r requirements.txt")
    raise

class ChartWidget(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.current_chart_type = "line"
        self.current_data = None
        self.current_symbol = None
        
        # Set up the figure
        self.setup_figure()
        
    def setup_figure(self):
        """Set up the matplotlib figure."""
        plt.style.use('default')  # Reset to default style
        
        # Create figure with light theme
        self.figure, self.ax = plt.subplots(figsize=(7, 4), facecolor='white')
        self.ax.set_facecolor('white')
        
        # Create canvas
        self.canvas = FigureCanvasTkAgg(self.figure, master=self)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        self.plot_placeholder()
        
    def set_chart_type(self, chart_type):
        """Set the chart type and replot if data is available."""
        print(f"Setting chart type to: {chart_type}")
        self.current_chart_type = chart_type
        if self.current_data is not None:
            print(f"Replotting data with chart type: {chart_type}")
            self.plot_data(self.current_data, self.current_symbol)

    def plot_placeholder(self):
        """Plot placeholder when no data is available."""
        self.ax.clear()
        self.ax.set_facecolor('white')
        self.ax.text(0.5, 0.5, "No data to display", ha="center", va="center", 
                    fontsize=14, color="gray", transform=self.ax.transAxes)
        self.ax.set_xticks([])
        self.ax.set_yticks([])
        self.figure.tight_layout()
        self.canvas.draw()

    def plot_line_chart(self, df, symbol=None):
        """Plot line chart."""
        self.current_data = df
        self.current_symbol = symbol
        self.plot_data(df, symbol)
        
    def plot_data(self, df, symbol=None):
        """Plot data with current chart type."""
        print(f"Plotting data with chart type: {self.current_chart_type}")
        print(f"Available columns: {list(df.columns) if df is not None else 'None'}")
        
        self.ax.clear()
        self.ax.set_facecolor('white')
        
        if df is not None and not df.empty:
            # Check if we have the required data for candlestick chart
            required_columns = ['Open', 'High', 'Low', 'Close']
            has_ohlc_data = all(col in df.columns for col in required_columns)
            print(f"Has OHLC data: {has_ohlc_data}")
            
            if self.current_chart_type == "candlestick" and has_ohlc_data:
                print("Plotting candlestick chart")
                self.plot_candlestick_chart_data(df, symbol)
            else:
                # Fallback to line chart if candlestick data is not available
                if self.current_chart_type == "candlestick" and not has_ohlc_data:
                    print("Warning: OHLC data not available, falling back to line chart")
                print("Plotting line chart")
                self.plot_line_chart_data(df, symbol)
        else:
            self.plot_placeholder()
            
        self.figure.tight_layout()
        self.canvas.draw() 
        
    def plot_line_chart_data(self, df, symbol):
        """Plot line chart data."""
        self.ax.plot(df.index, df['Close'], label="Close Price", color="#007bff", linewidth=2)
        self.ax.set_title(f"{symbol} Price Chart" if symbol else "Price Chart", 
                         color="black", fontsize=14, fontweight='bold')
        self.ax.set_xlabel("Date", color="black")
        self.ax.set_ylabel("Price", color="black")
        self.ax.grid(True, linestyle='--', alpha=0.5, color="#e0e0e0")
        self.ax.legend(facecolor='white', edgecolor="#e0e0e0")
        
        # Set text colors
        self.ax.tick_params(colors="black")
        for spine in self.ax.spines.values():
            spine.set_color("#e0e0e0")
            
    def plot_candlestick_chart_data(self, df, symbol):
        """Plot candlestick chart data."""
        try:
            # Calculate candlestick data
            dates = mdates.date2num(df.index.to_pydatetime())
            opens = df['Open'].values
            highs = df['High'].values
            lows = df['Low'].values
            closes = df['Close'].values
            
            # Plot candlesticks
            for i in range(len(dates)):
                date = dates[i]
                open_price = opens[i]
                high = highs[i]
                low = lows[i]
                close = closes[i]
                
                # Determine color based on whether price went up or down
                if close >= open_price:
                    color = "#21ce99"  # Green for up
                    body_color = "#21ce99"
                else:
                    color = "#ff4444"  # Red for down
                    body_color = "#ff4444"
                
                # Draw the wick (high-low line)
                self.ax.plot([date, date], [low, high], color=color, linewidth=1)
                
                # Draw the body
                body_height = abs(close - open_price)
                body_bottom = min(open_price, close)
                
                if body_height > 0:
                    rect = Rectangle((date - 0.3, body_bottom), 0.6, body_height, 
                                   facecolor=body_color, edgecolor=color, linewidth=1)
                    self.ax.add_patch(rect)
            
            self.ax.set_title(f"{symbol} Candlestick Chart" if symbol else "Candlestick Chart", 
                             color="black", fontsize=14, fontweight='bold')
            self.ax.set_xlabel("Date", color="black")
            self.ax.set_ylabel("Price", color="black")
            self.ax.grid(True, linestyle='--', alpha=0.5, color="#e0e0e0")
            
            # Format x-axis dates
            self.ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
            self.ax.xaxis.set_major_locator(mdates.AutoDateLocator())
            plt.setp(self.ax.xaxis.get_majorticklabels(), rotation=45)
            
            # Set text colors
            self.ax.tick_params(colors="black")
            for spine in self.ax.spines.values():
                spine.set_color("#e0e0e0")
                
        except Exception as e:
            print(f"Error plotting candlestick chart: {e}")
            # Fallback to line chart
            self.plot_line_chart_data(df, symbol) 