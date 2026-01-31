#ifndef MAX471_CUSTOM_H
#define MAX471_CUSTOM_H

#include <Arduino.h>

class MAX471_Custom {
private:
    uint8_t voltagePin;
    uint8_t currentPin;
    
    // Calibration constants
    float voltageScale;
    float currentScale;
    
public:
    MAX471_Custom(uint8_t voltagePin, uint8_t currentPin);
    
    void begin();
    void calibrate();
    
    float getVoltage();
    float getCurrent();
    float getPower();
    
    void setVoltageScale(float scale);
    void setCurrentScale(float scale);
    
private:
    float readAnalogAverage(uint8_t pin, int samples = 10);
    
    // ADC reference voltage (typically 3.3V for ESP32)
    static const float ADC_REF_VOLTAGE;
    static const float MAX471_SENSITIVITY; // 1V per Amp
};

#endif
