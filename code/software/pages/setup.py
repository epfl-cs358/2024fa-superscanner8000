import tkinter as tk
from tkinter import ttk
import cv2
import numpy as np
import asyncio

from widgets.image import ImageWidget

from config.dev_config import DEFAULT_VERTICAL_PRECISION, DEFAULT_HORIZONTAL_PRECISION

class SetupPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # Setup variable to choose which object to scan
        self.object_selected = False

        # Create a container frame to center the content
        self.container = tk.Frame(self)
        self.container.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        # Add widget to the container
        label = ttk.Label(self.container, text="Click on the object you want to scano in  the preview window")
        label.pack(pady=0)

        self._display_preview()
        self._display_directionnal_buttons()
        self._display_selection_buttons()

        self.controller.ss8.display_text("Connected")
        
    def _display_directionnal_buttons(self):
        buttons_container = tk.Frame(self.container)
        buttons_container.pack(pady=5)

        # Camera buttons
        self.cam_up_button = ttk.Button(buttons_container, text="Camera Up")
        self.cam_up_button.bind("<ButtonPress-1>", lambda event: asyncio.run(self.controller.ss8.up_camera()))
        self.cam_up_button.bind("<ButtonRelease-1>", lambda event: asyncio.run(self.controller.ss8.stop_cam()))
        self.cam_up_button.grid(row=1, column=0, padx=5, pady=5)

        self.cam_down_button = ttk.Button(buttons_container, text="Camera Down")
        self.cam_down_button.bind("<ButtonPress-1>", lambda event: asyncio.run(self.controller.ss8.down_camera()))
        self.cam_down_button.bind("<ButtonRelease-1>", lambda event: asyncio.run(self.controller.ss8.stop_cam()))
        self.cam_down_button.grid(row=1, column=2, padx=5, pady=5)

        # Directional buttons
        self.forward_button = ttk.Button(buttons_container, text="Forward")
        self.forward_button.bind("<ButtonPress-1>", lambda event: asyncio.run(self.controller.ss8.move_forward(wait_for_completion=False)))
        self.forward_button.bind("<ButtonRelease-1>", lambda event: asyncio.run(self.controller.ss8.stop_mov()))
        self.forward_button.grid(row=0, column=1, padx=5, pady=5)

        self.left_button = ttk.Button(buttons_container, text="Rotate Left")
        self.left_button.bind("<ButtonPress-1>", lambda event: asyncio.run(self.controller.ss8.rotate_left(wait_for_completion=False)))
        self.left_button.bind("<ButtonRelease-1>", lambda event: asyncio.run(self.controller.ss8.stop_mov()))
        self.left_button.grid(row=0, column=0, padx=5, pady=5)

        self.right_button = ttk.Button(buttons_container, text="Rotate Right")
        self.right_button.bind("<ButtonPress-1>", lambda event: asyncio.run(self.controller.ss8.rotate_right(wait_for_completion=False)))
        self.right_button.bind("<ButtonRelease-1>", lambda event: asyncio.run(self.controller.ss8.stop_mov()))
        self.right_button.grid(row=0, column=2, padx=5, pady=5)

        self.backward_button = ttk.Button(buttons_container, text="Backward")
        self.backward_button.bind("<ButtonPress-1>", lambda event: asyncio.run(self.controller.ss8.move_backward(wait_for_completion=False)))
        self.backward_button.bind("<ButtonRelease-1>", lambda event: asyncio.run(self.controller.ss8.stop_mov()))
        self.backward_button.grid(row=1, column=1, padx=5, pady=5)
    
    def _display_cam_buttons(self):
        buttons_container = tk.Frame(self.container)
        buttons_container.pack(side=tk.RIGHT, pady=5, padx=50)
        # Directional buttons   

    def _display_preview(self):
        def img_click_callback(x, y):
            points = np.array([[x, y]], dtype=np.float32)
    
            # Initialize ImageSegmenter with a random (for now) bounding box
            self.controller.segmenter.initialize(self.controller.ss8.capture_image(), points=points)

            if(not self.object_selected):
                self.controller.ss8.display_text("Image selected")
                self.selection_buttons_frame.pack(anchor=tk.S, pady=20)
                self.object_selected = True

        self.img_preview = ImageWidget(self, 400, 300, img_click_callback)
        
        def update_preview():
            cv2.waitKey(1)
            prev_img = self.controller.ss8.capture_image()
            prev_img = self.controller.segmenter.mask_img(prev_img) if self.object_selected else prev_img
            return prev_img
        
        self.img_preview.display(update_preview, 10)

    def _display_selection_buttons(self):
        
        def cancel_selection():
            self.selection_buttons_frame.pack_forget()
            self.object_selected = False


        self.selection_buttons_frame = tk.Frame(self.container)

        ttk.Label(self.selection_buttons_frame, text="Vertical precision").grid(row=0, column=0, padx=5, pady=5)
        self.vert_prec_entry = ttk.Entry(self.selection_buttons_frame)
        self.vert_prec_entry.insert(tk.END, DEFAULT_VERTICAL_PRECISION)
        self.vert_prec_entry.grid(row=1, column=0, padx=5, pady=5)

        ttk.Label(self.selection_buttons_frame, text="Horizontal precision").grid(row=0, column=1, padx=5, pady=5)
        self.hor_prec_entry = ttk.Entry(self.selection_buttons_frame)
        self.hor_prec_entry.insert(tk.END, DEFAULT_HORIZONTAL_PRECISION)
        self.hor_prec_entry.grid(row=1, column=1, padx=5, pady=5)

        cancel_button = ttk.Button(self.selection_buttons_frame, text="Cancel selection")
        cancel_button.grid(row=2, column=0, padx=5, pady=5)
        cancel_button.bind("<ButtonRelease-1>", lambda event: cancel_selection())

        start_button = ttk.Button(self.selection_buttons_frame, text="Start the scan", style='Accent.TButton')
        start_button.grid(row=2, column=1, padx=5, pady=5)
        start_button.bind("<ButtonRelease-1>", lambda event: self._start_scan())

    
    def _start_scan(self):
        """Start the scanning process and destroy the preview window"""
        self.controller.navigator.set_precision(int(self.vert_prec_entry.get()), int(self.hor_prec_entry.get()))
        self.img_preview.destroy()
        self.controller.show_page("ScanningPage")