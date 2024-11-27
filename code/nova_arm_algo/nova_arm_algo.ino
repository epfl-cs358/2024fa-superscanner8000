#include <AccelStepper.h>

// Define some steppers and the pins the will use
int enablePin = 40;
AccelStepper stepper1(AccelStepper::DRIVER, 11, 10);
AccelStepper stepper2(AccelStepper::DRIVER, 37, 36); // the one with belt facing the other way

long x = 0;
long y = 0;

const long a1 = 40; // length of lower arm in cm
const long a2 = 40; // length of upper arm in cm
const long gear_factor = 28; // factor created by gearbox on angle q1
const float pulley_factor = 200 / 18; // factor created by pulley on angle q2
const long full_revolution = 200;
float q1 = 0; // angle of lower arm (in radians) - stepper1
float q2 = 0; // angle of upper arm (in radians) - stepper2

void setup() {
  pinMode(enablePin, OUTPUT);
  digitalWrite(enablePin, LOW);

  stepper1.setMaxSpeed(1000.0);
  stepper1.setAcceleration(100.0);
  
  stepper2.setMaxSpeed(1000.0);
  stepper2.setAcceleration(100.0);

  Serial.begin(115200);
}

void loop() {
  Serial.println("Current Angle : " + String(q1) + ", " + String(q2));
  Serial.println("Please enter q1 q2 angles (press Enter after typing):");

  while (Serial.available() == 0) {
    // Wait for user input
  }
  q1 = Serial.parseInt() * PI / 180;
  q2 = Serial.parseInt() * PI / 180;
  while (Serial.available() > 0) {
    Serial.read(); // Clear the buffer
  }

  /*
  Serial.println("Current Coordinates : " + String(x) + ", " + String(y));
  Serial.println("Please enter x y coordinates (press Enter after typing):");

  while (Serial.available() == 0) {
    // Wait for user input
  }
  x = Serial.parseInt();
  y = Serial.parseInt();
  while (Serial.available() > 0) {
    Serial.read(); // Clear the buffer
  }

  if (sqrt(pow(x, 2) + pow(y, 2)) > (a1 + a2) || sqrt(pow(x, 2) + pow(y, 2)) < abs(a1 - a2)) {
    Serial.println("Error: Coordinates out of range. Please enter valid values.");
    return;
  }

  Serial.print("x = ");
  Serial.print(x);
  Serial.print("  y = ");
  Serial.println(y);

  noma_angles();
  */
  Serial.println("New angles : " + String(q1) + ", " + String(q2));
  Serial.println("New angles (degrees) : " + String(q1 * 180 / PI) + ", " + String(q2 * 180 / PI));
  
  stepper1.moveTo(gear_factor * full_revolution * q1 / (2 * PI));
  stepper2.moveTo(-1 * pulley_factor * full_revolution * q2 / (2 * PI)); // -1 beacause facing the other way

  Serial.println("Moving to : " + String(full_revolution * q1 / (2 * PI)) + ", " + String(full_revolution * q2 / (2 * PI)));

  while(stepper1.distanceToGo() != 0) {
        stepper1.run();
        Serial.println(stepper1.speed());
  }
  while(stepper2.distanceToGo() != 0) {
        stepper2.run();
        Serial.println(stepper2.speed());
  }
}

void noma_angles() {
  q2 = acos((pow(x, 2) + pow(y, 2) - pow(a1, 2) - pow(a2, 2)) / (2 * a1 * a2)); 
  q1 = atan2(y, x) - atan2(a2 * sin(q2), (a1 + a2 * cos(q2))); 
}