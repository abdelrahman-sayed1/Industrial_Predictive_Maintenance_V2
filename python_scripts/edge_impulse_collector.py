#!/usr/bin/env python3
"""
Edge Impulse Data Collector – Raw-only, EI-ready CSVs
Collects raw accel (X,Y,Z) from ESP32 and writes one CSV per window
in Edge Impulse format: timestamp,accX,accY,accZ (0.125 ms step, 8 kHz).
Labels: normal, imbalance, looseness, bearing_defect, misalignment.
"""

import serial
import serial.tools.list_ports
import csv
import time
import os
from datetime import datetime

# 8 kHz → 0.125 ms per sample
SAMPLE_INTERVAL_MS = 0.125
SAMPLE_SIZE = 512

OUTPUT_DIR = "collected_data"
EI_SUBDIR = "edge_impulse"

LABELS = [
    ("normal", "START_NORMAL"),
    ("imbalance", "START_IMBALANCE"),
    ("misalignment", "START_MISALIGNMENT"),
    ("bearing_defect", "START_BEARING"),
    ("looseness", "START_LOOSENESS"),
]


def select_port():
    ports = list(serial.tools.list_ports.comports())
    if not ports:
        print("No serial ports found.")
        return None
    print("\nAvailable serial ports:")
    for i, p in enumerate(ports):
        print(f"  {i}: {p.device} – {p.description}")
    while True:
        try:
            idx = int(input(f"Select port [0–{len(ports) - 1}]: "))
            if 0 <= idx < len(ports):
                return ports[idx].device
        except (ValueError, EOFError):
            pass
        print("Invalid choice.")


def collect_state(ser, state_name, command, run_dir, state_counts, timeout_s=310):
    print(f"\n{'='*60}")
    print(f"  STATE: {state_name.upper()}")
    print(f"{'='*60}\n")
    input(f"Set up «{state_name}» condition, then press ENTER…")

    ser.write(f"{command}\n".encode())
    time.sleep(0.5)

    window_count = 0
    raw_samples = []
    start = time.time()

    print(f"Collecting raw data (~5 min)…\n")

    while time.time() - start < timeout_s:
        if not ser.in_waiting:
            time.sleep(0.001)
            continue

        try:
            line = ser.readline().decode("utf-8", errors="ignore").strip()
        except Exception:
            continue

        if not line:
            continue

        if "COLLECTION_START" in line:
            print(f"  Collection started: {state_name}")
            continue
        if "COLLECTION_END" in line:
            print(f"  Collection complete: {state_name}")
            break

        if "RAW_WINDOW_START" in line:
            # Flush *previous* window to CSV (we just got the next window's header)
            if raw_samples and len(raw_samples) == SAMPLE_SIZE:
                out_path = os.path.join(run_dir, f"{state_name}.{window_count}.csv")
                with open(out_path, "w", newline="", encoding="utf-8") as f:
                    w = csv.writer(f)
                    w.writerow(["timestamp", "accX", "accY", "accZ"])
                    for i, (ax, ay, az, *_) in enumerate(raw_samples):
                        ts = i * SAMPLE_INTERVAL_MS
                        w.writerow([f"{ts:.6f}", ax, ay, az])
                window_count += 1
                print(f"\r  Windows: {window_count}", end="", flush=True)

            raw_samples = []
            continue

        # Raw line: accel_x,accel_y,accel_z,gyro_x,gyro_y,gyro_z
        if "," in line:
            p = [x.strip() for x in line.split(",")]
            if len(p) >= 3:
                try:
                    ax, ay, az = float(p[0]), float(p[1]), float(p[2])
                    gx = float(p[3]) if len(p) > 3 else 0.0
                    gy = float(p[4]) if len(p) > 4 else 0.0
                    gz = float(p[5]) if len(p) > 5 else 0.0
                    raw_samples.append((ax, ay, az, gx, gy, gz))
                except ValueError:
                    pass

    # Last window
    if raw_samples and len(raw_samples) == SAMPLE_SIZE:
        out_path = os.path.join(run_dir, f"{state_name}.{window_count}.csv")
        with open(out_path, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["timestamp", "accX", "accY", "accZ"])
            for i, (ax, ay, az, *_) in enumerate(raw_samples):
                ts = i * SAMPLE_INTERVAL_MS
                w.writerow([f"{ts:.6f}", ax, ay, az])
        window_count += 1

    state_counts[state_name] = window_count
    print(f"\n  Total windows for {state_name}: {window_count}")


def main():
    print("\n" + "=" * 60)
    print("  Edge Impulse Collector – Raw-only, EI-ready CSVs")
    print("  Labels: normal, imbalance, looseness, bearing_defect, misalignment")
    print("=" * 60)

    port = select_port()
    if not port:
        return

    try:
        ser = serial.Serial(port, 115200, timeout=1)
    except serial.SerialException as e:
        print(f"Serial error: {e}")
        return

    time.sleep(1)
    while ser.in_waiting:
        ser.read()
    print(f"Connected to {port}\n")

    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = os.path.join(OUTPUT_DIR, EI_SUBDIR, run_id)
    os.makedirs(run_dir, exist_ok=True)
    print(f"Output: {run_dir}\n")

    print("Plan: 5 states × ~5 min each (~25 min total)")
    input("Press ENTER to start…")

    state_counts = {}
    for state_name, command in LABELS:
        collect_state(ser, state_name, command, run_dir, state_counts)

    ser.close()

    total = sum(state_counts.values())
    print(f"\n{'='*60}")
    print(f"  Done. {total} CSVs in {run_dir}")
    print("  Upload that folder to Edge Impulse → Data acquisition.")
    print("  Use DSP «Choose recommended», then train & deploy.")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
