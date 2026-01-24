#ifndef ENCODER_WRAPPER_H
#define ENCODER_WRAPPER_H

#include <Arduino.h>

class Encoder {
public:
    Encoder(int pinA, int pinB);
    void begin();
    float getRPM();
    long getPosition();
    
private:
    int _pinA, _pinB;
    volatile long _position;
    volatile unsigned long _lastTime;
    volatile unsigned long _pulseCount;
    
    static void IRAM_ATTR handleInterruptA();
    static Encoder* _instance;
};

#endif
