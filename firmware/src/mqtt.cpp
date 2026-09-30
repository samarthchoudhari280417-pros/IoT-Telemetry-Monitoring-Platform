#include "mqtt.h"
#include "config.h"
#include <ArduinoJson.h>

void MqttManager::begin() {
    snprintf(_readingsTopic, sizeof(_readingsTopic), MQTT_TOPIC_READINGS_FMT, DEVICE_ID);
    snprintf(_statusTopic, sizeof(_statusTopic), MQTT_TOPIC_STATUS_FMT, DEVICE_ID);

    _mqttClient.setClient(_wifiClient);
    _mqttClient.setServer(MQTT_HOST, MQTT_PORT);
    _mqttClient.setBufferSize(384); // JSON payloads are small but give headroom
}

bool MqttManager::isConnected() {
    return _mqttClient.connected();
}

void MqttManager::tryConnect() {
    if (WiFi.status() != WL_CONNECTED) {
        return; // wait for WiFi manager to reconnect first
    }

    Serial.println("MQTT connecting...");

    bool ok;
    // Last-Will-and-Testament: broker publishes "offline" for us if we
    // disconnect unexpectedly (crash, power loss, etc.)
    StaticJsonDocument<128> lwt;
    lwt["device_id"] = DEVICE_ID;
    lwt["status"] = "offline";
    char lwtPayload[128];
    size_t n = serializeJson(lwt, lwtPayload);

    if (strlen(MQTT_USERNAME) > 0) {
        ok = _mqttClient.connect(DEVICE_ID, MQTT_USERNAME, MQTT_PASSWORD,
                                  _statusTopic, 1, true, lwtPayload, true);
    } else {
        ok = _mqttClient.connect(DEVICE_ID, nullptr, nullptr,
                                  _statusTopic, 1, true, lwtPayload, true);
    }

    if (ok) {
        Serial.println("MQTT connected.");
        publishStatus("online");
    } else {
        Serial.print("MQTT connect failed, rc=");
        Serial.println(_mqttClient.state());
    }
}

bool MqttManager::loop() {
    if (!_mqttClient.connected()) {
        unsigned long now = millis();
        // Non-blocking retry: only attempt reconnect every
        // MQTT_RECONNECT_INTERVAL_MS, never in a tight loop.
        if (now - _lastReconnectAttempt >= MQTT_RECONNECT_INTERVAL_MS) {
            _lastReconnectAttempt = now;
            tryConnect();
        }
        return false;
    }

    _mqttClient.loop();
    return true;
}

bool MqttManager::publishReading(unsigned long epochSeconds, float voltage, float current,
                                  float power, float energyWh) {
    if (!_mqttClient.connected()) return false;

    StaticJsonDocument<256> doc;
    doc["device_id"] = DEVICE_ID;
    doc["timestamp"] = epochSeconds;
    doc["voltage"] = voltage;
    doc["current"] = current;
    doc["power"] = power;
    doc["energy_wh"] = energyWh;

    char payload[256];
    size_t len = serializeJson(doc, payload);

    Serial.println("Publishing reading...");
    bool ok = _mqttClient.publish(_readingsTopic, payload, len);
    if (ok) {
        Serial.println("Reading published.");
    } else {
        Serial.println("Publish failed.");
    }
    return ok;
}

bool MqttManager::publishStatus(const char *status) {
    if (!_mqttClient.connected()) return false;

    StaticJsonDocument<128> doc;
    doc["device_id"] = DEVICE_ID;
    doc["status"] = status;

    char payload[128];
    size_t len = serializeJson(doc, payload);

    // retain=true so late-joining subscribers immediately know device status
    return _mqttClient.publish(_statusTopic, (const uint8_t *)payload, len, true);
}
