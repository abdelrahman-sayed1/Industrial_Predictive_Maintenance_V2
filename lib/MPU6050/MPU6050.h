#ifndef MPU6050_WRAPPER_H
#define MPU6050_WRAPPER_H

#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>
#include <Wire.h>

class MPU6050 {
public:
    MPU6050();
    bool initialize();
    void getAcceleration(float* x, float* y, float* z);
    void getGyroscope(float* x, float* y, float* z);
    
private:
    Adafruit_MPU6050 mpu;
};

#endif
