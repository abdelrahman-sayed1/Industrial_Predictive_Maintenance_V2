#include "data_collector.h"
#include "../lib/MPU6050_Custom.h"
#include "../lib/DS18B20_Custom.h"
#include "../lib/Encoder_Custom.h"
#include "../lib/MAX471_Custom.h"
#include "../include/config.h"

// External sensor objects (defined in main.cpp)
extern MPU6050_Custom mpu;
extern Encoder_Custom encoder;
extern MAX471_Custom powerSensor;
extern DS18B20_Custom tempSensor;

// Motor control variables
volatile bool motorRunning = false;

DataCollector::DataCollector() {
    // Constructor
}

bool DataCollector::begin() {
    Serial.begin(SERIAL_BAUD_RATE);
    Serial.println("\n╔════════════════════════════════════════╗");
    Serial.println("║   INDUSTRIAL PREDICTIVE MAINTENANCE     ║");
    Serial.println("║   PROFESSIONAL DATA COLLECTION          ║");
    Serial.println("╚════════════════════════════════════════╝\n");
    
    // Initialize custom sensors
    if (!mpu.begin()) {
        Serial.println("MPU6050 initialization failed");
    } else {
        Serial.println("MPU6050 initialized");
    }
    
    encoder.begin();
    Serial.println("Encoder initialized");
    
    powerSensor.begin();
    Serial.println("MAX471 initialized");
    
    tempSensor.begin();
    Serial.println("DS18B20 initialized");
    
    Serial.println("SYSTEM_READY");
    return true;
}

void DataCollector::waitForCommand() {
    if (Serial.available()) {
        String command = Serial.readStringUntil('\n');
        command.trim();
        
        // Motor control commands
        if (command == "MOTOR_START") {
            startMotor();
        }
        else if (command == "MOTOR_STOP") {
            stopMotor();
        }
        else if (command.startsWith("MOTOR_DIR")) {
            int dir = command.substring(10).toInt();
            setMotorDirection(dir);
        }
        
        // Sensor check command
        else if (command == "CHECK_SENSORS") {
            checkAllSensors();
        }
        
        // Data collection commands
        else if (command.startsWith("COLLECT_")) {
            parseCollectionCommand(command);
        }
        
        // System commands
        else if (command == "PING") {
            Serial.println("PONG");
        }
    }
}

void DataCollector::startMotor() {
    pinMode(DRV8825_STEP_PIN, OUTPUT);
    pinMode(DRV8825_DIR_PIN, OUTPUT);
    pinMode(DRV8825_ENABLE_PIN, OUTPUT);
    digitalWrite(DRV8825_ENABLE_PIN, LOW);
    motorRunning = true;
    Serial.println("MOTOR_STARTED");
}

void DataCollector::stopMotor() {
    motorRunning = false;
    digitalWrite(DRV8825_ENABLE_PIN, HIGH);
    Serial.println("MOTOR_STOPPED");
}

void DataCollector::setMotorDirection(int direction) {
    digitalWrite(DRV8825_DIR_PIN, direction == 1 ? HIGH : LOW);
    Serial.println("MOTOR_DIRECTION_SET:" + String(direction));
}

void DataCollector::checkAllSensors() {
    Serial.println("SENSOR_CHECK_START");
    
    // Check MPU6050
    mpu.initialize(); // initialize() returns void, just call it
    Serial.println("MPU6050:OK");
    
    // Check Encoder
    pinMode(ENCODER_PIN_A, INPUT_PULLUP);
    pinMode(ENCODER_PIN_B, INPUT_PULLUP);
    Serial.println("ENCODER:OK");
    
    // Check MAX471
    pinMode(MAX471_VOLTAGE_PIN, INPUT);
    pinMode(MAX471_CURRENT_PIN, INPUT);
    Serial.println("MAX471:OK");
    
    // Check DS18B20
    float temp = tempSensor.readTemperature();
    if (temp != -127.0 && temp != 85.0) {
        Serial.println("DS18B20:OK");
    } else {
        Serial.println("DS18B20:FAIL");
    }
    
    Serial.println("SENSOR_CHECK_END");
}

void DataCollector::parseCollectionCommand(String command) {
    // Format: COLLECT_<SENSOR>,<SECONDS>
    // Examples: COLLECT_MPU,10 or COLLECT_ALL,20
    
    int sensorEnd = command.indexOf('_', 8);
    int commaPos = command.indexOf(',');
    
    if (commaPos == -1) {
        Serial.println("ERROR:Invalid format. Use COLLECT_<SENSOR>,<SECONDS>");
        return;
    }
    
    String sensor = command.substring(8, commaPos);
    int duration = command.substring(commaPos + 1).toInt();
    
    if (duration <= 0 || duration > 300) {
        Serial.println("ERROR:Duration must be 1-300 seconds");
        return;
    }
    
    Serial.println("COLLECTION_START:" + sensor + "," + String(duration));
    
    if (sensor == "MPU") {
        collectMPUData(duration);
    }
    else if (sensor == "ENCODER") {
        collectEncoderData(duration);
    }
    else if (sensor == "MAX471") {
        collectPowerData(duration);
    }
    else if (sensor == "DS18B20") {
        collectTempData(duration);
    }
    else if (sensor == "ALL") {
        collectAllSensorData(duration);
    }
    else {
        Serial.println("ERROR:Unknown sensor. Use MPU, ENCODER, MAX471, DS18B20, or ALL");
    }
    
    Serial.println("COLLECTION_END:" + sensor);
}

