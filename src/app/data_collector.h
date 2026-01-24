#ifndef DATA_COLLECTOR_H
#define DATA_COLLECTOR_H

#include <Arduino.h>
#include "serial_streamer.h"
#include "../../include/types.h"
#include "../../include/config.h"

class DataCollector {
public:
    DataCollector();
    
    bool begin();
    void waitForCommand();
    
private:
    SerialStreamer* streamer;
    
    void collectSession(String label, int durationMinutes);
    void collectVibrationData(float* accel_x, float* accel_y, float* accel_z);
    SampleFeatures extractFeatures(float* accel_x, float* accel_y, float* accel_z);
    
    // Feature calculation methods
    float calculateRMS(float* data, int length);
    float calculatePeak(float* data, int length);
    float calculateStdDev(float* data, int length);
    
    // Timing variables
    unsigned long lastFeature;
    unsigned long lastRawWindow;
};

#endif