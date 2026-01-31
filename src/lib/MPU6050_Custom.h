#ifndef MPU6050_CUSTOM_H
#define MPU6050_CUSTOM_H

#include <Arduino.h>
#include <Wire.h>

// I2C pin definitions (from config.h)
#ifndef I2C_SDA_PIN
#define I2C_SDA_PIN 19
#endif
#ifndef I2C_SCL_PIN
#define I2C_SCL_PIN 22
#endif

class MPU6050_Custom {
private:
    uint8_t deviceAddress;
    
public:
    MPU6050_Custom(uint8_t addr = 0x68);
    
    bool begin();
    void initialize();
    
    // Accelerometer - Raw values
    void getAccelerationRaw(int16_t* x, int16_t* y, int16_t* z);
    int16_t getAccelerationRawX();
    int16_t getAccelerationRawY();
    int16_t getAccelerationRawZ();
    
    // Gyroscope - Raw values
    void getGyroscopeRaw(int16_t* x, int16_t* y, int16_t* z);
    int16_t getGyroscopeRawX();
    int16_t getGyroscopeRawY();
    int16_t getGyroscopeRawZ();
    
    // Legacy scaled methods (for reference)
    void getAcceleration(float* x, float* y, float* z);
    float getAccelerationX();
    float getAccelerationY();
    float getAccelerationZ();
    
    void getGyroscope(float* x, float* y, float* z);
    float getGyroscopeX();
    float getGyroscopeY();
    float getGyroscopeZ();
    
    // Temperature
    float getTemperature();
    
    // Configuration
    void setAccelerometerRange(uint8_t range);
    void setGyroscopeRange(uint8_t range);
    
private:
    void writeRegister(uint8_t reg, uint8_t value);
    uint8_t readRegister(uint8_t reg);
    void readRegisters(uint8_t reg, uint8_t count, uint8_t* data);
    
    // Register addresses
    static const uint8_t MPU6050_ADDRESS_AD0_LOW = 0x68;
    static const uint8_t MPU6050_ADDRESS_AD0_HIGH = 0x69;
    static const uint8_t MPU6050_WHO_AM_I = 0x75;
    static const uint8_t MPU6050_PWR_MGMT_1 = 0x6B;
    static const uint8_t MPU6050_CONFIG = 0x1A;
    static const uint8_t MPU6050_GYRO_CONFIG = 0x1B;
    static const uint8_t MPU6050_ACCEL_CONFIG = 0x1C;
    static const uint8_t MPU6050_ACCEL_XOUT_H = 0x3B;
    static const uint8_t MPU6050_TEMP_OUT_H = 0x41;
    static const uint8_t MPU6050_GYRO_XOUT_H = 0x43;
    
    // Conversion factors
    static const float ACCEL_SCALE_2G;
    static const float ACCEL_SCALE_4G;
    static const float ACCEL_SCALE_8G;
    static const float ACCEL_SCALE_16G;
    static const float GYRO_SCALE_250;
    static const float GYRO_SCALE_500;
    static const float GYRO_SCALE_1000;
    static const float GYRO_SCALE_2000;
    
    float accelScale;
    float gyroScale;
};

#endif
