#pragma once
#include <Arduino.h>

/*
 * sensor.h - abstraction over the voltage/current sensor.
 *
 * In SENSOR_MODE_SIMULATED (see config.h), readings are generated with
 * small realistic variations around typical mains values, so the whole
 * system can be developed and demoed with no electrical hardware at all.
 *
 * For real hardware: replace the body of Sensor::read() in sensor.cpp with
 * calls into your current-sensing module's driver (e.g. an ADC read from a
 * non-invasive CT clamp + a calibrated voltage reference). Do NOT connect
 * the ESP32 directly to mains - use an appropriately isolated module and
 * have the electrical wiring done by someone qualified to do so safely.
 */

struct SensorReading {
    float voltage;  // Volts (RMS)
    float current;  // Amps (RMS)
};

class Sensor {
public:
    void begin();

    // Returns the latest voltage/current reading.
    SensorReading read();

private:
    float lastVoltage = 230.0f;
    float lastCurrent = 2.2f;
};
