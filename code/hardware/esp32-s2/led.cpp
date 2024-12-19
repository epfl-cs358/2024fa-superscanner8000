#include <iterator>
#include <Arduino.h>
#include <FastLed.h>
#include "led.h"

#define DATA_PIN 17

Led::Led(int _numLeds) :
  numLeds(_numLeds) 
    {
    leds = new CRGB[numLeds];
}

void Led::setup() {
    FastLED.addLeds<WS2812, DATA_PIN, GRB>(leds, numLeds);
}

void Led::setAll(int _r, int _g, int _b) {
    rainbowMode = false;
    r = _r;
    g = _g;
    b = _b;
    for (int i = 0; i < numLeds; i++) {
        leds[i] = CRGB(r, g, b);
    }
}

void Led::flash(int _r, int _g, int _b, int _duration) {
    for (int i = 0; i < numLeds; i++) {
        leds[i] = CRGB(_r, _g, _b);
    }
    duration = _duration;
    start = millis();
    _rainbowMode = rainbowMode;
    rainbowMode = false;
    show();
}

void Led::show() {
    FastLED.show();
}

void Led::update() {
    if (duration != -1) {
        if (millis() - start > duration) {
            duration = -1;
            if (_rainbowMode) {
                rainbowMode = true;
            } else {
                setAll(r, g, b);
                show();
            }
        }
    }
    if (rainbowMode) {
        for (int i = 0; i < numLeds; i++) {
            leds[i] = CHSV(hue + i * 10, 255, 255);
        }
        hue1 ++;
        if (hue1 % 10 == 0) {
            hue ++;
        }
        show();
    }
}

