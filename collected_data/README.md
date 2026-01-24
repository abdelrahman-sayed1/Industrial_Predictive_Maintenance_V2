# Data Storage Directory

This folder contains all collected sensor data for the Industrial Predictive Maintenance System.

## Structure

```
collected_data/
├── edge_impulse/           # Edge Impulse training data
│   └── <session_id>/      # Timestamped session folders
│       ├── normal.0.csv   # Normal operation data
│       ├── imbalance.0.csv # Imbalance fault data
│       ├── misalignment.0.csv # Misalignment data
│       ├── bearing_defect.0.csv # Bearing fault data
│       └── looseness.0.csv # Looseness data
```

## Data Format

- **CSV files** with 512 samples each
- **Columns**: `timestamp,accX,accY,accZ`
- **Sample rate**: 8 kHz (0.125ms intervals)
- **File naming**: `<label>.<id>.csv`

## How to Collect Data

1. Run the GUI: `python python_scripts/run_gui.py`
2. Connect to ESP32
3. Select data label and collection time
4. Click "Start Collection"
5. Data will be saved here automatically

## Usage

- Upload the `edge_impulse/<session_id>/` folder to Edge Impulse for ML training
- Each session creates a new timestamped folder to organize data
