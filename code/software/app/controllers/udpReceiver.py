import socket
import cv2
import numpy as np
import time


# Define the IP address and port to listen on
UDP_IP = "0.0.0.0"  # Listen on all available interfaces
UDP_PORT = 12346     # Port used for receiving the stream

# Get the local IP address of the computer
def get_local_ip():
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
def send_ip_to_esp32(esp32_ip, esp32_port, computer_ip):
    # Create a TCP socket to send the IP address to the ESP32
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp_sock:
        tcp_sock.connect((esp32_ip, esp32_port))
        tcp_sock.send(f"IP:{computer_ip}\n".encode())  # Send IP in format "IP:192.168.x.x"
        print(f"Sent IP address {computer_ip} to ESP32")

computer_ip = get_local_ip()
esp32_ip = '192.168.1.100'  # Replace with ESP32's IP address
esp32_port = 12346

send_ip_to_esp32('172.21.71.73', esp32_port, computer_ip)


# Create a UDP socket
udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_sock.bind((UDP_IP, UDP_PORT))

print(f"Listening for UDP packets on {UDP_IP}:{UDP_PORT}...")

# Buffer for storing the received data
bytes_buffer = b''

while True:
    # Receive data from the ESP32-CAM
    data, addr = udp_sock.recvfrom(65536)  # Max buffer size for UDP is 64KB
    bytes_buffer += data  # Append the received data to the buffer

    # Look for the start and end markers for the JPEG image
    start_index = bytes_buffer.find(b'\xff\xd8')  # JPEG start marker
    end_index = bytes_buffer.find(b'\xff\xd9')    # JPEG end marker

    # If we have a complete JPEG image (both start and end markers)
    if start_index != -1 and end_index != -1:
        # Extract the JPEG frame
        jpg_frame = bytes_buffer[start_index:end_index + 2]
        bytes_buffer = bytes_buffer[end_index + 2:]  # Reset the buffer for the next frame

        # Convert the JPEG byte data to a NumPy array and decode it into an OpenCV image
        frame = cv2.imdecode(np.frombuffer(jpg_frame, np.uint8), cv2.IMREAD_COLOR)

        # Display the frame in a window
        if frame is not None:
            cv2.imshow("ESP32-CAM UDP Stream", frame)

        # Press 'q' to exit the loop
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

# Close the OpenCV window
cv2.destroyAllWindows()
