#include "MAX471.h"

MAX471::MAX471(int voltagePin, int currentPin)
    : _voltagePin(voltagePin), _currentPin(currentPin) {}

void MAX471::begin() {
    pinMode(_voltagePin, INPUT);
    pinMode(_currentPin, INPUT);
    
    Serial.println("✓ MAX471 initialized");
}

float MAX471::getVoltage() {
    int raw = analogRead(_voltagePin);
    return (raw / 4095.0) * 3.3 * VOLTAGE_SCALE;
}

float MAX471::getCurrent() {
    int raw = analogRead(_currentPin);
    return (raw / 4095.0) * 3.3 * CURRENT_SCALE;
}

float MAX471::getPower() {
    return getVoltage() * getCurrent();
}
