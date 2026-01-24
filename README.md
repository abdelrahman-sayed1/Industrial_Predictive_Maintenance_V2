# Industrial Predictive Maintenance System V2

Professional IoT system for real-time motor fault detection using TinyML on ESP32.

## System Overview

- **Hardware**: ESP32 + MPU6050 + DS18B20 + Encoder + MAX471 + DRV8825
- **Faults Detected**: Imbalance, Misalignment, Bearing Defects, Mechanical Looseness
- **ML Approach**: Hybrid (Rule-based + TinyML)
- **Connectivity**: MQTT → InfluxDB → Grafana

## Project Structure
```
├── src/
│   ├── main.cpp              # Clean entry point
│   ├── app/                  # Application logic
│   │   ├── data_collector.*  # Data collection module
│   │   └── serial_streamer.* # Serial communication
│   └── hal/                  # Hardware abstraction
│       └── sensor_manager.*  # Sensor initialization
├── lib/                      # Custom sensor libraries
├── python_scripts/           # PC-side data collection
└── collected_data/           # Training data output
```

## Quick Start

### 1. Hardware Setup
Connect sensors according to `docs/pinout.md`

### 2. Upload Firmware
```bash
pio run --target upload
```

### 3. Collect Training Data
```bash
cd python_scripts
pip install -r requirements.txt
python data_collector.py
```

### 4. Train ML Model
Upload `collected_data/*.csv` to Edge Impulse

### 5. Deploy
Export model and integrate into firmware

## Features

- ✅ 8kHz vibration sampling
- ✅ Real-time feature extraction
- ✅ Dual CSV output (features + raw data)
- ✅ Professional code structure
- ✅ MQTT telemetry ready
- ✅ Grafana visualization ready

## License

MIT License