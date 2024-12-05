import tkinter as tk
from PIL import Image, ImageTk
import numpy as np
import cv2

class ImageWidget():
    def __init__(self, parent, width, height, img_click_callback):

        self.parent = parent
        self.width = width
        self.height = height
        self.img_click_callback = img_click_callback

    def set_image(self, image_array):
        """
        Updates the displayed image with a new image array.
        
        Args:
            image_array: A numpy array representing the new image.
        """
        cv2.imshow('Preview', image_array)


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

        def get_click_coords(event, x, y, flags, params):
            """
            Event handler for mouse click events. Stores the coordinates of the click.
            
            Args:
                event: The event object containing the click coordinates.
            """

            if event == cv2.EVENT_LBUTTONDOWN:
                self.img_click_callback(x, y)

        cv2.namedWindow("Preview", cv2.WINDOW_AUTOSIZE) 
        cv2.setMouseCallback('Preview', get_click_coords)
        
        def update_loop():
            new_image = update_callback()
            
            if new_image is not None:
                self.set_image(new_image)
            
            self.parent.after(1000 // fps, update_loop)

        update_loop()

# Example
if __name__ == "__main__":
    image_array = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
    ui = ImageWidget(image_array)
    ui.run()
