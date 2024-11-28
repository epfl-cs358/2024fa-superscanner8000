#ifndef ARM_H
#define ARM_H

#include <AccelStepper.h>

class Arm {
private:
    int enablePin;
    AccelStepper stepper2;
    AccelStepper stepper1;

    long x;
    long y;

    const long a1;
    const long a2;
    const long fullRevolution;
    float q1;
    float q2;

public:
    Arm();
    void setup();
    void setPos(int x, int y);
    void stop();
    int update();
    void nomaAngles();
};

#endif // ARM_H