import tkinter as tk
from tkinter import ttk
from gui.main_window import MainWindow


def main():
    root = tk.Tk()
    root.title("Stock Price Visualizer & Analyzer")
    root.geometry("1200x800")
    root.minsize(900, 600)
    app = MainWindow(root)
    app.pack(fill=tk.BOTH, expand=True)
    root.mainloop()


if __name__ == "__main__":
    main() 