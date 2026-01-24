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

### 3. Collect Training Data (Edge Impulse – raw-only, EI-ready)
```bash
cd python_scripts
pip install -r requirements.txt
python edge_impulse_collector.py
```
- Select COM port, then run 5 states: **normal**, **imbalance**, **misalignment**, **bearing_defect**, **looseness** (~5 min each).
- Output: `collected_data/edge_impulse/<run_id>/*.csv` — one CSV per 512-sample window (`timestamp,accX,accY,accZ`, 0.125 ms step, 8 kHz). Filenames: `label.id.csv` (e.g. `normal.0.csv`).

### 4. Train ML Model (Edge Impulse)
- Upload the `collected_data/edge_impulse/<run_id>/` folder to Edge Impulse → **Data acquisition**.
- Use DSP → **Choose recommended**, then train classifier and deploy to ESP32.

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