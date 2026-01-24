#!/usr/bin/env python3
"""
Advanced Data Processor - Feature Extraction with NumPy/SciPy
Takes raw acceleration data from ESP32 and computes all features
"""

import numpy as np
from scipy import signal
from scipy.fft import fft
import csv
import time
import os

class FeatureExtractor:
    """Extracts ML-ready features from raw acceleration data"""
    
    def __init__(self, sample_rate=8000):
        self.sample_rate = sample_rate
        self.nyquist = sample_rate / 2
        
    def extract_all_features(self, accel_x, accel_y, accel_z):
        """Extract comprehensive feature set from raw data"""
        features = {}
        
        # Time domain features
        features['rms_x'] = np.sqrt(np.mean(accel_x**2))
        features['rms_y'] = np.sqrt(np.mean(accel_y**2))
        features['rms_z'] = np.sqrt(np.mean(accel_z**2))
        
        features['peak_x'] = np.max(np.abs(accel_x))
        features['peak_y'] = np.max(np.abs(accel_y))
        features['peak_z'] = np.max(np.abs(accel_z))
        
        features['std_x'] = np.std(accel_x)
        features['std_y'] = np.std(accel_y)
        features['std_z'] = np.std(accel_z)
        
        # Crest factor (peak/RMS)
        features['crest_x'] = features['peak_x'] / (features['rms_x'] + 1e-8)
        features['crest_y'] = features['peak_y'] / (features['rms_y'] + 1e-8)
        features['crest_z'] = features['peak_z'] / (features['rms_z'] + 1e-8)
        
        # FFT features
        features.update(self._extract_fft_features(accel_x, accel_y, accel_z))
        
        # Kurtosis (statistical measure of impulsiveness)
        from scipy.stats import kurtosis
        features['kurtosis_x'] = kurtosis(accel_x)
        features['kurtosis_y'] = kurtosis(accel_y)
        features['kurtosis_z'] = kurtosis(accel_z)
        
        # Skewness
        from scipy.stats import skew
        features['skew_x'] = skew(accel_x)
        features['skew_y'] = skew(accel_y)
        features['skew_z'] = skew(accel_z)
        
        return features
    
    def _extract_fft_features(self, accel_x, accel_y, accel_z):
        """Extract frequency domain features using FFT"""
        features = {}
        
        # Compute FFT
        fft_x = np.abs(fft(accel_x))[:len(accel_x)//2]
        fft_y = np.abs(fft(accel_y))[:len(accel_y)//2]
        fft_z = np.abs(fft(accel_z))[:len(accel_z)//2]
        
        # Frequency bins
        freq_bins = np.fft.fftfreq(len(accel_x), 1/self.sample_rate)[:len(accel_x)//2]
        
        # Peak frequency and magnitude
        peak_idx_x = np.argmax(fft_x[1:]) + 1  # Skip DC
        peak_idx_y = np.argmax(fft_y[1:]) + 1
        peak_idx_z = np.argmax(fft_z[1:]) + 1
        
        features['dominant_freq_x'] = freq_bins[peak_idx_x]
        features['dominant_freq_y'] = freq_bins[peak_idx_y]
        features['dominant_freq_z'] = freq_bins[peak_idx_z]
        
        features['dominant_mag_x'] = fft_x[peak_idx_x]
        features['dominant_mag_y'] = fft_y[peak_idx_y]
        features['dominant_mag_z'] = fft_z[peak_idx_z]
        
        # High frequency power (>1kHz)
        high_freq_idx = freq_bins > 1000
        features['high_freq_power'] = np.sum(fft_x[high_freq_idx]**2 + fft_y[high_freq_idx]**2 + fft_z[high_freq_idx]**2)
        
        # Total power
        features['total_power'] = np.sum(fft_x**2 + fft_y**2 + fft_z**2)
        
        # Energy in different frequency bands
        features['low_freq_power'] = np.sum(fft_x[freq_bins < 100]**2 + fft_y[freq_bins < 100]**2 + fft_z[freq_bins < 100]**2)
        features['mid_freq_power'] = np.sum(fft_x[(freq_bins >= 100) & (freq_bins < 1000)]**2 + fft_y[(freq_bins >= 100) & (freq_bins < 1000)]**2 + fft_z[(freq_bins >= 100) & (freq_bins < 1000)]**2)
        
        return features

class RawDataCollector:
    """Collects raw acceleration data from serial and processes it"""
    
    def __init__(self, port='COM8', baudrate=115200, sample_size=512):
        import serial
        self.port = port
        self.baudrate = baudrate
        self.sample_size = sample_size
        self.ser = None
        self.extractor = FeatureExtractor(sample_rate=8000)
        
    def connect(self):
        """Connect to device"""
        import serial
        try:
            self.ser = serial.Serial(self.port, self.baudrate, timeout=1)
            time.sleep(1)
            print(f"✓ Connected to {self.port}")
            return True
        except Exception as e:
            print(f"✗ Failed to connect: {e}")
            return False
    
    def read_raw_window(self):
        """Read one window of raw acceleration data from serial"""
        accel_x = []
        accel_y = []
        accel_z = []
        
        timeout_count = 0
        while len(accel_x) < self.sample_size:
            if not self.ser.in_waiting:
                timeout_count += 1
                if timeout_count > 1000:
                    return None  # Timeout
                time.sleep(0.001)
                continue
            
            timeout_count = 0
            try:
                line = self.ser.readline().decode('utf-8', errors='ignore').strip()
                
                # Skip non-data lines
                if not line or ',' not in line:
                    continue
                
                # Parse raw data (x,y,z format)
                parts = line.split(',')
                if len(parts) == 3:
                    try:
                        x, y, z = float(parts[0]), float(parts[1]), float(parts[2])
                        accel_x.append(x)
                        accel_y.append(y)
                        accel_z.append(z)
                    except:
                        continue
            except:
                continue
        
        return np.array(accel_x), np.array(accel_y), np.array(accel_z)
    
    def process_window(self, accel_x, accel_y, accel_z, label, timestamp):
        """Extract features from one window"""
        features = self.extractor.extract_all_features(accel_x, accel_y, accel_z)
        features['timestamp'] = timestamp
        features['label'] = label
        return features
    
    def close(self):
        """Close connection"""
        if self.ser:
            self.ser.close()


def main():
    """Main data collection with advanced processing"""
    import serial.tools.list_ports
    
    # Port selection
    ports = list(serial.tools.list_ports.comports())
    print("\nAvailable Ports:")
    for i, port in enumerate(ports):
        print(f"  {i}: {port.device}")
    
    idx = int(input("Select port: "))
    port = ports[idx].device
    
    # Initialize
    collector = RawDataCollector(port=port, sample_size=512)
    if not collector.connect():
        return
    
    # Create output file
    os.makedirs('collected_data', exist_ok=True)
    timestamp_str = time.strftime("%Y%m%d_%H%M%S")
    output_file = f"collected_data/features_ml_{timestamp_str}.csv"
    
    # Get all feature names
    test_window = collector.read_raw_window()
    if test_window is None:
        print("Failed to read initial data")
        return
    
    test_features = collector.process_window(test_window[0], test_window[1], test_window[2], "test", 0)
    fieldnames = ['timestamp', 'label'] + list(test_features.keys())[:-2]  # Remove timestamp/label from feature keys
    
    # Write CSV header
    with open(output_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
    
    print(f"\nCollecting data to: {output_file}")
    print("Features to extract:")
    for fname in fieldnames[2:]:
        print(f"  - {fname}")
    
    # Collection loop
    window_count = 0
    try:
        while True:
            accel_x, accel_y, accel_z = collector.read_raw_window()
            if accel_x is None:
                print("Timeout reading data")
                break
            
            window_count += 1
            timestamp = int(time.time() * 1000)
            
            features = collector.process_window(accel_x, accel_y, accel_z, "normal", timestamp)
            
            # Write to CSV
            with open(output_file, 'a', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writerow({k: features.get(k, '') for k in fieldnames})
            
            print(f"Window {window_count}: RMS_X={features['rms_x']:.4f}, Peak_X={features['peak_x']:.4f}, "
                  f"Crest_X={features['crest_x']:.4f}, Dom_Freq={features['dominant_freq_x']:.1f}Hz")
    
    except KeyboardInterrupt:
        print(f"\n✓ Collected {window_count} windows")
    finally:
        collector.close()

if __name__ == "__main__":
    main()
