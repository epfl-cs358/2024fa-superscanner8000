import socket
import cv2
import numpy as np
import threading

DEFAULT_UDP_IP = "0.0.0.0"  # Listen on all available interfaces
DEFAULT_UDP_PORT = 12346    # Port used for receiving the stream


class UDPReceiver:
    def __init__(self, controller, udp_port=DEFAULT_UDP_PORT, udp_ip=DEFAULT_UDP_IP):
        self.controller = controller
        self.udp_port = udp_port
        self.udp_ip = udp_ip
        self.udp_sock = None
        self.current_frame = None
        self.bytes_buffer = b''
        self.running = False
        self.lock = threading.Lock()  # Lock to ensure thread-safe access to current_frame

    def start_listening(self, esp32_cam_url):
        """
        Sets up the UDP socket and starts the background thread for frame fetching.
        """
        print(f"Starting to listen on UDP {self.udp_ip}:{self.udp_port}...")
        self.udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_sock.bind((self.udp_ip, self.udp_port))
        self.running = True

        # Start a background thread for continuous frame fetching
        threading.Thread(target=self._fetch_frames, daemon=True).start()
        print(f"Listening for UDP packets on {self.udp_ip}:{self.udp_port}...")

    def _fetch_frames(self):
        """
        Background thread function to continuously fetch and decode frames.
        """
        while self.running:
            try:
                # Receive data from the UDP socket
                data, _ = self.udp_sock.recvfrom(65536)  # Max buffer size
                self.bytes_buffer += data

                # Look for the start and end markers for a JPEG image
                start_index = self.bytes_buffer.find(b'\xff\xd8')  # Start of JPEG
                end_index = self.bytes_buffer.find(b'\xff\xd9')    # End of JPEG

                if start_index != -1 and end_index != -1:
                    # Extract the JPEG frame
                    jpg_frame = self.bytes_buffer[start_index:end_index + 2]
                    self.bytes_buffer = self.bytes_buffer[end_index + 2:]  # Clear processed data

                    # Decode the JPEG frame into an OpenCV image
                    frame = cv2.imdecode(np.frombuffer(jpg_frame, np.uint8), cv2.IMREAD_COLOR)

                    if frame is not None:
                        with self.lock:
                            self.current_frame = frame  # Update the latest frame
                        print("Frame received and updated.")
            except Exception as e:
                print(f"Error while fetching frames: {e}")

    def get_current_frame(self):
        """
        Returns the most recently fetched frame immediately.
        """
        with self.lock:
            if self.current_frame is not None:
                cv2.waitKey(1)
                return self.current_frame
            else:
                print("No frame available.")
                return None

    def stop(self):
        """
        Stops the background frame fetching and closes the UDP socket.
        """
        self.running = False
        if self.udp_sock:
            self.udp_sock.close()
        print("Stopped frame fetching.")
