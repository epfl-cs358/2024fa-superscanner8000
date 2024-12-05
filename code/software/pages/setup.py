import tkinter as tk
from tkinter import ttk
import cv2

from widgets.image import ImageWidget

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
        label.pack(pady=10)

        self._display_preview()

        self._display_directionnal_buttons()
        # self._display_cam_buttons()

        button = ttk.Button(self.container, text="Start the scan", style='Accent.TButton')
        button.pack(pady=10)
        
    def _display_directionnal_buttons(self):
        buttons_container = tk.Frame(self.container)
        buttons_container.pack(pady=5)

        # Camera buttons
        self.cam_up_button = ttk.Button(buttons_container, text="Camera Up")
        self.cam_up_button.bind("<ButtonPress-1>", lambda event: self.controller.ss8.up_camera())
        self.cam_up_button.bind("<ButtonRelease-1>", lambda event: self.controller.ss8.stop_cam())
        self.cam_up_button.grid(row=1, column=0, padx=5, pady=5)

        self.cam_down_button = ttk.Button(buttons_container, text="Camera Down")
        self.cam_down_button.bind("<ButtonPress-1>", lambda event: self.controller.ss8.down_camera())
        self.cam_down_button.bind("<ButtonRelease-1>", lambda event: self.controller.ss8.stop_cam())
        self.cam_down_button.grid(row=1, column=2, padx=5, pady=5)

        # Directional buttons
        self.forward_button = ttk.Button(buttons_container, text="Forward")
        self.forward_button.bind("<ButtonPress-1>", lambda event: self.controller.ss8.move_forward())
        self.forward_button.bind("<ButtonRelease-1>", lambda event: self.controller.ss8.stop_mov())
        self.forward_button.grid(row=0, column=1, padx=5, pady=5)

        self.left_button = ttk.Button(buttons_container, text="Rotate Left")
        self.left_button.bind("<ButtonPress-1>", lambda event: self.controller.ss8.rotate_left())
        self.left_button.bind("<ButtonRelease-1>", lambda event: self.controller.ss8.stop_mov())
        self.left_button.grid(row=0, column=0, padx=5, pady=5)

        self.right_button = ttk.Button(buttons_container, text="Rotate Right")
        self.right_button.bind("<ButtonPress-1>", lambda event: self.controller.ss8.rotate_right())
        self.right_button.bind("<ButtonRelease-1>", lambda event: self.controller.ss8.stop_mov())
        self.right_button.grid(row=0, column=2, padx=5, pady=5)

        self.backward_button = ttk.Button(buttons_container, text="Backward")
        self.backward_button.bind("<ButtonPress-1>", lambda event: self.controller.ss8.move_backward())
        self.backward_button.bind("<ButtonRelease-1>", lambda event: self.controller.ss8.stop_mov())
        self.backward_button.grid(row=1, column=1, padx=5, pady=5)
    
    def _display_cam_buttons(self):
        buttons_container = tk.Frame(self.container)
        buttons_container.pack(side=tk.RIGHT, pady=5, padx=50)
        # Directional buttons

    def _display_preview(self):
        def img_click_callback(x, y):
            self.object_selected = True
            print(f"Clicked at: {x}, {y}")

        image = ImageWidget(self, 400, 300, img_click_callback)
        
        def update_preview():
            new_image = self.controller.ss8.capture_image()
            # new_image = self.controller.img_mixer.mask_img(new_image) if self.object_selected else new_image

            return new_image
        
        image.display(update_preview, 10)


