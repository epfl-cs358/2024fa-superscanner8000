#include "display.h"

Display::Display(int rs, int en, int d4, int d5, int d6, int d7, int contrast, int backlight)
{
    lcd = LiquidCrystal(rs, en, d4, d5, d6, d7);
}

Display::setup()
{
    //set some defaults
    analogWrite(LCD_BACKLIGHT_PIN, 255); //set backlight on
    analogWrite(LCD_CONTRAST_PIN, 100); //set some contrast

    lcd.begin(16, 2);
    lcd.clear();
}

Display::print(String text)
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

Display::scroll(String txt1, String txt2)
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

Display::clear()
{
    text1 = "";
    text2 = "";
    lcd.clear();
}

Display::update()
{
    if (millis() - ms > 250 && text1 != "" && text2 != "")
    {
        lcd.clear();
        lcd.print(text1.substring(scrollIndex, scrollIndex + 16));
        lcd.setCursor(0, 1);
        lcd.print(text2.substring(scrollIndex, scrollIndex + 16));
        scrollIndex++;
        if (scrollIndex >= text1.length() && scrollIndex >= text2.length() && scrollIndex % 16 == 0)
        {
            scrollIndex = 0;
        }
        ms = millis();
    }
}
