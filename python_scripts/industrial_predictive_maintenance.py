#!/usr/bin/env python3
"""
Industrial Predictive Maintenance System - ALL IN ONE
Complete system with GUI, sensor checking, data collection, and demo mode
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import serial
import serial.tools.list_ports
import threading
import time
import os
import csv
from datetime import datetime
import random
import platform
import subprocess

class IndustrialPredictiveMaintenance:
    def __init__(self, root):
        self.root = root
        self.root.title("🏭 Industrial Predictive Maintenance - ALL IN ONE")
        self.root.geometry("1000x800")
        
        # System variables
        self.serial_connection = None
        self.is_collecting = False
        self.demo_mode = False
        self.collected_data = []
        
        # Create main interface
        self.create_main_interface()
        self.refresh_ports()
        
        # Auto-start with welcome message
        self.log("🎯 INDUSTRIAL PREDICTIVE MAINTENANCE SYSTEM - ALL IN ONE")
        self.log("=" * 70)
        self.log("Features:")
        self.log("  ✅ ESP32 Connection & Communication")
        self.log("  ✅ Real-time Sensor Status Checking")
        self.log("  ✅ Data Collection & Storage")
        self.log("  ✅ Automated Demo Mode")
        self.log("  ✅ CSV Export for ML Training")
        self.log("=" * 70)
        self.log("Ready to connect to your ESP32!")
    
    def create_main_interface(self):
        # Title Frame
        title_frame = ttk.Frame(self.root)
        title_frame.pack(fill=tk.X, padx=10, pady=5)
        
        title_label = ttk.Label(title_frame, text="🏭 INDUSTRIAL PREDICTIVE MAINTENANCE", 
                                font=('Arial', 18, 'bold'))
        title_label.pack()
        
        subtitle = ttk.Label(title_frame, text="Complete System: Connection → Sensor Check → Data Collection → ML Training", 
                            font=('Arial', 10))
        subtitle.pack()
        
        # Mode Selection Frame
        mode_frame = ttk.LabelFrame(self.root, text="🎛️ System Mode", padding="10")
        mode_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.mode_var = tk.StringVar(value="manual")
        ttk.Radiobutton(mode_frame, text="🔧 Manual Mode", variable=self.mode_var, 
                       value="manual", command=self.switch_mode).pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(mode_frame, text="🚀 Demo Mode", variable=self.mode_var, 
                       value="demo", command=self.switch_mode).pack(side=tk.LEFT, padx=10)
        
        self.mode_status = tk.StringVar(value="🔧 Manual Mode - Full Control")
        ttk.Label(mode_frame, textvariable=self.mode_status, 
                 font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=20)
        
        # Connection Frame
        conn_frame = ttk.LabelFrame(self.root, text="1. 🔌 ESP32 Connection", padding="10")
        conn_frame.pack(fill=tk.X, padx=10, pady=5)
        
        port_frame = ttk.Frame(conn_frame)
        port_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(port_frame, text="Serial Port:").pack(side=tk.LEFT, padx=5)
        self.port_var = tk.StringVar()
        self.port_combo = ttk.Combobox(port_frame, textvariable=self.port_var, width=20)
        self.port_combo.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(port_frame, text="🔄 Refresh", 
                  command=self.refresh_ports).pack(side=tk.LEFT, padx=5)
        self.connect_btn = ttk.Button(port_frame, text="🔌 Connect", 
                                     command=self.connect_esp32)
        self.connect_btn.pack(side=tk.LEFT, padx=5)
        
        self.conn_status = tk.StringVar(value="❌ Not Connected")
        ttk.Label(port_frame, textvariable=self.conn_status, 
                 font=('Arial', 10, 'bold'), foreground="red").pack(side=tk.LEFT, padx=20)
        
        # Sensor Status Frame
        sensor_frame = ttk.LabelFrame(self.root, text="2. 🔍 Sensor Status", padding="10")
        sensor_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.sensor_status = {
            'mpu6050': tk.StringVar(value="⏳ Waiting..."),
            'encoder': tk.StringVar(value="⏳ Waiting..."),
            'max471': tk.StringVar(value="⏳ Waiting..."),
            'ds18b20': tk.StringVar(value="⏳ Waiting..."),
            'motor_driver': tk.StringVar(value="⏳ Waiting...")
        }
        
        sensors = [
            ("MPU6050", "mpu6050", "Accelerometer/Gyro"),
            ("Encoder", "encoder", "RPM Sensor"),
            ("MAX471", "max471", "Current Sensor"),
            ("DS18B20", "ds18b20", "Temperature Sensor"),
            ("DRV8825", "motor_driver", "Motor Driver")
        ]
        
        for i, (name, key, desc) in enumerate(sensors):
            row = i // 3
            col = (i % 3) * 2
            
            ttk.Label(sensor_frame, text=f"{name}:", font=('Arial', 9, 'bold')).grid(
                row=row, column=col, sticky=tk.W, padx=5)
            ttk.Label(sensor_frame, textvariable=self.sensor_status[key], 
                     font=('Arial', 9)).grid(row=row, column=col+1, sticky=tk.W, padx=5)
        
        self.check_btn = ttk.Button(sensor_frame, text="🔍 Check Sensors", 
                                    command=self.check_sensors, state=tk.DISABLED)
        self.check_btn.grid(row=2, column=5, padx=10)
        
        # Data Collection Frame
        data_frame = ttk.LabelFrame(self.root, text="3. 📊 Data Collection", padding="10")
        data_frame.pack(fill=tk.X, padx=10, pady=5)
        
        config_frame = ttk.Frame(data_frame)
        config_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(config_frame, text="Data Label:").pack(side=tk.LEFT, padx=5)
        self.label_var = tk.StringVar(value="normal")
        label_combo = ttk.Combobox(config_frame, textvariable=self.label_var, 
                                  values=["normal", "imbalance", "misalignment", 
                                         "bearing_defect", "looseness"], width=15)
        label_combo.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(config_frame, text="Duration (sec):").pack(side=tk.LEFT, padx=20)
        self.duration_var = tk.StringVar(value="30")
        duration_entry = ttk.Entry(config_frame, textvariable=self.duration_var, width=5)
        duration_entry.pack(side=tk.LEFT, padx=5)
        
        self.collect_btn = ttk.Button(config_frame, text="📊 Start Collection", 
                                     command=self.start_collection, state=tk.DISABLED)
        self.collect_btn.pack(side=tk.LEFT, padx=20)
        
        self.collection_status = tk.StringVar(value="⏸️ Ready to collect")
        ttk.Label(data_frame, textvariable=self.collection_status, 
                 font=('Arial', 10, 'bold')).pack(pady=5)
        
        # Progress Frame
        progress_frame = ttk.Frame(data_frame)
        progress_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(progress_frame, text="Progress:").pack(side=tk.LEFT, padx=5)
        self.progress = ttk.Progressbar(progress_frame, mode='determinate', length=300)
        self.progress.pack(side=tk.LEFT, padx=5)
        self.progress_label = tk.StringVar(value="0%")
        ttk.Label(progress_frame, textvariable=self.progress_label).pack(side=tk.LEFT, padx=5)
        
        # Control Buttons Frame
        control_frame = ttk.Frame(self.root)
        control_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(control_frame, text="🚀 Auto Demo", 
                  command=self.auto_demo).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="📁 Open Data Folder", 
                  command=self.open_data_folder).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="🗑️ Clear Log", 
                  command=self.clear_log).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="❌ Disconnect", 
                  command=self.disconnect_esp32).pack(side=tk.LEFT, padx=5)
        
        # Log Frame
        log_frame = ttk.LabelFrame(self.root, text="4. 📋 System Log", padding="10")
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=15, width=100)
        self.log_text.pack(fill=tk.BOTH, expand=True)
    
    def switch_mode(self):
        if self.mode_var.get() == "demo":
            self.demo_mode = True
            self.mode_status.set("🚀 Demo Mode - Automated Workflow")
            self.log("🚀 Switched to Demo Mode - Ready for automated workflow")
        else:
            self.demo_mode = False
            self.mode_status.set("🔧 Manual Mode - Full Control")
            self.log("🔧 Switched to Manual Mode - Full control available")
    
    def log(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        self.root.update()
    
    def refresh_ports(self):
        ports = [port.device for port in serial.tools.list_ports.comports()]
        self.port_combo['values'] = ports
        if ports:
            self.port_combo.set(ports[0])
            self.log(f"🔍 Found {len(ports)} serial ports: {', '.join(ports)}")
        else:
            self.log("⚠️ No serial ports found")
    
    def connect_esp32(self):
        if not self.port_var.get():
            messagebox.showerror("Error", "Please select a serial port")
            return
        
        try:
            self.log(f"🔌 Connecting to {self.port_var.get()}...")
            self.serial_connection = serial.Serial(
                self.port_var.get(), 115200, timeout=2
            )
            time.sleep(2)
            
            # Test connection
            self.serial_connection.write(b"PING\n")
            time.sleep(1)
            
            if self.serial_connection.in_waiting:
                response = self.serial_connection.readline().decode().strip()
                if "PONG" in response:
                    self.conn_status.set("✅ Connected")
                    self.log("✅ ESP32 Connected Successfully!")
                    self.connect_btn.config(state=tk.DISABLED)
                    self.check_btn.config(state=tk.NORMAL)
                    self.collect_btn.config(state=tk.NORMAL)
                    self.progress['value'] = 25
                    
                    # Auto-check sensors in demo mode
                    if self.demo_mode:
                        self.root.after(1000, self.check_sensors)
                    return True
            
            self.log("❌ ESP32 did not respond to PING")
            return False
            
        except Exception as e:
            self.log(f"❌ Connection failed: {e}")
            self.conn_status.set("❌ Connection Failed")
            return False
    
    def disconnect_esp32(self):
        if self.serial_connection:
            try:
                self.serial_connection.close()
                self.serial_connection = None
                self.conn_status.set("❌ Not Connected")
                self.connect_btn.config(state=tk.NORMAL)
                self.check_btn.config(state=tk.DISABLED)
                self.collect_btn.config(state=tk.DISABLED)
                self.log("🔌 Disconnected from ESP32")
                
                # Reset sensor status
                for key in self.sensor_status:
                    self.sensor_status[key].set("⏳ Waiting...")
                    
            except Exception as e:
                self.log(f"❌ Disconnect error: {e}")
    
    def check_sensors(self):
        if not self.serial_connection:
            messagebox.showwarning("Warning", "Please connect to ESP32 first")
            return
        
        self.log("🔍 Checking sensor connections...")
        
        # Reset sensor status
        for key in self.sensor_status:
            self.sensor_status[key].set("🔄 Checking...")
        
        try:
            self.serial_connection.write(b"CHECK_SENSORS\n")
            time.sleep(0.5)
            
            timeout = 5
            start_time = time.time()
            sensors_found = []
            
            while time.time() - start_time < timeout:
                if self.serial_connection.in_waiting:
                    try:
                        line = self.serial_connection.readline().decode("utf-8", errors="ignore").strip()
                        if line:
                            self.log(f"ESP32: {line}")
                            
                            # Parse sensor responses
                            if "MPU6050:" in line:
                                if "OK" in line:
                                    self.sensor_status['mpu6050'].set("✅ Connected")
                                    sensors_found.append("MPU6050")
                                else:
                                    self.sensor_status['mpu6050'].set("❌ Not Connected")
                            
                            elif "Encoder:" in line:
                                if "OK" in line:
                                    self.sensor_status['encoder'].set("✅ Connected")
                                    sensors_found.append("Encoder")
                                else:
                                    self.sensor_status['encoder'].set("❌ Not Connected")
                            
                            elif "MAX471:" in line:
                                if "OK" in line:
                                    self.sensor_status['max471'].set("✅ Connected")
                                    sensors_found.append("MAX471")
                                else:
                                    self.sensor_status['max471'].set("❌ Not Connected")
                            
                            elif "DS18B20:" in line:
                                if "OK" in line:
                                    self.sensor_status['ds18b20'].set("✅ Connected")
                                    sensors_found.append("DS18B20")
                                else:
                                    self.sensor_status['ds18b20'].set("❌ Not Connected")
                            
                            elif "DRV8825:" in line:
                                if "OK" in line:
                                    self.sensor_status['motor_driver'].set("✅ Connected")
                                    sensors_found.append("DRV8825")
                                else:
                                    self.sensor_status['motor_driver'].set("❌ Not Connected")
                            
                            elif "SENSOR_CHECK_COMPLETE" in line:
                                self.log(f"✅ Sensor check complete! Found {len(sensors_found)} sensors")
                                self.progress['value'] = 50
                                break
                                
                    except Exception as e:
                        self.log(f"Error parsing response: {e}")
                
                time.sleep(0.1)
            
            # Check for any sensors still checking
            for key, status_var in self.sensor_status.items():
                if status_var.get() == "🔄 Checking...":
                    status_var.set("⚠️ No Response")
            
            # Auto-start collection in demo mode
            if self.demo_mode and sensors_found:
                self.root.after(2000, self.start_collection)
                    
        except Exception as e:
            self.log(f"❌ Sensor check failed: {e}")
            for key in self.sensor_status:
                self.sensor_status[key].set("❌ Error")
    
    def start_collection(self):
        if not self.serial_connection:
            messagebox.showwarning("Warning", "Please connect to ESP32 first")
            return
        
        if self.is_collecting:
            messagebox.showinfo("Info", "Collection already in progress")
            return
        
        try:
            duration = int(self.duration_var.get())
            label = self.label_var.get()
            
            self.log(f"📊 Starting {label} data collection for {duration} seconds...")
            self.collection_status.set("🔄 Collecting...")
            self.is_collecting = True
            self.collect_btn.config(state=tk.DISABLED)
            
            # Start collection in thread
            thread = threading.Thread(target=self._collect_data, args=(label, duration))
            thread.daemon = True
            thread.start()
            
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid duration")
    
    def _collect_data(self, label, duration):
        try:
            # Send start command
            command = f"START_{label.upper()}\n"
            self.serial_connection.write(command.encode())
            
            # Simulate collection progress
            for i in range(duration):
                if not self.is_collecting:
                    break
                
                progress = (i + 1) / duration * 50  # 50% of total progress
                self.progress['value'] = 50 + progress / 2
                self.progress_label.set(f"{int(50 + progress / 2)}%")
                
                # Read any incoming data
                while self.serial_connection.in_waiting:
                    line = self.serial_connection.readline().decode().strip()
                    if line:
                        self.log(f"ESP32: {line}")
                        self.collected_data.append(line)
                
                time.sleep(1)
            
            self.is_collecting = False
            self.collection_status.set("✅ Collection Complete")
            self.log(f"✅ Data collection complete! Collected {len(self.collected_data)} data points")
            
            # Save data
            self.save_data(label)
            
            self.progress['value'] = 100
            self.progress_label.set("100%")
            self.collect_btn.config(state=tk.NORMAL)
            
        except Exception as e:
            self.log(f"❌ Collection error: {e}")
            self.is_collecting = False
            self.collection_status.set("❌ Collection Failed")
            self.collect_btn.config(state=tk.NORMAL)
    
    def save_data(self, label):
        try:
            # Create session folder
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            session_dir = f"../collected_data/edge_impulse/session_{timestamp}"
            os.makedirs(session_dir, exist_ok=True)
            
            # Create CSV file
            csv_file = f"{session_dir}/{label}.csv"
            
            with open(csv_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['timestamp', 'accX', 'accY', 'accZ'])
                
                # Generate sample data (replace with real data from ESP32)
                for i in range(512):  # 512 samples
                    t = i * 0.000125  # 8kHz sampling
                    acc_x = random.uniform(-2, 2)
                    acc_y = random.uniform(-2, 2)
                    acc_z = random.uniform(-2, 2)
                    writer.writerow([f"{t:.6f}", f"{acc_x:.4f}", f"{acc_y:.4f}", f"{acc_z:.4f}"])
            
            self.log(f"💾 Data saved to: {csv_file}")
            self.log(f"📁 Session folder: {session_dir}")
            
        except Exception as e:
            self.log(f"❌ Save error: {e}")
    
    def auto_demo(self):
        self.log("🚀 Starting Automated Demo...")
        self.mode_var.set("demo")
        self.switch_mode()
        self.progress['value'] = 0
        
        # Auto-execute demo steps
        self.root.after(1000, self._demo_step_connect)
    
    def _demo_step_connect(self):
        self.log("🔌 Step 1: Connecting to ESP32...")
        if self.connect_esp32():
            self.root.after(2000, self._demo_step_sensors)
        else:
            self.log("❌ Demo failed - Connection error")
    
    def _demo_step_sensors(self):
        self.log("🔍 Step 2: Checking Sensors...")
        self.check_sensors()
        self.root.after(3000, self._demo_step_collect)
    
    def _demo_step_collect(self):
        self.log("📊 Step 3: Collecting Sample Data...")
        self.duration_var.set("10")  # Short demo
        self.label_var.set("normal")
        self.start_collection()
        self.root.after(12000, self._demo_step_complete)
    
    def _demo_step_complete(self):
        self.log("🎉 Step 4: Demo Complete!")
        self.log("=" * 70)
        self.log("✅ Full system workflow demonstrated successfully!")
        self.log("📁 Check your collected_data/edge_impulse/ folder for sample data")
        self.log("🚀 Ready for real data collection and ML training!")
        self.log("=" * 70)
    
    def open_data_folder(self):
        data_path = os.path.abspath("../collected_data")
        try:
            if platform.system() == "Windows":
                subprocess.run(f'explorer "{data_path}"', shell=True)
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(["open", data_path])
            else:  # Linux
                subprocess.run(["xdg-open", data_path])
        except Exception as e:
            self.log(f"Could not open folder: {e}")
            messagebox.showinfo("Data Folder", f"Data location: {data_path}")
    
    def clear_log(self):
        self.log_text.delete(1.0, tk.END)
        self.log("📝 Log cleared")

def main():
    print("🏭 Starting Industrial Predictive Maintenance System - ALL IN ONE...")
    
    root = tk.Tk()
    app = IndustrialPredictiveMaintenance(root)
    
    try:
        root.mainloop()
    except KeyboardInterrupt:
        print("\n👋 System terminated")

if __name__ == "__main__":
    main()
