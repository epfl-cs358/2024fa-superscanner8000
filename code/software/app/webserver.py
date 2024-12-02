import cv2
import requests
import numpy as np
import wifi

class ESP32CAM:
    def __init__(self, url, verbose=True):
        self.verbose = verbose
        if self.verbose:
            print("Connecting to ESP32-CAM stream...")
        self.url = url
        self.response = requests.get(url, stream=True)
        while self.response.status_code != 200:
            self.response = requests.get(url, stream=True)
            print("Error: Could not connect to ESP32-CAM.")

        self.bytes_buffer = b''

    def get_frame(self):
        try: 
            # Assert connection
            if self.response.status_code != 200:
                print("Error: Could not connect to ESP32-CAM.")
                exit()

            for chunk in self.response.iter_content(chunk_size=1024):
                # Append the chunk to the bytes buffer
                self.bytes_buffer += chunk

                # Look for the JPEG frame start and end
                start_index = self.bytes_buffer.find(b'\xff\xd8')  # JPEG start
                end_index = self.bytes_buffer.find(b'\xff\xd9')    # JPEG end

                if start_index != -1 and end_index != -1:
                    # Extract the JPEG frame
                    jpg_frame = self.bytes_buffer[start_index:end_index + 2]
                    self.bytes_buffer = self.bytes_buffer[end_index + 2:]

                    # Convert the JPEG frame to a NumPy array and decode it as an OpenCV image
                    frame = cv2.imdecode(np.frombuffer(jpg_frame, np.uint8), cv2.IMREAD_COLOR)
                    # Convert to RGB
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                    return frame
        
        except requests.exceptions.ConnectionError:
            print("Connection lost, retrying...")
            time.sleep(2)
        except Exception as e:
            print(f"Unexpected error: {e}")
            time.sleep(2)

class WIFI_CONTROLLER:
    def __init__(self):
        pass

    def get_available_wifi(self):
        wifi_scanner = wifi.Cell.all('wlan0')
        available_networks = [cell.ssid for cell in wifi_scanner]
        print(available_networks)
        return available_networks
        
if __name__ == "__main__":
    esp32cam = ESP32CAM("http://172.20.10.8:80/stream")

    while True:
        frame = esp32cam.get_frame()

        if frame is None or frame.size == 0:
            print("Received an invalid frame, retrying...")
            continue

        # Display the frame
        cv2.imshow("ESP32-CAM Stream", frame)

        # Press 'q' to exit the loop
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cv2.destroyAllWindows()

