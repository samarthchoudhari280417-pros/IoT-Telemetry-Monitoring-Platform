#pragma once
// Minimal Arduino.h shim so core calculation logic (sensor.h/energy.h) can
// be compiled and unit-tested natively on a desktop, without the ESP32
// toolchain. Only the handful of symbols actually used are stubbed out.
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>

inline unsigned long millis() { return 0; }
inline void delay(unsigned long) {}
inline void randomSeed(long) {}
inline long random(long lo, long hi) { return lo + (hi > lo ? (rand() % (hi - lo)) : 0); }
inline int analogRead(int) { return 0; }

struct SerialClass {
    void begin(long) {}
    void print(const char *s) { fputs(s, stdout); }
    void println(const char *s) { puts(s); }
    void println() { puts(""); }
    void print(int v) { printf("%d", v); }
    void println(int v) { printf("%d\n", v); }
};
inline SerialClass Serial;
