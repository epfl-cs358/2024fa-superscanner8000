#include <Arduino.h>
#include <WiFi.h>
#include <WebServer.h>
#include <ArduinoJson.h>
#include "password.h"
#include "wheels.h"
#include "arm.h"

WebServer server(80);
Arm arm = Arm();
Wheels wheels = Wheels();

StaticJsonDocument<250> jsonDocument;
char buffer[250];
 
void setup_routing() {    
  server.on("/fwd", HTTP_POST, fwd);     
  server.on("/bwd", HTTP_POST, bwd);
  server.on("/lft", HTTP_POST, lft);
  server.on("/rgt", HTTP_POST, rgt);
  server.on("/hrgt", HTTP_POST, hrgt);
  server.on("/hlft", HTTP_POST, hlft);
  server.on("/stp", HTTP_POST, stp);
  server.on("/arm/goto", HTTP_POST, arm_goto);
          
  server.begin();    
}
 
// must be changed for more general use
void create_json(char *tag, float value, char *unit) {  
  jsonDocument.clear();  
  jsonDocument["type"] = tag;
  jsonDocument["value"] = value;
  jsonDocument["unit"] = unit;
  serializeJson(jsonDocument, buffer);
}
 
void add_json_object(char *tag, float value, char *unit) {
  JsonObject obj = jsonDocument.createNestedObject();
  obj["type"] = tag;
  obj["value"] = value;
  obj["unit"] = unit; 
}

void handlePost() {
  if (server.hasArg("plain") == false) {
  }
  String body = server.arg("plain");
  deserializeJson(jsonDocument, body);

  server.send(200, "application/json", "{}");
}

//---- Wheels ----
void fwd() {
  handlePost();
  Serial.print("Forward ");
  Serial.println((int)jsonDocument["ms"]);
  wheels.forward(jsonDocument["ms"]);
  server.send(200, "application/json", "{}");
}

void bwd() {
  handlePost();
  Serial.print("Backward ");
  Serial.println((int)jsonDocument["ms"]);
  wheels.backward(jsonDocument["ms"]);
  server.send(200, "application/json", "{}");
}

void lft() {
  handlePost();
  Serial.print("Left ");
  Serial.println((int)jsonDocument["ms"]);
  wheels.left(jsonDocument["ms"]);
  server.send(200, "application/json", "{}");
}

void rgt() {
  handlePost();
  Serial.print("Right ");
  Serial.println((int)jsonDocument["ms"]);
  wheels.right(jsonDocument["ms"]);
  server.send(200, "application/json", "{}");
}

void hrgt() {
  handlePost();
  Serial.print("Hard right ");
  Serial.println((int)jsonDocument["ms"]);
  wheels.hard_right(jsonDocument["ms"]);
  server.send(200, "application/json", "{}");
}

void hlft() {
  handlePost();
  Serial.print("Hard left ");
  Serial.println((int)jsonDocument["ms"]);
  wheels.hard_left(jsonDocument["ms"]);
  server.send(200, "application/json", "{}");
}

void stp() {
  Serial.println("Stop");
  wheels.stop();
  server.send(200, "application/json", "{}");
}

//---- Arm ----
void arm_goto() {
  handlePost();

  Serial.println("Arm goto");
  int x = jsonDocument["x"];
  int y = jsonDocument["y"];
  arm.setPos(x, y);
  Serial.println(x);
}

void arm_stop() {
  Serial.println("Arm stop");
  arm.stop();
}

void setup() {     
  Serial.begin(115200);  

  Serial.print("Connecting to Wi-Fi with password ");
  Serial.println(PWD);
  WiFi.setHostname("superscanner8000");
  WiFi.begin(SSID, PWD);
  while (WiFi.status() != WL_CONNECTED) {
    Serial.print(".");
    delay(500);
  }
 
  Serial.print("Connected! IP Address: ");
  Serial.println(WiFi.localIP()); 
  setup_routing();

  arm.setup();
  wheels.setup();
}    
       
void loop() {    
  server.handleClient();     
  arm.update();
  wheels.update();
}