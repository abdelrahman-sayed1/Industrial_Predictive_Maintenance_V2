#ifndef DATA_COLLECTOR_H
#define DATA_COLLECTOR_H

#include <Arduino.h>

class DataCollector {
public:
    DataCollector();
    
    bool begin();
    void waitForCommand();
    
private:
    // Motor control methods
    void startMotor();
    void stopMotor();
    void setMotorDirection(int direction);
    
    // Sensor check method
    void checkAllSensors();
    
    // Data collection methods
    void parseCollectionCommand(String command);
    void collectMPUData(int duration);
    void collectEncoderData(int duration);
    void collectPowerData(int duration);
    void collectTempData(int duration);
    void collectAllSensorData(int duration);
};

#endif
