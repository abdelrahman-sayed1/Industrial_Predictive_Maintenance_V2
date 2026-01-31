#include "MPU6050_Custom.h"

// Conversion factors
const float MPU6050_Custom::ACCEL_SCALE_2G = 16384.0;
const float MPU6050_Custom::ACCEL_SCALE_4G = 8192.0;
const float MPU6050_Custom::ACCEL_SCALE_8G = 4096.0;
const float MPU6050_Custom::ACCEL_SCALE_16G = 2048.0;
const float MPU6050_Custom::GYRO_SCALE_250 = 131.0;
const float MPU6050_Custom::GYRO_SCALE_500 = 65.5;
const float MPU6050_Custom::GYRO_SCALE_1000 = 32.8;
const float MPU6050_Custom::GYRO_SCALE_2000 = 16.4;

MPU6050_Custom::MPU6050_Custom(uint8_t addr) : deviceAddress(addr), accelScale(ACCEL_SCALE_2G), gyroScale(GYRO_SCALE_250) {
}

bool MPU6050_Custom::begin() {
    Wire.begin(I2C_SDA_PIN, I2C_SCL_PIN);
    delay(100);
    
    // Check if device is present
    uint8_t whoAmI = readRegister(MPU6050_WHO_AM_I);
    if (whoAmI != 0x68 && whoAmI != 0x69) {
        Serial.print("MPU6050 not found. WHO_AM_I = 0x");
        Serial.println(whoAmI, HEX);
        return false;
    }
    
    initialize();
    return true;
}

void MPU6050_Custom::initialize() {
    // Wake up device
    writeRegister(MPU6050_PWR_MGMT_1, 0x00);
    delay(100);
    
    // Configure
    writeRegister(MPU6050_CONFIG, 0x00); // Disable DLPF
    writeRegister(MPU6050_GYRO_CONFIG, 0x00); // 250°/s range
    writeRegister(MPU6050_ACCEL_CONFIG, 0x00); // 2g range
    delay(100);
}

// Raw accelerometer methods
void MPU6050_Custom::getAccelerationRaw(int16_t* x, int16_t* y, int16_t* z) {
    uint8_t rawData[6];
    readRegisters(MPU6050_ACCEL_XOUT_H, 6, rawData);
    
    *x = (int16_t)((rawData[0] << 8) | rawData[1]);
    *y = (int16_t)((rawData[2] << 8) | rawData[3]);
    *z = (int16_t)((rawData[4] << 8) | rawData[5]);
}

int16_t MPU6050_Custom::getAccelerationRawX() {
    uint8_t rawData[2];
    readRegisters(MPU6050_ACCEL_XOUT_H, 2, rawData);
    return (int16_t)((rawData[0] << 8) | rawData[1]);
}

int16_t MPU6050_Custom::getAccelerationRawY() {
    uint8_t rawData[2];
    readRegisters(MPU6050_ACCEL_XOUT_H + 2, 2, rawData);
    return (int16_t)((rawData[0] << 8) | rawData[1]);
}

int16_t MPU6050_Custom::getAccelerationRawZ() {
    uint8_t rawData[2];
    readRegisters(MPU6050_ACCEL_XOUT_H + 4, 2, rawData);
    return (int16_t)((rawData[0] << 8) | rawData[1]);
}

// Raw gyroscope methods
void MPU6050_Custom::getGyroscopeRaw(int16_t* x, int16_t* y, int16_t* z) {
    uint8_t rawData[6];
    readRegisters(MPU6050_GYRO_XOUT_H, 6, rawData);
    
    *x = (int16_t)((rawData[0] << 8) | rawData[1]);
    *y = (int16_t)((rawData[2] << 8) | rawData[3]);
    *z = (int16_t)((rawData[4] << 8) | rawData[5]);
}

int16_t MPU6050_Custom::getGyroscopeRawX() {
    uint8_t rawData[2];
    readRegisters(MPU6050_GYRO_XOUT_H, 2, rawData);
    return (int16_t)((rawData[0] << 8) | rawData[1]);
}

int16_t MPU6050_Custom::getGyroscopeRawY() {
    uint8_t rawData[2];
    readRegisters(MPU6050_GYRO_XOUT_H + 2, 2, rawData);
    return (int16_t)((rawData[0] << 8) | rawData[1]);
}

int16_t MPU6050_Custom::getGyroscopeRawZ() {
    uint8_t rawData[2];
    readRegisters(MPU6050_GYRO_XOUT_H + 4, 2, rawData);
    return (int16_t)((rawData[0] << 8) | rawData[1]);
}

// Legacy scaled methods (for reference)
void MPU6050_Custom::getAcceleration(float* x, float* y, float* z) {
    uint8_t rawData[6];
    readRegisters(MPU6050_ACCEL_XOUT_H, 6, rawData);
    
    *x = (int16_t)((rawData[0] << 8) | rawData[1]) / accelScale;
    *y = (int16_t)((rawData[2] << 8) | rawData[3]) / accelScale;
    *z = (int16_t)((rawData[4] << 8) | rawData[5]) / accelScale;
}

