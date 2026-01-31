#include "Encoder_Custom.h"

// Static member initialization
Encoder_Custom* Encoder_Custom::instanceA = nullptr;
Encoder_Custom* Encoder_Custom::instanceB = nullptr;

Encoder_Custom::Encoder_Custom(uint8_t pinA, uint8_t pinB) 
    : pinA(pinA), pinB(pinB), position(0), lastPosition(0), lastTime(0), rpm(0.0) {
}

void Encoder_Custom::begin() {
    pinMode(pinA, INPUT_PULLUP);
    pinMode(pinB, INPUT_PULLUP);
    
    // Set up interrupts
    instanceA = this;
    attachInterrupt(digitalPinToInterrupt(pinA), isrA, CHANGE);
    attachInterrupt(digitalPinToInterrupt(pinB), isrB, CHANGE);
    
    lastTime = millis();
}

long Encoder_Custom::getPosition() {
    noInterrupts();
    long pos = position;
    interrupts();
    return pos;
}

float Encoder_Custom::getRPM() {
    update();
    return rpm;
}

void Encoder_Custom::reset() {
    noInterrupts();
    position = 0;
    lastPosition = 0;
    rpm = 0.0;
    interrupts();
    lastTime = millis();
}

void Encoder_Custom::update() {
    unsigned long currentTime = millis();
    if (currentTime - lastTime >= RPM_UPDATE_INTERVAL) {
        noInterrupts();
        long currentPos = position;
        interrupts();
        
        long deltaPos = currentPos - lastPosition;
        float deltaTime = (currentTime - lastTime) / 1000.0; // Convert to seconds
        
        if (deltaTime > 0) {
            float revolutions = (float)deltaPos / PULSES_PER_REVOLUTION;
            rpm = (revolutions / deltaTime) * 60.0; // Convert to RPM
        }
        
        lastPosition = currentPos;
        lastTime = currentTime;
    }
}

void Encoder_Custom::handleInterruptA() {
    bool aState = digitalRead(pinA);
    bool bState = digitalRead(pinB);
    
    if (aState != bState) {
        position++;
    } else {
        position--;
    }
}

void Encoder_Custom::handleInterruptB() {
    bool aState = digitalRead(pinA);
    bool bState = digitalRead(pinB);
    
    if (aState == bState) {
        position++;
    } else {
        position--;
    }
}

// Static interrupt service routines
void Encoder_Custom::isrA() {
    if (instanceA) {
        instanceA->handleInterruptA();
    }
}

void Encoder_Custom::isrB() {
    if (instanceB) {
        instanceB->handleInterruptB();
    }
}
