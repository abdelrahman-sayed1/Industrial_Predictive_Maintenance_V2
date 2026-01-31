#ifndef ENCODER_CUSTOM_H
#define ENCODER_CUSTOM_H

#include <Arduino.h>

class Encoder_Custom {
private:
    uint8_t pinA;
    uint8_t pinB;
    volatile long position;
    volatile long lastPosition;
    unsigned long lastTime;
    float rpm;
    
public:
    Encoder_Custom(uint8_t pinA, uint8_t pinB);
    
    void begin();
    void update();
    
    long getPosition();
    float getRPM();
    void reset();
    
    // Interrupt handlers
    void handleInterruptA();
    void handleInterruptB();
    
private:
    static Encoder_Custom* instanceA;
    static Encoder_Custom* instanceB;
    
    static void isrA();
    static void isrB();
    
    // Configuration
    static const unsigned long RPM_UPDATE_INTERVAL = 100; // ms
    static const int PULSES_PER_REVOLUTION = 360; // Adjust based on your encoder
};

#endif
