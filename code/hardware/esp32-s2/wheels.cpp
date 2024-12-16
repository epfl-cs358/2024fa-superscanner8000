#include "esp32-hal.h"
#include "wheels.h"
#include <Arduino.h>

const float WHEEL_DIAMETER_CM = 15.0; // Diameter of the wheel in cm
const float WHEEL_CIRCUMFERENCE_CM = 3.1416 * WHEEL_DIAMETER_CM; // Circumference of the wheel in cm
const int MAX_RPM = 110; // Max RPM of the motor
const float TRACK_WIDTH_CM = 26.0; // Distance between the two wheels in cm
const float CM_PER_SECOND = 15.0; // Distance per second in cm
const float SECONDS_PER_TURN = 10; // Time in seconds to turn 360 degrees
const float ANGLE_PER_SECOND = 360 / SECONDS_PER_TURN; // Angle per second in degrees

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

Wheels::Wheels(int m1Pin1, int m1Pin2, int m1En, int m2Pin1, int m2Pin2, int m2En)
    :   motor1Pin1(m1Pin1), 
        motor1Pin2(m1Pin2),
        enable1Pin(m1En),

        motor2Pin1(m2Pin1),
        motor2Pin2(m2Pin2),
        enable2Pin(m2En),

        freq(30000),
        resolution(8),
        pwmChannel1(0),
        pwmChannel2(1),

        dutyCycle(255),
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
    
    analogWrite(enable1Pin, dutyCycle);
    analogWriteResolution(enable1Pin, 8);
    analogWriteFrequency(enable1Pin, 30000);
    analogWrite(enable2Pin, dutyCycle);
    analogWriteResolution(enable2Pin, 8);
    analogWriteFrequency(enable2Pin, 30000);

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
    analogWrite(enable1Pin, freq);
    analogWrite(enable2Pin, resolution);

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

// stop the wheels
void Wheels::stop() {
    targetTime = 0;
    direction = STOP;
    digitalWrite(motor1Pin1, LOW);
    digitalWrite(motor1Pin2, LOW);
    digitalWrite(motor2Pin1, LOW);
    digitalWrite(motor2Pin2, LOW);
}

/** move the wheels forward for ms milliseconds. Moves indefinitely if ms is smaller than 0
 * @param ms the time in milliseconds to move, smaller than 0 to move indefinitely
 */
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

/** move the wheels backward for ms milliseconds. Moves indefinitely if ms is smaller than 0
 * @param ms the time in milliseconds to move, smaller than 0 to move indefinitely
 */
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

/** turn one wheel left for ms milliseconds. Moves indefinitely if ms is smaller than 0
 * @param ms the time in milliseconds to turn, smaller than 0 to move indefinitely
 */
void Wheels::left(int ms) {
    Wheels::stop();
    t = millis();
    targetTime = ms;
    direction = LEFT;
    digitalWrite(motor1Pin1, HIGH);
    digitalWrite(motor1Pin2, LOW);
}

/** turn one wheel right for ms milliseconds. Moves indefinitely if ms is smaller than 0
 * @param ms the time in milliseconds to turn, smaller than 0 to move indefinitely
 */
void Wheels::right(int ms) {
    Wheels::stop();
    t = millis();
    targetTime = ms;
    direction = RIGHT;
    digitalWrite(motor2Pin1, HIGH);
    digitalWrite(motor2Pin2, LOW);
}

/** turn both wheels left (turn on itself) for ms milliseconds. Moves indefinitely if ms is smaller than 0
 * @param ms the time in milliseconds to turn, smaller than 0 to move indefinitely
 */
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

/** turn both wheels right (turn on itself) for ms milliseconds. Moves indefinitely if ms is smaller than 0
 * @param ms the time in milliseconds to turn, smaller than 0 to move indefinitely
 */
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

/** move the wheels forward for cm centimeters
 * @param cm the distance in centimeters to move
 */
void Wheels::forward_cm(int cm) {
    int ms = (cm / CM_PER_SECOND) * 1000; 
    forward(ms);
}

/** move the wheels backward for cm centimeters
 * @param cm the distance in centimeters to move
 */
void Wheels::backward_cm(int cm) {
    int ms = (cm / CM_PER_SECOND) * 1000;
    backward(ms);
}

/** turn left on itself for angle degrees
 * @param angle the angle in degrees to turn
 */
void Wheels::hard_left_angle(float angle) {
    // float angularVelocity = (distancePerSecond * 360) / (3.1416 * TRACK_WIDTH_CM);
    float timeInSeconds = angle / ANGLE_PER_SECOND;
    int ms = timeInSeconds * 1000;

    hard_left(ms);
}

/** turn right on itself for angle degrees
 * @param angle the angle in degrees to turn
 */
void Wheels::hard_right_angle(float angle) {
    // float angularVelocity = (distancePerSecond * 360) / (3.1416 * TRACK_WIDTH_CM);
    float timeInSeconds = angle / ANGLE_PER_SECOND;
    int ms = timeInSeconds * 1000;

    hard_right(ms);
}
