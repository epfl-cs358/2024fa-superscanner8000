import tkinter as tk
from tkinter import ttk
from assets.style import font as f

class SetupPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # Create a container frame to center the content
        self.container = tk.Frame(self)
        self.container.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        label = ttk.Label(self.container, text="Click on the object you want to scan")
        label.pack(pady=10)

        button = ttk.Button(self.container, text="Go to Connection Page", style='Accent.TButton', command=lambda: controller.show_page("ConnectionPage"))
        button.pack(pady=10)