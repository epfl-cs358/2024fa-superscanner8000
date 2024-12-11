#include "esp32-hal.h"
#include "wheels.h"
#include <Arduino.h>

char* directionMap(Direction Direction) {
    switch (Direction) {
        case FORWARD:
            return "forward";
        case BACKWARD:
            return "backward";
        case LEFT:
            return "left";
        case RIGHT:
            return "right";
        case HARD_LEFT:
            return "hard left";
        case HARD_RIGHT:
            return "hard right";
        case STOP:
            return "stop";
        default:
            return "unknown";
    }
}

Wheels::Wheels()
    :   motor1Pin1(2), 
        motor1Pin2(3),
        enable1Pin(1),

        motor2Pin1(5),
        motor2Pin2(4),
        enable2Pin(6),

        freq(30000),
        resolution(8),
        //pwmChannel1(0),
        //pwmChannel2(1),
        dutyCycle(200),

        t(0),
        targetTime(0),
        direction(STOP) {

}

void Wheels::setup() {
    // sets the pins as outputs:
    pinMode(motor1Pin1, OUTPUT);
    pinMode(motor1Pin2, OUTPUT);
    pinMode(enable1Pin, OUTPUT);

    pinMode(motor2Pin1, OUTPUT);
    pinMode(motor2Pin2, OUTPUT);
    pinMode(enable2Pin, OUTPUT);
    
    // configure LEDC PWM
    //ledcAttachChannel(enable1Pin, freq, resolution, pwmChannel1);
    //ledcAttachChannel(enable2Pin, freq, resolution, pwmChannel2);

    //ledcWrite(enable1Pin, dutyCycle);
    //ledcWrite(enable2Pin, dutyCycle);

    analogWrite(enable1Pin, dutyCycle);
    analogWrite(enable2Pin, dutyCycle);
}

// updates the wheels. If the target time is set, it will stop the wheels after the target time is reached
void Wheels::update() {
    if (targetTime > 0 && millis() - t > targetTime) {
        Serial.println("wheels:: time is up");
        stop();
        direction = STOP;
    }
}

void Wheels::stop() {
    targetTime = 0;
    direction = STOP;
    digitalWrite(motor1Pin1, LOW);
    digitalWrite(motor1Pin2, LOW);
    digitalWrite(motor2Pin1, LOW);
    digitalWrite(motor2Pin2, LOW);
}

void Wheels::forward(int ms) {
    Wheels::stop();
    t = millis();
    targetTime = ms;
    direction = FORWARD;
    digitalWrite(motor1Pin1, HIGH);
    digitalWrite(motor1Pin2, LOW);
    digitalWrite(motor2Pin1, HIGH);
    digitalWrite(motor2Pin2, LOW);
}

void Wheels::backward(int ms) {
    Wheels::stop();
    t = millis();
    targetTime = ms;
    direction = BACKWARD;
    digitalWrite(motor1Pin1, LOW);
    digitalWrite(motor1Pin2, HIGH);
    digitalWrite(motor2Pin1, LOW);
    digitalWrite(motor2Pin2, HIGH);
}

void Wheels::left(int ms) {
    Wheels::stop();
    t = millis();
    targetTime = ms;
    direction = LEFT;
    digitalWrite(motor1Pin1, HIGH);
    digitalWrite(motor1Pin2, LOW);
}

void Wheels::right(int ms) {
    Wheels::stop();
    t = millis();
    targetTime = ms;
    direction = RIGHT;
    digitalWrite(motor2Pin1, HIGH);
    digitalWrite(motor2Pin2, LOW);
}

void Wheels::hard_left(int ms) {
    Wheels::stop();
    t = millis();
    targetTime = ms;
    direction = HARD_LEFT;
    digitalWrite(motor1Pin1, HIGH);
    digitalWrite(motor1Pin2, LOW);
    digitalWrite(motor2Pin1, LOW);
    digitalWrite(motor2Pin2, HIGH);
}

void Wheels::hard_right(int ms) {
    Wheels::stop();
    t = millis();
    targetTime = ms;
    direction = HARD_RIGHT;
    digitalWrite(motor1Pin1, LOW);
    digitalWrite(motor1Pin2, HIGH);
    digitalWrite(motor2Pin1, HIGH);
    digitalWrite(motor2Pin2, LOW);
}
