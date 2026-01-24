# Industrial Predictive Maintenance System

## 🏭 ALL-IN-ONE SYSTEM

This folder contains the complete Industrial Predictive Maintenance system in a single Python file.

## 📁 Files

- **`industrial_predictive_maintenance.py`** - Complete system with GUI, sensor checking, data collection
- **`requirements.txt`** - Python dependencies
- **`README.md`** - This documentation
- **`GUI_README.md`** - GUI usage guide

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the System
```bash
python industrial_predictive_maintenance.py
```

### 3. Connect to ESP32
- Select your COM port
- Click "Connect"
- System will auto-check sensors

### 4. Choose Mode
- **🔧 Manual Mode** - Full control
- **🚀 Demo Mode** - Automated workflow

### 5. Collect Data
- Select data label (normal, imbalance, etc.)
- Set duration
- Click "Start Collection"

## 📊 Data Storage

Data is automatically saved to:
```
../collected_data/edge_impulse/session_YYYY-MM-DD_HH-MM-SS/
├── normal.csv
├── imbalance.csv
├── misalignment.csv
└── bearing_defect.csv
```

## ✨ Features

- ✅ ESP32 Connection & Communication
- ✅ Real-time Sensor Status Checking
- ✅ Data Collection & Storage
- ✅ Automated Demo Mode
- ✅ CSV Export for ML Training
- ✅ Real-time Logging
- ✅ Progress Tracking

## 🎯 System Requirements

- Python 3.7+
- ESP32 with uploaded firmware
- Serial connection (USB)
- Sensors: MPU6050, Encoder, MAX471, DS18B20, DRV8825

## 📞 Support

The all-in-one system includes everything needed for industrial predictive maintenance data collection and ML training preparation.
