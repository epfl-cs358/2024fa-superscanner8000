#include "cam_angles.h"
#include <Arduino.h>

// Constructor: initializes steppers and sets pins
CamAngles::CamAngles(int s1Pin1, int s1Pin2, int s1Pin3, int s1Pin4, 
                     int s2Pin1, int s2Pin2, int s2Pin3, int s2Pin4, 
                     int stepsPerRev) 
    : stepper1(AccelStepper::FULL4WIRE, s1Pin1, s1Pin2, s1Pin3, s1Pin4),
      stepper2(AccelStepper::FULL4WIRE, s2Pin1, s2Pin2, s2Pin3, s2Pin4),
      stepsPerRevolution(stepsPerRev) {
    multiStepper.addStepper(stepper1);
    multiStepper.addStepper(stepper2);
}

// Setup function
void CamAngles::setup() {
    stepper1.setMaxSpeed(500.0);
    stepper2.setMaxSpeed(500.0);

    stepper1.setAcceleration(100.0);
    stepper2.setAcceleration(100.0);
}

// Convert angle to steps based on steps per revolution
long CamAngles::angleToSteps(float angle) {
    return static_cast<long>((angle / 360.0) * stepsPerRevolution);
}

// Convert steps to angle based on steps per revolution
float CamAngles::stepsToAngle(long steps) {
    return (steps / stepsPerRevolution) * 360.0;
}

// Move steppers to specified angles
void CamAngles::moveToAngles(float angle1, float angle2) {
    long positions[2]; // Array to hold target positions
    positions[0] = angleToSteps(angle1);
    positions[1] = angleToSteps(angle2);

    Serial.print("Moving to angles: ");
    Serial.print(angle1);
    Serial.print(", ");
    Serial.println(angle2);

    multiStepper.moveTo(positions);
}

// Check if the motors are moving
bool CamAngles::isMoving() {
    return stepper1.distanceToGo() != 0 || stepper2.distanceToGo() != 0;
}

// Update function for continuous motor operation (if needed)
void CamAngles::update() {
    stepper1.run();
    stepper2.run();
}

// Stop the motors
void CamAngles::stop() {
    stepper1.stop();
    stepper2.stop();
}