#ifndef MAX471_WRAPPER_H
#define MAX471_WRAPPER_H

#include <Arduino.h>

class MAX471 {
public:
    MAX471(int voltagePin, int currentPin);
    void begin();
    float getVoltage();
    float getCurrent();
    float getPower();
    
private:
    int _voltagePin;
    int _currentPin;
    
    const float VOLTAGE_SCALE = 5.0;
    const float CURRENT_SCALE = 1.0;
};

#endif
