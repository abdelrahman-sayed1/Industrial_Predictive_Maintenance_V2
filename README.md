# Industrial Predictive Maintenance System V2

Professional IoT system for real-time motor fault detection using TinyML on ESP32 with complete GUI interface.

## 🎯 System Overview

- **Hardware**: ESP32 + MPU6050 + DS18B20 + Encoder + MAX471 + DRV8825
- **Faults Detected**: Imbalance, Misalignment, Bearing Defects, Mechanical Looseness
- **ML Approach**: Hybrid (Rule-based + TinyML)
- **GUI**: Complete Python tkinter interface with tabbed navigation
- **Data Collection**: Acc+Gyro (6 channels) at 50Hz with 4-second windows

## 🚀 Major Updates (Latest Version)

### ✨ New Features Added:
- **🖥️ Complete GUI Interface**: All-in-one Python application with tabbed navigation
- **⚙️ Motor Control**: Full motor control (start/stop, speed 10-1000 RPM, direction CW/CCW)
- **📊 Enhanced Data Collection**: Configurable parameters from firmware (50Hz, 4s windows, 6 channels)
- **🔍 Real-time Sensor Checking**: Automatic sensor status detection for all 5 sensors
- **📋 Improved Logging**: Color-coded system log with timestamps and error handling
- **🎛️ Dual Mode Operation**: Manual mode for full control, Demo mode for automated workflow

### 🔧 Technical Improvements:
- **Consolidated Python Scripts**: Single `industrial_predictive_maintenance.py` file
- **Tabbed Interface**: No scrolling needed - everything fits on one screen (1400×800)
- **Enhanced Error Handling**: Robust serial communication and sensor detection
- **Better Data Format**: Optimized CSV format for TinyML training on Edge Impulse
- **Real-time Motor Control**: ESP32 firmware with motor driver command handling

## 📁 Updated Project Structure
```
├── src/
│   ├── main.cpp              # Clean entry point
│   ├── app/                  # Application logic
│   │   ├── data_collector.*  # Enhanced data collection with motor control
│   │   └── serial_streamer.* # Serial communication
│   └── hal/                  # Hardware abstraction
│       └── sensor_manager.*  # Sensor initialization
├── include/
│   └── config.h              # Configurable data collection parameters
├── lib/                      # Custom sensor libraries
│   ├── MPU6050/              # Accelerometer/Gyro library
│   ├── DS18B20/              # Temperature sensor library
│   ├── Encoder/              # RPM sensor library
│   ├── MAX471/               # Current sensor library
│   └── DRV8825/              # Motor driver library
├── python_scripts/
│   └── industrial_predictive_maintenance.py  # Complete GUI application
└── collected_data/           # Training data output
```

## 🎮 GUI Interface Features

### 🗂️ Tabbed Navigation (No Scrolling Required):
1. **🔌 Connection Tab**: ESP32 connection, system mode selection
2. **🔍 Sensors Tab**: Real-time sensor status checking for all 5 sensors
3. **📊 Data Collection Tab**: Configurable data collection with progress tracking
4. **⚙️ Motor Control Tab**: Complete motor control interface
5. **📋 System Log Tab**: Color-coded logging with control buttons

### 🎛️ System Modes:
- **🔧 Manual Mode**: Full control over all operations
- **🚀 Demo Mode**: Automated workflow (connect → check sensors → collect data)

### 📊 Data Collection Configuration:
- **Sampling Rate**: 50 Hz (configurable in `include/config.h`)
- **Window Duration**: 4 seconds (configurable in `include/config.h`)
- **Data Channels**: 6 channels (Acc X,Y,Z + Gyro X,Y,Z)
- **Output Format**: CSV optimized for Edge Impulse training

### ⚙️ Motor Control Features:
- **Start/Stop Control**: Easy motor on/off operation
- **Speed Control**: Adjustable from 10-1000 RPM with real-time slider
- **Direction Control**: Switch between Clockwise and Counter-Clockwise
- **Status Display**: Real-time motor status indicator

## 🔌 Hardware Connections

### ESP32 Pin Configuration:
```
I2C (MPU6050):
- GPIO 19 → SDA
- GPIO 22 → SCL

Digital Sensors:
- GPIO 27 → DS18B20 (OneWire)
- GPIO 2  → Encoder
- GPIO 4  → MAX471

Motor Driver (DRV8825):
- GPIO 25 → STEP
- GPIO 26 → DIR
- GPIO 14 → ENABLE
- GPIO 12 → FAULT
```

## 🚀 Quick Start Guide

### 1. Hardware Setup
- Connect all sensors according to pin configuration above
- Ensure DRV8825 motor driver is properly wired to motor and power supply
- Connect ESP32 to computer via USB

### 2. Upload Firmware
```bash
pio run --target upload
```

