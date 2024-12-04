import tkinter as tk
from PIL import Image, ImageTk
import numpy as np

class ImageWidget(tk.Frame):
    def __init__(self, parent, image_array):
        super().__init__(parent)

        self.image_array = image_array
        self.image = Image.fromarray(image_array)
        self.photo = ImageTk.PhotoImage(self.image)
        
        self.canvas = None
        
        self.canvas.bind("<Button-1>", self.get_click_coords)
        self.click_coords = None

    def get_click_coords(self, event):
        """
        Event handler for mouse click events. Stores the coordinates of the click.
        
        Args:
            event: The event object containing the click coordinates.
        """
        self.click_coords = np.array([event.x, event.y])
        print(f"Clicked at: {self.click_coords}")

    def set_image(self, image_array):
        """
        Updates the displayed image with a new image array.
        
        Args:
            image_array: A numpy array representing the new image.
        """
        self.image_array = image_array
        self.image = Image.fromarray(image_array)
        self.photo = ImageTk.PhotoImage(self.image)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)

    def has_click(self):
        """
        Checks if there has been a mouse click on the image.
        
        Returns:
            bool: True if there has been a click, False otherwise.
        """
        return self.click_coords is not None

    def display(self, update_callback, fps=10):
        """
        Displays the image and starts an update loop to refresh the display.
        
        Args:
            update_callback: A callback function to update the image.
            fps: Frames per second for the update loop.
        """
        self.canvas = tk.Canvas(self, width=self.image.width, height=self.image.height)
        self.canvas.pack()
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)


        def update_loop():
            update_callback()
            self.update_idletasks()
            self.after(1000/fps, update_loop)

        update_loop()

# Example
if __name__ == "__main__":
    image_array = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
    ui = ImageWidget(image_array)
    ui.run()
