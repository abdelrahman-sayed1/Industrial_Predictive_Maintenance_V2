#ifndef DS18B20_CUSTOM_H
#define DS18B20_CUSTOM_H

#include <Arduino.h>

class DS18B20_Custom {
private:
    uint8_t pin;
    
public:
    DS18B20_Custom(uint8_t dataPin);
    
    void begin();
    float readTemperature();
    bool isPresent();
    
private:
    void reset();
    void writeBit(uint8_t bit);
    void writeByte(uint8_t byte);
    uint8_t readBit();
    uint8_t readByte();
    
    // Commands
    static const uint8_t CMD_SEARCH_ROM = 0xF0;
    static const uint8_t CMD_READ_ROM = 0x33;
    static const uint8_t CMD_MATCH_ROM = 0x55;
    static const uint8_t CMD_SKIP_ROM = 0xCC;
    static const uint8_t CMD_ALARM_SEARCH = 0xEC;
    static const uint8_t CMD_CONVERT_T = 0x44;
    static const uint8_t CMD_WRITE_SCRATCHPAD = 0x4E;
    static const uint8_t CMD_READ_SCRATCHPAD = 0xBE;
    static const uint8_t CMD_COPY_SCRATCHPAD = 0x48;
    static const uint8_t CMD_RECALL_E2 = 0xB8;
    static const uint8_t CMD_READ_POWER_SUPPLY = 0xB4;
    
    // Timing constants (microseconds) - use uint16_t for larger values
    static const uint16_t RESET_PULSE = 480;
    static const uint8_t PRESENCE_WAIT = 70;
    static const uint16_t PRESENCE_PULSE = 410;
    static const uint8_t WRITE_SLOT = 60;
    static const uint8_t READ_SLOT = 15;
    static const uint8_t RECOVERY_TIME = 1;
};

#endif
