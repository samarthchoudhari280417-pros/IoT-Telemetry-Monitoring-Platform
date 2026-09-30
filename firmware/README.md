# Firmware - ESP32 Smart Energy Monitor

C++ / Arduino-framework firmware built with [PlatformIO](https://platformio.org/).

## Structure

```
firmware/
├── src/
│   ├── main.cpp      # setup()/loop(), non-blocking scheduling
│   ├── config.h       # WiFi/MQTT/device credentials & timing constants
│   ├── sensor.{h,cpp}  # voltage/current abstraction (simulated or real)
│   ├── energy.{h,cpp}  # P = V x I, Energy (Wh) = P x time
│   ├── mqtt.{h,cpp}    # WiFi/MQTT connectivity, JSON publish
│   └── display.{h,cpp} # SSD1306 OLED output
├── test/               # native (non-hardware) unit tests for energy.cpp
├── test_native/         # shim + script to run test/ with plain g++
└── platformio.ini
```

## Building & flashing (real hardware)

1. Install [PlatformIO](https://platformio.org/install) (VS Code extension or CLI).
2. Edit `src/config.h`: set `WIFI_SSID`, `WIFI_PASSWORD`, `MQTT_HOST`, `MQTT_PORT`, `DEVICE_ID`.
   **Never commit real credentials** — treat `config.h` like a secret once filled in.
3. Wire up an SSD1306 OLED over I2C (SDA/SCL to the ESP32's default I2C pins).
4. `pio run -t upload` to flash, `pio device monitor` to view Serial logs.

## Sensor modes

- **`SENSOR_MODE_SIMULATED=1`** (default, set in `platformio.ini`): generates
  realistic voltage/current values with small variations. No electrical
  wiring needed at all — useful for development, demos, and testing the OLED/
  MQTT/backend pipeline safely.
- **Real hardware**: set `SENSOR_MODE_SIMULATED=0` and implement `Sensor::read()`
  in `sensor.cpp` against your current-sensing hardware. **Do not wire the
  ESP32 directly to mains electricity.** Use an appropriately isolated
  current-sensing module (e.g. a non-invasive clamp-on CT sensor) and a
  calibrated voltage reference, and have the mains-side wiring done by
  someone qualified to do it safely.

## Running the native unit tests (no ESP32 required)

```bash
cd firmware/test_native
./run_tests.sh
```

This compiles `test/test_energy.cpp` against the real `energy.cpp`/`energy.h`
using a minimal `Arduino.h` shim, and checks the P = V×I and Wh accumulation
math directly.

## MQTT message format

Published to `energy/{device_id}/readings` every `MQTT_PUBLISH_INTERVAL_MS`
(default 5s):

```json
{
  "device_id": "esp32-energy-01",
  "timestamp": 1720000000,
  "voltage": 230.2,
  "current": 2.31,
  "power": 531.76,
  "energy_wh": 1.42
}
```

Status (retained, with Last-Will-and-Testament) published to
`energy/{device_id}/status`:

```json
{ "device_id": "esp32-energy-01", "status": "online" }
```

## Note on timestamps

`main.cpp` currently derives the published timestamp from `millis()/1000` as
a placeholder. For production use, sync the ESP32's clock via NTP
(`configTime()` + `time()`) after WiFi connects, and publish the real Unix
epoch instead — the backend expects seconds since epoch.
