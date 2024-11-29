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
    const long fullRevolution;
    float q1;
    float q2;
    void nomaAngles();
public:
    long x;
    long y;
    
    Arm();
    void setup();
    void setPos(int x, int y);
    void stop();
    bool getMoving();
    void update();
};

#endif // ARM_H