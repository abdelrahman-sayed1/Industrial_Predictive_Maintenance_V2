#!/usr/bin/env python3
"""
Industrial Predictive Maintenance - Professional GUI
Clean, professional interface for sensor data collection and motor control
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import serial
import serial.tools.list_ports
import threading
import time
import csv
import os
from datetime import datetime
import queue

class IndustrialMaintenanceGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Industrial Predictive Maintenance System")
        self.root.geometry("1200x800")
        self.root.configure(bg='#f0f0f0')
        
        # Variables
        self.serial_connection = None
        self.is_collecting = False
        self.motor_running = False
        self.data_queue = queue.Queue()
        self.collected_data = []  # Store actual sensor data
        self.collection_start_time = None  # Track when collection started
        self.data_points = 0
        self.status_var = tk.StringVar(value="Ready")
        
        # Create main container
        main_frame = ttk.Frame(root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # Create sections
        self.create_connection_section(main_frame)
        self.create_motor_control_section(main_frame)
        self.create_sensor_check_section(main_frame)
        self.create_data_collection_section(main_frame)
        self.create_log_section(main_frame)
        
        # Status bar
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
    
    def log(self, message):
        """Add message to log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        if hasattr(self, 'log_text'):
            self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
            self.log_text.see(tk.END)
        if hasattr(self, 'status_var'):
            self.status_var.set(message)
    
    def create_connection_section(self, parent):
        """Serial connection section"""
        frame = ttk.LabelFrame(parent, text="Serial Connection", padding="10")
        frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        frame.columnconfigure(1, weight=1)
        
        # Port selection
        ttk.Label(frame, text="Port:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.port_var = tk.StringVar()
        self.port_combo = ttk.Combobox(frame, textvariable=self.port_var, width=20)
        self.port_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 5))
        
        # Buttons
        ttk.Button(frame, text="Refresh Ports", command=self.refresh_ports).grid(row=0, column=2, padx=5)
        ttk.Button(frame, text="Connect", command=self.connect_serial).grid(row=0, column=3, padx=5)
        ttk.Button(frame, text="Disconnect", command=self.disconnect_serial).grid(row=0, column=4, padx=5)
        
        # Connection status
        self.connection_status = tk.StringVar(value="Disconnected")
        ttk.Label(frame, textvariable=self.connection_status, foreground="red").grid(row=0, column=5, padx=(10, 0))
        
        self.refresh_ports()
    
    def refresh_ports(self):
        """Refresh available serial ports"""
        ports = [port.device for port in serial.tools.list_ports.comports()]
        self.port_combo['values'] = ports
        if ports:
            self.port_combo.set(ports[0])
        self.log(f"Found {len(ports)} serial ports")
    
    def connect_serial(self):
        """Connect to serial port"""
        if not self.port_var.get():
            messagebox.showerror("Error", "Please select a serial port")
            return
        
        try:
            self.serial_connection = serial.Serial(self.port_var.get(), 921600, timeout=2)
            time.sleep(2)
            
            # Test connection
            self.serial_connection.write(b"PING\n")
            time.sleep(1)
            
            if self.serial_connection.in_waiting:
                response = self.serial_connection.readline().decode().strip()
                if "PONG" in response:
                    self.connection_status.set("Connected")
                    self.log(f"Connected to {self.port_var.get()}")
                    
                    # Enable controls
                    self.start_motor_btn.config(state=tk.NORMAL)
                    self.stop_motor_btn.config(state=tk.NORMAL)
                    self.collect_btn.config(state=tk.NORMAL)
                    
                    # Start data reader thread
                    self.start_data_reader()
                else:
                    raise Exception("No PONG response")
            else:
                raise Exception("No response from device")
                
        except Exception as e:
            messagebox.showerror("Connection Error", f"Failed to connect: {e}")
            self.log(f"Connection failed: {e}")
    
    def disconnect_serial(self):
        """Disconnect serial connection"""
        if self.serial_connection:
            self.serial_connection.close()
            self.serial_connection = None
            
        self.connection_status.set("Disconnected")
        self.log("Disconnected from serial port")
        
        # Disable controls
        self.start_motor_btn.config(state=tk.DISABLED)
        self.stop_motor_btn.config(state=tk.DISABLED)
        self.collect_btn.config(state=tk.DISABLED)
    
    def start_data_reader(self):
        """Start thread to read serial data"""
        def reader():
            while self.serial_connection and self.serial_connection.is_open:
                if self.serial_connection.in_waiting:
                    line = self.serial_connection.readline().decode().strip()
                    if line:
                        self.data_queue.put(line)
                time.sleep(0.01)
        
        thread = threading.Thread(target=reader, daemon=True)
        thread.start()
        
        # Start queue processor
        self.process_data_queue()
    
    def process_data_queue(self):
        """Process data from queue"""
        try:
            while not self.data_queue.empty():
                line = self.data_queue.get_nowait()
                self.process_serial_line(line)
        except queue.Empty:
            pass
        
        # Schedule next check
        self.root.after(50, self.process_data_queue)
    
    def process_serial_line(self, line):
        """Process incoming serial line"""
        if line.startswith("MOTOR_"):
            self.process_motor_status(line)
        elif line.startswith("SENSOR_"):
            self.process_sensor_status(line)
        elif line.startswith("COLLECTION_"):
            self.process_collection_status(line)
        elif "_DATA:" in line:
            self.process_sensor_data(line)
        elif line.startswith("ERROR:"):
            self.log(f"Error: {line[6:]}")
        # Log all data for debugging
        elif self.is_collecting:
            self.log(f"Data: {line}")
    
    def process_motor_status(self, line):
        """Process motor status updates"""
        if "MOTOR_STARTED" in line:
            self.motor_running = True
            self.motor_status.set("Motor: Running")
            self.log("Motor started")
        elif "MOTOR_STOPPED" in line:
            self.motor_running = False
            self.motor_status.set("Motor: Stopped")
            self.log("Motor stopped")
        elif "MOTOR_DIRECTION_SET" in line:
            self.log(f"Motor direction set: {line.split(':')[1]}")
    
    def process_sensor_status(self, line):
        """Process sensor check results"""
        if "SENSOR_CHECK_START" in line:
            self.log("Starting sensor check...")
        elif "SENSOR_CHECK_END" in line:
            self.log("Sensor check complete")
        else:
            # Update individual sensor status
            for sensor in self.sensor_status:
                if sensor in line:
                    status = "OK" if "OK" in line else "FAIL"
                    color = "green" if status == "OK" else "red"
                    self.sensor_status[sensor].set(f"{sensor}: {status}")
                    self.log(f"{sensor}: {status}")
    
    def process_collection_status(self, line):
        """Process collection status updates"""
        if "COLLECTION_START" in line:
            self.is_collecting = True
            self.collection_start_time = time.time()  # Record actual start time
            self.collect_btn.config(state=tk.DISABLED)
            self.stop_btn.config(state=tk.NORMAL)
            self.log(f"Started collection: {line.split(':')[1]}")
        elif "COLLECTION_END" in line:
            self.is_collecting = False
            self.collect_btn.config(state=tk.NORMAL)
            self.stop_btn.config(state=tk.DISABLED)
            self.progress['value'] = 100
            self.log(f"Collection ended: {line.split(':')[1]}")
    
    def clean_sensor_value(self, value_str):
        """Clean only severely malformed sensor values, preserve accurate data"""
        try:
            # Only fix obvious formatting errors, don't touch valid numbers
            if value_str.count('.') > 1:
                # Only fix if there are multiple decimal points (severe corruption)
                parts = value_str.split('.')
                # Keep first part and first decimal part, ignore the rest
                return parts[0] + '.' + parts[1]
            elif not value_str or value_str == '.':
                return "0.00"
            else:
                # Return original value if it looks reasonable
                return value_str
        except (ValueError, IndexError):
            return "0.00"  # Fallback for completely malformed values
    
    def clean_data_line(self, line):
        """Clean and validate incoming data line"""
        # Remove leading/trailing whitespace and quotes
        cleaned = line.strip().strip("'\"")
        
        # Skip empty lines
        if not cleaned:
            return None
        
        # Skip lines that don't start with known data prefixes
        valid_prefixes = ["MPU_DATA:", "ENCODER_DATA:", "POWER_DATA:", "TEMP_DATA:", "ALL_DATA:"]
        if not any(cleaned.startswith(prefix) for prefix in valid_prefixes):
            return None
        
        return cleaned
    
    def is_valid_timestamp(self, timestamp_str):
        """Check if timestamp string is a valid number"""
        try:
            int(timestamp_str)
            return True
        except ValueError:
            return False
    
    def process_sensor_data(self, line):
        """Process sensor data and update count"""
        if self.is_collecting:
            # Clean the data line first
            cleaned_line = self.clean_data_line(line)
            if cleaned_line is None:
                # Log corrupted data for debugging (only first few instances)
                if not hasattr(self, 'corrupted_count'):
                    self.corrupted_count = 0
                if self.corrupted_count < 5:
                    self.log(f"Filtered corrupted data: {line.strip()}")
                    self.corrupted_count += 1
                return  # Skip invalid/corrupted lines
            
            # Store the cleaned data line
            self.collected_data.append(cleaned_line)
            self.data_points += 1
            self.data_count.set(f"Data points: {self.data_points}")
            
            # Log every 100th data point to avoid spam
            if self.data_points % 100 == 0:
                self.log(f"Collected {self.data_points} data points")
    
    def create_motor_control_section(self, parent):
        """Motor control section"""
        frame = ttk.LabelFrame(parent, text="Motor Control", padding="10")
        frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))
        
        # Control buttons
        self.start_motor_btn = ttk.Button(frame, text="Start Motor", command=self.start_motor, state=tk.DISABLED)
        self.start_motor_btn.grid(row=0, column=0, padx=5, pady=5)
        
        self.stop_motor_btn = ttk.Button(frame, text="Stop Motor", command=self.stop_motor, state=tk.DISABLED)
        self.stop_motor_btn.grid(row=0, column=1, padx=5, pady=5)
        
        # Direction control
        ttk.Label(frame, text="Direction:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.direction_var = tk.StringVar(value="0")
        direction_frame = ttk.Frame(frame)
        direction_frame.grid(row=1, column=1, columnspan=2, sticky=tk.W, padx=5, pady=5)
        
        ttk.Radiobutton(direction_frame, text="Forward", variable=self.direction_var, value="1", 
                       command=self.set_direction).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(direction_frame, text="Reverse", variable=self.direction_var, value="0",
                       command=self.set_direction).pack(side=tk.LEFT, padx=5)
        
        # Motor status
        self.motor_status = tk.StringVar(value="Motor: Stopped")
        ttk.Label(frame, textvariable=self.motor_status, foreground="blue").grid(row=2, column=0, columnspan=3, pady=10)
    
    def start_motor(self):
        """Start motor"""
        if self.serial_connection:
            self.serial_connection.write(b"MOTOR_START\n")
    
    def stop_motor(self):
        """Stop motor"""
        if self.serial_connection:
            self.serial_connection.write(b"MOTOR_STOP\n")
    
    def set_direction(self):
        """Set motor direction"""
        if self.serial_connection:
            direction = self.direction_var.get()
            self.serial_connection.write(f"MOTOR_DIR {direction}\n".encode())
    
    def create_sensor_check_section(self, parent):
        """Sensor check section"""
        frame = ttk.LabelFrame(parent, text="Sensor Status", padding="10")
        frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(5, 0))
        
        # Check button
        ttk.Button(frame, text="Check All Sensors", command=self.check_sensors).grid(row=0, column=0, columnspan=2, pady=5)
        
        # Sensor status labels
        self.sensor_status = {
            'MPU6050': tk.StringVar(value="MPU6050: Unknown"),
            'ENCODER': tk.StringVar(value="Encoder: Unknown"),
            'MAX471': tk.StringVar(value="MAX471: Unknown"),
            'DS18B20': tk.StringVar(value="DS18B20: Unknown")
        }
        
        ttk.Label(frame, textvariable=self.sensor_status['MPU6050']).grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        ttk.Label(frame, textvariable=self.sensor_status['ENCODER']).grid(row=1, column=1, sticky=tk.W, padx=5, pady=2)
        ttk.Label(frame, textvariable=self.sensor_status['MAX471']).grid(row=2, column=0, sticky=tk.W, padx=5, pady=2)
        ttk.Label(frame, textvariable=self.sensor_status['DS18B20']).grid(row=2, column=1, sticky=tk.W, padx=5, pady=2)
    
    def check_sensors(self):
        """Check all sensors"""
        if self.serial_connection:
            self.serial_connection.write(b"CHECK_SENSORS\n")
    
    def create_data_collection_section(self, parent):
        """Data collection section"""
        frame = ttk.LabelFrame(parent, text="Data Collection", padding="10")
        frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        frame.columnconfigure(1, weight=1)
        
        # Sensor selection
        ttk.Label(frame, text="Select Sensor:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.sensor_var = tk.StringVar(value="MPU")
        sensor_combo = ttk.Combobox(frame, textvariable=self.sensor_var, 
                                   values=["MPU", "ENCODER", "MAX471", "DS18B20", "ALL"], width=15)
        sensor_combo.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Duration input
        ttk.Label(frame, text="Duration (seconds):").grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
        self.duration_var = tk.StringVar(value="10")
        duration_entry = ttk.Entry(frame, textvariable=self.duration_var, width=10)
        duration_entry.grid(row=0, column=3, sticky=tk.W, padx=5, pady=5)
        
        # Control buttons
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=1, column=0, columnspan=4, pady=10)
        
        self.collect_btn = ttk.Button(button_frame, text="Start Collection", command=self.start_collection, state=tk.DISABLED)
        self.collect_btn.pack(side=tk.LEFT, padx=5)
        
        self.stop_btn = ttk.Button(button_frame, text="Stop Collection", command=self.stop_collection, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, text="Save Data", command=self.save_data).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Clear Data", command=self.clear_data).pack(side=tk.LEFT, padx=5)
        
        # Progress bar
        ttk.Label(frame, text="Progress:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.progress = ttk.Progressbar(frame, mode='determinate')
        self.progress.grid(row=2, column=1, columnspan=3, sticky=(tk.W, tk.E), padx=5, pady=5)
        
        # Data count
        self.data_count = tk.StringVar(value="Data points: 0")
        ttk.Label(frame, textvariable=self.data_count).grid(row=3, column=0, columnspan=4, pady=5)
    
    def start_collection(self):
        """Start data collection"""
        if not self.serial_connection:
            messagebox.showerror("Error", "Not connected to device")
            return
        
        try:
            sensor = self.sensor_var.get()
            duration = int(self.duration_var.get())
            
            if duration <= 0 or duration > 300:
                messagebox.showerror("Error", "Duration must be 1-300 seconds")
                return
            
            # Reset data count
            self.data_points = 0
            self.data_count.set("Data points: 0")
            self.progress['value'] = 0
            
            # Send collection command
            command = f"COLLECT_{sensor},{duration}\n"
            self.serial_connection.write(command.encode())
            
            # Start progress update
            self.update_progress(duration)
            
        except ValueError:
            messagebox.showerror("Error", "Invalid duration")
    
    def update_progress(self, duration):
        """Update progress bar during collection"""
        if self.is_collecting:
            current = self.progress['value']
            if current < 90:
                self.progress['value'] = current + 1
                self.root.after(duration * 10, lambda: self.update_progress(duration))
    
    def stop_collection(self):
        """Stop data collection"""
        self.is_collecting = False
        if self.serial_connection:
            # Note: ESP32 doesn't support stopping mid-collection, but we'll update UI
            self.collect_btn.config(state=tk.NORMAL)
            self.stop_btn.config(state=tk.DISABLED)
            self.log("Collection stopped by user")
    
    def save_data(self):
        """Save collected data to CSV"""
        if len(self.collected_data) == 0:
            messagebox.showinfo("Info", "No data to save")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialfile=f"sensor_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        )
        
        if filename:
            try:
                with open(filename, 'w', newline='') as f:
                    writer = csv.writer(f)
                    
                    # Write header based on sensor type
                    sensor = self.sensor_var.get()
                    if sensor == "MPU":
                        writer.writerow(['timestamp', 'accX', 'accY', 'accZ', 'gyroX', 'gyroY', 'gyroZ'])
                        # Parse MPU data with timestamp from ESP32
                        for line in self.collected_data:
                            if line.startswith("MPU_DATA:"):
                                data = line[9:]  # Remove "MPU_DATA:" prefix
                                parts = data.split(',')
                                # Validate data has correct number of parts (timestamp + 6 values)
                                if len(parts) == 7 and self.is_valid_timestamp(parts[0]):
                                    writer.writerow(parts)  # Save original data unchanged
                                else:
                                    # Skip invalid data lines
                                    continue
                    
                    elif sensor == "ENCODER":
                        writer.writerow(['timestamp', 'rpm', 'position'])
                        for line in self.collected_data:
                            if line.startswith("ENCODER_DATA:"):
                                data = line[13:]  # Remove "ENCODER_DATA:" prefix
                                parts = data.split(',')
                                # Validate data has correct number of parts and valid timestamp
                                if len(parts) == 3 and self.is_valid_timestamp(parts[0]):
                                    writer.writerow(parts)  # Save original data unchanged
                    
                    elif sensor == "MAX471":
                        writer.writerow(['timestamp', 'voltage', 'current', 'power'])
                        for line in self.collected_data:
                            if line.startswith("POWER_DATA:"):
                                data = line[11:]  # Remove "POWER_DATA:" prefix
                                parts = data.split(',')
                                # Validate data has correct number of parts and valid timestamp
                                if len(parts) == 4 and self.is_valid_timestamp(parts[0]):
                                    writer.writerow(parts)  # Save original data unchanged
                    
                    elif sensor == "DS18B20":
                        writer.writerow(['timestamp', 'temperature'])
                        for line in self.collected_data:
                            if line.startswith("TEMP_DATA:"):
                                data = line[10:]  # Remove "TEMP_DATA:" prefix
                                parts = data.split(',')
                                # Validate data has correct number of parts and valid timestamp
                                if len(parts) == 2 and self.is_valid_timestamp(parts[0]):
                                    writer.writerow(parts)  # Save original data unchanged
                    
                    elif sensor == "ALL":
                        writer.writerow(['timestamp', 'accX', 'accY', 'accZ', 'gyroX', 'gyroY', 'gyroZ', 'rpm', 'voltage', 'current', 'temperature'])
                        for line in self.collected_data:
                            if line.startswith("ALL_DATA:"):
                                data = line[9:]  # Remove "ALL_DATA:" prefix
                                parts = data.split(',')
                                # Validate data has at least timestamp and valid format
                                if len(parts) >= 1 and self.is_valid_timestamp(parts[0]):
                                    writer.writerow(parts)  # Save original data unchanged
                    
                    else:
                        # Generic format for unknown sensors
                        writer.writerow(['raw_data'])
                        for line in self.collected_data:
                            writer.writerow([line])
                
                # Calculate actual duration from first and last timestamps
                if self.collected_data:
                    # Extract timestamps from data to calculate duration
                    first_timestamp = None
                    last_timestamp = None
                    
                    for line in self.collected_data:
                        if line.startswith("MPU_DATA:"):
                            data = line[9:]
                            parts = data.split(',')
                            if len(parts) >= 1:
                                ts = int(parts[0])
                                if first_timestamp is None:
                                    first_timestamp = ts
                                last_timestamp = ts
                                break
                    
                    if first_timestamp is not None and last_timestamp is not None:
                        actual_duration_ms = last_timestamp - first_timestamp
                        actual_duration_s = actual_duration_ms / 1000
                    else:
                        actual_duration_s = 0
                    
                    self.log(f"Data saved to {filename}")
                    self.log(f"Saved {len(self.collected_data)} data points")
                    self.log(f"Actual duration: {actual_duration_s:.2f} seconds")
                    messagebox.showinfo("Success", f"Data saved to {filename}\n{len(self.collected_data)} data points\nDuration: {actual_duration_s:.2f} seconds")
                
            except Exception as e:
                self.log(f"Save error: {e}")
                messagebox.showerror("Error", f"Failed to save data: {e}")
    
    def clear_data(self):
        """Clear collected data"""
        self.collected_data.clear()
        self.collection_start_time = None
        self.data_points = 0
        self.data_count.set("Data points: 0")
        self.progress['value'] = 0
        self.log("Data cleared")
    
    def create_log_section(self, parent):
        """Log section"""
        frame = ttk.LabelFrame(parent, text="System Log", padding="10")
        frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)
        
        # Log text widget with scrollbar
        log_frame = ttk.Frame(frame)
        log_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        self.log_text = tk.Text(log_frame, height=10, wrap=tk.WORD)
        scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)

def main():
    root = tk.Tk()
    app = IndustrialMaintenanceGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
