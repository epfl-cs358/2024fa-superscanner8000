#ifndef DISPLAY_H
#define DISPLAY_H

#include <Arduino.h>
#include <LiquidCrystal.h>

class Display
{
private:
    LiquidCrystal lcd;
    byte fullBlock[8] = {
        0b11111,
        0b11111,
        0b11111,
        0b11111,
        0b11111,
        0b11111,
        0b11111,
        0b11111
    };
    float ms;
    int scrollIndex;
    int contrast;
    int backlight;
    String text1;
    String text2;
public:
    Display(int rs, int en, int d4, int d5, int d6, int d7, int contrast, int backlight);
    void print(String text);
    void printProgressBar(String text, int percentage);
    void scroll(String text1, String text2);
    void clear();
    void setup();
    void update();
};

#endif
