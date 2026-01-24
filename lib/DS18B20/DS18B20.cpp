#include "DS18B20.h"

DS18B20::DS18B20(int pin) : oneWire(pin), sensors(&oneWire) {}

bool DS18B20::begin() {
    sensors.begin();
    
    if (sensors.getDeviceCount() == 0) {
        Serial.println("No DS18B20 found!");
        return false;
    }
    
    Serial.println("✓ DS18B20 initialized");
    return true;
}

float DS18B20::readTemperature() {
    sensors.requestTemperatures();
    return sensors.getTempCByIndex(0);
}
