#include "wheels.h"
#include <Arduino.h>

Wheels::Wheels()
    :   motor1Pin1(3), 
        motor1Pin2(2),
        enable1Pin(1),

        motor2Pin1(40),
        motor2Pin2(39),
        enable2Pin(41),

        freq(30000),
        resolution(8),
        pwmChannel1(0),
        pwmChannel2(1),
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
    ledcAttachChannel(enable1Pin, freq, resolution, pwmChannel1);
    ledcAttachChannel(enable2Pin, freq, resolution, pwmChannel2);

    ledcWrite(enable1Pin, dutyCycle);
    ledcWrite(enable2Pin, dutyCycle);
}

int Wheels::update() {
    if (direction == STOP){
        return -1;
    }
    if (targetTime > 0 && millis() - t > targetTime) {
        stop();
        direction = STOP;
        return -1;
    }
    return 0;

}

void Wheels::stop() {
    digitalWrite(motor1Pin1, LOW);
    digitalWrite(motor1Pin2, LOW);
    digitalWrite(motor2Pin1, LOW);
    digitalWrite(motor2Pin2, LOW);
}

void Wheels::forward(int ms) {
    t = millis();
    targetTime = ms;
    digitalWrite(motor1Pin1, HIGH);
    digitalWrite(motor1Pin2, LOW);
    digitalWrite(motor2Pin1, HIGH);
    digitalWrite(motor2Pin2, LOW);
}

void Wheels::backward(int ms) {
    t = millis();
    targetTime = ms;
    digitalWrite(motor1Pin1, LOW);
    digitalWrite(motor1Pin2, HIGH);
    digitalWrite(motor2Pin1, LOW);
    digitalWrite(motor2Pin2, HIGH);
}

void Wheels::left(int ms) {
    t = millis();
    targetTime = ms;
    digitalWrite(motor1Pin1, HIGH);
    digitalWrite(motor1Pin2, LOW);
}

void Wheels::right(int ms) {
    t = millis();
    targetTime = ms;
    digitalWrite(motor2Pin1, HIGH);
    digitalWrite(motor2Pin2, LOW);
}

void Wheels::hard_left(int ms) {
    t = millis();
    targetTime = ms;
    digitalWrite(motor1Pin1, HIGH);
    digitalWrite(motor1Pin2, LOW);
    digitalWrite(motor2Pin1, LOW);
    digitalWrite(motor2Pin2, HIGH);
}

void Wheels::hard_right(int ms) {
    t = millis();
    targetTime = ms;
    digitalWrite(motor1Pin1, LOW);
    digitalWrite(motor1Pin2, HIGH);
    digitalWrite(motor2Pin1, HIGH);
    digitalWrite(motor2Pin2, LOW);
}
