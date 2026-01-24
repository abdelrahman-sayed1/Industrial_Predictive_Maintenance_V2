#include "serial_streamer.h"
#include "../../include/types.h"

SerialStreamer::SerialStreamer() {
    headerSent = false;
}

void SerialStreamer::begin(int baudRate) {
    Serial.begin(baudRate);
    headerSent = false;
}

void SerialStreamer::sendStartMarker(String label, int durationMinutes) {
    Serial.println("SESSION_START");
    Serial.println("Label:" + label);
    Serial.println("Duration:" + String(durationMinutes));
    Serial.println("Timestamp:" + String(millis()));
    Serial.println("DATA_BEGIN");
}

void SerialStreamer::sendEndMarker() {
    Serial.println("DATA_END");
    Serial.println("SESSION_END");
}

void SerialStreamer::sendFeatures(const SampleFeatures& features) {
    if (!headerSent) {
        sendCSVHeader();
        headerSent = true;
    }
    
    Serial.print(features.label);
    Serial.print(",");
    Serial.print(features.timestamp);
    Serial.print(",");
    Serial.print(features.rms_x, 4);
    Serial.print(",");
    Serial.print(features.rms_y, 4);
    Serial.print(",");
    Serial.print(features.rms_z, 4);
    Serial.print(",");
    Serial.print(features.peak_x, 4);
    Serial.print(",");
    Serial.print(features.peak_y, 4);
    Serial.print(",");
    Serial.print(features.peak_z, 4);
    Serial.print(",");
    Serial.print(features.std_x, 4);
    Serial.print(",");
    Serial.print(features.std_y, 4);
    Serial.print(",");
    Serial.print(features.std_z, 4);
    Serial.print(",");
    Serial.print(features.temperature, 2);
    Serial.print(",");
    Serial.print(features.current, 4);
    Serial.print(",");
    Serial.print(features.rpm, 2);
    Serial.print(",");
    Serial.print(features.fft_1x, 4);
    Serial.print(",");
    Serial.print(features.fft_2x, 4);
    Serial.print(",");
    Serial.print(features.fft_3x, 4);
    Serial.print(",");
    Serial.print(features.high_freq_power, 4);
    Serial.print(",");
    Serial.print(features.spectral_kurtosis, 4);
    Serial.print(",");
    Serial.println(features.crest_factor, 4);
}

void SerialStreamer::streamFeatures(const SampleFeatures& features) {
    sendFeatures(features);
}

void SerialStreamer::sendRawData(float* accel_x, float* accel_y, float* accel_z, int length) {
    Serial.println("RAW_DATA_START");
    for (int i = 0; i < length; i++) {
        Serial.print(accel_x[i], 6);
        Serial.print(",");
        Serial.print(accel_y[i], 6);
        Serial.print(",");
        Serial.println(accel_z[i], 6);
    }
    Serial.println("RAW_DATA_END");
}

void SerialStreamer::streamRawWindow(float* accel_x, float* accel_y, float* accel_z, String label, int length) {
    Serial.println("RAW_WINDOW_START");
    Serial.println("Label:" + label);
    Serial.println("Length:" + String(length));
    sendRawData(accel_x, accel_y, accel_z, length);
}

void SerialStreamer::sendSensorData(float temperature, float current, float rpm) {
    Serial.print("SENSOR_DATA,");
    Serial.print(temperature, 2);
    Serial.print(",");
    Serial.print(current, 4);
    Serial.print(",");
    Serial.println(rpm, 2);
}

void SerialStreamer::sendCSVHeader() {
    Serial.println("FEATURES_CSV_HEADER");
    Serial.println("label,timestamp,rms_x,rms_y,rms_z,peak_x,peak_y,peak_z,std_x,std_y,std_z,temperature,current,rpm,fft_1x,fft_2x,fft_3x,high_freq_power,spectral_kurtosis,crest_factor");
}