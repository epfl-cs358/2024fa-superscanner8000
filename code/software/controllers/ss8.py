import requests 
import asyncio
import cv2
import os
import numpy as np
import config.dev_config as dconfig

from controllers.udp_receiver import UDPReceiver

# SS8 connection constants
DEFAULT_API_URL = "http://superscanner8000:80"
DEFAULT_TOP_CAM_URL = "http://superscanner8008:80"
DEFAULT_FRONT_CAM_URL = "http://superscanner8009:80"
TEST_CONNECTION_TIMEOUT = 3

# SS8 movement constants
DEFAULT_MOVING_DIST = 1000
DEFAULT_ROTATING_ANGLE = np.pi/2
BODY_ANGLE_TO_TIME = 1591.55 # Time to rotate the body by 1 radian            TODO: Update this value
BODY_DIST_TO_TIME = 66 # Time to move the body by 1 cm                   TODO: Update this value
TOP_CAM_ANGLE_TO_TIME = 1 # Time to rotate the top camera by 1 radian
TOP_CAM_FOV = 60

# Dev config constants
TEST_CONNECTION_TIMEOUT = 3
TEST_SEG_WITH_VID = False
CONNECT_TO_MOV_API = False

class SS8:
    def  __init__(self, controller, disconnected_callback):
        """
        Initializes the SS8 class with default values.
        """
        self.controller = controller
        self.connection_lost_callback = disconnected_callback

        self.top_cam_udp_receiver = UDPReceiver(12346, "0.0.0.0")
        self.front_cam_udp_receiver = UDPReceiver(22222, "0.0.0.0")

    # Connection methods

    def get_default_urls(self):
        """
        Returns the default hostname of the device.

        Returns:
            str: The default hostname.
        """
        return DEFAULT_API_URL,DEFAULT_TOP_CAM_URL,DEFAULT_FRONT_CAM_URL
       
    def connect(self, api_url=DEFAULT_API_URL, top_cam_url=DEFAULT_TOP_CAM_URL, front_cam_url=DEFAULT_FRONT_CAM_URL) -> bool:
        """
        Test connection to the given hostname.

        Args:
            hostname (str): The hostname to connect to.
            timeout (int): The timeout for the connection in seconds.

        Returns:
            bool: True if the connection is successful.
        """

        self.api_url = api_url
        self.top_cam_url = top_cam_url
        self.front_cam_url = front_cam_url

        if dconfig.CONNECT_TO_MOV_API and not self.init_api_connection():
            return False
        
        # Test connection to the camera hostname and start receiving video stream
        if(dconfig.TEST_SEG_WITH_VID):
            if not self.fake_init_udp_connection():
                return False
        elif not self.init_udp_connection():
            return False

        return True
    
    def init_api_connection(self) -> bool:
        """
        Initialize the API connection to the device.
        Returns:
            bool: True if the connection is successful.
        """
        try:
            res = requests.get(self.api_url+"/status", timeout=TEST_CONNECTION_TIMEOUT)
            if res.status_code == 200:
                print("Connection successful! Server is reachable.")
            else:
                print(f"Server responded with status code: {res.status_code}")
                return False
        except requests.ConnectionError:
            print("Connection failed. Server is unreachable.")
            return False
        except requests.Timeout:
            print("Connection timed out.")
            return False
        except Exception as e:
            print(f"An error occurred: {e}")
            return False
        
        return True

    def init_udp_connection(self) -> bool:
        if dconfig.CONNECT_TO_TOP_CAM :
            try:
                self.top_cam_udp_receiver.start_listening(self.top_cam_url)
            except Exception as e:
                print(f"An error occurred for the top cam: {e}")
                return False
        
        if dconfig.CONNECT_TO_FRONT_CAM:
            try:
                self.front_cam_udp_receiver.start_listening(self.front_cam_url)
            except Exception as e:
                print(f"An error occurred for the front cam: {e}")
                return False
        
        
        return True
    
    def fake_init_udp_connection(self) -> bool:
        """
        Initialize the UDP connection to the device.
        Returns:
            bool: True if the connection is successful.
        """

        video_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'assets', 'test-video.mp4')
        if not os.path.exists(video_path):
            print(f"Video file not found: {video_path}")
            return False
        
        cap = cv2.VideoCapture(video_path)
        video_fps = cap.get(cv2.CAP_PROP_FPS)

        def update_current_frame():
            ret, frame = cap.read()
            if(not ret):
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

            if (cv2.waitKey(1) & 0xFF == ord('q')):
                cap.release()
                cv2.destroyAllWindows()
                return

            #cv2.imshow('Frame', frame)
            self.fake_current_frame = frame

            self.controller.after(int(1000 // video_fps), update_current_frame)

        update_current_frame()

        return True

    # Instrucitons methods

    async def _send_req(self, req_func, on_error=lambda: None):
        """
        Send a request to the connected device.

        Args:
            req_func (function): The request function to call.
            on_error (function): The error callback function.
            on_success (function): The success callback function.
        """
        try:
            res = req_func()
            if res.status_code == 200:
                return res.json()
            else:
                on_error()
        except requests.ConnectionError:
            self.connection_lost_callback()
        except Exception as e:
            print(f"An error occurred: {e}")
            self.connection_lost_callback()
    
    async def move_forward(self, dist=DEFAULT_MOVING_DIST, wait_for_completion=True):
        """
        Move the device forward.
        dist (int): The distance or duration to move. If positive, the device moves for the given time.
        """
        ms = dist*BODY_DIST_TO_TIME

        if not dconfig.SIMULATION_MODE:
            await self._send_req(lambda: requests.post(self.api_url + "/fwd", json={"ms": ms}))
        print(f"Moving forward of {dist} cm...")
        
        if wait_for_completion:
            await asyncio.sleep(ms*0.001)
        return

    async def move_backward(self, dist=DEFAULT_MOVING_DIST, wait_for_completion=True):
        """
        Move the device backward.
        dist (int): The distance or duration to move. If positive, the device moves for the given time.
        """
        ms=dist*BODY_DIST_TO_TIME

        if not dconfig.SIMULATION_MODE:
            await self._send_req(lambda: requests.post(self.api_url + "/bwd", json={"ms": ms}))
        print(f"Moving backward of {dist} cm...")

        if wait_for_completion:
            await asyncio.sleep(ms*0.001)

        return
        
    async def rotate_left(self, angle=DEFAULT_ROTATING_ANGLE, wait_for_completion=True):
        """
        Rotate the device to the left.
        angle (int): The angleance or duration to rotate. If positive, the device rotates for the given time. 
                    If negative, the device rotates until it stops.
        """
        ms=angle*BODY_ANGLE_TO_TIME

        if not dconfig.SIMULATION_MODE:
            await self._send_req(lambda: requests.post(self.api_url + "/hlft", json={"ms": angle*BODY_ANGLE_TO_TIME}))
        
        print(f"Rotating left of {round(angle*180/np.pi)} degrees...")

        if wait_for_completion:
            await asyncio.sleep(ms*0.001)

        return
        
    async def rotate_right(self, angle=DEFAULT_ROTATING_ANGLE, wait_for_completion=True):
        """
        Rotate the device to the right.
        angle (int): The angleance or duration to rotate. If positive, the device rotates for the given time. 
                    If negative, the device rotates until it stops.
        
        """
        ms=angle*BODY_ANGLE_TO_TIME

        if not dconfig.SIMULATION_MODE:
            await self._send_req(lambda: requests.post(self.api_url + "/hrgt", json={"ms": angle*BODY_ANGLE_TO_TIME}))
        print(f"Rotating right of {round(angle*180/np.pi, 1)} degrees...")

        
        if wait_for_completion:
            await asyncio.sleep(ms*0.001)

        return

    async def stop_mov(self):
        """
        Stop the device movement.
        """
        if not dconfig.SIMULATION_MODE:
            print("Stopping movement...")
            await self._send_req(lambda: requests.post(self.api_url + "/stp"))

        return

    async def goto_arm(self, x=0, y=0):
        """
        Move the arm up.
        x (int): The x coordinate to move to.
        y (int): The y coordinate to move to.
        """
            
        if not dconfig.SIMULATION_MODE:
            if (x == 0 and y == 0):
                await self._send_req(lambda: requests.post(self.api_url + "/arm/goto", json={"x": 0, "y": 0, "angles": True}))
            else:
                await self._send_req(lambda: requests.post(self.api_url + "/arm/goto", json={"x": x, "y": y}))
        print("Moving arm to position...")

        return

    async def stop_arm(self):
        """
        Stop the arm movement.
        """
        
        if not dconfig.SIMULATION_MODE:
            await self._send_req(lambda: requests.post(self.api_url + "/arm/stp"))
        print("Stopping arm movement...")

        return

    async def goto_camera(self, alpha=0, beta=0):
        """
        Move the camera up.
        dist (int): The distance or duration to move. If positive, the camera moves for the given time.
        """
        
        if not dconfig.SIMULATION_MODE:
            await self._send_req(lambda: requests.post(self.api_url + "/cam/goto", json={"alpha": alpha, "beta": beta}))
        print("Moving camera to position...")
        
        return 

    async def stop_cam(self):
        """
        Stop the camera movement.
        """
        
        if not dconfig.SIMULATION_MODE:
            await self._send_req(lambda: requests.post(self.api_url + "/cam/stp")) 
        print("Stopping camera movement...")
        
        return

    # Camera control methods

    async def get_top_cam_angle(self):
        """
        Get the angle of the top camera.
        """
        data = await self._send_req(lambda: requests.get(self.api_url + "/cam/status"))
        return data
    
    def turn_on_tracker(self):
        """
        Start the object tracking. The camera will try to keep the object in the center of its view.
        """
        print("Start tracking the object...")
        # TODO: Implement the recentering logic
        
        def check_center():
            frame = self.capture_image()
            obj_coords = self.controller.segmenter.get_object_coords(frame)
            frame_center = frame.shape[:2]/2
            pos_diff = obj_coords - frame_center

            if(pos_diff[0] > 10):
                self.rotate_right()
            elif(pos_diff[0] < -10):
                self.rotate_left()
            else:
                self.stop_mov()
            
            if(pos_diff[1] > 10):
                self.down_camera()
            elif(pos_diff[1] < -10):
                self.up_camera()

    def capture_image(self, src='arm'):
        """
        Captures an image from the ESP32.
        
        Args:
            src (str): The source from which to capture the image. Default is 'arm'.
        Returns:
            cv2.typing.MatLike: The captured image in a format compatible with OpenCV.
        """
        if(dconfig.TEST_SEG_WITH_VID):
            return self.fake_current_frame
        elif src == 'arm':
            return self.top_cam_udp_receiver.get_current_frame()
        elif src == 'front':
            return self.front_cam_udp_receiver.get_current_frame()
        
        return None
     

            
