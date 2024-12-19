#ifndef LED_H
#define LED_H

#include <Arduino.h>
#include <FastLED.h>

class Led {
private:
    CRGB *leds;
    uint8_t hue = 0;
    uint8_t hue1 = 0;
public:
    const int numLeds;
    bool rainbowMode = false;
    Led(int _numLeds);
    void setup();
    void setColor(int index, int r, int g, int b);
    void setAll(int r, int g, int b);
    void update();
    void show();
};


#endif // LED_H
