#include "energy.h"

void EnergyMeter::begin() {
    _powerW = 0.0f;
    _sessionEnergyWh = 0.0;
    _todayEnergyWh = 0.0;
}

float EnergyMeter::update(const SensorReading &reading, unsigned long elapsedMs) {
    // P = V x I
    _powerW = reading.voltage * reading.current;

    // Energy (Wh) = Power (W) x Time (h)
    double elapsedHours = elapsedMs / 3600000.0; // ms -> h
    double deltaWh = _powerW * elapsedHours;

    _sessionEnergyWh += deltaWh;
    _todayEnergyWh += deltaWh;

    return _powerW;
}

void EnergyMeter::resetDaily() {
    _todayEnergyWh = 0.0;
}
