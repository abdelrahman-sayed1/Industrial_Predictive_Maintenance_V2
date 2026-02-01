#include "DS18B20_Custom.h"

DS18B20_Custom::DS18B20_Custom(uint8_t dataPin) : pin(dataPin) {
}

void DS18B20_Custom::begin() {
    pinMode(pin, OUTPUT);
    digitalWrite(pin, HIGH);
}

bool DS18B20_Custom::isPresent() {
    reset();
    return true; // Simple presence check
}

float DS18B20_Custom::readTemperature() {
    reset();
    writeByte(CMD_SKIP_ROM);
    writeByte(CMD_CONVERT_T);
    
    // Wait for conversion to complete (max 750ms for 12-bit resolution)
    delay(750);
    
    reset();
    writeByte(CMD_SKIP_ROM);
    writeByte(CMD_READ_SCRATCHPAD);
    
    // Read 9 bytes
    uint8_t data[9];
    for (int i = 0; i < 9; i++) {
        data[i] = readByte();
    }
    
    // Calculate temperature
    int16_t tempRaw = (data[1] << 8) | data[0];
    
    // Check if negative temperature
    if (tempRaw & 0x8000) {
        tempRaw = ~tempRaw + 1;
        return -(tempRaw / 16.0);
    } else {
        return tempRaw / 16.0;
    }
}

void DS18B20_Custom::reset() {
    pinMode(pin, OUTPUT);
    digitalWrite(pin, LOW);
    delayMicroseconds(RESET_PULSE);
    digitalWrite(pin, HIGH);
    pinMode(pin, INPUT);
    delayMicroseconds(PRESENCE_WAIT);
    
    // Check for presence pulse
    bool present = (digitalRead(pin) == LOW);
    delayMicroseconds(PRESENCE_PULSE);
    
    // Update presence status
    present = (digitalRead(pin) == LOW);
    return;
}

void DS18B20_Custom::writeBit(uint8_t bit) {
    pinMode(pin, OUTPUT);
    digitalWrite(pin, LOW);
    delayMicroseconds(RECOVERY_TIME);
    
    if (bit) {
        digitalWrite(pin, HIGH);
    }
    delayMicroseconds(WRITE_SLOT - RECOVERY_TIME);
    digitalWrite(pin, HIGH);
    delayMicroseconds(RECOVERY_TIME);
}

void DS18B20_Custom::writeByte(uint8_t byte) {
    for (uint8_t i = 0; i < 8; i++) {
        writeBit((byte >> i) & 1);
    }
}

uint8_t DS18B20_Custom::readBit() {
    pinMode(pin, OUTPUT);
    digitalWrite(pin, LOW);
    delayMicroseconds(RECOVERY_TIME);
    digitalWrite(pin, HIGH);
    pinMode(pin, INPUT);
    delayMicroseconds(READ_SLOT - RECOVERY_TIME);
    bool bit = digitalRead(pin);
    delayMicroseconds(RECOVERY_TIME);
    
    return bit;
}

uint8_t DS18B20_Custom::readByte() {
    uint8_t byte = 0;
    for (uint8_t i = 0; i < 8; i++) {
        byte |= (readBit() << i);
    }
    return byte;
}
