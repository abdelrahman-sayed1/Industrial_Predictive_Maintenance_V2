# GUI Data Collection Controller

## Overview
Simple Python GUI for controlling the Industrial Predictive Maintenance data collection system.

## Features
- **Start/Stop Control**: Easy button control for data collection
- **Data Label Selection**: Choose from 5 fault types (normal, imbalance, misalignment, bearing_defect, looseness)
- **Collection Time**: Configurable duration (1-30 minutes)
- **Serial Port Selection**: Automatic port detection and connection management
- **Real-time Status**: Progress bar and time remaining display
- **Live Logging**: Real-time display of ESP32 messages and system events

## Usage

### 1. Install Dependencies
```bash
cd python_scripts
pip install -r requirements.txt
```

### 2. Run the GUI
```bash
python gui_controller.py
```

### 3. Connect and Collect
1. **Select Serial Port**: Choose your ESP32's COM port from the dropdown
2. **Click Connect**: Establish connection with the device
3. **Configure Collection**:
   - Select data label (fault type)
   - Set collection time in minutes
4. **Start Collection**: Click "Start Collection" button
5. **Monitor Progress**: Watch real-time progress and logs
6. **Stop if Needed**: Click "Stop Collection" to abort early

## GUI Layout

### Connection Section
- Serial port dropdown with refresh button
- Connect/Disconnect toggle
- Connection status indicator

### Configuration Section  
- Data label dropdown (5 fault types)
- Collection time spinner (1-30 minutes)

### Control Section
- Start Collection button
- Stop Collection button (disabled when not collecting)

### Status Section
- Current status display
- Progress bar (0-100%)
- Time remaining countdown

### Log Section
- Scrollable text area
- Timestamped messages
- ESP32 communication logs

## Data Labels Available
- **normal**: Healthy motor operation
- **imbalance**: Unbalanced motor condition
- **misalignment**: Shaft misalignment
- **bearing_defect**: Bearing wear/damage
- **looseness**: Mechanical looseness

## Technical Details
- Uses tkinter (built into Python)
- Threading for non-blocking collection
- Real-time serial communication
- Progress tracking with time estimation
- Clean shutdown handling

## Notes
- GUI automatically detects available serial ports
- Collection can be stopped at any time
- Progress updates every 100ms
- All ESP32 messages are logged for debugging
- Window close protection during active collection
