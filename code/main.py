import numpy as np
from webserver import ESP32CAM
from ui import ImageUI
from image_segmentation import ImageSegmentation

def main():
    esp32cam = ESP32CAM("http://172.20.10.8:80/stream")
    frame = esp32cam.get_frame()

    if frame is None or frame.size == 0:
        print("Failed to receive initial frame.")
        return

    # Initialize UI with the first frame
    ui = ImageUI(frame)

    # Initialize ImageSegmentation with a random (for now) bounding box
    bbox = np.array([[100, 150], [100, 150]], dtype=np.float32)
    segmenter = ImageSegmentation(frame, bbox=bbox)

    def update_frame():
        frame = esp32cam.get_frame()

        if frame is None or frame.size == 0:
            print("Received an invalid frame, retrying...")
            return

        # Segment the frame
        segmented_frame = segmenter.propagate(frame)

        # Update the UI with the segmented frame
        ui.update_image(segmented_frame)

    ui.run(update_frame)

if __name__ == "__main__":
    main()