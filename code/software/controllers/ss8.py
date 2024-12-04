import requests 
import cv2

DEFAULT_URL = "http://superscanner8000:80"
TEST_CONNECTION_TIMEOUT = 3

class SS8:
    def  __init__(self, disconnected_callback):
        """
        Initializes the SS8 class with default values.
        """
        self.url = DEFAULT_URL
        self.connection_lost_callback = disconnected_callback

    def get_default_url(self):
        """
        Returns the default hostname of the device.

        Returns:
            str: The default hostname.
        """
        return "http://superscanner8000:80"
    
    def connect(self, url=DEFAULT_URL) -> bool:
        """
        Test connection to the given hostname.

        Args:
            hostname (str): The hostname to connect to.
            timeout (int): The timeout for the connection in seconds.

        Returns:
            bool: True if the connection is successful.
        """

        self.url = url
        try:
            res = requests.get(url+"/status", timeout=TEST_CONNECTION_TIMEOUT)
            if res.status_code == 200:
                print("Connection successful! Server is reachable.")
                return True
            else:
                print(f"Server responded with status code: {res.status_code}")
        except requests.ConnectionError:
            print("Connection failed. Server is unreachable.")
        except requests.Timeout:
            print("Connection timed out.")
        except Exception as e:
            print(f"An error occurred: {e}")

        return False
    
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
            print(res)
            if res.status_code == 200:
                on_success()
            else:
                on_error()
        except requests.ConnectionError:
            self.connection_lost_callback()
        except Exception as e:
            print(f"An error occurred: {e}")
            self.connection_lost_callback()
    
    def capture_image(self, src='arm') -> cv2.typing.MatLike:
        """
        Captures an image from the ESP32.
        
        Args:
            src (str): The source from which to capture the image. Default is 'arm'.
        Returns:
            cv2.typing.MatLike: The captured image in a format compatible with OpenCV.
        """
        #response = requests.get(self.ip_adress+"/capture")
        #print(response.json)

        pass

    def move_forward(self, dist=-1):
        """
        Move the device forward.
        dist (int): The distance or duration to move. If positive, the device moves for the given time.
        """
        self._send_req(lambda: requests.post(self.url + "/fwd", json={"ms": dist}), on_success=lambda: print("Moving forward..."))

        pass

    def move_backward(self, dist=-1):
        """
        Move the device backward.
        dist (int): The distance or duration to move. If positive, the device moves for the given time.
        """
        self._send_req(lambda: requests.post(self.url + "/bwd", json={"ms": dist}), on_success=lambda: print("Moving backward..."))

        pass

    def rotate_left(self, dist=-1):
        """
        Rotate the device to the left.
        dist (int): The distance or duration to rotate. If positive, the device rotates for the given time. 
                    If negative, the device rotates until it stops.
        """
        self._send_req(lambda: requests.post(self.url + "/hlft", json={"ms": dist}), on_success=lambda: print("Rotating left..."))

        pass

    def rotate_right(self, dist=-1):
        """
        Rotate the device to the right.
        dist (int): The distance or duration to rotate. If positive, the device rotates for the given time. 
                    If negative, the device rotates until it stops.
        
        """
        self._send_req(lambda: requests.post(self.url + "/hrgt", json={"ms": dist}), on_success=lambda: print("Rotating right..."))

        pass

    def stop_mov(self):
        """
        Stop the device movement.
        """
        self._send_req(lambda: requests.post(self.url + "/stp"), on_success=lambda: print("Stopping movement..."))
        pass

    def up_camera(self, dist=-1):
        """
        Move the camera up.
        dist (int): The distance or duration to move. If positive, the camera moves for the given time.
        """
        print("Moving camera up...")
        pass

    def down_camera(self, dist=-1):
        """
        Move the camera down.
        dist (int): The distance or duration to move. If positive, the camera moves for the given time.
        """
        print("Moving camera down...")
        pass

    def stop_cam(self):
        """
        Stop the camera movement.
        """
        print("Stopping camera movement...")
        pass
    
