// Motor A = Right
int motor1Pin1 = 3; 
int motor1Pin2 = 2; 
int enable1Pin = 1; 

// Motor B = Left
int motor2Pin1 = 40; 
int motor2Pin2 = 39; 
int enable2Pin = 41; 

// Setting PWM properties
const int freq = 30000;
const int pwmChannel1 = 0;
const int pwmChannel2 = 1;
const int resolution = 8;
//starts at ~150 ends at 255
int dutyCycle = 0;

void setup() {
  Serial.begin(115200);
  
  // sets the pins as outputs:
  pinMode(motor1Pin1, OUTPUT);
  pinMode(motor1Pin2, OUTPUT);
  pinMode(enable1Pin, OUTPUT);

  pinMode(motor2Pin1, OUTPUT);
  pinMode(motor2Pin2, OUTPUT);
  pinMode(enable2Pin, OUTPUT);
  
  // configure LEDC PWM
  Serial.println(ledcAttachChannel(enable1Pin, freq, resolution, pwmChannel1));
  Serial.println(ledcAttachChannel(enable2Pin, freq, resolution, pwmChannel2));

  ledcWrite(enable1Pin, dutyCycle);
  ledcWrite(enable2Pin, dutyCycle);

}

void loop() {
  // Move the DC motor forward at maximum speed
  forward(2000);
  stop();
  backward(2000);
  stop();
  right(1000);
  stop();
  left(1000);
  stop();

  dutyCycle += 10;

  Serial.println(dutyCycle);
  
  ledcWrite(enable1Pin, dutyCycle);
  ledcWrite(enable2Pin, dutyCycle);

  /*
  // Move DC motor forward with increasing speed
  digitalWrite(motor1Pin1, HIGH);
  digitalWrite(motor1Pin2, LOW);
  while (dutyCycle <= 255){
    ledcWrite(enable1Pin, dutyCycle);   
    Serial.print("Forward with duty cycle: ");
    Serial.println(dutyCycle);
    dutyCycle = dutyCycle + 5;
    delay(500);
  }
  dutyCycle = 200;
  */
}

void forward(int n) {
  digitalWrite(motor1Pin1, LOW);
  digitalWrite(motor1Pin2, HIGH);
  digitalWrite(motor2Pin1, LOW);
  digitalWrite(motor2Pin2, HIGH);
  delay(n);
  stop();
}

void backward(int n) {
  digitalWrite(motor1Pin1, HIGH);
  digitalWrite(motor1Pin2, LOW);
  digitalWrite(motor2Pin1, HIGH);
  digitalWrite(motor2Pin2, LOW);
  delay(n);
  stop();
}

void stop() {
  digitalWrite(motor1Pin1, LOW);
  digitalWrite(motor1Pin2, LOW);
  digitalWrite(motor2Pin1, LOW);
  digitalWrite(motor2Pin2, LOW);
}

void right(int n) {
  digitalWrite(motor1Pin1, LOW);
  digitalWrite(motor1Pin2, HIGH);
  delay(n);
  stop();
}

void left(int n) {
  digitalWrite(motor2Pin1, LOW);
  digitalWrite(motor2Pin2, HIGH);
  delay(n);
  stop();
}