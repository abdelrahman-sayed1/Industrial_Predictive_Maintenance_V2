#include "DRV8825.h"

DRV8825::DRV8825(int stepPin, int dirPin, int enablePin, int faultPin)
    : _stepPin(stepPin), _dirPin(dirPin),
      _enablePin(enablePin), _faultPin(faultPin) {}

void DRV8825::begin() {
    pinMode(_stepPin, OUTPUT);
    pinMode(_dirPin, OUTPUT);
    pinMode(_enablePin, OUTPUT);
    pinMode(_faultPin, INPUT_PULLUP);
    
    disable();
    Serial.println("✓ DRV8825 initialized");
}

void DRV8825::enable() {
    digitalWrite(_enablePin, LOW);
}

void DRV8825::disable() {
    digitalWrite(_enablePin, HIGH);
}

bool DRV8825::isFault() {
    return digitalRead(_faultPin) == LOW;
}

void DRV8825::setDirection(bool clockwise) {
    digitalWrite(_dirPin, clockwise ? HIGH : LOW);
}

void DRV8825::step() {
    digitalWrite(_stepPin, HIGH);
    delayMicroseconds(2);
    digitalWrite(_stepPin, LOW);
    delayMicroseconds(2);
}

void DRV8825::rotate(int steps, int delayMicros) {
    for (int i = 0; i < steps; i++) {
        step();
        delayMicroseconds(delayMicros);
    }
}
