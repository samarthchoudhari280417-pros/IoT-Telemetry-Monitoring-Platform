#pragma once
#include "sensor.h"

/*
 * energy.h - power/energy calculations.
 *
 * Power (W)     = Voltage (V) x Current (A)
 * Energy (Wh)   = Power (W) x Time (h), accumulated across samples
 */
class EnergyMeter {
public:
    void begin();

    // Feed a new sensor reading and elapsed time (ms) since the previous
    // sample; updates internal accumulators and returns instantaneous power.
    float update(const SensorReading &reading, unsigned long elapsedMs);

    float instantaneousPowerW() const { return _powerW; }
    float sessionEnergyWh() const { return _sessionEnergyWh; }
    float todayEnergyWh() const { return _todayEnergyWh; }

    // Call once every 24h (or on manual reset) to roll the daily counter.
    void resetDaily();

private:
    float _powerW = 0.0f;
    double _sessionEnergyWh = 0.0;
    double _todayEnergyWh = 0.0;
};
