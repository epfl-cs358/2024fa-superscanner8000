#include "arm.h"
#include <AccelStepper.h>
#include <Arduino.h>

Arm::Arm():   
    enablePin(40), 
    stepper1(AccelStepper::DRIVER, 8, 9), 
    stepper2(AccelStepper::DRIVER, 10, 11), 
    x(0), 
    y(0), 
    a1(40), 
    a2(40),
    gearFactor(28),
    pulleyFactor(200 / 18),
    fullRevolution(200), 
    q1(0), 
    q2(0) 
    {}

void Arm::setup() {
    pinMode(enablePin, OUTPUT);
    digitalWrite(enablePin, LOW);

    stepper1.setMaxSpeed(1000.0);
    stepper1.setAcceleration(100.0);

    stepper2.setMaxSpeed(1000.0);
    stepper2.setAcceleration(100.0);
}

int Arm::setPos(int _x, int _y) {
    x = _x;
    y = _y;

    
    // if the user wants to set the position using the angles
    q1 = x * PI / 180;
    q2 = y * PI / 180;
    

    /*
    // if the user wants to set the position using the coordinates
    if (sqrt(pow(x, 2) + pow(y, 2)) > (a1 + a2) || sqrt(pow(x, 2) + pow(y, 2)) < abs(a1 - a2)) {
        Serial.println("Error: Coordinates out of range.");
        return -1;
    }

    nomaAngles();
    */

    // Move the steppers
    stepper1.moveTo(gearFactor * fullRevolution * q1 / (2 * PI));
    stepper2.moveTo(-1 * pulleyFactor * fullRevolution * q2 / (2 * PI));

    Serial.println("Moving to : " + String(fullRevolution * q1 / (2 * PI)) + ", " + String(fullRevolution * q2 / (2 * PI)));
    return 0;
}

void Arm::stop() {
    stepper1.stop();
    stepper2.stop();
    // TODO: set the position and angle to the current position
}

bool Arm::getMoving() {
    return stepper1.distanceToGo() != 0 || stepper2.distanceToGo() != 0;
}

void Arm::update() {
    if (stepper1.distanceToGo() != 0) {
        stepper1.run();
    }
    if (stepper2.distanceToGo() != 0) {
        stepper2.run();
    }
}

void Arm::nomaAngles() {
    q2 = acos((pow(x, 2) + pow(y, 2) - pow(a1, 2) - pow(a2, 2)) / (2 * a1 * a2)); 
    q1 = atan2(y, x) - atan2(a2 * sin(q2), (a1 + a2 * cos(q2))); 
}
