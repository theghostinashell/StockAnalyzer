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

# Try different import approaches
try:
    from ..data.stock_fetcher import get_company_name
except ImportError:
    try:
        from stock_analyzer.data.stock_fetcher import get_company_name
    except ImportError:
        # Fallback: define a simple function that returns the symbol
        def get_company_name(symbol):
            return symbol

class ChartWidget(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.current_chart_type = "line"
        self.current_data = None
        self.current_symbol = None
        self.current_company_name = None
        
        # Hover tooltip variables
        self.hover_annotation = None
        self.hover_line = None
        self.hover_point = None
        
        # Set up the figure
        self.setup_figure()
        
    def setup_figure(self):
        """Set up the matplotlib figure with modern Apple-style design."""
        plt.style.use('default')  # Reset to default style
        
        # Create figure with modern Apple-style theme
        self.figure, self.ax = plt.subplots(figsize=(8, 5), facecolor='#F5F5F7')
        self.ax.set_facecolor('#F5F5F7')
        
        # Create canvas
        self.canvas = FigureCanvasTkAgg(self.figure, master=self)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        self.plot_placeholder()
        
    def set_chart_type(self, chart_type):
        """Set the chart type and replot if data is available."""
        print(f"Setting chart type to: {chart_type}")
        self.current_chart_type = chart_type
        
        # Remove any existing hover elements when switching chart types
        self.remove_hover_elements()
        
        if self.current_data is not None:
            print(f"Replotting data with chart type: {chart_type}")
            self.plot_data(self.current_data, self.current_symbol)

    def plot_placeholder(self):
        """Plot placeholder when no data is available with modern design."""
        self.ax.clear()
        self.ax.set_facecolor('#F5F5F7')
        self.ax.text(0.5, 0.5, "Enter a stock symbol to view chart", ha="center", va="center", 
                    fontsize=16, color="#86868B", fontfamily="Segoe UI", transform=self.ax.transAxes)
        self.ax.set_xticks([])
        self.ax.set_yticks([])
        self.figure.tight_layout()
        self.canvas.draw()

    def plot_line_chart(self, df, symbol=None):
        """Plot line chart."""
        self.current_data = df
        self.current_symbol = symbol
        self.current_company_name = get_company_name(symbol)
        self.plot_data(df, symbol)
        
    def plot_data(self, df, symbol=None):
        """Plot data with current chart type."""
        print(f"Plotting data with chart type: {self.current_chart_type}")
        print(f"Available columns: {list(df.columns) if df is not None else 'None'}")
        
        # Remove any existing hover elements before clearing
        self.remove_hover_elements()
        
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
        """Plot line chart data with modern Apple-style design."""
        # Modern Apple-style colors
        line_color = "#007AFF"
        grid_color = "#E5E5E7"
        text_color = "#1D1D1F"
        
        # Store data for hover functionality
        self.current_data = df
        
        # Plot the line
        line, = self.ax.plot(df.index, df['Close'], label="Close Price", color=line_color, linewidth=2.5)
        self.ax.set_title(f"{self.current_company_name} Price Chart" if self.current_company_name else "Price Chart", 
                         color=text_color, fontsize=18, fontweight='bold', fontfamily="Segoe UI", pad=20)
        self.ax.set_xlabel("Date", color=text_color, fontsize=12, fontfamily="Segoe UI")
        self.ax.set_ylabel("Price ($)", color=text_color, fontsize=12, fontfamily="Segoe UI")
        self.ax.grid(True, linestyle='-', alpha=0.3, color=grid_color, linewidth=0.5)
        
        # Remove legend for cleaner look
        # self.ax.legend(facecolor='#F5F5F7', edgecolor=grid_color, fontsize=10, fontfamily="Segoe UI")
        
        # Set text colors and modern styling
        self.ax.tick_params(colors=text_color, labelsize=10)
        for spine in self.ax.spines.values():
            spine.set_color(grid_color)
            spine.set_linewidth(0.5)
        
        # Add hover functionality only for line charts
        self.setup_hover_functionality(line)
            
    def plot_candlestick_chart_data(self, df, symbol):
        """Plot candlestick chart data with modern Apple-style design."""
        try:
            # Modern Apple-style colors
            up_color = "#34C759"  # Apple green
            down_color = "#FF3B30"  # Apple red
            grid_color = "#E5E5E7"
            text_color = "#1D1D1F"
            
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
                    color = up_color
                    body_color = up_color
                else:
                    color = down_color
                    body_color = down_color
                
                # Draw the wick (high-low line)
                self.ax.plot([date, date], [low, high], color=color, linewidth=1.5)
                
                # Draw the body
                body_height = abs(close - open_price)
                body_bottom = min(open_price, close)
                
                if body_height > 0:
                    rect = Rectangle((date - 0.3, body_bottom), 0.6, body_height, 
                                   facecolor=body_color, edgecolor=color, linewidth=1)
                    self.ax.add_patch(rect)
            
            self.ax.set_title(f"{self.current_company_name} Candlestick Chart" if self.current_company_name else "Candlestick Chart", 
                             color=text_color, fontsize=18, fontweight='bold', fontfamily="Segoe UI", pad=20)
            self.ax.set_xlabel("Date", color=text_color, fontsize=12, fontfamily="Segoe UI")
            self.ax.set_ylabel("Price ($)", color=text_color, fontsize=12, fontfamily="Segoe UI")
            self.ax.grid(True, linestyle='-', alpha=0.3, color=grid_color, linewidth=0.5)
            
            # Format x-axis dates
            self.ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
            self.ax.xaxis.set_major_locator(mdates.AutoDateLocator())
            plt.setp(self.ax.xaxis.get_majorticklabels(), rotation=45, fontsize=10, fontfamily="Segoe UI")
            
            # Set text colors and modern styling
            self.ax.tick_params(colors=text_color, labelsize=10)
            for spine in self.ax.spines.values():
                spine.set_color(grid_color)
                spine.set_linewidth(0.5)
            
            # Store data for potential fallback
            self.current_data = df
                
        except Exception as e:
            print(f"Error plotting candlestick chart: {e}")
            # Fallback to line chart
            self.plot_line_chart_data(df, symbol)
    
    def setup_hover_functionality(self, line):
        """Setup hover functionality for line charts."""
        if self.current_chart_type != "line":
            return
            
        # Connect hover events
        self.canvas.mpl_connect('motion_notify_event', lambda event: self.on_hover(event, line))
        self.canvas.mpl_connect('axes_leave_event', self.on_leave)
    
    def on_hover(self, event, line):
        """Handle mouse hover events."""
        if event.inaxes != self.ax or self.current_chart_type != "line":
            return
            
        # Get the closest data point
        xdata, ydata = line.get_data()
        if len(xdata) == 0:
            return
            
        # Find closest point
        x_pos = event.xdata
        if x_pos is None:
            return
            
        # Convert to datetime if needed
        if hasattr(xdata[0], 'to_pydatetime'):
            x_pos_dt = mdates.num2date(x_pos)
            distances = [abs((x.to_pydatetime() - x_pos_dt).total_seconds()) for x in xdata]
        else:
            distances = [abs(x - x_pos) for x in xdata]
        
        closest_idx = distances.index(min(distances))
        closest_x = xdata[closest_idx]
        closest_y = ydata[closest_idx]
        
        # Remove previous hover elements
        self.remove_hover_elements()
        
        # Add vertical line
        self.hover_line = self.ax.axvline(x=closest_x, color='#FF3B30', alpha=0.7, linewidth=1)
        
        # Add point marker
        self.hover_point = self.ax.plot(closest_x, closest_y, 'o', color='#FF3B30', 
                                       markersize=8, markeredgecolor='white', markeredgewidth=2)[0]
        
        # Add annotation with price
        price_text = f"${closest_y:.2f}"
        date_text = closest_x.strftime('%Y-%m-%d') if hasattr(closest_x, 'strftime') else str(closest_x)
        
        # Position annotation above the point
        self.hover_annotation = self.ax.annotate(
            f"{date_text}\n{price_text}",
            xy=(closest_x, closest_y),
            xytext=(10, 10),
            textcoords='offset points',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor='#E5E5E7', alpha=0.9),
            fontsize=10,
            fontfamily="Segoe UI",
            color='#1D1D1F'
        )
        
        # Redraw
        self.canvas.draw_idle()
    
    def on_leave(self, event):
        """Handle mouse leave events."""
        self.remove_hover_elements()
        self.canvas.draw_idle()
    
    def remove_hover_elements(self):
        """Remove hover elements from the chart."""
        if self.hover_line:
            self.hover_line.remove()
            self.hover_line = None
        if self.hover_point:
            self.hover_point.remove()
            self.hover_point = None
        if self.hover_annotation:
            self.hover_annotation.remove()
            self.hover_annotation = None 