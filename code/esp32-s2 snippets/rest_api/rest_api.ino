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

// set the endpoints for the API
void setup_routing() { 
  server.on("/status", get_status);   
  server.on("/fwd", HTTP_GET, fwd);     
  server.on("/bwd", HTTP_GET, bwd);
  server.on("/lft", HTTP_GET, lft);
  server.on("/rgt", HTTP_GET, rgt);
  server.on("/hrgt", HTTP_GET, hrgt);
  server.on("/hlft", HTTP_GET, hlft);
  server.on("/stp", HTTP_GET, stp);
  server.on("arm/status", arm_status);
  server.on("/arm/goto", HTTP_POST, arm_goto);
  server.on("/arm/stop", HTTP_POST, arm_stop);
          
  server.begin();    
}

// retrieve the body of the request, parse it and send a response
void handlePost() {
  if (server.hasArg("plain") == false) {
  }
  String body = server.arg("plain");
  deserializeJson(jsonDocument, body);

  server.send(200, "application/json", "{}");
}

//---- Wheels ----
// return the current direction of the wheels
void get_status() {  
  jsonDocument.clear();
  jsonDocument["direction"] = directionMap(wheels.direction);
  serializeJson(jsonDocument, buffer);
  server.send(200, "application/json", buffer);
}

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
// return the current position of the arm and if it is currently moving
void arm_status() {
  jsonDocument.clear();
  jsonDocument["x"] = arm.x;
  jsonDocument["y"] = arm.y;
  jsonDocument["moving"] = arm.getMoving();
  serializeJson(jsonDocument, buffer);
  server.send(200, "application/json", buffer);
}

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
  // access the esp by http://superscanner8000/ when connected to the same network
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