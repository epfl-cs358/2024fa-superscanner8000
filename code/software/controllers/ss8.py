import requests 
import time
import cv2
import os
import numpy as np
from scipy.spatial.transform import Rotation as Rot
import scipy.optimize as opt

import config.dev_config as dconfig

from controllers.udp_receiver import UDPReceiver

# SS8 connection constants
DEFAULT_API_URL = "http://superscanner8000:80"
DEFAULT_TOP_CAM_URL = "http://superscanner8008:80"
DEFAULT_FRONT_CAM_URL = "http://superscanner8009:80"
TEST_CONNECTION_TIMEOUT = 3

# SS8 movement constants
DEFAULT_MOVING_DIST = 1000
DEFAULT_ROTATING_ANGLE = 2*np.pi
BODY_ANGLE_TO_TIME = 510 # Time to rotate the body by 1 radian            TODO: Update this value
BODY_DIST_TO_TIME = 28 # Time to move the body by 1 cm                   TODO: Update this value
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

        self.top_cam_angles = np.array([0,0])
        self.is_aligning = False

        self.top_cam_udp_receiver = UDPReceiver(12346, "0.0.0.0")
        self.front_cam_udp_receiver = UDPReceiver(12349, "0.0.0.0")

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
        
        self.stop_cam()
        return True

    def init_udp_connection(self) -> bool:
        if dconfig.CONNECT_TO_TOP_CAM :
            try:
                self.top_cam_udp_receiver.start_listening(self.top_cam_url)
                print("Connected to top cam")
            except Exception as e:
                print(f"An error occurred for the top cam: {e}")
                return False
        
        if dconfig.CONNECT_TO_FRONT_CAM:
            try:
                self.front_cam_udp_receiver.start_listening(self.front_cam_url)
                print("Connected to front cam")
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

    def _send_req(self, req_func, on_error=lambda: None):
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
            print(f"An error occurred when sending req : {e}")
            self.connection_lost_callback()
    
    def move_forward(self, dist=DEFAULT_MOVING_DIST, wait_for_completion=True):
        """
        Move the device forward.
        dist (int): The distance or duration to move. If positive, the device moves for the given time.
        """
        ms = dist*BODY_DIST_TO_TIME

        if dconfig.CAN_MOVE:
            self._send_req(lambda: requests.post(self.api_url + "/fwd", json={"ms": ms}))
        
        if dconfig.DEBUG_SS8:
            print(f"Moving forward of {dist} cm")
        
        if wait_for_completion:
            time.sleep(ms*0.001)
        return

    def move_backward(self, dist=DEFAULT_MOVING_DIST, wait_for_completion=True):
        """
        Move the device backward.
        dist (int): The distance or duration to move. If positive, the device moves for the given time.
        """
        ms=dist*BODY_DIST_TO_TIME

        if dconfig.CAN_MOVE:
            self._send_req(lambda: requests.post(self.api_url + "/bwd", json={"ms": ms}))
        
        
        if dconfig.DEBUG_SS8:
            print(f"Moving backward of {dist} cm")

        if wait_for_completion:
            time.sleep(ms*0.001)

        return
        
    def rotate_left(self, angle=DEFAULT_ROTATING_ANGLE, wait_for_completion=True):
        """
        Rotate the device to the left.
        angle (int): The angleance or duration to rotate. If positive, the device rotates for the given time. 
                    If negative, the device rotates until it stops.
        """
        ms=angle*BODY_ANGLE_TO_TIME

        if(angle < 0.000001):
            return

        if dconfig.CAN_MOVE:
            self._send_req(lambda: requests.post(self.api_url + "/lft", json={"ms": angle*BODY_ANGLE_TO_TIME}))
        
        if dconfig.DEBUG_SS8:
            print(f"Rotating left of {round(angle*180/np.pi)} degrees")

        if wait_for_completion:
            time.sleep(ms*0.001)

        return
        
    def rotate_right(self, angle=DEFAULT_ROTATING_ANGLE, wait_for_completion=True):
        """
        Rotate the device to the right.
        angle (int): The angleance or duration to rotate. If positive, the device rotates for the given time. 
                    If negative, the device rotates until it stops.
        
        """
        ms=angle*BODY_ANGLE_TO_TIME

        if(angle < 0.000001):
            return

        if dconfig.CAN_MOVE:
            self._send_req(lambda: requests.post(self.api_url + "/rgt", json={"ms": angle*BODY_ANGLE_TO_TIME}))
        
        if dconfig.DEBUG_SS8:
            print(f"Rotating right of {round(angle*180/np.pi, 1)} degrees")

        if wait_for_completion:
            time.sleep(ms*0.001)

        self.display_text("Connected")
        self.set_led(0, dconfig.LED_BRIGHTNESS, dconfig.LED_BRIGHTNESS)

        return

    def stop_mov(self):
        """
        Stop the device movement.
        """
        if dconfig.CONNECT_TO_MOV_API:
            self._send_req(lambda: requests.post(self.api_url + "/stp"))

        if dconfig.DEBUG_SS8:
            print("Stopping movement")

        return

    def goto_arm(self, x=0, y=0):
        """
        Move the arm up.
        x (int): The x coordinate to move to.
        y (int): The y coordinate to move to.
        """
            
        if dconfig.CONNECT_TO_MOV_API:
            if (x == 0 and y == 0):
                self._send_req(lambda: requests.post(self.api_url + "/arm/goto", json={"x": 0, "y": 0, "angles": True}))
            else:
                self._send_req(lambda: requests.post(self.api_url + "/arm/goto", json={"x": x, "y": y}))
        
        if dconfig.DEBUG_SS8:
            print(f"Moving arm to position {x},{y}")

        return

    def stop_arm(self):
        """
        Stop the arm movement.
        """
        
        if dconfig.CONNECT_TO_MOV_API:
            self._send_req(lambda: requests.post(self.api_url + "/arm/stp"))

        if dconfig.DEBUG_SS8:
            print("Stopping arm movement")

        return
        
    def _get_reverse_kin_angle(self, x_angle, y_angle):
        # Given final rotation matrix
        R_final = Rot.from_euler('xyz', [x_angle, 0, y_angle], degrees=True).as_matrix()

        # Fixed angle alpha: defines the axis of R1 on the XY plane
        gamma = np.radians(self.top_cam_angles[1])
        u1 = np.array([np.cos(gamma), np.sin(gamma), 0])  # Rotation axis for R1
        print(u1)
        # Function to compute the error between R_final and R2 @ R1
        def error_function(params):
            alpha, beta = params  # Rotation angles for R1 and R2

            # R1: Rotation around custom axis u1
            R1 = Rot.from_rotvec(alpha * u1).as_matrix()
            
            # R2: Rotation around Z-axis
            R2 = Rot.from_euler('z', beta).as_matrix()

            # Combined rotation
            R_combined = R2 @ R1

            # Compute error as Frobenius norm
            error = np.linalg.norm(R_final - R_combined, ord='fro')

            print(f'RC :\n{np.round(R_combined, 3)}')
            return error

        initial_guess = [0.1, 0.1]

        result = opt.minimize(error_function, initial_guess, method='Nelder-Mead')
        opt_alpha, opt_beta = result.x % (2*np.pi)

        print(f'RF :\n{np.round(R_final, 3)}')

        return np.array([opt_alpha, opt_beta])
    
    def goto_cam(self, x_angle, y_angle, relative=False):
        """
        Move the camera up.
        x_angle (int): The angle to move to from the first motor. Positive -> right
        y_angle (int): The angle to move to from the second motor. Positive -> up
        relative (boolean):_ If the given angle is relative or absolute
        """

        angles = np.array([x_angle, y_angle])

        if(relative):
            if(x_angle==0 or True):
                angles = angles + self.top_cam_angles
            else:
                angles = np.degrees(self._get_reverse_kin_angle(x_angle, y_angle)) + self.top_cam_angles

        [alpha, beta] =  (angles + 180) % 360 -180
            


        if dconfig.DEBUG_SS8:
            print(f"Moving camera to position {int(alpha)}, {int(beta)}")
        
        if dconfig.CONNECT_TO_MOV_API:
            self._send_req(lambda: requests.post(self.api_url + "/cam/goto", json={"alpha": int(alpha), "beta": int(beta)}))
        
        self.top_cam_angles = np.array([alpha, beta])
        return 

    def stop_cam(self):
        """
        Stop the camera movement.
        """
        
        if dconfig.CONNECT_TO_MOV_API:
            data = self._send_req(lambda: requests.post(self.api_url + "/cam/stp"))
            self.top_cam_angles = np.array([data['alpha'], data['beta']])
        if dconfig.DEBUG_SS8:
            print("Stopped  camera movement at ", np.round(self.top_cam_angles))
        
        return
    
    def display_text(self, text):
        """
        Display text on the device screen.
        text (str): The text to display.
        """
        if dconfig.CONNECT_TO_MOV_API:
            requests.post(self.api_url + "/text", json={"text": text})
        
        if(dconfig.DEBUG_SS8):
            print(f"Displaying text: {text}")

        return
    
    def display_progress_bar(self, text, progress):
        """
        Display text on the device screen.
        text (str): The text to display.
        """
        if dconfig.CONNECT_TO_MOV_API:
            requests.post(self.api_url + "/progress", json={"text": text, "progress": progress})
        
        if(dconfig.DEBUG_SS8):
            print(f"Displaying text: {text}")
            print(f"Displaying progress: {progress}")

        return
    
    def display_text_2lines(self, line1, line2):
        """
        Display text on two lines on the device screen.
        line1 (str): The text to display on the first line.
        line2 (str): The text to display on the second line.
        """
        if dconfig.CONNECT_TO_MOV_API:
            requests.post(self.api_url + "/scroll", json={"text1": line1, "text2": line2})
        
        if(dconfig.DEBUG_SS8):
            print(f"Displaying text: {line1}, {line2}")

        return
    
    # Leds control methods

    def set_led(self, r, g, b):
        """
        Set the color of the LED.
        r (int): The red value. range [0, 255]
        g (int): The green value. range [0, 255]
        b (int): The blue value. range [0, 255]
        """
        if dconfig.CONNECT_TO_MOV_API:
            requests.post(self.api_url + "/led/set", json={"r": r, "g": g, "b": b})
        
        if(dconfig.DEBUG_SS8):
            print(f"Set LED color to {r}, {g}, {b}")

        return
    
    def set_led_rainbow(self):
        """
        Set the LED to rainbow mode.
        """
        if dconfig.CONNECT_TO_MOV_API:
            requests.post(self.api_url + "/led/rainbow", json={"rainbow": True})
        
        if(dconfig.DEBUG_SS8):
            print("Set LED to rainbow mode")

        return
    
    def flash_led(self, r, g, b, duration):
        """
        Flash the LED with a given color.
        r (int): The red value. range [0, 255]
        g (int): The green value. range [0, 255]
        b (int): The blue value. range [0, 255]
        duration (int): The duration of the flash in milliseconds.
        """
        if dconfig.CONNECT_TO_MOV_API:
            requests.post(self.api_url + "/led/flash", json={"r": r, "g": g, "b": b, "duration": duration})
        if dconfig.DEBUG_SS8:
            print(f"Flashing LED with color {r}, {g}, {b} for {duration} ms")
    
    # Camera control methods

    def get_top_cam_angle(self):
        """
        Get the angle of the top camera.
        """
        return self.top_cam_angles
    
    def align_to(self, mode='pos', wait_for_completion=True, keep_arm_cam_settings=False):
        """
        Start the object tracking. The camera will try to keep the object in the center of its view.
        """
        def get_diff():
            frame = self.capture_image()
            obj_coords = self.controller.segmenter.get_object_coords(frame, False)
            if obj_coords is None:
                return np.array([0, 0])
            [height, width] = frame.shape[:2]
            return (obj_coords - np.array([width, height])/2)/3

        def update_cam_angle(): 
            init_diff = get_diff()
            if(dconfig.DEBUG_NAV):
                print('Align cam angle to obj')
            if(init_diff[0] > center_threshold):
                self.stop_cam()
                self.goto_cam(0, np.sqrt(np.abs(init_diff[0])), relative=True)
            elif(init_diff[0] < -center_threshold):
                self.stop_cam()
                self.goto_cam(0, -np.sqrt(np.abs(init_diff[0])), relative=True)
            elif(wait_for_completion):
                if(dconfig.DEBUG_NAV):
                    print(f'Alignment finished with angle : {self.top_cam_angles[1]}')
                
                self.is_aligning=False
                return self.top_cam_angles[1]
        
        def update_body_angle(): 
            init_diff = get_diff()
            alpha = self.top_cam_angles[0]

            print(np.abs(alpha), np.abs(alpha+90))
            if(np.abs(alpha) < np.abs(alpha-90)):
                print('x axis')
                diff_axis = 0
            else :
                print('y axis')
                diff_axis=1

            diff_angle = np.sqrt((np.abs(init_diff[diff_axis]))*np.pi/1000)
            if(dconfig.DEBUG_NAV):
                print('Align body angle to obj')
            if(init_diff[diff_axis] > center_threshold):
                self.stop_mov()
                if(diff_axis==0):
                    self.rotate_left(diff_angle)
                else:
                    self.rotate_right(diff_angle)
            elif(init_diff[diff_axis] < -center_threshold):
                self.stop_mov()
                if(diff_axis==0):
                    self.rotate_right(diff_angle)
                else:
                    self.rotate_left(diff_angle)
            else:
                self.is_aligning=False
                return self.top_cam_angles[1]
        
        def update_pos_alignment():
            init_diff = get_diff()
            if(dconfig.DEBUG_SS8):
                print('Align body position to obj')
            if(init_diff[0] > center_threshold):
                self.stop_mov()
                self.move_backward(dist=np.sqrt(np.abs(init_diff[0]))*dconfig.ALIGNMENT_SPEED, wait_for_completion=False)
            elif(init_diff[0] < -center_threshold):
                self.stop_mov()
                self.move_forward(dist=np.sqrt(np.abs(init_diff[0]))*dconfig.ALIGNMENT_SPEED, wait_for_completion=False)
            else:
                self.is_aligning=False
                return self.top_cam_angles[1]
            
        center_threshold = dconfig.CENTER_THRESHOLD

        if not keep_arm_cam_settings:
            self.goto_arm(0, 0)
            self.goto_cam(0, 90)

        if dconfig.DEBUG_NAV:
            print("Start tracking the object")

        self.is_aligning = True
        res = None

        def update_align_to():
            if mode=='pos':
                return update_pos_alignment()
            elif mode =='body':
                return update_body_angle()
            else:
                return update_cam_angle()

        if(wait_for_completion):
            while self.is_aligning:
                res = update_align_to()
                time.sleep(dconfig.ALIGNMENT_WAIT)

        else:
            def loop():
                update_align_to()
                if self.is_aligning:
                    self.controller.after(dconfig.ALIGNMENT_WAIT*1000, loop)

            loop()


        if(dconfig.DEBUG_NAV and res is not None and False):
            print(f'Aligned with angle {res}')
        
        return res
        
    def stop_align_to(self):
        self.is_aligning = False
        
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
