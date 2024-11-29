#ifndef WHHEL_H
#define WHHEL_H

#include <Arduino.h>

enum Direction {
    FORWARD,
    BACKWARD,
    LEFT,
    RIGHT,
    HARD_LEFT,
    HARD_RIGHT,
    STOP
};

char* directionMap(Direction direction);

class Wheels {
    private:
        int motor1Pin1;
        int motor1Pin2;
        int enable1Pin;

        int motor2Pin1;
        int motor2Pin2;
        int enable2Pin;

        const int freq;
        const int resolution;
        const int pwmChannel1;
        const int pwmChannel2;
        int dutyCycle;

        long t;
        long targetTime;
    public:
        Direction direction;

        Wheels();
        void setup();
        void forward(int ms);
        void backward(int ms);
        void left(int ms);
        void right(int ms);
        void hard_left(int ms);
        void hard_right(int ms);
        void stop();
        void update();
};

#endif // WHHEL_H