/*
 * Native unit tests for the core embedded calculation logic (power/energy),
 * compiled with a plain g++ (see firmware/test_native/run_tests.sh) using a
 * minimal Arduino.h shim - no ESP32 hardware or PlatformIO test runner
 * required to check the math is right.
 */
#include <cassert>
#include <cmath>
#include <cstdio>

#include "../src/energy.h"
#include "../src/energy.cpp"

static bool approxEqual(double a, double b, double eps = 1e-6) {
    return std::fabs(a - b) < eps;
}

void test_power_is_voltage_times_current() {
    EnergyMeter meter;
    meter.begin();

    SensorReading r{230.0f, 2.0f};
    float power = meter.update(r, 0); // 0 ms elapsed -> no energy accumulation yet

    assert(approxEqual(power, 460.0, 1e-3));
    printf("PASS test_power_is_voltage_times_current\n");
}

void test_energy_accumulates_over_time() {
    EnergyMeter meter;
    meter.begin();

    SensorReading r{230.0f, 2.0f}; // 460 W
    // 1 hour elapsed (3,600,000 ms) -> Energy = Power * Time = 460 Wh
    meter.update(r, 3600000UL);

    assert(approxEqual(meter.sessionEnergyWh(), 460.0, 1e-2));
    assert(approxEqual(meter.todayEnergyWh(), 460.0, 1e-2));
    printf("PASS test_energy_accumulates_over_time\n");
}

void test_energy_accumulates_across_multiple_samples() {
    EnergyMeter meter;
    meter.begin();

    SensorReading r{230.0f, 2.0f}; // 460 W
    // 5 samples of 1 second each = 5 seconds total
    for (int i = 0; i < 5; i++) {
        meter.update(r, 1000UL);
    }
    // Expected: 460 W * (5/3600) h = 0.63888... Wh
    double expected = 460.0 * (5.0 / 3600.0);
    assert(approxEqual(meter.sessionEnergyWh(), expected, 1e-3));
    printf("PASS test_energy_accumulates_across_multiple_samples\n");
}

void test_daily_reset_does_not_affect_session_total() {
    EnergyMeter meter;
    meter.begin();

    SensorReading r{230.0f, 2.0f};
    meter.update(r, 3600000UL); // 460 Wh

    meter.resetDaily();

    assert(approxEqual(meter.todayEnergyWh(), 0.0, 1e-6));
    assert(approxEqual(meter.sessionEnergyWh(), 460.0, 1e-2)); // unaffected
    printf("PASS test_daily_reset_does_not_affect_session_total\n");
}

void test_zero_current_means_zero_power_and_energy() {
    EnergyMeter meter;
    meter.begin();

    SensorReading r{230.0f, 0.0f};
    float power = meter.update(r, 3600000UL);

    assert(approxEqual(power, 0.0, 1e-6));
    assert(approxEqual(meter.sessionEnergyWh(), 0.0, 1e-6));
    printf("PASS test_zero_current_means_zero_power_and_energy\n");
}

int main() {
    test_power_is_voltage_times_current();
    test_energy_accumulates_over_time();
    test_energy_accumulates_across_multiple_samples();
    test_daily_reset_does_not_affect_session_total();
    test_zero_current_means_zero_power_and_energy();
    printf("\nAll firmware calculation tests passed.\n");
    return 0;
}
