# Python Scripts

## Edge Impulse collector (recommended for TinyML)

**`edge_impulse_collector.py`** — Raw-only data collection, Edge Impulse–ready CSVs.

- **Labels:** `normal`, `imbalance`, `misalignment`, `bearing_defect`, `looseness`
- **Output:** `collected_data/edge_impulse/<run_id>/` — one CSV per 512-sample window
- **Format:** `timestamp,accX,accY,accZ` (0.125 ms step, 8 kHz). Filename: `label.id.csv` (e.g. `normal.0.csv`, `imbalance.1.csv`).
- **Usage:** Run script → select COM port → follow prompts for each fault state (~5 min each). Upload the run folder to Edge Impulse → Data acquisition → DSP “Choose recommended” → train & deploy.

## Other scripts

- **`advanced_collector.py`** — Raw 6-axis (accel + gyro) + Python feature extraction; writes features + raw CSVs. Use if you want hand-crafted features or raw+features for classical ML.
- **`data_collector.py`** — Older collector; protocol does not match current firmware.
- **`data_processor.py`** — 3-axis raw + features; different protocol.

## Requirements

```bash
pip install -r requirements.txt
```

(`pyserial` only for `edge_impulse_collector.py`; `advanced_collector` / `data_processor` use `numpy` / `scipy`.)
