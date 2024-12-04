import tkinter as tk
from tkinter import ttk

from base64 import b64decode


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
        label = ttk.Label(self.container, text="Click on the object you want to scan")
        label.pack(pady=10)

        button = ttk.Button(self.container, text="Start the scan", style='Accent.TButton')
        button.pack(pady=10)

        self._display_directionnal_buttons()
        self._display_cam_buttons()
    
    def _display_directionnal_buttons(self):
        buttons_container = tk.Frame(self.container)
        buttons_container.pack(side=tk.LEFT, pady=5)
        # Directional buttons
        self.forward_button = ttk.Button(buttons_container, text="Forward")
        self.forward_button.bind("<ButtonPress-1>", lambda event: self.controller.ss8.move_forward())
        self.forward_button.bind("<ButtonRelease-1>", lambda event: self.controller.ss8.stop_mov())
        self.forward_button.pack(pady=5)

        self.left_button = ttk.Button(buttons_container, text="Rotate Left")
        self.left_button.bind("<ButtonPress-1>", lambda event: self.controller.ss8.rotate_left())
        self.left_button.bind("<ButtonRelease-1>", lambda event: self.controller.ss8.stop_mov())
        self.left_button.pack(side=tk.LEFT, padx=5)

        self.right_button = ttk.Button(buttons_container, text="Rotate Right")
        self.right_button.bind("<ButtonPress-1>", lambda event: self.controller.ss8.rotate_right())
        self.right_button.bind("<ButtonRelease-1>", lambda event: self.controller.ss8.stop_mov())
        self.right_button.pack(side=tk.RIGHT, padx=5)

        self.backward_button = ttk.Button(buttons_container, text="Backward")
        self.backward_button.bind("<ButtonPress-1>", lambda event: self.controller.ss8.move_backward())
        self.backward_button.bind("<ButtonRelease-1>", lambda event: self.controller.ss8.stop_mov())
        self.backward_button.pack(pady=5)
    
    def _display_cam_buttons(self):
        buttons_container = tk.Frame(self.container)
        buttons_container.pack(side=tk.RIGHT, pady=5, padx=50)
        # Directional buttons
        self.up_button = ttk.Button(buttons_container, text="Camera Up")
        self.up_button.bind("<ButtonPress-1>", lambda event: self.controller.ss8.up_camera())
        self.up_button.bind("<ButtonRelease-1>", lambda event: self.controller.ss8.stop_cam())
        self.up_button.pack(pady=5)

        self.down_button = ttk.Button(buttons_container, text="Camera Down")
        self.down_button.bind("<ButtonPress-1>", lambda event: self.controller.ss8.down_camera())
        self.down_button.bind("<ButtonRelease-1>", lambda event: self.controller.ss8.stop_cam())
        self.down_button.pack(pady=5)

    def _display_preview(self):
        raw_image = self.controller.ss8.capture_image()
        raw_image = self.controller.img_mixer.mask_img(raw_image) if self.object_selected else raw_image

        base64_image = self.controller.img_mixer.convert_img_to_base64(raw_image)
        image = tk.PhotoImage(data=b64decode(base64_image))
        label = ttk.Label(image=image)
        label.pack()
        self.update_idletasks()
