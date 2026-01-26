#ifndef CONFIG_H
#define CONFIG_H

#include <Arduino.h>

// ============================================
// SYSTEM CONFIGURATION
// ============================================
#define FIRMWARE_VERSION "2.0.0"
#define DEVICE_ID "WEMOS_LOLIN32_LITE_V2"
#define SERIAL_BAUD_RATE 115200

// ============================================
// PIN CONFIGURATION (Wemos Lolin32 Lite)
// ============================================
// Encoder pins
#define ENCODER_PIN_A 32
#define ENCODER_PIN_B 33

// MAX471 power sensor pins (analog pins)
#define MAX471_VOLTAGE_PIN 34
#define MAX471_CURRENT_PIN 35

// DS18B20 temperature sensor
#define ONEWIRE_PIN 27

// MPU6050 uses I2C (GPIO 19=SDA, GPIO 22=SCL)
#define I2C_SDA_PIN 19
#define I2C_SCL_PIN 22

// DRV8825 motor driver pins
#define DRV8825_STEP_PIN    25
#define DRV8825_DIR_PIN     26
#define DRV8825_ENABLE_PIN  14
#define DRV8825_FAULT_PIN   12

// DRV8825 current limiting (IMPORTANT for preventing overheating!)
#define DRV8825_CURRENT_LIMIT_MA  500    // Set to 500mA for safety (adjust based on motor)
#define DRV8825_MODE0_PIN        13      // Microstep mode pins (optional)
#define DRV8825_MODE1_PIN        15      // Microstep mode pins (optional)
#define DRV8825_MODE2_PIN        2       // Microstep mode pins (optional)

// ============================================
// DATA COLLECTION CONFIGURATION
// ============================================
// Data collection parameters (editable from Python GUI)
#define DATA_COLLECTION_RATE_HZ 50        // 50Hz sampling rate
#define WINDOW_DURATION_SECONDS 4          // 4-second windows
#define SAMPLES_PER_WINDOW (DATA_COLLECTION_RATE_HZ * WINDOW_DURATION_SECONDS)  // 200 samples per window
#define SAMPLE_INTERVAL_US (1000000 / DATA_COLLECTION_RATE_HZ)  // 20000μs for 50Hz
#define DATA_CHANNELS 6                   // Acc(X,Y,Z) + Gyro(X,Y,Z)

// Legacy sampling configuration (for compatibility)
#define SAMPLE_SIZE SAMPLES_PER_WINDOW
#define FEATURE_INTERVAL_MS 500
#define RAW_WINDOW_INTERVAL_MS (WINDOW_DURATION_SECONDS * 1000)

// ============================================
// FEATURE EXTRACTION
// ============================================
// SampleFeatures struct is defined in types.h

#endif