### 3. Run GUI Application
```bash
cd python_scripts
pip install -r requirements.txt
python industrial_predictive_maintenance.py
```

### 4. Basic Operation:
1. **Connect**: Select COM port and click "🔌 Connect"
2. **Check Sensors**: Click "🔍 Check Sensors" to verify all connections
3. **Collect Data**: Configure label and duration, then click "📊 Start Collection"
4. **Motor Control**: Use motor control tab to test motor operation
5. **View Data**: Click "📁 Open Data Folder" to access collected CSV files

### 5. Data Collection for ML Training:
- **Labels Available**: normal, imbalance, misalignment, bearing_defect, looseness
- **Default Duration**: 20 seconds (5 windows of 4 seconds each)
- **Output**: `collected_data/industrial_data_YYYYMMDD_HHMMSS/*.csv`
- **Format**: `timestamp,accX,accY,accZ,gyroX,gyroY,gyroZ`

## 📊 Data Collection Parameters (Configurable)

Edit `include/config.h` to modify:
```cpp
#define DATA_COLLECTION_RATE_HZ    50      // Sampling frequency
#define WINDOW_DURATION_SECONDS    4       // Window size
#define DATA_CHANNELS              6       // Acc+Gyro channels
#define SAMPLES_PER_WINDOW         200     // Total samples per window
```

## 🔧 ESP32 Motor Control Commands

The firmware responds to serial commands:
```cpp
MOTOR_START     → MOTOR_START_ACK
MOTOR_STOP      → MOTOR_STOP_ACK
MOTOR_SPEED:100 → MOTOR_SPEED_ACK:100
MOTOR_DIR:1     → MOTOR_DIR_ACK:1     (1=CW, 0=CCW)
```

## 📋 GUI Requirements

### Python Dependencies:
```bash
pip install pyserial tkinter
```

### System Requirements:
- **OS**: Windows 10/11, macOS, Linux
- **Screen Resolution**: Minimum 1200×700 (recommended 1400×800)
- **Python**: 3.7 or higher

## 🎯 Training Data Collection

### For Edge Impulse ML Training:
1. **Collect Data**: Use GUI to collect data for each fault type
2. **Upload**: Upload CSV files to Edge Impulse
3. **Configure**: Set up 6-channel data (Acc+Gyro) at 50Hz
4. **Train**: Train your TinyML model
5. **Deploy**: Deploy back to ESP32

### Data Format:
```csv
timestamp,accX,accY,accZ,gyroX,gyroY,gyroZ
1692915200.123,0.123,-0.456,9.812,0.012,0.034,-0.023
1692915200.143,0.124,-0.457,9.813,0.013,0.035,-0.022
...
```

## 🐛 Troubleshooting

### Common Issues:
1. **Connection Failed**: Check COM port and ensure ESP32 is powered
2. **Sensor Not Detected**: Verify wiring and power connections
3. **Motor Not Working**: Check DRV8825 connections and power supply
4. **GUI Not Starting**: Install required Python dependencies

### Debug Features:
- **Real-time Logging**: All operations logged with timestamps
- **Sensor Status**: Live sensor connection status
- **Error Messages**: Color-coded error and warning messages

## 📈 System Features

### ✅ Core Features:
- [x] Complete GUI interface with tabbed navigation
- [x] Real-time sensor status checking (5 sensors)
- [x] Configurable data collection (50Hz, 4s windows, 6 channels)
- [x] Full motor control (speed, direction, start/stop)
- [x] Professional logging system
- [x] Dual mode operation (Manual/Demo)
- [x] CSV data export optimized for ML training
- [x] Edge Impulse compatibility

### ✅ Technical Features:
- [x] Modular firmware architecture
- [x] Hardware abstraction layer
- [x] Robust error handling
- [x] Real-time data streaming
- [x] Configurable parameters
- [x] Professional code structure

## 📝 Development Notes

### Recent Changes:
- **Consolidated** all Python functionality into single GUI application
- **Added** complete motor control interface
- **Improved** data collection format for TinyML
- **Enhanced** GUI with tabbed navigation (no scrolling)
- **Updated** firmware with motor command handling
- **Fixed** sensor detection and status reporting

### Future Enhancements:
- [ ] MQTT integration for remote monitoring
- [ ] Grafana dashboard integration
- [ ] Advanced ML model deployment
- [ ] Real-time fault detection alerts
- [ ] Data visualization in GUI

## 📄 License

MIT License - Feel free to use and modify for your projects.

---

## 🤝 Contributing

Contributions are welcome! Please ensure:
- Code follows the existing structure
- Add appropriate comments
- Test all functionality
- Update documentation

---

**🏭 Industrial Predictive Maintenance System V2 - Complete IoT Solution for Motor Health Monitoring**