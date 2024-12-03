import requests 
import cv2

DEFAULT_HOSTNAME = "http://superscanner8000:80"
TEST_CONNECTION_TIMEOUT = 3

class SS8:
    def  __init__(self):
        """
        Initializes the SS8 class with default values.
        """
        self.device_hostname = DEFAULT_HOSTNAME

    def get_default_hostname(self):
        """
        Returns the default hostname of the device.

        Returns:
            str: The default hostname.
        """
        return "http://superscanner8000:80"
    
    def connect(self, hostname=DEFAULT_HOSTNAME) -> bool:
        """
        Test connection to the given hostname.

        Args:
            hostname (str): The hostname to connect to.
            timeout (int): The timeout for the connection in seconds.

        Returns:
            bool: True if the connection is successful.
        """

        try:
            res = requests.get(hostname+"/", timeout=TEST_CONNECTION_TIMEOUT)
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

        return True
        return False
    
    def capture_image(self) -> cv2.typing.MatLike:
        """
        Captures an image from the connected device.

        Returns:
            cv2.typing.MatLike
        """
        #response = requests.get(self.ip_adress+"/capture")
        #print(response.json)

        pass
