import tkinter as tk
from PIL import Image, ImageTk
import numpy as np
import cv2

PREVIEW_WINDOW_NAME = "Preview"

class ImageWidget():
    def __init__(self, parent, width, height, img_click_callback):

        self.parent = parent
        self.width = width
        self.height = height
        self.img_click_callback = img_click_callback
        self.canvas = tk.Canvas(parent, width=width, height=height)
        self.canvas.pack(padx=30, pady=0)
        #self.canvas.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        self.canvas.bind("<Button-1>", self.on_click)
        self.image_on_canvas = None

    def set_image(self, image_array):
        """
        Updates the displayed image with a new image array.
        
        Args:
            image_array: A numpy array representing the new image.
        """
        self.image = ImageTk.PhotoImage(image=Image.fromarray(image_array))
        if self.image_on_canvas is None:
            self.image_on_canvas = self.canvas.create_image(0, 0, anchor=tk.NW, image=self.image)
        else:
            self.canvas.itemconfig(self.image_on_canvas, image=self.image)
    
    def display(self, update_callback, fps=10):
        """
        Displays the image and starts an update loop to refresh the display.
        Args:
            update_callback: A callback function to update the image.
            fps: Frames per second for the update loop.
        """
        def update_loop():
            new_image = update_callback()
            if new_image is not None:
                self.set_image(new_image)
            self.parent.after(1000 // fps, update_loop)
        update_loop()

    def on_click(self, event):
        """
        Event handler for mouse click events. Stores the coordinates of the click.
        
        Args:
            event: The event object containing the click coordinates.
        """
        self.img_click_callback(event.x, event.y)

    def destroy(self):
        """
        Destroys the image window.
        """
        self.canvas.destroy()

# Example
if __name__ == "__main__":
    root = tk.Tk()
    image_array = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
    ui = ImageWidget(root, 100, 100, lambda x, y: print(f"Clicked at ({x}, {y})"))
    ui.set_image(image_array)
    ui.display(lambda: np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8), fps=10)
    root.mainloop()
