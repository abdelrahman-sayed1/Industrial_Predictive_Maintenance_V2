#include "MPU6050.h"
#include "../../include/config.h"

MPU6050::MPU6050() {}

bool MPU6050::initialize() {
    // Initialize I2C with custom pins
    Wire.begin(I2C_SDA_PIN, I2C_SCL_PIN);
    
    if (!mpu.begin()) {
        Serial.println("Failed to find MPU6050!");
        return false;
    }
    
    mpu.setAccelerometerRange(MPU6050_RANGE_8_G);
    mpu.setGyroRange(MPU6050_RANGE_500_DEG);
    mpu.setFilterBandwidth(MPU6050_BAND_260_HZ);
    
    Serial.println("✓ MPU6050 initialized");
    return true;
}

void MPU6050::getAcceleration(float* x, float* y, float* z) {
    sensors_event_t a, g, temp;
    mpu.getEvent(&a, &g, &temp);
    
    *x = a.acceleration.x;
    *y = a.acceleration.y;
    *z = a.acceleration.z;
}

void MPU6050::getGyroscope(float* x, float* y, float* z) {
    sensors_event_t a, g, temp;
    mpu.getEvent(&a, &g, &temp);
    
    *x = g.gyro.x;
    *y = g.gyro.y;
    *z = g.gyro.z;
}
