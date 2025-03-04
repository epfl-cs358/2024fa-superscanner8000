#include "esp_camera.h"
#include <WiFi.h>
#include <WebServer.h>
#include <WiFiClient.h>
#include <ESPmDNS.h>


// Camera configuration for the AI Thinker model
#define PWDN_GPIO_NUM     32
#define RESET_GPIO_NUM    -1
#define XCLK_GPIO_NUM      0
#define SIOD_GPIO_NUM     26
#define SIOC_GPIO_NUM     27

#define Y9_GPIO_NUM       35
#define Y8_GPIO_NUM       34
#define Y7_GPIO_NUM       39
#define Y6_GPIO_NUM       36
#define Y5_GPIO_NUM       21
#define Y4_GPIO_NUM       19
#define Y3_GPIO_NUM       18
#define Y2_GPIO_NUM        5
#define VSYNC_GPIO_NUM    25
#define HREF_GPIO_NUM     23
#define PCLK_GPIO_NUM     22

// Wi-Fi credentials
const char* ssid = "SPOT-iot";
const char* password = "SuccionPourquoiSensation5900";
String computerIP ="";
WiFiUDP udp; 

WiFiServer server(12346);  // TCP server to listen for incoming connection



void startCamera() {
  camera_config_t config;
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer = LEDC_TIMER_0;
  config.pin_d0 = Y2_GPIO_NUM;
  config.pin_d1 = Y3_GPIO_NUM;
  config.pin_d2 = Y4_GPIO_NUM;
  config.pin_d3 = Y5_GPIO_NUM;
  config.pin_d4 = Y6_GPIO_NUM;
  config.pin_d5 = Y7_GPIO_NUM;
  config.pin_d6 = Y8_GPIO_NUM;
  config.pin_d7 = Y9_GPIO_NUM;
  config.pin_xclk = XCLK_GPIO_NUM;
  config.pin_pclk = PCLK_GPIO_NUM;
  config.pin_vsync = VSYNC_GPIO_NUM;
  config.pin_href = HREF_GPIO_NUM;
  config.pin_sccb_sda = SIOD_GPIO_NUM;
  config.pin_sccb_scl = SIOC_GPIO_NUM;
  config.pin_pwdn = PWDN_GPIO_NUM;
  config.pin_reset = RESET_GPIO_NUM;
  config.xclk_freq_hz = 20000000;
  config.pixel_format = PIXFORMAT_JPEG;

  config.frame_size = FRAMESIZE_QVGA; // Adjust the frame size here
  config.jpeg_quality = 12; // 0-63 lower means higher quality
  config.fb_count = 1;

  // Camera init
  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK) {
    Serial.printf("Camera init failed with error 0x%x", err);
    return;
  }
}


void setup() {
  Serial.begin(115200);

  WiFi.setHostname("superscanner8008");


  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("WiFi connected");
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());
  if (!MDNS.begin("superscanner8008")) {
  Serial.println("Error starting mDNS");
} else {
  Serial.println("mDNS responder started");
}

// Wait for the connection and receive the computer's IP address
 
  server.begin();


  // Initialize the camera
  startCamera();

  udp.begin(12345);
}

void loop() {
   // Check for incoming TCP connection to get the computer's IP address
  WiFiClient client = server.available();
  if (client) {
    Serial.println("Client connected");
    String ipMessage = "";
    while (client.connected()) {
      if (client.available()) {
        ipMessage = client.readStringUntil('\n');
        if (ipMessage.startsWith("IP:")) {
          computerIP = ipMessage.substring(3);  // Extract the IP address
          Serial.println("Received IP address: " + computerIP);
          client.stop();  // Close TCP connection after receiving the IP
          break;
        }
      }
    }
  }



    if (computerIP != "") {
      // Capture an image from the camera
      camera_fb_t *fb = esp_camera_fb_get();
      if (!fb) {
        Serial.println("Failed to capture image");
        return;
      }// Send the captured image over UDP to the computer IP
      udp.beginPacket(computerIP.c_str(), 12346);  // Use the computer's IP address and port for UDP
      udp.write(fb->buf, fb->len);  // Send the frame data
      udp.endPacket();

      Serial.println("Image sent via UDP");

      esp_camera_fb_return(fb);  // Free memory

      delay(300);  
    }
}
