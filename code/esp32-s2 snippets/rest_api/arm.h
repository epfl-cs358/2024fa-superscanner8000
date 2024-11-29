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
    void nomaAngles();
public:
    float q1;
    float q2;
    long x;
    long y;

    Arm();
    void setup();
    int setPos(int x, int y);
    void stop();
    bool getMoving();
    void update();
};

#endif // ARM_H