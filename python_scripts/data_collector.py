#!/usr/bin/env python3
"""
ESP32 Data Collector - Professional Edition
Receives data via Serial and saves to CSV files
Compatible with Windows, Linux, and macOS
"""

import serial
import serial.tools.list_ports
import csv
import time
from datetime import datetime
import os
import sys

class Colors:
    """ANSI color codes for terminal output"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

class DataCollector:
    """Handles serial communication and CSV data logging"""
    
    def __init__(self, port='COM8', baudrate=115200):
        self.port = port
        self.baudrate = baudrate
        self.ser = None
        self.features_file = None
        self.raw_data_file = None
        self.features_writer = None
        self.raw_writer = None
        
        # Create output directory
        os.makedirs('collected_data', exist_ok=True)
    
    def connect(self):
        """Establish serial connection with ESP32"""
        print(f"{Colors.OKBLUE}Connecting to ESP32 on {self.port}...{Colors.ENDC}")
        
        try:
            self.ser = serial.Serial(self.port, self.baudrate, timeout=0.5)
            time.sleep(1)
            
            # Drain any leftover data
            while self.ser.in_waiting:
                self.ser.read()
            
            # Just accept connection after small delay
            print(f"{Colors.OKGREEN}[OK] Connected successfully{Colors.ENDC}\n")
            return True
            
        except serial.SerialException as e:
            print(f"{Colors.FAIL}[ERROR] Connection error: {e}{Colors.ENDC}")
            return False
    
    def initialize_csv_files(self):
        """Create CSV files with appropriate headers"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Features CSV file
        features_path = f'collected_data/features_{timestamp}.csv'
        self.features_file = open(features_path, 'w', newline='', encoding='utf-8')
        self.features_writer = csv.writer(self.features_file)
        self.features_writer.writerow([
            'timestamp', 'rms_x', 'rms_y', 'rms_z',
            'peak_x', 'peak_y', 'peak_z',
            'std_x', 'std_y', 'std_z',
            'fft_1x', 'fft_2x', 'fft_3x',
            'high_freq_power', 'spectral_kurtosis', 'crest_factor',
            'rpm', 'current', 'temperature', 'label'
        ])
        
        # Raw data CSV file
        raw_path = f'collected_data/raw_data_{timestamp}.csv'
        self.raw_data_file = open(raw_path, 'w', newline='', encoding='utf-8')
        self.raw_writer = csv.writer(self.raw_data_file)
        self.raw_writer.writerow([
            'window_id', 'sample_index', 'accel_x', 'accel_y', 'accel_z', 'label'
        ])
        
        print(f"{Colors.OKGREEN}[OK] Created: {features_path}{Colors.ENDC}")
        print(f"{Colors.OKGREEN}[OK] Created: {raw_path}{Colors.ENDC}\n")
    
    def collect_state(self, state_name, command):
        """Collect data for a specific fault state"""
        print(f"\n{Colors.HEADER}{'='*60}{Colors.ENDC}")
        print(f"{Colors.HEADER}{Colors.BOLD}  STATE: {state_name.upper()}{Colors.ENDC}")
        print(f"{Colors.HEADER}{'='*60}{Colors.ENDC}")
        
        input(f"\n{Colors.WARNING}► Set up {state_name} condition, then press ENTER...{Colors.ENDC}")
        
        # Send command to ESP32
        self.ser.write(f"{command}\n".encode())
        time.sleep(0.5)
        
        feature_count = 0
        raw_window_count = 0
        
        print(f"{Colors.OKCYAN}Collecting data (5 minutes)...{Colors.ENDC}\n")
        
        collecting_session = True
        raw_samples = []
        session_start = time.time()
        session_timeout = 310  # 5 minutes + 10 second buffer
        
        while collecting_session:
            if time.time() - session_start > session_timeout:
                print(f"\n\n{Colors.OKGREEN}[OK] Collection complete (timeout)!{Colors.ENDC}")
                break
                
            if not self.ser.in_waiting:
                time.sleep(0.01)
                continue
            
            try:
                line = self.ser.readline().decode('utf-8', errors='ignore').strip()
            except:
                continue
            
            if not line:
                continue
            
            # Parse feature data (format: label,timestamp,rms_x,rms_y,...)
            if line.startswith(state_name) and ',' in line and len(line.split(',')) > 3:
                parts = line.split(',')
                if len(parts) >= 10:  # Should have at least label, timestamp, and some features
                    self.features_writer.writerow(parts)
                    self.features_file.flush()
                    feature_count += 1
                    print(f"\r  ► Features: {feature_count:3d} | Raw windows: {raw_window_count:2d}", 
                          end='', flush=True)
            
            # Parse raw window data
            elif line == "RAW_WINDOW_START":
                raw_window_count += 1
                raw_samples = []
                
            elif line == "RAW_DATA_START":
                raw_samples = []
                
            elif line == "RAW_DATA_END":
                # Write collected samples
                for idx, sample in enumerate(raw_samples):
                    parts = sample.split(',')
                    if len(parts) == 3:
                        self.raw_writer.writerow([raw_window_count, idx] + parts + [state_name])
                self.raw_data_file.flush()
                
            elif line and line[0].isdigit() and ',' in line:
                # Raw acceleration data (x,y,z format)
                raw_samples.append(line)
            
            elif line.startswith("SESSION_STATS"):
                collecting_session = False
                print(f"\n\n{Colors.OKGREEN}[OK] Collection complete!{Colors.ENDC}")
                break
        
        print(f"  Features: {feature_count}")
        print(f"  Raw windows: {raw_window_count}")
        time.sleep(2)
    
    def run_collection_plan(self):
        """Execute full data collection plan"""
        print(f"{Colors.HEADER}{Colors.BOLD}")
        print("╔════════════════════════════════════════╗")
        print("║   PREDICTIVE MAINTENANCE              ║")
        print("║   Data Collection Plan                ║")
        print("╚════════════════════════════════════════╝")
        print(f"{Colors.ENDC}")
        
        print("\nCollection Plan:")
        print("  1. Normal (Baseline) - 5 minutes")
        print("  2. Imbalance - 5 minutes")
        print("  3. Misalignment - 5 minutes")
        print("  4. Bearing Defect - 5 minutes")
        print("  5. Mechanical Looseness - 5 minutes")
        print("\nTotal time: ~25 minutes\n")
        
        input("Press ENTER to begin...")
        
        self.initialize_csv_files()
        
        # Collect data for each state
        self.collect_state("normal", "START_NORMAL")
        self.collect_state("imbalance", "START_IMBALANCE")
        self.collect_state("misalignment", "START_MISALIGNMENT")
        self.collect_state("bearing_defect", "START_BEARING")
        self.collect_state("looseness", "START_LOOSENESS")
        
        # Close files
        self.features_file.close()
        self.raw_data_file.close()
        
        print(f"\n{Colors.OKGREEN}{Colors.BOLD}")
        print("╔════════════════════════════════════════╗")
        print("║   DATA COLLECTION COMPLETE!           ║")
        print("╚════════════════════════════════════════╝")
        print(f"{Colors.ENDC}")
        
        print("\nData saved to collected_data/ folder")
        print("Ready for model training with Edge Impulse")
    
    def close(self):
        """Close serial connection"""
        if self.ser:
            self.ser.close()

def select_port():
    """Let user select COM port"""
    ports = list(serial.tools.list_ports.comports())
    
    if not ports:
        print("No serial ports found!")
        return None
    
    print("\nAvailable Serial Ports:")
    for i, port in enumerate(ports):
        print(f"  {i}: {port.device} - {port.description}")
    
    while True:
        try:
            choice = input(f"\nSelect port number [0-{len(ports)-1}]: ")
            idx = int(choice)
            if 0 <= idx < len(ports):
                return ports[idx].device
        except:
            pass
        print("Invalid selection")

def main():
    """Main entry point"""
    port = select_port()
    if not port:
        return
    
    collector = DataCollector(port=port, baudrate=115200)
    
    if not collector.connect():
        return
    
    try:
        collector.run_collection_plan()
    except KeyboardInterrupt:
        print(f"\n{Colors.WARNING}Collection interrupted by user{Colors.ENDC}")
    finally:
        collector.close()

if __name__ == "__main__":
    main()
