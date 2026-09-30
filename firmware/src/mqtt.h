#pragma once
#include <Arduino.h>
#include <WiFi.h>
#include <PubSubClient.h>

/*
 * mqtt.h - MQTT connectivity: non-blocking connect/reconnect + JSON publish.
 *
 * Publishes to:
 *   energy/{device_id}/readings  - periodic measurement payloads
 *   energy/{device_id}/status    - "online"/"offline" (retained, LWT)
 */
class MqttManager {
public:
    void begin();

    // Call every loop() iteration. Handles the PubSubClient loop and
    // non-blocking reconnect attempts. Returns true if currently connected.
    bool loop();

    bool isConnected();

    // Publish a reading as JSON: {device_id, timestamp, voltage, current, power, energy_wh}
    bool publishReading(unsigned long epochSeconds, float voltage, float current,
                         float power, float energyWh);

    bool publishStatus(const char *status);

private:
    WiFiClient _wifiClient;
    PubSubClient _mqttClient;

    char _readingsTopic[64];
    char _statusTopic[64];

    unsigned long _lastReconnectAttempt = 0;

    void tryConnect();
};
