#!/usr/bin/env python3
"""
Advanced Data Collector - Raw Data + Python Feature Extraction
Receives raw x,y,z acceleration data from ESP32
Computes RMS, Peak, Std Dev, FFT, Kurtosis, Crest Factor with NumPy/SciPy
"""

import serial
import serial.tools.list_ports
import csv
import time
from datetime import datetime
import os
import sys
import numpy as np
from scipy.fft import fft
from scipy.stats import kurtosis

class AdvancedCollector:
    """Collects raw data and extracts advanced features"""
    
    def __init__(self, port='COM8', baudrate=115200, sample_size=512):
        self.port = port
        self.baudrate = baudrate
        self.sample_size = sample_size
        self.ser = None
        self.features_file = None
        self.raw_data_file = None
        self.features_writer = None
        self.raw_writer = None
        
        os.makedirs('collected_data', exist_ok=True)
    
    def connect(self):
        """Establish serial connection"""
        print(f"🔌 Connecting to ESP32 on {self.port}...")
        try:
            self.ser = serial.Serial(self.port, self.baudrate, timeout=1)
            time.sleep(1)
            while self.ser.in_waiting:
                self.ser.read()
            print("✅ Connected!\n")
            return True
        except serial.SerialException as e:
            print(f"❌ Error: {e}")
            return False
    
    def initialize_csv_files(self):
        """Create CSV output files"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Features CSV
        features_path = f'collected_data/features_{timestamp}.csv'
        self.features_file = open(features_path, 'w', newline='', encoding='utf-8')
        self.features_writer = csv.writer(self.features_file)
        self.features_writer.writerow([
            'timestamp',
            'rms_accel_x', 'rms_accel_y', 'rms_accel_z',
            'rms_gyro_x', 'rms_gyro_y', 'rms_gyro_z',
            'peak_accel_x', 'peak_accel_y', 'peak_accel_z',
            'peak_gyro_x', 'peak_gyro_y', 'peak_gyro_z',
            'std_accel_x', 'std_accel_y', 'std_accel_z',
            'std_gyro_x', 'std_gyro_y', 'std_gyro_z',
            'fft_accel', 'fft_gyro', 'crest_factor',
            'rpm', 'voltage', 'current', 'temperature', 'label'
        ])
        
        # Raw data CSV
        raw_path = f'collected_data/raw_data_{timestamp}.csv'
        self.raw_data_file = open(raw_path, 'w', newline='', encoding='utf-8')
        self.raw_writer = csv.writer(self.raw_data_file)
        self.raw_writer.writerow(['window_id', 'sample_idx', 'accel_x', 'accel_y', 'accel_z', 'gyro_x', 'gyro_y', 'gyro_z', 'rpm', 'voltage', 'current', 'temperature', 'label'])
        
        print(f"✅ Created: {features_path}")
        print(f"✅ Created: {raw_path}\n")
    
    def extract_features(self, accel_x, accel_y, accel_z, gyro_x, gyro_y, gyro_z):
        """Extract features from 6-axis IMU data"""
        features = {}
        
        # Acceleration features
        features['rms_accel_x'] = np.sqrt(np.mean(accel_x**2))
        features['rms_accel_y'] = np.sqrt(np.mean(accel_y**2))
        features['rms_accel_z'] = np.sqrt(np.mean(accel_z**2))
        
        features['peak_accel_x'] = np.max(np.abs(accel_x))
        features['peak_accel_y'] = np.max(np.abs(accel_y))
        features['peak_accel_z'] = np.max(np.abs(accel_z))
        
        features['std_accel_x'] = np.std(accel_x)
        features['std_accel_y'] = np.std(accel_y)
        features['std_accel_z'] = np.std(accel_z)
        
        # Gyroscope features
        features['rms_gyro_x'] = np.sqrt(np.mean(gyro_x**2))
        features['rms_gyro_y'] = np.sqrt(np.mean(gyro_y**2))
        features['rms_gyro_z'] = np.sqrt(np.mean(gyro_z**2))
        
        features['peak_gyro_x'] = np.max(np.abs(gyro_x))
        features['peak_gyro_y'] = np.max(np.abs(gyro_y))
        features['peak_gyro_z'] = np.max(np.abs(gyro_z))
        
        features['std_gyro_x'] = np.std(gyro_x)
        features['std_gyro_y'] = np.std(gyro_y)
        features['std_gyro_z'] = np.std(gyro_z)
        
        # FFT for both acceleration and gyroscope
        fft_accel = np.max(np.abs(fft(accel_x + accel_y + accel_z)))
        fft_gyro = np.max(np.abs(fft(gyro_x + gyro_y + gyro_z)))
        
        features['fft_accel'] = fft_accel
        features['fft_gyro'] = fft_gyro
        
        # Combined crest factor
        rms_combined = np.sqrt(
            features['rms_accel_x']**2 + features['rms_accel_y']**2 + 
            features['rms_accel_z']**2 + features['rms_gyro_x']**2 + 
            features['rms_gyro_y']**2 + features['rms_gyro_z']**2
        )
        peak_combined = max(
            features['peak_accel_x'], features['peak_accel_y'], features['peak_accel_z'],
            features['peak_gyro_x'], features['peak_gyro_y'], features['peak_gyro_z']
        )
        features['crest_factor'] = peak_combined / (rms_combined + 0.001)
        
        return features
    
    def collect_state(self, state_name, command):
        """Collect data for a fault condition"""
        print(f"\n{'='*60}")
        print(f"  STATE: {state_name.upper()}")
        print(f"{'='*60}\n")
        
        input(f"⚠️  Set up {state_name} condition, then press ENTER...")
        
        self.ser.write(f"{command}\n".encode())
        time.sleep(0.5)
        
        features_count = 0
        window_count = 0
        raw_samples = []
        sensor_data = {}
        session_start = time.time()
        
        print(f"📊 Collecting raw data (5 minutes)...\n")
        
        while time.time() - session_start < 310:  # 5 min + buffer
            if not self.ser.in_waiting:
                time.sleep(0.001)
                continue
            
            try:
                line = self.ser.readline().decode('utf-8', errors='ignore').strip()
            except:
                continue
            
            if not line:
                continue
            
            # Detect collection markers
            if "COLLECTION_START" in line:
                print(f"✅ Collection started: {state_name}")
                continue
            elif "COLLECTION_END" in line:
                print(f"\n✅ Collection complete!")
                break
            elif "RAW_WINDOW_START" in line:
                # Parse: RAW_WINDOW_START,window_id,label,rpm,voltage,current,temperature
                parts = line.split(",")
                if len(parts) >= 7:
                    try:
                        sensor_data['window_id'] = int(parts[1])
                        sensor_data['label'] = parts[2]
                        sensor_data['rpm'] = float(parts[3])
                        sensor_data['voltage'] = float(parts[4])
                        sensor_data['current'] = float(parts[5])
                        sensor_data['temperature'] = float(parts[6])
                    except:
                        pass
                
                # Process previous window if exists
                if raw_samples:
                    accel_x = np.array([s[0] for s in raw_samples])
                    accel_y = np.array([s[1] for s in raw_samples])
                    accel_z = np.array([s[2] for s in raw_samples])
                    gyro_x = np.array([s[3] for s in raw_samples])
                    gyro_y = np.array([s[4] for s in raw_samples])
                    gyro_z = np.array([s[5] for s in raw_samples])
                    
                    features = self.extract_features(accel_x, accel_y, accel_z, gyro_x, gyro_y, gyro_z)
                    
                    row = [
                        int(time.time() * 1000),
                        features['rms_accel_x'], features['rms_accel_y'], features['rms_accel_z'],
                        features['rms_gyro_x'], features['rms_gyro_y'], features['rms_gyro_z'],
                        features['peak_accel_x'], features['peak_accel_y'], features['peak_accel_z'],
                        features['peak_gyro_x'], features['peak_gyro_y'], features['peak_gyro_z'],
                        features['std_accel_x'], features['std_accel_y'], features['std_accel_z'],
                        features['std_gyro_x'], features['std_gyro_y'], features['std_gyro_z'],
                        features['fft_accel'], features['fft_gyro'], features['crest_factor'],
                        sensor_data.get('rpm', 0.0),
                        sensor_data.get('voltage', 0.0),
                        sensor_data.get('current', 0.0),
                        sensor_data.get('temperature', -127.0),
                        state_name
                    ]
                    self.features_writer.writerow(row)
                    self.features_file.flush()
                    features_count += 1
                
                window_count += 1
                raw_samples = []
                print(f"\r  ► Features: {features_count:3d} | Windows: {window_count:2d}", end='', flush=True)
            
            elif "," in line and len(line.split(",")) == 6:
                # Raw 6-axis data: accel_x,accel_y,accel_z,gyro_x,gyro_y,gyro_z
                try:
                    parts = line.split(",")
                    x, y, z = float(parts[0]), float(parts[1]), float(parts[2])
                    gx, gy, gz = float(parts[3]), float(parts[4]), float(parts[5])
                    raw_samples.append((x, y, z, gx, gy, gz))
                    
                    # Write to raw CSV
                    self.raw_writer.writerow([
                        window_count, len(raw_samples)-1, x, y, z, gx, gy, gz,
                        sensor_data.get('rpm', 0.0),
                        sensor_data.get('voltage', 0.0),
                        sensor_data.get('current', 0.0),
                        sensor_data.get('temperature', -127.0),
                        state_name
                    ])
                except:
                    pass
        
        self.raw_data_file.flush()
        time.sleep(1)
    
    def run(self):
        """Main collection routine"""
        print("\n" + "="*60)
        print("  PREDICTIVE MAINTENANCE - Advanced Data Collector")
        print("  Raw Arduino Streaming + Python Feature Extraction")
        print("="*60 + "\n")
        
        print("Collection Plan:")
        print("  1. Normal (Baseline) - 5 minutes")
        print("  2. Imbalance - 5 minutes")
        print("  3. Misalignment - 5 minutes")
        print("  4. Bearing Defect - 5 minutes")
        print("  5. Mechanical Looseness - 5 minutes")
        print("\nTotal time: ~25 minutes\n")
        
        input("Press ENTER to begin...")
        
        self.initialize_csv_files()
        
        # Collect all states
        self.collect_state("normal", "START_NORMAL")
        self.collect_state("imbalance", "START_IMBALANCE")
        self.collect_state("misalignment", "START_MISALIGNMENT")
        self.collect_state("bearing_defect", "START_BEARING")
        self.collect_state("looseness", "START_LOOSENESS")
        
        # Close files
        self.features_file.close()
        self.raw_data_file.close()
        
        print(f"\n{'='*60}")
        print("✅ DATA COLLECTION COMPLETE!")
        print(f"{'='*60}\n")
        print("✨ Data ready for Edge Impulse model training!")
    
    def close(self):
        """Close connection"""
        if self.ser:
            self.ser.close()

def select_port():
    """Let user select COM port"""
    ports = list(serial.tools.list_ports.comports())
    
    if not ports:
        print("❌ No serial ports found!")
        return None
    
    print("\n📡 Available Serial Ports:")
    for i, port in enumerate(ports):
        print(f"  {i}: {port.device} - {port.description}")
    
    while True:
        try:
            choice = input(f"\nSelect port [0-{len(ports)-1}]: ")
            idx = int(choice)
            if 0 <= idx < len(ports):
                return ports[idx].device
        except:
            pass
        print("❌ Invalid selection")

def main():
    port = select_port()
    if not port:
        return
    
    collector = AdvancedCollector(port=port, baudrate=115200, sample_size=512)
    
    if not collector.connect():
        return
    
    try:
        collector.run()
    except KeyboardInterrupt:
        print(f"\n⚠️  Collection interrupted by user")
    finally:
        collector.close()

if __name__ == "__main__":
    main()
