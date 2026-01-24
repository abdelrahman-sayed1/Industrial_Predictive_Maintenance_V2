#include <Arduino.h>
#include "app/data_collector.h"
#include "hal/sensor_manager.h"
#include "../lib/MPU6050/MPU6050.h"
#include "../lib/Encoder/Encoder.h"
#include "../lib/MAX471/MAX471.h"
#include "../lib/DS18B20/DS18B20.h"
#include "../include/config.h"

// ============================================
// GLOBAL SENSOR INSTANCES
// ============================================
MPU6050 mpu;
Encoder encoder(ENCODER_PIN_A, ENCODER_PIN_B);
MAX471 powerSensor(MAX471_VOLTAGE_PIN, MAX471_CURRENT_PIN);
DS18B20 tempSensor(ONEWIRE_PIN);

// ============================================
// APPLICATION COMPONENTS
// ============================================
SensorManager sensorManager;
DataCollector dataCollector;

// ============================================
// SETUP
// ============================================
void setup() {
    // Initialize serial communication
    Serial.begin(SERIAL_BAUD_RATE);
    delay(2000);
    
    // Print banner
    Serial.println("\n\n");
    Serial.println("╔════════════════════════════════════════╗");
    Serial.println("║  INDUSTRIAL PREDICTIVE MAINTENANCE    ║");
    Serial.println("║  Firmware Version: " FIRMWARE_VERSION "               ║");
    Serial.println("║  Device ID: " DEVICE_ID "                    ║");
    Serial.println("╚════════════════════════════════════════╝");
    
    // Initialize all sensors
    if (!sensorManager.initializeAll()) {
        Serial.println("\n⚠ WARNING: Some sensors failed initialization");
        Serial.println("Attempting to continue...");
    }
    
    // Print sensor status
    sensorManager.printStatus();
    
    // Initialize data collector
    if (!dataCollector.begin()) {
        Serial.println("✗ ERROR: Data collector initialization failed");
        while(1) delay(1000);
    }
    
    Serial.println("✓ System ready for data collection\n");
}

// ============================================
// MAIN LOOP
// ============================================
void loop() {
    // Wait for commands from Python script
    dataCollector.waitForCommand();
    
    delay(100);
}