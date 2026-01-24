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

// ============================================
// SAMPLING CONFIGURATION
// ============================================
#define SAMPLE_SIZE 512
#define SAMPLE_INTERVAL_US 125  // 8kHz sampling (1,000,000 / 8000 = 125)
#define FEATURE_INTERVAL_MS 500
#define RAW_WINDOW_INTERVAL_MS 2000

// ============================================
// FEATURE EXTRACTION
// ============================================
// SampleFeatures struct is defined in types.h

#endif