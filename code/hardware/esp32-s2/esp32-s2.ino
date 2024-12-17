#include <Arduino.h>
#include <WiFi.h>
#include <WebServer.h>
#include <LiquidCrystal.h>
#include "password.h"
#include "wheels.h"
#include "arm.h"
#include "cam_angles.h"
#include <ArduinoJson.h>
#include "display.h"

WebServer server(80);
Arm arm(8, 9, 10, 11, 7);
Wheels wheels(2, 3, 1, 5, 4, 6);
CamAngles camera(12, 13, 14, 15, 39, 40, 41, 42, 200);
Display display(36, 35, 34, 33, 20, 21, 37, 38); // rs, en, d4, d5, d6, d7, contrast, backlight

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
  server.on("/speed", HTTP_POST, set_speed);

  server.on("/arm/status", arm_status);
  server.on("/arm/goto", HTTP_POST, arm_goto);
  server.on("/arm/stp", HTTP_POST, arm_stop);

  server.on("/cam/status", cam_status);
  server.on("/cam/goto", HTTP_POST, cam_goto);
  server.on("/cam/stp", HTTP_POST, cam_stop);

  server.on("/text", HTTP_POST, text);
  server.on("/scroll", HTTP_POST, scroll);
          
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

void set_speed() {
  handlePost();

  int speed = jsonDocument["speed"];
  if (speed < 0 || speed > 255) {
    server.send(422, "application/json", "{}");
    return;
  }
  wheels.setDutyCycle(speed);
  server.send(200, "application/json", "{}");
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
  jsonDocument["q1"] = arm.q1;
  jsonDocument["q2"] = arm.q2;
  jsonDocument["moving"] = arm.getMoving();
  serializeJson(jsonDocument, buffer);
  server.send(200, "application/json", buffer);
}

void arm_goto() {
  handlePost();

  Serial.println("Arm goto");
  int x = jsonDocument["x"];
  int y = jsonDocument["y"];

  bool angles = false;
  if (jsonDocument.containsKey("angles")) {
    angles = jsonDocument["angles"];
  }
  Serial.println(x);
  Serial.println(y);
  Serial.println(angles);

  if (arm.setPos(x, y, angles) == -1) {
    server.send(422, "application/json", "{}");
    return;
  }

  StaticJsonDocument<200> doc;
  doc["x"] = arm.x;
  doc["y"] = arm.y;
  doc["q1"] = arm.q1;
  doc["q2"] = arm.q2;
  String resp;
  serializeJson(doc, resp);
  server.send(200, "application/json", resp);
}

void arm_stop() {
  Serial.println("Arm stop");
  arm.stop();
  server.send(200, "application/json", "{}");
}


//---- Camera ----
void cam_status() {
  jsonDocument.clear();
  jsonDocument["moving"] = camera.isMoving();
  jsonDocument["alpha"] = camera.stepsToAngle(1);
  jsonDocument["beta"] = camera.stepsToAngle(2);
  serializeJson(jsonDocument, buffer);
  server.send(200, "application/json", buffer);
}

void cam_goto() {
  handlePost();
  
  float angle1 = jsonDocument["alpha"];
  float angle2 = jsonDocument["beta"];
  if (camera.moveToAngles(angle1, angle2) == -1){
    server.send(422, "application/json", "{}");
    return;
  }

  server.send(200, "application/json", "{}");
}

void cam_stop() {
  handlePost();
  Serial.println("cam stop");
  camera.stop();

  server.send(200, "application/json", "{}");
}

//---- Display ----
void text() {
  handlePost();
  
  String text = jsonDocument["text"];
  
  display.print(text);

  Serial.print("Text is: ");
  Serial.println(text);

  server.send(200, "application/json", "{}");
}

void scroll() {
  handlePost();
  
  String text1 = jsonDocument["text1"];
  String text2 = jsonDocument["text2"];
  
  display.scroll(text1, text2);

  server.send(200, "application/json", "{}");
}


void setup() {
  Serial.begin(115200); 

  arm.setup();
  wheels.setup();
  camera.setup();
  display.setup();

  display.scroll("Connecting to Wi-Fi", "Please wait");

  Serial.print("Connecting to Wi-Fi with password ");
  Serial.println(PWD);
  // access the esp by http://superscanner8000/ when connected to the same network
  WiFi.setHostname("superscanner8000");
  WiFi.begin(SSID, PWD);
  while (WiFi.status() != WL_CONNECTED) {
    Serial.print(".");
    delay(500);
  }
  
  display.scroll("Connected to Wi-Fi with hostname superscanner8000", "");
  Serial.print("Connected! IP Address: ");
  Serial.println(WiFi.localIP()); 
  setup_routing();
}    
       
void loop() {    
  server.handleClient();     
  arm.update();
  wheels.update();
  camera.update();
  display.update();
}