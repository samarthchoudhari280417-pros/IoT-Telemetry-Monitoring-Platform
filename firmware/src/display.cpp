#include "display.h"
#include "config.h"
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

static Adafruit_SSD1306 oled(OLED_WIDTH, OLED_HEIGHT, &Wire, OLED_RESET_PIN);

bool Display::begin() {
    Wire.begin();
    _available = oled.begin(SSD1306_SWITCHCAPVCC, OLED_I2C_ADDRESS);
    if (!_available) {
        Serial.println("[display] SSD1306 not found - continuing without OLED.");
        return false;
    }
    oled.clearDisplay();
    oled.setTextColor(SSD1306_WHITE);
    oled.setTextSize(1);
    oled.setCursor(0, 0);
    oled.println("SMART ENERGY MONITOR");
    oled.println("Starting...");
    oled.display();
    return true;
}

void Display::showReadings(float voltage, float current, float power, float energyWh) {
    if (!_available) return;

    oled.clearDisplay();
    oled.setCursor(0, 0);
    oled.setTextSize(1);
    oled.println("SMART ENERGY MONITOR");
    oled.println();

    oled.print("Voltage: ");
    oled.print(voltage, 1);
    oled.println(" V");

    oled.print("Current: ");
    oled.print(current, 2);
    oled.println(" A");

    oled.print("Power:   ");
    oled.print(power, 1);
    oled.println(" W");

    oled.print("Energy:  ");
    oled.print(energyWh, 2);
    oled.println(" Wh");

    oled.display();
}

void Display::showMessage(const char *line1, const char *line2) {
    if (!_available) return;

    oled.clearDisplay();
    oled.setCursor(0, 0);
    oled.setTextSize(1);
    oled.println(line1);
    if (line2) {
        oled.println(line2);
    }
    oled.display();
}
