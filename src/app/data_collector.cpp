#include "data_collector.h"
#include "../../include/types.h"
#include "../../include/config.h"
#include "../../lib/MPU6050/MPU6050.h"
#include "../../lib/Encoder/Encoder.h"
#include "../../lib/MAX471/MAX471.h"
#include "../../lib/DS18B20/DS18B20.h"

// External sensor objects (defined in main.cpp)
extern MPU6050 mpu;
extern Encoder encoder;
extern MAX471 powerSensor;
extern DS18B20 tempSensor;

DataCollector::DataCollector() {
    streamer = new SerialStreamer();
    lastFeature = 0;
    lastRawWindow = 0;
}

bool DataCollector::begin() {
    streamer->begin(SERIAL_BAUD_RATE);
    
    Serial.println("\n╔════════════════════════════════════════╗");
    Serial.println("║   PREDICTIVE MAINTENANCE SYSTEM       ║");
    Serial.println("║   DATA COLLECTION MODE                ║");
    Serial.println("╚════════════════════════════════════════╝\n");
    
    Serial.println("SYSTEM_READY");
    Serial.println("Waiting for commands...\n");
    
    return true;
}

void DataCollector::waitForCommand() {
    if (Serial.available()) {
        String command = Serial.readStringUntil('\n');
        command.trim();
        
        if (command == "START_NORMAL") {
            collectSession("normal", 5);
        }
        else if (command == "START_IMBALANCE") {
            collectSession("imbalance", 5);
        }
        else if (command == "START_MISALIGNMENT") {
            collectSession("misalignment", 5);
        }
        else if (command == "START_BEARING") {
            collectSession("bearing_defect", 5);
        }
        else if (command == "START_LOOSENESS") {
            collectSession("looseness", 5);
        }
        else if (command == "PING") {
            Serial.println("PONG");
        }
    }
}

void DataCollector::collectSession(String label, int durationMinutes) {
    Serial.println("COLLECTION_START," + label);
    
    unsigned long sessionStart = millis();
    unsigned long sessionDuration = durationMinutes * 60UL * 1000UL;
    
    int sampleCount = 0;
    
    while (millis() - sessionStart < sessionDuration) {
        // Collect vibration data and stream immediately
        float accel_x[SAMPLE_SIZE];
        float accel_y[SAMPLE_SIZE];
        float accel_z[SAMPLE_SIZE];
        
        collectVibrationData(accel_x, accel_y, accel_z);
        
        // Read other sensors
        float rpm = encoder.getRPM();
        float voltage = powerSensor.getVoltage();
        float current = powerSensor.getCurrent();
        float temperature = tempSensor.readTemperature();
        
        // Mark each window with sensor data
        Serial.print("RAW_WINDOW_START,");
        Serial.print(String(sampleCount) + ",");
        Serial.print(label + ",");
        Serial.print(rpm, 2);
        Serial.print(",");
        Serial.print(voltage, 3);
        Serial.print(",");
        Serial.print(current, 4);
        Serial.print(",");
        Serial.println(temperature, 2);
        
        sampleCount++;
        delay(10);
    }
    
    Serial.println("COLLECTION_END," + label);
}

void DataCollector::collectVibrationData(float* accel_x, float* accel_y, float* accel_z) {
    for (int i = 0; i < SAMPLE_SIZE; i++) {
        // Read acceleration and gyroscope
        mpu.getAcceleration(&accel_x[i], &accel_y[i], &accel_z[i]);
        
        // Also read gyroscope (we'll stream both together)
        float gyro_x, gyro_y, gyro_z;
        mpu.getGyroscope(&gyro_x, &gyro_y, &gyro_z);
        
        // Stream: accel_x,accel_y,accel_z,gyro_x,gyro_y,gyro_z
        Serial.print(accel_x[i], 4);
        Serial.print(",");
        Serial.print(accel_y[i], 4);
        Serial.print(",");
        Serial.print(accel_z[i], 4);
        Serial.print(",");
        Serial.print(gyro_x, 4);
        Serial.print(",");
        Serial.print(gyro_y, 4);
        Serial.print(",");
        Serial.println(gyro_z, 4);
        
        delayMicroseconds(SAMPLE_INTERVAL_US);
    }
}

SampleFeatures DataCollector::extractFeatures(float* accel_x, float* accel_y, float* accel_z) {
    SampleFeatures f;
    
    // Arduino only sends raw data - Python will compute features
    // These are placeholders
    f.rms_x = 0.0;
    f.rms_y = 0.0;
    f.rms_z = 0.0;
    f.peak_x = 0.0;
    f.peak_y = 0.0;
    f.peak_z = 0.0;
    f.std_x = 0.0;
    f.std_y = 0.0;
    f.std_z = 0.0;
    f.fft_1x = 0.0;
    f.fft_2x = 0.0;
    f.fft_3x = 0.0;
    f.high_freq_power = 0.0;
    f.spectral_kurtosis = 0.0;
    f.crest_factor = 0.0;
    
    return f;
}

float DataCollector::calculateRMS(float* data, int length) {
    float sum = 0;
    for (int i = 0; i < length; i++) {
        sum += data[i] * data[i];
    }
    return sqrt(sum / length);
}

float DataCollector::calculatePeak(float* data, int length) {
    float max_val = abs(data[0]);
    for (int i = 1; i < length; i++) {
        if (abs(data[i]) > max_val) {
            max_val = abs(data[i]);
        }
    }
    return max_val;
}

float DataCollector::calculateStdDev(float* data, int length) {
    float mean = 0;
    for (int i = 0; i < length; i++) {
        mean += data[i];
    }
    mean /= length;
    
    float variance = 0;
    for (int i = 0; i < length; i++) {
        variance += (data[i] - mean) * (data[i] - mean);
    }
    return sqrt(variance / length);
}