import tkinter as tk
from tkinter import ttk
from tkinter.ttk import *
from controllers.object_detector import Object_Detector
import asyncio, threading
import config.dev_config as dconfig
from widgets.image import ImageWidget
import cv2

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

        self.nav = self.controller.nav
        
        self.detector = Object_Detector(self.nav, self.controller.ss8, visualize=False)

        asyncio.run(self._start_scanning())

    async def _start_scanning(self):
        # Start centering the camera all the time
        self.controller.ss8.turn_on_tracker()

        # Start the movement
        #mov_coroutine = asyncio.create_task(self.nav.start_moving(self._on_finish))
        movement_thread = threading.Thread(target=self.nav.start_moving, args=(self._on_finish,))
        movement_thread.start()
        
        def detect_occupancy_loop():
            self.detector.detect_occupancy()
            self.container.after(100, detect_occupancy_loop)

        def get_occupancy_map():
            cv2.waitKey(1)
            return self.detector.get_occupancy_map()
        
        def get_frame():
            return self.detector.get_frame()

        # Start the detection of obstacles
        if dconfig.CONNECT_TO_FRONT_CAM:
            #detector_coroutine = asyncio.create_task(self.detector.start_detection())
            # Show occupancy map
            detect_occupancy_loop()
            self.img_preview_occupancy = ImageWidget(self.container, 445, 300, None)
            self.img_preview_occupancy.display(get_frame, 10)

            #await detector_coroutine
            
        #await mov_coroutine

    def _interrupt_scan(self):
        self.controller.ss8.stop_mov()
        self.controller.show_page('SetupPage')

    def _on_finish(self):
        self.controller.show_page('EndPage')