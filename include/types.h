#ifndef TYPES_H
#define TYPES_H

#include <Arduino.h>

struct SampleFeatures {
    float rms_x;
    float rms_y;
    float rms_z;
    float peak_x;
    float peak_y;
    float peak_z;
    float std_x;
    float std_y;
    float std_z;
    float temperature;
    float current;
    float rpm;
    String label;
    unsigned long timestamp;
    
    // Frequency domain features
    float fft_1x;
    float fft_2x;
    float fft_3x;
    float high_freq_power;
    float spectral_kurtosis;
    
    // Derived features
    float crest_factor;
};

#endif
