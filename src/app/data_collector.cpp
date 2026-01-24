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
        else if (command == "CHECK_SENSORS") {
            checkSensorStatus();
        }
        else if (command == "MOTOR_START") {
            Serial.println("MOTOR_START_ACK");
        }
        else if (command == "MOTOR_STOP") {
            Serial.println("MOTOR_STOP_ACK");
        }
        else if (command.startsWith("MOTOR_SPEED")) {
            // Format: MOTOR_SPEED:100 (RPM)
            int speed = command.substring(12).toInt();
            Serial.println("MOTOR_SPEED_ACK:" + String(speed));
        }
        else if (command.startsWith("MOTOR_DIR")) {
            // Format: MOTOR_DIR:1 (CW) or MOTOR_DIR:0 (CCW)
            int dir = command.substring(10).toInt();
            Serial.println("MOTOR_DIR_ACK:" + String(dir));
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
        float accel_x[SAMPLES_PER_WINDOW];
        float accel_y[SAMPLES_PER_WINDOW];
        float accel_z[SAMPLES_PER_WINDOW];
        
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
        delay(4000);  // 4-second window
    }
    
    Serial.println("COLLECTION_END," + label);
}

void DataCollector::collectVibrationData(float* accel_x, float* accel_y, float* accel_z) {
    for (int i = 0; i < SAMPLES_PER_WINDOW; i++) {
        // Read acceleration and gyroscope
        mpu.getAcceleration(&accel_x[i], &accel_y[i], &accel_z[i]);
        
        // Also read gyroscope (we'll stream both together)
        float gyro_x, gyro_y, gyro_z;
        mpu.getGyroscope(&gyro_x, &gyro_y, &gyro_z);
        
        // Stream: accX,accY,accZ,gyroX,gyroY,gyroZ (6 channels at 50Hz)
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
        
        delayMicroseconds(20000);  // 50Hz sampling
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

void DataCollector::checkSensorStatus() {
    Serial.println("Checking sensor connections...");
    
    // Check MPU6050
    if (mpu.initialize()) {
        Serial.println("MPU6050: OK");
    } else {
        Serial.println("MPU6050: FAIL - Not connected or I2C error");
    }
    
    // Check Encoder (simple test - read current state)
    int encoderA = digitalRead(ENCODER_PIN_A);
    int encoderB = digitalRead(ENCODER_PIN_B);
    if (encoderA != -1 && encoderB != -1) {
        Serial.println("Encoder: OK");
    } else {
        Serial.println("Encoder: FAIL - Pin configuration error");
    }
    
    // Check MAX471 (analog read test)
    int voltageRead = analogRead(MAX471_VOLTAGE_PIN);
    int currentRead = analogRead(MAX471_CURRENT_PIN);
    if (voltageRead >= 0 && currentRead >= 0) {
        Serial.println("MAX471: OK");
    } else {
        Serial.println("MAX471: FAIL - Analog read error");
    }
    
    // Check DS18B20
    float temp = tempSensor.readTemperature();
    if (temp != -127.0 && temp != 85.0) {  // Common error values
        Serial.println("DS18B20: OK");
    } else {
        Serial.println("DS18B20: FAIL - Not connected or read error");
    }
    
    // Check Motor Driver (using FLT pin for detection)
    pinMode(DRV8825_ENABLE_PIN, OUTPUT);
    pinMode(DRV8825_DIR_PIN, OUTPUT);
    pinMode(DRV8825_STEP_PIN, OUTPUT);
    pinMode(DRV8825_FAULT_PIN, INPUT_PULLUP);
    
    // Enable the driver first
    digitalWrite(DRV8825_ENABLE_PIN, LOW);
    delay(100);  // Give it time to initialize
    
    // Read fault pin - should be HIGH if no fault and driver is connected
    int faultState = digitalRead(DRV8825_FAULT_PIN);
    
    // Test by toggling enable pin and checking if fault pin responds
    digitalWrite(DRV8825_ENABLE_PIN, HIGH);  // Disable
    delay(50);
    int faultDisabled = digitalRead(DRV8825_FAULT_PIN);
    
    digitalWrite(DRV8825_ENABLE_PIN, LOW);   // Enable again
    delay(50);
    int faultEnabled = digitalRead(DRV8825_FAULT_PIN);
    
    // If the fault pin is consistently LOW, driver is either not connected or in fault
    if (faultState == LOW && faultDisabled == LOW && faultEnabled == LOW) {
        Serial.println("DRV8825: FAIL - Not connected or fault condition");
    }
    // If fault pin changes state or is HIGH, driver is likely connected
    else if (faultState == HIGH || faultDisabled != faultEnabled) {
        Serial.println("DRV8825: OK");
    }
    else {
        Serial.println("DRV8825: UNKNOWN - Inconsistent readings");
    }
    
    // Leave driver in disabled state for safety
    digitalWrite(DRV8825_ENABLE_PIN, HIGH);
    
    Serial.println("SENSOR_CHECK_COMPLETE");
}