import tkinter as tk
from tkinter import ttk
from tkinter.ttk import *
from controllers.navigator import Navigator
import asyncio

CALIBRATION_ITERATION = 4

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
        
        button = ttk.Button(self.container, text="Save image", style='Accent.TButton', command=self._save_image)
        button.pack(pady=10)

        self.nav = Navigator(self.controller.ss8, self._save_image, lambda: print('Finish first round'))
        asyncio.run(self._start_scanning())

    async def _start_scanning(self):
        # Start centering the camera all the time
        self.controller.ss8.turn_on_tracker()

        # Start the movement
        mov_coroutine = asyncio.create_task(self.nav.start_moving(4))

        # TODO : Start the detection of obstacles and save them to the navigator with self.nav.add_obstacle()
        print('Start adding obstacles')

        await mov_coroutine

    def _interrupt_scan(self):
        self.controller.ss8.stop_mov()
        self.controller.show_page('SetupPage')

    def _save_image(self):
        # TODO : Save the image to a tmp folder
        print('Take picture')
        pass