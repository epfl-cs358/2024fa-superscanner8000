import tkinter as tk
from PIL import Image, ImageTk
import numpy as np

class ImageUI:
    def __init__(self, image_array):
        self.root = tk.Tk()
        self.image_array = image_array
        self.image = Image.fromarray(image_array)
        self.photo = ImageTk.PhotoImage(self.image)
        
        self.canvas = tk.Canvas(self.root, width=self.image.width, height=self.image.height)
        self.canvas.pack()
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)
        
        self.canvas.bind("<Button-1>", self.get_click_coords)
        self.click_coords = None

    def get_click_coords(self, event):
        self.click_coords = np.array([event.x, event.y])
        print(f"Clicked at: {self.click_coords}")

    def update_image(self, image_array):
        self.image_array = image_array
        self.image = Image.fromarray(image_array)
        self.photo = ImageTk.PhotoImage(self.image)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)

    def run(self, update_callback):
        def update_loop():
            update_callback()
            self.root.after(100, update_loop)

        self.root.after(100, update_loop)
        self.root.mainloop()

# Example
if __name__ == "__main__":
    image_array = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
    ui = ImageUI(image_array)
    ui.run()
