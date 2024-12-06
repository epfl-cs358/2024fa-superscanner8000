import socket
import cv2
import numpy as np
import time

# Define the IP address and port to listen on
DEFAULT_UDP_IP = "0.0.0.0"  # Listen on all available interfaces
DEFAULT_UDP_PORT = 12346     # Port used for receiving the stream

class UDPReceiver:
    def __init__(self, controller, udp_port=DEFAULT_UDP_PORT, udp_ip=DEFAULT_UDP_IP):
        self.controller = controller
        self.udp_port = udp_port
        self.udp_ip = udp_ip

        # Get the local IP address of the computer
        self.computer_ip = self._get_local_ip()

        # Buffer for storing the received data
        self.bytes_buffer = b''

    # Get the local IP address of the computer
    def _get_local_ip(self):
        # This uses the default gateway to get the local machine's IP
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

    # Function to send the computer IP to the ESP32 via TCP
    def _send_ip_to_esp32(self, esp32_cam_url):
        #TODO: Implement this function with esp32_cam_url

        # Create a TCP socket to send the IP address to the ESP32
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp_sock:
            tcp_sock.connect((esp32_ip, esp32_port))
            tcp_sock.send(f"IP:{self.computer_ip}\n".encode())  # Send IP in format "IP:192.168.x.x"
            print(f"Sent IP address {self.computer_ip} to ESP32")

    def start_listening(self, esp32_cam_url):
        self._send_ip_to_esp32(esp32_cam_url)

        # Create a UDP socket
        udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp_sock.bind((self.udp_ip, self.udp_port))

        print(f"Listening for UDP packets on {self.udp_ip}:{self.udp_port}...")

        def process_udp_stream():
            # Receive data from the ESP32-CAM
            data, _ = udp_sock.recvfrom(65536)  # Max buffer size for UDP is 64KB
            self.bytes_buffer += data  # Append the received data to the buffer

            # Look for the start and end markers for the JPEG image
            start_index = self.bytes_buffer.find(b'\xff\xd8')  # JPEG start marker
            end_index = self.bytes_buffer.find(b'\xff\xd9')    # JPEG end marker

            # If we have a complete JPEG image (both start and end markers)
            if start_index != -1 and end_index != -1:
                # Extract the JPEG frame
                jpg_frame = self.bytes_buffer[start_index:end_index + 2]
                self.bytes_buffer = self.bytes_buffer[end_index + 2:]  # Reset the buffer for the next frame

                # Convert the JPEG byte data to a NumPy array and decode it into an OpenCV image
                frame = cv2.imdecode(np.frombuffer(jpg_frame, np.uint8), cv2.IMREAD_COLOR)

                # Display the frame in a window
                if frame is not None:
                    self.current_frame = frame
                # Press 'q' to exit the loop
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    return
        
        process_udp_stream()
        # Close the OpenCV window

    def get_current_frame(self):
        return self.current_frame