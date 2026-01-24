#ifndef DRV8825_WRAPPER_H
#define DRV8825_WRAPPER_H

#include <Arduino.h>

class DRV8825 {
public:
    DRV8825(int stepPin, int dirPin, int enablePin, int faultPin);
    void begin();
    void enable();
    void disable();
    bool isFault();
    void setDirection(bool clockwise);
    void step();
    void rotate(int steps, int delayMicros = 1000);
    
private:
    int _stepPin;
    int _dirPin;
    int _enablePin;
    int _faultPin;
};

#endif
