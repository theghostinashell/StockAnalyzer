import tkinter as tk
from tkinter import ttk

class StatsPanel(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.labels = {}
        self._build()

    def _build(self):
        title = ttk.Label(self, text="Statistics", font=("Segoe UI", 14, "bold"))
        title.pack(pady=(10, 10))
        self.stats_frame = ttk.Frame(self)
        self.stats_frame.pack(fill=tk.BOTH, expand=True)
        self._show_placeholder()

    def _show_placeholder(self):
        for widget in self.stats_frame.winfo_children():
            widget.destroy()
        placeholder = ttk.Label(self.stats_frame, text="No statistics to display.", foreground="gray")
        placeholder.pack(pady=20)

    def update_stats(self, stats_dict):
        for widget in self.stats_frame.winfo_children():
            widget.destroy()
        if not stats_dict:
            self._show_placeholder()
            return
        for key, value in stats_dict.items():
            row = ttk.Frame(self.stats_frame)
            row.pack(fill=tk.X, pady=2, padx=10)
            label = ttk.Label(row, text=f"{key}", width=18, anchor="w")
            label.pack(side=tk.LEFT)
            val = ttk.Label(row, text=f"{value}", anchor="e")
            val.pack(side=tk.RIGHT)
            self.labels[key] = val 