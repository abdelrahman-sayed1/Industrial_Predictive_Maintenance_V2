import sys
sys.path.insert(0, 'python_scripts')
from data_collector import DataCollector

dc = DataCollector(port='COM8', baudrate=115200)
if dc.connect():
    print("Ready to receive data...")
    try:
        while True:
            if dc.ser.in_waiting:
                line = dc.ser.readline().decode('utf-8', errors='ignore').strip()
                if line:
                    print(f"Device: {line}")
    except KeyboardInterrupt:
        print("\nConnection closed")
        dc.ser.close()
else:
    print("Connection failed")
