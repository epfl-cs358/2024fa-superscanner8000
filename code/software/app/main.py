from tkinter import ttk, font 
import tkinter as tk
from tkinter.ttk import *
import os

from controllers.ss8 import SS8

# Pages
from pages.connection import ConnectionPage
from pages.setup import SetupPage

class App(tk.Tk):
    def __init__(self):
        """Initialize the main application window and set up pages."""
        super().__init__()

        # Init the window
        self.title("SuperScanner8000")
        self.geometry("990x540")
        self.container = tk.Frame(self)
        self.container.pack(fill="both", expand=True)
        self.apply_styling()
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        # Init the Superscanner8000 object
        self.ss8 = SS8()

        # Init pages
        self.pages = {}
        for F in (ConnectionPage, SetupPage):
            page_name = F.__name__
            frame = F(parent=self.container, controller=self)
            self.pages[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        
        # First page to show
        self.show_page("ConnectionPage")
        
    def apply_styling(self):
        """Apply custom styling to the application using a specified theme."""
        style = ttk.Style(self)
        tcl_file_path = os.path.join(os.path.dirname(__file__), 'assets', 'Forest-ttk-theme', 'forest-dark.tcl')
        self.tk.call('source', tcl_file_path)
        style.theme_use('forest-dark')

    def show_page(self, page_name):
        """Raise the specified frame to the front.
        
        Args:
            page_name (str): The name of the page to show.
        """
        frame = self.pages[page_name]
        frame.tkraise()

if __name__ == "__main__":
    app = App()
    app.mainloop()