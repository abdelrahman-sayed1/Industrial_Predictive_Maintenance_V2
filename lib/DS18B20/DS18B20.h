#ifndef DS18B20_WRAPPER_H
#define DS18B20_WRAPPER_H

#include <OneWire.h>
#include <DallasTemperature.h>

class DS18B20 {
public:
    DS18B20(int pin);
    bool begin();
    float readTemperature();
    
private:
    OneWire oneWire;
    DallasTemperature sensors;
};

#endif
