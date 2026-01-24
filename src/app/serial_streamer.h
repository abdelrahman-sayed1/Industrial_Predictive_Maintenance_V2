#ifndef SERIAL_STREAMER_H
#define SERIAL_STREAMER_H

#include <Arduino.h>
#include "../../include/types.h"

class SerialStreamer {
public:
    SerialStreamer();
    
    void begin(int baudRate);
    void sendStartMarker(String label, int durationMinutes);
    void sendEndMarker();
    void sendFeatures(const SampleFeatures& features);
    void streamFeatures(const SampleFeatures& features);
    void sendRawData(float* accel_x, float* accel_y, float* accel_z, int length);
    void streamRawWindow(float* accel_x, float* accel_y, float* accel_z, String label, int length);
    void sendSensorData(float temperature, float current, float rpm);
    
private:
    void sendCSVHeader();
    bool headerSent;
};

#endif