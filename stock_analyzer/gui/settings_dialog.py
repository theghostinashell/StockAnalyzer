import tkinter as tk
from tkinter import ttk
from stock_analyzer.utils.helpers import load_config, save_config
from stock_analyzer.utils.config import chart_types

class SettingsDialog(tk.Toplevel):
    def __init__(self, master, on_settings_changed=None):
        super().__init__(master)
        self.title("Settings")
        self.geometry("400x200")
        self.resizable(False, False)
        self.on_settings_changed = on_settings_changed
        
        # Load current config
        self.config = load_config()
        
        # Center the dialog
        self.transient(master)
        self.grab_set()
        
        self.create_widgets()
        
    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="Settings", font=("Segoe UI", 16, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Chart section
        chart_frame = ttk.LabelFrame(main_frame, text="Chart", padding="10")
        chart_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Chart type
        chart_type_label = ttk.Label(chart_frame, text="Chart Type:")
        chart_type_label.pack(anchor=tk.W, pady=(0, 5))
        
        self.chart_type_var = tk.StringVar(value=self.config.get("chart_type", "line"))
        
        # Debug: Print available chart types
        print(f"Available chart types: {chart_types}")
        print(f"Current chart type: {self.chart_type_var.get()}")
        
        chart_type_combo = ttk.Combobox(chart_frame, textvariable=self.chart_type_var, 
                                       values=chart_types, state="readonly", width=15)
        chart_type_combo.pack(anchor=tk.W, pady=(0, 10))
        chart_type_combo.bind("<<ComboboxSelected>>", self.on_chart_type_changed)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        ok_btn = ttk.Button(button_frame, text="OK", command=self.on_ok)
        ok_btn.pack(side=tk.RIGHT, padx=(5, 0))
        
        cancel_btn = ttk.Button(button_frame, text="Cancel", command=self.on_cancel)
        cancel_btn.pack(side=tk.RIGHT)
        
        # Bind escape key to close
        self.bind("<Escape>", lambda e: self.on_cancel())
        
    def on_chart_type_changed(self, event=None):
        """Handle chart type change."""
        new_type = self.chart_type_var.get()
        print(f"Chart type changed to: {new_type}")
        self.config["chart_type"] = new_type
        
    def on_ok(self):
        """Save settings and close dialog."""
        # Save config
        save_config(self.config)
        
        # Notify parent of changes
        if self.on_settings_changed:
            self.on_settings_changed(self.config)
            
        self.destroy()
        
    def on_cancel(self):
        """Close dialog without saving."""
        self.destroy() 