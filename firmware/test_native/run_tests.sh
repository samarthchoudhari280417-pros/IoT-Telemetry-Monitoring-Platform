#!/usr/bin/env bash
# Compiles and runs the native (non-hardware) unit tests for the firmware's
# core power/energy calculation logic.
set -e
cd "$(dirname "$0")"
g++ -std=c++17 -I shim -I ../src -o /tmp/test_energy ../test/test_energy.cpp
/tmp/test_energy
