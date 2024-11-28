#include <Arduino.h>
#include <WiFi.h>
#include <WebServer.h>
#include <ArduinoJson.h>

const char *SSID = "qwer";
const char *PWD = "12345678";

enum TYPE {
  SINGLE_NUMBER,
  TWO_NUMBERS,
  BOOLEAN
};

WebServer server(80);

StaticJsonDocument<250> jsonDocument;
char buffer[250];
 
void setup_routing() {    
  server.on("/forward", HTTP_POST, handleForward);     
  server.on("/backward", HTTP_POST, handlePost);
  server.on("/left", HTTP_POST, handlePost);  
  server.on("/right", HTTP_POST, handlePost);  
  server.on("/stop", HTTP_POST, handlePost);  
  server.on("/arm/goto", HTTP_POST, handlePost);  
  server.on("/arm/stop", HTTP_POST, handlePost);  
          
  server.begin();    
}


void handleForward(){
    Serial.println("Forward");
    handlePost(SINGLE_NUMBER, forward);
}

void handlePost(TYPE type, void* func) {
  if (server.hasArg("plain") == false) {
  }
  String body = server.arg("plain");
  deserializeJson(jsonDocument, body);

  switch (type)
  {
  case SINGLE_NUMBER:
    ((void (*)(int))func)(jsonDocument["x"]);
    break;
  case TWO_NUMBERS:
    ((void (*)(int, int))func)(jsonDocument["x"], jsonDocument["y"]);
    break;
  case BOOLEAN:
    ((void (*)(bool))func)(jsonDocument["x"]);
  
  default:
    break;
  }

  Serial.println(jsonDocument);

  server.send(200, "application/json", "{}");
}

void setup() {     
  Serial.begin(115200);  

  while (Serial.available() == 0) {
    // Wait for user input
  }
  password = Serial.readString();
  while (Serial.available() > 0) {
    Serial.read(); // Clear the buffer
  }

  Serial.print("Connecting to Wi-Fi");
  WiFi.setHostname("superscanner8000");
  WiFi.begin(SSID, PWD);
  while (WiFi.status() != WL_CONNECTED) {
    Serial.print(".");
    delay(500);
  }
 
  Serial.print("Connected! IP Address: ");
  Serial.println(WiFi.localIP()); 
  setup_routing();     
   
}    
       
void loop() {    
  server.handleClient();     
}