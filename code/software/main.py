from tkinter import ttk, font 
import tkinter as tk
from tkinter.ttk import *
import os

from controllers.ss8 import SS8
from controllers.image_segmenter import ImageSegmenter
from controllers.navigator import Navigator

# Pages
from pages.connection import ConnectionPage
from pages.setup import SetupPage
from pages.scanning import ScanningPage
from pages.end import EndPage

STARTING_PAGE = "ConnectionPage"

class App(tk.Tk):
    def __init__(self):
        """Initialize the main application window and set up pages."""
        super().__init__()

        # Init the window
        self.title("SuperScanner8000")
        self.geometry("990x540")
        self.container = tk.Frame(self)
        self.container.pack(fill="both", expand=True)
        self._apply_styling()
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        # Init the Superscanner8000 object
        self.ss8 = SS8(self, self._connection_lost_callback)

        # Init the image segmenter
        self.segmenter = ImageSegmenter(model_cfg="sam2_hiera_s.yaml", checkpoint="config/sam2_checkpoints/sam2_hiera_small.pt", expand_pixels=10)

        self.nav = Navigator(self.ss8, self.segmenter)

        # Init pages
        self.pages = {}
        for F in (ConnectionPage, SetupPage, ScanningPage, EndPage):
            page_name = F.__name__
            self.pages[page_name] = F

        self.current_frame = None
        
        # First page to show
        self.show_page(STARTING_PAGE)
        
    def _apply_styling(self):
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
        if self.current_frame is not None:
            self.current_frame.destroy()
        self.current_frame = self.pages[page_name](parent=self.container, controller=self)
        self.current_frame.grid(row=0, column=0, sticky="nsew")
        self.current_frame.tkraise()
        self.update_idletasks()
        
    def _connection_lost_callback(self):
        """Callback function to be called when the connection is lost."""
        print("Connection lost")
        self.show_page("ConnectionPage")
        self.update_idletasks()

if __name__ == "__main__":
    app = App()
    app.mainloop()