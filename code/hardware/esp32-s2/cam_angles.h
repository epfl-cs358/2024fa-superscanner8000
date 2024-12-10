#ifndef CAM_ANGLES_H
#define CAM_ANGLES_H

#include <AccelStepper.h>
#include <MultiStepper.h>

class CamAngles {
private:
    AccelStepper stepper1; // First stepper motor
    AccelStepper stepper2; // Second stepper motor
    MultiStepper multiStepper; // Synchronize both steppers

    const int stepsPerRevolution; // Steps per revolution for the steppers

    // Convert angle to steps
    long angleToSteps(float angle);

public:
    // Constructor
    CamAngles(int s1Pin1, int s1Pin2, int s1Pin3, int s1Pin4, 
              int s2Pin1, int s2Pin2, int s2Pin3, int s2Pin4, 
              int stepsPerRev);

    // Initialization
    void setup();

    // Move the steppers to the specified angles
    void moveToAngles(float angle1, float angle2);

    // Check if the motors are moving
    bool isMoving();

    // Update to keep the motors running
    void update();

    // Stop the motors
    void stop();
    
    // Convert steps to angle
    float stepsToAngle(int axis);
};

#endif // CAM_ANGLES_H