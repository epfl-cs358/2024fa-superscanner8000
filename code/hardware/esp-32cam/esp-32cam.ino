
#include "esp_camera.h"
#include <WiFi.h>
#include <WiFiUdp.h>




const char* ssid = "SPOT-iot";
const char* password = "";
const char* udpAddress = "";  // Computer that wants to receive IP's
const int udpPort = 12345;  

WiFiUDP udp;  // Create a UDP object for sending data

void setup() {
  Serial.begin(115200);
  
  // Connect to Wi-Fi
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println(Wifi connected!");

     // Print the IP address of the ESP32
  Serial.print("ESP32 Camera ready! Connect to http://");
  Serial.println(WiFi.localIP());

  camera_config_t config = {
 .pin_pwdn = 32,
    .pin_reset = -1,
    .pin_xclk = 0,
    .pin_sscb_sda = 26,
    .pin_sscb_scl = 27,
    .pin_d7 = 35,
    .pin_d6 = 34,
    .pin_d5 = 39,
    .pin_d4 = 36,
    .pin_d3 = 21,
    .pin_d2 = 19,
    .pin_d1 = 18,
    .pin_d0 = 5,
    .pin_vsync = 25,
    .pin_href = 23,
    .pin_pclk = 22,

    .xclk_freq_hz = 20000000,
    .ledc_timer = LEDC_TIMER_0,
    .ledc_channel = LEDC_CHANNEL_0,
    .pixel_format = PIXFORMAT_JPEG,
    .frame_size = FRAMESIZE_QVGA,  
    .jpeg_quality = 12,
    .fb_count = 2,                  
}
  esp_camera_init(&config);


void loop() {
  // Capture an image from the camera
  camera_fb_t *fb = esp_camera_fb_get();
  if (!fb) {
    Serial.println("Failed to capture image");
    return;
  }

// Send the captured image over UDP
  udp.beginPacket(udpAddress, udpPort);
  udp.write(fb->buf, fb->len);  // Send the frame data
  udp.endPacket();

 Serial.println("Image sent via UDP");

  esp_camera_fb_return(fb);  // freeing up memory

  delay(3000);  // Delay between captures 3s ? need to be calculated or
}
