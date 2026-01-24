#!/usr/bin/env python3
"""
Simple GUI for Industrial Predictive Maintenance Data Collection
Controls ESP32 data collection with start/stop functionality and configuration
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import serial
import serial.tools.list_ports
import threading
import time
from datetime import datetime
import os

class DataCollectionGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Industrial Predictive Maintenance - Data Collection")
        self.root.geometry("600x500")
        
        # Variables
        self.serial_port = tk.StringVar()
        self.data_label = tk.StringVar(value="normal")
        self.collection_time = tk.IntVar(value=5)  # minutes
        self.is_collecting = False
        self.serial_connection = None
        self.collection_thread = None
        
        # Data labels available
        self.labels = [
            "normal", 
            "imbalance", 
            "misalignment", 
            "bearing_defect", 
            "looseness"
        ]
        
        # Commands sent to ESP32
        self.commands = {
            "normal": "START_NORMAL",
            "imbalance": "START_IMBALANCE", 
            "misalignment": "START_MISALIGNMENT",
            "bearing_defect": "START_BEARING",
            "looseness": "START_LOOSENESS"
        }
        
        self.setup_gui()
        self.refresh_ports()
        
    def setup_gui(self):
        # Title
        title_frame = ttk.Frame(self.root, padding="10")
        title_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E))
        
        ttk.Label(title_frame, text="Industrial Predictive Maintenance", 
                 font=('Arial', 16, 'bold')).grid(row=0, column=0)
        ttk.Label(title_frame, text="Data Collection Control", 
                 font=('Arial', 12)).grid(row=1, column=0)
        
        # Connection Frame
        conn_frame = ttk.LabelFrame(self.root, text="Connection", padding="10")
        conn_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), padx=10, pady=5)
        
        ttk.Label(conn_frame, text="Serial Port:").grid(row=0, column=0, sticky=tk.W)
        self.port_combo = ttk.Combobox(conn_frame, textvariable=self.serial_port, width=20)
        self.port_combo.grid(row=0, column=1, padx=5)
        ttk.Button(conn_frame, text="Refresh", command=self.refresh_ports).grid(row=0, column=2, padx=5)
        ttk.Button(conn_frame, text="Connect", command=self.toggle_connection).grid(row=0, column=3, padx=5)
        
        self.connection_status = ttk.Label(conn_frame, text="Disconnected", foreground="red")
        self.connection_status.grid(row=0, column=4, padx=10)
        
        # Configuration Frame
        config_frame = ttk.LabelFrame(self.root, text="Collection Configuration", padding="10")
        config_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), padx=10, pady=5)
        
        ttk.Label(config_frame, text="Data Label:").grid(row=0, column=0, sticky=tk.W)
        self.label_combo = ttk.Combobox(config_frame, textvariable=self.data_label, 
                                       values=self.labels, width=20, state="readonly")
        self.label_combo.grid(row=0, column=1, padx=5, sticky=tk.W)
        
        ttk.Label(config_frame, text="Collection Time (minutes):").grid(row=1, column=0, sticky=tk.W, pady=5)
        time_spinbox = ttk.Spinbox(config_frame, from_=1, to=30, textvariable=self.collection_time, width=10)
        time_spinbox.grid(row=1, column=1, padx=5, sticky=tk.W, pady=5)
        
        # Control Frame
        control_frame = ttk.LabelFrame(self.root, text="Control", padding="10")
        control_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), padx=10, pady=5)
        
        self.start_button = ttk.Button(control_frame, text="Start Collection", 
                                      command=self.start_collection, width=20)
        self.start_button.grid(row=0, column=0, padx=5)
        
        self.stop_button = ttk.Button(control_frame, text="Stop Collection", 
                                     command=self.stop_collection, width=20, state="disabled")
        self.stop_button.grid(row=0, column=1, padx=5)
        
        # Status Frame
        status_frame = ttk.LabelFrame(self.root, text="Status", padding="10")
        status_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), padx=10, pady=5)
        
        self.status_label = ttk.Label(status_frame, text="Ready", font=('Arial', 10))
        self.status_label.grid(row=0, column=0, sticky=tk.W)
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(status_frame, variable=self.progress_var, 
                                          maximum=100, length=400)
        self.progress_bar.grid(row=1, column=0, columnspan=2, pady=5, sticky=(tk.W, tk.E))
        
        self.time_remaining = ttk.Label(status_frame, text="Time remaining: --:--")
        self.time_remaining.grid(row=2, column=0, sticky=tk.W)
        
        # Log Frame
        log_frame = ttk.LabelFrame(self.root, text="Log", padding="10")
        log_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=10, pady=5)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=10, width=70)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(5, weight=1)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
    def refresh_ports(self):
        """Refresh available serial ports"""
        ports = [port.device for port in serial.tools.list_ports.comports()]
        self.port_combo['values'] = ports
        if ports and not self.serial_port.get():
            self.serial_port.set(ports[0])
        self.log(f"Found {len(ports)} serial ports: {', '.join(ports)}")
        
    def toggle_connection(self):
        """Toggle serial connection"""
        if self.serial_connection is None:
            self.connect_serial()
        else:
            self.disconnect_serial()
            
    def connect_serial(self):
        """Connect to serial port"""
        if not self.serial_port.get():
            messagebox.showerror("Error", "Please select a serial port")
            return
            
        try:
            self.serial_connection = serial.Serial(self.serial_port.get(), 115200, timeout=1)
            self.connection_status.config(text="Connected", foreground="green")
            self.log(f"Connected to {self.serial_port.get()}")
            
            # Clear any existing data
            time.sleep(1)
            while self.serial_connection.in_waiting:
                self.serial_connection.read()
                
        except Exception as e:
            messagebox.showerror("Connection Error", f"Failed to connect: {e}")
            self.log(f"Connection failed: {e}")
            
    def disconnect_serial(self):
        """Disconnect from serial port"""
        if self.serial_connection:
            self.serial_connection.close()
            self.serial_connection = None
            self.connection_status.config(text="Disconnected", foreground="red")
            self.log("Disconnected from serial port")
            
    def start_collection(self):
        """Start data collection"""
        if not self.serial_connection:
            messagebox.showerror("Error", "Please connect to serial port first")
            return
            
        if self.is_collecting:
            return
            
        self.is_collecting = True
        self.start_button.config(state="disabled")
        self.stop_button.config(state="normal")
        
        # Start collection in separate thread
        self.collection_thread = threading.Thread(target=self.collect_data)
        self.collection_thread.daemon = True
        self.collection_thread.start()
        
        self.log(f"Starting collection: {self.data_label.get()} for {self.collection_time.get()} minutes")
        
    def stop_collection(self):
        """Stop data collection"""
        if not self.is_collecting:
            return
            
        self.is_collecting = False
        self.start_button.config(state="normal")
        self.stop_button.config(state="disabled")
        
        # Send stop command if connected
        if self.serial_connection:
            try:
                self.serial_connection.write(b"STOP\n")
            except:
                pass
                
        self.log("Collection stopped by user")
        self.status_label.config(text="Stopped")
        self.progress_var.set(0)
        self.time_remaining.config(text="Time remaining: --:--")
        
    def collect_data(self):
        """Collect data in separate thread"""
        try:
            label = self.data_label.get()
            command = self.commands[label]
            duration_minutes = self.collection_time.get()
            
            # Send start command
            self.serial_connection.write(f"{command}\n".encode())
            time.sleep(0.5)
            
            start_time = time.time()
            end_time = start_time + (duration_minutes * 60)
            
            self.status_label.config(text=f"Collecting: {label}")
            
            while self.is_collecting and time.time() < end_time:
                # Check for serial data
                if self.serial_connection.in_waiting:
                    try:
                        line = self.serial_connection.readline().decode("utf-8", errors="ignore").strip()
                        if line:
                            self.log(f"ESP32: {line}")
                    except:
                        pass
                
                # Update progress
                elapsed = time.time() - start_time
                remaining = end_time - time.time()
                progress = (elapsed / (duration_minutes * 60)) * 100
                
                self.root.after(0, self.update_progress, progress, remaining)
                
                time.sleep(0.1)
            
            # Collection completed
            if self.is_collecting:
                self.root.after(0, self.collection_complete)
                
        except Exception as e:
            self.root.after(0, lambda: self.log(f"Collection error: {e}"))
        finally:
            self.root.after(0, self.reset_ui)
            
    def update_progress(self, progress, remaining):
        """Update progress bar and time remaining"""
        self.progress_var.set(min(progress, 100))
        if remaining > 0:
            mins = int(remaining // 60)
            secs = int(remaining % 60)
            self.time_remaining.config(text=f"Time remaining: {mins:02d}:{secs:02d}")
        else:
            self.time_remaining.config(text="Time remaining: 00:00")
            
    def collection_complete(self):
        """Handle collection completion"""
        self.log(f"Collection completed: {self.data_label.get()}")
        self.status_label.config(text="Completed")
        messagebox.showinfo("Complete", f"Data collection for '{self.data_label.get()}' completed!")
        
    def reset_ui(self):
        """Reset UI after collection"""
        self.is_collecting = False
        self.start_button.config(state="normal")
        self.stop_button.config(state="disabled")
        self.progress_var.set(0)
        self.time_remaining.config(text="Time remaining: --:--")
        
    def log(self, message):
        """Add message to log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        
    def on_closing(self):
        """Handle window closing"""
        if self.is_collecting:
            if messagebox.askokcancel("Quit", "Collection is in progress. Stop and quit?"):
                self.stop_collection()
            else:
                return
                
        if self.serial_connection:
            self.disconnect_serial()
        self.root.destroy()

def main():
    root = tk.Tk()
    app = DataCollectionGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()
