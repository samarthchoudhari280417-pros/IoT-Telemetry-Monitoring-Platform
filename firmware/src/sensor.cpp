#include "sensor.h"
#include "config.h"

void Sensor::begin() {
#if SENSOR_MODE_SIMULATED
    randomSeed(analogRead(0));
    Serial.println("[sensor] Running in SIMULATED mode (no hardware required).");
#else
    // TODO: initialize your real current/voltage sensing hardware here
    // (e.g. begin ADC, configure the current-transformer driver, etc.)
    Serial.println("[sensor] Running in HARDWARE mode.");
#endif
}

#if SENSOR_MODE_SIMULATED

static float bounded(float value, float lo, float hi) {
    if (value < lo) return lo;
    if (value > hi) return hi;
    return value;
}

// Generates a small, realistic drift around the previous value rather than
// fully random noise, so plotted values look like a real load.
static float nextValue(float previous, float maxStep, float lo, float hi) {
    float step = ((float)random(-1000, 1000) / 1000.0f) * maxStep;
    return bounded(previous + step, lo, hi);
}

SensorReading Sensor::read() {
    lastVoltage = nextValue(lastVoltage, 0.6f, 215.0f, 245.0f);

    // Occasionally simulate a load spike (e.g. an appliance switching on).
    float maxCurrentStep = (random(0, 100) < 3) ? 4.0f : 0.15f;
    lastCurrent = nextValue(lastCurrent, maxCurrentStep, 0.1f, 12.0f);

    SensorReading r;
    r.voltage = lastVoltage;
    r.current = lastCurrent;
    return r;
}

#else

SensorReading Sensor::read() {
    // TODO: replace with real ADC reads from your sensor module, converted
    // to RMS voltage/current. Keep the same struct shape so the rest of the
    // firmware (energy calculation, MQTT, display) needs no changes.
    SensorReading r;
    r.voltage = 0.0f;
    r.current = 0.0f;
    return r;
}

#endif
