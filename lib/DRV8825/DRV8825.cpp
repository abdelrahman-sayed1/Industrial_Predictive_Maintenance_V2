/*
 * Very Simple Stepper Motor - One Direction Only
 * Just runs continuously in one direction
 */

#include "DRV8825.h"
#include <Arduino.h>

DRV8825::DRV8825(int stepPin, int dirPin, int enablePin, int faultPin)
    : _stepPin(stepPin), _dirPin(dirPin), _enablePin(enablePin), _faultPin(faultPin) {
    motorRunning = false;
}

void DRV8825::begin() {
  // Set pins as outputs
  pinMode(_stepPin, OUTPUT);
  pinMode(_dirPin, OUTPUT);
  pinMode(_enablePin, OUTPUT);
  
  // Set direction (HIGH = one direction, LOW = opposite)
  digitalWrite(_dirPin, HIGH);
  
  // Enable motor (LOW = enabled, HIGH = disabled)
  digitalWrite(_enablePin, HIGH); // Start disabled
  Serial.println("Simple Motor Ready");
}

void DRV8825::enable() {
  digitalWrite(_enablePin, LOW); // Enable motor
  motorRunning = true;
  Serial.println("MOTOR_START_ACK");
}

void DRV8825::disable() {
  digitalWrite(_enablePin, HIGH); // Disable motor
  motorRunning = false;
  Serial.println("MOTOR_STOP_ACK");
}

void DRV8825::setDirection(bool clockwise) {
  digitalWrite(_dirPin, clockwise ? HIGH : LOW);
  Serial.println("MOTOR_DIR_ACK:" + String(clockwise ? 1 : 0));
}

void DRV8825::step() {
  // Step the motor - EXACTLY like your working code
  digitalWrite(_stepPin, HIGH);
  delayMicroseconds(800);  // Small delay
  digitalWrite(_stepPin, LOW);
  delayMicroseconds(50);  // Small delay
}

void DRV8825::runMotor() {
  if (motorRunning) {
    // Step the motor - EXACTLY like your working code
    digitalWrite(_stepPin, HIGH);
    delayMicroseconds(800);  // Small delay
    digitalWrite(_stepPin, LOW);
    delayMicroseconds(50);  // Small delay
    
    // Debug output every 1000 steps
    static int stepCount = 0;
    stepCount++;
    if (stepCount % 1000 == 0) {
      Serial.println("Stepping motor: " + String(stepCount));
    }
  }
}

bool DRV8825::isFault() {
  return digitalRead(_faultPin) == LOW;
}
