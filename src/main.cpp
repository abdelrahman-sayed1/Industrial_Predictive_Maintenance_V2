#include <Arduino.h>
#include "app/data_collector.h"
#include "hal/sensor_manager.h"
#include "../lib/MPU6050/MPU6050.h"
#include "../lib/Encoder/Encoder.h"
#include "../lib/MAX471/MAX471.h"
#include "../lib/DS18B20/DS18B20.h"
#include "../lib/DRV8825/DRV8825.h"
#include "../include/config.h"
#include "soc/gpio_struct.h"

extern volatile bool motorRunning;

static hw_timer_t* stepTimer = nullptr;
static portMUX_TYPE stepTimerMux = portMUX_INITIALIZER_UNLOCKED;
static volatile bool stepPinHigh = false;

// ============================================
// GLOBAL SENSOR INSTANCES
// ============================================
MPU6050 mpu;
Encoder encoder(ENCODER_PIN_A, ENCODER_PIN_B);
MAX471 powerSensor(MAX471_VOLTAGE_PIN, MAX471_CURRENT_PIN);
DS18B20 tempSensor(ONEWIRE_PIN);
DRV8825 motorDriver(DRV8825_STEP_PIN, DRV8825_DIR_PIN, DRV8825_ENABLE_PIN, DRV8825_FAULT_PIN);

// ============================================
// APPLICATION COMPONENTS
// ============================================
SensorManager sensorManager;
DataCollector dataCollector;

static void IRAM_ATTR onStepTimer() {
    portENTER_CRITICAL_ISR(&stepTimerMux);

    if (!motorRunning) {
        if (stepPinHigh) {
            GPIO.out_w1tc = (1UL << DRV8825_STEP_PIN);
            stepPinHigh = false;
        }
        timerAlarmWrite(stepTimer, 50, true);
        portEXIT_CRITICAL_ISR(&stepTimerMux);
        return;
    }

    if (!stepPinHigh) {
        GPIO.out_w1ts = (1UL << DRV8825_STEP_PIN);
        stepPinHigh = true;
        timerAlarmWrite(stepTimer, 800, true);
    } else {
        GPIO.out_w1tc = (1UL << DRV8825_STEP_PIN);
        stepPinHigh = false;
        timerAlarmWrite(stepTimer, 50, true);
    }

    portEXIT_CRITICAL_ISR(&stepTimerMux);
}

// ============================================
// SETUP
// ============================================
void setup() {
    // Initialize serial communication
    Serial.begin(SERIAL_BAUD_RATE);
    delay(2000);

    // Print banner
    Serial.println("\n\n");
    Serial.println("╔════════════════════════════════════════╗");
    Serial.println("║  INDUSTRIAL PREDICTIVE MAINTENANCE    ║");
    Serial.println("║  Firmware Version: " FIRMWARE_VERSION "               ║");
    Serial.println("║  Device ID: " DEVICE_ID "                    ║");
    Serial.println("╚════════════════════════════════════════╝");

    // Initialize all sensors
    if (!sensorManager.initializeAll()) {
        Serial.println("\n⚠ WARNING: Some sensors failed initialization");
        Serial.println("Attempting to continue...");
    }

    // Print sensor status
    sensorManager.printStatus();

    // Initialize data collector
    if (!dataCollector.begin()) {
        Serial.println("✗ ERROR: Data collector initialization failed");
        while(1) delay(1000);
    }

    // Motor pins (timer ISR will generate STEP pulses)
    pinMode(DRV8825_STEP_PIN, OUTPUT);
    pinMode(DRV8825_DIR_PIN, OUTPUT);
    pinMode(DRV8825_ENABLE_PIN, OUTPUT);
    digitalWrite(DRV8825_STEP_PIN, LOW);
    digitalWrite(DRV8825_ENABLE_PIN, HIGH);  // disabled by default; GUI enables

    // Hardware timer: 1 tick = 1us (divider 80 @ 80MHz APB)
    stepTimer = timerBegin(0, 80, true);
    timerAttachInterrupt(stepTimer, &onStepTimer, true);
    timerAlarmWrite(stepTimer, 50, true);
    timerAlarmEnable(stepTimer);

    Serial.println("✓ Motor step timer initialized");

    Serial.println("✓ System ready for data collection\n");
}

// ============================================
// MAIN LOOP
// ============================================
void loop() {
    // Wait for commands from Python script
    dataCollector.waitForCommand();
    
    // No delay - let motor step at its own pace
}