#include "Encoder.h"

Encoder* Encoder::_instance = nullptr;

Encoder::Encoder(int pinA, int pinB)
    : _pinA(pinA), _pinB(pinB), _position(0), _lastTime(0), _pulseCount(0) {
    _instance = this;
}

void Encoder::begin() {
    pinMode(_pinA, INPUT_PULLUP);
    pinMode(_pinB, INPUT_PULLUP);
    
    attachInterrupt(digitalPinToInterrupt(_pinA), handleInterruptA, RISING);
    
    Serial.println("✓ Encoder initialized");
}

void IRAM_ATTR Encoder::handleInterruptA() {
    if (_instance) {
        _instance->_position++;
        _instance->_pulseCount++;
    }
}

float Encoder::getRPM() {
    unsigned long currentTime = millis();
    unsigned long deltaTime = currentTime - _lastTime;
    
    if (deltaTime >= 1000) {
        float rpm = (_pulseCount * 60.0) / (deltaTime / 1000.0);
        _pulseCount = 0;
        _lastTime = currentTime;
        return rpm;
    }
    return 0.0;
}

long Encoder::getPosition() {
    return _position;
}
