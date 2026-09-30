/*
 * Smart Energy Monitor - ESP32 firmware entry point.
 *
 * Reads voltage/current (simulated or real, see sensor.cpp), computes
 * power/energy, shows the latest values on an OLED, and publishes JSON
 * readings over MQTT. Everything is scheduled with millis() - there are
 * no blocking delay() calls in the main loop, so WiFi/MQTT reconnects and
 * sensor sampling never freeze the device.
 */
#include <Arduino.h>
#include <WiFi.h>

#include "config.h"
#include "sensor.h"
#include "energy.h"
#include "mqtt.h"
#include "display.h"

Sensor sensor;
EnergyMeter energyMeter;
MqttManager mqttManager;
Display display;

unsigned long lastSensorSampleMs = 0;
unsigned long lastDisplayUpdateMs = 0;
unsigned long lastMqttPublishMs = 0;
unsigned long lastWifiAttemptMs = 0;

SensorReading latestReading = {230.0f, 0.0f};

bool wifiConnectInProgress = false;
unsigned long wifiConnectStartedMs = 0;

// ---------------------------------------------------------------------------
// WiFi: non-blocking connect with timeout + automatic reconnection.
// ---------------------------------------------------------------------------
void startWifiConnect() {
    Serial.println("WiFi connecting...");
    WiFi.mode(WIFI_STA);
    WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
    wifiConnectInProgress = true;
    wifiConnectStartedMs = millis();
}

void handleWifi() {
    if (WiFi.status() == WL_CONNECTED) {
        if (wifiConnectInProgress) {
            wifiConnectInProgress = false;
            Serial.print("WiFi connected. IP: ");
            Serial.println(WiFi.localIP());
        }
        return;
    }

    // Not connected right now.
    if (!wifiConnectInProgress) {
        // Retry periodically rather than hammering WiFi.begin().
        unsigned long now = millis();
        if (now - lastWifiAttemptMs >= 5000UL) {
            lastWifiAttemptMs = now;
            startWifiConnect();
        }
        return;
    }

    // A connection attempt is in progress - check for timeout without blocking.
    if (millis() - wifiConnectStartedMs >= WIFI_CONNECT_TIMEOUT_MS) {
        Serial.println("WiFi connect timed out, will retry.");
        wifiConnectInProgress = false;
        lastWifiAttemptMs = millis();
    }
}

// ---------------------------------------------------------------------------
void setup() {
    Serial.begin(115200);
    delay(200); // brief pause purely for USB-serial enumeration, not logic

    Serial.println();
    Serial.println("=== Smart Energy Monitor booting ===");

    display.begin();
    display.showMessage("SMART ENERGY MONITOR", "Booting...");

    sensor.begin();
    energyMeter.begin();
    mqttManager.begin();

    startWifiConnect();
    lastSensorSampleMs = lastDisplayUpdateMs = lastMqttPublishMs = millis();
}

// ---------------------------------------------------------------------------
void loop() {
    unsigned long now = millis();

    // WiFi + MQTT connectivity are both handled non-blockingly every loop.
    handleWifi();
    mqttManager.loop();

    // --- Sensor sampling (every SENSOR_SAMPLE_INTERVAL_MS) ---
    if (now - lastSensorSampleMs >= SENSOR_SAMPLE_INTERVAL_MS) {
        unsigned long elapsed = now - lastSensorSampleMs;
        lastSensorSampleMs = now;

        Serial.println("Sensor reading...");
        latestReading = sensor.read();
        energyMeter.update(latestReading, elapsed);
    }

    // --- OLED update (every DISPLAY_UPDATE_INTERVAL_MS) ---
    if (now - lastDisplayUpdateMs >= DISPLAY_UPDATE_INTERVAL_MS) {
        lastDisplayUpdateMs = now;
        display.showReadings(
            latestReading.voltage,
            latestReading.current,
            energyMeter.instantaneousPowerW(),
            energyMeter.sessionEnergyWh()
        );
    }

    // --- MQTT publish (every MQTT_PUBLISH_INTERVAL_MS) ---
    if (now - lastMqttPublishMs >= MQTT_PUBLISH_INTERVAL_MS) {
        lastMqttPublishMs = now;
        if (mqttManager.isConnected()) {
            mqttManager.publishReading(
                (unsigned long)(millis() / 1000), // NOTE: use RTC/NTP epoch in production
                latestReading.voltage,
                latestReading.current,
                energyMeter.instantaneousPowerW(),
                energyMeter.sessionEnergyWh()
            );
        } else {
            Serial.println("Skipping publish: MQTT not connected.");
        }
    }
}
