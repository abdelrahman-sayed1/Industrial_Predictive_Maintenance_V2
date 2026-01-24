#ifndef SENSOR_MANAGER_H
#define SENSOR_MANAGER_H

#include <Arduino.h>

class SensorManager {
public:
    SensorManager();
    
    bool initializeAll();
    bool checkHealth();
    void printStatus();
    
private:
    bool mpu6050_ok;
    bool ds18b20_ok;
    bool encoder_ok;
    bool max471_ok;
};

#endif