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
    pulleyFactor(200. / 18.),
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
    return setPos(_x, _y, false);
}

int Arm::setPos(int _x, int _y, bool angles) {
    if (angles){
        if (_x < 0 || _x > 190 || _y < 0 || _y > 190) {
            Serial.println("Error: Angles out of range.");
            return -1;
        }
        // q1 and q2 are in radians
        q1 = _x * PI / 180;
        q2 = _y * PI / 180;
        angleToPos();
    } else {
        if (sqrt(pow(x, 2) + pow(y, 2)) > (a1 + a2) || sqrt(pow(x, 2) + pow(y, 2)) < abs(a1 - a2)) {
            Serial.println("Error: Coordinates out of range.");
            return -1;
        }
        x = _x;
        y = _y;
        posToAngles();
    }

    // Move the steppers
    stepper1.moveTo(gearFactor * fullRevolution * q1 / (2 * PI));
    stepper2.moveTo(-1 * pulleyFactor * fullRevolution * q2 / (2 * PI));

    Serial.println("Moving to : " + String(fullRevolution * q1 / (2 * PI)) + ", " + String(fullRevolution * q2 / (2 * PI)));
    return 0;
}

void Arm::stop() {
    float accel = stepper1.acceleration();
    stepper1.setAcceleration(10000);
    stepper2.setAcceleration(10000);
    stepper1.moveTo(stepper1.currentPosition());
    stepper2.moveTo(stepper2.currentPosition());
    q1 = stepper1.currentPosition() * 2 * PI / (gearFactor * fullRevolution);
    q2 = stepper2.currentPosition() * 2 * PI / (pulleyFactor * fullRevolution);
    angleToPos();
    stepper1.setAcceleration(accel);
    stepper2.setAcceleration(accel);
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

void Arm::posToAngles() {
    q2 = acos((pow(x, 2) + pow(y, 2) - pow(a1, 2) - pow(a2, 2)) / (2 * a1 * a2)); 
    q1 = atan2(y, x) - atan2(a2 * sin(q2), (a1 + a2 * cos(q2))); 
}

void Arm::angleToPos() {
    x = a1 * cos(q1) + a2 * cos(q1 + q2);
    y = a1 * sin(q1) + a2 * sin(q1 + q2);
}
