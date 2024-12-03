from tkinter import ttk
import tkinter as tk
from tkinter.ttk import *
import os

from pages.connection import ConnectionPage
from pages.setup import SetupPage


class SuperScanner8000(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("SuperScanner8000")
        self.geometry("990x540")

        self.container = tk.Frame(self)
        self.container.pack(fill="both", expand=True)
        self.apply_styling()

        self.frames = {}
        for F in (ConnectionPage, SetupPage):
            page_name = F.__name__
            frame = F(parent=self.container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("ConnectionPage")
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

    def apply_styling(self):
        style = ttk.Style(self)
        tcl_file_path = os.path.join(os.path.dirname(__file__), 'assets', 'Forest-ttk-theme', 'forest-dark.tcl')
        self.tk.call('source', tcl_file_path)
        style.theme_use('forest-dark')

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()

if __name__ == "__main__":
    app = SuperScanner8000()
    app.mainloop()