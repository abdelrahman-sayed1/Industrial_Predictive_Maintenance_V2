#ifndef DRV8825_H
#define DRV8825_H

#include <Arduino.h>

class DRV8825 {
private:
    int _stepPin;
    int _dirPin;
    int _enablePin;
    int _faultPin;
    bool motorRunning;  // Add motorRunning variable

public:
    DRV8825(int stepPin, int dirPin, int enablePin, int faultPin);
    
    void begin();
    void enable();
    void disable();
    void setDirection(bool clockwise);
    void step();
    void runMotor();  // New method for continuous running
    bool isFault();
};

#endif