float MPU6050_Custom::getAccelerationX() {
    uint8_t rawData[2];
    readRegisters(MPU6050_ACCEL_XOUT_H, 2, rawData);
    return (int16_t)((rawData[0] << 8) | rawData[1]) / accelScale;
}

float MPU6050_Custom::getAccelerationY() {
    uint8_t rawData[2];
    readRegisters(MPU6050_ACCEL_XOUT_H + 2, 2, rawData);
    return (int16_t)((rawData[0] << 8) | rawData[1]) / accelScale;
}

float MPU6050_Custom::getAccelerationZ() {
    uint8_t rawData[2];
    readRegisters(MPU6050_ACCEL_XOUT_H + 4, 2, rawData);
    return (int16_t)((rawData[0] << 8) | rawData[1]) / accelScale;
}

void MPU6050_Custom::getGyroscope(float* x, float* y, float* z) {
    uint8_t rawData[6];
    readRegisters(MPU6050_GYRO_XOUT_H, 6, rawData);
    
    *x = (int16_t)((rawData[0] << 8) | rawData[1]) / gyroScale;
    *y = (int16_t)((rawData[2] << 8) | rawData[3]) / gyroScale;
    *z = (int16_t)((rawData[4] << 8) | rawData[5]) / gyroScale;
}

float MPU6050_Custom::getGyroscopeX() {
    uint8_t rawData[2];
    readRegisters(MPU6050_GYRO_XOUT_H, 2, rawData);
    return (int16_t)((rawData[0] << 8) | rawData[1]) / gyroScale;
}

float MPU6050_Custom::getGyroscopeY() {
    uint8_t rawData[2];
    readRegisters(MPU6050_GYRO_XOUT_H + 2, 2, rawData);
    return (int16_t)((rawData[0] << 8) | rawData[1]) / gyroScale;
}

float MPU6050_Custom::getGyroscopeZ() {
    uint8_t rawData[2];
    readRegisters(MPU6050_GYRO_XOUT_H + 4, 2, rawData);
    return (int16_t)((rawData[0] << 8) | rawData[1]) / gyroScale;
}

float MPU6050_Custom::getTemperature() {
    uint8_t rawData[2];
    readRegisters(MPU6050_TEMP_OUT_H, 2, rawData);
    int16_t tempRaw = (int16_t)((rawData[0] << 8) | rawData[1]);
    return tempRaw / 340.0 + 36.53;
}

void MPU6050_Custom::setAccelerometerRange(uint8_t range) {
    uint8_t config = 0x00;
    switch(range) {
        case 2:  accelScale = ACCEL_SCALE_2G;  config = 0x00; break;
        case 4:  accelScale = ACCEL_SCALE_4G;  config = 0x08; break;
        case 8:  accelScale = ACCEL_SCALE_8G;  config = 0x10; break;
        case 16: accelScale = ACCEL_SCALE_16G; config = 0x18; break;
    }
    writeRegister(MPU6050_ACCEL_CONFIG, config);
}

void MPU6050_Custom::setGyroscopeRange(uint8_t range) {
    uint8_t config = 0x00;
    switch(range) {
        case 250:  gyroScale = GYRO_SCALE_250;  config = 0x00; break;
        case 500:  gyroScale = GYRO_SCALE_500;  config = 0x08; break;
        case 1000: gyroScale = GYRO_SCALE_1000; config = 0x10; break;
        case 2000: gyroScale = GYRO_SCALE_2000; config = 0x18; break;
    }
    writeRegister(MPU6050_GYRO_CONFIG, config);
}

void MPU6050_Custom::writeRegister(uint8_t reg, uint8_t value) {
    Wire.beginTransmission(deviceAddress);
    Wire.write(reg);
    Wire.write(value);
    uint8_t error = Wire.endTransmission();
    if (error != 0) {
        Serial.print("MPU6050 write error: ");
        Serial.println(error);
    }
}

uint8_t MPU6050_Custom::readRegister(uint8_t reg) {
    Wire.beginTransmission(deviceAddress);
    Wire.write(reg);
    uint8_t error = Wire.endTransmission(false);
    if (error != 0) {
        Serial.print("MPU6050 read error: ");
        Serial.println(error);
        return 0xFF;
    }
    
    Wire.requestFrom(deviceAddress, (uint8_t)1);
    return Wire.read();
}

void MPU6050_Custom::readRegisters(uint8_t reg, uint8_t count, uint8_t* data) {
    Wire.beginTransmission(deviceAddress);
    Wire.write(reg);
    uint8_t error = Wire.endTransmission(false);
    if (error != 0) {
        Serial.print("MPU6050 multi-read error: ");
        Serial.println(error);
        return;
    }
    
    Wire.requestFrom(deviceAddress, count);
    for(uint8_t i = 0; i < count; i++) {
        data[i] = Wire.read();
    }
}
