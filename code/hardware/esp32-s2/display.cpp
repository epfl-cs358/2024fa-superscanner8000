#include "HardwareSerial.h"
#include "display.h"
#include <LiquidCrystal.h>

Display::Display(int rs, int en, int d4, int d5, int d6, int d7, int contrast, int backlight)
    :   lcd(rs, en, d4, d5, d6, d7),
        ms(0),
        scrollIndex(0),
        text1(""),
        text2(""),
        contrast(contrast),
        backlight(backlight)
  {}

void Display::setup()
{
    //set some defaults
    analogWrite(contrast, 40);
    analogWrite(backlight, 255);

    lcd.begin(16, 2);
    lcd.clear();
}

void Display::print(String text)
{
    text1 = "";
    text2 = "";
    lcd.clear();
    if (text.length() < 16)
    {
        lcd.print(text.substring(0, 16));
    }
    else if (text.length() < 32)
    {
        lcd.print(text.substring(0, 16));
        lcd.setCursor(0, 1);
        lcd.print(text.substring(16, 32));
    } else
    {
        scroll(text, "");
    }
}

void Display::scroll(String txt1, String txt2)
{
    lcd.clear();
    text1 = txt1;
    text2 = txt2;
    scrollIndex = 0;

    lcd.print(text1.substring(scrollIndex, scrollIndex + 16));
    lcd.setCursor(0, 1);
    lcd.print(text2.substring(scrollIndex, scrollIndex + 16));
    scrollIndex++;
    ms = millis();
}

void Display::clear()
{
    text1 = "";
    text2 = "";
    lcd.clear();
}

void Display::update()
{
    if (millis() - ms > 500 && (text1 != "" || text2 != ""))
    {
        lcd.clear();
        lcd.setCursor(0, 0);
        lcd.print(text1.substring(scrollIndex, scrollIndex + 16));
        lcd.setCursor(0, 1);
        lcd.print(text2.substring(scrollIndex, scrollIndex + 16));
        scrollIndex++;
        if (scrollIndex >= (text1.length()) && scrollIndex >= (text2.length()))
        {
            scrollIndex = 0;
        }
        ms = millis();
    }
}
