import requests 
import cv2
import os

from controllers.udp_receiver import UDPReceiver

DEFAULT_API_URL = "http://superscanner8000:80"
DEFAULT_TOP_CAM_URL = "http://superscanner8008:80"
DEFAULT_FRONT_CAM_URL = "http://superscanner8009:80"
TEST_CONNECTION_TIMEOUT = 3
DEFAULT_MOVING_TIME = 5000

class SS8:
    def  __init__(self, controller, disconnected_callback):
        """
        Initializes the SS8 class with default values.
        """
        self.controller = controller
        self.connection_lost_callback = disconnected_callback

        self.top_cam_udp_receiver = UDPReceiver(self.controller, 12346, "0.0.0.0")
        self.front_cam_udp_receiver = UDPReceiver(self.controller, 22222, "0.0.0.0")

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

        if False and not self.init_api_connection():
            return False
        
        # Test connection to the camera hostname and start receiving video stream
        if not self.init_udp_connection():
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
        self.top_cam_udp_receiver.start_listening(self.top_cam_url)
        #self.front_cam_udp_receiver.start_listening(self.front_cam_url)
        return True
    
    def _send_req(self, req_func, on_error=lambda: None, on_success=lambda: None):
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
                on_success()
            else:
                on_error()
        except requests.ConnectionError:
            self.connection_lost_callback()
        except Exception as e:
            print(f"An error occurred: {e}")
            self.connection_lost_callback()
    
    def capture_image(self, src='arm'):
        """
        Captures an image from the ESP32.
        
        Args:
            src (str): The source from which to capture the image. Default is 'arm'.
        Returns:
            cv2.typing.MatLike: The captured image in a format compatible with OpenCV.
        """
        if src == 'arm':
            return self.top_cam_udp_receiver.get_current_frame()
        elif src == 'front':
            return self.front_cam_udp_receiver.get_current_frame()
        else:
            return None

        if frame is not None:
            return frame
        else:
            print(f"No frame available from {src} camera.")
        return None
    def move_forward(self, dist=DEFAULT_MOVING_TIME):
        """
        Move the device forward.
        dist (int): The distance or duration to move. If positive, the device moves for the given time.
        """
        self._send_req(lambda: requests.post(self.api_url + "/fwd", json={"ms": dist}), on_success=lambda: print("Moving forward..."))

    def move_backward(self, dist=DEFAULT_MOVING_TIME):
        """
        Move the device backward.
        dist (int): The distance or duration to move. If positive, the device moves for the given time.
        """
        self._send_req(lambda: requests.post(self.api_url + "/bwd", json={"ms": dist}), on_success=lambda: print("Moving backward..."))

    def rotate_left(self, dist=DEFAULT_MOVING_TIME):
        """
        Rotate the device to the left.
        dist (int): The distance or duration to rotate. If positive, the device rotates for the given time. 
                    If negative, the device rotates until it stops.
        """
        self._send_req(lambda: requests.post(self.api_url + "/hlft", json={"ms": dist}), on_success=lambda: print("Rotating left..."))

    def rotate_right(self, dist=DEFAULT_MOVING_TIME):
        """
        Rotate the device to the right.
        dist (int): The distance or duration to rotate. If positive, the device rotates for the given time. 
                    If negative, the device rotates until it stops.
        
        """
        self._send_req(lambda: requests.post(self.api_url + "/hrgt", json={"ms": dist}), on_success=lambda: print("Rotating right..."))

    def stop_mov(self):
        """
        Stop the device movement.
        """
        self._send_req(lambda: requests.post(self.api_url + "/stp"), on_success=lambda: print("Stopping movement..."))

    def goto_arm(self, x=0, y=0):
        """
        Move the arm up.
        x (int): The x coordinate to move to.
        y (int): The y coordinate to move to.
        """
        self._send_req(lambda: requests.post(self.api_url + "/arm/goto", json={"x": x, "y": y}), on_success=lambda: print("Moving arm to position..."))

    def stop_arm(self):
        """
        Stop the arm movement.
        """
        self._send_req(lambda: requests.post(self.api_url + "/arm/stp"), on_success=lambda: print("Stopping arm movement..."))

    def goto_camera(self, alpha=0, beta=0):
        """
        Move the camera up.
        dist (int): The distance or duration to move. If positive, the camera moves for the given time.
        """
        self._send_req(lambda: requests.post(self.api_url + "/cam/goto", json={"alpha": alpha, "beta": beta}), on_success=lambda: print("Moving camera to position..."))

    def stop_cam(self):
        """
        Stop the camera movement.
        """
        self._send_req(lambda: requests.post(self.api_url + "/cam/stp"), on_success=lambda: print("Stopping camera movement...")) 

        
    def recenter_cam(self):
        """
        Recenter the camera to have the object to be scanned in the center of the frame.
        """
        print("Recentering camera...")
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
            
