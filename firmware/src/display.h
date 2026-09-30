#pragma once
#include <Arduino.h>

/*
 * display.h - OLED (SSD1306) output. Keeps the UI simple and readable:
 * shows the latest voltage, current, power, and session energy.
 */
class Display {
public:
    // Returns false if the display was not found on the I2C bus (firmware
    // continues running headless in that case - never blocks on this).
    bool begin();

    void showReadings(float voltage, float current, float power, float energyWh);
    void showMessage(const char *line1, const char *line2 = nullptr);

private:
    bool _available = false;
};
