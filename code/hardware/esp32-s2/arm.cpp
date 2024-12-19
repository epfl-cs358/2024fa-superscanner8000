#include "HardwareSerial.h"
#include "arm.h"
#include <AccelStepper.h>
#include <Arduino.h>

#define INIT_ANGLE 5. / 180. * PI
#define DEG_TO_RAD PI / 180.

Arm::Arm(int m1Step, int m1Dir, int m2Step, int m2Dir, int _enablePin):   
    enablePin(_enablePin), 
    stepper1(AccelStepper::DRIVER, m1Step, m1Dir), 
    stepper2(AccelStepper::DRIVER, m2Step, m2Dir), 
    x(0), 
    y(0), 
    a1(40), 
    a2(40),
    gearFactor(30), // 28
    pulleyFactor(200. / 20.),
    fullRevolution(200), 
    q1(0), 
    q2(0) 
    {}

// Setup function for the arm. Initializes the steppers and sets the enable pin
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

/** Set the position of the arm in either angles or coordinates
 * @param _x the x coordinate or angle in degrees
 * @param _y the y coordinate or angle in degrees
 * @param angles true if the input is in angles, false if it is in coordinates
 */
int Arm::setPos(int _x, int _y, bool angles) {
    if (angles){
        if (_x < -8 || _x > 190 || _y < 0 || _y > 190) {
            Serial.println("Error: Angles out of range.");
            return -1;
        }
        // q1 and q2 are in radians
        q1 = _x * DEG_TO_RAD;
        q2 = _y * DEG_TO_RAD;
        angleToPos();
    } else {
        if (sqrt(pow(x, 2) + pow(y, 2)) > (a1 + a2) || sqrt(pow(x, 2) + pow(y, 2)) < abs(a1 - a2)) {
            Serial.println("Error: Coordinates out of range.");
            return -1;
        }
        long oldX = x;
        long oldY = y;
        x = _x;
        y = _y;
        if (posToAngles() < 0) {
            x = oldX;
            y = oldY;
            return -1;
        }
    }

    // Move the steppers
    stepper1.moveTo(gearFactor * fullRevolution * (q1 - INIT_ANGLE) / (2 * PI));
    stepper2.moveTo(pulleyFactor * fullRevolution * (q2 - INIT_ANGLE) / (2 * PI));

    Serial.println("Moving to : " + String(fullRevolution * q1 / (2 * PI)) + ", " + String(fullRevolution * q2 / (2 * PI)));
    return 0;
}

// Stop the arm
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

// Check if the arm is moving
bool Arm::getMoving() {
    return stepper1.distanceToGo() != 0 || stepper2.distanceToGo() != 0;
}

// Update function to move the arm
void Arm::update() {
    if (stepper1.distanceToGo() != 0) {
        stepper1.run();
    }
    if (stepper2.distanceToGo() != 0) {
        stepper2.run();
    }
}

// Convert position to angles
int Arm::posToAngles() {
    float _q2 = acos((pow(x, 2) + pow(y, 2) - pow(a1, 2) - pow(a2, 2)) / (2 * a1 * a2)); 
    if (_q2 < 0) {
        _q2 = -_q2;
    } else if (q2 > PI) {
        _q2 = 2 * PI - _q2;
    }
    // float _q1 = atan2(y, x) - atan2(a2 * sin(_q2), (a1 + a2 * cos(_q2)));
    float _q1 = atan2(y, x) - acos((pow(a1, 2) + pow(x, 2) + pow(y, 2) - pow(a2, 2)) / (2 * a1 * sqrt(pow(x, 2) + pow(y, 2))));
    if (_q1 < 0) {
        _q1 = 2 * PI + _q1;
    }
    if (_q1 < -8. * DEG_TO_RAD || _q1 > 190. * DEG_TO_RAD || _q2 < 0. || _q2 > 190. * DEG_TO_RAD) {
        Serial.print("Error: Angles out of range. Angles are q1=");
        Serial.print(_q1 / PI * 180.);
        Serial.print(", q2=");
        Serial.println(180 - _q2 / PI * 180.);
        return -1;
    }
    q1 = _q1;
    q2 = 180 * DEG_TO_RAD - _q2;
    return 0;
}

// Convert angles to position
void Arm::angleToPos() {
    x = a1 * cos(q1) + a2 * cos(q1 + q2);
    y = a1 * sin(q1) + a2 * sin(q1 + q2);
}
