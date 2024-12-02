import torch
import numpy as np
import cv2
from sam2 import build_sam
# use bfloat16 for the entire notebook
torch.autocast(device_type="cuda", dtype=torch.bfloat16).__enter__()

if torch.cuda.get_device_properties(0).major >= 8:
    torch.backends.cuda.matmul.allow_tf32 = True
    torch.backends.cudnn.allow_tf32 = True

class ImageSegmenter:
    def __init__(self, model_cfg, checkpoint, expand_pixels=0):
        self.predictor = build_sam.build_sam2_camera_predictor(model_cfg, checkpoint)
        self.if_init = False
        self.expand_pixels = expand_pixels

    def initialize(self, frame, points=None, bbox=None):
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        self.width, self.height = frame.shape[:2][::-1]

        self.predictor.load_first_frame(frame)
        self.if_init = True

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

    def propagate(self, frame):
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        out_obj_ids, out_mask_logits = self.predictor.track(frame)

        all_mask = np.zeros((self.height, self.width, 1), dtype=np.uint8)
        for i in range(0, len(out_obj_ids)):
            out_mask = (out_mask_logits[i] > 0.0).permute(1, 2, 0).cpu().numpy().astype(
                np.uint8
            ) * 255
            if self.expand_pixels > 0:
                kernel = np.ones((self.expand_pixels, self.expand_pixels), np.uint8)
                out_mask = cv2.dilate(out_mask, kernel, iterations=1)
            all_mask = cv2.bitwise_or(all_mask, out_mask)

        return cv2.cvtColor(all_mask, cv2.COLOR_GRAY2RGB)
    
if __name__ == "__main__":

    scanner = ImageSegmenter(model_cfg="sam2_hiera_s.yaml", checkpoint="sam2_checkpoints/sam2_hiera_small.pt", expand_pixels=10)

    cap = cv2.VideoCapture("./IMG_4225.MOV")

    while True:
        ret, frame = cap.read()
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        if not ret:
            break

        if not scanner.if_init:
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
