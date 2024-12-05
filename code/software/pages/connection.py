import tkinter as tk
from tkinter import ttk
from tkinter.ttk import *
from assets.style import font
import time


class ConnectionPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # Create a container frame to center the content
        self.container = tk.Frame(self)
        self.container.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        self.err_message = None

        # Add widget to the container
        label = ttk.Label(self.container, text="Setup")
        label.pack(pady=10)

        label = ttk.Label(self.container, text="Please make sure that you're connected to the same WiFi as the SuperScanner8000 and then enter the Superscanner8000's IP adress.")
        label.pack(pady=10)
        self.entry = ttk.Entry(self.container)
        self.entry.insert(tk.END, self.controller.ss8.get_default_url())
        self.entry.pack(pady=10, ipadx=100)

        button = ttk.Button(self.container, text="Connect", style='Accent.TButton', command=self._connect)
        button.pack(pady=10)
    
    def _connect(self):
        hostname = self.entry.get()

        # Destroy previous error message
        if(self.err_message is not None):
            self.err_message.destroy()

        #Check if entry is empty
        if(len(hostname)<1):
            self.err_message = ttk.Label(self.container, text="Empty field ", foreground='red')
            self.err_message.pack(pady=2)
            return
        
        loadingText = ttk.Label(self.container, text="Connecting to "+hostname+"...")
        loadingText.pack(pady=2)
        self.update_idletasks()

        if self.controller.ss8.connect(hostname):
            self.controller.show_page('SetupPage')
        else:
            self.err_message = ttk.Label(self.container, text="Connection failed ", foreground='red')
            self.err_message.pack(pady=2)

        loadingText.destroy()
        self.update_idletasks()
