import socket
import cv2
import numpy as np
import threading
from urllib.parse import urlparse
import tempfile
import os

from config.dev_config import DEBUG_CAM


DEFAULT_UDP_IP = "0.0.0.0"  # Listen on all available interfaces
DEFAULT_UDP_PORT = 12346    # Port used for receiving the stream
DEFAULT_UDP_PORT = 12349   # Port used for receiving the stream


class UDPReceiver:
    def __init__(self, udp_port=DEFAULT_UDP_PORT, udp_ip=DEFAULT_UDP_IP):
        self.udp_port = udp_port
        self.udp_ip = udp_ip
        self.udp_sock = None
        self.current_frame = None
        self.bytes_buffer = b''
        self.computer_ip = self._get_local_ip()
        self.running = False
        self.lock = threading.Lock()  # Lock to ensure thread-safe access to current_frame
        self.frame_counter = 0
    def _get_local_ip(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(0)
        try:
            s.connect(('10.254.254.254', 1))  # Just connect to any IP
            ip_address = s.getsockname()[0]
        except Exception:
            ip_address = '127.0.0.1'  # Fallback if no network connection
        finally:
            s.close()
        return ip_address
    
    def get_ip_of_hostname(self, hostname):
        try:
            # Get the IP address of the given hostname
            ip_address = socket.gethostbyname(hostname)
            return ip_address
        except socket.gaierror as e:
            return f"Error: {e}"
    

    def _send_ip_to_esp32(self, esp32_ip, esp32_port):
        # Create a TCP socket to send the IP address to the ESP32
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp_sock:
            tcp_sock.connect((esp32_ip, esp32_port))
            tcp_sock.send(f"IP:{self.computer_ip}\n".encode())  # Send IP in format "IP:192.168.x.x"
            if DEBUG_CAM:
                print(f"Sent IP address {self.computer_ip} to ESP32")
                
    def start_listening(self, esp32_cam_url):
        if DEBUG_CAM:
            print(esp32_cam_url)
        parsed_url = urlparse(esp32_cam_url)

        hostname = parsed_url.hostname
        esp32_port = parsed_url.port
        if DEBUG_CAM:
            print(f"ESP32 hostname: {hostname}")
            print(f"ESP32 port: {esp32_port}")

        # Resolve ESP32 hostname
        try:
            esp32_ip = self.get_ip_of_hostname(hostname)
            if DEBUG_CAM:
                print(f"ESP32 resolved to IP: {esp32_ip}")
        except Exception as e:
            if DEBUG_CAM:
                print(f"Error resolving ESP32 hostname: {e}")
            exit(1)

        self._send_ip_to_esp32(esp32_ip, esp32_port)
        self.udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_sock.bind((self.udp_ip, self.udp_port))
        self.running = True

        # Start a background thread for continuous frame fetching
        threading.Thread(target=self._fetch_frames, daemon=True).start()
        if DEBUG_CAM:
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
                        
                        if DEBUG_CAM:
                            print("Frame received and updated.")
            except Exception as e:
                if DEBUG_CAM:
                    print(f"Error while fetching frames: {e}")
                pass

    def get_current_frame(self):
        """
        Returns the most recently fetched frame immediately.
        """
        if self.current_frame is not None:
            return self.current_frame
        else:
            if DEBUG_CAM:
                print("No frame available.")
            return None

    def save_frame(self):  # Save the current frame to a file
        """
        Save the given frame to a temporary folder with a unique filename.
        """

        if self.current_frame is not None:
            # Get the system's temporary directory
            temp_dir = tempfile.gettempdir()
            # Construct the full path for the file with a numbered filename
            filename = f"frame_{self.frame_counter}.jpg"
            temp_file_path = os.path.join(temp_dir, filename)
            # Save theself.current_frame to the temporary folder
            cv2.imwrite(temp_file_path, self.current_frame)
            if DEBUG_CAM:
                print(f"Savedself.current_frame {self.frame_counter} to {temp_file_path}")
            # Increment theself.current_frame counter
            self.frame_counter += 1
        else:
            if DEBUG_CAM:
                print("No frame available to save.")

    def stop(self):
        """
        Stops the background frame fetching and closes the UDP socket.
        """
        self.running = False
        if self.udp_sock:
            self.udp_sock.close()
        if DEBUG_CAM:
            print("Stopped frame fetching.")


if __name__ == "__main__":
    DEFAULT_TOP_CAM_URL = "http://superscanner8008:80"
    DEFAULT_FRONT_CAM_URL = "http://superscanner8009:80"
    top_cam_udp_receiver = UDPReceiver(12346, "0.0.0.0")
    #front_cam_udp_receiver = UDPReceiver(12349, "0.0.0.0")
    top_cam_udp_receiver.start_listening(DEFAULT_TOP_CAM_URL)
    #ront_cam_udp_receiver.start_listening(DEFAULT_FRONT_CAM_URL)
    ContVid = True
    def update_frame():
        #cv2.namedWindow('front', cv2.WINDOW_NORMAL)
        cv2.namedWindow('top', cv2.WINDOW_NORMAL)
        while ContVid :
            #if front_cam_udp_receiver.current_frame is not None :

                #cv2.imshow('front', front_cam_udp_receiver.current_frame)
            if top_cam_udp_receiver.current_frame is not None :
                cv2.imshow('top', top_cam_udp_receiver.current_frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):  # Allow exit with 'q' key
                break
        threading.Timer(0. ,update_frame).start()

    thread = threading.Thread(target=update_frame)
    thread.start()
    top_cam_udp_receiver.save_frame()



    

"""
    cv2.imshow('top', top_cam_udp_receiver.current_frame)
"""