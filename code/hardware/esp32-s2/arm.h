#ifndef ARM_H
#define ARM_H

#include <AccelStepper.h>

class Arm {
private:
    int enablePin;
    AccelStepper stepper2;
    AccelStepper stepper1;

    const long a1;
    const long a2;
    const long gearFactor;
    const float pulleyFactor;
    const long fullRevolution;
    void posToAngles();
    void angleToPos();
public:
    float q1;
    float q2;
    long x;
    long y;

    Arm(int m1Step, int m1Dir, int m2Step, int m2Dir, int _enablePin);
    void setup();
    int setPos(int _x, int _y);
    int setPos(int _x, int _y, bool angles = false);
    void stop();
    bool getMoving();
    void update();
};

#endif // ARM_H