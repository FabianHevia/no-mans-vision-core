# no-mans-vision-core

## v0.1.0

A flexible, high-performance Python module designed for edge computing (Raspberry Pi) and IP Camera streams (RTSP). It combines traditional OpenCV motion detection with lightweight AI object classification to minimize false positives and measure spatial occupation.

## Key Features

- **Hybrid Motion & AI Pipeline:** Leverages OpenCV `MOG2` for fast motion detection and YOLO (ONNX/TFLite) for precise object classification.
- **Human vs. Non-Human Analytics:** Distinguishes human presence/movement from pets, vehicles, or environmental noise.
- **Occupancy & Counting Engine:** Real-time instance count for both persons and non-person moving objects.
- **Extensible Alert System:** Event-driven notifier supports Webhooks, Telegram, or internal API integrations with threshold suppression.
- **RTSP & Hardware Friendly:** Multi-threaded stream ingestion designed for low latency on edge devices like Raspberry Pi 4/5.

## Architecture Overview

[ RTSP Stream / Cam ]
        │
        ▼
[ Threaded Stream Reader ]
        │
        ▼
[ Motion Filter (OpenCV) ] ── (No Motion) ──► [ Drop Frame / Wait ]
        │ (Motion Detected)
        ▼
[ AI Object Detector (YOLO/ONNX) ]
        │
        ├── Person Count / Non-Person Count
        └── Spatial State (Occupied / Free)
        │
        ▼
[ Alert Manager & Dispatcher ] ──► [ Telegram / Webhook / Console ]
