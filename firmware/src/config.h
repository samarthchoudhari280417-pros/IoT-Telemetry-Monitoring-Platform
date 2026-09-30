#pragma once
/*
 * config.h - central configuration for the Smart Energy Monitor firmware.
 *
 * IMPORTANT: never commit real credentials. Copy this file, fill in your
 * own values, and keep the real one out of version control (see
 * firmware/.gitignore-equivalent guidance in the README).
 */

// ---------------------------------------------------------------------------
// Device identity
// ---------------------------------------------------------------------------
#define DEVICE_ID "esp32-energy-01"

// ---------------------------------------------------------------------------
// Wi-Fi
// ---------------------------------------------------------------------------
#define WIFI_SSID "YOUR_WIFI_SSID"
#define WIFI_PASSWORD "YOUR_WIFI_PASSWORD"
#define WIFI_CONNECT_TIMEOUT_MS 15000UL

// ---------------------------------------------------------------------------
// MQTT
// ---------------------------------------------------------------------------
#define MQTT_HOST "192.168.1.100"
#define MQTT_PORT 1883
#define MQTT_USERNAME ""   // leave empty if broker allows anonymous access
#define MQTT_PASSWORD ""

// Topics (device id is interpolated at runtime, see mqtt.cpp)
#define MQTT_TOPIC_READINGS_FMT "energy/%s/readings"
#define MQTT_TOPIC_STATUS_FMT   "energy/%s/status"

#define MQTT_RECONNECT_INTERVAL_MS 5000UL

// ---------------------------------------------------------------------------
// Sensor mode
// ---------------------------------------------------------------------------
// SENSOR_MODE_SIMULATED is set via platformio.ini build_flags.
// 1 = generate realistic simulated readings (SAFE, no mains wiring needed)
// 0 = read from a real current/voltage sensor (see sensor.cpp for the
//     integration point; requires an appropriately isolated sensing module,
//     e.g. a non-invasive current transformer + a calibrated voltage
//     reference, wired by someone qualified to work with mains electricity).
#ifndef SENSOR_MODE_SIMULATED
#define SENSOR_MODE_SIMULATED 1
#endif

// ---------------------------------------------------------------------------
// Timing (all non-blocking, millis()-based - see main.cpp)
// ---------------------------------------------------------------------------
#define SENSOR_SAMPLE_INTERVAL_MS 1000UL
#define DISPLAY_UPDATE_INTERVAL_MS 1000UL
#define MQTT_PUBLISH_INTERVAL_MS 5000UL

// ---------------------------------------------------------------------------
// OLED display (SSD1306 over I2C)
// ---------------------------------------------------------------------------
#define OLED_WIDTH 128
#define OLED_HEIGHT 64
#define OLED_RESET_PIN -1
#define OLED_I2C_ADDRESS 0x3C
