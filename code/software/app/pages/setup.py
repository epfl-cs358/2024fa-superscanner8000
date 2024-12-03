import tkinter as tk
from tkinter import ttk


class SetupPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        label = ttk.Label(self, text="Hello, Tkinter!", font=("Arial", 16))
        label.pack(pady=10)

        entry = ttk.Entry(self)
        entry.pack(pady=10)

        button = ttk.Button(self, text="Go to Connection Page", style='Accent.TButton', command=lambda: controller.show_frame("ConnectionPage"))
        button.pack(pady=10)