#!/usr/bin/env python3
"""
Simulates an ESP32 energy-monitoring device publishing over MQTT.

Publishes the exact same JSON message format the real firmware uses, so the
backend/dashboard cannot tell the difference between a simulated and a real
device. This lets the whole system be demonstrated without any hardware.

Usage:
    python scripts/simulate_device.py --device esp32-energy-01
    python scripts/simulate_device.py --device esp32-energy-01 --host localhost --port 1883
"""
import argparse
import json
import random
import signal
import sys
import time

import paho.mqtt.client as mqtt

BASE_VOLTAGE = 230.0
BASE_CURRENT = 2.2

running = True


def _handle_sigint(signum, frame):
    global running
    running = False


def next_voltage(prev: float) -> float:
    # Small realistic wobble around the mains voltage, not fully random.
    delta = random.uniform(-0.6, 0.6)
    v = prev + delta
    return max(215.0, min(245.0, v))


def next_current(prev: float) -> float:
    # Simulate a household load that drifts slowly, with occasional spikes
    # (e.g. a kettle switching on) so alerts have something to trigger on.
    if random.random() < 0.03:
        delta = random.uniform(3.0, 8.0)  # spike
    else:
        delta = random.uniform(-0.15, 0.15)
    i = prev + delta
    return max(0.1, min(12.0, i))


def main():
    parser = argparse.ArgumentParser(description="Simulate an ESP32 energy monitor over MQTT.")
    parser.add_argument("--device", default="esp32-energy-01", help="Device ID")
    parser.add_argument("--host", default="localhost", help="MQTT broker host")
    parser.add_argument("--port", type=int, default=1883, help="MQTT broker port")
    parser.add_argument("--username", default=None)
    parser.add_argument("--password", default=None)
    parser.add_argument("--interval", type=float, default=5.0, help="Publish interval (s)")
    args = parser.parse_args()

    signal.signal(signal.SIGINT, _handle_sigint)
    signal.signal(signal.SIGTERM, _handle_sigint)

    client = mqtt.Client(
        client_id=f"sim-{args.device}",
        callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
    )
    if args.username:
        client.username_pw_set(args.username, args.password)

    client.connect(args.host, args.port, keepalive=30)
    client.loop_start()

    readings_topic = f"energy/{args.device}/readings"
    status_topic = f"energy/{args.device}/status"

    client.publish(status_topic, json.dumps({"device_id": args.device, "status": "online"}), qos=1, retain=True)
    print(f"[simulator] {args.device} online. Publishing to {readings_topic} every {args.interval}s.")

    voltage = BASE_VOLTAGE
    current = BASE_CURRENT
    session_energy_wh = 0.0

    try:
        while running:
            voltage = next_voltage(voltage)
            current = next_current(current)
            power = voltage * current  # Watts

            # Energy accumulated during this interval, converted to Wh.
            session_energy_wh += power * (args.interval / 3600.0)

            payload = {
                "device_id": args.device,
                "timestamp": int(time.time()),
                "voltage": round(voltage, 2),
                "current": round(current, 2),
                "power": round(power, 2),
                "energy_wh": round(session_energy_wh, 4),
            }
            client.publish(readings_topic, json.dumps(payload), qos=1)
            print(f"[simulator] published: {payload}")

            time.sleep(args.interval)
    finally:
        client.publish(status_topic, json.dumps({"device_id": args.device, "status": "offline"}), qos=1, retain=True)
        client.loop_stop()
        client.disconnect()
        print("\n[simulator] stopped, published offline status.")


if __name__ == "__main__":
    main()
