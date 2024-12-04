#include <Arduino.h>
#include <WiFi.h>
#include <WebServer.h>
#include <ArduinoJson.h>
#include "password.h"
#include "wheels.h"
#include "arm.h"
#include "cam_angles.h"

WebServer server(80);
Arm arm = Arm();
Wheels wheels = Wheels();
CamAngles camera(12, 13, 14, 15, 36, 37, 38, 39, 200); 

StaticJsonDocument<250> jsonDocument;
char buffer[250];

// set the endpoints for the API
void setup_routing() { 
  server.on("/status", get_status);   
  server.on("/fwd", HTTP_POST, fwd);     
  server.on("/bwd", HTTP_POST, bwd);
  server.on("/lft", HTTP_POST, lft);
  server.on("/rgt", HTTP_POST, rgt);
  server.on("/hrgt", HTTP_POST, hrgt);
  server.on("/hlft", HTTP_POST, hlft);
  server.on("/stp", HTTP_POST, stp);
  server.on("/arm/status", arm_status);
  server.on("/arm/goto", HTTP_POST, arm_goto);
  server.on("/arm/stop", HTTP_POST, arm_stop);
          
  server.begin();    
}

// retrieve the body of the request and parse it
void handlePost() {
  if (server.hasArg("plain") == false) {
  }
  String body = server.arg("plain");
  deserializeJson(jsonDocument, body);
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
  jsonDocument["target x"] = arm.x;
  jsonDocument["target y"] = arm.y;
  jsonDocument["moving"] = arm.getMoving();
  serializeJson(jsonDocument, buffer);
  server.send(200, "application/json", buffer);
}

void arm_goto() {
  handlePost();

  Serial.println("Arm goto");
  int x = jsonDocument["x"];
  int y = jsonDocument["y"];

  float currentSum = arm.q1 + arm.q2;

  if (arm.setPos(x, y) == -1) {
    server.send(422, "application/json", "{}");
    return;
  }

  float newSum = arm.q1 + arm.q2;
  float cameraCompensation = currentSum - newSum;
  camera.moveToAngles(cameraCompensation, 0); 

  server.send(200, "application/json", "{}");
}

void arm_stop() {
  Serial.println("Arm stop");
  arm.stop();
  server.send(200, "application/json", "{}");
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
  camera.setup();
}    
       
void loop() {    
  server.handleClient();     
  arm.update();
  yield();
  wheels.update();
  camera.update();
}