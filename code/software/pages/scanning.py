import tkinter as tk
from tkinter import ttk
from tkinter.ttk import *
from controllers.object_detector import Object_Detector
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,  
NavigationToolbar2Tk) 
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
        self.fig = Figure(figsize = (5, 5), dpi = 100)

        # Add widget to the container
        label = ttk.Label(self.container, text="Scanning..")
        label.pack(pady=0)

        button = ttk.Button(self.container, text="Stop scanning", style='Accent.TButton', command=self._interrupt_scan)
        button.pack(pady=10)

        self.nav = self.controller.nav
        
        self.detector = Object_Detector(self.nav, self.controller.ss8, visualize=False)
        

        self._start_scanning()

    def _start_scanning(self):
        # Start the movement

        print("Will update mask loop")

        def update_mask():
            cv2.waitKey(1)
            self.controller.segmenter.propagate(self.controller.ss8.capture_image())
            self.after(1000//24, update_mask())

        print("Will start thread")

        self.after(100, update_mask)

        movement_thread = threading.Thread(target=self.nav.start_moving, args=(self._on_finish,))
        movement_thread.start()

        return 

        def update_plot():
            self.fig.clear()
            plot = self.fig.add_subplot(111)
            ss8_pos, obstacles = self.controller.nav.get_obstacle_plot_data()
            plot.scatter(ss8_pos[0], ss8_pos[1], c='r', marker='o', label='SS8')
            if obstacles.shape[0] > 0:
                plot.scatter(obstacles[:][:,0], obstacles[:][:,1], c='b', marker='x', label='Obstacle')

            plot.set_xlim(-110, 100)
            plot.set_ylim(-60, 60)

            self.occupancy_plot.draw_idle()

            self.container.after(100, update_plot)

        
        def detect_occupancy_loop():
            self.detector.start_detection()
            #self.detector.detect_occupancy()
            self.container.after(100, detect_occupancy_loop)

        def get_occupancy_map():
            cv2.waitKey(1)
            return self.detector.get_occupancy_map()
        
        def get_depth_map():
            cv2.waitKey(1)
            return self.detector.get_depth_map()
        
        def get_frame():
            return self.detector.get_frame()

        # Start the detection of obstacles
        if dconfig.CONNECT_TO_FRONT_CAM:

            # Show occupancy map
            detect_occupancy_loop()
            self.img_preview_occupancy = ImageWidget(self.container, 445, 300, None)
            self.img_preview_occupancy.display(get_depth_map, 10)
            

            self.occupancy_plot = FigureCanvasTkAgg(self.fig, master = self.container)   
            self.occupancy_plot.draw() 
  
            # placing the canvas on the Tkinter window 
            self.occupancy_plot.get_tk_widget().pack() 
  
            # creating the Matplotlib toolbar 
            toolbar = NavigationToolbar2Tk(self.occupancy_plot, 
                                        self.container) 
            toolbar.update() 
  
            # placing the toolbar on the Tkinter window 
            self.occupancy_plot.get_tk_widget().pack() 
            
            update_plot()


    def _interrupt_scan(self):
        self.controller.ss8.stop_mov()
        self.controller.show_page('SetupPage')

    def _on_finish(self):
        self.controller.show_page('EndPage')