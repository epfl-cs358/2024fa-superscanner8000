import torch
import numpy as np
import cv2
from sam2 import build_sam
import os, tempfile, shutil
import base64
from config.dev_config import DEBUG_CAM

# use bfloat16 for the entire notebook
torch.autocast(device_type="cuda", dtype=torch.bfloat16).__enter__()

if torch.cuda.get_device_properties(0).major >= 8:
    torch.backends.cuda.matmul.allow_tf32 = True
    torch.backends.cudnn.allow_tf32 = True

class ImageSegmenter:
    def __init__(self, model_cfg, checkpoint, expand_pixels=0):
        self.predictor = build_sam.build_sam2_camera_predictor(model_cfg, checkpoint)
        self.is_init = False
        self.expand_pixels = expand_pixels  
        self.all_mask = None
        self.frame_counter = 0

    def initialize(self, frame, points=None, bbox=None):
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        self.width, self.height = frame.shape[:2][::-1]

        self.predictor.load_first_frame(frame)
        self.is_init = True

        ann_frame_idx = 0  # the frame index we interact with
        ann_obj_id = 1  # give a unique id to each object we interact with (it can be any integers)

        if points is not None:
            labels = np.array([1] * len(points), dtype=np.int32)
            _, self.out_obj_ids, self.out_mask_logits = self.predictor.add_new_prompt(
                frame_idx=ann_frame_idx, obj_id=ann_obj_id, points=points, labels=labels
            )
        elif bbox is not None:
            _, self.out_obj_ids, self.out_mask_logits = self.predictor.add_new_prompt(
                frame_idx=ann_frame_idx, obj_id=ann_obj_id, bbox=bbox
            )

    def propagate(self, img:cv2.typing.MatLike):
        """
        Get the mask for the given image
        """
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        out_obj_ids, out_mask_logits = self.predictor.track(img)

        all_mask = np.zeros((self.height, self.width, 1), dtype=np.uint8)
        for i in range(0, len(out_obj_ids)):
            out_mask = (out_mask_logits[i] > 0.0).permute(1, 2, 0).cpu().numpy().astype(
                np.uint8
            ) * 255
            if self.expand_pixels > 0:
                kernel = np.ones((self.expand_pixels, self.expand_pixels), np.uint8)
                out_mask = cv2.dilate(out_mask, kernel, iterations=1)
            all_mask = cv2.bitwise_or(all_mask, out_mask)

        self.all_mask = all_mask
        return cv2.cvtColor(self.all_mask, cv2.COLOR_GRAY2RGB)
    
    def mask_img(self, img:cv2.typing.MatLike) -> cv2.typing.MatLike:
        """
        Masks the given image with the object mask.
            img (cv2.typing.MatLike): The image to mask.
        """

        # Only keep pixels from frame that are selected in all_mask
        mask = cv2.cvtColor(self.propagate(img), cv2.COLOR_RGB2GRAY)
        return cv2.bitwise_and(img, img, mask=mask)
    
    def save_mask(self):
        if self.all_mask is not None:
            # Get the system's temporary directory
            temp_dir = os.path.join(tempfile.gettempdir(), "superscanner8000/masks")
            # Create the temporary directory if it doesn't exist or delete if it does
            
            if not os.path.exists(temp_dir):
                os.makedirs(temp_dir)
            elif self.frame_counter == 0:
                shutil.rmtree(temp_dir)
                os.makedirs(temp_dir)
            else:
                pass

            # Construct the full path for the file with a numbered filename
            filename = f"{self.frame_counter}.mask.png"
            temp_file_path = os.path.join(temp_dir, filename)
            # Save theself.current_frame to the temporary folder
            cv2.imwrite(temp_file_path, self.all_mask)
            if DEBUG_CAM:
                print(f"Saved self.all_mask {self.frame_counter} to {temp_file_path}")
            # Increment theself.current_frame counter
            self.frame_counter += 1
        else:
            if DEBUG_CAM:
                print("No frame available to save.")
        
    def get_object_coords(self, img, update_mask=False):
        """
        Get the coordinates of the object in the image.
        """
        if update_mask:
            self.propagate(img)
        
        if self.all_mask is None: #TODO: Check with Mateo
            return None
        
        contours, _ = cv2.findContours(self.all_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if len(contours) > 0:
            bounding_box = cv2.boundingRect(contours[0])
            return [bounding_box[0]+bounding_box[2]//2, bounding_box[1]+bounding_box[3]//2]
        return None
    
    def convert_img_to_base64(img):
        # Convert the frame to base64
        _, buffer = cv2.imencode('.jpg', img)
        return base64.b64encode(buffer).decode('utf-8')

if __name__ == "__main__":

    scanner = ImageSegmenter(model_cfg="sam2_hiera_s.yaml", checkpoint="../config/sam2_checkpoints/sam2_hiera_small.pt", expand_pixels=10)

    cap = cv2.VideoCapture("../assets/test-video.mp4")

    while True:
        ret, frame = cap.read()
        if frame is None:
            continue
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        if not ret:
            break

        if not scanner.is_init:
            points = np.array([[608, 253]], dtype=np.float32)
            scanner.initialize(frame, points=points)
        else:
            all_mask = scanner.propagate(frame)
            frame = cv2.addWeighted(frame, 1, all_mask, 1, 0)

        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        cv2.imshow("frame", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
