#include "sensor_manager.h"
#include "../../lib/MPU6050/MPU6050.h"
#include "../../lib/Encoder/Encoder.h"
#include "../../lib/MAX471/MAX471.h"
#include "../../lib/DS18B20/DS18B20.h"

extern MPU6050 mpu;
extern Encoder encoder;
extern MAX471 powerSensor;
extern DS18B20 tempSensor;

SensorManager::SensorManager() {
    mpu6050_ok = false;
    ds18b20_ok = false;
    encoder_ok = false;
    max471_ok = false;
}

bool SensorManager::initializeAll() {
    Serial.println("\n--- Initializing Sensors ---");
    
    // MPU6050 (Critical)
    mpu6050_ok = mpu.initialize();
    if (!mpu6050_ok) {
        Serial.println("ERROR: MPU6050 initialization failed!");
        Serial.println("System cannot proceed without MPU6050");
        return false;
    }
    
    // DS18B20 (Optional)
    ds18b20_ok = tempSensor.begin();
    if (!ds18b20_ok) {
        Serial.println("WARNING: DS18B20 not found (temperature monitoring disabled)");
    }
    
    // Encoder (Required)
    encoder.begin();
    encoder_ok = true;
    
    // MAX471 (Required)
    powerSensor.begin();
    max471_ok = true;
    
    Serial.println("--- Sensor Initialization Complete ---\n");
    
    return true;
}

bool SensorManager::checkHealth() {
    // Perform basic health checks
    return mpu6050_ok;
}

void SensorManager::printStatus() {
    Serial.println("\n╔════════════════════════════════════════╗");
    Serial.println("║        SENSOR STATUS                  ║");
    Serial.println("╚════════════════════════════════════════╝");
    Serial.print("  MPU6050:  "); Serial.println(mpu6050_ok ? "✓ OK" : "✗ FAILED");
    Serial.print("  DS18B20:  "); Serial.println(ds18b20_ok ? "✓ OK" : "⚠ WARNING");
    Serial.print("  Encoder:  "); Serial.println(encoder_ok ? "✓ OK" : "✗ FAILED");
    Serial.print("  MAX471:   "); Serial.println(max471_ok ? "✓ OK" : "✗ FAILED");
    Serial.println();
}