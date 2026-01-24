# Motor Control Pin Configuration - Wemos Lolin32 Lite

## DRV8825 Motor Driver Connections

| ESP32 Pin | DRV8825 Pin | Function |
|-----------|-------------|----------|
| GPIO 25   | STEP        | Step pulse control |
| GPIO 26   | DIR         | Direction control |
| GPIO 14   | ENABLE      | Motor enable/disable |
| GPIO 12   | FAULT       | Fault detection (input) |

## Wiring Instructions

1. **STEP (GPIO 25)**: Connect to DRV8825 STEP pin
2. **DIR (GPIO 26)**: Connect to DRV8825 DIR pin  
3. **ENABLE (GPIO 14)**: Connect to DRV8825 ENABLE pin
4. **FAULT (GPIO 12)**: Connect to DRV8825 FAULT pin

## Power Connections
- **VMOT**: Motor power supply (8-35V)
- **GND**: Common ground
- **VDD**: Logic power (3.3V from ESP32)
- **GND**: Logic ground

## Motor Connections
- **A1, A2**: Motor coil 1
- **B1, B2**: Motor coil 2

## Usage Examples

```cpp
// Enable motor
motorDriver.enable();

// Set direction (true = clockwise, false = counter-clockwise)
motorDriver.setDirection(true);

// Rotate motor (200 steps = 1 revolution for 1.8° stepper)
motorDriver.rotate(200, 1000); // 200 steps, 1000μs delay between steps

// Disable motor
motorDriver.disable();

// Check for faults
if (motorDriver.isFault()) {
    Serial.println("Motor fault detected!");
}
```

## Notes
- Pins 25, 26, 14, 12 are available on Wemos Lolin32 Lite
- All pins support digital output/input
- Pin 12 has internal pull-up for fault detection