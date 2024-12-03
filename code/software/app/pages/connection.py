import tkinter as tk
from tkinter import ttk
from tkinter.ttk import *


class ConnectionPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        label = ttk.Label(self, text="Setup", font=("Arial", 20, "bold"))
        label.pack(pady=10)

        label = ttk.Label(self, text="Please make sure that you're connected to the same WiFi as the SuperScanner8000", font=("Arial", 16))
        label.pack(pady=10)

        button = ttk.Button(self, text="Go to Setup Page", style='Accent.TButton', command=lambda: controller.show_frame("SetupPage"))
        button.pack(pady=10)