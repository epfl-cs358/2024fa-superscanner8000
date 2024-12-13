#include "esp32-hal.h"
#include "wheels.h"
#include <Arduino.h>

const float WHEEL_DIAMETER_CM = 15.0; // Diameter of the wheel in cm
const float WHEEL_CIRCUMFERENCE_CM = 3.1416 * WHEEL_DIAMETER_CM; // Circumference of the wheel in cm
const int MAX_RPM = 110; // Max RPM of the motor
const float TRACK_WIDTH_CM = 26.0; // Distance between the two wheels in cm


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
        distancePerSecond(0.0),

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

    updateDistancePerSecond();
}

void Wheels::updateDistancePerSecond() {
    float currentRPM = MAX_RPM * (dutyCycle / 100.0); // RPM at given duty cycle
    float rps = currentRPM / 60.0;                    // Rotations per second
    distancePerSecond = WHEEL_CIRCUMFERENCE_CM * rps; // Distance per second in cm
}

void Wheels::setDutyCycle(int newDutyCycle) {
    dutyCycle = newDutyCycle;

    // Update PWM output
    analogWrite(enable1Pin, dutyCycle);
    analogWrite(enable2Pin, dutyCycle);

    // Update cached distance per second
    updateDistancePerSecond();
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

// Function with cm distance 

void Wheels::forward_cm(int cm) {
    int ms = (cm / distancePerSecond) * 1000; 
    forward(ms);
}

void Wheels::backward_cm(int cm) {
    int ms = (cm / distancePerSecond) * 1000;
    backward(ms);
}

void Wheels::hard_left_angle(float angle) {
    float angularVelocity = (distancePerSecond * 360) / (3.1416 * TRACK_WIDTH_CM);
    float timeInSeconds = angle / angularVelocity;
    int ms = timeInSeconds * 1000;

    hard_left(ms);
}

void Wheels::hard_right_angle(float angle) {
    float angularVelocity = (distancePerSecond * 360) / (3.1416 * TRACK_WIDTH_CM);
    float timeInSeconds = angle / angularVelocity;
    int ms = timeInSeconds * 1000;

    hard_right(ms);
}
