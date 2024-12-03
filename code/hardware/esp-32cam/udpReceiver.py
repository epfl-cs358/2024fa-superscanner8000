import socket
import cv2
import numpy as np

# Define the IP address and port to listen on
UDP_IP = "0.0.0.0"  # Listen on all available interfaces
UDP_PORT = 12345     # Port used for receiving the stream

# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

print(f"Listening for UDP packets on {UDP_IP}:{UDP_PORT}...")

# Buffer for storing the received data
bytes_buffer = b''

while True:
    # Receive data from the ESP32-CAM
    data, addr = sock.recvfrom(65536)  # Max buffer size for UDP is 64KB
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
