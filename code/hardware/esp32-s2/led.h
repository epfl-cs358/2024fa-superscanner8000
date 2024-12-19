#ifndef LED_H
#define LED_H

#include <Arduino.h>
#include <FastLED.h>

class Led {
private:
    CRGB *leds;
    uint8_t hue = 0;
    uint8_t hue1 = 0;
    int r, g, b = 0;
    bool _rainbowMode = false;
    int duration = -1;
    int start = millis();
public:
    const int numLeds;
    bool rainbowMode = false;
    Led(int _numLeds);
    void setup();
    void setAll(int r, int g, int b);
    void flash(int r, int g, int b, int duration);
    void update();
    void show();
};


#endif // LED_H
