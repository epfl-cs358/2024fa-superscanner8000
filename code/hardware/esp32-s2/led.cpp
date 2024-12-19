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

void Led::setColor(int index, int r, int g, int b) {
    rainbowMode = false;
    leds[index] = CRGB(r, g, b);
}

void Led::setAll(int r, int g, int b) {
    rainbowMode = false;
    for (int i = 0; i < numLeds; i++) {
        leds[i] = CRGB(r, g, b);
    }
}

void Led::show() {
    FastLED.show();
}

void Led::update() {
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

