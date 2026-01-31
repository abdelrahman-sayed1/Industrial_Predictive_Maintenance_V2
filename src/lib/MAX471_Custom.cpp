#include "MAX471_Custom.h"

const float MAX471_Custom::ADC_REF_VOLTAGE = 3.3;
const float MAX471_Custom::MAX471_SENSITIVITY = 1.0; // 1V per Amp

MAX471_Custom::MAX471_Custom(uint8_t voltagePin, uint8_t currentPin) 
    : voltagePin(voltagePin), currentPin(currentPin), voltageScale(1.0), currentScale(1.0) {
}

void MAX471_Custom::begin() {
    pinMode(voltagePin, INPUT);
    pinMode(currentPin, INPUT);
    
    // Default calibration for typical setup
    voltageScale = (ADC_REF_VOLTAGE * 2.0) / 4096.0; // Assuming voltage divider
    currentScale = (ADC_REF_VOLTAGE / 4096.0) / MAX471_SENSITIVITY;
}

void MAX471_Custom::calibrate() {
    // Simple calibration - can be enhanced with actual calibration procedure
    voltageScale = (ADC_REF_VOLTAGE * 2.0) / 4096.0; // Assuming 2:1 voltage divider
    currentScale = (ADC_REF_VOLTAGE / 4096.0) / MAX471_SENSITIVITY;
}

float MAX471_Custom::getVoltage() {
    float adcValue = readAnalogAverage(voltagePin);
    return adcValue * voltageScale;
}

float MAX471_Custom::getCurrent() {
    float adcValue = readAnalogAverage(currentPin);
    return adcValue * currentScale;
}

float MAX471_Custom::getPower() {
    return getVoltage() * getCurrent();
}

void MAX471_Custom::setVoltageScale(float scale) {
    voltageScale = scale;
}

void MAX471_Custom::setCurrentScale(float scale) {
    currentScale = scale;
}

float MAX471_Custom::readAnalogAverage(uint8_t pin, int samples) {
    float sum = 0.0;
    for (int i = 0; i < samples; i++) {
        sum += analogRead(pin);
        delay(1); // Small delay between readings
    }
    return sum / samples;
}
