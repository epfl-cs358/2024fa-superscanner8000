import numpy as np
from webserver import ESP32CAM
from esp32s2 import Car
from ui import ImageUI
from software.app.controller.image_segmenter import ImageSegmenter
import cv2

def main():
    esp32cam = ESP32CAM("http://172.20.10.8:80/stream")
    frame = esp32cam.get_frame()

    if frame is None or frame.size == 0:
        print("Failed to receive initial frame.")
        return
    
    # Initialize UI with the first frame
    ui = ImageUI(frame)

    def wait_for_click():
        while not ui.has_click():
            frame = esp32cam.get_frame()
            if frame is not None and frame.size != 0:
                ui.update_image(frame)
            ui.root.update_idletasks()
            ui.root.update()

    wait_for_click()
    points = np.array([ui.click_coords], dtype=np.float32)
    
    # Initialize ImageSegmenter with a random (for now) bounding box
    segmenter = ImageSegmenter(model_cfg="sam2_hiera_s.yaml", checkpoint="sam2_checkpoints/sam2_hiera_small.pt", expand_pixels=10)
    segmenter.initialize(frame, points=points)

    def update_frame():
        frame = esp32cam.get_frame()

        if frame is None or frame.size == 0:
            print("Received an invalid frame, retrying...")
            return

        # Segment the frame
        mask = segmenter.propagate(frame)

        frame = cv2.addWeighted(frame, 1, mask, 1, 0)

        # Update the UI with the segmented frame
        ui.update_image(frame)

    ui.run(update_frame)

if __name__ == "__main__":
    main()