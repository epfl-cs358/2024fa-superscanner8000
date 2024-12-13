import tkinter as tk
from tkinter import ttk
from tkinter.ttk import *


class ConnectionPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # Create a container frame to center the content
        self.container = tk.Frame(self)
        self.container.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        self.entry_err_message = None

        # Add widget to the container
        label = ttk.Label(self.container, text="Setup")
        label.pack(pady=0)

        ttk.Label(self.container, text="Please make sure that you're connected to the same WiFi as the SuperScanner8000").pack(pady=10)

        default_api_url, default_top_cam_url, default_front_cam_url = self.controller.ss8.get_default_urls()

        ttk.Label(self.container, text="Api url :").pack(pady=10)
        self.api_url_entry = ttk.Entry(self.container)
        self.api_url_entry.insert(tk.END, default_api_url)
        self.api_url_entry.pack(pady=5, ipadx=100)

        ttk.Label(self.container, text="Top camera url :").pack(pady=10)
        self.top_cam_url_entry = ttk.Entry(self.container)
        self.top_cam_url_entry.insert(tk.END, default_top_cam_url)
        self.top_cam_url_entry.pack(pady=5, ipadx=100)

        ttk.Label(self.container, text="Front camera url :").pack(pady=10)
        self.front_cam_url_entry = ttk.Entry(self.container)
        self.front_cam_url_entry.insert(tk.END, default_front_cam_url)
        self.front_cam_url_entry.pack(pady=5, ipadx=100)

        button = ttk.Button(self.container, text="Connect", style='Accent.TButton', command=self._connect)
        button.pack(pady=10)
    
    def _connect(self):
        api_hostname = self.api_url_entry.get()
        top_cam_hostname = self.top_cam_url_entry.get()
        front_cam_url_hostname = self.front_cam_url_entry.get()

        # Destroy previous error message
        if(self.entry_err_message is not None):
            self.entry_err_message.destroy()
        #Check if entry is empty
        if(len(api_hostname)<1 or len(top_cam_hostname)<1 or len(front_cam_url_hostname)<1):
            self.entry_err_message = ttk.Label(self.container, text="Empty field(s)", foreground='red')
            self.entry_err_message.pack(pady=2)
            return
        
        loadingText = ttk.Label(self.container, text="Connecting to "+api_hostname+"...")
        loadingText.pack(pady=2)
        self.update_idletasks()

        if self.controller.ss8.connect(api_hostname, top_cam_hostname,front_cam_url_hostname):
            self.controller.show_page('SetupPage')
        else:
            self.entry_err_message = ttk.Label(self.container, text="Connection failed ", foreground='red')
            self.entry_err_message.pack(pady=2)

        loadingText.destroy()
        self.update_idletasks()
