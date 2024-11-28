#include "arm.h"
#include <AccelStepper.h>
#include <Arduino.h>

Arm::Arm() 
    : enablePin(40), 
      stepper2(AccelStepper::DRIVER, 37, 36), 
      stepper1(AccelStepper::DRIVER, 11, 10), 
      x(0), 
      y(0), 
      a1(40), 
      a2(40), 
      fullRevolution(200), 
      q1(0), 
      q2(0) {
}

void Arm::setup() {
    pinMode(enablePin, OUTPUT);
    digitalWrite(enablePin, LOW);

    stepper1.setMaxSpeed(1000.0);
    stepper1.setAcceleration(100.0);

    stepper2.setMaxSpeed(1000.0);
    stepper2.setAcceleration(100.0);
}

void Arm::setPos(int x, int y) {
    q1 = x * PI / 180;
    q2 = y * PI / 180;

    stepper1.moveTo(q1 * fullRevolution / (2 * PI));
    stepper2.moveTo(q2 * (-fullRevolution) / (2 * PI));

    Serial.println("Moving to : " + String(fullRevolution * q1 / (2 * PI)) + ", " + String(fullRevolution * q2 / (2 * PI)));
}

void Arm::stop() {
    stepper1.stop();
    stepper2.stop();
}

int Arm::update() {
    int ret = -1;
    if (stepper1.distanceToGo() != 0) {
        stepper1.run();
        ret = 0;
    }
    if (stepper2.distanceToGo() != 0) {
        stepper2.run();
        ret = 0;
    }
    return ret;
}

void Arm::nomaAngles() {
    q2 = acos((pow(x, 2) + pow(y, 2) - pow(a1, 2) - pow(a2, 2)) / (2 * a1 * a2)); 
    q1 = atan2(y, x) - atan2(a2 * sin(q2), (a1 + a2 * cos(q2))); 
}