void DataCollector::collectMPUData(int duration) {
    unsigned long startTime = millis();
    unsigned long endTime = startTime + (duration * 1000);
    
    while (millis() < endTime) {
        unsigned long currentTime = millis();
        unsigned long elapsedMs = currentTime - startTime;
        
        // Get RAW sensor values for fault detection (no scaling)
        int16_t accel_x, accel_y, accel_z;
        int16_t gyro_x, gyro_y, gyro_z;
        
        mpu.getAccelerationRaw(&accel_x, &accel_y, &accel_z);
        mpu.getGyroscopeRaw(&gyro_x, &gyro_y, &gyro_z);
        
        Serial.print("MPU_DATA:");
        Serial.print(elapsedMs);
        Serial.print(",");
        Serial.print(accel_x);  // Raw integer values
        Serial.print(",");
        Serial.print(accel_y);
        Serial.print(",");
        Serial.print(accel_z);
        Serial.print(",");
        Serial.print(gyro_x);   // Raw integer values
        Serial.print(",");
        Serial.print(gyro_y);
        Serial.print(",");
        Serial.println(gyro_z);
        
        delay(5); // 200Hz sampling
    }
}

void DataCollector::collectEncoderData(int duration) {
    unsigned long startTime = millis();
    unsigned long endTime = startTime + (duration * 1000);
    
    while (millis() < endTime) {
        unsigned long currentTime = millis();
        unsigned long elapsedMs = currentTime - startTime;
        
        float rpm = encoder.getRPM();
        long position = encoder.getPosition();
        
        Serial.print("ENCODER_DATA:");
        Serial.print(elapsedMs);
        Serial.print(",");
        Serial.print(rpm, 2);
        Serial.print(",");
        Serial.println(position);
        
        delay(50); // 20Hz sampling
    }
}

void DataCollector::collectPowerData(int duration) {
    unsigned long startTime = millis();
    unsigned long endTime = startTime + (duration * 1000);
    
    while (millis() < endTime) {
        unsigned long currentTime = millis();
        unsigned long elapsedMs = currentTime - startTime;
        
        float voltage = powerSensor.getVoltage();
        float current = powerSensor.getCurrent();
        float power = voltage * current;
        
        Serial.print("POWER_DATA:");
        Serial.print(elapsedMs);
        Serial.print(",");
        Serial.print(voltage, 2);
        Serial.print(",");
        Serial.print(current, 3);
        Serial.print(",");
        Serial.println(power, 2);
        
        delay(50); // 20Hz sampling
    }
}

void DataCollector::collectTempData(int duration) {
    unsigned long startTime = millis();
    unsigned long endTime = startTime + (duration * 1000);
    
    while (millis() < endTime) {
        unsigned long currentTime = millis();
        unsigned long elapsedMs = currentTime - startTime;
        
        float temp = tempSensor.readTemperature();
        
        Serial.print("TEMP_DATA:");
        Serial.print(elapsedMs);
        Serial.print(",");
        Serial.println(temp, 1);
        
        delay(1000); // 1Hz sampling
    }
}

void DataCollector::collectAllSensorData(int duration) {
    unsigned long startTime = millis();
    unsigned long endTime = startTime + (duration * 1000);
    unsigned long lastTempTime = 0;
    
    while (millis() < endTime) {
        unsigned long currentTime = millis();
        unsigned long elapsedMs = currentTime - startTime;
        
        // MPU data (200Hz) - RAW values for fault detection
        int16_t accel_x, accel_y, accel_z;
        int16_t gyro_x, gyro_y, gyro_z;
        
        mpu.getAccelerationRaw(&accel_x, &accel_y, &accel_z);
        mpu.getGyroscopeRaw(&gyro_x, &gyro_y, &gyro_z);
        
        Serial.print("ALL_DATA:");
        Serial.print(elapsedMs);
        Serial.print(",");
        Serial.print(accel_x);  // Raw integer values
        Serial.print(",");
        Serial.print(accel_y);
        Serial.print(",");
        Serial.print(accel_z);
        Serial.print(",");
        Serial.print(gyro_x);   // Raw integer values
        Serial.print(",");
        Serial.print(gyro_y);
        Serial.print(",");
        Serial.print(gyro_z);
        
        // Encoder data (20Hz)
        static unsigned long lastEncoderTime = 0;
        if (currentTime - lastEncoderTime >= 50) {
            float rpm = encoder.getRPM();
            Serial.print(",");
            Serial.print(rpm, 2);
            lastEncoderTime = currentTime;
        }
        
        // Power data (20Hz)
        static unsigned long lastPowerTime = 0;
        if (currentTime - lastPowerTime >= 50) {
            float voltage = powerSensor.getVoltage();
            float current = powerSensor.getCurrent();
            Serial.print(",");
            Serial.print(voltage, 3);
            Serial.print(",");
            Serial.print(current, 4);
            lastPowerTime = currentTime;
        }
        
        // Temperature data (1Hz)
        if (currentTime - lastTempTime >= 1000) {
            float temp = tempSensor.readTemperature();
            Serial.print(",");
            Serial.println(temp, 2);
            lastTempTime = currentTime;
        } else {
            Serial.println(); // End line even without temp
        }
        
        delay(5); // 200Hz base rate
    }
}
