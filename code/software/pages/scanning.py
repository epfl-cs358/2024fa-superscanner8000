import tkinter as tk
from tkinter import ttk
from tkinter.ttk import *
from assets.style import font
import time


class ScanningPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # Create a container frame to center the content
        self.container = tk.Frame(self)
        self.container.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        # Add widget to the container
        label = ttk.Label(self.container, text="Scanning..")
        label.pack(pady=0)

        button = ttk.Button(self.container, text="Stop scanning", style='Accent.TButton', command=self._interrupt_scan)
        button.pack(pady=10)

        self.start_movement()

    def _interrupt_scan(self):
        self.controller.ss8.stop_mov()
        self.controller.show_page('SetupPage')

    def start_movement(self):
        def center_cam():
            self.controller.ss8.recenter_cam()
            self.after(1000, center_cam)
        
        center_cam()