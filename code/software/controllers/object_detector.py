import cv2
import numpy as np
import torch
from controllers.image_segmenter import ImageSegmenter
from controllers.navigator import Navigator
from controllers.ss8 import SS8
import sys, pathlib, asyncio

path_to_da = pathlib.Path(__file__).parent / "packages/depth_anything_v2"
sys.path.insert(0, str(path_to_da))
from packages.depth_anything_v2.depth_anything_v2.dpt import DepthAnythingV2

import time


class Object_Detector:
    def __init__(self, navigator: Navigator, ss8: SS8, visualize=False):
        self.segmenter = ImageSegmenter(model_cfg="sam2_hiera_s.yaml", checkpoint="config/sam2_checkpoints/sam2_hiera_small.pt", expand_pixels=10)
        self.navigator = navigator
        self.ss8 = ss8
        self.hfov = np.deg2rad(95) # Horizontal field of view set according to OV5640 datasheet
        self.occupancy_map = None
        self.frame = None
        self.depth = None
        if visualize:
            # Initialize rerun
            rr.init("Occupancy Map", spawn=True)

        self.must_detect = False
        self._init_depth_anything()


    def _init_depth_anything(self):
        # Init DepthAnything model
        DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'

        model_configs = {
            'vits': {'encoder': 'vits', 'features': 64, 'out_channels': [48, 96, 192, 384]},
            'vitb': {'encoder': 'vitb', 'features': 128, 'out_channels': [96, 192, 384, 768]},
            'vitl': {'encoder': 'vitl', 'features': 256, 'out_channels': [256, 512, 1024, 1024]},
            'vitg': {'encoder': 'vitg', 'features': 384, 'out_channels': [1536, 1536, 1536, 1536]}
        }

        encoder = 'vits'
        depth_anything = DepthAnythingV2(**model_configs[encoder])
        depth_anything.load_state_dict(torch.load('config/depth_anything/depth_anything_v2_vits.pth', map_location='cpu'))
        self.depth_anything = depth_anything.to(DEVICE).eval()
    
    def _get_intrinsic_matrix(self, hfov: float, frame = None):
        '''
        hfov: Horizontal field of view in radians
        frame: Frame to get the intrinsic matrix from
        '''
        
        cx = frame.shape[1] / 2
        cy = frame.shape[0] / 2 
        focal_length = 0.25
        sensor_pixel_size = 1.4e-4
        fx = focal_length / sensor_pixel_size #frame.shape[0] / (2 * np.tan(hfov / 2.)) #
        fy = focal_length / sensor_pixel_size #frame.shape[1] / (2 * np.tan(70 / 2.)) #
        return np.array([
            [fx, 0., cx],
            [0., fy, cy],
            [0., 0., 1]])
    
    def _get_rotation_matrix(self, angle: float):
        '''
        angle: Angle in radians
        '''
        return np.array([
            [np.cos(angle), -np.sin(angle)],
            [np.sin(angle), np.cos(angle)]
        ])
    
    def _pixel_max_resize(self, img, h, w):
        source_h, source_w = img.shape[:2]
        return img.reshape(h,source_h // h,-1,source_w // w).swapaxes(1,2).reshape(h,w,-1).max(axis=2)

    def _pixelate(self, image: np.ndarray, pixel_size: int = 16):
        '''
        image: Image to pixelate
        pixel_size: Size of the pixelation
        '''
        height, width = image.shape[:2]

        w, h = (width//pixel_size, height//pixel_size)
        pixelated_image_small = self._pixel_max_resize(image, h, w)
        #pixelated_image_small = cv2.resize(image, (w, h), interpolation=cv2.INTER_LINEAR)
        pixelated_image = cv2.resize(pixelated_image_small, (width, height), interpolation=cv2.INTER_NEAREST)

        return pixelated_image

        # TODO: Nearest ground point is at 24 cm, so we can use this as a base value
    
    def _get_depth_map(self, frame: np.ndarray):
        # Convert to rgb
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        depth = 1 / (self.depth_anything.infer_image(frame))# / 10 # Mapped from 0 to 10
        min_depth = np.min(depth)
        ratio = 25 / min_depth
        return depth * ratio # Depth map where values are in cm
    
    def _update_occupancy_map(self, depth: np.ndarray, threshold_distance: float = 100): # TODO: Adjust for base value
        """
        Get the occupancy map from the depth map
        depth: Depth map
        threshold_distance: Distance threshold to consider an object as an obstacle in cm
        """
        self.occupancy_map = (depth < threshold_distance).astype(np.uint8)# 1 = occupied, 0 = free

    def get_occupancy_map(self):
        return self.occupancy_map * 255
    
    def get_depth_map(self):
        return self.depth
    
    def get_frame(self):
        return self.frame
    
    def _project_to_world(self, pixel_index, T, R, depth, hfov, frame):
        '''
        pixel_index: 3x1 array with the pixel index
        T: 3x1 array with the translation vector
        R: 3x3 array with the rotation matrix
        depth: pixel depth value
        hfov: horizontal field of view
        '''
        #camera_position = (np.linalg.inv(self._get_intrinsic_matrix(hfov, frame)) @ pixel_index) * depth
        cx = frame.shape[1] / 2
        cy = frame.shape[0] / 2 
        sensor_pixel_size = 1.4e-4
        focal_length = 0.25

        # TODO: Check if this is correct
        Xc = depth
        Yc = (pixel_index[0] - cy) * depth / (focal_length/sensor_pixel_size)
        camera_position = np.array([Xc, Yc[0]])
        

        world_position = R @ camera_position + T #np.linalg.inv(R) @
        #print(f"Camera position: {camera_position} World position: {world_position} T position: {T.T}")

        # get 2d camera position norm
        camera_position_norm = np.linalg.norm(camera_position)

        return world_position
    
    def _segment_ground(self, frame):
        '''
        Returns a mask with the ground segmented where 0 is the ground and 1 is the rest
        '''

        if not self.segmenter.is_init:
            points = np.array([[0, frame.shape[0] - 1]], dtype=np.float32)#np.linspace([0, frame.shape[0] - 1], [frame.shape[1] - 1, frame.shape[0] - 1], 10, dtype=np.uint8) #
            self.segmenter.initialize(frame, points=points)
            ground_mask = self.segmenter.propagate(frame)

        else:   
            ground_mask = self.segmenter.propagate(frame)

        return (cv2.cvtColor(ground_mask, cv2.COLOR_RGB2GRAY) == 0).astype(np.uint8)

    def _compute_perspective_views(self, depth, frame, T, R, pixel_size = 16, hfov = np.pi/6):
        height, width = depth.shape

        pixelated_depth = self._pixelate(depth, pixel_size=pixel_size)
        pixelated_rgb = self._pixelate(frame, pixel_size=pixel_size)
        pixelated_rgb = cv2.cvtColor(pixelated_rgb, cv2.COLOR_BGR2RGB)

        # Square array of size of pixelated_depth width
        top_view = np.ones((width, width))
        pos_3d = []
        colors = []

        for i in range(0, width, pixel_size):
            for j in range(0, height, pixel_size):
                # Get the pixelated depth value
                value = pixelated_depth[j, i]
                if value == 0:
                    continue
                # Set the pixelated depth value to all pixels in the square
                #top_view[i:i+pixel_size, d:d+pixel_size] = 0

                pixel_index = np.array([i, j, 1]).reshape(3, 1)
                pixel_coords = self._project_to_world(pixel_index, T, R, value, hfov, frame)

                # Check if values are not nan
                if not np.isnan(pixel_coords).any():
                    pos_3d.append(pixel_coords)
                    colors.append(pixelated_rgb[j, i])
        
        return top_view, pixelated_depth, np.array(pos_3d), np.array(colors)

    def _request_frame(self):
        
        frame = self.ss8.capture_image('front')
        if frame is not None:
            # rotate 90 degrees
            frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        return frame

    def start_detection(self):
        frame = self._request_frame()
        if frame is not None:
            ground_mask = self._segment_ground(frame)
            self.depth = self._get_depth_map(frame)
            self._update_occupancy_map(self.depth, 70)

            # substract occupancy map by ground mask
            self.occupancy_map = cv2.multiply(self.occupancy_map, ground_mask)
            self.depth = cv2.multiply(self.depth, self.occupancy_map.astype(np.float32))

            # Convert ss8 position to 3d position
            T = self.navigator.ss8_pos
            R = self._get_rotation_matrix(self.navigator.ss8_angle) 

            top_view, pixelated_depth, pos_3d, colors = self._compute_perspective_views(
                                    self.depth, frame, T, R, pixel_size=20, hfov=self.hfov)
            self.depth = pixelated_depth
            
            #print(pos_3d.shape)
            

            for pos in pos_3d:
                if np.linalg.norm(pos - T) > 15:
                    self.navigator.add_obstacle(pos, -100000)
                    #print(T, pos, np.linalg.norm(pos - T))
                    

    def detect_occupancy(self):
        frame = self._request_frame()


        if frame is not None:
            depth = self._get_depth_map(frame)
            self._update_occupancy_map(depth)
            
            #self.occupancy_map = self._segment_ground(frame, self.occupancy_map)

            depth = cv2.multiply(depth, self.occupancy_map.astype(np.float32))
            self.depth = depth
            # Convert ss8 position to 3d position
            T = np.array([self.navigator.ss8_pos[0], self.navigator.ss8_pos[1], 0]).reshape(3, 1)
            top_view, pixelated_depth, pos_3d, colors = self._compute_perspective_views(
                                    depth, frame, T, 
                                    self._get_rotation_matrix(self.navigator.ss8_angle) , pixel_size=16, hfov=self.hfov)
            # TODO: Display top view

            for pos in pos_3d:
                self.navigator.add_obstacle(pos)
        
        # await asyncio.sleep(0.1)

        # if self.must_detect:
        #     await self.detect_occupancy()
        



if __name__ == "__main__":
    # Load webcam
    cap = cv2.VideoCapture(0)
    object_detector = Object_Detector(Navigator(), visualize=True)


    start_time = time.time()
    i = 0
    # Play webcam
    while True:
        import rerun as rr
        ret, frame = cap.read()
        frame = cv2.resize(frame, (256, 128))

        depth, depth_normalized = object_detector._get_depth_map(frame)
        clean_depth = cv2.cvtColor(depth.copy(), cv2.COLOR_GRAY2BGR)


        # Remove ground from occupancy map
        if not object_detector.segmenter.is_init:
            points = np.array([[0, frame.shape[0] - 1], [frame.shape[1] - 1, frame.shape[0] - 1]], dtype=np.float32)
            object_detector.segmenter.initialize(frame, points=points)
        else:   
            ground_mask = object_detector.segmenter.propagate(frame)
            occupancy_map = cv2.subtract(occupancy_map, cv2.cvtColor(ground_mask, cv2.COLOR_RGB2GRAY))

        
        # Apply occupancy map to depth image
        depth = cv2.multiply(depth, occupancy_map.astype(np.float32))
        frame_masked = cv2.multiply(frame, cv2.cvtColor(occupancy_map, cv2.COLOR_GRAY2BGR))

        pixel_size = 16
        hfov = np.deg2rad(95)

        # Compute top view
        top_view, pixelated_depth, pos_3d, colors = object_detector._compute_perspective_views(depth, frame, pixel_size=pixel_size, hfov=hfov) # TODO: Adjust for hfov



        
        height, width = depth.shape

        depth = cv2.cvtColor(depth, cv2.COLOR_GRAY2BGR)
        occupancy_map = cv2.cvtColor(occupancy_map, cv2.COLOR_GRAY2BGR) * 255
        pixelated_depth = cv2.cvtColor(pixelated_depth, cv2.COLOR_GRAY2BGR)

        top_view = cv2.cvtColor(top_view.astype(np.uint8), cv2.COLOR_GRAY2BGR) * 255
        top_view = cv2.resize(top_view, (width, height), interpolation=cv2.INTER_NEAREST)

        # Concatenate depth, pixelated depth and occupancy map
        output = np.concatenate((clean_depth, depth, pixelated_depth, occupancy_map, top_view), axis=1)
        #output = np.concatenate((edges1, edges2, edges3, edges4), axis=1)

        #cv2.imshow('frame', output)

        rr.log(f"2d_views/clean_depth", rr.Clear(recursive=False))
        rr.log(f"2d_views/depth", rr.Clear(recursive=False))
        rr.log(f"2d_views/pixelated_depth", rr.Clear(recursive=False))
        rr.log(f"2d_views/occupancy_map", rr.Clear(recursive=False))
        rr.log(f"2d_views/top_view", rr.Clear(recursive=False))


        rr.set_time_seconds("stable_time", time.time() - start_time)

        rr.log(
            "world/points",
            rr.Points3D(pos_3d, radii=pixel_size/2, colors=colors),
        )
        rr.log("2d_views/clean_depth", rr.Image(clean_depth))
        rr.log("2d_views/depth", rr.Image(depth))
        rr.log("2d_views/pixelated_depth", rr.Image(pixelated_depth))
        rr.log("2d_views/occupancy_map", rr.Image(occupancy_map))
        rr.log("2d_views/top_view", rr.Image(top_view))
        rr.log("world/camera", rr.Transform3D(translation=np.zeros((3)), mat3x3=np.diag([1, 1, 1])))
        rr.log(
            "world/camera/pinhole",
            rr.Pinhole(fov_y=hfov, aspect_ratio=1.7777778, camera_xyz=rr.ViewCoordinates.RUB, image_plane_distance=3),
        )

        i += 1

        # if cv2.waitKey(1) & 0xFF == ord('q'):
        #     break
